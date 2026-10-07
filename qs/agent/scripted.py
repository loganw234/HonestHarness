"""A stand-in for the sandbox that never runs a process.

For tests, P2's own and any suite's that builds on the loop. Its files live in a
dict, and its shell answers from a script. Where the loop can tell, it behaves as
the container does:
- a write outside /work/scratch is refused as a read-only filesystem refuses it;
- output is kept and counted the same way, head and tail;
- a responder may report a timeout, or raise SandboxDied, to stand for a
  container that went away.
"""
from __future__ import annotations

import json
from typing import Callable

from .sandbox import RO_ROOT, SCRATCH, Capture, ExecResult, SandboxDied, SandboxError


def tool_call(call_id: str, name: str, arguments) -> dict:
    """A tool call as a reply carries it. arguments is a dict, or a raw string
    to send as it is, malformed or not."""
    raw = arguments if isinstance(arguments, str) else json.dumps(arguments)
    return {"id": call_id, "type": "function", "function": {"name": name, "arguments": raw}}


class ScriptedModel:
    """A responder for qs.fake.FakeServer: it answers the runner's identity
    probe, then each chat request with the next reply in its script. A reply is
    a FakeReply, or a function of the request body that returns one. When the
    script runs out it answers 500, which stops the batch, so a test sees it."""

    def __init__(self, *replies):
        self.replies = list(replies)
        self.bodies: list[dict] = []

    def __call__(self, body: dict):
        from ..fake import error, reply
        from ..identity import PROBE_MESSAGES
        if body.get("messages") == PROBE_MESSAGES:
            return reply("ready")
        self.bodies.append(body)
        if not self.replies:
            return error(500, "the script ran out")
        r = self.replies.pop(0)
        return r(body) if callable(r) else r


def result(exit_code: int | None, output: bytes | str = b"", *, timed_out: bool = False,
           limit_s: float = 0.0) -> ExecResult:
    """An ExecResult as the real sandbox would keep it: head and tail, every byte
    and line counted."""
    cap = Capture()
    cap.feed(output.encode("utf-8") if isinstance(output, str) else output)
    return cap.result(exit_code, timed_out=timed_out, limit_s=limit_s)


class ScriptedSandbox:
    kind = "scripted"
    scratch_target = SCRATCH

    def __init__(self, shell: Callable[[str], ExecResult | tuple] | None = None,
                 files: dict | None = None, mounts: tuple[str, ...] = ("repo",)):
        self.responder = shell or (lambda command: result(0))
        self.files = {k: (v.encode("utf-8") if isinstance(v, str) else v)
                      for k, v in (files or {}).items()}
        self.mount_names = tuple(mounts)
        self.started = self.stopped = self.dead = False
        self.lifetime_s: float | None = None          # what start() was given
        self.commands: list[tuple[str, str]] = []    # every call, in order: (kind, command or path)

    def mounts(self) -> list[dict]:
        return [{"target": f"{RO_ROOT}/{n}", "label": n} for n in self.mount_names]

    def describe(self) -> dict:
        return {"kind": self.kind, "mounts": self.mounts(), "scratch": SCRATCH}

    def redact(self, text) -> str:
        return text if isinstance(text, str) else (text or b"").decode("utf-8", "replace")

    def start(self, lifetime_s: float | None = None) -> dict:
        self.started = True
        self.lifetime_s = lifetime_s
        return {**self.describe(), "image_id": None, "running_at_start": 0}

    def alive(self) -> bool:
        return not self.dead

    def stop(self) -> dict:
        self.stopped = True
        return {"removed": True, "detail": None}

    def _ready(self) -> None:
        if self.dead:
            raise SandboxDied("the container stopped")
        if not self.started or self.stopped:
            raise SandboxError("the sandbox is not started")

    def shell(self, command: str, limit_s: float) -> ExecResult:
        self._ready()
        self.commands.append(("shell", command))
        r = self.responder(command)
        if isinstance(r, tuple):
            r = result(*r)
        r.limit_s = limit_s
        return r

    def read_file(self, path: str, start: int, count: int, limit_s: float) -> ExecResult:
        self._ready()
        self.commands.append(("read", path))
        data = self.files.get(path)
        if data is None:
            return result(2, f"read_file: No such file or directory: {path}\n", limit_s=limit_s)
        lines = data.splitlines(keepends=True)
        out = b"".join(b"%d: " % n + line for n, line in enumerate(lines, 1)
                       if n >= start and (not count or n < start + count))
        return result(0, out, limit_s=limit_s)

    def write_file(self, path: str, data: bytes, append: bool, limit_s: float) -> ExecResult:
        self._ready()
        self.commands.append(("write", path))
        if not path.startswith(SCRATCH + "/"):
            return result(1, f"write_file: Read-only file system: {path}\n", limit_s=limit_s)
        self.files[path] = (self.files.get(path, b"") + data) if append else data
        verb = "appended" if append else "wrote"
        return result(0, f"write_file: {verb} {len(data)} bytes to {path}\n", limit_s=limit_s)

    def scratch_bytes(self) -> int:
        return sum(len(v) for k, v in self.files.items() if k.startswith(SCRATCH + "/"))

    def scratch_manifest(self) -> list[dict]:
        import hashlib
        return [{"path": k, "kind": "file", "bytes": len(v), "sha256": hashlib.sha256(v).hexdigest()}
                for k, v in sorted(self.files.items()) if k.startswith(SCRATCH + "/")]
