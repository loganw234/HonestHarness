import hashlib
import os
import subprocess

import jsonschema
import pytest

from qs import record as rec


def good(**over):
    r = rec.new_record(
        record_id="b.i.r0", batch="b", live=False, suite="s", suite_version="1", item="i",
        repeat=0, provider="deepseek", base_url="http://127.0.0.1:1", model_sent="m",
        model_reported=["m"], system_fingerprint=[], thinking=True, effort=None,
        sampling={"sent": {}, "ignored": []}, prompt_version="1",
        caps={"max_prompt_tokens": 100, "max_output_tokens": 50, "max_call_prompt_tokens": 80},
        calls=1,
        usage={"cache_hit": 0, "cache_miss": 10, "output": 5, "reasoning": 0},
        price_table="t", rate_period="off_peak", cost_usd="0.0000045",
        outcome={"status": "pass", "detail": ""}, stop_reason=None,
        transcript_sha256="0" * 64,
        code={"commit": "a" * 40, "changed": False, "tools_sha256": None})
    r.update(over)
    return r


def test_good_record_validates():
    rec.validate(good())


@pytest.mark.parametrize("field", ["usage", "cost_usd", "model_sent", "transcript_sha256",
                                   "caps", "stop_reason"])
def test_missing_field_fails(field):
    r = good()
    del r[field]
    with pytest.raises(jsonschema.ValidationError):
        rec.validate(r)


def test_bad_values_fail():
    for over in ({"cost_usd": "-1"}, {"rate_period": "midnight"},
                 {"outcome": {"status": "maybe", "detail": ""}}, {"extra": 1},
                 {"ts_utc": "2026-10-06 17:25"}, {"cost_usd": "6E-7"},
                 {"model_reported": "m"}, {"record_id": "b:i.r0"}, {"item": "a:b"},
                 {"record_id": "b.i.r0" + chr(10)}, {"batch": "b" + chr(10)},
                 {"caps": {"max_prompt_tokens": 1}}):
        with pytest.raises(jsonschema.ValidationError):
            rec.validate(good(**over))


def test_a_run_across_periods_is_mixed():
    rec.validate(good(rate_period="mixed", model_reported=["a", "b"],
                      system_fingerprint=["fp_1", "fp_2"]))


def test_append_validates_first(tmp_path):
    p = tmp_path / "runs.jsonl"
    rec.append(p, good())
    bad = good()
    del bad["usage"]
    with pytest.raises(jsonschema.ValidationError):
        rec.append(p, bad)
    assert len(p.read_text(encoding="utf-8").splitlines()) == 1


def test_transcript_is_redacted_before_hashing(tmp_path):
    sha = rec.save_transcript(tmp_path, "r1", {"auth": "Bearer secret-xyz"},
                              redact=lambda s: s.replace("secret-xyz", "<redacted>"))
    text = (tmp_path / "r1.json").read_text(encoding="utf-8")
    assert "secret-xyz" not in text
    assert sha == hashlib.sha256(text.encode("utf-8")).hexdigest()


def test_a_version_1_record_without_code_still_validates():
    r = good(record_version=1)
    del r["code"]
    rec.validate(r)


def test_a_version_2_record_must_name_its_code():
    assert good()["record_version"] == 2
    r = good()
    del r["code"]
    with pytest.raises(jsonschema.ValidationError):
        rec.validate(r)


def test_bad_code_values_fail():
    for code in ({"commit": "xyz", "changed": False, "tools_sha256": None},
                 {"commit": "a" * 39, "changed": False, "tools_sha256": None},
                 {"commit": None, "changed": "no", "tools_sha256": None},
                 {"commit": None, "changed": None},
                 {"commit": None, "changed": None, "tools_sha256": "f" * 63},
                 {"commit": None, "changed": None, "tools_sha256": None, "extra": 1}):
        with pytest.raises(jsonschema.ValidationError):
            rec.validate(good(code=code))


def _git(cwd, *args):
    return subprocess.run(["git", "-c", "user.name=test", "-c", "user.email=test",
                           "-c", "commit.gpgsign=false", *args],
                          cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def test_code_identity_reads_head_and_any_change_outside_records(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    (repo / "a.py").write_text("x = 1\n", encoding="utf-8")
    (repo / "records").mkdir()
    (repo / "records" / "spend.jsonl").write_text("", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "one")
    head = _git(repo, "rev-parse", "HEAD")
    assert rec.code_identity(repo) == {"commit": head, "changed": False}
    (repo / "records" / "spend.jsonl").write_text("{}\n", encoding="utf-8")
    (repo / "records" / "runs.jsonl").write_text("{}\n", encoding="utf-8")
    assert rec.code_identity(repo) == {"commit": head, "changed": False}
    (repo / "a.py").write_text("x = 2\n", encoding="utf-8")
    assert rec.code_identity(repo) == {"commit": head, "changed": True}
    _git(repo, "checkout", "--", "a.py")
    (repo / "b.py").write_text("", encoding="utf-8")         # untracked counts
    assert rec.code_identity(repo) == {"commit": head, "changed": True}


def test_code_identity_outside_a_checkout_is_unknown(tmp_path):
    assert rec.code_identity(tmp_path) == {"commit": None, "changed": None}


def test_tools_digest_is_of_the_distinct_tool_lists_as_sent():
    t1 = [{"type": "function", "function": {"name": "f", "description": "one"}}]
    t2 = [{"type": "function", "function": {"name": "f", "description": "two"}}]
    call = lambda tools: {"request": {"messages": [], **({"tools": tools} if tools else {})}}
    assert rec.tools_digest([]) is None
    assert rec.tools_digest([call(None), {"request": None}]) is None
    once = rec.tools_digest([call(t1)])
    assert once == rec.tools_digest([call(t1), call(t1), call(None)])
    assert rec.tools_digest([call(t1), call(t2)]) == rec.tools_digest([call(t2), call(t1)])
    assert rec.tools_digest([call(t2)]) != once



def _repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    (repo / "a.py").write_text("x = 1\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "one")
    return repo


def test_untracked_files_count_whatever_git_config_says(tmp_path):
    repo = _repo(tmp_path)
    _git(repo, "config", "status.showUntrackedFiles", "no")
    (repo / "b.py").write_text("", encoding="utf-8")
    assert rec.code_identity(repo)["changed"] is True


def test_a_directory_inside_another_repository_is_unknown(tmp_path):
    repo = _repo(tmp_path)
    (repo / "sub").mkdir()
    (repo / "sub" / "c.py").write_text("", encoding="utf-8")
    assert rec.code_identity(repo / "sub") == {"commit": None, "changed": None}


def test_git_output_that_is_not_a_hash_is_unknown(tmp_path, monkeypatch):
    real = subprocess.run

    def fake(args, **kw):
        if args[-2:] == ["rev-parse", "HEAD"]:
            return subprocess.CompletedProcess(args, 0, stdout=b"\x81 not a hash\n", stderr=b"")
        return real(args, **kw)

    repo = _repo(tmp_path)
    monkeypatch.setattr(rec.subprocess, "run", fake)
    assert rec.code_identity(repo) == {"commit": None, "changed": None}


def test_code_identity_takes_no_lock_and_writes_no_index(tmp_path):
    repo = _repo(tmp_path)
    index = repo / ".git" / "index"
    a = repo / "a.py"
    st = a.stat()
    os.utime(a, ns=(st.st_atime_ns, st.st_mtime_ns + 5_000_000_000))   # the index is now stale
    before = (index.read_bytes(), index.stat().st_mtime_ns)
    rec.code_identity(repo)
    assert (index.read_bytes(), index.stat().st_mtime_ns) == before
    _git(repo, "status", "--porcelain")                                 # the control: plain status
    assert (index.read_bytes(), index.stat().st_mtime_ns) != before     # rewrites it


def test_a_trailing_newline_does_not_validate():
    for code in ({"commit": "a" * 40 + "\n", "changed": False, "tools_sha256": None},
                 {"commit": None, "changed": None, "tools_sha256": "f" * 64 + "\n"}):
        with pytest.raises(jsonschema.ValidationError):
            rec.validate(good(code=code))


def test_check_code_refuses_what_a_record_could_not_hold():
    rec.check_code({"commit": None, "changed": None})
    rec.check_code({"commit": "a" * 40, "changed": True})
    for bad in ({"commit": "xyz", "changed": False}, {"commit": None}, {"commit": None, "changed": "no"}):
        with pytest.raises(jsonschema.ValidationError):
            rec.check_code(bad)
