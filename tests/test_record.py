import hashlib

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
        transcript_sha256="0" * 64)
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
