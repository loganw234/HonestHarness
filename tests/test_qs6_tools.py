"""tools/qs6_extract.py and tools/qs6_key.py, on the synthetic archive of
tests/test_qs6_support.py: installing a copy and refusing a changed one,
unpacking without keys/, reading from a git object store, building the data
files (checked against a computation apart from them), the cuts report, the
key's four checks, and output that holds no absolute path."""
import hashlib
import importlib.util
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from qs.suites import qs6  # noqa: E402
from test_qs6_support import (ITEMS, MEMBERS, VALUES, build_zip, make_world,  # noqa: E402
                              source_for)


def _tool(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


extract = _tool("qs6_extract")
keytool = _tool("qs6_key")


# -- the extractor -----------------------------------------------------------------------------------
def test_install_writes_the_archive_as_it_is(tmp_path):
    data = build_zip()
    out = extract.install(data, source_for(data), tmp_path / "d")
    assert out == tmp_path / "d" / "round6-ledger.zip" and out.read_bytes() == data


def test_install_refuses_a_changed_byte_and_writes_nothing(tmp_path):
    data = bytearray(build_zip())
    source = source_for(bytes(data))
    data[50] ^= 1
    with pytest.raises(qs6.SourceError):
        extract.install(bytes(data), source, tmp_path / "d")
    assert not (tmp_path / "d").exists()


def test_install_refuses_another_git_blob_id(tmp_path):
    data = build_zip()
    with pytest.raises(qs6.SourceError, match="blob"):
        extract.install(data, dict(source_for(data), git_blob="0" * 40), tmp_path / "d")


def test_unpack_writes_each_member_checked_and_no_keys_member(tmp_path):
    data = build_zip()
    names = extract.unpack(data, source_for(data), tmp_path / "u")
    assert sorted(names) == sorted(MEMBERS)
    assert not (tmp_path / "u" / "keys").exists()
    for name, (_, text) in MEMBERS.items():
        assert (tmp_path / "u" / name).read_bytes() == text.encode("utf-8")


def test_the_archive_is_read_from_a_git_object_store(tmp_path):
    repo = tmp_path / "repo"
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")

    def git(*args, data=b""):
        return subprocess.run(["git", "-C", str(repo), *args], input=data, capture_output=True,
                              check=True, env=env).stdout.decode().strip()

    repo.mkdir()
    git("init", "-q")
    blob = git("hash-object", "-w", "--stdin", data=build_zip())
    inner = git("mktree", data=f"100644 blob {blob}\tround6-ledger.zip\n".encode())
    tree = git("mktree", data=f"040000 tree {inner}\tarchive\n".encode())
    assert extract.fetch_git(repo, tree) == build_zip()
    assert extract.git_blob_id(build_zip()) == blob
    with pytest.raises(qs6.SourceError, match="git show"):
        extract.fetch_git(repo, tree, "archive/absent.zip")


def test_build_source_agrees_with_a_computation_apart_from_it():
    data = build_zip()
    built, apart = extract.build_source(data), source_for(data)
    for k in ("bytes", "sha256", "git_blob", "top", "kept_time_zone", "excluded"):
        assert built[k] == apart[k], k
    assert [(m["name"], m["sha256"], m["kept"]) for m in built["members"]] == [
        (m["name"], m["sha256"], m["kept"]) for m in apart["members"]]
    stamped = {m["name"]: m["kept_minus_last_stamp_s"] for m in built["members"] if m["stamped_entries"]}
    assert stamped == {"P1.md": 0, "lead.md": 0, "verifier-P0.md": 0}


def _targets_at(times):
    """TARGETS that put the four cuts at the given unit times."""
    data = build_zip()
    units = qs6.timeline(qs6.read_archive(data, source_for(data)))
    size = {t: len(qs6.cut_text(units, datetime.fromisoformat(t)).encode("utf-8")) // 4 for t in times}
    return dict(zip(["c016k", "c032k", "c064k", "c128k"], (size[t] for t in times)))


TIMES = ["2026-10-02T09:20:00-07:00", "2026-10-02T09:40:00-07:00", "2026-10-02T10:15:00-07:00",
         "2026-10-02T10:46:00-07:00"]


def test_build_cuts_chooses_each_time_by_bytes_over_4_and_sets_the_caps_by_rule(tmp_path, monkeypatch):
    monkeypatch.setattr(qs6, "TARGETS", _targets_at(TIMES))
    w = make_world(tmp_path)
    cuts = extract.build_cuts(w.archive_bytes, w.data["source"], w.data["items"])["cuts"]
    assert [c["time"] for c in cuts] == TIMES + ["2026-10-02T11:00:00-07:00"]
    units = qs6.timeline(qs6.read_archive(w.archive_bytes, w.data["source"]))
    for c in cuts:
        text = qs6.cut_text(units, datetime.fromisoformat(c["time"]))
        assert c["sha256"] == hashlib.sha256(text.encode("utf-8")).hexdigest()
        assert c["caps"]["max_call_prompt_tokens"] == qs6.cap_for(c["p0_largest_request"])


def test_the_cuts_report_holds_and_names_what_differs(tmp_path, monkeypatch):
    monkeypatch.setattr(qs6, "TARGETS", _targets_at(TIMES))
    w = make_world(tmp_path)
    data = dict(w.data, cuts=extract.build_cuts(w.archive_bytes, w.data["source"], w.data["items"]))
    ok, lines = extract.cuts_report(w.archive_bytes, data)
    assert ok and all(line.endswith("ok") for line in lines)
    data["cuts"]["cuts"][2]["sha256"] = "0" * 64
    ok, lines = extract.cuts_report(w.archive_bytes, data)
    assert not ok and "DIFFERS: sha256" in lines[2]


def test_main_installs_prints_no_absolute_path_and_refuses_with_exit_2(tmp_path, monkeypatch, capsys):
    w = make_world(tmp_path)
    monkeypatch.setattr(qs6, "load_data", lambda *a, **k: w.data)
    assert extract.main(["--zip", str(w.archive), "--dest", str(tmp_path / "d")]) == 0
    assert (tmp_path / "d" / "round6-ledger.zip").read_bytes() == w.archive_bytes
    bad = tmp_path / "bad.zip"
    data = bytearray(w.archive_bytes)
    data[60] ^= 1
    bad.write_bytes(bytes(data))
    assert extract.main(["--zip", str(bad), "--dest", str(tmp_path / "e")]) == 2
    out = capsys.readouterr()
    text = out.out + out.err
    assert "REFUSED" in out.err and "installed" in out.out
    for form in (str(tmp_path), tmp_path.as_posix()):
        assert form not in text
    assert text.isascii()


# -- the key tool -------------------------------------------------------------------------------------
def test_a_sound_key_holds_all_four_checks(tmp_path):
    w = make_world(tmp_path)
    assert keytool.check(w.key.read_bytes(), w.data, w.archive_bytes) == []
    assert keytool.check(w.key.read_bytes(), w.data, None) == []        # check 4 needs the archive


def test_a_changed_key_fails_check_1(tmp_path):
    w = make_world(tmp_path)
    bad = keytool.check(w.key.read_bytes() + b" ", w.data, w.archive_bytes)
    assert len(bad) == 1 and bad[0].startswith("1.")


def _edited(tmp_path, edit):
    w = make_world(tmp_path, doc_edit=edit)
    return keytool.check(w.key.read_bytes(), w.data, w.archive_bytes)


def test_not_in_the_input_where_the_cut_holds_the_evidence_fails_check_4(tmp_path):
    bad = _edited(tmp_path, lambda d: d["items"]["S01"].update(c016k={"nil": True}))
    assert bad == [f"4. S01 at c016k is 'not in the input', but the cut holds {ITEMS[0]['evidence']}"]


def test_a_value_whose_evidence_lies_after_its_cut_fails_check_4(tmp_path):
    ev = ITEMS[4]["evidence"]
    bad = _edited(tmp_path, lambda d: d["items"]["S05"].update(c016k=dict(VALUES["S05"], evidence=ev)))
    assert bad == [f"4. S05 at c016k cites {ev[0]}, which lies after the cut"]


def test_a_citation_the_item_does_not_make_fails_check_4(tmp_path):
    bad = _edited(tmp_path, lambda d: d["items"]["S02"]["c016k"].update(evidence=["lead.md:1"]))
    assert bad == ["4. S02 at c016k cites lead.md:1, which qs6_items.json does not"]


def test_a_value_of_the_wrong_form_fails_check_2(tmp_path):
    bad = _edited(tmp_path, lambda d: d["items"]["S01"]["c016k"].update(value="not-a-sha"))
    assert bad == ["2. the key's value for S01 at c016k is not a sha"]


def test_a_key_that_does_not_score_itself_exact_fails_check_3(tmp_path):
    bad = _edited(tmp_path, lambda d: d["items"]["S03"]["c016k"].update(written="4.5 parsecs"))
    assert bad == ["3. S03 at c016k: one of the key's own answer forms scores dropped_unit"]


def test_show_prints_the_question_its_lines_and_the_key_in_ascii(tmp_path):
    w = make_world(tmp_path)
    out = keytool.show("S02", w.key.read_bytes(), w.data, w.archive_bytes)
    assert out[0].startswith("S02 (length, count): Of the 9 faults")
    assert any("lead.md:" in x and "7 were caught" in x for x in out)
    assert sum(x.startswith("  key at ") for x in out) == 5 and all(x.isascii() for x in out)


def test_main_hashes_and_checks_with_exit_codes(tmp_path, monkeypatch, capsys):
    w = make_world(tmp_path)
    monkeypatch.setattr(qs6, "load_data", lambda *a, **k: w.data)
    assert keytool.main(["--hash", "--key", str(w.key)]) == 0
    assert capsys.readouterr().out.strip() == w.data["items"]["key_sha256"]
    assert keytool.main(["--check", "--key", str(w.key), "--archive", str(w.archive)]) == 0
    assert "holds" in capsys.readouterr().out
    w.key.write_bytes(w.key.read_bytes() + b"\n")
    assert keytool.main(["--check", "--key", str(w.key), "--archive", str(w.archive)]) == 2
    assert keytool.main(["--check", "--key", str(tmp_path / "absent.json")]) == 2
