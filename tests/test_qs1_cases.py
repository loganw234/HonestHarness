"""QS1's case file, checked on its own: its ids, its coverage of TC 7.8's list,
its tools, goldens consistent with their tools' schemas and their own canonical
values, one hand-written history only, the documented expectations, and the
special-token list's source."""
import importlib
import inspect
import json
import re
from pathlib import Path

import jsonschema

from qs.providers import deepseek
from qs.suite import ID_PATTERN
from qs.suites import qs1
from qs.suites.qs1 import QS1

ROOT = Path(__file__).resolve().parent.parent
DATA = qs1.load_cases()
SUITE = QS1()
CASES = list(SUITE.cases.values())


def _objects(schema):
    """Every object schema inside a schema."""
    if isinstance(schema, dict):
        if schema.get("type") == "object":
            yield schema
        for v in schema.values():
            yield from _objects(v)
    elif isinstance(schema, list):
        for v in schema:
            yield from _objects(v)


def _call(name, args):
    return {"id": "call_00_x", "type": "function",
            "function": {"name": name, "arguments": json.dumps(args, ensure_ascii=False)}}


def test_qs1_takes_no_arguments_and_loads_as_the_live_entry_point_loads_it():
    assert list(inspect.signature(QS1).parameters) == []
    module, _, cls = "qs.suites.qs1:QS1".partition(":")      # as tools/live.py's load_suite
    suite = getattr(importlib.import_module(module), cls)()
    assert suite.name == "qs1" and len(suite.items()) == 35


def test_item_ids_are_valid_and_unique():
    ids = [i.id for i in SUITE.items()]
    assert len(ids) == len(set(ids)) == 35
    assert all(ID_PATTERN.fullmatch(i) for i in ids)
    assert sum(i.endswith(".stream") for i in ids) == 13


def test_every_case_of_tc_7_8_is_present():
    shapes = {c["shape"] for c in CASES}
    assert {"single", "parallel", "multiturn", "handwritten", "code", "unicode", "empty",
            "nested", "enum", "nocall", "choice"} <= shapes
    # streamed and not, for at least the single, parallel and multi-turn shapes
    for shape in ("single", "parallel", "multiturn"):
        assert {c["stream"] for c in CASES if c["shape"] == shape} == {False, True}
    # each tool_choice
    assert {"default", "none", "auto", "required", "named:get_date"} <= {
        qs1._label(c.get("tool_choice")) for c in CASES}
    # parallel calls, a chain of turns, a follow-up question, and a no-call case
    assert max(len(t.get("calls", [])) for c in CASES for t in c["turns"]) == 3
    assert any(len(c["turns"]) == 3 for c in CASES)
    assert any(t.get("user") for c in CASES for t in c["turns"])
    assert all(t["expect"] == "none" for c in CASES if c["shape"] == "nocall" for t in c["turns"])


def test_the_tools_are_valid_and_portable():
    names = [t["function"]["name"] for t in DATA["tools"]]
    assert len(names) == len(set(names)) == 6
    for t in DATA["tools"]:
        assert t["type"] == "function"
        assert re.fullmatch(r"[A-Za-z0-9_-]{1,128}", t["function"]["name"])   # D10:430
        params = t["function"].get("parameters", qs1.EMPTY_PARAMETERS)
        jsonschema.Draft202012Validator.check_schema(params)
        objects = list(_objects(params))
        assert objects and all(o.get("additionalProperties") is False for o in objects)
    # one tool is declared with parameters omitted: D10's empty parameter list
    assert [n for n, f in SUITE.declared.items() if "parameters" not in f] == ["get_time"]


def test_each_golden_turn_says_what_is_right_and_what_may_vary():
    for c in CASES:
        for t in c["turns"]:
            assert t["expect"] in qs1.EXPECTS, c["id"]
            assert t["right"].strip() and t["may_vary"].strip(), c["id"]
            assert bool(t.get("calls")) == (t["expect"] != "none"), c["id"]


def test_each_golden_call_is_schema_valid_and_matches_its_own_golden():
    n = 0
    for c in CASES:
        for t in c["turns"]:
            for g in t.get("calls", []):
                call = _call(g["name"], g["canonical"])
                assert qs1.schema_valid(call, SUITE.declared), (c["id"], g["name"])
                assert qs1.match_call(g, call) is None, (c["id"], g["name"])
                n += 1
    assert n == 38      # the 35 items' golden calls, required's examples included


def test_a_case_goes_on_after_calls_only_with_their_results():
    for c in CASES:
        for t in c["turns"][:-1]:
            assert t["expect"] != "any_declared", c["id"]
            for g in t.get("calls", []):
                assert isinstance(g.get("result"), str) and g["result"], c["id"]


def test_only_the_handwritten_case_carries_an_assistant_message():
    holders = sorted({c["id"] for c in CASES for m in c["messages"] if m["role"] == "assistant"})
    assert holders == ["multiturn.handwritten"]
    hw = SUITE.cases["multiturn.handwritten"]
    written = [m for m in hw["messages"] if m["role"] == "assistant"]
    assert len(written) == 1 and "reasoning_content" not in written[0]
    assert len(written[0]["tool_calls"]) == 1
    results = [m["tool_call_id"] for m in hw["messages"] if m["role"] == "tool"]
    assert results == [written[0]["tool_calls"][0]["id"]]
    # every other case opens with the user's message alone
    assert all([m["role"] for m in c["messages"]] == ["user"] for c in CASES if c is not hw)


def test_the_documented_expectations_agree_with_the_adapter():
    for c in CASES:
        doc, tc = c.get("documented"), c.get("tool_choice")
        if c["id"] == "multiturn.handwritten":
            assert doc["thinking"]["status"] == 400 and doc["thinking"]["source"].startswith("D8")
            assert doc["non_thinking"]["status"] is None
            assert doc["non_thinking"]["source"].startswith("D9")
        elif deepseek.documented_refusal(True, tc):
            assert doc["thinking"]["status"] == 400
            assert doc["thinking"]["source"] == "D10, ds/chat_completion_full.txt:463-466"
            assert doc["non_thinking"] is None and deepseek.documented_refusal(False, tc) is None
        else:
            assert doc is None, c["id"]
    assert sorted(c["item"] for c in CASES if deepseek.documented_refusal(True, c.get("tool_choice"))) == [
        "choice.named", "choice.named.stream", "choice.required", "choice.required.stream"]


def test_the_code_and_unicode_goldens_are_the_text_their_prompts_give():
    for cid, key in (("code.multiline", "content"), ("code.json_text", "content"),
                     ("unicode.text", "text")):
        c = SUITE.cases[cid]
        g = c["turns"][0]["calls"][0]
        text = g["args"][key]["equals"]
        assert "\nBEGIN\n" + text + "\nEND" in c["messages"][0]["content"], cid
        assert g["canonical"][key] == text
    code = SUITE.cases["code.multiline"]["turns"][0]["calls"][0]["canonical"]["content"]
    bs = chr(92)
    for piece in ('"', "'", bs + "'", bs + bs, bs + "d", bs + "t", bs + "n", "{", "}", '"""'):
        assert piece in code, piece
    text = SUITE.cases["code.json_text"]["turns"][0]["calls"][0]["canonical"]["content"]
    for piece in (bs + "u00e9", bs + bs, bs + '"'):
        assert piece in text, piece


def test_each_special_token_comes_from_the_research():
    research = (ROOT / "Research" / "open-weight-harness-research.md").read_text(encoding="utf-8")
    for token in qs1.SPECIAL_TOKENS:
        assert token in research, token
    leak = next(line for line in research.splitlines() if line.startswith("- **Leak recovery:**"))
    tc_7_4 = re.findall(r"`([^`]+)`", leak.split(" contains ", 1)[1])
    assert len(tc_7_4) == 6, tc_7_4
    for listed in tc_7_4:      # each of TC 7.4's six is caught
        assert qs1.find_tokens(listed), listed


def test_the_version_names_the_case_file_and_the_judge(tmp_path):
    major, cases_hash, code_hash = QS1.version.split(".")
    assert major == "1"
    assert cases_hash == qs1._sha12(qs1.CASES_PATH)
    assert code_hash == qs1._sha12(Path(qs1.__file__))
    lf, crlf = tmp_path / "lf", tmp_path / "crlf"
    lf.write_bytes(b"a\nb\n")
    crlf.write_bytes(b"a\r\nb\r\n")
    assert qs1._sha12(lf) == qs1._sha12(crlf)
