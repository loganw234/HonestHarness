"""The loop end to end through P0's runner: what the published record holds, what
stays in the local transcript, and how a budget stop or a provider failure is
recorded."""
import importlib.util
import json
from decimal import Decimal
from pathlib import Path

from qs import record as rec
from qs.agent import Budgets, ScriptedSandbox, builtin_tools, run_agent
from qs.agent.scripted import ScriptedModel, result, tool_call
from qs.fake import FakeServer, error, reply
from qs.guard import SpendGuard
from qs.registry import Endpoint
from qs.suite import Caps, Item, Runner, Suite

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("hh_check_runner", ROOT / "tools" / "check.py")
check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check)

OUTPUT = "TOOL-OUTPUT-KEPT-LOCAL"


def calls(*tcs, finish="tool_calls"):
    return reply(None, reasoning="thinking", tool_calls=list(tcs), finish=finish, usage=(0, 300, 40, 10))


class AgentSuite(Suite):
    """A suite that runs the loop once per item, with the scripted sandbox."""
    name = "agentsuite"
    version = "test-1"
    caps = Caps(max_prompt_tokens=200_000, max_output_tokens=20_000, max_call_prompt_tokens=50_000)

    def __init__(self, n=1, budgets=Budgets()):
        self.n, self.budgets = n, budgets

    def items(self):
        return [Item(f"i{k}") for k in range(self.n)]

    def run_item(self, ctx, item):
        box = ScriptedSandbox(shell=lambda c: result(0, OUTPUT + "\n"))
        res = run_agent(ctx, messages=[{"role": "user", "content": "work, then report"}],
                        tools=builtin_tools(self.budgets), sandbox=box, budgets=self.budgets)
        return res.item_result(lambda r: ("pass", "reported") if r.outcome == "reported"
                               else ("fail", "no report"))


def run_batch(tmp_path, prices, clock, model, suite):
    with FakeServer(model, prices=prices, clock=clock) as url:
        ep = Endpoint(name="fake", provider="deepseek", base_url=url, model="deepseek-flash",
                      price_table="prices/deepseek-2026-10-06.json", key_env=None)
        guard = SpendGuard(Decimal("250"), tmp_path / "records" / "spend.jsonl")
        runner = Runner(ep, prices, guard, records_dir=tmp_path / "records",
                        transcripts_dir=tmp_path / "transcripts", clock=clock)
        summary = runner.run_batch(suite)
    return summary


def lines(p):
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def transcript(tmp_path, summary, item="i0"):
    p = tmp_path / "transcripts" / summary["batch"] / f"{summary['batch']}.{item}.r0.json"
    return json.loads(p.read_text(encoding="utf-8"))


def test_a_loop_run_is_recorded_and_its_log_stays_in_the_transcript(tmp_path, prices, off_peak_clock):
    model = ScriptedModel(calls(tool_call("c1", "shell", {"command": "ls"})),
                          calls(tool_call("c2", "report", {"text": "REPORT-TEXT"})))
    s = run_batch(tmp_path, prices, off_peak_clock, model, AgentSuite())
    assert s["runs"] == 1 and s["stopped_for"] is None and s["reconciliation"] == "ok"
    path = tmp_path / "records" / "runs" / "agentsuite.jsonl"
    record = lines(path)[0]
    rec.validate(record)
    assert record["outcome"]["status"] == "pass" and record["calls"] == 2
    agent = record["outcome"]["data"]["agent"]
    assert agent["outcome"] == "reported" and agent["tool_calls"] == {"shell": 1, "report": 1}
    text = path.read_text(encoding="utf-8")
    assert OUTPUT not in text and "REPORT-TEXT" not in text and check.findings(text) == []
    local = transcript(tmp_path, s)["result"]["local"]["agent"]
    assert [e["kind"] for e in local["log"]].count("tool") == 2 and local["report"] == {"text": "REPORT-TEXT"}
    assert any(OUTPUT in (e.get("sent") or "") for e in local["log"])
    assert len(lines(tmp_path / "records" / "spend.jsonl")) == 3      # the probe and two calls


def test_each_request_the_fake_received_equals_the_transcripts(tmp_path, prices, off_peak_clock):
    model = ScriptedModel(calls(tool_call("c1", "shell", {"command": "ls"})),
                          calls(tool_call("c2", "shell", {"command": "pwd"})),
                          calls(tool_call("c3", "report", {"text": "done"})))
    s = run_batch(tmp_path, prices, off_peak_clock, model, AgentSuite())
    sent = [c["request"] for c in transcript(tmp_path, s)["calls"]]
    assert sent == model.bodies and [len(b["messages"]) for b in sent] == [1, 3, 5]


def test_a_budget_stop_is_recorded_as_stopped_with_its_budget(tmp_path, prices, off_peak_clock):
    model = ScriptedModel(*[calls(tool_call(f"c{i}", "shell", {"command": "ls"})) for i in range(5)])
    s = run_batch(tmp_path, prices, off_peak_clock, model, AgentSuite(budgets=Budgets(max_turns=2)))
    record = lines(tmp_path / "records" / "runs" / "agentsuite.jsonl")[0]
    assert record["outcome"]["status"] == "stopped" and "turns budget" in record["outcome"]["detail"]
    assert record["outcome"]["data"]["agent"]["budget"] == "turns" and record["stop_reason"] is None
    assert s["stopped_for"] is None


def test_a_provider_failure_mid_run_is_an_error_and_stops_the_batch(tmp_path, prices, off_peak_clock):
    model = ScriptedModel(calls(tool_call("c1", "shell", {"command": "ls"})), error(503, "busy"))
    s = run_batch(tmp_path, prices, off_peak_clock, model, AgentSuite(n=2))
    records = lines(tmp_path / "records" / "runs" / "agentsuite.jsonl")
    assert len(records) == 1 and s["runs"] == 1 and "HTTP 503" in s["stopped_for"]
    assert records[0]["outcome"]["status"] == "error" and "HTTP 503" in records[0]["stop_reason"]
    assert transcript(tmp_path, s)["result"]["local"]["agent"]["log"][-1]["outcome"] == "error"
