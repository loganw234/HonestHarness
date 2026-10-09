"""The agent loop and its sandbox: a model works with tools, as a verifier
works, and every tool call runs in a container with no network.

- loop:     run_agent(), which reaches the model only through Context.chat and
            records every turn and tool execution; AgentResult and its mapping
            to an ItemResult;
- tools:    the built-ins (shell, read_file, write_file, report), a suite's own,
            the arguments' check, and how untrusted output reaches the model;
- sandbox:  DockerSandbox, one container per run, removed on every path;
- scripted: ScriptedSandbox, a stand-in for tests that never runs a process;
- budgets:  the loop's own budgets, beside the suite's token caps.

A suite uses it as P4 will:

    sandbox = DockerSandbox(scratch_dir, [Mount(repo_dir, "repo", "label")])
    result = run_agent(ctx, messages=[...], tools=builtin_tools(budgets),
                       sandbox=sandbox, budgets=budgets)
    return result.item_result(judge)

Each module's docstring states its threat model and its limits.
"""
from .budgets import Budgets
from .loop import NUDGE, VERSION, AgentResult, run_agent
from .sandbox import (IMAGE, DockerSandbox, ExecResult, Limits, Mount, SandboxDied, SandboxError,
                      SandboxUnavailable, docker_status)
from .scripted import ScriptedSandbox
from .tools import Tool, ToolEnv, ToolOutcome, builtin_tools

__all__ = ["AgentResult", "Budgets", "DockerSandbox", "ExecResult", "IMAGE", "Limits", "Mount",
           "NUDGE", "SandboxDied", "SandboxError", "SandboxUnavailable", "ScriptedSandbox", "Tool",
           "ToolEnv", "ToolOutcome", "VERSION", "builtin_tools", "docker_status", "run_agent"]
