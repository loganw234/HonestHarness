import json

import pytest

from qs.providers import deepseek as ds


def test_build_request_thinking_and_effort():
    b = ds.build_request("deepseek-flash", [{"role": "user", "content": "hi"}], thinking=True,
                         effort="high", max_tokens=100)
    assert b["thinking"] == {"type": "enabled"} and b["reasoning_effort"] == "high"
    assert b["max_tokens"] == 100 and "stream" not in b
    b2 = ds.build_request("deepseek-flash", [], thinking=False, effort="high")
    assert b2["thinking"] == {"type": "disabled"} and "reasoning_effort" not in b2


def test_build_request_refuses_unknown_effort():
    with pytest.raises(ValueError):
        ds.build_request("m", [], effort="ultra")


def test_build_request_sends_documented_refusals():
    # A suite testing a refusal must be able to make the request.
    b = ds.build_request("m", [], thinking=True, tools=[{"type": "function"}],
                         tool_choice="required")
    assert b["tool_choice"] == "required"
    assert ds.documented_refusal(True, "required")
    assert ds.documented_refusal(True, {"type": "function", "function": {"name": "f"}})
    assert ds.documented_refusal(False, "required") is None
    assert ds.documented_refusal(True, "auto") is None


def test_sampling_record():
    r = ds.sampling_record(True, 0.2, 0.5)
    assert r["sent"] == {"temperature": 0.2, "top_p": 0.5} and len(r["ignored"]) == 2
    r = ds.sampling_record(False, 0.2, 0.5)
    assert r["ignored"] == ["top_p (fixed at 1.0 in non-thinking mode)"]
    assert ds.sampling_record(False, 0.2, None)["ignored"] == []


def test_parse_usage_deepseek_and_openai_forms():
    u = ds.parse_usage({"prompt_tokens": 100, "prompt_cache_hit_tokens": 80,
                        "prompt_cache_miss_tokens": 20, "completion_tokens": 7,
                        "completion_tokens_details": {"reasoning_tokens": 5}})
    assert (u.cache_hit, u.cache_miss, u.output, u.reasoning) == (80, 20, 7, 5)
    u = ds.parse_usage({"prompt_tokens": 100, "prompt_tokens_details": {"cached_tokens": 30},
                        "completion_tokens": 7})
    assert (u.cache_hit, u.cache_miss, u.output) == (30, 70, 7)
    assert ds.parse_usage(None).prompt == 0


def test_parse_response():
    t = ds.parse_response({"model": "deepseek-flash", "system_fingerprint": "fp_1",
                           "choices": [{"message": {"content": "hi", "reasoning_content": "r",
                                                    "tool_calls": [{"id": "c1"}]},
                                        "finish_reason": "tool_calls"}],
                           "usage": {"prompt_tokens": 3, "completion_tokens": 2}})
    assert t.content == "hi" and t.reasoning_content == "r" and t.tool_calls == [{"id": "c1"}]
    assert t.finish_reason == "tool_calls" and t.model == "deepseek-flash"
    assert t.system_fingerprint == "fp_1" and t.usage.output == 2


def test_parse_stream_skips_keepalive_and_takes_usage_from_last_chunk():
    lines = [
        "",
        ": keep-alive",
        "data: " + json.dumps({"model": "m", "system_fingerprint": "fp",
                               "choices": [{"delta": {"reasoning_content": "thin"}}]}),
        "data: " + json.dumps({"choices": [{"delta": {"reasoning_content": "king"}}]}),
        "data: " + json.dumps({"choices": [{"delta": {"content": "an"}}]}),
        ": keep-alive",
        "data: " + json.dumps({"choices": [{"delta": {"content": "swer"},
                                            "finish_reason": "stop"}],
                               "usage": {"prompt_tokens": 9, "prompt_cache_hit_tokens": 4,
                                         "prompt_cache_miss_tokens": 5,
                                         "completion_tokens": 6}}),
        "data: [DONE]",
    ]
    t = ds.parse_stream(lines)
    assert t.reasoning_content == "thinking" and t.content == "answer"
    assert t.finish_reason == "stop" and t.model == "m" and t.system_fingerprint == "fp"
    assert (t.usage.cache_hit, t.usage.cache_miss, t.usage.output) == (4, 5, 6)


def test_parse_stream_accumulates_tool_calls_by_index():
    def d(tc):
        return "data: " + json.dumps({"choices": [{"delta": {"tool_calls": [tc]}}]})
    lines = [d({"index": 0, "id": "a", "function": {"name": "get_", "arguments": "{\"x\""}}),
             d({"index": 1, "id": "b", "function": {"name": "other", "arguments": "{}"}}),
             d({"index": 0, "function": {"name": "time", "arguments": ": 1}"}}),
             "data: " + json.dumps({"choices": [{"delta": {}, "finish_reason": "tool_calls"}],
                                    "usage": {"prompt_tokens": 9, "completion_tokens": 6}}),
             "data: [DONE]"]
    t = ds.parse_stream(lines)
    assert [c["id"] for c in t.tool_calls] == ["a", "b"]
    assert t.tool_calls[0]["function"] == {"name": "get_time", "arguments": "{\"x\": 1}"}


def test_assistant_message_passes_reasoning_back_only_with_tools():
    t = ds.Turn(content="c", reasoning_content="r", tool_calls=[{"id": "x"}])
    m = ds.assistant_message(t, tools_in_request=True)
    assert m["reasoning_content"] == "r" and m["tool_calls"] == [{"id": "x"}]
    assert "reasoning_content" not in ds.assistant_message(t, tools_in_request=False)


def test_finish_reasons_include_deepseeks_own():
    assert {"insufficient_system_resource", "aborted"} <= ds.FINISH_REASONS


def test_max_tokens_is_deepseeks_documented_limit():
    assert ds.MAX_TOKENS == 393216


def test_a_reply_without_usage_raises():
    with pytest.raises(ds.IncompleteReply):
        ds.parse_response({"choices": [{"message": {"content": "x"}, "finish_reason": "stop"}]})


def test_a_stream_cut_short_raises():
    content = "data: " + json.dumps({"choices": [{"delta": {"content": "a"}}]})
    usage = "data: " + json.dumps({"choices": [{"delta": {}, "finish_reason": "stop"}],
                                   "usage": {"prompt_tokens": 1, "completion_tokens": 1}})
    with pytest.raises(ds.IncompleteReply):
        ds.parse_stream([content, usage])               # no [DONE]
    with pytest.raises(ds.IncompleteReply):
        ds.parse_stream([content, "data: [DONE]"])      # no usage
    assert ds.parse_stream([content, usage, "data: [DONE]"]).content == "a"
