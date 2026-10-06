"""The agent loop: a model works with tools, as a verifier works, and its tool
calls run in the sandbox.

run_agent() reaches the model only through Context.chat, which meters every
call and stops at the suite's caps. Each turn:
1. the turn and run-time budgets are checked;
2. Context.chat is sent a new list of the messages, the same tool declarations
   every turn (TC §7.7), and no tool_choice, which thinking mode refuses with a
   400 (D10);
3. the model's turn is appended exactly as it came, through
   assistant_message(turn, tools_in_request=True): every request carries the
   tools, so every earlier turn goes back with its reasoning_content (D8). The
   loop never writes an assistant turn of its own, and never a tool call the
   model did not make (D9);
4. its calls run in order, one tool message for each, in the same order
   (TC §7.7). A turn without a call gets a reminder, a user message, up to
   `nudges` times; then the run ends as unreported.

How a run ends, and what it is recorded as:
- reported: a tool that ends the run was called with valid arguments. Its
  arguments are the report, and calls after it in that turn are not run;
- unreported: the model stopped calling tools after its reminders;
- stopped: a budget the harness sets ended it, and the budget is named: turns,
  run_seconds, caps (Context's token caps, with P0's message), peak,
  malformed_retries (the 4th malformed call in a row, by default), or
  scratch_bytes;
- error: the sandbox failed or went away; the model call failed (a provider
  error, a transport failure, a reply not whole); the reply carried a
  documented provider condition (content_filter, insufficient_system_resource,
  aborted, D10) or a tool call without a usable id; a tool's handler raised; or
  the loop itself raised. When Context has set stop_reason, the outcome is its
  stop_kind, and the runner stops the batch whatever this returns.
The loop starts the sandbox before the first call and stops it in a finally
block, so the container is removed on every path. run_agent never raises: every
ending is an AgentResult. item_result() maps stopped and error to those statuses
and never asks the suite's judge about them, so a run a budget stopped is never
scored as "found nothing".

What is recorded:
- every model call and reply: Context.calls, in the local transcript;
- every tool execution, turn, reminder, the sandbox's start and stop and the
  scratch's files: AgentResult.log, which item_result() puts in ItemResult.local,
  so it reaches the local transcript only (P0, 0692de3);
- a summary in ItemResult.data, which the published record holds: counts, the
  budgets, the image and its id, the mounts' targets and labels, the limits, and
  whether the container was removed. No tool output, no model text, no host path.

Limits, each stated by the behaviour it concedes:
- the time budget is checked between calls, so a run can pass it by one model
  call and one tool call;
- the scratch's size is checked after each turn, so a turn can pass it by what
  its calls write within their limits;
- the calls of one turn run one after another, never in parallel.
"""
from __future__ import annotations

import secrets
import time
from dataclasses import asdict, dataclass, field
from typing import Callable

from ..client import ProviderError
from ..providers import deepseek
from ..suite import BatchStopping, CapReached, Context, ItemResult, PeakReached, RunStopped
from .budgets import Budgets
from .sandbox import SandboxDied, SandboxError
from .tools import Tool, ToolEnv, check_tools, find_leaks, format_result, parse_arguments

VERSION = "agent-1"
NUDGE = ("You did not call a tool. Continue your work with the tools, or call {report} to end "
         "the run with your report.")
PROVIDER_CONDITIONS = frozenset({"content_filter", "insufficient_system_resource", "aborted"})
JUDGED = frozenset({"pass", "fail", "error", "refused", "skipped"})


@dataclass
class AgentResult:
    outcome: str = "error"               # reported | unreported | stopped | error
    budget: str | None = None            # which budget stopped the run
    cause: str | None = None             # why it stopped or failed, redacted
    report: dict | None = None
    report_tool: str | None = None
    final_content: str | None = None     # the last turn's content, for an unreported run
    turns: int = 0
    tool_calls: dict = field(default_factory=dict)   # executed calls, by tool
    malformed: int = 0
    timeouts: int = 0
    nudges: int = 0
    leaks: int = 0
    provider_condition: str | None = None
    elapsed_s: float = 0.0
    budgets: dict = field(default_factory=dict)
    sandbox: dict = field(default_factory=dict)
    scratch: dict = field(default_factory=dict)
    log: list = field(default_factory=list)

    def detail(self) -> str:
        if self.outcome == "stopped":
            return f"stopped by the {self.budget} budget: {self.cause}"
        if self.outcome == "error":
            return self.cause or "error"
        if self.outcome == "reported":
            return f"reported through {self.report_tool}"
        return "ended without a report"

    def summary(self) -> dict:
        """What the published record holds: no tool output, no model text, no
        host path."""
        sb = self.sandbox
        return {
            "version": VERSION, "outcome": self.outcome, "budget": self.budget, "cause": self.cause,
            "turns": self.turns, "tool_calls": dict(self.tool_calls), "malformed": self.malformed,
            "timeouts": self.timeouts, "nudges": self.nudges, "leaks": self.leaks,
            "provider_condition": self.provider_condition, "elapsed_s": round(self.elapsed_s, 1),
            "budgets": self.budgets,
            "sandbox": {k: sb.get(k) for k in ("kind", "image", "image_id", "python", "git", "mounts",
                                               "scratch", "limits", "running_at_start", "removed")
                        if k in sb},
            "scratch": self.scratch,
        }

    def item_result(self, judge: Callable[["AgentResult"], tuple[str, str]] | None = None) -> ItemResult:
        """The run's ItemResult. A stopped or errored run is recorded as such,
        and the judge is never asked about it; a reported or unreported run's
        status and detail are the suite's judge's."""
        local = {"agent": {"version": VERSION, "log": self.log, "report": self.report,
                           "final_content": self.final_content}}
        data = {"agent": self.summary()}
        if self.outcome in ("stopped", "error"):
            return ItemResult(self.outcome, self.detail(), data, local=local)
        if judge is None:
            raise ValueError("a reported or unreported run needs the suite's judge")
        status, detail = judge(self)
        if status not in JUDGED:
            raise ValueError(f"a judge may return {sorted(JUDGED)}, not {status!r}")
        return ItemResult(status, detail, data, local=local)


def run_agent(ctx: Context, *, messages: list[dict], tools: list[Tool], sandbox, budgets: Budgets = Budgets(),
              stream: bool = False, nudge: str | None = None,
              clock: Callable[[], float] = time.monotonic,
              tag: Callable[[], str] = lambda: secrets.token_hex(4)) -> AgentResult:
    """Run one agent through Context.chat, its tool calls in `sandbox`, until it
    reports, stops calling tools, meets a budget, or fails. It never raises."""
    t0 = clock()
    res = AgentResult(budgets=asdict(budgets))
    log = res.log

    def elapsed() -> float:
        return clock() - t0

    def redact(text) -> str:
        text = str(text)
        try:
            text = ctx.client.redact(text)
        except Exception:  # noqa: BLE001 - a redaction must not lose the result
            pass
        return sandbox.redact(text)

    def end(outcome: str, *, budget: str | None = None, cause: str | None = None) -> None:
        res.outcome, res.budget, res.cause = outcome, budget, cause
        if outcome in ("stopped", "error") and ctx.stop_reason:
            # Context's own reason is what stops the batch: record the run as its
            # kind, with that reason beside the loop's.
            res.outcome = ctx.stop_kind or "error"
            if not cause:
                res.cause = ctx.stop_reason
            elif ctx.stop_reason not in cause:
                res.cause = f"{cause}; {ctx.stop_reason}"
            if res.outcome == "error":
                res.budget = None

    started = False
    try:
        try:
            table = check_tools(tools)
        except Exception as e:  # noqa: BLE001 - a suite's bad tool set ends the run, before any call
            end("error", cause=f"the suite's tools are not valid: {e}")
            return res
        reporting = [n for n, (t, _) in table.items() if t.ends_run]
        nudge_text = (nudge or NUDGE).format(report=" or ".join(reporting))
        declarations = [t.declaration() for t, _ in table.values()]
        env = ToolEnv(sandbox=sandbox, budgets=budgets)
        try:
            facts = sandbox.start()
            started = True
        except SandboxError as e:
            started = True     # stop() still runs: start may have left something behind
            end("error", cause=f"the sandbox did not start: {redact(e)}")
            return res
        res.sandbox.update(facts)
        log.append({"kind": "sandbox", "event": "start", "facts": facts})

        msgs = [dict(m) for m in messages]
        streak = 0
        while True:
            if res.turns >= budgets.max_turns:
                end("stopped", budget="turns", cause=f"the run used its {budgets.max_turns} turns")
                break
            if elapsed() >= budgets.max_run_seconds:
                end("stopped", budget="run_seconds",
                    cause=f"the run used its {budgets.max_run_seconds:g} s")
                break
            kw: dict = {"tools": declarations}
            if stream:
                kw["stream"] = True
            if budgets.max_tokens_per_turn:
                kw["max_tokens"] = budgets.max_tokens_per_turn
            try:
                turn = ctx.chat(list(msgs), **kw)
            except CapReached as e:
                end("stopped", budget="caps", cause=str(e))
                break
            except PeakReached as e:
                end("stopped", budget="peak", cause=str(e))
                break
            except BatchStopping as e:
                end("error", cause=str(e))
                break
            except RunStopped as e:
                end("stopped", budget="harness", cause=str(e))
                break
            except ProviderError as e:
                end("error", cause=f"the provider returned HTTP {e.status}: {redact(e.body)[:300]}")
                break
            except Exception as e:  # noqa: BLE001 - every failed call is recorded, then the run ends
                end("error", cause=f"the model call failed: {type(e).__name__}: {redact(e)[:300]}")
                break
            res.turns += 1
            msgs.append(deepseek.assistant_message(turn, tools_in_request=True))
            leaks = find_leaks(turn.content)
            res.leaks += len(leaks)
            sent = ctx.calls[-1]["request"] if ctx.calls else {}
            log.append({"kind": "turn", "n": res.turns, "finish_reason": turn.finish_reason,
                        "tool_calls": [{"id": c.get("id"), "name": (c.get("function") or {}).get("name")}
                                       for c in turn.tool_calls],
                        "content_chars": len(turn.content or ""),
                        "reasoning_chars": len(turn.reasoning_content or ""),
                        "leaks": leaks, "max_tokens_sent": sent.get("max_tokens"),
                        "usage": vars(turn.usage), "t": round(elapsed(), 3)})
            if turn.finish_reason in PROVIDER_CONDITIONS:
                res.provider_condition = turn.finish_reason
                end("error", cause=f"the reply ended with {turn.finish_reason}, a provider "
                                   f"condition DeepSeek documents (D10), not the model's failure")
                break
            if not turn.tool_calls:
                if res.nudges < budgets.nudges:
                    res.nudges += 1
                    msgs.append({"role": "user", "content": nudge_text})
                    log.append({"kind": "nudge", "after_turn": res.turns, "text": nudge_text})
                    continue
                res.final_content = turn.content
                end("unreported", cause="the model stopped calling tools")
                break
            ids = [c.get("id") for c in turn.tool_calls]
            if any(not isinstance(i, str) or not i for i in ids) or len(set(ids)) != len(ids):
                end("error", cause="the reply's tool calls lack ids or repeat one, so no result can "
                                   "answer them: a provider defect")
                break

            ended = False
            for i, call in enumerate(turn.tool_calls):
                fn = call.get("function") or {}
                name, raw = fn.get("name"), fn.get("arguments")
                entry = {"kind": "tool", "turn": res.turns, "index": i, "id": call["id"], "name": name,
                         "arguments": raw}
                if ended:
                    log.append({**entry, "status": "not executed", "error": "the run had ended"})
                    continue
                if elapsed() >= budgets.max_run_seconds:
                    end("stopped", budget="run_seconds",
                        cause=f"the run used its {budgets.max_run_seconds:g} s")
                    ended = True
                    log.append({**entry, "status": "not executed", "error": "the run had ended"})
                    continue
                if i >= budgets.max_calls_per_turn:
                    content = (f"[{name} {call['id']}] cancelled: a turn may make at most "
                               f"{budgets.max_calls_per_turn} calls")
                    msgs.append({"role": "tool", "tool_call_id": call["id"], "content": content})
                    log.append({**entry, "status": "cancelled", "sent": content})
                    continue
                tool, validator = table.get(name, (None, None))
                if tool is None:
                    args, err = None, (f"there is no tool named {name!r}; the tools are "
                                       f"{', '.join(sorted(table))}")
                else:
                    args, err = parse_arguments(raw, validator)
                if err is not None:
                    streak += 1
                    res.malformed += 1
                    if streak > budgets.malformed_retries:
                        end("stopped", budget="malformed_retries",
                            cause=f"{streak} malformed calls in a row; the last: {err}")
                        ended = True
                        log.append({**entry, "status": "malformed", "error": err})
                        continue
                    content = f"[{name} {call['id']}] error: {err}"
                    msgs.append({"role": "tool", "tool_call_id": call["id"], "content": content})
                    log.append({**entry, "status": "malformed", "error": err, "sent": content})
                    continue
                streak = 0
                try:
                    outcome = tool.handler(args, env)
                except SandboxError as e:
                    end("error", cause=f"the sandbox failed during {name}: {redact(e)[:300]}")
                    ended = True
                    log.append({**entry, "parsed": args, "status": "error", "error": res.cause})
                    continue
                except Exception as e:  # noqa: BLE001 - a broken tool must not be the model's failure
                    end("error", cause=f"the tool {name} failed: {type(e).__name__}: {redact(e)[:300]}")
                    ended = True
                    log.append({**entry, "parsed": args, "status": "error", "error": res.cause})
                    continue
                content, info = format_result(name, call["id"], outcome, budgets.max_output_chars, tag())
                msgs.append({"role": "tool", "tool_call_id": call["id"], "content": content})
                ex = outcome.exec
                res.tool_calls[name] = res.tool_calls.get(name, 0) + 1
                if ex is not None and ex.timed_out:
                    res.timeouts += 1
                log.append({**entry, "parsed": args,
                            "status": ("refused" if outcome.refused else
                                       "timed out" if ex is not None and ex.timed_out else "ok"),
                            "exit_code": ex.exit_code if ex else None,
                            "duration_s": ex.duration_s if ex else None,
                            "output_bytes": ex.total_bytes if ex else None,
                            "output_lines": ex.total_lines if ex else None, **info, "sent": content})
                if tool.ends_run:
                    res.report, res.report_tool = args, name
                    end("reported")
                    ended = True
            if ended:
                break
            used = sandbox.scratch_bytes()
            if used > budgets.max_scratch_bytes:
                end("stopped", budget="scratch_bytes",
                    cause=f"the scratch holds {used} bytes, over its {budgets.max_scratch_bytes}")
                break
    except Exception as e:  # noqa: BLE001 - the loop's own failure is recorded, never raised
        end("error", cause=f"the agent loop failed: {type(e).__name__}: {redact(e)[:300]}")
    finally:
        if started:
            try:
                stop = sandbox.stop()
            except Exception as e:  # noqa: BLE001
                stop = {"removed": False, "detail": f"{type(e).__name__}: {redact(e)[:300]}"}
            res.sandbox["removed"] = bool(stop.get("removed"))
            log.append({"kind": "sandbox", "event": "stop", **stop})
            try:
                files = sandbox.scratch_manifest()
                res.scratch = {"files": len(files), "bytes": sum(f["bytes"] for f in files)}
                log.append({"kind": "scratch", "files": files})
            except Exception as e:  # noqa: BLE001
                log.append({"kind": "scratch", "error": f"{type(e).__name__}"})
        res.elapsed_s = elapsed()
        log.append({"kind": "end", "outcome": res.outcome, "budget": res.budget, "cause": res.cause,
                    "elapsed_s": round(res.elapsed_s, 3)})
    return res
