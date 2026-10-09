"""The round's table: which batches enter, what each suite's pooling gives, and
what the cost columns read. Records here are synthetic, written in tmp_path."""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SELECT = ROOT / "Rounds" / "HonestHarness-R1" / "table-batches.json"


def load_table():
    spec = importlib.util.spec_from_file_location("round_table", ROOT / "tools" / "table.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


T = load_table()


def run(batch, suite, thinking, status, data, k, usage=(900, 100, 50)):
    return {"record_id": f"{batch}.i{k}.r0", "batch": batch, "suite": suite, "suite_version": "1.a.b",
            "thinking": thinking, "calls": 1, "cost_usd": "0.001",
            "usage": {"cache_hit": usage[0], "cache_miss": usage[1], "output": usage[2], "reasoning": 0},
            "outcome": {"status": status, "detail": "", "data": data}}


def qs1_data(tp=0, fp=0, fn=0, tn=0, calls=0, valid=0, turns=0, emitted=0):
    return {"metric_inputs": {"trigger": {"tp": tp, "fp": fp, "fn": fn, "tn": tn},
                              "schema": {"calls": calls, "valid": valid},
                              "reasoning": {"turns": turns, "emitted": emitted}}}


def qs6_data(cls, cut="c016k", kind="value", tokens=30_000):
    return {"cut": cut, "set": "length", "class": cls, "key_kind": kind, "prompt_tokens": tokens}


def summary(batch, suite, runs, computed="0.01", billed="0.00", recon="ok", stopped=None, unmetered=0):
    return {"kind": "batch", "batch": batch, "suite": suite, "suite_version": "1.a.b", "runs": runs,
            "live": True, "stopped_for": stopped, "computed_usd": computed, "billed_usd": billed,
            "reconciliation": recon, "unmetered_attempts": unmetered}


def world(tmp_path):
    """Two QS1 batches, a full QS6 batch, a stopped QS6 batch, a probe and a
    recheck."""
    recs = tmp_path / "records"
    (recs / "runs").mkdir(parents=True)
    qs1 = [run("q1off", "qs1", False, "pass", qs1_data(tp=2, tn=1, calls=2, valid=2), 0),
           run("q1off", "qs1", False, "fail", qs1_data(fn=1, calls=1, valid=0), 1),
           run("q1on", "qs1", True, "pass", qs1_data(tp=1, calls=1, valid=1, turns=2, emitted=1), 0)]
    qs6 = [run("q6full", "qs6-c016k", True, "pass", qs6_data("exact"), 0),
           run("q6full", "qs6-c016k", True, "fail", qs6_data("overclaim", kind="not_in_input"), 1),
           run("q6stop", "qs6-c016k", True, "fail", qs6_data("wrong"), 0)]
    for name, rs in (("qs1", qs1), ("qs6-c016k", qs6)):
        (recs / "runs" / f"{name}.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rs), encoding="utf-8")
    lines = [summary("probe-1", "probe", 0, computed="0.0000045"),
             summary("q1off", "qs1", 2), summary("q1on", "qs1", 1),
             summary("q6full", "qs6-c016k", 2, computed="0.04", recon="mismatch"),
             {"kind": "recheck", "batch": "q6full", "billed_usd": "0.02", "reconciliation": "ok"},
             summary("q6stop", "qs6-c016k", 1, stopped="a reply did not arrive whole", unmetered=3)]
    (recs / "batches.jsonl").write_text("".join(json.dumps(x) + "\n" for x in lines), encoding="utf-8")
    sel = {"include": {"q1off": "complete", "q1on": "complete", "q6full": "complete"},
           "exclude": {"q6stop": "stopped at its third dropped attempt"}}
    return recs, sel


def test_the_included_batches_pool_by_their_suites_own_functions(tmp_path):
    recs, sel = world(tmp_path)
    t = T.compute(recs, sel)
    off, on = t["qs1"]
    assert (off["thinking"], off["runs"], on["thinking"], on["runs"]) == (False, 2, True, 1)
    assert off["trigger"]["tp"] == 2 and off["trigger"]["fn"] == 1 and off["schema"]["valid"] == 2
    assert off["statuses"] == {"pass": 1, "fail": 1} and on["reasoning"]["share"] == 0.5
    (row,) = t["qs6"]
    # The stopped batch's "wrong" is not pooled with the full batch.
    assert row["value"]["wrong"] == 0 and row["value"]["exact"] == 1 and row["accuracy"] == 1.0
    assert row["not_in_input"]["overclaim"] == 1 and row["overclaim_rate"] == 1.0
    assert t["qs4"] is None


def test_every_live_batch_is_listed_with_its_cost_and_the_last_bill(tmp_path):
    recs, sel = world(tmp_path)
    rows = {b["batch"]: b for b in T.compute(recs, sel)["batches"]}
    assert set(rows) == {"probe-1", "q1off", "q1on", "q6full", "q6stop"}
    assert (rows["q6full"]["billed_usd"], rows["q6full"]["reconciliation"]) == ("0.02", "ok")
    assert rows["q6stop"]["entered"] is False and rows["q6stop"]["unmetered_attempts"] == 3
    assert rows["q6stop"]["why"] == "stopped at its third dropped attempt"
    assert rows["probe-1"]["why"] == "no runs, so not named"
    assert rows["q1off"]["cache_hit"] == 1800 and rows["q1off"]["output"] == 100
    # 0.0000045 + 0.01 + 0.01 + 0.04 + 0.01, every live batch, included or not
    assert T.compute(recs, sel)["computed_usd_all_live_batches"] == "0.0700045"


def test_a_live_batch_the_selection_does_not_name_is_refused(tmp_path):
    recs, sel = world(tmp_path)
    del sel["exclude"]["q6stop"]
    with pytest.raises(T.SelectionError, match="q6stop"):
        T.compute(recs, sel)


@pytest.mark.parametrize("change", ["twice", "absent"])
def test_a_batch_named_twice_or_named_and_absent_is_refused(tmp_path, change):
    recs, sel = world(tmp_path)
    if change == "twice":
        sel["exclude"]["q1on"] = "also"
    else:
        sel["include"]["q9"] = "no such batch"
    with pytest.raises(T.SelectionError):
        T.compute(recs, sel)


def test_an_included_batch_missing_run_records_is_refused(tmp_path):
    recs, sel = world(tmp_path)
    p = recs / "runs" / "qs1.jsonl"
    p.write_text("".join(p.read_text(encoding="utf-8").splitlines(keepends=True)[1:]), encoding="utf-8")
    with pytest.raises(T.SelectionError, match="q1off: 1 run records"):
        T.compute(recs, sel)


def test_the_markdown_carries_each_section_and_its_figures(tmp_path):
    recs, sel = world(tmp_path)
    md = T.markdown(T.compute(recs, sel))
    assert "## QS1" in md and "## QS6" in md and "## Batches" in md and "## QS4" not in md
    assert "| off | 1.a.b | 2 | fail 1, pass 1 | 0.800 (2/0/1/1) |" in md
    assert "| c016k | length | on | 1/1 (1.000) | 1/1 (1.000) | none | 30000 |" in md
    assert "| q6stop | on | no | 1 |" in md


def test_a_qs4_run_enters_through_qs4s_own_table(tmp_path):
    recs, sel = world(tmp_path)
    q = {"item": "p2-planted", "parcel": "P2", "kind": "planted", "wave": 1, "verdict": "NOT READY",
         "plants": [{"id": "P2-p1"}, {"id": "P2-p2"}],
         "counts": {"plants_caught": 1, "findings": 3, "unmatched": 1, "r6_in_view": 3, "r6_in_view_located": 2}}
    r = run("q4", "qs4-p2-planted", True, "fail", {"qs4": q}, 0)
    (recs / "runs" / "qs4-p2-planted.jsonl").write_text(json.dumps(r) + "\n", encoding="utf-8")
    with (recs / "batches.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(summary("q4", "qs4-p2-planted", 1, computed="0.5")) + "\n")
    sel["include"]["q4"] = "QS4 p2-planted, complete"
    t = T.compute(recs, sel)
    row = t["qs4"]["rows"]["q4.i0.r0"]
    assert (row["item"], row["status"], row["plants_caught_screen"], row["plants_caught_judged"]) == \
        ("p2-planted", "fail", 1, None)
    assert t["qs4"]["planted_by_wave"]["wave1"] == {"runs": 1, "plants_caught_screen": 1}
    assert "| q4.i0.r0 | p2-planted | fail | 1 | None | 3 | 2/3 | 1000 | 50 | 0.001 |" in T.markdown(t)


def test_a_qs4h_run_enters_through_qs4hs_own_table(tmp_path):
    recs, sel = world(tmp_path)
    q = {"item": "h1-planted", "parcel": "P1", "kind": "planted", "verdict": "NOT READY",
         "plants": [{"id": "P1-A"}, {"id": "P1-B"}],
         "counts": {"plants_caught": 2, "findings": 4, "unmatched": 1, "recorded_in_view": 5,
                    "recorded_in_view_located": 2}}
    r = run("q4h", "qs4h-h1-planted", True, "pass", {"qs4h": q}, 0)
    (recs / "runs" / "qs4h-h1-planted.jsonl").write_text(json.dumps(r) + "\n", encoding="utf-8")
    with (recs / "batches.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(summary("q4h", "qs4h-h1-planted", 1, computed="0.4")) + "\n")
    sel["include"]["q4h"] = "QS4h h1-planted, complete"
    t = T.compute(recs, sel)
    assert t["qs4"] is None
    row = t["qs4h"]["rows"]["q4h.i0.r0"]
    assert (row["item"], row["status"], row["verdict"], row["plants_caught_screen"],
            row["plants_caught_judged"]) == ("h1-planted", "pass", "NOT READY", 2, None)
    assert t["qs4h"]["planted_by_parcel"]["P1"] == {"runs": 1, "plants_caught_screen": 2}
    md = T.markdown(t)
    assert "## QS4h" in md and "## QS4\n" not in md
    assert "| q4h.i0.r0 | h1-planted | pass | NOT READY | 2 | None | 4 | 2/5 | 1000 | 50 | 0.001 |" in md


def test_main_refuses_with_its_exit_code(tmp_path, capsys):
    recs, sel = world(tmp_path)
    del sel["include"]["q1on"]
    p = tmp_path / "sel.json"
    p.write_text(json.dumps(sel), encoding="utf-8")
    assert T.main(["--select", str(p), "--records", str(recs)]) == 3
    assert "REFUSED" in capsys.readouterr().err


@pytest.mark.skipif(not SELECT.exists(), reason="the round's selection file is written once its runs end")
def test_the_committed_selection_draws_the_committed_records():
    sel = json.loads(SELECT.read_text(encoding="utf-8"))
    T.compute(ROOT / "records", sel)
