"""QS1 against qs/fake.py, on 127.0.0.1 only.

The conformant fake answers each request from the goldens, in DeepSeek's
documented format (D10), and refuses what DeepSeek documents as refused: a 400
for tool_choice required or named in thinking mode (D10, chat_completion_full
.txt:463-466), and a 400 for an assistant turn sent back without its reasoning,
in thinking mode with tools (D8, thinking.txt:54). It keeps every assistant
message the suite should send back, and refuses any other, so a hand-written
call or a changed turn is seen. Each breaking fake changes one reply of the
conformant one, and the suite must fail and name the assertion it broke. Then
the documented refusals, provider conditions, harness caps, the reservation,
records free of model text, and the judge and metrics on their own."""
import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from qs import identity
from qs.fake import FakeReply, FakeServer, error, reply, usage_dict
from qs.guard import SpendGuard
from qs.prices import PriceTable
from qs.providers import deepseek
from qs.registry import Endpoint
from qs.suite import ItemResult, Runner
from qs.suites import qs1
from qs.suites.qs1 import QS1

ROOT = Path(__file__).resolve().parent.parent
PRICES = PriceTable.load(ROOT / "prices" / "deepseek-2026-10-06.json")
OFF_PEAK = datetime(2026, 10, 6, 17, 25, tzinfo=timezone.utc)    # a Tuesday, off-peak
PEAK = datetime(2026, 10, 6, 2, 0, tzinfo=timezone.utc)          # a Tuesday, peak
SENTINEL = "QS1-SENTINEL-7f3a9c"
DOCUMENTED_IN_THINKING = {"choice.required", "choice.required.stream", "choice.named",
                          "choice.named.stream", "multiturn.handwritten"}


# -- the fakes --------------------------------------------------------------------
class Conformant:
    """A responder for qs/fake.py that answers QS1 from its goldens.

    mutate(item, k, thinking, reply, body) may change the reply dict in place,
    or return a FakeReply to send instead."""

    def __init__(self, *, refuse_documented=True, accept_handwritten=True, mutate=None):
        self.suite = QS1()
        self.by_key = {}
        for c in self.suite.cases.values():
            key = self.key(c["messages"][0]["content"], c["stream"], c.get("tool_choice"))
            assert key not in self.by_key
            self.by_key[key] = c
        self.refuse_documented = refuse_documented
        self.accept_handwritten = accept_handwritten
        self.mutate = mutate
        self.produced = []     # the assistant messages the suite should send back
        self.foreign = []      # assistant messages received that this fake never produced
        self.errors = []       # the fake's own failures
        self.seen = []         # (item, turn index, thinking) for each request
        self.n = 0

    @staticmethod
    def key(first_user, stream, tool_choice):
        return first_user, bool(stream), json.dumps(tool_choice, sort_keys=True)

    def __call__(self, body):
        try:
            return self.respond(body)
        except Exception as e:  # noqa: BLE001 - the test reads it
            self.errors.append(f"{type(e).__name__}: {e}")
            return error(500, "the fake failed")

    def respond(self, body):
        if body["messages"] == identity.PROBE_MESSAGES:
            return reply("ready")
        thinking = body["thinking"]["type"] == "enabled"
        first_user = next(m["content"] for m in body["messages"] if m["role"] == "user")
        case = self.by_key[self.key(first_user, body.get("stream"), body.get("tool_choice"))]
        own = sum(1 for m in case["messages"] if m["role"] == "assistant")
        back = [m for m in body["messages"] if m["role"] == "assistant"]
        k = len(back) - own
        self.seen.append((case["item"], k, thinking))
        if (thinking and self.refuse_documented
                and deepseek.documented_refusal(True, body.get("tool_choice"))):
            return error(400, "required and named tool choices are not supported in thinking mode")
        if thinking and body.get("tools") and any(m.get("reasoning_content") is None for m in back):
            return error(400, "the reasoning_content of each earlier turn must be passed back")
        for m in back[own:]:
            if m not in self.produced:
                self.foreign.append(m)
                return error(400, "an assistant message this endpoint did not produce")
        if own and not self.accept_handwritten:
            return error(400, "tool calls inserted mid-conversation are not supported")
        r = self.answer(case, k, case["turns"][k], thinking)
        if self.mutate is not None:
            out = self.mutate(case["item"], k, thinking, r, body)
            if isinstance(out, FakeReply):
                return out
        fr = self.render(r, bool(body.get("stream")))
        self.produced.append(self.sent_back(fr))
        return fr

    def answer(self, case, k, golden, thinking):
        self.n += 1
        calls = []
        if golden["expect"] in ("calls", "any_declared"):
            order = list(range(len(golden["calls"])))
            if golden.get("order", "any") == "any":
                order.reverse()          # the golden leaves the order free
            for i, j in enumerate(order):
                g = golden["calls"][j]
                calls.append({"id": f"call_{i:02d}_qs1fake{self.n:05d}", "type": "function",
                              "function": {"name": g["name"],
                                           "arguments": json.dumps(g["canonical"],
                                                                   ensure_ascii=False)}})
        return {"content": "" if calls else f"Here is the answer for {case['id']}.",
                "reasoning": (f"The request in {case['id']}, turn {k + 1}, is read against "
                              "the tools offered." if thinking else None),
                "calls": calls, "finish": "tool_calls" if calls else "stop",
                "usage": [0, 600, 120, 80 if thinking else 0]}

    def render(self, r, stream):
        msg = {"role": "assistant", "content": r["content"]}
        if r["reasoning"] is not None:
            msg["reasoning_content"] = r["reasoning"]
        if r["calls"]:
            msg["tool_calls"] = r["calls"]
        usage = usage_dict(*r["usage"])
        base = {"id": f"fake-{self.n}", "created": 0, "model": "deepseek-flash",
                "system_fingerprint": "fp_fake"}
        if not stream:
            return FakeReply(body=dict(base, object="chat.completion", usage=usage, choices=[
                {"index": 0, "message": msg, "finish_reason": r["finish"], "logprobs": None}]))

        def chunk(delta, finish=None, with_usage=False):
            c = dict(base, object="chat.completion.chunk", choices=[
                {"index": 0, "delta": delta, "finish_reason": finish, "logprobs": None}])
            if with_usage:
                c["usage"] = usage
            return "data: " + json.dumps(c, ensure_ascii=False)
        out = [": keep-alive", chunk({"role": "assistant", "content": ""})]
        for field in ("reasoning", "content"):
            text = r[field]
            if text:
                half = len(text) // 2
                key = "reasoning_content" if field == "reasoning" else "content"
                out += [chunk({key: text[:half]}), chunk({key: text[half:]})]
        for i, c in enumerate(r["calls"]):
            out.append(chunk({"tool_calls": [{"index": i, "id": c.get("id"), "type": c.get("type"),
                                              "function": {"name": c["function"]["name"],
                                                           "arguments": ""}}]}))
            args = c["function"]["arguments"]
            for p in range(0, len(args), 7):     # split anywhere, escapes included
                out.append(chunk({"tool_calls": [{"index": i,
                                                  "function": {"arguments": args[p:p + 7]}}]}))
            out.append(": keep-alive")
        out.append(chunk({"content": ""}, finish=r["finish"], with_usage=True))
        out.append("data: [DONE]")
        return FakeReply(stream=out)

    @staticmethod
    def sent_back(fr):
        """What the suite will send back for this reply, through P0's own parser."""
        turn = (deepseek.parse_stream(fr.stream) if fr.stream is not None
                else deepseek.parse_response(fr.body))
        return deepseek.assistant_message(turn, tools_in_request=True)


def at(item, k, change):
    """A mutate that applies change(reply, body) to one item's turn k only."""
    def mutate(it, kk, thinking, r, body):
        if (it, kk) == (item, k):
            return change(r, body)
        return None
    return mutate


class Only(QS1):
    """QS1 restricted to some of its items."""

    def __init__(self, *ids):
        super().__init__()
        assert set(ids) <= set(self.cases), ids
        self.only = ids

    def items(self):
        return [i for i in super().items() if i.id in self.only]


class Dry(QS1):
    """QS1's items and caps, making no call: the runner's reservation alone."""

    def run_item(self, ctx, item):
        return ItemResult("skipped", "dry")


# -- running a batch --------------------------------------------------------------------
def endpoint(url):
    return Endpoint(name="fake", provider="deepseek", base_url=url, model="deepseek-flash",
                    price_table="prices/deepseek-2026-10-06.json", key_env=None)


def lines(p):
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


@pytest.fixture(scope="module")
def server():
    srv = FakeServer(prices=PRICES, clock=lambda: OFF_PEAK)
    url = srv.start()
    yield srv, url
    srv.stop()


def batch(tmp_path, server, responder, suite, *, thinking=True, repeats=1):
    srv, url = server
    srv.responder = responder
    srv.requests.clear()
    guard = SpendGuard(Decimal("250"), tmp_path / "records" / "spend.jsonl")
    runner = Runner(endpoint(url), PRICES, guard, records_dir=tmp_path / "records",
                    transcripts_dir=tmp_path / "transcripts", clock=lambda: OFF_PEAK)
    summary = runner.run_batch(suite, repeats=repeats, thinking=thinking)
    records = lines(tmp_path / "records" / "runs" / "qs1.jsonl")
    return summary, {r["item"]: r for r in records}, records


def one(tmp_path, server, item, mutate=None, *, thinking=True, **fake_kw):
    fake = Conformant(mutate=mutate, **fake_kw)
    s, by_item, _ = batch(tmp_path, server, fake, Only(item), thinking=thinking)
    assert fake.errors == []
    return by_item[item], s, fake


# -- the conformant fake ------------------------------------------------------------------
@pytest.mark.parametrize("thinking", [True, False])
def test_the_conformant_fake_passes_every_item_but_the_documented_refusals(
        tmp_path, server, thinking):
    fake = Conformant()
    s, by_item, records = batch(tmp_path, server, fake, QS1(), thinking=thinking)
    assert fake.errors == [] and fake.foreign == []
    assert s["runs"] == 35 and s["stopped_for"] is None and s["reconciliation"] == "ok"
    assert len(fake.seen) == 49         # every golden turn of every item was asked
    for item, rec in by_item.items():
        out, data = rec["outcome"], rec["outcome"]["data"]
        assert rec["thinking"] is thinking and data["thinking"] is thinking
        if thinking and item in DOCUMENTED_IN_THINKING:
            assert out["status"] == "refused", item
            assert data["documented"]["observed"] == "HTTP 400"
            assert data["documented"]["matches"] is True and data["status_basis"] == "documented"
        else:
            assert out["status"] == "pass", (item, out["detail"])
            assert data["turns_reached"] == data["turns_in_case"]
            assert data["status_basis"] == "assertions"
        assert data["failed"] == []
    m = qs1.metrics(r["outcome"]["data"] for r in records)
    # by hand, from the case file: 29 turns where a call is expected and the model
    # decides; 14 where none is, 13 in thinking mode, whose hand-written history
    # is refused. 34 calls in judged turns, and 4 more in non-thinking mode, from
    # required and named (one call each, streamed and not).
    tn, calls = (13, 34) if thinking else (14, 38)
    assert m["trigger"] == {"tp": 29, "fp": 0, "fn": 0, "tn": tn, "n": 29 + tn,
                            "f1_denominator": 58, "f1": 1.0, "agreement": 1.0}
    assert m["schema"] == {"calls": calls, "valid": calls, "accuracy": 1.0}


def test_the_transcript_holds_each_request_as_sent_and_reasoning_goes_back(tmp_path, server):
    s, by_item, _ = batch(tmp_path, server, Conformant(), Only("multiturn.followup"))
    assert by_item["multiturn.followup"]["outcome"]["status"] == "pass"
    sent = [b for b in server[0].requests if b["messages"] != identity.PROBE_MESSAGES]
    path = tmp_path / "transcripts" / s["batch"] / f"{s['batch']}.multiturn.followup.r0.json"
    calls = json.loads(path.read_text(encoding="utf-8"))["calls"]
    assert [c["request"] for c in calls] == sent
    assert [len(b["messages"]) for b in sent] == [2, 4, 6]
    # D8: every earlier assistant turn goes back with its reasoning, the call-free one too
    back = [m for m in sent[-1]["messages"] if m["role"] == "assistant"]
    assert [bool(m.get("reasoning_content")) for m in back] == [True, True]
    assert [bool(m.get("tool_calls")) for m in back] == [True, False]
    assert sent[-1]["messages"][-1] == {"role": "user", "content": "And in Guangzhou?"}


def test_non_thinking_mode_sends_no_reasoning_back(tmp_path, server):
    batch(tmp_path, server, Conformant(), Only("multiturn.chain"), thinking=False)
    last = server[0].requests[-1]
    assert [m["role"] for m in last["messages"]] == ["system", "user", "assistant", "tool",
                                                     "assistant", "tool"]
    assert not any("reasoning_content" in m for m in last["messages"])
    assert last["thinking"] == {"type": "disabled"}


# -- one breaking fake per assertion ---------------------------------------------------------
def _args(r, args, i=0):
    r["calls"][i]["function"]["arguments"] = json.dumps(args)


def _no_calls(r, content="It is sunny in Paris."):
    r["calls"], r["content"], r["finish"] = [], content, "stop"


def _add_call(r):
    r["calls"] = [{"id": "call_00_added", "type": "function",
                   "function": {"name": "get_date", "arguments": "{}"}}]
    r["finish"] = "tool_calls"


BREAKS = [
    # name_args
    ("a wrong name", "single.weather", 0, True,
     lambda r, b: r["calls"][0]["function"].update(name="get_date"), ["name_args"]),
    ("a wrong value", "single.weather", 0, True,
     lambda r, b: _args(r, {"location": "Lyon"}), ["name_args"]),
    ("a wrong value, streamed", "single.weather.stream", 0, False,
     lambda r, b: _args(r, {"location": "Lyon"}), ["name_args"]),
    ("a missing argument", "single.weather", 0, True, lambda r, b: _args(r, {}), ["name_args"]),
    ("an extra argument", "single.weather", 0, True,
     lambda r, b: _args(r, {"location": "Paris", "zip": "75001"}), ["name_args"]),
    ("a date never asked for", "single.weather", 0, False,
     lambda r, b: _args(r, {"location": "Paris", "date": "2026-10-07"}), ["name_args"]),
    ("arguments that are not JSON", "single.weather", 0, True,
     lambda r, b: r["calls"][0]["function"].update(arguments="{location: Paris"), ["name_args"]),
    ("arguments that are a JSON array", "single.weather", 0, True,
     lambda r, b: r["calls"][0]["function"].update(arguments='["Paris"]'), ["name_args"]),
    ("empty arguments where an object is due", "empty.args", 0, True,
     lambda r, b: r["calls"][0]["function"].update(arguments=""), ["name_args"]),
    ("one call where the golden has two", "parallel.weather", 0, True,
     lambda r, b: r["calls"].pop(), ["name_args"]),
    ("a call where the golden has none", "nocall.arithmetic", 0, True,
     lambda r, b: _add_call(r), ["name_args"]),
    ("a call despite tool_choice none", "choice.none.stream", 0, False,
     lambda r, b: _add_call(r), ["name_args"]),
    ("no call where the golden has one", "single.weather", 0, True,
     lambda r, b: _no_calls(r), ["name_args"]),
    ("a type other than function", "single.weather", 0, True,
     lambda r, b: r["calls"][0].update(type="tool"), ["name_args"]),
    ("a code argument with a backslash lost", "code.multiline.stream", 0, True,
     lambda r, b: _args(r, {"path": "tools/escape_demo.py",
                            "content": "OUT_DIR = " + chr(34) + "C:" + chr(92) + "temp" + chr(34)}),
     ["name_args"]),
    ("the date not carried from the first result", "multiturn.chain", 1, True,
     lambda r, b: _args(r, {"location": "Hangzhou", "date": "2026-10-06"}), ["name_args"]),
    ("an attendee missing from a nested array", "nested.event", 0, False,
     lambda r, b: _args(r, {"title": "Design review", "priority": "high",
                            "location": {"city": "Oslo", "room": "4B"},
                            "attendees": [{"name": "Ada Lovelace",
                                           "email": "ada" + chr(64) + "example.com"}]}),
     ["name_args"]),
    ("an enum's name instead of its value", "enum.language", 0, True,
     lambda r, b: _args(r, {"text": "good morning", "target_language": "Japanese"}),
     ["name_args"]),
    ("required, with a call to an undeclared tool", "choice.required", 0, False,
     lambda r, b: r["calls"][0]["function"].update(name="launch_probe"), ["name_args"]),
    ("required, with schema-invalid arguments", "choice.required", 0, False,
     lambda r, b: r["calls"][0]["function"].update(name="get_weather"), ["name_args"]),
    ("named, with a call to another tool", "choice.named", 0, False,
     lambda r, b: (r["calls"][0]["function"].update(name="get_weather"),
                   _args(r, {"location": "Paris"})), ["name_args"]),
    # reasoning
    ("no reasoning in thinking mode", "single.weather", 0, True,
     lambda r, b: r.update(reasoning=None), ["reasoning"]),
    ("no reasoning in thinking mode, streamed", "single.weather.stream", 0, True,
     lambda r, b: r.update(reasoning=None), ["reasoning"]),
    ("reasoning in non-thinking mode", "single.weather", 0, False,
     lambda r, b: r.update(reasoning="I should call the weather tool."), ["reasoning"]),
    ("a think marker in content", "nocall.arithmetic", 0, False,
     lambda r, b: r.update(content="<think>add them</think>42"), ["reasoning"]),
    ("the reasoning repeated in content", "nocall.arithmetic", 0, True,
     lambda r, b: r.update(content=r["reasoning"] + " 42"), ["reasoning"]),
    # ids
    ("two calls with one id", "parallel.weather", 0, True,
     lambda r, b: r["calls"][1].update(id=r["calls"][0]["id"]), ["ids"]),
    ("a call without an id", "single.weather", 0, True,
     lambda r, b: r["calls"][0].pop("id"), ["ids"]),
    ("a call without an id, streamed", "single.weather.stream", 0, True,
     lambda r, b: r["calls"][0].pop("id"), ["ids"]),
    ("a follow-up carrying the ids refused with 400", "multiturn.weather", 1, True,
     lambda r, b: error(400, "invalid tool_call_id"), ["ids"]),
    ("a follow-up carrying the ids refused with 422", "parallel.weather", 1, False,
     lambda r, b: error(422, "invalid parameters"), ["ids"]),
    # finish_reason
    ("stop on a turn with calls", "single.weather", 0, True,
     lambda r, b: r.update(finish="stop"), ["finish_reason"]),
    ("stop on a turn with calls, streamed", "single.weather.stream", 0, False,
     lambda r, b: r.update(finish="stop"), ["finish_reason"]),
    ("tool_calls on a turn without calls", "nocall.arithmetic", 0, True,
     lambda r, b: r.update(finish="tool_calls"), ["finish_reason"]),
    ("a finish_reason outside D10's list", "nocall.arithmetic", 0, True,
     lambda r, b: r.update(finish="end_turn"), ["finish_reason"]),
]


@pytest.mark.parametrize("what,item,k,thinking,change,failed", BREAKS,
                         ids=[b[0].replace(" ", "_") for b in BREAKS])
def test_a_broken_reply_fails_and_names_its_assertion(tmp_path, server, what, item, k, thinking,
                                                      change, failed):
    rec, s, fake = one(tmp_path, server, item, at(item, k, change), thinking=thinking)
    out, data = rec["outcome"], rec["outcome"]["data"]
    assert out["status"] == "fail", (what, out["detail"])
    assert data["failed"] == failed, (what, out["detail"])
    assert data["status_basis"] == "assertions"
    assert all(a in out["detail"] for a in failed)
    assert s["stopped_for"] is None       # a model's failure never stops the batch


@pytest.mark.parametrize("token", qs1.SPECIAL_TOKENS)
def test_each_special_token_in_content_fails_special_tokens(tmp_path, server, token):
    rec, _, _ = one(tmp_path, server, "nocall.arithmetic",
                    at("nocall.arithmetic", 0, lambda r, b: r.update(content="42 " + token)))
    assert rec["outcome"]["status"] == "fail" and rec["outcome"]["data"]["failed"] == ["special_tokens"]


def test_a_special_token_in_arguments_fails_special_tokens(tmp_path, server):
    rec, _, _ = one(tmp_path, server, "single.weather",
                    at("single.weather", 0, lambda r, b: _args(r, {"location": "Paris<tool_call>"})))
    assert rec["outcome"]["data"]["failed"] == ["name_args", "special_tokens"]


def test_a_special_token_in_reasoning_is_recorded_not_failed(tmp_path, server):
    rec, _, _ = one(tmp_path, server, "single.weather",
                    at("single.weather", 0, lambda r, b: r.update(reasoning=r["reasoning"] + " <tool_call>")))
    assert rec["outcome"]["status"] == "pass"
    assert rec["outcome"]["data"]["turns"][0]["special_tokens_in_reasoning"] == 1


# -- documented behaviour, never a model failure ------------------------------------------------
@pytest.mark.parametrize("item", sorted(DOCUMENTED_IN_THINKING))
def test_thinking_modes_documented_400_is_recorded_as_documented(tmp_path, server, item):
    rec, s, _ = one(tmp_path, server, item)
    out, data = rec["outcome"], rec["outcome"]["data"]
    assert out["status"] == "refused" and data["failed"] == [] and data["status_basis"] == "documented"
    assert data["documented"]["matches"] is True and data["documented"]["observed"] == "HTTP 400"
    source = "D8" if item == "multiturn.handwritten" else "D10"
    assert data["documented"]["source"].startswith(source)
    reason = "must be passed back" if source == "D8" else "not supported in thinking mode"
    assert reason in out["detail"]          # the provider's own reason, for a reader to check
    assert data["metric_inputs"] == {"trigger": {"tp": 0, "fp": 0, "fn": 0, "tn": 0},
                                     "schema": {"calls": 0, "valid": 0}}
    assert s["stopped_for"] is None and rec["stop_reason"] is None


@pytest.mark.parametrize("item", ["choice.required", "choice.named.stream"])
def test_a_200_where_a_400_is_documented_is_judged_and_flagged(tmp_path, server, item):
    rec, _, _ = one(tmp_path, server, item, refuse_documented=False)
    out, data = rec["outcome"], rec["outcome"]["data"]
    assert out["status"] == "pass" and data["documented"]["observed"] == "HTTP 200"
    assert data["documented"]["matches"] is False


def test_another_status_where_a_400_is_documented_is_an_error(tmp_path, server):
    rec, _, _ = one(tmp_path, server, "choice.named",
                    at("choice.named", 0, lambda r, b: error(422, "invalid parameters")),
                    refuse_documented=False)
    data = rec["outcome"]["data"]
    assert rec["outcome"]["status"] == "error" and data["status_basis"] == "provider_error"
    assert data["documented"]["matches"] is False and data["documented"]["observed"] == "HTTP 422"


def test_the_handwritten_history_refused_in_non_thinking_mode_is_documented_without_a_status(
        tmp_path, server):
    rec, _, _ = one(tmp_path, server, "multiturn.handwritten", thinking=False,
                    accept_handwritten=False)
    out, data = rec["outcome"], rec["outcome"]["data"]
    assert out["status"] == "refused" and data["documented"]["matches"] is None
    assert data["documented"]["source"].startswith("D9") and data["failed"] == []
    assert "inserted mid-conversation" in out["detail"]


def test_a_documented_refusal_is_known_by_its_status_alone(tmp_path, server):
    # Limit 12, pinned: a 400 at turn 1 of a documented case reads as the
    # documented refusal whatever its cause. The detail keeps the provider's
    # reason, so a reader can tell the two apart.
    rec, _, _ = one(tmp_path, server, "choice.required",
                    at("choice.required", 0, lambda r, b: error(400, "messages[1] is malformed")),
                    refuse_documented=False)
    out = rec["outcome"]
    assert out["status"] == "refused" and out["data"]["documented"]["matches"] is True
    assert "messages[1] is malformed" in out["detail"]


def test_the_handwritten_history_accepted_in_non_thinking_mode_is_judged(tmp_path, server):
    rec, _, _ = one(tmp_path, server, "multiturn.handwritten", thinking=False)
    data = rec["outcome"]["data"]
    assert rec["outcome"]["status"] == "pass" and data["documented"]["observed"] == "HTTP 200"
    assert data["documented"]["matches"] is None
    assert data["metric_inputs"]["trigger"]["tn"] == 1


# -- provider conditions and harness caps -------------------------------------------------------
@pytest.mark.parametrize("condition", sorted(qs1.PROVIDER_CONDITIONS))
def test_a_provider_condition_is_an_error_not_a_failure(tmp_path, server, condition):
    rec, s, _ = one(tmp_path, server, "single.weather",
                    at("single.weather", 0, lambda r, b: r.update(finish=condition)))
    data = rec["outcome"]["data"]
    assert rec["outcome"]["status"] == "error" and data["status_basis"] == "provider_condition"
    assert data["provider_condition"] == condition and data["failed"] == []
    assert data["turns"][0]["judged"] is False and s["stopped_for"] is None


def _length(r, b, short=0):
    r["finish"] = "length"
    r["usage"][2] = b["max_tokens"] - short


def test_a_length_finish_at_the_harness_clamp_is_stopped(tmp_path, server):
    rec, _, _ = one(tmp_path, server, "single.weather", at("single.weather", 0, _length))
    data = rec["outcome"]["data"]
    assert rec["outcome"]["status"] == "stopped" and data["status_basis"] == "harness_cap"
    turn = data["turns"][0]
    assert turn["length_cause"] == "harness_clamp" and data["failed"] == []
    assert turn["max_tokens_sent"] == QS1.caps.max_output_tokens == turn["output_tokens"]


def test_a_length_finish_below_the_clamp_is_a_provider_condition(tmp_path, server):
    rec, _, _ = one(tmp_path, server, "single.weather",
                    at("single.weather", 0, lambda r, b: _length(r, b, short=1)))
    data = rec["outcome"]["data"]
    assert rec["outcome"]["status"] == "error" and data["status_basis"] == "provider_condition"
    assert data["turns"][0]["length_cause"] == "below_request_max_tokens"


def test_a_length_finish_on_a_later_turn_keeps_the_earlier_turns(tmp_path, server):
    rec, _, _ = one(tmp_path, server, "multiturn.chain", at("multiturn.chain", 1, _length))
    data = rec["outcome"]["data"]
    assert rec["outcome"]["status"] == "stopped" and data["turns_reached"] == 2
    assert data["turns"][0]["checks"]["name_args"]["result"] == "pass"
    assert data["turns"][1]["max_tokens_sent"] == QS1.caps.max_output_tokens - 120
    assert data["metric_inputs"]["trigger"]["tp"] == 1


def test_a_cap_mid_item_is_stopped_and_the_batch_goes_on(tmp_path, server):
    def big(it, k, thinking, r, body):
        if (it, k) == ("multiturn.chain", 0):
            r["usage"][1] = 25_000        # past the run's 20,000 prompt tokens
    fake = Conformant(mutate=big)
    s, by_item, _ = batch(tmp_path, server, fake, Only("multiturn.chain", "nocall.arithmetic"))
    chain = by_item["multiturn.chain"]["outcome"]
    assert chain["status"] == "stopped" and chain["data"]["status_basis"] == "harness_cap"
    assert chain["data"]["turns"][1]["stopped_by"] == "CapReached"
    assert chain["data"]["metric_inputs"]["trigger"]["tp"] == 1
    assert s["runs"] == 2 and by_item["nocall.arithmetic"]["outcome"]["status"] == "pass"


@pytest.mark.parametrize("status", [429, 503])
def test_a_status_that_stops_the_batch_is_an_error_and_stops_it(tmp_path, server, status):
    fake = Conformant(mutate=at("multiturn.weather", 1, lambda r, b: error(status, "busy")))
    s, by_item, _ = batch(tmp_path, server, fake, Only("multiturn.weather", "nocall.arithmetic"))
    rec = by_item["multiturn.weather"]
    assert rec["outcome"]["status"] == "error" and f"HTTP {status}" in s["stopped_for"]
    assert rec["outcome"]["data"]["status_basis"] == "provider_error"
    assert rec["stop_reason"] == s["stopped_for"] and s["runs"] == 1


def test_a_reply_dropped_after_billing_is_an_error_and_stops_the_batch(tmp_path, server):
    drop = FakeReply(body=reply("x").body, drop=True)
    fake = Conformant(mutate=at("single.weather", 0, lambda r, b: drop))
    s, by_item, _ = batch(tmp_path, server, fake, Only("single.weather", "nocall.arithmetic"))
    rec = by_item["single.weather"]
    assert rec["outcome"]["status"] == "error" and "did not arrive whole" in s["stopped_for"]
    assert rec["outcome"]["data"]["status_basis"] == "transport" and s["runs"] == 1


# -- the reservation ---------------------------------------------------------------------------
def test_the_reservation_at_three_repeats_is_under_the_limit(tmp_path, server):
    s, _, records = batch(tmp_path, server, lambda b: reply("ready"), Dry(), repeats=3)
    # by hand: (20,000 + 16,000) prompt at $0.15 and 12,000 output at $0.60 per
    # million is $0.0126 a run, $1.323 over 105 runs; the probe's 64 and 16 add
    # $0.0000192; one call's peak premium, 16,000 and 12,000 at peak less the
    # same off-peak, adds $0.0096.
    assert Decimal(s["reserved_usd"]) == Decimal("1.3326192") < Decimal("1.50")
    assert Decimal(s["crossing_margin_usd"]) == Decimal("0.0096")
    assert s["reserved_at"] == ["off_peak"] and len(records) == 105


def test_with_peak_allowed_the_reservation_is_priced_at_peak(tmp_path):
    srv = FakeServer(lambda b: reply("ready"), prices=PRICES, clock=lambda: PEAK)
    with srv as url:
        guard = SpendGuard(Decimal("250"), tmp_path / "records" / "spend.jsonl")
        r = Runner(endpoint(url), PRICES, guard, records_dir=tmp_path / "records",
                   transcripts_dir=tmp_path / "transcripts", clock=lambda: PEAK,
                   allow_peak=True)
        s = r.run_batch(Dry(), repeats=3)
    # by hand: (36,000 at $0.30 and 12,000 at $1.20 per million) is $0.0252 a run,
    # $2.646 over 105; the probe at peak adds $0.0000384.
    assert Decimal(s["reserved_usd"]) == Decimal("2.6460384")
    assert s["reserved_at"] == ["off_peak", "peak"]


# -- records free of model text ----------------------------------------------------------------
def test_no_model_text_reaches_a_record(tmp_path, server):
    def plant(item, k, thinking, r, body):
        if r["reasoning"]:
            r["reasoning"] += " " + SENTINEL
        if not r["calls"]:
            r["content"] += " " + SENTINEL
        elif item == "single.weather":
            _args(r, {"location": "Paris " + SENTINEL})
        elif item == "code.json_text":
            r["calls"][0]["function"]["name"] = SENTINEL
        elif item == "unicode.text":
            r["calls"][0]["id"] = SENTINEL
    fake = Conformant(mutate=plant)
    s, by_item, _ = batch(tmp_path, server, fake, QS1())
    assert by_item["single.weather"]["outcome"]["status"] == "fail"
    assert by_item["code.json_text"]["outcome"]["status"] == "fail"
    for p in (tmp_path / "records").rglob("*.jsonl"):
        assert SENTINEL not in p.read_text(encoding="utf-8"), p.name
    transcripts = "".join(p.read_text(encoding="utf-8")
                          for p in (tmp_path / "transcripts").rglob("*.json"))
    assert transcripts.count(SENTINEL) > 30


def test_qs1_reaches_a_model_only_through_context():
    source = Path(qs1.__file__).read_text(encoding="utf-8")
    for word in ("httpx", "Client(", ".post(", ".get(\"/", "stream_lines", "os.environ"):
        assert word not in source, word


# -- the judge, on its own ---------------------------------------------------------------------
def _c(name, arguments, **extra):
    return dict({"id": "call_00_a", "type": "function",
                 "function": {"name": name, "arguments": arguments}}, **extra)


def test_the_matchers():
    m = qs1.match_value
    assert m({"equals": "a"}, "a") is None and m({"equals": "a"}, "A")
    assert m({"equals": "a", "casefold": True, "strip": True}, " A ") is None
    assert m({"equals": "x\n", "trailing_newline": True}, "x") is None
    assert m({"equals": "x", "trailing_newline": True}, "x\n") is None
    assert m({"equals": "x", "trailing_newline": True}, "x\n\n")
    assert m({"equals": "café", "nfc": True}, "cafe" + chr(0x301)) is None
    assert m({"equals": "café"}, "cafe" + chr(0x301))
    assert m({"equals": 1}, True) and m({"equals": 1}, 1) is None
    assert m({"match": "par"}, "paris")                         # a full match, not a prefix
    assert m({"one_of": ["北京", "Beijing"], "casefold": True}, "BEIJING") is None
    assert m({"object": {"a": {"equals": 1}}}, {"a": 1, "b": 2}) == "1 key(s) the golden does not name"
    assert m({"absent_or": {"equals": "c"}}, qs1._ABSENT) is None
    assert m({"equals": "c"}, qs1._ABSENT) == "is missing"
    assert m({"items_any_order": [{"equals": 1}, {"equals": 2}]}, [2, 1]) is None
    assert m({"items_any_order": [{"equals": 1}, {"equals": 2}]}, [1, 1])
    with pytest.raises(ValueError):
        m({"resembles": "x"}, "x")


def test_schema_validity():
    declared = QS1().declared
    v = qs1.schema_valid
    assert v(_c("get_time", "{}"), declared) and not v(_c("get_time", '{"tz": "UTC"}'), declared)
    assert v(_c("get_weather", '{"location": "Oslo", "date": "2026-10-07"}'), declared)
    assert not v(_c("get_weather", '{"location": "Oslo", "date": "tomorrow"}'), declared)
    assert not v(_c("get_weather", '{"location": "Oslo", "zip": "0150"}'), declared)
    assert not v(_c("get_weather", '{"location": "Oslo", "unit": "kelvin"}'), declared)
    assert not v(_c("launch_probe", "{}"), declared) and not v(_c(["x"], "{}"), declared)
    assert not v(_c("get_date", "null"), declared) and not v(_c("get_date", ""), declared)


def test_the_assertions_on_edge_values():
    assert qs1.judge_finish(["stop"], [], frozenset({"stop"}))[0] == "fail"     # unhashable
    assert qs1.judge_finish(None, [], frozenset({"stop"}))[0] == "fail"
    assert qs1.judge_ids([_c("get_date", "{}", id="")])[0] == "fail"
    assert qs1.judge_ids([])[0] == "not_judged"
    assert qs1.judge_reasoning("x", "   ", thinking=False)[0] == "pass"
    assert qs1.judge_reasoning("x", "   ", thinking=True)[0] == "fail"
    short = "a" * (qs1.LEAK_MIN - 1)
    assert qs1.judge_reasoning(short + " and more", short, thinking=True)[0] == "pass"
    assert qs1.judge_special_tokens(None, [])[0] == "pass"
    assert qs1.judge_special_tokens("ok", [_c("get_date", "{}")])[0] == "pass"


def test_the_metrics_and_their_denominators():
    d = [{"metric_inputs": {"trigger": {"tp": 3, "fp": 1, "fn": 1, "tn": 5},
                            "schema": {"calls": 4, "valid": 3}}},
         {"metric_inputs": {"trigger": {"tp": 0, "fp": 0, "fn": 0, "tn": 0},
                            "schema": {"calls": 0, "valid": 0}}},
         None]
    m = qs1.metrics(d)
    assert m["trigger"] == {"tp": 3, "fp": 1, "fn": 1, "tn": 5, "n": 10, "f1_denominator": 8,
                            "f1": 0.75, "agreement": 0.8}
    assert m["schema"] == {"calls": 4, "valid": 3, "accuracy": 0.75}
    empty = qs1.metrics([])
    assert empty["trigger"]["f1"] is None and empty["trigger"]["agreement"] is None
    assert empty["schema"]["accuracy"] is None
    # F1 ignores TN: all-negative turns leave it undefined, and agreement says 1
    neg = qs1.metrics([{"metric_inputs": {"trigger": {"tp": 0, "fp": 0, "fn": 0, "tn": 4},
                                          "schema": {"calls": 0, "valid": 0}}}])
    assert neg["trigger"]["f1"] is None and neg["trigger"]["agreement"] == 1.0
