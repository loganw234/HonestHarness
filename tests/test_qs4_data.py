"""QS4's committed data: its shape and self-consistency, everywhere. Where the
round's inputs are built under local/qs4 (in the checkout the lead runs from,
after tools/qs4_cut.py and tools/qs4_rebuild.py), the inputs are checked
against it as well; without them those tests skip, saying so."""
import re

import pytest

from qs.suite import ID_PATTERN
from qs.suites import qs4

ITEMS, EXP = qs4.ITEMS, qs4.EXPECTED
PARCELS = ITEMS["parcels"]
HEX40, HEX64 = re.compile(r"[0-9a-f]{40}"), re.compile(r"[0-9a-f]{64}")


def test_the_items_are_round_6s_five_parcels_twice():
    ids = [i["id"] for i in ITEMS["items"]]
    assert len(ids) == 10 == len(set(ids)) and all(ID_PATTERN.fullmatch(i) for i in ids)
    assert {(i["parcel"], i["kind"]) for i in ITEMS["items"]} == {
        (p, k) for p in ("P1", "P2", "P3", "P4", "P5") for k in ("planted", "real")}
    for p, v in PARCELS.items():
        assert all(HEX40.fullmatch(v[k]) for k in ("copy", "tip", "base"))
        assert v["key"] == f"keys/key-{v['copy'][:7]}.json" and v["wave"] == (2 if p == "P5" else 1)
        assert re.fullmatch(r"2026-10-0[23] \d{2}:\d{2}:\d{2}", v["dispatch"])


def test_each_parcel_has_two_plants_with_marker_sets():
    for p, v in PARCELS.items():
        assert [pl["id"] for pl in v["plants"]] == [f"{p}-p1", f"{p}-p2"]
        assert [pl["index"] for pl in v["plants"]] == [0, 1]
        for pl in v["plants"]:
            assert pl["shape"] in ("figure", "rule") and pl["markers"]
            assert all(alt and all(isinstance(ph, str) and ph.strip() for ph in alt) for alt in pl["markers"])


def test_round_6s_recorded_findings_are_well_formed():
    for p, v in PARCELS.items():
        files = set(EXP["repos"][f"{p.lower()}-planted"]["files"])
        cut = set(EXP["cuts"][f"{p.lower()}-planted"]["files"])
        for r in v["r6_findings"]:
            assert r["class"] in qs4.CLASSES and isinstance(r["in_view"], bool) and isinstance(r["copy_only"], bool)
            assert r["file"] in files or r["file"] == qs4.COMMIT_MESSAGE or (
                r["file"].startswith("ledger/") and r["file"][7:] in cut)
            assert all(len(s) == 2 and 1 <= s[0] <= s[1] for s in r["lines"])
            assert re.match(r"verifier-P\d\.md \d{2}:\d{2}:\d{2}", r["recorded"])


def test_the_expected_inputs_cover_every_item_plant_and_finding():
    a = EXP["archive"]
    assert HEX64.fullmatch(a["sha256"]) and HEX40.fullmatch(a["blob"]) and a["bytes"] > 0
    assert sum(1 for m in a["members"] if m.startswith(ITEMS["archive"]["root"] + "keys/")) == 5
    for item in ITEMS["items"]:
        c, r = EXP["cuts"][item["id"]], EXP["repos"][item["id"]]
        assert HEX64.fullmatch(c["digest"]) and not any(f.startswith("keys/") for f in c["files"])
        assert f"{item['parcel']}.md" not in c["files"] and "lead.md" in c["files"]
        assert r["commit"] == qs4.item_commit(ITEMS, item) and HEX40.fullmatch(r["tree"]) and r["objects"] > 0
        assert "CASE-STUDY-6.md" not in r["files"] and "archive/round6-ledger.zip" not in r["files"]
    for p, v in PARCELS.items():
        for pl in v["plants"]:
            s = EXP["plant_spans"][pl["id"]]
            assert s["file"] in EXP["repos"][f"{p.lower()}-planted"]["files"] and 1 <= s["lines"][0] <= s["lines"][1]
        for r in v["r6_findings"]:
            assert len(EXP["r6_tip_lines"][r["id"]]) == len(r["lines"])
    assert HEX64.fullmatch(EXP["plan"]["sha256"]) and HEX64.fullmatch(EXP["sources"]["digest"])
    assert sorted(EXP["sources"]["files"]) == sorted(f"{s['name']}/{p}" for s in ITEMS["sources"] for p in s["paths"])


def test_the_caps_fit_deepseeks_context_with_a_turns_output():
    caps, b = ITEMS["caps"], ITEMS["budgets"]
    assert caps == {"max_prompt_tokens": 40_000_000, "max_output_tokens": 500_000, "max_call_prompt_tokens": 900_000}
    assert caps["max_call_prompt_tokens"] + b["max_tokens_per_turn"] <= 1_048_576   # ds/list_models.txt:36, :62
    assert b["max_tokens_per_turn"] == 65_536 and ITEMS["settings"]["stream"] is True


def test_the_judgements_file_is_well_formed_and_its_check_can_fail():
    assert qs4.judgement_problems(qs4.load_judgements()) == []
    good = [{"record_id": "b.p2-planted.r0", "plant": "P2-p1", "finding": None, "verdict": "caught", "r6": None,
             "by": "lead", "checked_by": "verifier-X", "note": "states 38 against 28"},
            {"record_id": "b.p2-real.r0", "plant": None, "finding": 0, "verdict": "match", "r6": "P2-r1",
             "by": "lead", "checked_by": "verifier-X", "note": "the same restate"}]
    assert qs4.judgement_problems(good) == []
    bad = [dict(good[0], verdict="match"), dict(good[1], r6=None), dict(good[0], finding=0),
           dict(good[0], plant="P9-p1"), dict(good[0], checked_by=""), {k: v for k, v in good[0].items() if k != "note"}]
    assert len(qs4.judgement_problems(bad)) == len(bad)


# -- with the round's inputs built under local/qs4 ------------------------------------
LOCAL_OK = (qs4.LOCAL / "cuts.json").is_file() and (qs4.LOCAL / "built.json").is_file()
needs_local = pytest.mark.skipif(not LOCAL_OK, reason="no inputs under local/qs4: build them with "
                                 "tools/qs4_cut.py and tools/qs4_rebuild.py")


def local_keys():
    members = qs4.archive_members((qs4.LOCAL / "archive" / "round6-ledger.zip").read_bytes(), EXP["archive"])
    return members, qs4.keys_of(members, ITEMS)


@needs_local
def test_each_cut_rebuilds_from_the_archive_as_pinned():
    members, keys = local_keys()
    for item in ITEMS["items"]:
        assert qs4.tree_digest(qs4.cut_for(members, ITEMS, item, keys)) == EXP["cuts"][item["id"]]["digest"]


@needs_local
def test_no_marker_set_passes_on_a_plants_own_text_alone():
    _, keys = local_keys()
    for p, v in PARCELS.items():
        for pl in v["plants"]:
            new = keys[p]["plants"][pl["index"]]["new"]
            assert not qs4.markers_hit(new, pl["markers"]), pl["id"]


@needs_local
def test_each_plants_span_holds_its_text_in_the_replay_repository():
    _, keys = local_keys()
    for p, v in PARCELS.items():
        repo = qs4.LOCAL / "repos" / v["copy"][:12]
        for pl in v["plants"]:
            s, kp = EXP["plant_spans"][pl["id"]], keys[p]["plants"][pl["index"]]
            text = qs4.git(repo, "cat-file", "blob", f"HEAD:{s['file']}").decode("utf-8").split("\n")
            assert kp["new"] in "\n".join(text[s["lines"][0] - 1:s["lines"][1]])


@needs_local
def test_each_items_local_inputs_are_as_pinned():
    from qs.agent import docker_status
    ok, why = docker_status()
    if not ok:
        pytest.skip(why)
    for item in ITEMS["items"]:
        assert qs4.LocalInputs().prepare(item["id"]).facts["gate_held"] is True
