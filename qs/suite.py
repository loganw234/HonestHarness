"""The suite interface, and the runner that drives a batch.

A suite declares its items and its caps, and runs one item through a Context
that meters every call as it happens. The runner does the rest, the same way
against the fake endpoint and a live provider:

1. refuse to start while the last batch's reconciliation is not ok, until the
   lead acknowledges that batch by its id, or a later balance read reconciles
   it (a recheck);
2. refuse to start in a peak window, or within the peak margin before one,
   unless peak is allowed;
3. read the balance and the model list, under a read-only reservation. A
   failure here raises: nothing has been reserved or spent;
4. reserve the batch's worst case from the guard, which refuses what does not
   fit the ceiling or the balance. Without peak allowed, every run is priced
   at the start's rate period, plus one call's premium at the dearest period:
   the one call in flight when a window opens may be billed at peak, and the
   gate stops the batch at the call after it. With peak allowed, every run is
   priced at the dearest period in the table;
5. probe identity, then run each item and repeat:
   - the reservation is checked before each run;
   - before each call, unless peak is allowed, a call that would fall in a
     peak window, or within the margin before one, is refused, and the run
     and the batch stop;
   - after each call, its cost is priced at the period its reply arrived in
     and written to the spend file at once, so a later error loses no
     metered spend;
   - a request the server closes with no reply at all is retried after a
     delay, twice at most, and passes the peak gate again first. Each failed
     attempt is counted, the batch stops at its third, and its reservation
     covers three calls more for them;
   - any other error the meter cannot see past stops the batch: a transport
     failure, a reply without usage, or a stream cut short. So does a provider
     status the next request would meet too;
6. read the balance again, reconcile what was computed against what was
   billed, and write the batch's summary, whatever stopped the batch. When the
   bill exceeds the meter beyond tolerance, an adjustment line brings the
   spend file up to the bill. A mismatch raises after the summary is written,
   and so does a run record that could not be written.

Limits, each stated by the behaviour it concedes:
- an interrupt (Ctrl-C) ends a batch without its summary. Every call metered
  before it is in the spend file, and the next batch is not held;
- a call whose reply never arrives is billed, if at all, without a meter
  reading. Each attempt the server closed with no reply is counted in the run
  record's unmetered_calls; any other such failure stops the batch at once,
  and is counted nowhere but its stopped_for. A bill shows in the batch's
  reconciliation only beyond its tolerance: a billed drop inside it is in no
  spend line and no adjustment, so the spend file can fall short of the bill
  by up to the tolerance a batch, and the summary's unmetered_attempts and
  the run records' unmetered_calls are its only trace.
  When reconciliation is not ok, the summary's detail names the attempts
  closed with no reply; a recheck does not. Such a bill can even match
  another model's rates within tolerance, and read as a routing finding;
- the balance's precision and how soon it reflects a call are not documented
  (D18). A batch that moves the balance by less than the tolerance reconciles
  ok whatever its meter says, and a slow balance shows as a mismatch until a
  recheck;
- a batch run with concurrent=True is not reconciled alone and holds nothing.
  The flag is the operator's word that others spend from the same balance;
  the code cannot know it. Its reconciliation reads "concurrent", with no
  bill, no adjustment and a tolerance of "0", for nothing was checked, and a
  recheck refuses it. Its calls are metered as any batch's. Reconciling the
  marked batches together, against the balance and the usage export, is the
  lead's practice: no code here does it, and no record says it was done;
- public holidays are not in the price table's schedule, so a holiday is
  priced as an ordinary weekday;
- when the provider bills a call that spans a window's start is not
  documented. The meter prices a call at its reply's period. If the bill uses
  the send time, the meter over-counts that call, and a difference beyond the
  tolerance holds the next batch.
"""
from __future__ import annotations

import copy
import json
import re
import time as _time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Callable

from . import identity
from . import record as rec
from .client import Client, ProviderError
from .guard import Reconciliation, Refused, SpendGuard, reconcile
from .prices import PriceTable, Usage, usd
from .providers import deepseek
from .registry import Endpoint

ID_PATTERN = re.compile(r"[A-Za-z0-9._-]+")   # matched whole, so no trailing newline
DEFAULT_PEAK_MARGIN = timedelta(minutes=10)
# A request the server closed before sending any reply. Live, DeepSeek did this
# to 2 of about 31 requests of 64K tokens, 18 to 25 s in, at peak (the round's
# ledger, 19:11:24). Such a request is retried; any other transport error is not.
DISCONNECTED = "Server disconnected without sending a response"
DEFAULT_RETRY_DELAYS = (2.0, 5.0)     # seconds before the first and second retry
MAX_UNMETERED_PER_BATCH = 3           # failed attempts a batch may make before it stops
# A batch run beside others from the same balance: its balance change is
# theirs too, so it is not reconciled alone (the round's ledger, 09:32:39).
CONCURRENT = "concurrent"


def stops_batch(status: int) -> bool:
    """A provider status the next request would meet too: the key (401, 403),
    the balance (402), the rate limit (429) or the service (5xx), per D13.
    A 400 or 422 belongs to its one request."""
    return status in (401, 402, 403, 429) or status >= 500


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
    """A run's outcome. status, detail and data go into the published record;
    local goes into the run's local, gitignored transcript only, so bulky or
    model-written material (tool output, a model's text) stays out of what is
    published while its hash is."""
    status: str               # pass | fail | error | stopped | refused | skipped
    detail: str
    data: dict = field(default_factory=dict)
    local: dict = field(default_factory=dict)


class RunStopped(Exception):
    """A run ended by a limit the harness sets, not by the model or provider."""


class CapReached(RunStopped):
    pass


class PeakReached(RunStopped):
    pass


class BatchStopping(RunStopped):
    """A call refused because the run has already met a reason to stop the
    batch: a suite that retries cannot send past it."""


class MeterMismatch(Exception):
    def __init__(self, detail: str, summary: dict | None = None):
        super().__init__(detail)
        self.summary = summary


class Held(Refused):
    """A batch refused because the last batch's reconciliation is not ok."""


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
    """One item run's calls, metered as they happen.

    The thinking setting and effort are the batch's, so chat() takes neither: a
    record cannot claim a setting its calls did not use. max_tokens is the run's
    remaining output or less, and never more than the provider accepts.

    A failed call that leaves the meter uncertain, or a status the next request
    would meet too, sets stop_reason. A request the server closed with no reply
    sets it only once the call's retries, or the batch's allowance, are spent.
    From then on every call is refused with
    BatchStopping, before anything is sent, and the runner reads stop_reason
    whatever the suite returns: a suite that catches the error, or retries,
    can neither hide it nor send past it."""

    def __init__(self, client: Client, endpoint: Endpoint, caps: Caps, *, thinking: bool,
                 effort: str | None, provider=deepseek,
                 before_call: Callable[[], None] | None = None,
                 after_call: Callable[[Usage], tuple[Decimal, str]] | None = None,
                 on_unmetered: Callable[[], bool] | None = None,
                 retry_delays: tuple = DEFAULT_RETRY_DELAYS):
        self.client, self.endpoint, self.caps = client, endpoint, caps
        self.thinking, self.effort, self.provider = thinking, effort, provider
        self.before_call, self.after_call = before_call, after_call
        # on_unmetered counts a failed attempt against the batch's allowance and
        # says whether another may follow; without it, nothing is retried.
        self.on_unmetered, self.retry_delays = on_unmetered, tuple(retry_delays)
        self.unmetered = 0
        self.used = Usage(0, 0, 0, 0)
        self.cost = Decimal("0")
        self.periods: list[str] = []
        self.calls: list[dict] = []
        self.models_reported: list[str] = []
        self.fingerprints: list[str] = []
        self.sampling = {"sent": {}, "ignored": []}
        self.stop_reason: str | None = None
        self.stop_kind: str | None = None

    def _stop(self, reason: str, kind: str = "error") -> None:
        """kind is the status a pass or fail after this stop is recorded as:
        "stopped" for a limit the harness sets, "error" for a failed call."""
        if self.stop_reason is None:
            self.stop_reason, self.stop_kind = reason, kind

    def chat(self, messages: list[dict], **kw):
        if self.stop_reason is not None:
            raise BatchStopping(f"no further call: {self.stop_reason}")
        for k in ("thinking", "effort"):
            if k in kw:
                raise ValueError(f"{k} is the batch's setting; Context.chat does not take it")
        if self.used.prompt >= self.caps.max_prompt_tokens:
            raise CapReached(f"prompt cap reached: {self.used.prompt} of {self.caps.max_prompt_tokens}")
        if self.used.output >= self.caps.max_output_tokens:
            raise CapReached(f"output cap reached: {self.used.output} of {self.caps.max_output_tokens}")
        est = estimate_tokens(rec.canonical({"m": messages, "t": kw.get("tools")}))
        if est > self.caps.max_call_prompt_tokens:
            raise CapReached(f"a request of about {est} tokens exceeds the suite's declared "
                             f"largest, {self.caps.max_call_prompt_tokens}")
        kw["thinking"] = self.thinking
        if self.thinking and self.effort:
            kw["effort"] = self.effort
        left = self.caps.max_output_tokens - self.used.output
        limit = getattr(self.provider, "MAX_TOKENS", None) or left
        kw["max_tokens"] = min(kw.get("max_tokens") or left, left, limit)
        self.sampling = self.provider.sampling_record(kw["thinking"], kw.get("temperature"),
                                                      kw.get("top_p"))
        body = self.provider.build_request(self.endpoint.model, messages, **kw)
        # The record keeps each request as it was sent, whatever the suite later
        # does to the lists it passed (P2's finding, P2.md 12:52:07).
        sent = copy.deepcopy(body)
        attempt = 0
        while True:
            if self.before_call is not None:
                try:
                    self.before_call()
                except RunStopped as e:
                    self._stop(str(e), kind="stopped")
                    raise
            try:
                turn = self.provider.chat(self.client, body)
                turn.thinking = kw["thinking"]
                break
            except ProviderError as e:
                self.calls.append({"request": sent, "error": {"status": e.status, "body": e.body}})
                if stops_batch(e.status):
                    self._stop(f"the provider returned HTTP {e.status}")
                raise
            except Exception as e:
                self.calls.append({"request": sent,
                                   "error": {"type": type(e).__name__, "message": str(e)}})
                if DISCONNECTED in str(e):
                    # Closed with no reply: unmetered, perhaps billed. Retried
                    # while the batch's allowance and this call's delays last.
                    self.unmetered += 1
                    allowed = self.on_unmetered() if self.on_unmetered is not None else False
                    if allowed and attempt < len(self.retry_delays):
                        _time.sleep(self.retry_delays[attempt])
                        attempt += 1
                        continue
                self._stop(f"a reply did not arrive whole ({type(e).__name__}), "
                           "so its cost is unmetered")
                raise
        self.used = _add(self.used, turn.usage)
        cost, period = (self.after_call(turn.usage) if self.after_call is not None
                        else (Decimal("0"), "none"))
        self.cost += cost
        self.periods.append(period)
        if turn.model and turn.model not in self.models_reported:
            self.models_reported.append(turn.model)
        if turn.system_fingerprint and turn.system_fingerprint not in self.fingerprints:
            self.fingerprints.append(turn.system_fingerprint)
        self.calls.append({"request": sent, "turn": copy.deepcopy({
            "content": turn.content, "reasoning_content": turn.reasoning_content,
            "tool_calls": turn.tool_calls, "finish_reason": turn.finish_reason,
            "model": turn.model, "system_fingerprint": turn.system_fingerprint,
            "usage": vars(turn.usage)}), "cost_usd": usd(cost), "rate_period": period})
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


@dataclass
class _Tally:
    """A batch's metered spend, and the same usage priced as each other model."""
    spent: Decimal = Decimal("0")
    alts: dict = field(default_factory=dict)
    lines: int = 0
    unmetered: int = 0


class Runner:
    def __init__(self, endpoint: Endpoint, prices: PriceTable, guard: SpendGuard, *,
                 records_dir: str | Path = "records", transcripts_dir: str | Path = "transcripts",
                 live: bool = False, allow_peak: bool = False,
                 clock: Callable[[], datetime] | None = None, settle_seconds: float = 0.0,
                 provider=deepseek, peak_margin: timedelta = DEFAULT_PEAK_MARGIN,
                 retry_delays: tuple = DEFAULT_RETRY_DELAYS,
                 max_unmetered: int = MAX_UNMETERED_PER_BATCH, concurrent: bool = False,
                 code: dict | None = None):
        self.endpoint, self.prices, self.guard = endpoint, prices, guard
        # The code each batch records (record version 2): read from git as the
        # batch starts, unless given, as tests give it.
        self.code = code
        self.records_dir, self.transcripts_dir = Path(records_dir), Path(transcripts_dir)
        self.live, self.allow_peak, self.provider = live, allow_peak, provider
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.settle_seconds = settle_seconds
        self.peak_margin = peak_margin
        self.retry_delays, self.max_unmetered = tuple(retry_delays), max_unmetered
        self.concurrent = concurrent

    @property
    def batches_file(self) -> Path:
        return self.records_dir / "batches.jsonl"

    def _client(self, reservation) -> Client:
        return Client(self.endpoint.base_url, key_env=self.endpoint.key_env, live=self.live,
                      reservation=reservation)

    def _read_balance(self, batch: str) -> tuple[Decimal | None, str | None]:
        """The balance, or None and the redacted reason it could not be read."""
        try:
            c = self._client(self.guard.readonly(batch))
        except Exception as e:  # noqa: BLE001 - reported, never raised past here
            return None, f"{type(e).__name__}: {e}"
        try:
            return self.provider.get_balance(c), None
        except Exception as e:  # noqa: BLE001
            return None, f"{type(e).__name__}: {c.redact(str(e))}"
        finally:
            c.close()

    # -- the hold -------------------------------------------------------------------
    def _lines(self) -> list[dict]:
        p = self.batches_file
        if not p.exists():
            return []
        return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]

    def hold(self) -> dict | None:
        """The last batch's latest reconciliation, if it is neither ok nor
        concurrent and the lead has not acknowledged it; otherwise None. Only
        the last batch line is read, so a held batch with others' lines after
        it holds nothing."""
        lines = self._lines()
        last = next((x for x in reversed(lines) if x.get("kind", "batch") == "batch"), None)
        if last is None:
            return None
        latest = last
        for x in lines:
            if x.get("batch") != last["batch"]:
                continue
            if x.get("kind") == "acknowledge":
                return None
            if x.get("kind") == "recheck":
                latest = x
        return None if latest.get("reconciliation") in ("ok", CONCURRENT) else latest

    def _check_hold(self, acknowledge: str | None) -> dict | None:
        """The hold this batch's acknowledgment lifts, or None if there is no
        hold. A hold the caller does not name refuses the batch."""
        h = self.hold()
        if h is None:
            return None
        if acknowledge != h["batch"]:
            raise Held(f"batch {h['batch']} reconciled as {h['reconciliation']} "
                       f"({h.get('detail')}); acknowledge it by its id, or recheck it")
        return h

    def _acknowledge(self, h: dict, batch: str) -> None:
        """Written once the acknowledging batch holds its reservation, so a
        batch refused at its start lifts nothing."""
        self._append_json(self.batches_file, {
            "kind": "acknowledge", "batch": h["batch"], "ts_utc": rec.now_utc(),
            "reconciliation": h["reconciliation"], "by_batch": batch})

    def recheck(self, batch: str | None = None) -> dict:
        """Read the balance now and reconcile the last batch again, against
        its own opening balance. It is valid only while no later batch, and no
        other use of the key, has spent since: a stated limit. A concurrent
        batch is refused, since its balance change is others' too."""
        lines = self._lines()
        last = next((x for x in reversed(lines) if x.get("kind", "batch") == "batch"), None)
        if last is None:
            raise Refused("there is no batch to recheck")
        if batch is not None and batch != last["batch"]:
            raise Refused(f"only the last batch, {last['batch']}, can be rechecked")
        if last.get("reconciliation") == CONCURRENT:
            raise Refused(f"batch {last['batch']} ran concurrently with others: its balance "
                          "change is theirs too, so it is reconciled with them, not alone")
        after, err = self._read_balance(last["batch"])
        before = None if last.get("balance_before") in (None, "None") else Decimal(last["balance_before"])
        computed = Decimal(last["computed_usd"])
        alts = {k: Decimal(v) for k, v in (last.get("alternatives_usd") or {}).items()}
        recon = reconcile(before, after, computed, alternatives=alts)
        adjusted = self._adjust(last["batch"], recon)
        line = {"kind": "recheck", "batch": last["batch"], "ts_utc": rec.now_utc(),
                "balance_after": None if after is None else str(after),
                "computed_usd": usd(computed),
                "billed_usd": None if recon.billed is None else usd(recon.billed),
                "adjustment_usd": usd(adjusted), "reconciliation": recon.status,
                "tolerance_usd": usd(recon.tolerance),
                "detail": recon.detail if err is None else f"{recon.detail}; the read failed: {err}"}
        self._append_json(self.batches_file, line)
        return line

    def _adjust(self, batch: str, recon) -> Decimal:
        """When the bill exceeds what the spend file holds for the batch beyond
        tolerance, add the difference as an adjustment line, so the ceiling
        counts what was billed. A bill below the meter adds nothing."""
        if recon.billed is None or recon.status in ("ok", "topup"):
            return Decimal("0")
        held = self.guard.spent_in(batch)
        diff = recon.billed - held
        if diff <= recon.tolerance:
            return Decimal("0")
        self.guard.record(batch=batch, record_id=f"{batch}.adjustment", model=self.endpoint.model,
                          period="none", price_table=self.prices.id, cost=diff, kind="adjustment")
        return diff

    # -- metering -------------------------------------------------------------------
    def _gate(self) -> None:
        """Before each call: unless peak is allowed, no call in a peak window or
        within the margin before one."""
        if self.allow_peak:
            return
        now = self.clock()
        if self.prices.peak_within(now, self.peak_margin):
            raise PeakReached(f"a call at {now.isoformat()} would fall in a peak window, or "
                              f"within {self.peak_margin} of one")

    def _meter(self, batch: str, spend_id: str, usage: Usage, tally: _Tally) -> tuple[Decimal, str]:
        """Price one reply at the period it arrived in, and write its spend line."""
        model = self.endpoint.model
        period = self.prices.period(self.clock())
        cost = self.prices.cost(model, period, usage)
        for m in tally.alts:
            tally.alts[m] += self.prices.cost(m, period, usage)
        tally.spent += cost
        tally.lines += 1
        self.guard.record(batch=batch, record_id=spend_id, model=model, period=period,
                          price_table=self.prices.id, cost=cost)
        return cost, period

    def _unmetered_for(self, tally: _Tally):
        """Count one failed attempt against the batch's allowance; True while
        another may follow."""
        def unmetered() -> bool:
            tally.unmetered += 1
            return tally.unmetered < self.max_unmetered
        return unmetered

    def _meter_for(self, batch: str, record_id: str, tally: _Tally):
        n = 0

        def meter(usage: Usage) -> tuple[Decimal, str]:
            nonlocal n
            n += 1
            return self._meter(batch, f"{record_id}.c{n}", usage, tally)
        return meter

    # -- the batch ------------------------------------------------------------------
    def run_batch(self, suite: Suite, *, repeats: int = 1, thinking: bool = True,
                  effort: str | None = None, batch: str | None = None,
                  acknowledge: str | None = None) -> dict:
        start = self.clock()
        batch = batch or f"{suite.name}-{start.strftime('%Y%m%dT%H%M%SZ')}"
        items = suite.items()
        for name in [batch] + [i.id for i in items]:
            if not ID_PATTERN.fullmatch(name):
                raise ValueError(f"{name!r} is not a valid id: use letters, digits, '.', '_' or '-'")
        held = self._check_hold(acknowledge)
        if not self.allow_peak and self.prices.peak_within(start, self.peak_margin):
            raise Refused(f"{start.isoformat()} is in the provider's peak window, or within "
                          f"{self.peak_margin} of one")
        code = dict(self.code) if self.code is not None else rec.code_identity()
        model = self.endpoint.model
        caps = suite.caps
        periods = (sorted(self.prices.models[model]) if self.allow_peak
                   else [self.prices.period(start)])

        def worst(prompt: int, output: int) -> Decimal:
            return max(self.prices.worst_case(model, p, prompt, output) for p in periods)

        run_worst = worst(caps.max_prompt_tokens + caps.max_call_prompt_tokens,
                          caps.max_output_tokens)
        probe_worst = worst(identity.PROBE_MAX_PROMPT, identity.PROBE_MAX_OUTPUT)
        # The one call in flight when a window opens may be billed at peak; the
        # gate stops the batch at the call after it. Zero when peak is allowed.
        call_out = min(caps.max_output_tokens,
                       getattr(self.provider, "MAX_TOKENS", None) or caps.max_output_tokens)
        crossing = max(self.prices.worst_case(model, p, caps.max_call_prompt_tokens, call_out)
                       for p in self.prices.models[model]) - worst(caps.max_call_prompt_tokens,
                                                                   call_out)
        # Each attempt the server closes with no reply is unmetered and may be
        # billed; a batch allows max_unmetered of them, each at most the
        # dearest single call.
        unmetered_margin = self.max_unmetered * max(
            self.prices.worst_case(model, p, caps.max_call_prompt_tokens, call_out)
            for p in self.prices.models[model])
        batch_worst = (run_worst * len(items) * repeats + probe_worst + crossing
                       + unmetered_margin)

        with self._client(self.guard.readonly(batch)) as c:
            before = self.provider.get_balance(c)
            names = identity.display_names(self.provider.list_models(c))
        reservation = self.guard.reserve(batch, batch_worst, before)
        acknowledged = None
        if held is not None:
            self._acknowledge(held, batch)
            acknowledged = held["batch"]

        tally = _Tally(alts={m: Decimal("0") for m in self.prices.models if m != model})
        runs, stopped_for, record_error = 0, None, None
        with self._client(reservation) as client:
            stopped_for = self._probe(batch, client, names, tally)
            for item in items if stopped_for is None else []:
                for r in range(repeats):
                    now = self.clock()
                    if not self.allow_peak and self.prices.peak_within(now, self.peak_margin):
                        stopped_for = (f"a peak window begins within {self.peak_margin} of "
                                       f"{now.isoformat()}")
                        break
                    try:
                        self.guard.check_run(reservation, run_worst, tally.spent)
                    except Refused as e:
                        stopped_for = f"the guard refused the next run: {e}"
                        break
                    record_id = f"{batch}.{item.id}.r{r}"
                    ctx = Context(client, self.endpoint, caps, thinking=thinking, effort=effort,
                                  provider=self.provider, before_call=self._gate,
                                  after_call=self._meter_for(batch, record_id, tally),
                                  on_unmetered=self._unmetered_for(tally),
                                  retry_delays=self.retry_delays)
                    result = self._run_one(suite, ctx, item, client)
                    runs += 1
                    try:
                        self._run_line(batch, suite, item, r, record_id, ctx, result, thinking,
                                       effort, client, code)
                    except Exception as e:  # noqa: BLE001 - raised after the summary
                        record_error = e
                        stopped_for = f"a run record could not be written: {type(e).__name__}"
                    if ctx.stop_reason and not stopped_for:
                        stopped_for = ctx.stop_reason
                    if stopped_for:
                        break
                if stopped_for:
                    break

        if self.settle_seconds:
            _time.sleep(self.settle_seconds)
        after, read_error = self._read_balance(batch)
        if self.concurrent:
            recon = Reconciliation(CONCURRENT, tally.spent, None, Decimal("0"),
                                   "marked concurrent, so not reconciled alone: others may spend from "
                                   "the same balance meanwhile; for the lead to reconcile with the "
                                   "other marked batches")
            adjusted = Decimal("0")
        else:
            recon = reconcile(before, after, tally.spent, alternatives=tally.alts)
            adjusted = self._adjust(batch, recon)
        detail = recon.detail if read_error is None else (
            f"{recon.detail}; the closing balance read failed: {read_error}")
        if tally.unmetered and recon.status not in ("ok", CONCURRENT):
            # A bill raised by such attempts can even match another model's rates.
            detail += (f"; {tally.unmetered} attempt(s) closed with no reply may have "
                       "been billed without a meter reading")
        summary = {"kind": "batch", "batch": batch, "ts_utc": rec.now_utc(), "suite": suite.name,
                   "suite_version": suite.version, "runs": runs, "stopped_for": stopped_for,
                   "balance_before": str(before), "balance_after": None if after is None else str(after),
                   "computed_usd": usd(tally.spent),
                   "alternatives_usd": {m: usd(v) for m, v in tally.alts.items()},
                   "billed_usd": None if recon.billed is None else usd(recon.billed),
                   "adjustment_usd": usd(adjusted), "reconciliation": recon.status,
                   "tolerance_usd": usd(recon.tolerance), "detail": detail,
                   "reserved_usd": usd(reservation.amount), "reserved_at": periods,
                   "crossing_margin_usd": usd(crossing),
                   "unmetered_margin_usd": usd(unmetered_margin),
                   "unmetered_attempts": tally.unmetered,
                   "allow_peak": self.allow_peak, "concurrent": self.concurrent,
                   "peak_margin_minutes": int(self.peak_margin.total_seconds() // 60),
                   "spend_lines": tally.lines, "acknowledged": acknowledged,
                   "price_table": self.prices.id, "live": self.live, "code": code}
        self._append_json(self.batches_file, summary)
        if record_error is not None:
            raise record_error
        if recon.status == "mismatch":
            raise MeterMismatch(recon.detail, summary)
        return summary

    def _probe(self, batch: str, client: Client, names: dict, tally: _Tally) -> str | None:
        """The identity probe: metered like any call. A failure is recorded and
        stops the batch before its runs."""
        try:
            self._gate()
            turn = identity.probe(client, self.provider, self.endpoint.model)
        except Exception as e:  # noqa: BLE001 - recorded, and it stops the batch
            msg = f"{type(e).__name__}: {client.redact(str(e))}"
            self._identity_line(batch, names, None, "none", Decimal("0"), error=msg)
            return f"the identity probe failed: {msg}"
        cost, period = self._meter(batch, f"{batch}.identity", turn.usage, tally)
        self._identity_line(batch, names, turn, period, cost)
        return None

    def _run_one(self, suite: Suite, ctx: Context, item: Item, client: Client) -> ItemResult:
        try:
            return suite.run_item(ctx, item)
        except RunStopped as e:
            return ItemResult("stopped", str(e))
        except ProviderError as e:
            return ItemResult("error", client.redact(str(e)))
        except Exception as e:  # noqa: BLE001 - a run's error is its record's outcome
            return ItemResult("error", f"{type(e).__name__}: {client.redact(str(e))}")

    # -- record lines -----------------------------------------------------------------
    def _identity_line(self, batch, names, turn, period, cost, error: str | None = None) -> None:
        self._append_json(self.records_dir / "identity.jsonl", {
            "batch": batch, "ts_utc": rec.now_utc(), "model_sent": self.endpoint.model,
            "display_names": names, "model_reported": turn.model if turn else None,
            "system_fingerprint": turn.system_fingerprint if turn else None,
            "rate_period": period, "cost_usd": usd(cost), "error": error, "live": self.live})

    def _run_line(self, batch, suite, item, r, record_id, ctx, result, thinking, effort,
                  client, code: dict) -> None:
        sha = rec.save_transcript(self.transcripts_dir / batch, record_id,
                                  {"calls": ctx.calls, "result": vars(result)},
                                  redact=client.redact)
        periods = set(ctx.periods)
        period = "none" if not periods else (periods.pop() if len(periods) == 1 else "mixed")
        outcome = {"status": result.status, "detail": result.detail, "data": result.data}
        if ctx.stop_reason and result.status in ("pass", "fail"):
            # A pass or fail after a stop is not the model's: the stop is recorded
            # as what the run was, with the suite's own verdict kept beside it.
            outcome = {"status": ctx.stop_kind or "error",
                       "detail": (f"{ctx.stop_reason}; the suite returned "
                                  f"{result.status}: {result.detail}"),
                       "data": result.data}
        line = rec.new_record(
            record_id=record_id, batch=batch, live=self.live, suite=suite.name,
            suite_version=suite.version, item=item.id, repeat=r,
            provider=self.endpoint.provider, base_url=self.endpoint.base_url,
            model_sent=self.endpoint.model, model_reported=ctx.models_reported,
            system_fingerprint=ctx.fingerprints, thinking=thinking,
            effort=effort if thinking else None, sampling=ctx.sampling,
            prompt_version=suite.version, caps=asdict(suite.caps), calls=len(ctx.calls),
            usage={"cache_hit": ctx.used.cache_hit, "cache_miss": ctx.used.cache_miss,
                   "output": ctx.used.output, "reasoning": ctx.used.reasoning},
            price_table=self.prices.id, rate_period=period, cost_usd=usd(ctx.cost),
            outcome=outcome, stop_reason=ctx.stop_reason, unmetered_calls=ctx.unmetered,
            transcript_sha256=sha,
            code={"commit": code["commit"], "changed": code["changed"],
                  "tools_sha256": rec.tools_digest(ctx.calls)})
        rec.append(self.records_dir / "runs" / f"{suite.name}.jsonl", line)

    @staticmethod
    def _append_json(path: Path, obj: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8", newline="\n") as f:
            f.write(rec.canonical(obj) + "\n")
