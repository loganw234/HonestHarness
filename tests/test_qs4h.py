"""QS4h end to end, through P0's runner on qs/fake.py, with P2's ScriptedSandbox: the
brief's controls on the committed data (8 of 8 caught by the screen; 0 of 8 for spans
without the faults; nothing for an empty report and for none), the statuses, refusal
before any call, no model text in a published record, the prompt, the reservation, and
QS4's version unmoved."""
import hashlib
import json
from decimal import Decimal

import pytest

from qs import identity
from qs import record as rec
from qs.agent.scripted import ScriptedModel, result, tool_call
from qs.fake import FakeServer, reply
from qs.guard import SpendGuard
from qs.prices import PriceTable
from qs.providers import deepseek
from qs.registry import Endpoint
from qs.suite import Runner
from qs.suites import qs4, qs4h
from test_qs4h_support import ROOT, StubInputs, build_inputs, build_world, report_call, turn

PLANTED = [c for c in qs4h.SUITES if c.ITEM.endswith("-planted")]


def run(tmp_path, prices, clock, model, suite, max_unmetered=3):
    with FakeServer(model, prices=prices, clock=clock, balance="40.00") as url:
        ep = Endpoint(name="fake", provider="deepseek", base_url=url, model="deepseek-flash",
                      price_table="prices/deepseek-2026-10-06.json", key_env=None)
        guard = SpendGuard(Decimal("250"), tmp_path / "records" / "spend.jsonl")
        runner = Runner(ep, prices, guard, records_dir=tmp_path / "records", transcripts_dir=tmp_path / "transcripts",
                        clock=clock, retry_delays=(0, 0), max_unmetered=max_unmetered)
        summary = runner.run_batch(suite)
    path = tmp_path / "records" / "runs" / f"{suite.name}.jsonl"
    records = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    for r in records:
        rec.validate(r)
    t = tmp_path / "transcripts" / summary["batch"] / f"{summary['batch']}.{suite.ITEM}.r0.json"
    return summary, records, path.read_text(encoding="utf-8"), t.read_text(encoding="utf-8") if t.exists() else ""


def scripted(boxes):
    from qs.agent import ScriptedSandbox

    def factory(scratch, mounts, budgets):
        box = ScriptedSandbox(shell=lambda c: result(0, "ok\n"), mounts=tuple(m.name for m in mounts))
        boxes.append(box)
        return box
    return factory


def make(cls, tmp_path, items=None, expected=None, boxes=None):
    items = items or qs4h.ITEMS
    expected = qs4h.EXPECTED if expected is None else expected
    return cls(inputs=StubInputs(items, expected), sandbox_factory=scripted([] if boxes is None else boxes),
               run_dir=tmp_path / "runs", items=items, expected=expected, stream=False)


def finding(file, lines, statement, cls="wrong answer"):
    return {"class": cls, "file": file, "lines": lines, "statement": statement}


def data_of(records):
    return records[0]["outcome"]["data"]["qs4h"]


# -- the brief's controls, on the committed data ---------------------------------------------------
# A statement of each plant's fault, as a verifier would write one, and one that only
# describes the same lines.
STATED = {
    "P1-A": "nested.event's golden expects the priority normal, but its prompt and right text give high",
    "P1-B": "special_tokens no longer scans a call's name, though the module docstring says it does",
    "P2-A": "the malformed-call streak is never reset after a well-formed call, so the run stops at the fourth "
            "malformed call in total",
    "P2-B": "the run-time budget, max_run_seconds, is no longer checked before each tool call, so a turn's calls "
            "run past it",
    "P3-A": "R09 asks how many entries verifier-P1 has written, but every line it cites is verifier-P0.md's",
    "P3-B": "L06 asks for entries before 18:00, but its cited verifier-P0.md:46 is stamped 18:38:25",
    "P4-A": "the dispatch says the copy holds two planted faults; round 6's brief says it may hold faults, and a "
            "real tip holds none",
    "P4-B": "a planted item passes when one of its two plants is caught; the docstring says both",
}
NEUTRAL = {
    "P1-A": "the create_event golden's argument matchers: title, priority and location",
    "P1-B": "the loop that builds the places list from each call",
    "P2-A": "the branch that handles an argument error, and the handler's try block",
    "P2-B": "the head of the loop over a turn's calls",
    "P3-A": "R09's entry: a reach item, with its question and its evidence list",
    "P3-B": "L06's entry: a length item, with its question and its evidence list",
    "P4-A": "the dispatch's bullet that names the copy and its commit",
    "P4-B": "the judge's branch for planted items",
}


def plant_findings(item_id, statements):
    parcel = qs4h.item_spec(qs4h.ITEMS, item_id)["parcel"]
    out = []
    for pl in qs4h.ITEMS["parcels"][parcel]["plants"]:
        e = qs4h.EXPECTED["plant_spans"][pl["id"]][0]
        out.append(finding(e["file"], f"{e['lines'][0]}-{e['lines'][1]}", statements[pl["id"]]))
    return out


@pytest.mark.parametrize("statements, caught", [(STATED, 8), (NEUTRAL, 0)])
def test_the_screen_on_the_committed_data(tmp_path, prices, off_peak_clock, statements, caught):
    """A scripted model reporting each plant at its spans, naming its fault, scores 8 of
    8; one citing the same spans without naming the faults scores 0."""
    total, statuses = 0, []
    for cls in PLANTED:
        model = ScriptedModel(turn(report_call("r1", plant_findings(cls.ITEM, statements))))
        _, records, _, _ = run(tmp_path / cls.ITEM, prices, off_peak_clock, model, make(cls, tmp_path / cls.ITEM))
        d = data_of(records)
        total += d["counts"]["plants_caught"]
        statuses.append(records[0]["outcome"]["status"])
        assert d["counts"]["plants_located"] == 2          # located either way: only the statement differs
    assert total == caught
    assert statuses == (["pass"] * 4 if caught else ["fail"] * 4)


def test_an_empty_report_scores_nothing_and_is_recorded_as_reported(tmp_path, prices, off_peak_clock):
    model = ScriptedModel(turn(report_call("r1", [], verdict="READY")))
    _, records, _, _ = run(tmp_path, prices, off_peak_clock, model, make(qs4h.QS4hH2Planted, tmp_path))
    d = data_of(records)
    assert records[0]["outcome"]["status"] == "fail"
    assert d["reported"] is True and d["verdict"] == "READY" and d["counts"]["findings"] == 0
    assert d["counts"]["plants_caught"] == 0 and d["status_basis"] == "screen"


def test_no_report_is_recorded_as_none(tmp_path, prices, off_peak_clock):
    model = ScriptedModel(reply("I am done."), reply("Still done."), reply("Done."))
    _, records, _, _ = run(tmp_path, prices, off_peak_clock, model, make(qs4h.QS4hH2Real, tmp_path))
    d = data_of(records)
    assert records[0]["outcome"]["status"] == "fail" and "without a report" in records[0]["outcome"]["detail"]
    assert d["reported"] is False and d["counts"] is None and d["findings"] == []


# -- statuses on a synthetic world ------------------------------------------------------------------
@pytest.fixture(scope="module")
def world(tmp_path_factory):
    w = build_world(tmp_path_factory.mktemp("qs4h-suite-world"))
    w.expected = build_inputs(w)
    return w


def world_suite(world, item_id, tmp_path, boxes=None):
    cls = next(c for c in qs4h.SUITES if c.ITEM == item_id)
    return make(cls, tmp_path, items=json.loads(world.items_path.read_text(encoding="utf-8")),
                expected=world.expected, boxes=boxes)


def world_finding(world, plant_id, statement, edit=0, shift=0):
    e = world.expected["plant_spans"][plant_id][edit]
    return finding(e["file"], str(e["lines"][0] + shift), statement)


def test_a_planted_item_passes_only_when_every_plant_is_caught(world, tmp_path, prices, off_peak_clock):
    both = [world_finding(world, "P1-A", "high where the golden says normal"),
            world_finding(world, "P1-B", "the scan skips the call's name")]
    for findings, status, n in ((both, "pass", 2), (both[:1], "fail", 1), ([], "fail", 0)):
        d = tmp_path / status / str(n)
        _, records, _, _ = run(d, prices, off_peak_clock, ScriptedModel(turn(report_call("r", findings))),
                               world_suite(world, "h1-planted", d))
        assert records[0]["outcome"]["status"] == status
        assert data_of(records)["counts"]["plants_caught"] == n
        assert f"{n} of 2 plants caught" in records[0]["outcome"]["detail"]


def test_a_real_tip_passes_when_it_reported(world, tmp_path, prices, off_peak_clock):
    findings = [finding("qs/loop.py", "54", "a recorded finding at the real tip's line", cls="other")]
    _, records, _, _ = run(tmp_path, prices, off_peak_clock, ScriptedModel(turn(report_call("r", findings))),
                           world_suite(world, "h2-real", tmp_path))
    d = data_of(records)
    assert records[0]["outcome"]["status"] == "pass" and d["plants"] == []
    assert d["findings"][0]["matched"] == "P2-v1" and d["findings"][0]["matched_by"] == "lines"
    assert [r["id"] for r in d["recorded"]] == ["P2-v1"]          # P2-v2 is the copy's only


def test_a_stopped_run_is_never_judged(world, tmp_path, prices, off_peak_clock):
    shells = [turn(tool_call(f"c{k}", "shell", {"command": "ls"})) for k in range(10)]
    _, records, _, _ = run(tmp_path, prices, off_peak_clock, ScriptedModel(*shells),
                           world_suite(world, "h1-planted", tmp_path))
    d = data_of(records)
    assert records[0]["outcome"]["status"] == "stopped" and d["status_basis"] == "agent"
    assert d["counts"] is None and d["reported"] is False


def test_an_input_that_fails_in_run_item_makes_no_call(world, tmp_path, prices, off_peak_clock):
    suite = world_suite(world, "h1-real", tmp_path)

    def refuse(item_id):
        raise qs4.InputError("a planted test refusal")
    suite.inputs.prepare = refuse
    model = ScriptedModel(turn(report_call("r", [])))
    summary, records, _, _ = run(tmp_path, prices, off_peak_clock, model, suite)
    assert records[0]["outcome"]["status"] == "error" and records[0]["calls"] == 0 and model.bodies == []
    assert data_of(records)["status_basis"] == "input"


def test_no_model_text_reaches_the_published_record(world, tmp_path, prices, off_peak_clock):
    s = "SENTINEL-MODEL-TEXT"
    findings = [finding(s + "/qs/scan.py", "25", s + " the scan skips a name", cls="other"),
                world_finding(world, "P1-B", s + " the call's name is not scanned")]
    model = ScriptedModel(turn(tool_call("w", "write_file", {"path": "verifier-P1.md", "content": s}),
                               report_call("r", findings, text=s)))
    _, records, published, transcript = run(tmp_path, prices, off_peak_clock, model,
                                            world_suite(world, "h1-planted", tmp_path))
    assert s not in published and s in transcript
    assert data_of(records)["findings"][0]["file"] == "qs/scan.py"      # the copy's file the path ends with


def test_a_located_finding_that_is_not_stated_goes_on_to_the_recorded_findings(tmp_path, prices, off_peak_clock):
    """On the committed data: a finding at R09 about its keys (P3-v10) sits inside plant
    P3-A's span. Not stated, it is matched to the recorded finding, not hidden by the plant."""
    f = finding("qs/suites/qs6_items.json", "75-80", "R09 and R10 have a key at every cut, though reach items",
                cls="known limit")
    _, records, _, _ = run(tmp_path, prices, off_peak_clock, ScriptedModel(turn(report_call("r", [f]))),
                           make(qs4h.QS4hH3Planted, tmp_path))
    d = data_of(records)["findings"][0]
    assert d["located"] == ["P3-A"] and d["stated"] == [] and d["matched"] == "P3-v10"


def test_a_deletion_is_located_within_its_widened_tolerance_and_no_further(tmp_path, prices, off_peak_clock):
    join = qs4h.EXPECTED["plant_spans"]["P2-A"][0]["lines"]
    tol = qs4h.ITEMS["settings"]["deletion_tolerance"]
    for line, located in ((join[0] - tol, True), (join[0] - tol - 1, False), (join[1] + tol, True)):
        d = tmp_path / str(line)
        f = finding("qs/agent/loop.py", str(line), "the streak is never reset")
        _, records, _, _ = run(d, prices, off_peak_clock, ScriptedModel(turn(report_call("r", [f]))),
                               make(qs4h.QS4hH2Planted, d))
        assert ("P2-A" in data_of(records)["findings"][0]["located"]) is located


def test_each_edit_of_a_two_edit_plant_locates_it(tmp_path, prices, off_peak_clock):
    for k, e in enumerate(qs4h.EXPECTED["plant_spans"]["P1-A"]):
        d = tmp_path / str(k)
        f = finding(e["file"], str(e["lines"][0]), "the golden says normal where the prompt says high")
        _, records, _, _ = run(d, prices, off_peak_clock, ScriptedModel(turn(report_call("r", [f]))),
                               make(qs4h.QS4hH1Planted, d))
        assert data_of(records)["plants"][0] == {"id": "P1-A", "edits": 2, "located": True, "stated": True,
                                                  "caught": True}


def test_a_file_given_in_a_clone_under_the_scratch_is_the_copys_file():
    repo = ["qs/agent/loop.py", "README.md"]
    sources = {"ds": {"prefixes": ["/work/ro/ds/"], "paths": ["thinking.txt"]}}
    assert qs4h.normalise_file("/work/scratch/r1-vP2/work/qs/agent/loop.py:294", "P2", repo, [], sources) == \
        ("qs/agent/loop.py", [294, 294])
    assert qs4h.normalise_file("/work/ro/r1-vP2-copy/qs/agent/loop.py", "P2", repo, [], sources)[0] == "qs/agent/loop.py"
    assert qs4h.normalise_file("<scratch>/r1-vP2/copy/README.md#L3", "P2", repo, [], sources) == ("README.md", [3, 3])
    assert qs4h.normalise_file("/work/ro/ds/thinking.txt", "P2", repo, [], sources)[0] == "ds/thinking.txt"
    assert qs4h.normalise_file("/work/ro/other/README.md", "P2", repo, [], sources)[0] == "<unlisted>"
    assert qs4h.normalise_file("commit message", "P2", repo, [], sources)[0] == "<commit message>"
    assert qs4h.normalise_file("git log", "P2", repo, [], sources)[0] == "<history>"


# -- the prompt --------------------------------------------------------------------------------------
def test_both_conditions_read_alike_and_hold_none_of_p4_as_sentence():
    for cls in PLANTED:
        planted = qs4h.item_spec(qs4h.ITEMS, cls.ITEM)
        real = qs4h.item_spec(qs4h.ITEMS, cls.ITEM.replace("planted", "real"))
        c = qs4h.own_commit(qs4h.ITEMS, qs4h.EXPECTED, planted)
        b = qs4h.own_commit(qs4h.ITEMS, qs4h.EXPECTED, real)
        mp = qs4h.render_messages(qs4h.PROMPT, qs4h.ITEMS, planted, c)
        mr = qs4h.render_messages(qs4h.PROMPT, qs4h.ITEMS, real, b)
        assert json.dumps(mp).replace(c[:7], "#######") == json.dumps(mr).replace(b[:7], "#######")
        text = json.dumps(mp)
        assert "may hold faults the lead planted" not in text and "holds two faults" not in text
        assert "$" not in text and "verifier-" + planted["parcel"] + ": channel test" in text
    h3 = json.dumps(qs4h.render_messages(qs4h.PROMPT, qs4h.ITEMS, qs4h.item_spec(qs4h.ITEMS, "h3-real"), "0" * 40))
    assert "QS6's answer key" in h3 and "<repos>/ds/" in h3 and "parcelround-worktrees/P0" in h3
    h4 = json.dumps(qs4h.render_messages(qs4h.PROMPT, qs4h.ITEMS, qs4h.item_spec(qs4h.ITEMS, "h4-real"), "0" * 40))
    assert "twelve files" in h4 and "809ed2f" in h4 and "<repos>/ds/" not in h4


def test_the_suites_are_eight_at_qs4s_caps_and_budgets():
    assert [c.ITEM for c in qs4h.SUITES] == [i["id"] for i in qs4h.ITEMS["items"]]
    assert len(qs4h.SUITES) == 8 and all(c.name == f"qs4h-{c.ITEM}" for c in qs4h.SUITES)
    assert qs4h.ITEMS["caps"] == qs4.ITEMS["caps"]
    assert qs4h.QS4H.caps == qs4.QS4.caps


# -- the reservation, worked by hand ---------------------------------------------------------------
def test_one_batch_reserves_what_the_hand_arithmetic_gives(tmp_path, prices, off_peak_clock):
    """At QS4's caps on deepseek-flash, off-peak: the run (40.9M prompt tokens and 0.5M
    output at 0.15 and 0.60 a million), the probe, the crossing margin (one call of 900K
    and 393,216 at peak less off-peak) and N times the dearest single call."""
    caps = qs4h.ITEMS["caps"]
    run_worst = (Decimal(caps["max_prompt_tokens"] + caps["max_call_prompt_tokens"]) * Decimal("0.15")
                 + Decimal(caps["max_output_tokens"]) * Decimal("0.60")) / Decimal(1_000_000)
    probe = (Decimal(identity.PROBE_MAX_PROMPT) * Decimal("0.15") + Decimal(identity.PROBE_MAX_OUTPUT)
             * Decimal("0.60")) / Decimal(1_000_000)
    call_out = min(caps["max_output_tokens"], deepseek.MAX_TOKENS)
    peak_call = (Decimal(caps["max_call_prompt_tokens"]) * Decimal("0.30") + Decimal(call_out) * Decimal("1.20")) / 10**6
    off_call = (Decimal(caps["max_call_prompt_tokens"]) * Decimal("0.15") + Decimal(call_out) * Decimal("0.60")) / 10**6
    for n, want in ((3, "9.0315264"), (28, "27.5780064")):
        assert run_worst + probe + (peak_call - off_call) + n * peak_call == Decimal(want)
        d = tmp_path / str(n)
        suite = make(qs4h.QS4hH1Planted, d)
        summary, _, _, _ = run(d, prices, off_peak_clock, ScriptedModel(turn(report_call("r", []))), suite,
                               max_unmetered=n)
        assert summary["reserved_usd"] == want


# -- the versions ------------------------------------------------------------------------------------
def test_qs4s_version_has_not_moved():
    assert qs4.VERSION == "1.ffc3d24774c0.bc875ea6a27a"


def test_qs4hs_version_names_its_code_and_qs4s():
    norm = lambda p: p.read_bytes().replace(b"\r\n", b"\n")  # noqa: E731
    code = hashlib.sha256(norm(ROOT / "qs/suites/qs4h.py") + b"\0" + norm(ROOT / "qs/suites/qs4.py")).hexdigest()
    data = hashlib.sha256(b"\0".join(norm(ROOT / p) for p in ("qs/suites/qs4h_items.json", "qs/suites/qs4h_prompt.md",
                                                             "qs/suites/qs4h_expected.json",
                                                             "sandbox/qs4h.Dockerfile"))).hexdigest()
    assert qs4h.VERSION == f"1.{data[:12]}.{code[:12]}"


# -- the judgements and the table ------------------------------------------------------------------
def test_the_judgements_form():
    assert qs4h.judgement_problems(qs4h.load_judgements()) == []
    good = {"record_id": "r", "plant": "P1-A", "finding": None, "verdict": "caught", "recorded": None, "by": "lead",
            "checked_by": "verifier", "note": "n"}
    assert qs4h.judgement_problems([good]) == []
    bad = [dict(good, plant="P9-Z"), dict(good, finding=0), dict(good, plant=None, finding=0, verdict="match",
                                                                   recorded="P1-v99"), dict(good, by="")]
    assert len(qs4h.judgement_problems(bad)) == 4


def test_the_table_draws_a_run(world, tmp_path, prices, off_peak_clock):
    both = [world_finding(world, "P1-A", "high where the golden says normal"),
            world_finding(world, "P1-B", "the scan skips the call's name")]
    _, records, _, _ = run(tmp_path, prices, off_peak_clock, ScriptedModel(turn(report_call("r", both))),
                           world_suite(world, "h1-planted", tmp_path))
    rid = records[0]["record_id"]
    t = qs4h.table(records, [{"record_id": rid, "plant": "P1-A", "verdict": "caught"},
                             {"record_id": rid, "plant": "P1-B", "verdict": "missed"}])
    assert t["rows"][rid]["plants_caught_screen"] == 2 and t["rows"][rid]["plants_caught_judged"] == 1
    assert t["planted_by_parcel"] == {"P1": {"runs": 1, "plants_caught_screen": 2}}
