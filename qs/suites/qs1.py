"""QS1: tool calls through a provider's API (TC section 7.8, with 7.4's leak list
and 7.7's ids and history).

QS1 measures whether a model's tool calls through DeepSeek's Chat Completions
API are well formed and right. The lead runs it once per thinking setting:

    python tools/live.py qs.suites.qs1:QS1 --repeats 3 --thinking on --effort high
    python tools/live.py qs.suites.qs1:QS1 --repeats 3 --thinking off

The cases and their goldens are in qs1_cases.json, beside this file. They are
written by hand from DeepSeek's documented format (D10, ds/chat_completion_full
.txt:561-590 for a reply, :826-871 for a stream) and each case's prompt, never
recorded from a model. Every request carries the same system prompt and the
same six tools, in the same order (TC 7.7). An item is a case run streamed or
not: <id> or <id>.stream. QS1.version holds a hash of the case file and of this
file, so a record names the exact prompts, goldens and judge behind it.

A run
- Each golden turn is one call to Context.chat, the only way QS1 reaches a
  model. Context keeps each request as it was sent (P0 fix 4), so a run keeps
  one message list and appends to it.
- After a turn that passed, the model's own turn goes back through the
  adapter's assistant_message(turn, tools_in_request=True), so its
  reasoning_content goes back with it (D8, ds/thinking.txt:54). One tool result
  per call follows, in the model's call order, each the canned result of the
  golden call it matched. QS1 writes no assistant message itself, except in the
  one hand-written history kept as a case, multiturn.handwritten.
- An item stops at its first failing turn: later turns are not reached.

The statuses, in order of precedence
- stopped: a harness limit ended the run. That is CapReached, PeakReached or
  BatchStopping, or a `length` finish whose output reached the max_tokens the
  harness sent: Context clamps it to what is left of the run's output.
- refused: the provider refused the request as its docs say it would in this
  mode. Never a model failure.
  - Thinking mode's 400 for tool_choice required or named (D10,
    ds/chat_completion_full.txt:463-466), and for an assistant turn sent back
    without its reasoning, which the hand-written history is (D8,
    ds/thinking.txt:54). documented.matches is true.
  - The hand-written history refused with 400 or 422 in non-thinking mode,
    which D9 calls unsupported without naming a status (ds/tool_calls.txt:
    29-32). documented.matches is null.
- error: the provider, not the model. That is a provider condition
  (insufficient_system_resource, aborted or content_filter, D10:545-558, or a
  `length` finish below the request's max_tokens), an HTTP status the docs do
  not give for the request, or a reply that never arrived whole. When the cause
  also stops the batch, ctx.stop_reason stops it whatever QS1 returns.
- fail: an assertion failed on a judged turn. outcome.data's `failed` names
  each one.
- pass: every assertion held on every turn, to the case's end.
A 200 where a 400 is documented is judged by the turn's golden, and
documented.matches false records the finding about the docs.

The assertions, on each judged turn: its request returned 200, and its
finish_reason is neither `length` nor a provider condition.
- name_args: every call is well formed (D10:569-590): type "function", a string
  name, and arguments that parse as a JSON object. Then the golden:
  - "none": no call, and a non-blank content;
  - "calls": the golden's calls, matched one to one (in any order where the
    golden says so): the same name, every argument the golden names satisfying
    its matcher, and no argument it does not name;
  - "any_declared" (tool_choice required): one call or more, each to a tool
    the request declared, with schema-valid arguments.
- special_tokens: none of SPECIAL_TOKENS in content, nor in a call's name or
  arguments. Reasoning is scanned and its hits recorded, not asserted.
- reasoning: in thinking mode, reasoning_content is a non-blank string, and
  content holds no <think> or </think> and does not repeat the reasoning's
  first LEAK_SPAN characters, when the reasoning has LEAK_MIN or more. In
  non-thinking mode, reasoning_content is absent, null or blank, and content
  holds neither marker.
- ids: every call has a non-empty string id, the ids in a turn are distinct,
  and a later request that carries them, with one tool result per call, is
  accepted. A 400 or 422 there fails this assertion on the last turn whose
  ids it was the first to carry.
- finish_reason: tool_calls on a turn with calls, stop on one without. A value
  outside the provider's documented FINISH_REASONS fails.

The metrics. metrics() pools the outcome.data of one model, provider and
thinking setting, across items and repeats.
- Schema accuracy = valid calls / all calls in judged turns; null when there
  are none. A call is valid when its name is declared in its request and its
  arguments parse as a JSON object that validates against the tool's
  parameters under JSON Schema 2020-12. A tool declared without parameters
  takes an object with no properties and no others (D10:434-436). Every
  tool_choice counts.
- Trigger similarity, K2VV-style, over judged turns whose tool_choice is auto,
  sent or by default (D10:459-462): the turns where the model decides. A turn
  is golden-positive when its golden expects calls, and observed-positive when
  it carries one call or more. Trigger F1 = 2TP / (2TP + FP + FN), null when
  that denominator is 0. Trigger agreement = (TP + TN) / N, with N = TP + FP +
  FN + TN, null at 0. Forced turns (none, required and named) are left out:
  their calls are the API's doing, and name_args judges them.

outcome.data holds no model-generated text: only the suite's own words, enums,
numbers and booleans. A provider's error body is kept, cut to ERROR_BODY
characters, as P0 keeps it. So a reply that looks like a key, an address or a
home path cannot reach a published record. The model's text stays in the local
transcript, whose hash the record carries.

Caps: Caps(max_prompt_tokens=20_000, max_output_tokens=12_000,
max_call_prompt_tokens=16_000), the same in both modes. At 35 items and 3
repeats, from an off-peak start, the runner reserves $1.3326192 per setting.
With --allow-peak it reserves $2.6460384. tests/test_qs1.py holds both.

Limits, each stated by the behaviour it concedes:
1. Reasoning paraphrased into content passes: the leak check is the markers and
   a verbatim overlap.
2. Only SPECIAL_TOKENS are caught. Another family's token, or a listed one split
   by whitespace, passes. Reasoning is scanned and recorded, not asserted.
3. In a stream every call reads as type "function", the adapter's default when
   it accumulates deltas, so the type check holds only for unstreamed replies.
4. The goldens accept only the variations they state. A semantically right call
   outside them fails, and its reason names the argument.
5. An item stops at its first failing turn, so a failed item has no judgement
   of its later turns, and no metric inputs from them.
6. Trigger similarity counts auto turns only.
7. QS1 judges the raw arguments and repairs nothing. TC 7.4's repair pipeline
   belongs to a harness, not to a test.
8. Context's token estimate, two characters a token, undercounts CJK text, at
   about 0.6 tokens a Chinese character (ds/quick_start_token_usage.txt:12).
   QS1's CJK text is a few dozen characters.
9. A table reads how a reply was judged, never what the model said.
10. No sampling parameter is sent, so non-thinking mode samples at the API's
    default temperature, 1 (D10:393-398), and repeats vary as that makes them.
11. The documented expectations are DeepSeek's, from its docs as read on
    2026-10-06. Another provider needs its own.
12. A documented refusal is known by its status alone. A 400 at turn 1 of a
    documented case is recorded refused whatever its cause, so a request
    refused for another reason reads as the documented refusal. The record's
    detail keeps the provider's reason, cut to ERROR_BODY characters, for a
    reader to check.
"""
from __future__ import annotations

import copy
import hashlib
import itertools
import json
import re
import unicodedata
from pathlib import Path

import jsonschema

from ..client import ProviderError
from ..suite import ID_PATTERN, Caps, Item, ItemResult, RunStopped, Suite

CASES_PATH = Path(__file__).with_name("qs1_cases.json")
ASSERTIONS = ("name_args", "special_tokens", "reasoning", "ids", "finish_reason")
EXPECTS = frozenset({"calls", "none", "any_declared"})

# TC 7.4's list (Research/open-weight-harness-research.md:530). Its <｜DSML｜ is
# matched as ｜DSML｜, so that DSML's closing tags and V4.1's leading-space form
# are caught too (TC 3.4). Then DeepSeek's own tokens, from TC 3.4 and 2, which
# transcribe its encoding README and V3's format. Then the ASCII lookalike TC 3.4
# reports (F10). A test holds that each one is in the research file verbatim.
SPECIAL_TOKENS = (
    "<|tool_call_begin|>",
    "<tool_call>",
    "｜DSML｜",
    "<minimax:tool_call>",
    "[TOOL_CALLS]",
    "<|start|>assistant",
    "<｜tool▁calls▁begin｜>",
    "<｜tool▁call▁begin｜>",
    "<｜tool▁sep｜>",
    "<｜tool▁call▁end｜>",
    "<｜tool▁calls▁end｜>",
    "<｜tool▁outputs▁begin｜>",
    "<｜end▁of▁sentence｜>",
    "|DSML|",
)
THINK_MARKERS = ("<think>", "</think>")
PROVIDER_CONDITIONS = frozenset({"insufficient_system_resource", "aborted", "content_filter"})
REFUSALS = (400, 422)          # a request refused as malformed or invalid (D13)
LEAK_MIN, LEAK_SPAN = 40, 80   # reasoning this long, repeated this far, is a leak
ERROR_BODY = 200               # characters of a provider's error body kept
EMPTY_PARAMETERS = {"type": "object", "properties": {}, "additionalProperties": False}
_ABSENT = object()


def _sha12(path: Path) -> str:
    """A file's identity, unchanged by a checkout's line endings."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()[:12]


def load_cases(path: Path = CASES_PATH) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def expand(data: dict) -> list[dict]:
    """One item per case and stream setting: <id> unstreamed, <id>.stream
    streamed."""
    out = []
    for case in data["cases"]:
        for stream in case["streams"]:
            out.append(dict(case, stream=bool(stream),
                            item=case["id"] + (".stream" if stream else "")))
    return out


# -- matchers ----------------------------------------------------------------------
def _text(s: str, m: dict) -> str:
    if m.get("nfc"):
        s = unicodedata.normalize("NFC", s)
    if m.get("strip"):
        s = s.strip()
    if m.get("casefold"):
        s = s.casefold()
    return s


def match_value(m: dict, v) -> str | None:
    """None when v satisfies the matcher m, else why not. A reason is in the
    suite's own words, and never quotes v, which is the model's."""
    if "absent_or" in m:
        return None if v is _ABSENT else match_value(m["absent_or"], v)
    if v is _ABSENT:
        return "is missing"
    if "equals" in m:
        want = m["equals"]
        if isinstance(want, str):
            if not isinstance(v, str):
                return "is not a string"
            got, want = _text(v, m), _text(want, m)
            if got == want:
                return None
            if (m.get("trailing_newline") and got.rstrip("\n") == want.rstrip("\n")
                    and abs(len(got) - len(want)) <= 1):
                return None
            return "differs from the golden"
        return None if type(v) is type(want) and v == want else "differs from the golden"
    if "match" in m:
        if not isinstance(v, str):
            return "is not a string"
        return None if re.fullmatch(m["match"], v, re.DOTALL) else "does not match the golden's pattern"
    if "one_of" in m:
        if not isinstance(v, str):
            return "is not a string"
        return None if _text(v, m) in {_text(x, m) for x in m["one_of"]} else "is none of the golden's values"
    if "object" in m:
        if not isinstance(v, dict):
            return "is not an object"
        return match_object(m["object"], v)
    if "items_any_order" in m:
        want = m["items_any_order"]
        if not isinstance(v, list):
            return "is not an array"
        if len(v) != len(want):
            return f"has {len(v)} items where the golden has {len(want)}"
        if assign(want, v, lambda g, x: match_value(g, x) is None) is None:
            return "has items that match the golden's in no order"
        return None
    raise ValueError(f"an unknown matcher: {sorted(m)}")


def match_object(spec: dict, obj: dict) -> str | None:
    """Every key the golden names satisfies its matcher, and no other key is
    present. A reason names only the golden's own keys."""
    for key, m in spec.items():
        why = match_value(m, obj.get(key, _ABSENT))
        if why:
            return f"{key} {why}"
    extra = sum(1 for k in obj if k not in spec)
    return f"{extra} key(s) the golden does not name" if extra else None


def assign(golden: list, observed: list, ok, any_order: bool = True) -> list[int] | None:
    """A one-to-one assignment: for each observed item, the index of the golden
    item it matches; None when there is none. A turn holds a few calls, so every
    order is tried."""
    if len(golden) != len(observed):
        return None
    orders = itertools.permutations(range(len(golden))) if any_order else [range(len(golden))]
    for perm in orders:
        perm = list(perm)
        if all(ok(golden[perm[j]], observed[j]) for j in range(len(observed))):
            return perm
    return None


# -- calls ---------------------------------------------------------------------------
def _fn(call) -> dict:
    fn = call.get("function") if isinstance(call, dict) else None
    return fn if isinstance(fn, dict) else {}


def parse_arguments(call) -> tuple[dict | None, str | None]:
    """A call's arguments as a JSON object, or why they are not one."""
    raw = _fn(call).get("arguments")
    if not isinstance(raw, str):
        return None, "arguments are not a string"
    try:
        args = json.loads(raw)
    except ValueError:
        return None, "arguments are not JSON"
    if not isinstance(args, dict):
        return None, "arguments are JSON but not an object"
    return args, None


def schema_valid(call, declared: dict) -> bool:
    """Schema accuracy's test: a declared name, and arguments that parse as a
    JSON object valid against the tool's parameters (JSON Schema 2020-12)."""
    name = _fn(call).get("name")
    if not isinstance(name, str) or name not in declared:
        return False
    args, why = parse_arguments(call)
    if why:
        return False
    schema = declared[name].get("parameters", EMPTY_PARAMETERS)
    return jsonschema.Draft202012Validator(schema).is_valid(args)


def match_call(golden: dict, call) -> str | None:
    if _fn(call).get("name") != golden["name"]:
        return "the call names another tool"
    args, why = parse_arguments(call)
    if why:
        return why
    return match_object(golden["args"], args)


# -- the assertions --------------------------------------------------------------------
def judge_name_args(golden: dict, calls: list, content, declared: dict):
    """(result, why, pairs). pairs maps each observed call to the index of the
    golden call it matched, when the golden is a list of calls and all match."""
    for i, c in enumerate(calls, 1):
        if not isinstance(c, dict) or c.get("type") != "function":
            return "fail", f"call {i}: its type is not function", None
        if not isinstance(_fn(c).get("name"), str):
            return "fail", f"call {i}: it has no function name", None
        _, why = parse_arguments(c)
        if why:
            return "fail", f"call {i}: its {why}", None
    expect = golden["expect"]
    if expect == "none":
        if calls:
            return "fail", f"{len(calls)} call(s) where the golden expects none", None
        if not isinstance(content, str) or not content.strip():
            return "fail", "no call, and a blank content", None
        return "pass", "no call, and an answer", None
    if expect == "any_declared":
        if not calls:
            return "fail", "no call where tool_choice requires one", None
        for i, c in enumerate(calls, 1):
            name = _fn(c)["name"]
            if name not in declared:
                return "fail", f"call {i}: it names a tool the request did not declare", None
            if not schema_valid(c, declared):
                return "fail", f"call {i}: its arguments fail {name}'s schema", None
        return "pass", f"{len(calls)} call(s) to declared tools, schema-valid", None
    want = golden["calls"]
    if len(calls) != len(want):
        return "fail", f"{len(calls)} call(s) where the golden has {len(want)}", None
    pairs = assign(want, calls, lambda g, c: match_call(g, c) is None,
                   any_order=golden.get("order", "any") == "any")
    if pairs is not None:
        return "pass", f"{len(calls)} call(s) match the golden", pairs
    for k, g in enumerate(want, 1):
        whys = [match_call(g, c) for c in calls]
        if all(whys):
            same = [w for c, w in zip(calls, whys) if _fn(c)["name"] == g["name"]]
            return "fail", (f"the golden's call {k}, to {g['name']}: "
                            + (same[0] if same else "no call names it")), None
    return "fail", "the calls match the golden's in no order", None


def find_tokens(text) -> list[str]:
    return [t for t in SPECIAL_TOKENS if isinstance(text, str) and t in text]


def judge_special_tokens(content, calls: list):
    places = [("content", content)]
    for i, c in enumerate(calls, 1):
        fn = _fn(c)
        places += [(f"call {i}'s name", fn.get("name")), (f"call {i}'s arguments", fn.get("arguments"))]
    for where, text in places:
        hits = find_tokens(text)
        if hits:
            return "fail", f"{where} holds {hits[0]}"
    return "pass", "no special token"


def judge_reasoning(content, reasoning, thinking: bool):
    text = content if isinstance(content, str) else ""
    for mark in THINK_MARKERS:
        if mark in text:
            return "fail", f"content holds {mark}"
    if thinking:
        if not isinstance(reasoning, str) or not reasoning.strip():
            return "fail", "no reasoning_content in thinking mode"
        r = reasoning.strip()
        if len(r) >= LEAK_MIN and r[:LEAK_SPAN] in text:
            return "fail", "content repeats the reasoning"
        return "pass", "reasoning present, apart from content"
    if reasoning is None or (isinstance(reasoning, str) and not reasoning.strip()):
        return "pass", "no reasoning, as in non-thinking mode"
    return "fail", "reasoning_content in non-thinking mode"


def judge_ids(calls: list):
    if not calls:
        return "not_judged", "no calls"
    ids = [c.get("id") if isinstance(c, dict) else None for c in calls]
    for i, x in enumerate(ids, 1):
        if not isinstance(x, str) or not x:
            return "fail", f"call {i} has no id"
    if len(set(ids)) != len(ids):
        return "fail", "two calls in the turn share an id"
    return "pass", f"{len(ids)} distinct id(s)"


def judge_finish(finish, calls: list, documented: frozenset):
    if not isinstance(finish, str) or finish not in documented:
        return "fail", "a finish_reason outside the documented set"
    if calls and finish != "tool_calls":
        return "fail", f"{finish} on a turn with {len(calls)} call(s)"
    if not calls and finish != "stop":
        return "fail", f"{finish} on a turn without calls"
    return "pass", finish


# -- the metrics ------------------------------------------------------------------------
def metrics(datas) -> dict:
    """Pool the outcome.data of QS1 records (one model, provider and thinking
    setting) into schema accuracy and trigger similarity, with their counts."""
    t = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
    calls = valid = 0
    for d in datas:
        mi = (d or {}).get("metric_inputs") or {}
        for k in t:
            t[k] += int((mi.get("trigger") or {}).get(k, 0))
        calls += int((mi.get("schema") or {}).get("calls", 0))
        valid += int((mi.get("schema") or {}).get("valid", 0))
    f1_den = 2 * t["tp"] + t["fp"] + t["fn"]
    n = t["tp"] + t["fp"] + t["fn"] + t["tn"]
    return {
        "trigger": dict(t, n=n, f1_denominator=f1_den,
                        f1=None if f1_den == 0 else 2 * t["tp"] / f1_den,
                        agreement=None if n == 0 else (t["tp"] + t["tn"]) / n),
        "schema": {"calls": calls, "valid": valid,
                   "accuracy": None if calls == 0 else valid / calls},
    }


# -- the suite --------------------------------------------------------------------------
def _label(tool_choice) -> str:
    if tool_choice is None:
        return "default"
    if isinstance(tool_choice, dict):
        return "named:" + str((tool_choice.get("function") or {}).get("name"))
    return str(tool_choice)


def _content_form(content) -> str:
    if content is None:
        return "null"
    if isinstance(content, str):
        return "empty" if content == "" else "text"
    return "other"


class QS1(Suite):
    name = "qs1"
    version = f"1.{_sha12(CASES_PATH)}.{_sha12(Path(__file__))}"
    caps = Caps(max_prompt_tokens=20_000, max_output_tokens=12_000,
                max_call_prompt_tokens=16_000)

    def __init__(self):
        data = load_cases()
        self.system = data["system"]
        self.tools = data["tools"]
        self.declared = {t["function"]["name"]: t["function"] for t in self.tools}
        self.cases: dict[str, dict] = {}
        for case in expand(data):
            if not ID_PATTERN.fullmatch(case["item"]) or case["item"] in self.cases:
                raise ValueError(f"case id {case['item']!r} is not a valid, unique id")
            self.cases[case["item"]] = case

    def items(self) -> list[Item]:
        return [Item(i) for i in self.cases]

    def run_item(self, ctx, item: Item) -> ItemResult:
        return _Run(self, ctx, self.cases[item.id]).run()


class _Run:
    """One item run: its calls, its judgement and its outcome.data."""

    def __init__(self, suite: QS1, ctx, case: dict):
        self.suite, self.ctx, self.case = suite, ctx, case
        self.thinking = bool(ctx.thinking)
        self.tool_choice = case.get("tool_choice")
        self.decides = self.tool_choice in (None, "auto")
        self.doc = (case.get("documented") or {}).get("thinking" if self.thinking else "non_thinking")
        self.finishes = frozenset(getattr(ctx.provider, "FINISH_REASONS", ()))
        self.limit = getattr(ctx.provider, "MAX_TOKENS", None)
        self.seen_ids: list[str] = []
        self.data = {
            "qs1": 1, "case": case["id"], "shape": case["shape"], "stream": case["stream"],
            "tool_choice": _label(self.tool_choice), "thinking": self.thinking,
            "status_basis": None, "documented": None, "provider_condition": None,
            "assertions": {}, "failed": [], "metric_inputs": {},
            "turns_in_case": len(case["turns"]), "turns": [],
        }
        if self.doc is not None:
            self.data["documented"] = {
                "source": self.doc["source"], "says": self.doc["says"],
                "expected": (f"HTTP {self.doc['status']}" if self.doc.get("status") is not None
                             else "unsupported, with no status documented"),
                "observed": None, "matches": None}

    def run(self) -> ItemResult:
        ctx, case = self.ctx, self.case
        messages = ([{"role": "system", "content": self.suite.system}]
                    + copy.deepcopy(case["messages"]))
        kw = {"tools": self.suite.tools, "stream": case["stream"]}
        if self.tool_choice is not None:
            kw["tool_choice"] = self.tool_choice
        awaiting: list[dict] = []    # turns with calls whose ids no later request has carried yet
        for k, golden in enumerate(case["turns"]):
            if golden.get("user"):
                messages.append({"role": "user", "content": golden["user"]})
            t = {"n": k + 1, "http": None, "judged": False, "expect": golden["expect"]}
            self.data["turns"].append(t)
            try:
                turn = ctx.chat(messages, **kw)
            except RunStopped as e:
                t["stopped_by"] = type(e).__name__
                return self.finish("stopped", "harness_cap", f"turn {k + 1}: {e}")
            except ProviderError as e:
                return self.refused_or_error(k, t, e, awaiting)
            except Exception as e:  # noqa: BLE001 - a reply that never arrived whole
                t["error"] = type(e).__name__
                return self.finish("error", "transport", f"turn {k + 1}: {type(e).__name__}; "
                                   f"{ctx.stop_reason or 'no stop reason set'}")
            t["http"] = 200
            if k == 0 and self.doc is not None:
                self.data["documented"]["observed"] = "HTTP 200"
                self.data["documented"]["matches"] = (False if self.doc.get("status") is not None
                                                      else None)
            for earlier in awaiting:
                earlier["checks"]["ids"]["why"] += "; a later request carrying them was accepted"
            awaiting = []
            ended = self.judge(k, t, golden, turn)
            if ended is not None:
                return ended
            if k + 1 < len(case["turns"]):
                messages.append(ctx.provider.assistant_message(turn, tools_in_request=True))
                calls = list(turn.tool_calls or [])
                if calls:
                    pairs = t.pop("_pairs")
                    if pairs is None:
                        raise ValueError(f"case {case['id']} goes on after a turn without "
                                         "golden results")
                    for j, c in enumerate(calls):
                        messages.append({"role": "tool", "tool_call_id": c["id"],
                                         "content": golden["calls"][pairs[j]]["result"]})
                    awaiting.append(t)
            t.pop("_pairs", None)
        return self.finish("pass", "assertions", f"{len(case['turns'])} turn(s)")

    def refused_or_error(self, k: int, t: dict, e: ProviderError, awaiting: list) -> ItemResult:
        t["http"] = e.status
        body = str(e.body or "")[:ERROR_BODY]
        if k == 0 and self.doc is not None:
            doc, rec = self.doc, self.data["documented"]
            rec["observed"] = f"HTTP {e.status}"
            if doc.get("status") is not None:
                rec["matches"] = e.status == doc["status"]
                if rec["matches"]:
                    return self.finish("refused", "documented",
                                       f"HTTP {e.status} at turn 1, as {doc['source']} "
                                       f"documents: {body}")
            elif e.status in REFUSALS:
                return self.finish("refused", "documented",
                                   f"HTTP {e.status} at turn 1; {doc['source']} calls this "
                                   f"unsupported, and names no status: {body}")
            return self.finish("error", "provider_error",
                               f"HTTP {e.status} at turn 1, not the documented outcome: {body}")
        if awaiting and e.status in REFUSALS:
            why = f"a later request carrying its ids was refused with HTTP {e.status}"
            awaiting[-1]["checks"]["ids"] = {"result": "fail", "why": why}
            return self.finish("fail", "assertions",
                               f"turn {awaiting[-1]['n']}: ids ({why}, at turn {k + 1}): {body}")
        return self.finish("error", "provider_error", f"turn {k + 1}: HTTP {e.status}: {body}")

    def judge(self, k: int, t: dict, golden: dict, turn) -> ItemResult | None:
        """Judge one turn that returned 200. An ItemResult when it ends the run."""
        ctx = self.ctx
        calls = list(turn.tool_calls or [])
        finish = turn.finish_reason
        request = ctx.calls[-1].get("request", {}) if ctx.calls else {}
        sent_max = request.get("max_tokens")
        t.update({
            "finish_reason": finish if isinstance(finish, str) and finish in self.finishes
            else "undocumented",
            "calls": len(calls), "content": _content_form(turn.content),
            "reasoning_chars": (len(turn.reasoning_content)
                                if isinstance(turn.reasoning_content, str) else 0),
            "special_tokens_in_reasoning": len(find_tokens(turn.reasoning_content)),
            "max_tokens_sent": sent_max, "output_tokens": turn.usage.output,
            "reasoning_tokens": turn.usage.reasoning, "length_cause": None,
        })
        self.seen_ids += [c["id"] for c in calls if isinstance(c, dict) and isinstance(c.get("id"), str)]
        if finish == "length":
            if isinstance(sent_max, int) and turn.usage.output >= sent_max:
                t["length_cause"] = ("provider_limit" if self.limit and sent_max >= self.limit
                                     else "harness_clamp")
                return self.finish("stopped", "harness_cap",
                                   f"turn {k + 1} reached the max_tokens the harness sent "
                                   f"({sent_max}): {t['length_cause']}")
            t["length_cause"] = "below_request_max_tokens"
            self.data["provider_condition"] = "length below the request's max_tokens"
            return self.finish("error", "provider_condition",
                               f"turn {k + 1}: a length finish below the request's max_tokens")
        if finish in PROVIDER_CONDITIONS:
            self.data["provider_condition"] = finish
            return self.finish("error", "provider_condition",
                               f"turn {k + 1}: the provider's finish_reason {finish}")
        t["judged"] = True
        declared = self.suite.declared
        name_args, why, pairs = judge_name_args(golden, calls, turn.content, declared)
        t["_pairs"] = pairs
        checks = {"name_args": (name_args, why),
                  "special_tokens": judge_special_tokens(turn.content, calls),
                  "reasoning": judge_reasoning(turn.content, turn.reasoning_content, self.thinking),
                  "ids": judge_ids(calls),
                  "finish_reason": judge_finish(finish, calls, self.finishes)}
        t["checks"] = {a: {"result": r, "why": w} for a, (r, w) in checks.items()}
        t["schema_valid"] = [schema_valid(c, declared) for c in calls]
        if self.decides:
            positive = golden["expect"] == "calls"
            t["trigger"] = ("tp" if calls else "fn") if positive else ("fp" if calls else "tn")
        failed = [a for a in ASSERTIONS if t["checks"][a]["result"] == "fail"]
        if failed:
            t.pop("_pairs", None)
            return self.finish("fail", "assertions", f"turn {k + 1}: " + "; ".join(
                f"{a} ({t['checks'][a]['why']})" for a in failed))
        return None

    def finish(self, status: str, basis: str, detail: str) -> ItemResult:
        """The outcome. A pass with a failed assertion is a fail, and a fail with
        none is an error in QS1 itself, raised so the runner records it."""
        turns = self.data["turns"]

        def results(a):
            return [t["checks"][a]["result"] for t in turns if "checks" in t]
        failed = [a for a in ASSERTIONS if "fail" in results(a)]
        self.data["assertions"] = {a: ("fail" if a in failed else
                                        "pass" if "pass" in results(a) else "not_judged")
                                   for a in ASSERTIONS}
        self.data["failed"] = failed
        if status == "pass" and failed:
            status = "fail"
        if status == "fail" and not failed:
            raise AssertionError("QS1 returned fail with no failed assertion")
        trigger = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
        for t in turns:
            if t.get("trigger"):
                trigger[t["trigger"]] += 1
        valid = [v for t in turns for v in t.get("schema_valid", [])]
        self.data["metric_inputs"] = {"trigger": trigger,
                                      "schema": {"calls": len(valid), "valid": sum(valid)}}
        self.data["ids_distinct_in_conversation"] = (len(set(self.seen_ids)) == len(self.seen_ids)
                                                     if self.seen_ids else None)
        self.data["status_basis"] = basis
        self.data["turns_reached"] = len(turns)
        for t in turns:
            t.pop("_pairs", None)
        return ItemResult(status, f"{status}: {detail}", self.data)
