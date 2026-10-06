"""The suite interface, and the runner that drives a batch.

A suite declares its items and its caps, and runs one item through a Context
that meters every call as it happens. The runner does the rest, the same way
against the fake endpoint and a live provider:

1. refuse to start inside a peak window, unless told otherwise;
2. read the balance and the model list, under a read-only reservation;
3. reserve the batch's worst case from the guard, which refuses what does not
   fit the ceiling or the balance;
4. probe identity, then run each item and repeat, checking the reservation
   before each run, and recording each run's line, cost and transcript;
5. read the balance again and reconcile what was computed against what was
   billed. A mismatch stops the caller's next batch.
"""
from __future__ import annotations

import time as _time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Callable

from . import identity
from . import record as rec
from .client import Client, ProviderError
from .guard import Refused, SpendGuard, reconcile
from .prices import PriceTable, Usage
from .providers import deepseek
from .registry import Endpoint


@dataclass(frozen=True)
class Caps:
    """Per item run, summed over its calls. max_call_prompt_tokens bounds the
    one call that may cross max_prompt_tokens, so a run's worst case is
    (max_prompt_tokens + max_call_prompt_tokens) prompt and max_output_tokens."""
    max_prompt_tokens: int
    max_output_tokens: int
    max_call_prompt_tokens: int


@dataclass
class Item:
    id: str
    data: dict = field(default_factory=dict)


@dataclass
class ItemResult:
    status: str               # pass | fail | error | stopped | skipped
    detail: str
    data: dict = field(default_factory=dict)


class CapReached(Exception):
    pass


class MeterMismatch(Exception):
    pass


def _add(a: Usage, b: Usage) -> Usage:
    return Usage(a.cache_hit + b.cache_hit, a.cache_miss + b.cache_miss,
                 a.output + b.output, a.reasoning + b.reasoning)


def estimate_tokens(text: str) -> int:
    """A conservative token estimate for English and JSON text: two characters
    per token, about double the usual rate. It bounds a request's size before
    it is sent; text in scripts with a token per character defeats it, which is
    a stated limit."""
    return len(text) // 2 + 1


class Context:
    """One item run's calls, metered as they happen."""

    def __init__(self, client: Client, endpoint: Endpoint, caps: Caps, *, thinking: bool,
                 effort: str | None, provider=deepseek):
        self.client, self.endpoint, self.caps = client, endpoint, caps
        self.thinking, self.effort, self.provider = thinking, effort, provider
        self.used = Usage(0, 0, 0, 0)
        self.calls: list[dict] = []
        self.model_reported: str | None = None
        self.fingerprint: str | None = None
        self.sampling = {"sent": {}, "ignored": []}

    def chat(self, messages: list[dict], **kw):
        if self.used.prompt >= self.caps.max_prompt_tokens:
            raise CapReached(f"prompt cap reached: {self.used.prompt} of {self.caps.max_prompt_tokens}")
        if self.used.output >= self.caps.max_output_tokens:
            raise CapReached(f"output cap reached: {self.used.output} of {self.caps.max_output_tokens}")
        est = estimate_tokens(rec.canonical({"m": messages, "t": kw.get("tools")}))
        if est > self.caps.max_call_prompt_tokens:
            raise CapReached(f"a request of about {est} tokens exceeds the suite's declared "
                             f"largest, {self.caps.max_call_prompt_tokens}")
        kw.setdefault("thinking", self.thinking)
        if kw["thinking"] and self.effort:
            kw.setdefault("effort", self.effort)
        left = self.caps.max_output_tokens - self.used.output
        kw["max_tokens"] = min(kw["max_tokens"], left) if kw.get("max_tokens") else left
        self.sampling = self.provider.sampling_record(kw["thinking"], kw.get("temperature"),
                                                      kw.get("top_p"))
        body = self.provider.build_request(self.endpoint.model, messages, **kw)
        try:
            turn = self.provider.chat(self.client, body)
        except ProviderError as e:
            self.calls.append({"request": body, "error": {"status": e.status, "body": e.body}})
            raise
        self.used = _add(self.used, turn.usage)
        self.model_reported = turn.model or self.model_reported
        self.fingerprint = turn.system_fingerprint or self.fingerprint
        self.calls.append({"request": body, "turn": {
            "content": turn.content, "reasoning_content": turn.reasoning_content,
            "tool_calls": turn.tool_calls, "finish_reason": turn.finish_reason,
            "model": turn.model, "system_fingerprint": turn.system_fingerprint,
            "usage": vars(turn.usage)}})
        return turn


class Suite(ABC):
    name: str = "suite"
    version: str = "0"
    caps: Caps = Caps(max_prompt_tokens=50_000, max_output_tokens=8_000, max_call_prompt_tokens=20_000)

    @abstractmethod
    def items(self) -> list[Item]:
        ...

    @abstractmethod
    def run_item(self, ctx: Context, item: Item) -> ItemResult:
        ...


class Runner:
    def __init__(self, endpoint: Endpoint, prices: PriceTable, guard: SpendGuard, *,
                 records_dir: str | Path = "records", transcripts_dir: str | Path = "transcripts",
                 live: bool = False, allow_peak: bool = False,
                 clock: Callable[[], datetime] | None = None, settle_seconds: float = 0.0,
                 provider=deepseek):
        self.endpoint, self.prices, self.guard = endpoint, prices, guard
        self.records_dir, self.transcripts_dir = Path(records_dir), Path(transcripts_dir)
        self.live, self.allow_peak, self.provider = live, allow_peak, provider
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.settle_seconds = settle_seconds

    def _client(self, reservation) -> Client:
        return Client(self.endpoint.base_url, key_env=self.endpoint.key_env, live=self.live,
                      reservation=reservation)

    def _balance(self, batch: str) -> Decimal | None:
        with self._client(self.guard.readonly(batch)) as c:
            return self.provider.get_balance(c)

    def run_batch(self, suite: Suite, *, repeats: int = 1, thinking: bool = True,
                  effort: str | None = None, batch: str | None = None) -> dict:
        start = self.clock()
        batch = batch or f"{suite.name}-{start.strftime('%Y%m%dT%H%M%SZ')}"
        period = self.prices.period(start)
        if period == "peak" and not self.allow_peak:
            raise Refused(f"{start.isoformat()} is in the provider's peak window")
        model = self.endpoint.model
        items = suite.items()
        caps = suite.caps
        run_worst = self.prices.worst_case(model, period, caps.max_prompt_tokens
                                           + caps.max_call_prompt_tokens, caps.max_output_tokens)
        probe_worst = self.prices.worst_case(model, period, identity.PROBE_MAX_PROMPT,
                                             identity.PROBE_MAX_OUTPUT)
        batch_worst = run_worst * len(items) * repeats + probe_worst

        with self._client(self.guard.readonly(batch)) as c:
            before = self.provider.get_balance(c)
            names = identity.display_names(self.provider.list_models(c))
        reservation = self.guard.reserve(batch, batch_worst, before)

        spent = Decimal("0")
        alts = {m: Decimal("0") for m in self.prices.models if m != model}
        runs, stopped_for = 0, None
        with self._client(reservation) as client:
            turn = identity.probe(client, self.provider, model)
            cost = self.prices.cost(model, period, turn.usage)
            for m in alts:
                alts[m] += self.prices.cost(m, period, turn.usage)
            spent += cost
            self.guard.record(batch=batch, record_id=f"{batch}.identity", model=model,
                              period=period, price_table=self.prices.id, cost=cost)
            self._identity_line(batch, names, turn, period, cost)

            for item in items:
                for r in range(repeats):
                    now = self.clock()
                    p_now = self.prices.period(now)
                    if p_now == "peak" and not self.allow_peak:
                        stopped_for = f"a peak window began at or before {now.isoformat()}"
                        break
                    try:
                        self.guard.check_run(reservation, run_worst, spent)
                    except Refused as e:
                        stopped_for = f"the guard refused the next run: {e}"
                        break
                    ctx = Context(client, self.endpoint, caps, thinking=thinking, effort=effort,
                                  provider=self.provider)
                    try:
                        result = suite.run_item(ctx, item)
                    except CapReached as e:
                        result = ItemResult("stopped", str(e))
                    except ProviderError as e:
                        result = ItemResult("error", client.redact(str(e)))
                    cost = self.prices.cost(model, p_now, ctx.used)
                    for m in alts:
                        alts[m] += self.prices.cost(m, p_now, ctx.used)
                    spent += cost
                    runs += 1
                    self._run_line(batch, suite, item, r, ctx, result, thinking, effort,
                                   p_now, cost, client)
                if stopped_for:
                    break

        if self.settle_seconds:
            _time.sleep(self.settle_seconds)
        after = self._balance(batch)
        recon = reconcile(before, after, spent, alternatives=alts)
        summary = {"batch": batch, "ts_utc": rec.now_utc(), "suite": suite.name, "runs": runs,
                   "stopped_for": stopped_for, "balance_before": str(before),
                   "balance_after": str(after), "computed_usd": str(spent),
                   "billed_usd": None if recon.billed is None else str(recon.billed),
                   "reconciliation": recon.status, "tolerance_usd": str(recon.tolerance),
                   "detail": recon.detail, "reserved_usd": str(reservation.amount),
                   "price_table": self.prices.id, "live": self.live}
        self._append_json(self.records_dir / "batches.jsonl", summary)
        if recon.status == "mismatch":
            raise MeterMismatch(recon.detail)
        return summary

    # -- record lines -----------------------------------------------------------
    def _identity_line(self, batch, names, turn, period, cost) -> None:
        self._append_json(self.records_dir / "identity.jsonl", {
            "batch": batch, "ts_utc": rec.now_utc(), "model_sent": self.endpoint.model,
            "display_names": names, "model_reported": turn.model,
            "system_fingerprint": turn.system_fingerprint, "rate_period": period,
            "cost_usd": str(cost), "live": self.live})

    def _run_line(self, batch, suite, item, r, ctx, result, thinking, effort, period, cost,
                  client) -> None:
        record_id = f"{batch}.{item.id}.r{r}"
        sha = rec.save_transcript(self.transcripts_dir / batch, record_id,
                                  {"calls": ctx.calls, "result": vars(result)},
                                  redact=client.redact)
        line = rec.new_record(
            record_id=record_id, batch=batch, live=self.live, suite=suite.name,
            suite_version=suite.version, item=item.id, repeat=r,
            provider=self.endpoint.provider, base_url=self.endpoint.base_url,
            model_sent=self.endpoint.model, model_reported=ctx.model_reported,
            system_fingerprint=ctx.fingerprint, thinking=thinking,
            effort=effort if thinking else None, sampling=ctx.sampling,
            prompt_version=suite.version, calls=len(ctx.calls),
            usage={"cache_hit": ctx.used.cache_hit, "cache_miss": ctx.used.cache_miss,
                   "output": ctx.used.output, "reasoning": ctx.used.reasoning},
            price_table=self.prices.id, rate_period=period, cost_usd=str(cost),
            outcome={"status": result.status, "detail": result.detail, "data": result.data},
            transcript_sha256=sha)
        rec.append(self.records_dir / "runs" / f"{suite.name}.jsonl", line)
        self.guard.record(batch=batch, record_id=record_id, model=self.endpoint.model,
                          period=period, price_table=self.prices.id, cost=cost)

    @staticmethod
    def _append_json(path: Path, obj: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8", newline="\n") as f:
            f.write(rec.canonical(obj) + "\n")
