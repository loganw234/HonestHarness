"""QS6's archive reader and cut builder, on the synthetic archive of
tests/test_qs6_support.py: stamp order across files, unstamped files at their
kept times, keys/ never read, preambles, shared stamps, CRLF, the rendering,
the choice of cut times by bytes / 4, and every refusal of a changed copy."""
import hashlib
import io
import sys
import zipfile
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from qs.suites import qs6  # noqa: E402
from test_qs6_support import (KEYS_MEMBER, KEYS_SENTINEL, MEMBERS, TOP, build_zip,  # noqa: E402
                              source_for)


def units():
    data = build_zip()
    return qs6.timeline(qs6.read_archive(data, source_for(data)))


def at(s: str) -> datetime:
    return datetime.fromisoformat(s)


def test_units_go_in_time_order_across_files_with_unstamped_files_at_their_kept_times():
    got = [(u.t.strftime("%H:%M:%S"), u.file, u.kind) for u in units()]
    assert got == [
        ("09:00:00", "README.md", "file"),
        ("09:05:00", "briefs/P1.md", "file"),
        ("09:10:00", "lead.md", "entry"),
        ("09:20:00", "verifier-P0.md", "entry"),
        ("09:30:00", "lead.md", "entry"),
        ("09:40:00", "verifier-P0.md", "entry"),
        ("10:15:00", "lead.md", "entry"),              # one time, two files: by file name
        ("10:15:00", "verifier-P0.md", "entry"),
        ("10:30:00", "P1.md", "entry"),
        ("10:30:00", "P1.md", "entry"),
        ("10:46:00", "briefs/P2.md", "file"),
        ("11:00:00", "lead.md", "entry"),
    ]


def test_two_entries_with_one_stamp_keep_their_order_in_the_file():
    p1 = [u for u in units() if u.file == "P1.md"]
    assert [u.n for u in p1] == [1, 2]
    assert "P1's design" in p1[0].text and "P1's appendix" in p1[1].text


def test_a_preamble_goes_with_its_files_first_entry():
    lead = [u for u in units() if u.file == "lead.md"]
    assert lead[0].text.startswith("# The lead's ledger\n\nAppend only.\n\n## 2026-10-02 09:10:00")
    assert all(u.text.startswith("## ") for u in lead[1:])


def test_crlf_is_read_as_lf_and_entries_split_on_stamped_headings_only():
    us = units()
    assert all("\r" not in u.text for u in us)
    assert [u.t.strftime("%H:%M:%S") for u in us if u.file == "verifier-P0.md"] == [
        "09:20:00", "09:40:00", "10:15:00"]
    readme = next(u for u in us if u.file == "README.md")
    assert readme.kind == "file" and "## The rules" in readme.text


def test_an_unstamped_file_enters_at_its_kept_time_and_not_a_second_before():
    us = units()
    assert "Written late." not in qs6.cut_text(us, at("2026-10-02T10:45:59-07:00"))
    assert "Written late." in qs6.cut_text(us, at("2026-10-02T10:46:00-07:00"))


def test_an_entry_enters_at_its_stamp_and_not_a_second_before():
    us = units()
    assert "the last entry" not in qs6.cut_text(us, at("2026-10-02T10:59:59-07:00"))
    assert "the last entry" in qs6.cut_text(us, at("2026-10-02T11:00:00-07:00"))


def test_keys_are_never_read_and_never_enter_a_cut():
    data = build_zip()
    members = qs6.read_archive(data, source_for(data))
    assert not any(name.startswith("keys/") for name in members)
    whole = qs6.cut_text(qs6.timeline(members), at("2026-10-02T23:59:59-07:00"))
    assert KEYS_SENTINEL not in whole and "keys/" not in whole


def test_each_unit_is_rendered_under_a_line_naming_its_file():
    text = qs6.cut_text(units(), at("2026-10-02T09:20:00-07:00"))
    assert text == (
        "=== README.md (a whole file) ===\n# The synthetic ledger\n\n## The rules\n\n"
        "One file per author; stamps from date.\n\n"
        "=== briefs/P1.md (a whole file) ===\n# P1's brief\n\n## Your job\n\nWrite the rows.\n\n"
        "=== lead.md ===\n# The lead's ledger\n\nAppend only.\n\n"
        "## 2026-10-02 09:10:00 -0700 - the round opens\n\nMeasured: P0 landed at abc1234.\n\n"
        "=== verifier-P0.md ===\n## 2026-10-02 09:20:00 -0700 - verifier-P0 starts\n\nIt reads.\n\n")


def test_cut_times_are_chosen_by_bytes_over_4_and_never_split_a_time(monkeypatch):
    us = units()
    sizes = {u.t: len(qs6.cut_text(us, u.t).encode("utf-8")) for u in us}
    t0940, t1015 = at("2026-10-02T09:40:00-07:00"), at("2026-10-02T10:15:00-07:00")
    lead_1015 = next(u for u in us if u.t == t1015 and u.file == "lead.md")
    # A target that the cut to 09:40 plus lead.md's 10:15 entry fits, but not the
    # cut to 10:15, which holds verifier-P0.md's 10:15 entry too: choosing by unit
    # would split 10:15:00; choosing by time must stop at 09:40.
    half = sizes[t0940] + len(qs6.render_unit(lead_1015).encode("utf-8"))
    target = half // 4
    assert sizes[t1015] // 4 > target
    monkeypatch.setattr(qs6, "TARGETS", {"c016k": target})
    chosen = qs6.choose_cut_times(us)
    assert chosen["c016k"] == t0940
    assert chosen["whole"] == at("2026-10-02T11:00:00-07:00")
    for t, size in sizes.items():
        assert (size // 4 <= target) == (t <= chosen["c016k"])


def test_measures_are_characters_bytes_and_their_quarters():
    m = qs6.measures("ab§")        # a section sign is two bytes in UTF-8
    assert m == {"chars": 3, "bytes": 4, "bytes_over_4": 1, "deepseek_ratio": 1}


# -- refusals of a changed copy ------------------------------------------------------------------
def _rezip(edit):
    """The synthetic archive with one member's bytes changed by edit(name, raw)."""
    src = io.BytesIO(build_zip())
    out = io.BytesIO()
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        for i in zin.infolist():
            raw = edit(i.filename[len(TOP):], zin.read(i))
            if raw is not None:
                zout.writestr(zipfile.ZipInfo(i.filename, date_time=i.date_time), raw)
    return out.getvalue()


def test_a_changed_archive_byte_is_refused():
    data = bytearray(build_zip())
    source = source_for(bytes(data))
    data[len(data) // 2] ^= 1
    with pytest.raises(qs6.SourceError, match="SHA-256"):
        qs6.read_archive(bytes(data), source)


def test_a_changed_member_is_refused_even_when_the_archive_hash_is_updated():
    good = build_zip()
    changed = _rezip(lambda n, raw: raw.replace(b"7 were caught", b"8 were caught"))
    source = dict(source_for(good), bytes=len(changed), sha256=hashlib.sha256(changed).hexdigest())
    with pytest.raises(qs6.SourceError, match="lead.md"):
        qs6.read_archive(changed, source)


def test_an_extra_member_a_missing_member_and_an_unnamed_keys_member_are_refused():
    good = build_zip()
    base = source_for(good)

    def resource(data):
        return dict(base, bytes=len(data), sha256=hashlib.sha256(data).hexdigest())

    missing = _rezip(lambda n, raw: None if n == "briefs/P2.md" else raw)
    with pytest.raises(qs6.SourceError, match="lacks"):
        qs6.read_archive(missing, resource(missing))
    renamed = _rezip(lambda n, raw: raw)
    spec = resource(renamed)
    spec["excluded"] = []
    with pytest.raises(qs6.SourceError, match="keys/"):
        qs6.read_archive(renamed, spec)
    spec = resource(renamed)
    spec["members"] = [m for m in spec["members"] if m["name"] != "README.md"]
    with pytest.raises(qs6.SourceError, match="does not list"):
        qs6.read_archive(renamed, spec)


def test_a_changed_kept_time_is_refused():
    data = build_zip()
    spec = source_for(data)
    for m in spec["members"]:
        if m["name"] == "README.md":
            m["kept"] = "2026-10-02T09:00:02-07:00"
    with pytest.raises(qs6.SourceError, match="README.md"):
        qs6.read_archive(data, spec)
    assert hashlib.sha256(data).hexdigest() == spec["sha256"]


def test_the_keys_member_is_known_by_name_only():
    data = build_zip()
    source = source_for(data)          # built before the spy, which then sees read_archive alone
    reads = []
    real_read = zipfile.ZipFile.read

    def spy(self, name, *a, **k):
        reads.append(name if isinstance(name, str) else name.filename)
        return real_read(self, name, *a, **k)

    try:
        zipfile.ZipFile.read = spy
        qs6.read_archive(data, source)
    finally:
        zipfile.ZipFile.read = real_read
    assert TOP + KEYS_MEMBER[0] not in reads
    assert sorted(reads) == sorted(TOP + name for name in MEMBERS)
