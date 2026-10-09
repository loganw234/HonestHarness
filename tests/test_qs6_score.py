"""QS6's scorer on its own: the answer field, "not in the input", each type's
normal form, the five classes, and the key's own answer forms. Every value
here is made up for the tests: the real key's values stay out of the
repository until the runs are scored."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from qs.suites import qs6  # noqa: E402

MEMBERS = ["README.md", "lead.md", "verifier-P0.md", "P1.md", "briefs/P1.md"]
SHA, SHA_KEY = {"id": "X1", "type": "sha"}, {"value": "abc1234", "evidence": ["lead.md:1"]}
HEX, HEX_KEY = {"id": "X2", "type": "hex"}, {"value": "0123abcd", "evidence": ["lead.md:1"]}
TIME, TIME_KEY = {"id": "X3", "type": "time"}, {"value": "09:10:00", "evidence": ["lead.md:1"]}
COUNT, COUNT_KEY = {"id": "X4", "type": "count"}, {"value": 7, "evidence": ["lead.md:1"]}
PCT = {"id": "X5", "type": "figure", "units": ["%", "percent", "per cent"]}
PCT_KEY = {"value": "12.5", "unit": "%", "written": "12.5%", "evidence": ["lead.md:1"]}
TOK = {"id": "X6", "type": "figure", "units": ["tokens", "token", "subagent tokens"]}
TOK_KEY = {"value": "2500000", "unit": "tokens", "written": "2.5 M tokens", "evidence": ["lead.md:1"]}
SEC = {"id": "X7", "type": "figure", "units": ["s", "sec", "secs", "second", "seconds"]}
SEC_KEY = {"value": "4.5", "unit": "s", "written": "4.5 s", "evidence": ["lead.md:1"]}
FILE, FILE_KEY = {"id": "X8", "type": "file"}, {"value": "lead.md", "evidence": ["lead.md:1"]}
NIL_KEY = {"nil": True}
SENTINEL = "QS6-SENTINEL-4d2c"


def cls(spec, entry, content):
    return qs6.score(spec, entry, content, MEMBERS)["class"]


# -- the answer field ------------------------------------------------------------------------
@pytest.mark.parametrize("content", [
    "ANSWER: abc1234", "**ANSWER:** `abc1234`", "- **ANSWER**: abc1234.", "Reasoning first.\n\nAnswer: abc1234",
    "> ANSWER: abc1234", "ANSWER: \"abc1234\"", "ANSWER: abc1234\nANSWER:",
], ids=["plain", "bold", "list", "case", "quote", "quoted", "empty-after"])
def test_the_answer_field_is_read_in_its_allowed_forms(content):
    assert cls(SHA, SHA_KEY, content) == "exact"


def test_the_last_answer_line_with_a_value_is_the_one_read():
    assert cls(SHA, SHA_KEY, "ANSWER: 1111111\nOn reflection:\nANSWER: abc1234") == "exact"
    assert cls(SHA, SHA_KEY, "ANSWER: abc1234\nOn reflection:\nANSWER: 1111111") == "wrong"
    assert qs6.score(SHA, SHA_KEY, "ANSWER: 1\nANSWER: abc1234", MEMBERS)["flags"]["answer_lines"] == 2


@pytest.mark.parametrize("content", [None, "", "The commit is abc1234.", "ANSWER:", "answer abc1234"],
                         ids=["none", "empty", "no-line", "no-value", "no-colon"])
def test_without_an_answer_field_the_class_is_no_answer(content):
    s = qs6.score(SHA, SHA_KEY, content, MEMBERS)
    assert s["class"] == "no_answer" and s["answer_form"] == "absent" and s["answer"] is None


# -- "not in the input" ----------------------------------------------------------------------
@pytest.mark.parametrize("content", [
    "ANSWER: not in the input", "ANSWER: Not in the input.", "ANSWER: NOT IN THE LEDGER",
    "ANSWER: unknown", "ANSWER: not stated", "ANSWER: cannot be determined",
], ids=["plain", "case", "ledger", "unknown", "stated", "determined"])
def test_not_in_the_input_is_exact_where_the_key_is_not_in_the_input(content):
    s = qs6.score(SHA, NIL_KEY, content, MEMBERS)
    assert s["class"] == "exact" and s["answer"] == "not in the input"


def test_not_in_the_input_followed_by_more_is_still_not_in_the_input():
    s = qs6.score(SHA, NIL_KEY, "ANSWER: not in the input; the ledger ends before abc1234", MEMBERS)
    assert s["class"] == "exact" and s["flags"]["nil_with_more"] is True


def test_not_in_the_input_where_the_key_holds_a_value_is_wrong_and_flagged():
    s = qs6.score(SHA, SHA_KEY, "ANSWER: not in the input", MEMBERS)
    assert s["class"] == "wrong" and s["flags"]["nil_answer"] is True


@pytest.mark.parametrize("spec,content", [
    (SHA, "ANSWER: abc1234"), (TIME, "ANSWER: 09:10:00"), (COUNT, "ANSWER: 0"),
    (PCT, "ANSWER: 12.5%"), (FILE, "ANSWER: lead.md"), (HEX, "ANSWER: 0123abcd"),
], ids=["sha", "time", "zero", "figure", "file", "hex"])
def test_a_value_where_the_key_is_not_in_the_input_is_an_overclaim(spec, content):
    assert cls(spec, NIL_KEY, content) == "overclaim"


def test_a_refusal_in_other_words_is_no_answer_not_an_overclaim():
    assert cls(SHA, NIL_KEY, "ANSWER: the ledger is silent on this") == "no_answer"


# -- the types ---------------------------------------------------------------------------------
@pytest.mark.parametrize("content,want", [
    ("ANSWER: abc1234", "exact"), ("ANSWER: ABC1234", "exact"), ("ANSWER: abc1234def99", "exact"),
    ("ANSWER: abc1235", "wrong"), ("ANSWER: abc123", "no_answer"), ("ANSWER: 1111111 then abc1234", "wrong"),
    ("ANSWER: abc1234, not 1111111", "exact"),
], ids=["same", "upper", "longer", "other", "short", "first-wrong", "first-right"])
def test_a_sha_is_exact_when_one_is_a_prefix_of_the_other_at_seven_digits(content, want):
    assert cls(SHA, SHA_KEY, content) == want


def test_the_hex_item_needs_eight_digits_and_takes_a_whole_hash():
    assert cls(HEX, HEX_KEY, "ANSWER: 0123abcd" + "e" * 56) == "exact"
    assert cls(HEX, HEX_KEY, "ANSWER: 0123abc") == "wrong"


@pytest.mark.parametrize("content,want", [
    ("ANSWER: 09:10:00", "exact"), ("ANSWER: 9:10:00", "exact"),
    ("ANSWER: 2026-10-02 09:10:00 -0700", "exact"), ("ANSWER: 09:10:01", "wrong"),
    ("ANSWER: 09:10", "wrong"), ("ANSWER: 25:10:00", "no_answer"),
], ids=["same", "one-digit-hour", "with-date", "other", "minutes", "invalid"])
def test_a_time_is_compared_by_hh_mm_ss(content, want):
    assert cls(TIME, TIME_KEY, content) == want


def test_a_time_without_seconds_is_flagged():
    assert qs6.score(TIME, TIME_KEY, "ANSWER: 09:10", MEMBERS)["flags"]["precision"] == "minutes"


@pytest.mark.parametrize("content,want", [
    ("ANSWER: 7", "exact"), ("ANSWER: seven", "exact"), ("ANSWER: 7 entries", "exact"),
    ("ANSWER: 7 of 9", "exact"), ("ANSWER: 7. That is all.", "exact"), ("ANSWER: 9, of which 7", "wrong"),
    ("ANSWER: 7.5", "no_answer"), ("ANSWER: 17:20:54", "no_answer"), ("ANSWER: eight", "wrong"),
], ids=["digit", "word", "unit", "of", "stop", "first", "decimal", "time", "other-word"])
def test_a_count_is_the_first_integer_or_number_word(content, want):
    assert cls(COUNT, COUNT_KEY, content) == want


@pytest.mark.parametrize("content", [
    "ANSWER: verifier-P9 has written 7 entries", "ANSWER: in round9, 7", "ANSWER: 7a12345 holds 7",
], ids=["agent", "word", "hex"])
def test_the_digits_of_a_name_are_never_a_count(content):
    assert cls(COUNT, COUNT_KEY, content) == "exact"


def test_the_digits_of_a_name_are_never_a_figure():
    assert cls(SEC, SEC_KEY, "ANSWER: qs9 took 4.5 s") == "exact"


def test_counts_read_digit_groups_and_compound_number_words():
    assert cls(COUNT, dict(COUNT_KEY, value=1563), "ANSWER: 1,563 lines") == "exact"
    assert cls(COUNT, dict(COUNT_KEY, value=21), "ANSWER: twenty-one") == "exact"
    assert cls(COUNT, dict(COUNT_KEY, value=40), "ANSWER: forty") == "exact"


@pytest.mark.parametrize("spec,key,content,want", [
    (PCT, PCT_KEY, "ANSWER: 12.5%", "exact"), (PCT, PCT_KEY, "ANSWER: 12.5 percent", "exact"),
    (PCT, PCT_KEY, "ANSWER: 12.5", "dropped_unit"), (PCT, PCT_KEY, "ANSWER: 0.125", "wrong"),
    (PCT, PCT_KEY, "ANSWER: 12.5 minutes", "wrong"), (PCT, PCT_KEY, "ANSWER: 12.6%", "wrong"),
    (TOK, TOK_KEY, "ANSWER: 2.5 M tokens", "exact"), (TOK, TOK_KEY, "ANSWER: 2,500,000 tokens", "exact"),
    (TOK, TOK_KEY, "ANSWER: about 2.5 million subagent tokens", "exact"),
    (TOK, TOK_KEY, "ANSWER: 2.5M", "dropped_unit"), (TOK, TOK_KEY, "ANSWER: 2.5", "dropped_unit"),
    (TOK, TOK_KEY, "ANSWER: 2500000", "dropped_unit"), (TOK, TOK_KEY, "ANSWER: 2.5 M bytes", "wrong"),
    (TOK, TOK_KEY, "ANSWER: 3 M tokens", "wrong"),
    (SEC, SEC_KEY, "ANSWER: 4.5 s", "exact"), (SEC, SEC_KEY, "ANSWER: 4.50 seconds", "exact"),
    (SEC, SEC_KEY, "ANSWER: about 4.5 s in a tree copy", "exact"), (SEC, SEC_KEY, "ANSWER: 4.5", "dropped_unit"),
    (SEC, SEC_KEY, "ANSWER: 4500 ms", "wrong"), (SEC, SEC_KEY, "ANSWER: 5.4 s", "wrong"),
], ids=["pct", "percent", "pct-bare", "fraction", "pct-other-unit", "pct-other",
        "tok", "tok-digits", "tok-words", "tok-mag-only", "tok-significand", "tok-bare", "tok-other-unit",
        "tok-other", "sec", "sec-word", "sec-prose", "sec-bare", "sec-ms", "sec-other"])
def test_a_figure_is_its_value_and_unit(spec, key, content, want):
    assert cls(spec, key, content) == want


def test_a_figures_normal_form_is_a_decimal_and_a_closed_unit_word():
    assert qs6.score(TOK, TOK_KEY, "ANSWER: 2.5 M tokens", MEMBERS)["answer"] == {"value": "2500000", "unit": "given"}
    assert qs6.score(SEC, SEC_KEY, "ANSWER: 4.5", MEMBERS)["answer"] == {"value": "4.5", "unit": "absent"}
    assert qs6.score(SEC, SEC_KEY, "ANSWER: 4500 ms", MEMBERS)["answer"] == {"value": "4500", "unit": "other"}


@pytest.mark.parametrize("content,want", [
    ("ANSWER: lead.md", "exact"), ("ANSWER: `lead.md`", "exact"), ("ANSWER: lead", "exact"),
    ("ANSWER: the lead's file", "exact"), ("ANSWER: parcelround-r6-ledger/lead.md", "exact"),
    ("ANSWER: verifier-P0.md", "wrong"), ("ANSWER: notes.md", "wrong"), ("ANSWER: none of them", "no_answer"),
], ids=["name", "code", "stem", "possessive", "prefixed", "other", "unlisted", "none"])
def test_a_file_is_a_members_name(content, want):
    assert cls(FILE, FILE_KEY, content) == want


def test_a_file_outside_the_archive_is_recorded_as_unlisted_and_briefs_keep_their_directory():
    assert qs6.score(FILE, FILE_KEY, "ANSWER: notes.md", MEMBERS)["answer"] == "unlisted"
    brief = dict(FILE_KEY, value="briefs/P1.md")
    assert cls(FILE, brief, "ANSWER: briefs/P1.md") == "exact"
    assert cls(FILE, brief, "ANSWER: P1.md") == "wrong"


# -- the key's own forms, and no model text in what is recorded ----------------------------------
@pytest.mark.parametrize("spec,key", [
    (SHA, SHA_KEY), (HEX, HEX_KEY), (TIME, TIME_KEY), (COUNT, COUNT_KEY), (PCT, PCT_KEY),
    (TOK, TOK_KEY), (SEC, SEC_KEY), (FILE, FILE_KEY), (SHA, NIL_KEY), (PCT, NIL_KEY),
], ids=["sha", "hex", "time", "count", "pct", "tok", "sec", "file", "nil-sha", "nil-figure"])
def test_the_keys_own_answer_forms_all_score_exact(spec, key):
    forms = qs6.answer_forms(spec, key)
    assert len(forms) >= 2
    for f in forms:
        assert cls(spec, key, f) == "exact", f


@pytest.mark.parametrize("spec,key,content", [
    (FILE, FILE_KEY, f"ANSWER: {SENTINEL}.md"), (SEC, SEC_KEY, f"ANSWER: 4.5 {SENTINEL}"),
    (SHA, SHA_KEY, f"ANSWER: {SENTINEL}"), (COUNT, COUNT_KEY, f"ANSWER: 7 {SENTINEL}"),
    (TIME, TIME_KEY, f"ANSWER: 09:10:00 {SENTINEL}"), (SHA, NIL_KEY, f"ANSWER: not in the input {SENTINEL}"),
], ids=["file", "figure", "sha", "count", "time", "nil"])
def test_no_model_text_reaches_the_normal_form(spec, key, content):
    s = qs6.score(spec, key, content, MEMBERS)
    recorded = {k: v for k, v in s.items() if k != "raw"}
    assert SENTINEL not in repr(recorded)
    assert SENTINEL in s["raw"]
