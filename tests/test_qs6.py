"""QS6 through P0's runner, against qs/fake.py on 127.0.0.1 only, on the
synthetic world of tests/test_qs6_support.py.

The controls: the key scores 100% at every cut; a planted wrong answer, an
overclaim, a dropped unit and a reply without an answer field each score as
that class. Then the statuses (a harness cap is stopped, a provider's
condition or error is error, never fail), the refusals before any call, the
request QS6 sends, records free of model text, the table, and the reservation
at the committed caps."""
import inspect
import json
import sys
from collections import Counter
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from qs.fake import FakeReply, error, reply  # noqa: E402
from qs.suite import Caps, Item, ItemResult, Suite  # noqa: E402
from qs.suites import qs6  # noqa: E402
from test_qs6_support import (OFF_PEAK, PEAK, Answers, make_world, question_of,  # noqa: E402
                              run)

SENTINEL = "QS6-SENTINEL-8e7f"


def keyed(world, suite, rotate=True):
    """content(iid, body): each item answered with its key's own forms, in turn."""
    forms = {iid: qs6.answer_forms(world.specs[iid], suite.key[iid]) for iid in suite.specs}
    seen = Counter()

    def content(iid, body):
        f = forms[iid][seen[iid] % len(forms[iid]) if rotate else 0]
        seen[iid] += 1
        return f
    return content


# -- the controls ---------------------------------------------------------------------------------
def test_the_key_scores_100_percent_at_every_cut(tmp_path):
    w = make_world(tmp_path)
    nil_runs = Counter()
    for cut in qs6.CUT_NAMES:
        suite = w.suite(cut)
        s, _, records = run(tmp_path / cut, suite, Answers(w, keyed(w, suite)), repeats=2)
        assert s["stopped_for"] is None and len(records) == 2 * len(suite.specs)
        for r in records:
            d = r["outcome"]["data"]
            assert (r["outcome"]["status"], d["class"], d["cut"]) == ("pass", "exact", cut), r["item"]
            nil_runs[cut] += d["key_kind"] == "not_in_input"
    # "Not in the input" keys were asked and scored too: S05 to S07 at c016k,
    # S07 at c032k, two repeats each.
    assert dict(nil_runs) == {"c016k": 6, "c032k": 2, "c064k": 0, "c128k": 0, "whole": 0}


def test_not_in_the_input_scores_exact_where_the_key_says_so(tmp_path):
    w = make_world(tmp_path)
    suite = w.suite("c016k")
    _, by_item, _ = run(tmp_path, suite, Answers(w, keyed(w, suite, rotate=False)))
    nil = {iid for iid, r in by_item.items() if r["outcome"]["data"]["key_kind"] == "not_in_input"}
    assert nil == {"S05", "S06", "S07"}
    assert all(by_item[i]["outcome"]["data"]["class"] == "exact" for i in nil)


def test_a_wrong_answer_an_overclaim_a_dropped_unit_and_no_answer_each_score_as_that_class(tmp_path):
    w = make_world(tmp_path)
    suite = w.suite("c016k")
    plants = {"S01": "ANSWER: 9999999",            # a wrong SHA
              "S05": "ANSWER: 10:15:00",           # a value where the key is not in the input
              "S03": "ANSWER: 4.5",                # the right figure without its unit
              "S02": "I counted them all."}        # no answer field
    base = keyed(w, suite, rotate=False)
    _, by_item, records = run(tmp_path, suite, Answers(w, lambda i, b: plants.get(i) or base(i, b)))
    got = {i: (r["outcome"]["status"], r["outcome"]["data"]["class"]) for i, r in by_item.items()}
    assert got["S01"] == ("fail", "wrong")
    assert got["S05"] == ("fail", "overclaim")
    assert got["S03"] == ("fail", "dropped_unit")
    assert got["S02"] == ("fail", "no_answer")
    assert all(got[i] == ("pass", "exact") for i in got if i not in plants)


def test_an_answer_in_reasoning_alone_is_no_answer(tmp_path):
    w = make_world(tmp_path)
    suite = w.suite("c016k")
    responder = Answers(w, lambda i, b: "I have read the ledger.",
                        reasoning="Reading it through. ANSWER: abc1234\nANSWER: abc1234")
    _, by_item, _ = run(tmp_path, suite, responder, thinking=True)
    d = by_item["S01"]["outcome"]["data"]
    assert by_item["S01"]["outcome"]["status"] == "fail" and d["class"] == "no_answer"
    assert all(b["thinking"] == {"type": "enabled"} for b in responder.bodies)


# -- statuses: never the model's failure ------------------------------------------------------------
def only(iid, fr, w, suite):
    base = keyed(w, suite, rotate=False)
    return Answers(w, lambda i, b: (fr(b) if callable(fr) else fr) if i == iid else base(i, b))


def test_a_length_finish_at_the_harness_clamp_is_stopped_and_below_it_error(tmp_path):
    w = make_world(tmp_path)
    suite = w.suite("c016k")
    at_clamp = only("S01", lambda b: reply("ANSWER: abc", finish="length",
                                           usage=(0, 3000, b["max_tokens"], 0)), w, suite)
    _, by_item, _ = run(tmp_path / "a", suite, at_clamp)
    d = by_item["S01"]["outcome"]["data"]
    assert by_item["S01"]["outcome"]["status"] == "stopped"
    assert (d["status_basis"], d["length_cause"], d["max_tokens_sent"]) == (
        "harness_cap", "harness_clamp", qs6.MAX_OUTPUT_TOKENS)
    below = only("S01", reply("ANSWER: abc1234", finish="length", usage=(0, 3000, 10, 0)), w, suite)
    _, by_item, _ = run(tmp_path / "b", suite, below)
    d = by_item["S01"]["outcome"]["data"]
    assert by_item["S01"]["outcome"]["status"] == "error"
    assert (d["status_basis"], d["length_cause"], d["class"]) == (
        "provider_condition", "below_request_max_tokens", None)


@pytest.mark.parametrize("finish", ["content_filter", "insufficient_system_resource", "aborted"])
def test_a_provider_condition_is_error_and_the_batch_goes_on(tmp_path, finish):
    w = make_world(tmp_path)
    suite = w.suite("c016k")
    s, by_item, _ = run(tmp_path, suite, only("S01", reply("ANSWER: abc1234", finish=finish), w, suite))
    d = by_item["S01"]["outcome"]["data"]
    assert by_item["S01"]["outcome"]["status"] == "error" and d["status_basis"] == "provider_condition"
    assert d["class"] is None and s["runs"] == len(suite.specs) and s["stopped_for"] is None


def test_a_finish_qs6_does_not_score_is_error(tmp_path):
    w = make_world(tmp_path)
    suite = w.suite("c016k")
    _, by_item, _ = run(tmp_path, suite, only("S01", reply("ANSWER: abc1234", finish="tool_calls"), w, suite))
    d = by_item["S01"]["outcome"]["data"]
    assert by_item["S01"]["outcome"]["status"] == "error" and d["status_basis"] == "unexpected_finish"


def test_a_400_is_error_and_the_batch_goes_on(tmp_path):
    w = make_world(tmp_path)
    suite = w.suite("c016k")
    s, by_item, _ = run(tmp_path, suite, only("S01", error(400, "context too long"), w, suite))
    d = by_item["S01"]["outcome"]["data"]
    assert by_item["S01"]["outcome"]["status"] == "error" and (d["status_basis"], d["http"]) == ("provider_error", 400)
    assert s["runs"] == len(suite.specs) and s["stopped_for"] is None


@pytest.mark.parametrize("status", [429, 503])
def test_a_status_the_next_request_would_meet_is_error_and_stops_the_batch(tmp_path, status):
    w = make_world(tmp_path)
    suite = w.suite("c016k")
    s, by_item, _ = run(tmp_path, suite, only("S01", error(status, "later"), w, suite))
    assert by_item["S01"]["outcome"]["status"] == "error" and s["runs"] == 1
    assert f"HTTP {status}" in s["stopped_for"]


def test_a_reply_dropped_after_billing_is_error_and_stops_the_batch(tmp_path):
    w = make_world(tmp_path)
    suite = w.suite("c016k")
    s, by_item, _ = run(tmp_path, suite, only("S01", FakeReply(body=reply("x").body, drop=True), w, suite))
    d = by_item["S01"]["outcome"]["data"]
    assert by_item["S01"]["outcome"]["status"] == "error" and d["status_basis"] == "transport"
    assert s["runs"] == 1 and "did not arrive whole" in s["stopped_for"]
    # Every attempt dropped: retried twice, then the batch stops.
    assert by_item["S01"]["unmetered_calls"] == 3 and s["unmetered_attempts"] == 3


def test_a_cap_reached_is_stopped_never_fail(tmp_path):
    w = make_world(tmp_path)
    suite = w.suite("c016k")
    suite.caps = Caps(max_prompt_tokens=1, max_output_tokens=qs6.MAX_OUTPUT_TOKENS, max_call_prompt_tokens=100)
    responder = Answers(w, keyed(w, suite))
    _, by_item, records = run(tmp_path, suite, responder)
    assert responder.bodies == []                      # refused before anything was sent
    assert {r["outcome"]["status"] for r in records} == {"stopped"}
    assert {r["outcome"]["data"]["status_basis"] for r in records} == {"harness_cap"}


def test_one_call_per_run_a_second_would_meet_the_prompt_cap():
    assert qs6.MAX_PROMPT_TOKENS == 1
    assert all(c.caps.max_prompt_tokens == 1 for c in qs6.CUT_CLASSES.values())


# -- refusals before any call -----------------------------------------------------------------------
def test_a_missing_or_changed_local_copy_is_refused(tmp_path):
    w = make_world(tmp_path)
    data = bytearray(w.archive_bytes)
    data[100] ^= 1
    w.archive.write_bytes(bytes(data))
    with pytest.raises(qs6.SourceError, match="SHA-256"):
        w.suite("c016k")
    w.archive.unlink()
    with pytest.raises(qs6.SourceError, match="missing"):
        w.suite("c016k")


def test_a_missing_or_changed_key_is_refused(tmp_path):
    w = make_world(tmp_path)
    w.key.write_bytes(w.key.read_bytes().replace(b'"abc1234"', b'"abc1235"'))
    with pytest.raises(qs6.SourceError, match="key"):
        w.suite("c016k")
    w.key.unlink()
    with pytest.raises(qs6.SourceError, match="missing"):
        w.suite("c016k")


def test_a_key_without_an_entry_for_an_item_at_the_cut_is_refused(tmp_path):
    w = make_world(tmp_path, doc_edit=lambda doc: doc["items"]["S03"].pop("c032k"))
    w.suite("c016k")
    with pytest.raises(ValueError, match="S03 at c032k"):
        w.suite("c032k")


def test_a_cut_whose_text_is_not_the_committed_ones_is_refused(tmp_path):
    w = make_world(tmp_path)
    w.data["cuts"]["cuts"][1]["sha256"] = "0" * 64
    w.suite("c016k")
    with pytest.raises(qs6.SourceError, match="c032k"):
        w.suite("c032k")


def test_the_cut_classes_take_no_arguments_and_refuse_without_the_local_copy(tmp_path, monkeypatch):
    monkeypatch.setattr(qs6, "ARCHIVE_PATH", tmp_path / "absent" / "round6-ledger.zip")
    for cls in qs6.CUT_CLASSES.values():
        params = inspect.signature(cls).parameters.values()
        assert all(p.kind is p.KEYWORD_ONLY and p.default is None for p in params)
        with pytest.raises(qs6.SourceError, match="tools/qs6_extract.py"):
            cls()
    with pytest.raises(TypeError):
        qs6.QS6()


# -- the request, and what the record keeps ----------------------------------------------------------
def test_the_request_is_one_call_with_the_cut_first_and_nothing_else_sent(tmp_path):
    w = make_world(tmp_path)
    suite = w.suite("c032k")
    responder = Answers(w, keyed(w, suite))
    s, by_item, records = run(tmp_path, suite, responder)
    prompt = w.data["items"]["prompt"]
    prefix = prompt["before_ledger"] + suite.text + prompt["after_ledger"]
    for b in responder.bodies:
        assert [m["role"] for m in b["messages"]] == ["system", "user"]
        assert b["messages"][0]["content"] == prompt["system"]
        assert b["messages"][1]["content"].startswith(prefix)
        assert b["messages"][1]["content"].endswith(question_of(b) + prompt["after_question"])
        assert b["thinking"] == {"type": "disabled"} and b["max_tokens"] == qs6.MAX_OUTPUT_TOKENS
        for k in ("tools", "tool_choice", "temperature", "top_p", "stream", "response_format"):
            assert k not in b
    assert all(r["calls"] == 1 for r in records)


def test_the_record_keeps_the_cut_the_class_and_the_measured_size(tmp_path):
    w = make_world(tmp_path)
    suite = w.suite("c064k")
    _, by_item, _ = run(tmp_path, suite, Answers(w, keyed(w, suite), usage=(2800, 200, 40, 0)))
    r = by_item["S07"]
    d = r["outcome"]["data"]
    assert (d["cut"], d["set"], d["type"], d["key_kind"], d["class"]) == ("c064k", "reach", "file", "value", "exact")
    assert d["cut_time"] == datetime.fromisoformat(suite.data["cuts"]["cuts"][2]["time"]).isoformat()
    assert d["prompt_tokens"] == r["usage"]["cache_hit"] + r["usage"]["cache_miss"] == 3000
    assert d["key_sha256_12"] == w.data["items"]["key_sha256"][:12]
    assert d["cut_sha256_12"] == w.data["cuts"]["cuts"][2]["sha256"][:12]
    assert d["answer"] == "P1.md" and d["finish_reason"] == "stop" and d["content"] == "text"
    assert r["suite"] == "qs6-c064k" and r["suite_version"] == qs6.VERSION


def test_no_model_text_reaches_a_record(tmp_path):
    w = make_world(tmp_path)
    suite = w.suite("c128k")
    content = (f"I read it. {SENTINEL}\nANSWER: {SENTINEL}\n"
               f"ANSWER: {SENTINEL}.md 4.5 {SENTINEL} 7 abc1234 10:15:00 {SENTINEL}")
    s, _, records = run(tmp_path, suite, Answers(w, lambda i, b: content, reasoning=f"Thinking {SENTINEL}"),
                        thinking=True)
    assert len(records) == len(suite.specs)
    for p in (tmp_path / "records").rglob("*.jsonl"):
        assert SENTINEL not in p.read_text(encoding="utf-8"), p.name
    transcripts = "".join(p.read_text(encoding="utf-8") for p in (tmp_path / "transcripts").rglob("*.json"))
    assert transcripts.count(SENTINEL) >= 3 * len(suite.specs)
    assert all(r["outcome"]["detail"].count(SENTINEL) == 0 for r in records)


def test_qs6_reaches_a_model_only_through_context():
    source = Path(qs6.__file__).read_text(encoding="utf-8")
    for word in ("httpx", "Client(", ".post(", "stream_lines", "os.environ", "urllib"):
        assert word not in source, word


# -- the table ------------------------------------------------------------------------------------------
def test_the_table_pools_classes_by_cut_set_and_thinking(tmp_path):
    w = make_world(tmp_path)
    suite = w.suite("c016k")
    base = keyed(w, suite, rotate=False)
    plants = {"S01": "ANSWER: 9999999", "S05": "ANSWER: 10:15:00"}
    _, _, records = run(tmp_path, suite, Answers(w, lambda i, b: plants.get(i) or base(i, b)), repeats=2)
    rows = {(r["cut"], r["set"]): r for r in qs6.table(records)}
    length, reach = rows[("c016k", "length")], rows[("c016k", "reach")]
    assert length["value"]["exact"] == 6 and length["value"]["wrong"] == 2
    assert length["accuracy"] == 6 / 8 and length["accuracy_denominator"] == 8
    assert reach["not_in_input"]["overclaim"] == 2 and reach["not_in_input"]["exact"] == 4
    assert reach["overclaim_rate"] == 2 / 6 and reach["value"]["exact"] == 2
    assert length["median_prompt_tokens"] == 3000 and length["thinking"] is False


# -- the reservation, at the committed caps --------------------------------------------------------------
class Dry(Suite):
    """A cut's 22 items and committed caps, with no calls: the reservation
    depends only on the caps, the item count and the repeats."""

    def __init__(self, cut):
        self.name = f"qs6-{cut}"
        self.caps = qs6.CUT_CLASSES[cut].caps
        self._items = [Item(it["id"]) for it in qs6.load_data()["items"]["items"]]

    def items(self):
        return self._items

    def run_item(self, ctx, item):
        return ItemResult("skipped", "no call")


def by_hand(max_call: int, peak: bool) -> Decimal:
    """The runner's worst case worked by hand, per million tokens: a run is
    (1 + max_call) prompt and 32,000 output; 66 runs; the probe's 64 and 16;
    off-peak only, one call's peak premium; and three unmetered attempts, each
    one call at peak (P0's retry allowance, the round's ledger 19:11:24)."""
    miss, out = (Decimal("0.30"), Decimal("1.20")) if peak else (Decimal("0.15"), Decimal("0.60"))
    m = Decimal(1_000_000)
    run_ = ((1 + max_call) * miss + 32_000 * out) / m
    probe = (64 * miss + 16 * out) / m
    crossing = Decimal(0) if peak else (max_call * Decimal("0.15") + 32_000 * Decimal("0.60")) / m
    unmetered = 3 * (max_call * Decimal("0.30") + 32_000 * Decimal("1.20")) / m
    return run_ * 66 + probe + crossing + unmetered


# The figures P3.md's design gives (15:21:02), at the caps qs6_cuts.json holds,
# each plus P0's unmetered margin of three calls at peak: 0.1458, 0.1719,
# 0.2259, 0.3501 and 0.3735 (the round's ledger 19:11:24).
RESERVED = {"c016k": ("1.77392910", "3.3534582"), "c032k": ("2.09147910", "3.9537582"),
            "c064k": ("2.74847910", "5.1957582"), "c128k": ("4.25957910", "8.0523582"),
            "whole": ("4.54427910", "8.5905582")}


@pytest.mark.parametrize("cut", qs6.CUT_NAMES)
def test_each_batchs_reservation_at_three_repeats_is_the_hand_computed_worst_case(tmp_path, cut):
    s, _, records = run(tmp_path, Dry(cut), lambda b: reply("ready"), repeats=3)
    max_call = qs6.CUT_CLASSES[cut].caps.max_call_prompt_tokens
    assert Decimal(s["reserved_usd"]) == by_hand(max_call, peak=False) == Decimal(RESERVED[cut][0])
    assert s["reserved_at"] == ["off_peak"] and len(records) == 66
    assert Decimal(s["reserved_usd"]) < Decimal("12.50")      # the balance last read


@pytest.mark.parametrize("cut", ["c016k", "whole"])
def test_with_peak_allowed_the_reservation_is_priced_at_peak(tmp_path, cut):
    s, _, _ = run(tmp_path, Dry(cut), lambda b: reply("ready"), repeats=3, clock=PEAK, allow_peak=True)
    max_call = qs6.CUT_CLASSES[cut].caps.max_call_prompt_tokens
    assert Decimal(s["reserved_usd"]) == by_hand(max_call, peak=True) == Decimal(RESERVED[cut][1])
    assert s["reserved_at"] == ["off_peak", "peak"]


def test_records_are_json_lines_the_schema_takes(tmp_path):
    from qs.record import validate
    w = make_world(tmp_path)
    suite = w.suite("whole")
    _, _, records = run(tmp_path, suite, Answers(w, keyed(w, suite)))
    for r in records:
        validate(json.loads(json.dumps(r)))
