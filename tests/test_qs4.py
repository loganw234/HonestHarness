"""QS4 end to end, through P0's runner on qs/fake.py, with P2's ScriptedSandbox:
the brief's controls, the statuses, refusal before any call, no model text in a
published record, the ledger file read back, the escalation, streaming, and the
reservation."""
import json
from decimal import Decimal

import pytest

from qs import identity
from qs import record as rec
from qs.agent import ScriptedSandbox
from qs.agent.scripted import ScriptedModel, result, tool_call
from qs.fake import FakeServer, error, reply
from qs.guard import SpendGuard
from qs.providers import deepseek
from qs.registry import Endpoint
from qs.suite import Caps, Runner
from qs.suites import qs4
from test_qs4_support import (StubInputs, Streamed, build_inputs, build_world, copy_local, load_tool, put,
                              report_call, turn)

check = load_tool("check")
PLANTED = [c for c in qs4.SUITES if c.ITEM.endswith("-planted")]


def run(tmp_path, prices, clock, model, suite):
    with FakeServer(model, prices=prices, clock=clock) as url:
        ep = Endpoint(name="fake", provider="deepseek", base_url=url, model="deepseek-flash",
                      price_table="prices/deepseek-2026-10-06.json", key_env=None)
        guard = SpendGuard(Decimal("250"), tmp_path / "records" / "spend.jsonl")
        runner = Runner(ep, prices, guard, records_dir=tmp_path / "records",
                        transcripts_dir=tmp_path / "transcripts", clock=clock)
        summary = runner.run_batch(suite)
    path = tmp_path / "records" / "runs" / f"{suite.name}.jsonl"
    records = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    for r in records:
        rec.validate(r)
    tpath = tmp_path / "transcripts" / summary["batch"] / f"{summary['batch']}.{suite.ITEM}.r0.json"
    transcript = tpath.read_text(encoding="utf-8") if tpath.exists() else ""
    return summary, records, path.read_text(encoding="utf-8"), transcript


def scripted(boxes, files=None):
    def factory(scratch, mounts, budgets):
        box = ScriptedSandbox(shell=lambda c: result(0, "ok\n"), files=dict(files or {}),
                              mounts=tuple(m.name for m in mounts))
        box.host_scratch = scratch
        boxes.append(box)
        return box
    return factory


def make(cls, tmp_path, boxes=None, items=None, stream=False):
    spec = items or qs4.ITEMS
    return cls(inputs=StubInputs(spec, qs4.EXPECTED), sandbox_factory=scripted([] if boxes is None else boxes),
               run_dir=tmp_path / "runs", stream=stream, items=spec)


def plant_findings(cls, statement):
    item = qs4.item_spec(qs4.ITEMS, cls.ITEM)
    out = []
    for pl in qs4.ITEMS["parcels"][item["parcel"]]["plants"]:
        span = qs4.EXPECTED["plant_spans"][pl["id"]]
        out.append({"class": "wrong answer", "file": span["file"],
                    "lines": f"{span['lines'][0]}-{span['lines'][1]}", "statement": statement(pl)})
    return out


# -- the brief's controls ------------------------------------------------------------
def test_a_report_naming_each_plants_fault_at_its_line_scores_10_of_10(tmp_path, prices, off_peak_clock):
    caught = 0
    for cls in PLANTED:
        assert all("*" not in ph for p in qs4.ITEMS["parcels"][qs4.item_spec(qs4.ITEMS, cls.ITEM)["parcel"]]["plants"]
                   for ph in p["markers"][0])
        findings = plant_findings(cls, lambda p: "it says otherwise than its source: " + " and ".join(p["markers"][0]))
        model = ScriptedModel(turn(report_call("c1", findings)))
        _, records, _, _ = run(tmp_path / cls.ITEM, prices, off_peak_clock, model, make(cls, tmp_path))
        q = records[0]["outcome"]["data"]["qs4"]
        assert records[0]["outcome"]["status"] == "pass" and q["status_basis"] == "screen"
        caught += q["counts"]["plants_caught"]
    assert caught == 10


def test_a_report_citing_the_lines_without_the_faults_scores_0(tmp_path, prices, off_peak_clock):
    located = caught = 0
    statement = "This line needs a second look."
    for cls in PLANTED:
        findings = plant_findings(cls, lambda p: statement)
        for p in qs4.ITEMS["parcels"][qs4.item_spec(qs4.ITEMS, cls.ITEM)["parcel"]]["plants"]:
            assert not qs4.markers_hit(statement, p["markers"])
        model = ScriptedModel(turn(report_call("c1", findings)))
        _, records, _, _ = run(tmp_path / cls.ITEM, prices, off_peak_clock, model, make(cls, tmp_path))
        q = records[0]["outcome"]["data"]["qs4"]
        assert records[0]["outcome"]["status"] == "fail"
        located += q["counts"]["plants_located"]
        caught += q["counts"]["plants_caught"]
    assert (located, caught) == (10, 0)


def test_a_report_of_nothing_scores_0_and_is_recorded_as_reported_not_stopped(tmp_path, prices, off_peak_clock):
    caught = 0
    for cls in PLANTED:
        model = ScriptedModel(turn(report_call("c1", [], verdict="READY", text="found nothing")))
        _, records, _, _ = run(tmp_path / cls.ITEM, prices, off_peak_clock, model, make(cls, tmp_path))
        r = records[0]
        q, agent = r["outcome"]["data"]["qs4"], r["outcome"]["data"]["agent"]
        assert r["outcome"]["status"] == "fail" and agent["outcome"] == "reported" and agent["budget"] is None
        assert q["reported"] is True and q["counts"]["findings"] == 0 and q["verdict"] == "READY"
        caught += q["counts"]["plants_caught"]
    assert caught == 0


# -- statuses ------------------------------------------------------------------------
def test_a_budget_stop_is_stopped_and_never_scored(tmp_path, prices, off_peak_clock):
    spec = json.loads(json.dumps(qs4.ITEMS))
    spec["budgets"]["max_turns"] = 2
    model = ScriptedModel(*[turn(tool_call(f"c{i}", "shell", {"command": "ls"})) for i in range(4)])
    _, records, _, _ = run(tmp_path, prices, off_peak_clock, model, make(qs4.QS4P2Planted, tmp_path, items=spec))
    r = records[0]
    q = r["outcome"]["data"]["qs4"]
    assert r["outcome"]["status"] == "stopped" and "turns budget" in r["outcome"]["detail"]
    assert q["reported"] is False and q["counts"] is None and q["plants"] == [] and q["status_basis"] == "agent"


def test_a_cap_stop_is_stopped(tmp_path, prices, off_peak_clock):
    suite = make(qs4.QS4P2Planted, tmp_path)
    suite.caps = Caps(max_prompt_tokens=200_000, max_output_tokens=20_000, max_call_prompt_tokens=100)
    _, records, _, _ = run(tmp_path, prices, off_peak_clock, ScriptedModel(), suite)
    assert records[0]["outcome"]["status"] == "stopped" and "caps budget" in records[0]["outcome"]["detail"]


def test_a_run_that_never_reports_fails_with_no_report(tmp_path, prices, off_peak_clock):
    model = ScriptedModel(*[reply("I am thinking about it.") for _ in range(4)])
    _, records, _, _ = run(tmp_path, prices, off_peak_clock, model, make(qs4.QS4P2Planted, tmp_path))
    r = records[0]
    assert r["outcome"]["status"] == "fail" and "without a report" in r["outcome"]["detail"]
    assert r["outcome"]["data"]["agent"]["outcome"] == "unreported" and r["outcome"]["data"]["qs4"]["counts"] is None


def test_a_provider_failure_is_an_error_and_stops_the_batch(tmp_path, prices, off_peak_clock):
    model = ScriptedModel(turn(tool_call("c1", "shell", {"command": "ls"})), error(503, "busy"))
    s, records, _, _ = run(tmp_path, prices, off_peak_clock, model, make(qs4.QS4P2Real, tmp_path))
    assert records[0]["outcome"]["status"] == "error" and "HTTP 503" in s["stopped_for"]


def test_a_real_tip_passes_on_its_report_and_its_findings_await_adjudication(tmp_path, prices, off_peak_clock):
    findings = [{"class": "restate", "file": "METHOD.md", "lines": "340-342", "statement": "wider than the survey"},
                {"class": "other", "file": "METHOD.md", "lines": "100", "statement": "something new"}]
    model = ScriptedModel(turn(report_call("c1", findings)))
    _, records, _, _ = run(tmp_path, prices, off_peak_clock, model, make(qs4.QS4P2Real, tmp_path))
    q = records[0]["outcome"]["data"]["qs4"]
    assert records[0]["outcome"]["status"] == "pass" and q["status_basis"] == "reported" and q["plants"] == []
    assert [f["matched"] for f in q["findings"]] == ["r6:P2-r1", None] and q["counts"]["unmatched"] == 1


# -- what is recorded ------------------------------------------------------------------
def test_no_model_text_reaches_a_published_record(tmp_path, prices, off_peak_clock):
    s = "SENTINEL-QS4"
    model = ScriptedModel(
        turn(tool_call("c1", "write_file", {"path": "verifier-P2.md", "content": f"## an entry {s}\n"})),
        turn(tool_call("c2", "escalate", {"question": f"a question {s}"})),
        reply(f"content {s}", reasoning=f"reasoning {s}", tool_calls=[report_call("c3", [
            {"class": "wrong answer", "file": f"{s}.md", "lines": "1", "statement": f"statement {s}"},
            {"class": "wrong answer", "file": "METHOD.md", "lines": "414", "statement": f"38 {s}"}], text=f"text {s}")],
            finish="tool_calls"))
    _, records, text, transcript = run(tmp_path, prices, off_peak_clock, model, make(qs4.QS4P2Planted, tmp_path))
    assert s not in text and check.findings(text) == [] and s in transcript
    q = records[0]["outcome"]["data"]["qs4"]
    assert q["findings"][0]["file"] == qs4.UNLISTED and q["escalations"] == 1


def test_the_ledger_file_is_read_back_through_the_manifest(tmp_path, prices, off_peak_clock):
    model = ScriptedModel(
        turn(tool_call("c1", "write_file", {"path": "verifier-P2.md", "content": "## 2026-10-07 entry\n"})),
        turn(report_call("c2", [])))
    _, records, _, transcript = run(tmp_path, prices, off_peak_clock, model, make(qs4.QS4P2Planted, tmp_path))
    assert records[0]["outcome"]["data"]["qs4"]["ledger_file"] == {"kind": "file", "bytes": 20}
    local = json.loads(transcript)["result"]["local"]["qs4"]
    assert local["ledger_file"]["text"] == "## 2026-10-07 entry\n" and local["scored"] is True


def test_a_link_in_place_of_the_ledger_file_is_recorded_and_not_read(tmp_path, prices, off_peak_clock):
    boxes = []
    suite = make(qs4.QS4P2Planted, tmp_path, boxes)
    real = suite.sandbox_factory

    def factory(scratch, mounts, budgets):
        box = real(scratch, mounts, budgets)
        box.scratch_manifest = lambda: [{"path": "/work/scratch/verifier-P2.md", "kind": "link", "bytes": 0,
                                         "sha256": None}]
        return box
    suite.sandbox_factory = factory
    _, records, _, _ = run(tmp_path, prices, off_peak_clock, ScriptedModel(turn(report_call("c1", []))), suite)
    assert records[0]["outcome"]["data"]["qs4"]["ledger_file"] == {"kind": "link", "bytes": 0}


@pytest.mark.parametrize("change,kind", [("hash", "changed"), ("size", "too large")])
def test_a_ledger_file_that_changed_or_is_too_large_is_not_read(tmp_path, prices, off_peak_clock, change, kind):
    spec = json.loads(json.dumps(qs4.ITEMS))
    if change == "size":
        spec["settings"]["ledger_file_cap"] = 5
    suite = make(qs4.QS4P2Planted, tmp_path, items=spec)
    real = suite.sandbox_factory

    def factory(scratch, mounts, budgets):
        box = real(scratch, mounts, budgets)
        if change == "hash":
            plain = box.scratch_manifest
            box.scratch_manifest = lambda: [dict(e, sha256="0" * 64) for e in plain()]
        return box
    suite.sandbox_factory = factory
    model = ScriptedModel(turn(tool_call("c1", "write_file", {"path": "verifier-P2.md", "content": "an entry\n"})),
                          turn(report_call("c2", [])))
    _, records, _, transcript = run(tmp_path, prices, off_peak_clock, model, suite)
    assert records[0]["outcome"]["data"]["qs4"]["ledger_file"]["kind"] == kind
    assert json.loads(transcript)["result"]["local"]["qs4"]["ledger_file"]["text"] is None


def test_a_report_without_its_findings_list_is_answered_as_malformed(tmp_path, prices, off_peak_clock):
    model = ScriptedModel(turn(tool_call("c1", "report", {"verdict": "READY", "text": "no list"})),
                          turn(report_call("c2", [])))
    _, records, _, _ = run(tmp_path, prices, off_peak_clock, model, make(qs4.QS4P2Planted, tmp_path))
    agent = records[0]["outcome"]["data"]["agent"]
    assert agent["malformed"] == 1 and agent["outcome"] == "reported" and agent["turns"] == 2


def test_a_runs_scratch_is_named_by_a_random_id_and_holds_the_verifiers_empty_directory(tmp_path, prices,
                                                                                         off_peak_clock):
    boxes = []
    run(tmp_path, prices, off_peak_clock, ScriptedModel(turn(report_call("c1", []))),
        make(qs4.QS4P2Real, tmp_path, boxes))
    scratch = boxes[0].host_scratch
    assert len(scratch.name) == 12 and int(scratch.name, 16) >= 0 and scratch.parent == tmp_path / "runs"
    assert [p.name for p in scratch.iterdir()] == ["r6-vP2"] and not any((scratch / "r6-vP2").iterdir())


def test_the_escalation_answers_with_the_committed_reply(tmp_path, prices, off_peak_clock):
    model = ScriptedModel(turn(tool_call("c1", "escalate", {"question": "may I?"})), turn(report_call("c2", [])))
    run(tmp_path, prices, off_peak_clock, model, make(qs4.QS4P2Planted, tmp_path))
    tool_msgs = [m for m in model.bodies[1]["messages"] if m["role"] == "tool"]
    assert tool_msgs[-1]["content"].endswith(qs4.PROMPT["escalate-reply"])


def test_the_live_setting_streams_and_still_reports(tmp_path, prices, off_peak_clock):
    assert qs4.ITEMS["settings"]["stream"] is True
    model = ScriptedModel(turn(report_call("c1", [])))
    suite = qs4.QS4P1Real(inputs=StubInputs(qs4.ITEMS, qs4.EXPECTED), sandbox_factory=scripted([]),
                          run_dir=tmp_path / "runs")
    _, records, _, _ = run(tmp_path, prices, off_peak_clock, Streamed(model), suite)
    assert model.bodies[0]["stream"] is True and records[0]["outcome"]["status"] == "pass"


# -- the prompt --------------------------------------------------------------------
@pytest.mark.parametrize("cls", qs4.SUITES, ids=lambda c: c.ITEM)
def test_each_items_messages_carry_its_commit_and_the_adaptation_and_no_host_path(cls):
    item = qs4.item_spec(qs4.ITEMS, cls.ITEM)
    p = qs4.ITEMS["parcels"][item["parcel"]]
    sysmsg, user = qs4.render_messages(qs4.PROMPT, qs4.ITEMS, item)
    text = sysmsg["content"] + user["content"]
    assert f"detached at {qs4.item_commit(qs4.ITEMS, item)[:7]}, parent {p['base'][:7]}" in user["content"]
    assert "<repos> is /work/ro" in user["content"] and "is not given in this run" in user["content"]
    assert ("do not open keys/" in user["content"]) is (p["wave"] == 2)
    assert "${" not in text and check.findings(text) == []
    other = p["tip"][:7] if item["kind"] == "planted" else p["copy"][:7]
    assert other not in text


def test_the_prompt_has_every_section_and_a_planted_and_a_real_run_read_alike():
    assert set(qs4.PROMPT_SECTIONS) <= set(qs4.PROMPT)
    a = qs4.render_messages(qs4.PROMPT, qs4.ITEMS, qs4.item_spec(qs4.ITEMS, "p3-planted"))
    b = qs4.render_messages(qs4.PROMPT, qs4.ITEMS, qs4.item_spec(qs4.ITEMS, "p3-real"))
    p = qs4.ITEMS["parcels"]["P3"]
    assert a[1]["content"].replace(p["copy"][:7], "X") == b[1]["content"].replace(p["tip"][:7], "X")


# -- refusal, classes, version, reservation ----------------------------------------------
def test_each_item_has_one_suite_class_named_for_it():
    assert [c.ITEM for c in qs4.SUITES] == [i["id"] for i in qs4.ITEMS["items"]]
    for c in qs4.SUITES:
        assert c.name == f"qs4-{c.ITEM}" and getattr(qs4, c.__name__) is c
    with pytest.raises(TypeError):
        qs4.QS4()


def test_a_class_built_with_no_local_inputs_refuses_before_any_spend(tmp_path):
    with pytest.raises(qs4.InputError, match="build the inputs"):
        qs4.QS4P2Planted(local=tmp_path / "nothing", sandbox_factory=scripted([]))


def test_an_input_changed_after_construction_is_refused_in_run_item_with_no_call(tmp_path, prices, off_peak_clock):
    w = build_world(tmp_path / "w")
    expected = build_inputs(w)
    local = copy_local(w, tmp_path / "local")
    cls = type("QS4W", (qs4.QS4,), {"ITEM": "p1-planted", "name": "qs4w-p1-planted"})
    inputs = qs4.LocalInputs(local, items=w.items, expected=expected, image_id=lambda: "test-image")
    suite = cls(inputs=inputs, items=w.items, expected=expected, sandbox_factory=scripted([]),
                run_dir=tmp_path / "runs", stream=False)
    put(local / "repos" / expected["repos"]["p1-planted"]["commit"][:12], "METHOD.md", "changed\n")
    model = ScriptedModel(turn(report_call("c1", [])))
    _, records, _, _ = run(tmp_path, prices, off_peak_clock, model, suite)
    r = records[0]
    assert r["outcome"]["status"] == "error" and "an input failed its checks" in r["outcome"]["detail"]
    assert r["calls"] == 0 and model.bodies == [] and r["outcome"]["data"]["qs4"]["status_basis"] == "input"


def test_the_version_names_the_data_and_the_code():
    assert qs4.VERSION == qs4.compute_version() and qs4.QS4.version == qs4.VERSION
    parts = qs4.VERSION.split(".")
    assert parts[0] == "1" and all(len(x) == 12 and int(x, 16) >= 0 for x in parts[1:])


def test_one_run_reserves_the_hand_computed_worst_case(tmp_path, prices, off_peak_clock):
    caps = qs4.QS4.caps
    m, out = "deepseek-flash", min(caps.max_output_tokens, deepseek.MAX_TOKENS)
    wc = prices.worst_case
    run_worst = wc(m, "off_peak", caps.max_prompt_tokens + caps.max_call_prompt_tokens, caps.max_output_tokens)
    probe = wc(m, "off_peak", identity.PROBE_MAX_PROMPT, identity.PROBE_MAX_OUTPUT)
    crossing = wc(m, "peak", caps.max_call_prompt_tokens, out) - wc(m, "off_peak", caps.max_call_prompt_tokens, out)
    s, _, _, _ = run(tmp_path, prices, off_peak_clock, ScriptedModel(turn(report_call("c1", []))),
                     make(qs4.QS4P2Planted, tmp_path))
    assert Decimal(s["reserved_usd"]) == run_worst + probe + crossing == Decimal("6.8059488")
