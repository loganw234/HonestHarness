"""QS6's committed data, checked everywhere without the local copy; then, where
the local copy is present (local/qs6/, gitignored), against round 6's ledger
itself and the key. Those tests skip, with the reason, in a checkout without
it: the live checkout has it, and the gate runs them there."""
import importlib.util
import json
import re
import shutil
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from qs.suites import qs6  # noqa: E402

DATA = qs6.load_data()
HAVE_ARCHIVE = qs6.ARCHIVE_PATH.is_file()
HAVE_KEY = HAVE_ARCHIVE and qs6.KEY_PATH.is_file()
needs_archive = pytest.mark.skipif(
    not HAVE_ARCHIVE, reason="no local copy at local/qs6/round6-ledger.zip; put it in place "
                             "with tools/qs6_extract.py --parcelround <a ParcelRound checkout>")
needs_key = pytest.mark.skipif(
    not HAVE_KEY, reason="no key at local/qs6/qs6_key.json: it stays out of the repository "
                         "until the runs are scored")
MINE = ["qs/suites/qs6.py", "qs/suites/qs6_source.json", "qs/suites/qs6_cuts.json",
        "qs/suites/qs6_items.json", "tools/qs6_extract.py", "tools/qs6_key.py",
        *sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "tests").glob("test_qs6*.py"))]


def _tool(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# -- everywhere ---------------------------------------------------------------------------------
def test_the_committed_data_holds_together():
    qs6.check_data(DATA)


def test_twenty_two_items_twelve_in_the_length_set_and_ten_in_the_reach_set():
    items = DATA["items"]["items"]
    assert [i["id"] for i in items] == [f"L{n:02d}" for n in range(1, 13)] + [f"R{n:02d}" for n in range(1, 11)]
    assert Counter(i["set"] for i in items) == {"length": 12, "reach": 10}
    assert Counter(i["type"] for i in items) == {"count": 9, "sha": 4, "time": 3, "figure": 3, "file": 2, "hex": 1}
    assert all(i["set"] == ("length" if i["id"].startswith("L") else "reach") for i in items)


def test_the_source_is_round_6s_archive_at_f42242e_and_keys_are_named_only():
    s = DATA["source"]
    assert (s["commit"], s["path"], s["bytes"]) == (
        "f42242ecc1707a3d36c52e4b2a3b580ee2783e5b", "archive/round6-ledger.zip", 203064)
    assert s["git_blob"] == "c25bbaa216138c4eeaeb2a7de5d28783cb82d2ca"
    assert len(s["members"]) == 22 and len(s["excluded"]) == 5
    assert all(e.startswith("keys/") for e in s["excluded"])
    assert not any(m["name"].startswith("keys/") for m in s["members"])


def test_the_kept_times_are_read_in_the_zone_of_the_stamps_on_the_measured_evidence():
    s = DATA["source"]
    assert s["kept_time_zone"] == "-07:00"
    stamped = [m for m in s["members"] if m["stamped_entries"]]
    assert len(stamped) == 13 and sum(m["stamped_entries"] for m in stamped) == 113
    # A DOS time keeps even seconds: each stamped file's kept time is its last
    # stamp, or one second before it when that stamp's second is odd.
    for m in stamped:
        last = datetime.fromisoformat(m["last_stamp"])
        assert m["kept_minus_last_stamp_s"] == (-1 if last.second % 2 else 0), m["name"]


def test_the_cuts_are_the_ones_the_lead_accepted_at_lead_md_15_25_54():
    cuts = DATA["cuts"]["cuts"]
    assert [c["time"] for c in cuts] == [
        "2026-10-02T21:11:40-07:00", "2026-10-02T21:54:16-07:00", "2026-10-02T22:09:39-07:00",
        "2026-10-03T00:19:49-07:00", "2026-10-03T01:18:19-07:00"]
    for c, target in zip(cuts, (16_000, 32_000, 64_000, 128_000, None)):
        assert c["target_bytes_over_4"] == target
        if target:
            assert c["bytes_over_4"] <= target
        assert c["caps"] == {"max_prompt_tokens": 1, "max_output_tokens": 32_000,
                             "max_call_prompt_tokens": qs6.cap_for(c["p0_largest_request"])}
        assert c["caps"]["max_call_prompt_tokens"] >= c["p0_largest_request"] * 1.02
    assert cuts[-1]["units"] == DATA["cuts"]["units_in_ledger"] == 122


def test_each_cut_class_is_named_for_its_cut_and_takes_its_caps():
    for spec in DATA["cuts"]["cuts"]:
        cls = qs6.CUT_CLASSES[spec["name"]]
        assert cls.cut == spec["name"] and cls.name == f"qs6-{spec['name']}"
        assert cls.caps == qs6.caps_of(spec)
    assert [c.__name__ for c in qs6.CUT_CLASSES.values()] == [
        "QS6C016K", "QS6C032K", "QS6C064K", "QS6C128K", "QS6Whole"]


def test_the_version_names_the_data_files_and_the_code(tmp_path):
    paths = [qs6.SOURCE_PATH, qs6.CUTS_PATH, qs6.ITEMS_PATH]
    assert qs6.version_of(paths, Path(qs6.__file__)) == qs6.VERSION
    copies = []
    for p in paths:
        shutil.copy(p, tmp_path / p.name)
        copies.append(tmp_path / p.name)
    copies[2].write_bytes(copies[2].read_bytes().replace(b"L01", b"L1x", 1))
    assert qs6.version_of(copies, Path(qs6.__file__)) != qs6.VERSION
    assert re.fullmatch(r"1\.[0-9a-f]{12}\.[0-9a-f]{12}", qs6.VERSION)


def test_no_committed_file_of_qs6_holds_an_absolute_path_or_an_address():
    check = _tool("check")          # the gate's own patterns, read-only
    for rel in MINE:
        assert check.findings((ROOT / rel).read_text(encoding="utf-8")) == [], rel


# -- against the ledger itself, where the local copy is present ----------------------------------------
@needs_archive
def test_the_local_copy_is_the_archive_qs6_source_json_records():
    data = qs6.ARCHIVE_PATH.read_bytes()
    extract = _tool("qs6_extract")
    members = extract.verify(data, DATA["source"])
    assert len(members) == 22


@needs_archive
def test_each_cut_renders_to_its_committed_text_and_its_time_is_the_rules_choice():
    extract = _tool("qs6_extract")
    ok, lines = extract.cuts_report(qs6.ARCHIVE_PATH.read_bytes(), DATA)
    assert ok, "\n".join(lines)


@needs_archive
def test_each_items_evidence_exists_and_a_length_items_lies_in_the_smallest_cut():
    key_tool = _tool("qs6_key")
    members = qs6.read_archive(qs6.ARCHIVE_PATH.read_bytes(), DATA["source"])
    units = qs6.timeline(members)
    first = datetime.fromisoformat(DATA["cuts"]["cuts"][0]["time"])
    for it in DATA["items"]["items"]:
        for c in it["evidence"]:
            u, line = key_tool.locate(units, members, c)
            assert u is not None and line, c
            if it["set"] == "length":
                assert u.t <= first, (it["id"], c)


@needs_archive
def test_no_line_of_the_ledger_is_copied_into_a_committed_file():
    members = qs6.read_archive(qs6.ARCHIVE_PATH.read_bytes(), DATA["source"])
    lines = {x.strip() for text, _ in members.values() for x in text.split("\n") if len(x.strip()) >= 40}
    for rel in MINE:
        text = (ROOT / rel).read_text(encoding="utf-8")
        copied = [x for x in lines if x in text]
        assert copied == [], (rel, copied[:1])


@needs_key
def test_the_key_holds_its_hash_its_form_100_percent_and_its_evidence():
    key_tool = _tool("qs6_key")
    assert key_tool.check(qs6.KEY_PATH.read_bytes(), DATA, qs6.ARCHIVE_PATH.read_bytes()) == []


@needs_key
def test_no_sha_hex_or_time_of_the_keys_is_written_in_a_committed_file():
    key = json.loads(qs6.KEY_PATH.read_text(encoding="utf-8"))
    types = {it["id"]: it["type"] for it in DATA["items"]["items"]}
    values = {e["value"] for iid, cuts in key["items"].items() for e in cuts.values()
              if not e.get("nil") and types[iid] in ("sha", "hex", "time")}
    assert values
    for rel in MINE:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert [v for v in values if v in text] == [], rel


@needs_key
@pytest.mark.parametrize("cut", qs6.CUT_NAMES)
def test_each_cut_class_builds_from_the_local_copy_with_no_arguments(cut):
    suite = qs6.CUT_CLASSES[cut]()
    assert len(suite.items()) == 22 and qs6.sha256_text(suite.text) == suite.cut_sha
