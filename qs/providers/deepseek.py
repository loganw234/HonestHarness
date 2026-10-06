"""DeepSeek's API, beyond the OpenAI format.

From DeepSeek's docs, read 2026-10-06 (the plan's D8-D18):
- thinking is a top-level request field, {"thinking": {"type": "enabled" |
  "disabled"}}, on by default; reasoning_effort takes low, high or max;
- with tools in the request, every earlier assistant turn's reasoning_content
  must be passed back, or the API returns 400;
- tool_choice "required" or a named function returns 400 in thinking mode;
- in thinking mode temperature has no effect and top_p below 0.95 is treated
  as 0.95; in non-thinking mode temperature applies and top_p is fixed at 1.0;
- usage reports prompt_cache_hit_tokens and prompt_cache_miss_tokens, and
  completion_tokens_details.reasoning_tokens;
- finish reasons include insufficient_system_resource and aborted;
- streams carry ": keep-alive" comments, and usage arrives on the last chunk
  before "data: [DONE]";
- max_tokens must be between 1 and 393216 (D10; the model list's
  max_output_tokens, D17).

A reply without its usage, or a stream that ends before its usage and
[DONE], raises IncompleteReply: the call may have been billed, and the meter
cannot say for how much.

What the docs leave open is marked where the code meets it: P0's first live
calls confirm or correct each.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Iterable

from ..prices import Usage

FINISH_REASONS = frozenset({"stop", "length", "tool_calls", "content_filter",
                            "insufficient_system_resource", "aborted"})
EFFORTS = frozenset({"low", "high", "max"})
MAX_TOKENS = 393216   # "between 1 and 384K (393216)", D10


class IncompleteReply(Exception):
    """A reply that arrived without its usage: billed, perhaps, but unmetered."""


@dataclass
class Turn:
    content: str | None
    reasoning_content: str | None
    tool_calls: list[dict] = field(default_factory=list)
    finish_reason: str | None = None
    usage: Usage = field(default_factory=lambda: Usage(0, 0, 0, 0))
    model: str | None = None
    system_fingerprint: str | None = None
    # Set by Context.chat from the request: whether thinking was on. None for a
    # turn made outside a Context, such as a test's. Last, so positional use of
    # the fields above is unchanged.
    thinking: bool | None = None


def build_request(model: str, messages: list[dict], *, thinking: bool = True,
                  effort: str | None = None, tools: list[dict] | None = None,
                  tool_choice=None, stream: bool = False, max_tokens: int | None = None,
                  temperature: float | None = None, top_p: float | None = None,
                  response_format: dict | None = None) -> dict:
    """A request body. It sends what the caller asks, documented-refused
    combinations included: a suite that tests a refusal must be able to make
    the request."""
    if effort is not None and effort not in EFFORTS:
        raise ValueError(f"reasoning_effort must be one of {sorted(EFFORTS)}")
    body: dict = {"model": model, "messages": messages,
                  "thinking": {"type": "enabled" if thinking else "disabled"}}
    if thinking and effort:
        body["reasoning_effort"] = effort
    if tools:
        body["tools"] = tools
    if tool_choice is not None:
        body["tool_choice"] = tool_choice
    if stream:
        body["stream"] = True
    if max_tokens is not None:
        body["max_tokens"] = max_tokens
    if temperature is not None:
        body["temperature"] = temperature
    if top_p is not None:
        body["top_p"] = top_p
    if response_format is not None:
        body["response_format"] = response_format
    return body


def sampling_record(thinking: bool, temperature: float | None, top_p: float | None) -> dict:
    """What was sent, and which of it the API documents as ignored or fixed."""
    sent = {k: v for k, v in (("temperature", temperature), ("top_p", top_p)) if v is not None}
    ignored = []
    if thinking:
        if temperature is not None:
            ignored.append("temperature (no effect in thinking mode)")
        if top_p is not None and top_p < 0.95:
            ignored.append("top_p (treated as 0.95 in thinking mode)")
    elif top_p is not None:
        ignored.append("top_p (fixed at 1.0 in non-thinking mode)")
    return {"sent": sent, "ignored": ignored}


def documented_refusal(thinking: bool, tool_choice) -> str | None:
    """The 400 DeepSeek documents for this combination, if any."""
    if thinking and (tool_choice == "required" or isinstance(tool_choice, dict)):
        return "tool_choice required or named is refused in thinking mode (400)"
    return None


def parse_usage(u: dict | None) -> Usage:
    u = u or {}
    prompt = int(u.get("prompt_tokens", 0) or 0)
    if "prompt_cache_hit_tokens" in u or "prompt_cache_miss_tokens" in u:
        hit = int(u.get("prompt_cache_hit_tokens", 0) or 0)
        miss = int(u.get("prompt_cache_miss_tokens", max(prompt - hit, 0)) or 0)
    else:  # the OpenAI form, which other providers and the fake may send
        hit = int((u.get("prompt_tokens_details") or {}).get("cached_tokens", 0) or 0)
        miss = max(prompt - hit, 0)
    output = int(u.get("completion_tokens", 0) or 0)
    reasoning = int((u.get("completion_tokens_details") or {}).get("reasoning_tokens", 0) or 0)
    return Usage(cache_hit=hit, cache_miss=miss, output=output, reasoning=reasoning)


def parse_response(data: dict) -> Turn:
    if not data.get("usage"):
        raise IncompleteReply("the reply carried no usage")
    choice = (data.get("choices") or [{}])[0]
    msg = choice.get("message") or {}
    return Turn(content=msg.get("content"), reasoning_content=msg.get("reasoning_content"),
                tool_calls=list(msg.get("tool_calls") or []),
                finish_reason=choice.get("finish_reason"), usage=parse_usage(data.get("usage")),
                model=data.get("model"), system_fingerprint=data.get("system_fingerprint"))


def parse_stream(lines: Iterable[str]) -> Turn:
    """Accumulate a server-sent-event stream into one turn. Blank lines and
    comment lines (": keep-alive") are skipped; usage is taken from whichever
    chunk carries it. A stream that ends before [DONE], or without usage,
    raises IncompleteReply."""
    content, reasoning = [], []
    calls: dict[int, dict] = {}
    turn = Turn(content=None, reasoning_content=None)
    done = usage_seen = False
    for line in lines:
        s = line.strip()
        if not s or s.startswith(":"):
            continue
        if not s.startswith("data:"):
            continue
        payload = s[5:].strip()
        if payload == "[DONE]":
            done = True
            break
        chunk = json.loads(payload)
        turn.model = chunk.get("model", turn.model)
        turn.system_fingerprint = chunk.get("system_fingerprint", turn.system_fingerprint)
        if chunk.get("usage"):
            turn.usage = parse_usage(chunk["usage"])
            usage_seen = True
        for choice in chunk.get("choices") or []:
            delta = choice.get("delta") or {}
            if delta.get("content"):
                content.append(delta["content"])
            if delta.get("reasoning_content"):
                reasoning.append(delta["reasoning_content"])
            for tc in delta.get("tool_calls") or []:
                i = tc.get("index", 0)
                slot = calls.setdefault(i, {"id": None, "type": "function",
                                            "function": {"name": "", "arguments": ""}})
                if tc.get("id"):
                    slot["id"] = tc["id"]
                fn = tc.get("function") or {}
                if fn.get("name"):
                    slot["function"]["name"] += fn["name"]
                if fn.get("arguments"):
                    slot["function"]["arguments"] += fn["arguments"]
            if choice.get("finish_reason"):
                turn.finish_reason = choice["finish_reason"]
    if not done:
        raise IncompleteReply("the stream ended before [DONE]")
    if not usage_seen:
        raise IncompleteReply("the stream carried no usage")
    turn.content = "".join(content) if content else None
    turn.reasoning_content = "".join(reasoning) if reasoning else None
    turn.tool_calls = [calls[i] for i in sorted(calls)]
    return turn


def assistant_message(turn: Turn, *, tools_in_request: bool) -> dict:
    """The assistant turn to carry into the next request. With tools in the
    request, its reasoning_content goes back too (D8). A thinking-mode turn the
    model gave no reasoning goes back with "", as D8's own streaming sample
    builds the field (thinking.txt:49): a stream that carried no reasoning
    parses to None, and leaving the field out would meet D8's 400 (P1's
    finding, P1.md 15:03:47)."""
    msg: dict = {"role": "assistant", "content": turn.content}
    if turn.tool_calls:
        msg["tool_calls"] = turn.tool_calls
    if tools_in_request:
        if turn.reasoning_content is not None:
            msg["reasoning_content"] = turn.reasoning_content
        elif turn.thinking:
            msg["reasoning_content"] = ""
    return msg


def chat(client, body: dict) -> Turn:
    if body.get("stream"):
        return parse_stream(client.stream_lines("/chat/completions", body))
    return parse_response(client.post("/chat/completions", body))


def list_models(client) -> list[dict]:
    return list(client.get("/models").get("data") or [])


def get_balance(client, currency: str = "USD") -> Decimal | None:
    """The total balance in the given currency, or None if the account reports
    none in it. The response shape is DeepSeek's documented example (D18);
    P0's first live read confirms it."""
    data = client.get("/user/balance")
    for info in data.get("balance_infos") or []:
        if info.get("currency") == currency:
            return Decimal(str(info.get("total_balance")))
    return None
