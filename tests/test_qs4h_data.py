"""QS4h's committed data against itself, git and QS4: the items, the plants and their
markers, the recorded findings, the pinned values, the prompt's sections and the
deletion tolerance's derivation. Where the built inputs are present under local/qs4h,
each item is prepared, and each plant's markers are read against the lines of its own
span in the planted copy."""
import json
import re
import subprocess

import pytest

from qs.agent import Budgets
from qs.agent.sandbox import BACKSTOP_S, KILL_AFTER_S
from qs.suites import qs4, qs4h

ITEMS, EXPECTED = qs4h.ITEMS, qs4h.EXPECTED
HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")


def built() -> bool:
    return all((qs4h.LOCAL / f).is_file() for f in ("built.json", "cuts.json", "image.json"))


def blob(repo, rev: str) -> bytes | None:
    r = subprocess.run(["git", "-C", str(repo), "cat-file", "blob", rev], capture_output=True,
                       env={"GIT_OPTIONAL_LOCKS": "0", **__import__("os").environ})
    return r.stdout if r.returncode == 0 else None


# -- the items -------------------------------------------------------------------------------
def test_the_items_are_eight_over_four_parcels():
    assert [i["id"] for i in ITEMS["items"]] == [f"h{n}-{k}" for n in (1, 2, 3, 4) for k in ("planted", "real")]
    assert sorted(ITEMS["parcels"]) == ["P1", "P2", "P3", "P4"]
    for p, spec in ITEMS["parcels"].items():
        for k in ("copy", "tip", "base"):
            assert HEX40.fullmatch(spec[k])
        assert HEX64.fullmatch(spec["key_sha256"]) and spec["key"] == f"keys/key-{spec['copy'][:7]}.json"
        assert re.fullmatch(r"2026-10-06 \d\d:\d\d:\d\d", spec["stamp"])
        assert set(spec["inputs"]) <= {"ds", "parcelround", "sources"}


def test_the_plants_and_their_markers():
    ids = [pl["id"] for p in ITEMS["parcels"].values() for pl in p["plants"]]
    assert ids == ["P1-A", "P1-B", "P2-A", "P2-B", "P3-A", "P3-B", "P4-A", "P4-B"]
    for p in ITEMS["parcels"].values():
        for pl in p["plants"]:
            assert pl["markers"] and all(alt and all(isinstance(w, str) and w.strip() for w in alt)
                                         for alt in pl["markers"])


def test_the_recorded_findings():
    rec = [r for p in ITEMS["parcels"].values() for r in p["recorded"]]
    assert len(rec) == 40 and len({r["id"] for r in rec}) == 40
    in_view = {p: sum(r["in_view"] for r in spec["recorded"]) for p, spec in ITEMS["parcels"].items()}
    assert in_view == {"P1": 6, "P2": 4, "P3": 4, "P4": 5}
    for p, spec in ITEMS["parcels"].items():
        files = set(EXPECTED["repos"][f"h{p[1]}-planted"]["files"])
        for r in spec["recorded"]:
            assert r["id"].startswith(p + "-v") and r["class"] in qs4h.CLASSES and r["recorded"]
            for pl in r["places"]:
                assert pl["file"] in files or pl["file"].startswith("ledger/") or pl["file"] in (
                    qs4h.COMMIT_MESSAGE, qs4h.HISTORY)
                assert all(1 <= a <= b for a, b in pl["lines"])


# Each recorded finding's class, in-view mark and copy-only mark, generated from the table
# in P5.md's entry of 14:30:06 (its "when" column: view or after; "copy only" in its last).
# --- RECORDED (generated) ---
RECORDED = {
    'P1-v1': ('known limit', True, False),
    'P1-v2': ('known limit', True, False),
    'P1-v3': ('known limit', True, False),
    'P1-v4': ('known limit', True, False),
    'P1-v5': ('known limit', True, False),
    'P1-v6': ('restate', True, False),
    'P2-v1': ('wrong answer', True, False),
    'P2-v2': ('wrong answer', True, False),
    'P2-v3': ('wrong answer', False, False),
    'P2-v4': ('known limit', False, False),
    'P2-v5': ('known limit', False, False),
    'P2-v6': ('known limit', False, False),
    'P2-v7': ('known limit', False, False),
    'P2-v8': ('known limit', True, False),
    'P2-v9': ('known limit', True, False),
    'P2-v10': ('restate', False, True),
    'P2-v11': ('restate', False, False),
    'P2-v12': ('restate', False, False),
    'P2-v13': ('other', False, False),
    'P2-v14': ('other', False, False),
    'P2-v15': ('other', False, True),
    'P3-v1': ('restate', True, False),
    'P3-v2': ('other', True, False),
    'P3-v3': ('other', True, False),
    'P3-v4': ('other', True, False),
    'P3-v5': ('restate', False, False),
    'P3-v6': ('restate', False, False),
    'P3-v7': ('known limit', False, False),
    'P3-v8': ('known limit', False, False),
    'P3-v9': ('known limit', False, False),
    'P3-v10': ('known limit', False, False),
    'P3-v11': ('known limit', False, False),
    'P4-v1': ('restate', True, False),
    'P4-v2': ('known limit', True, False),
    'P4-v3': ('other', True, False),
    'P4-v4': ('other', True, False),
    'P4-v5': ('known limit', True, False),
    'P4-v6': ('known limit', False, False),
    'P4-v7': ('other', False, False),
    'P4-v8': ('other', False, False),
}
# --- end RECORDED ---


def test_each_recorded_finding_has_the_ledgers_class_and_marks():
    """Each parcel's count of in-view findings held while two of P4's marks were swapped
    (verifier-P5's F2, a plant), so each mark is pinned on its own."""
    marks = {r["id"]: (r["class"], r["in_view"], r["copy_only"])
             for p in ITEMS["parcels"].values() for r in p["recorded"]}
    assert marks == RECORDED


def test_qs4hs_caps_and_sources_are_qs4s():
    assert ITEMS["caps"] == qs4.ITEMS["caps"] and ITEMS["sources"] == qs4.ITEMS["sources"]
    assert ITEMS["parcelround"]["commit"] == qs4.ITEMS["archive"]["parcelround"]


def test_qs4hs_budgets_are_qs4s_but_the_call_timeout_and_the_run_which_fits_two_hours():
    """The lead's rule (lead.md 14:32:37, answer 3), applied at lead.md 19:54:31: a model's
    --control at h4 took 208.1 s in the sandbox, so a tool call's timeout is 1.5 times
    that, rounded up, 320 s; and a run, one call more with P2's kill grace, and 15
    minutes fit 2 hours."""
    b, theirs = ITEMS["budgets"], qs4.ITEMS["budgets"]
    Budgets(**b)
    moved = {"call_timeout_seconds", "max_run_seconds"}
    assert {k: v for k, v in b.items() if k not in moved} == {k: v for k, v in theirs.items() if k not in moved}
    assert b["call_timeout_seconds"] == 320 >= 1.5 * 208.1
    assert b["max_run_seconds"] < theirs["max_run_seconds"]
    assert b["max_run_seconds"] + b["call_timeout_seconds"] + KILL_AFTER_S + BACKSTOP_S + 900 <= 7200


def test_the_briefs_rebuild_names_lines_and_hashes_only():
    rb = ITEMS["briefs_rebuild"]
    assert rb["parcels"] == ["P1", "P2"]
    assert [e["file"] for e in rb["edits"]] == ["briefs/_common.md", "briefs/_verifier.md"]
    for e in rb["edits"]:
        assert HEX64.fullmatch(e["source_sha256"]) and HEX64.fullmatch(e["removed_sha256"])
        assert e["lines"][0] <= e["lines"][1] and e["absent"] == ["15:35:17", "16:39:34", "lowprio"]


def test_the_prompt_has_every_section_the_items_name():
    needed = set(qs4h.PROMPT_SECTIONS) | {"line-" + n for p in ITEMS["parcels"].values() for n in p["adaptation"]}
    assert needed <= set(qs4h.PROMPT)
    # the sentence plant P4-A changes is in none of them (A1.10's self-reference)
    assert not any("may hold faults" in v or "holds two faults" in v for v in qs4h.PROMPT.values())


# -- the pinned values ------------------------------------------------------------------------
def test_the_expected_values():
    b = EXPECTED["builds"]
    assert b["P2"] == ITEMS["parcels"]["P2"]["tip"] and b["P3"] == ITEMS["parcels"]["P3"]["tip"]
    assert b["P1"] != ITEMS["parcels"]["P1"]["tip"] and b["P4"] != ITEMS["parcels"]["P4"]["tip"]
    for i in ITEMS["items"]:
        assert EXPECTED["repos"][i["id"]]["commit"] == qs4h.own_commit(ITEMS, EXPECTED, i)
        assert i["id"] in EXPECTED["cuts"]
    s = EXPECTED["plant_spans"]
    assert len(s["P1-A"]) == 2 and [e["kind"] for e in s["P2-A"] + s["P2-B"]] == ["deletion", "deletion"]
    assert all(e["kind"] == "replacement" for k in ("P1-A", "P1-B", "P3-A", "P3-B", "P4-A", "P4-B") for e in s[k])
    assert EXPECTED["sources"]["digest"] == qs4.EXPECTED["sources"]["digest"]
    assert EXPECTED["parcelround"]["commit"] == ITEMS["parcelround"]["commit"]
    assert len(EXPECTED["ds"]["files"]) == 32
    assert sorted(EXPECTED["briefs_rebuilt"]) == ["briefs/_common.md", "briefs/_verifier.md"]


def test_the_deletion_tolerance_reaches_the_blocks_the_deletions_end():
    """settings.deletion_tolerance is the distance from P2-A's join up to the head of the
    malformed-call block it ends; it also reaches the tool loop's head above P2-B's
    join. Measured on the real tip's loop.py, by the lines the plants removed."""
    tip = ITEMS["parcels"]["P2"]["tip"]
    data = blob(qs4h.ROOT, f"{tip}:qs/agent/loop.py")
    if data is None:
        pytest.skip("the real tip's objects are not in this repository")
    lines = data.decode("utf-8").split("\n")
    head_a = next(n for n, x in enumerate(lines, 1) if x.strip() == "if err is not None:")
    head_b = next(n for n, x in enumerate(lines, 1) if x.strip() == "for i, call in enumerate(turn.tool_calls):")
    a, b = EXPECTED["plant_spans"]["P2-A"][0], EXPECTED["plant_spans"]["P2-B"][0]
    tol = ITEMS["settings"]["deletion_tolerance"]
    assert (a["tip_lines"][0] - 1) - head_a == tol
    assert (b["tip_lines"][0] - 1) - head_b == 7 <= tol


# -- the built inputs, where present ---------------------------------------------------------------
needs_inputs = pytest.mark.skipif(not built(), reason="QS4h's inputs are not built under local/qs4h")


@needs_inputs
def test_every_item_prepares_on_the_built_inputs():
    """Skips while an item has no gate record, as after tools/qs4h_rebuild.py --no-gate
    (verifier-P5's L1); a record that does not hold still fails here."""
    try:
        qs4h.current_image_id()
    except qs4.InputError as e:
        pytest.skip(f"the sandbox image: {e}")
    b = json.loads((qs4h.LOCAL / "built.json").read_text(encoding="utf-8"))
    missing = [i["id"] for i in ITEMS["items"] if "gate" not in b["items"].get(i["id"], {})]
    if missing:
        pytest.skip(f"no gate record for {', '.join(missing)}: tools/qs4h_rebuild.py --gate-only writes them")
    inputs = qs4h.LocalInputs()
    for i in ITEMS["items"]:
        prep = inputs.prepare(i["id"])
        assert prep.mounts[0].name == qs4h.copy_mount(i["parcel"]) and prep.facts["gate_held"]


@needs_inputs
def test_no_marker_set_is_held_by_its_own_spans_lines():
    """Each plant's markers name its change, not its neighbours' words: none of its sets
    is satisfied by the planted lines within its span's tolerance, read from the planted
    copy. P3-A is the stated exception (limit 9): its change is its two names, and the
    evidence line beside it holds one."""
    b = json.loads((qs4h.LOCAL / "built.json").read_text(encoding="utf-8"))
    for p, spec in ITEMS["parcels"].items():
        repo = qs4h.LOCAL / b["items"][f"h{p[1]}-planted"]["repo"]
        for pl in spec["plants"]:
            for e in EXPECTED["plant_spans"][pl["id"]]:
                lines = blob(repo, f"HEAD:{e['file']}").decode("utf-8").split("\n")
                tol = qs4h._tolerance(ITEMS["settings"], e)
                text = "\n".join(lines[max(e["lines"][0] - tol, 1) - 1:e["lines"][1] + tol])
                assert qs4.markers_hit(text, pl["markers"]) is (pl["id"] == "P3-A"), pl["id"]


@needs_inputs
def test_the_ledger_copy_holds_the_sealed_keys():
    copies = sorted((qs4h.LOCAL / "ledger").glob("*/manifest.json"))
    assert copies
    members, _ = qs4h.load_snapshot(copies[-1].parent)
    for spec in ITEMS["parcels"].values():
        assert qs4.sha256(members[qs4h.LEDGER_ROOT + spec["key"]][0]) == spec["key_sha256"]


def runs_of_six(text: str) -> set:
    w = re.findall(r"[a-z0-9_.:'-]+", text.lower())
    return {tuple(w[i:i + 6]) for i in range(len(w) - 5)}


@needs_inputs
def test_each_plants_description_is_qs4hs_own_words():
    """verifier-P5's R1: the items say their descriptions are QS4h's own words. No plant's
    `about` shares a run of six words with any plant's shape in its parcel's key, read
    from the ledger copy, since QS4h's data holds no key text."""
    copies = sorted((qs4h.LOCAL / "ledger").glob("*/manifest.json"))
    assert copies
    members, _ = qs4h.load_snapshot(copies[-1].parent)
    for spec in ITEMS["parcels"].values():
        key = json.loads(members[qs4h.LEDGER_ROOT + spec["key"]][0])
        shapes = set().union(*(runs_of_six(p["shape"]) for p in key["plants"]))
        for pl in spec["plants"]:
            assert not runs_of_six(pl["about"]) & shapes, pl["id"]
