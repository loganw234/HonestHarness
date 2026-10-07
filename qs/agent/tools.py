"""The agent's tools: the four built-ins, a suite's own, the arguments' check,
and how a tool's output reaches the model.

Tool output is untrusted (TC §7.9). What the model gets back is:
- a header the harness writes: the tool, the call, the exit code, and the
  output's size in bytes and lines before any truncation;
- the output between two delimiter lines that carry a random tag for each call,
  so no text inside can close them;
- with control tokens replaced by "[control token removed]": TC §7.9's and
  §7.4's, DeepSeek's fullwidth-bar tokens and DSML tag prefixes (TC §3.4), ASCII
  <|name|> tokens, and the lookalike <||DSML||;
- cut to max_output_chars: its first three quarters and its last quarter, with
  the cut stated.
The loop never parses tool output, so nothing in it can change a tool, a budget,
a mount or a permission.

Malformed arguments are answered as tool-result errors that name what failed:
the JSON parse error with its position, or a schema violation's JSON pointer and
what the schema expected (TC §7.4, step 6). Arguments are never repaired: a
malformed call is the model's, and is recorded as it was sent. The error may
quote the model's text, so it goes to the model and the local log only; a
published record names only its kind, from MALFORMED_KINDS.

Limits, each stated by the behaviour it concedes:
- a control token in a form not listed passes; all other content is verbatim;
- the delimiters mark output as data; they do not stop its text addressing the
  model;
- a token split across the point where the output was cut is not seen;
- write_file content holding a lone surrogate (JSON's "\\ud800" escape, say)
  cannot be encoded as UTF-8: the handler raises UnicodeEncodeError, and the
  loop ends the run as error, recording a model-made input as a broken tool.
"""
from __future__ import annotations

import json
import posixpath
import re
from dataclasses import dataclass
from typing import Callable

from jsonschema import Draft202012Validator
from jsonschema.exceptions import best_match

from .budgets import Budgets
from .sandbox import RO_ROOT, SCRATCH, WORK, ExecResult

TOOL_NAME = re.compile(r"[A-Za-z0-9_-]{1,64}")   # TC §7.6; DeepSeek allows 128 (D10)
REMOVED = "[control token removed]"
CONTROL_TOKENS = re.compile(
    r"</?｜DSML｜"                          # DeepSeek V4 and V4.1 DSML tag prefixes (TC §3.4)
    r"|</?\|\|DSML\|\|"                     # a lookalike of them (TC §3.4)
    r"|<｜[^｜<>\n]{0,64}｜>"                # DeepSeek's fullwidth-bar tokens, such as <｜tool▁sep｜>
    r"|<\|[A-Za-z0-9_:./-]{1,64}\|>"         # ASCII special tokens: <|im_start|>, <|start|>, ...
    r"|</?tool_call>|</?minimax:tool_call>|\[TOOL_CALLS\]"   # TC §7.4 and §7.9
)
JSON_TYPES = {dict: "an object", list: "an array", str: "a string", int: "a number",
              float: "a number", bool: "a boolean", type(None): "null"}


@dataclass(frozen=True)
class Tool:
    """A tool the model may call. The handler gets the checked arguments and
    the run's ToolEnv, and returns a ToolOutcome. A tool that ends the run, such
    as report, makes its arguments the run's report."""
    name: str
    description: str
    parameters: dict
    handler: Callable[[dict, "ToolEnv"], "ToolOutcome"]
    ends_run: bool = False

    def declaration(self) -> dict:
        return {"type": "function", "function": {"name": self.name, "description": self.description,
                                                 "parameters": self.parameters}}


@dataclass
class ToolOutcome:
    """exec is the sandbox's result when the tool ran a process; text is the
    harness's own message when it did not. refused marks a call the harness
    turned down."""
    exec: ExecResult | None = None
    text: str | None = None
    refused: bool = False


@dataclass
class ToolEnv:
    sandbox: object
    budgets: Budgets


# -- the tools' table --------------------------------------------------------------
def check_tools(tools: list[Tool]) -> dict[str, tuple[Tool, Draft202012Validator]]:
    """Each tool's name and schema, checked before the run's first call."""
    table: dict = {}
    for t in tools:
        if not isinstance(t, Tool):
            raise ValueError(f"{t!r} is not a Tool")
        if not TOOL_NAME.fullmatch(t.name):
            raise ValueError(f"the tool name {t.name!r} is not 1 to 64 letters, digits, '_' or '-'")
        if t.name in table:
            raise ValueError(f"two tools are named {t.name!r}")
        if not isinstance(t.parameters, dict) or t.parameters.get("type") != "object":
            raise ValueError(f"the tool {t.name!r} needs a JSON schema with an object at its root")
        Draft202012Validator.check_schema(t.parameters)
        table[t.name] = (t, Draft202012Validator(t.parameters))
    if not any(t.ends_run for t, _ in table.values()):
        raise ValueError("no tool ends the run: give report, or a suite's own")
    return table


def parse_arguments(raw, validator: Draft202012Validator) -> tuple[dict | None, str | None, str | None]:
    """(arguments, None, None), or (None, what failed, its kind).

    What failed is for the model to read, and may quote what the model sent.
    Its kind is one of a fixed few, MALFORMED_KINDS, and is all a published
    record may say about it. Everything json or the schema check raises on an
    argument string is answered here, including JSON nested too deeply for the
    parser and numbers too long for it to read."""
    if not isinstance(raw, str):
        return None, "the call carried no arguments; send a JSON object, {} for none", "no arguments"
    try:
        args = json.loads(raw)
    except json.JSONDecodeError as e:
        return None, f"the arguments are not valid JSON: {e}", "not valid JSON"
    except RecursionError:
        return None, "the arguments are nested too deeply to read", "nested too deeply"
    except ValueError as e:      # such as a number with more digits than Python will convert
        return None, f"the arguments cannot be read: {e}", "not valid JSON"
    if not isinstance(args, dict):
        return (None, f"the arguments must be a JSON object, not {JSON_TYPES.get(type(args), 'that')}",
                "not a JSON object")
    try:
        err = best_match(validator.iter_errors(args))
    except RecursionError:
        return None, "the arguments are nested too deeply to check", "nested too deeply"
    if err is not None:
        pointer = "/" + "/".join(str(p) for p in err.absolute_path)
        expected = json.dumps(err.validator_value, ensure_ascii=False)
        if len(expected) > 200:
            expected = expected[:200] + "..."
        return (None, f"at {pointer}: {err.message} (the schema's {err.validator}: {expected})",
                "against the schema")
    return args, None, None


MALFORMED_KINDS = frozenset({"no arguments", "not valid JSON", "nested too deeply", "not a JSON object",
                             "against the schema", "an unknown tool"})


# -- untrusted output ----------------------------------------------------------------
def strip_control(text: str) -> tuple[str, int]:
    out, n = CONTROL_TOKENS.subn(REMOVED, text)
    return out, n


def find_leaks(text: str | None) -> list[str]:
    """Control tokens in a model's own content: a provider defect to record
    (TC §7.4), never something to edit."""
    return sorted(set(CONTROL_TOKENS.findall(text or "")))


def render_output(ex: ExecResult, max_chars: int) -> tuple[str, dict]:
    """The text the model sees, and what was done to it."""
    head, n1 = strip_control(ex.head.decode("utf-8", "replace"))
    tail, n2 = strip_control(ex.tail.decode("utf-8", "replace"))
    whole = head + tail if ex.complete else None
    if whole is not None and len(whole) <= max_chars:
        return whole, {"truncated": False, "control_tokens_replaced": n1 + n2,
                       "shown_chars": len(whole)}
    keep_head = max_chars * 3 // 4
    keep_tail = max_chars - keep_head
    first = (whole if whole is not None else head)[:keep_head]
    last = (whole if whole is not None else tail)[-keep_tail:] if keep_tail else ""
    marker = (f"\n[... the middle of the output is not shown: it was {ex.total_bytes} bytes and "
              f"{ex.total_lines} lines; shown are its first {len(first)} and last {len(last)} "
              f"characters ...]\n")
    return first + marker + last, {"truncated": True, "control_tokens_replaced": n1 + n2,
                                   "shown_chars": len(first) + len(last)}


def format_result(tool: str, call_id: str, outcome: ToolOutcome, max_chars: int,
                  tag: str) -> tuple[str, dict]:
    """The tool message's content, and the facts the log keeps about it."""
    if outcome.exec is None:
        return f"[{tool} {call_id}] {outcome.text}", {"truncated": False,
                                                      "control_tokens_replaced": 0}
    ex = outcome.exec
    shown, info = render_output(ex, max_chars)
    status = (f"timed out after its {ex.limit_s:g} s limit and was killed" if ex.timed_out
              else f"exit code {ex.exit_code}")
    header = f"[{tool} {call_id}] {status}; output {ex.total_bytes} bytes, {ex.total_lines} lines"
    if info["truncated"]:
        header += f"; shown truncated to {info['shown_chars']} characters"
    if info["control_tokens_replaced"]:
        header += f"; {info['control_tokens_replaced']} control tokens replaced"
    if ex.note:
        header += f"\n[sandbox: {ex.note}]"
    return f"{header}\n<<<output {tag}>>>\n{shown}\n<<<end output {tag}>>>", info


# -- paths -----------------------------------------------------------------------------
def resolve(path: str, base: str) -> str:
    return posixpath.normpath(path if path.startswith("/") else posixpath.join(base, path))


def in_scratch(path: str) -> bool:
    return path == SCRATCH or path.startswith(SCRATCH + "/")


# -- the built-ins -----------------------------------------------------------------------
def _shell(args: dict, env: ToolEnv) -> ToolOutcome:
    return ToolOutcome(exec=env.sandbox.shell(args["command"], env.budgets.call_timeout_seconds))


def _read_file(args: dict, env: ToolEnv) -> ToolOutcome:
    path = resolve(args["path"], WORK)
    return ToolOutcome(exec=env.sandbox.read_file(path, args.get("start_line", 1),
                                                  args.get("line_count", 0),
                                                  env.budgets.call_timeout_seconds))


def _write_file(args: dict, env: ToolEnv) -> ToolOutcome:
    path = resolve(args["path"], SCRATCH)
    if not in_scratch(path) or path == SCRATCH:
        return ToolOutcome(text=f"refused: write_file writes only to files under {SCRATCH}, "
                                f"and {path} is not one", refused=True)
    return ToolOutcome(exec=env.sandbox.write_file(path, args["content"].encode("utf-8"),
                                                   bool(args.get("append", False)),
                                                   env.budgets.call_timeout_seconds))


def _report(args: dict, env: ToolEnv) -> ToolOutcome:
    return ToolOutcome(text="the report is received, and the run ends")


def builtin_tools(budgets: Budgets = Budgets(), *, report: bool = True) -> list[Tool]:
    """shell, read_file and write_file, and report unless the suite brings its
    own tool that ends the run. Their descriptions state the budgets the run
    holds them to."""
    limit = f"{budgets.call_timeout_seconds:g} s"
    cap = f"{budgets.max_output_chars} characters"
    place = (f"You work in a Linux container with no network. {RO_ROOT}/<name> holds the "
             f"directories you were given, read-only; {SCRATCH} is yours to write, and is kept; "
             f"/tmp is in memory and lost at the end.")
    tools = [
        Tool("shell", f"Run a bash command in {WORK}, as an unprivileged user. {place} Each call "
                      f"is a new shell, so cd and variables do not carry over. stdout and stderr "
                      f"come back together; output longer than {cap} shows its start and end. "
                      f"A call is killed after {limit}.",
             {"type": "object", "properties": {"command": {"type": "string", "minLength": 1,
                                                           "description": "The bash command."}},
              "required": ["command"], "additionalProperties": False},
             _shell),
        Tool("read_file", f"Read a text file, each line prefixed with its number and a colon, "
                          f"as grep -n prints it. A relative path is "
                          f"relative to {WORK}. Give start_line and line_count to read part of "
                          f"a long file; output longer than {cap} shows its start and end.",
             {"type": "object", "properties": {
                 "path": {"type": "string", "minLength": 1},
                 "start_line": {"type": "integer", "minimum": 1},
                 "line_count": {"type": "integer", "minimum": 1}},
              "required": ["path"], "additionalProperties": False},
             _read_file),
        Tool("write_file", f"Write a file under {SCRATCH}, the only place you can write that is "
                           f"kept. A relative path is relative to {SCRATCH}. Set append to add to "
                           f"the end of the file instead of replacing it.",
             {"type": "object", "properties": {
                 "path": {"type": "string", "minLength": 1},
                 "content": {"type": "string"},
                 "append": {"type": "boolean"}},
              "required": ["path", "content"], "additionalProperties": False},
             _write_file),
    ]
    if report:
        tools.append(Tool("report", "End the run with your report. Call it once, when your "
                                    "work is done; nothing after it runs.",
                          {"type": "object", "properties": {"text": {"type": "string",
                                                                     "minLength": 1}},
                           "required": ["text"], "additionalProperties": False},
                          _report, ends_run=True))
    return tools
