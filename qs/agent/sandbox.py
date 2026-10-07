"""The sandbox: one Docker container per agent run, with no network, the run's
directories mounted read-only, one writable scratch, and limits.

Everything a tool call does happens inside the container, through `docker
exec`. This module is the only code in qs/agent that starts a process, and it
starts only `docker`, from argument lists, never through a shell.

The container, one per run, removed when the run ends:
- `--network none`: the loopback interface only;
- a read-only root (`--read-only`), with a tmpfs at /tmp, to which Docker adds
  noexec;
- each read-only directory at /work/ro/<name>, bound with
  `--mount type=bind,...,readonly`;
- the scratch at /work/scratch, the one writable place that outlives the
  container;
- `--cap-drop ALL`, no-new-privileges, and limits on CPU, memory, processes and
  the size of any one file;
- no environment variable but the image's own, Docker's HOSTNAME, and ENV
  below;
- its main process sleeps for the run's lifetime and then ends, and `--rm`
  removes it: so a container whose host process died goes away by itself.
Each call runs as nobody (65534) under `timeout`, which kills the call's process
group at its limit. The mounts are owned by root, so git would refuse them as
"dubious ownership": safe.directory is set inside the container (see ENV and
GIT_SETUP), never on the host. The host keeps the first HEAD_BYTES and the last TAIL_BYTES
of a call's output and counts every byte and line, so a runaway command cannot
fill the host's memory.

Threat model. The sandbox guards against a model's tool calls, careless or
curious, reaching beyond the run:
- a network;
- host files other than the directories the run is given;
- writes that persist outside the scratch;
- the owner's credentials, the Docker socket and the host's environment;
- runaway use of CPU, memory, processes, time and the scratch's disk.
It does not guard against an escape through a flaw in Docker or the kernel, nor
against a model deliberately hunting for one.

Limits, each stated by the behaviour it concedes:
- on this desktop (Docker Desktop, WSL2), a bind mount whose source is missing
  is created, not refused, with `--mount` as with `-v` (P2.md 13:10:10). The
  check before `docker run` is what refuses one; a source removed between that
  check and `docker run` would be created empty;
- /tmp and /dev/shm accept writes, in memory only, and they vanish with the
  container;
- the calls of one run share the container: a process that leaves its process
  group outlives its call's timeout until the run's container is removed, inside
  the container's limits;
- the container's /proc/self/mountinfo names each mount's host path, so a model
  can read the owner's user name and directory names, though no file it was not
  given;
- the mount check refuses drive roots, the home directory and its ancestors, and
  a short list of credential directory names. A credential kept anywhere else in
  a mounted directory is the suite's to keep out, by mounting only what the run
  needs;
- host paths in Docker's error text are replaced by labels before they reach a
  record. A path in a form the redaction does not match would pass into a run's
  detail, where the gate's privacy check reads it before any push;
- a shell command longer than INLINE_COMMAND_CHARS runs from a file in /tmp, so
  bash's own messages about it name that file where a shorter one's say
  "line N", and it needs room in /tmp;
- a NUL in a shell command or a read_file path, and a lone surrogate in
  write_file content or in a command longer than INLINE_COMMAND_CHARS, raise in
  the handler (ValueError or UnicodeEncodeError), and the loop ends the run as
  error.
"""
from __future__ import annotations

import hashlib
import os
import re
import secrets
import stat
import subprocess
import threading
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence

# The Docker Official Image python:3.12 on Debian trixie, pinned at its
# linux/amd64 manifest (P2.md 13:03:40 records its size before the pull).
IMAGE = ("python:3.12-trixie@sha256:"
         "3d361d7fea344d55ac7a0f51ed7faa99213808ccc96fc9b9170adb95b6570b96")
NAME_PREFIX = "hh-sbx-"
LABEL = "hh.sandbox=qs.agent"
USER = "65534:65534"                  # nobody:nogroup, in the image's /etc/passwd
WORK = "/work"
RO_ROOT = "/work/ro"
SCRATCH = "/work/scratch"
ENV = {
    "HOME": "/tmp",
    "LANG": "C.UTF-8",
    "PYTHONDONTWRITEBYTECODE": "1",
    "GIT_OPTIONAL_LOCKS": "0",
    # The mounts are owned by root and the calls run as nobody, so git refuses
    # them as "dubious ownership". The setting is made inside the container,
    # never on the host, twice: here, in git's command scope, which every call
    # gets afresh; and in git's global file, written by start() (GIT_SETUP),
    # because git clears the command scope for the upload-pack a local clone
    # runs. Both are scopes git honours for safe.directory. A commit made in the
    # scratch needs a name and an address.
    "GIT_CONFIG_COUNT": "3",
    "GIT_CONFIG_KEY_0": "safe.directory",
    "GIT_CONFIG_VALUE_0": "*",
    "GIT_CONFIG_KEY_1": "user.name",
    "GIT_CONFIG_VALUE_1": "sandbox",
    "GIT_CONFIG_KEY_2": "user.email",
    "GIT_CONFIG_VALUE_2": "sandbox@example.invalid",
}
GIT_SETUP = ("git config --global safe.directory '*' && git config --global user.name sandbox && "
             "git config --global user.email sandbox@example.invalid")   # HOME is /tmp, in memory
CREDENTIAL_NAMES = frozenset({".ssh", ".gnupg", ".aws", ".azure", ".kube", ".docker", ".config",
                              ".claude"})
MOUNT_NAME = re.compile(r"[A-Za-z0-9._-]+")
KILL_AFTER_S = 5         # timeout's grace between its TERM and its KILL
BACKSTOP_S = 15          # how long past a call's timeout the host itself waits
HEAD_BYTES = 64 * 1024   # kept from the start of a call's output
TAIL_BYTES = 16 * 1024   # and from its end
DOCKER_TIMEOUT_S = 120   # for docker's own commands: run, rm, ps, inspect
INLINE_COMMAND_CHARS = 8000   # a longer shell command goes in through stdin, not the command line

# Lines are numbered "N: text": the number, a colon and a space (grep -n puts no
# space). DeepSeek's content filter refused a file in cat -n's form, every time,
# and answered the same file in this one (HonestHarness round 1's ledger, 03:23:16).
READ_SCRIPT = """\
import sys
path, start, count = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
try:
    f = open(path, "rb")
except OSError as e:
    print(f"read_file: {e.strerror}: {path}")
    sys.exit(2)
out = sys.stdout.buffer
with f:
    for n, line in enumerate(f, 1):
        if n < start:
            continue
        if count and n >= start + count:
            break
        out.write(b"%d: " % n + line)
"""

WRITE_SCRIPT = """\
import os, sys
path, mode = sys.argv[1], sys.argv[2]
data = sys.stdin.buffer.read()
try:
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "ab" if mode == "append" else "wb") as f:
        f.write(data)
except OSError as e:
    print(f"write_file: {e.strerror}: {path}")
    sys.exit(1)
print(f"write_file: {'appended' if mode == 'append' else 'wrote'} {len(data)} bytes to {path}")
"""


class SandboxError(Exception):
    """The sandbox could not do what was asked. A run meeting it ends as error."""


class SandboxUnavailable(SandboxError):
    """Docker or the image is not there. Nothing was started."""


class SandboxDied(SandboxError):
    """The container or the daemon went away during the run."""


@dataclass(frozen=True)
class Mount:
    """A host directory the run is given, mounted read-only at /work/ro/<name>.
    Its source is never recorded; its name and label are."""
    source: Path
    name: str
    label: str = ""


@dataclass(frozen=True)
class Limits:
    cpus: float = 2.0
    memory_mb: int = 2048
    pids: int = 256
    tmp_mb: int = 512
    file_mb: int = 512


@dataclass
class ExecResult:
    """One call's result. head and tail are the kept ends of its output (stdout
    and stderr merged, as a terminal shows them); total_bytes and total_lines
    count all of it, before any truncation."""
    exit_code: int | None
    head: bytes = b""
    tail: bytes = b""
    total_bytes: int = 0
    total_lines: int = 0
    timed_out: bool = False
    duration_s: float = 0.0
    limit_s: float = 0.0
    note: str | None = None      # the sandbox's own remark, such as docker's stderr

    @property
    def complete(self) -> bool:
        """True when head and tail hold the whole output."""
        return self.total_bytes == len(self.head) + len(self.tail)


class Capture:
    """Keeps the first `head` and the last `tail` bytes of a stream, and counts
    every byte and newline."""

    def __init__(self, head: int = HEAD_BYTES, tail: int = TAIL_BYTES):
        self.head_max, self.tail_max = head, tail
        self.head, self.tail = bytearray(), bytearray()
        self.total = self.lines = 0

    def feed(self, chunk: bytes) -> None:
        self.total += len(chunk)
        self.lines += chunk.count(b"\n")
        room = self.head_max - len(self.head)
        if room > 0:
            self.head += chunk[:room]
            chunk = chunk[room:]
        if chunk and self.tail_max:
            self.tail += chunk
            if len(self.tail) > self.tail_max:
                del self.tail[:len(self.tail) - self.tail_max]

    def drain(self, stream) -> None:
        read = getattr(stream, "read1", stream.read)
        while True:
            chunk = read(65536)
            if not chunk:
                return
            self.feed(chunk)

    def result(self, exit_code: int | None, **kw) -> ExecResult:
        return ExecResult(exit_code, bytes(self.head), bytes(self.tail), self.total, self.lines, **kw)


_HOME_PATH = re.compile(r"(?i)[^\s'\"<>|]*?[\\/](?:users|home)[\\/]+[^\s'\"<>|]+")


def redact_home(text: str) -> str:
    """Replace anything that reads as a path under a home directory."""
    return _HOME_PATH.sub("<a host path>", text)


def docker_status(image: str = IMAGE, docker: str = "docker") -> tuple[bool, str]:
    """(True, the image's id) when the daemon answers and the image is present;
    otherwise (False, why). It never pulls: getting the image is a download."""
    try:
        r = subprocess.run([docker, "version", "--format", "{{.Server.Version}}"],
                           capture_output=True, text=True, timeout=30)
    except FileNotFoundError:
        return False, "docker: the docker command is not installed"
    except subprocess.TimeoutExpired:
        return False, "docker: the daemon did not answer within 30 s"
    if r.returncode != 0 or not r.stdout.strip():
        first = (r.stderr.strip().splitlines() or ["no answer"])[0]
        return False, f"docker: the daemon is not reachable ({redact_home(first)[:200]})"
    try:
        r = subprocess.run([docker, "image", "inspect", "--format", "{{.Id}}", image],
                           capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        return False, "docker: the daemon did not answer within 30 s"
    if r.returncode != 0 or not r.stdout.strip():
        return False, f"the image {image} is not present: run docker pull {image}"
    return True, r.stdout.strip()


def _text(b: bytes | str | None) -> str:
    if b is None:
        return ""
    return b if isinstance(b, str) else b.decode("utf-8", "replace")


class DockerSandbox:
    """One run's container. start() before the first call, stop() on every
    path; the agent loop does both."""

    kind = "docker"
    scratch_target = SCRATCH

    def __init__(self, scratch: str | os.PathLike, readonly: Sequence[Mount] = (), *,
                 image: str = IMAGE, limits: Limits = Limits(), lifetime_s: int = 5400,
                 docker: str = "docker"):
        self.scratch = Path(scratch)
        self.readonly = tuple(readonly)
        self.image, self.limits, self.docker = image, limits, docker
        self.lifetime_s = int(lifetime_s)
        self.run_id = secrets.token_hex(6)
        self.name = NAME_PREFIX + self.run_id
        self.started = False
        self._attempted = False
        self.facts: dict = {}

    # -- what a record may say: targets and labels, never host paths -----------------
    def mounts(self) -> list[dict]:
        return [{"target": f"{RO_ROOT}/{m.name}", "label": m.label or m.name}
                for m in self.readonly]

    def describe(self) -> dict:
        return {"kind": self.kind, "image": self.image, "container": self.name,
                "mounts": self.mounts(), "scratch": SCRATCH, "user": USER, "network": "none",
                "limits": asdict(self.limits), "lifetime_s": self.lifetime_s}

    def redact(self, text: str | bytes | None) -> str:
        """Docker's text with each host source replaced by its label, then any
        other home path by a placeholder."""
        out = _text(text)
        named = [(self.scratch, "<scratch>")] + [(m.source, f"<mount:{m.name}>") for m in self.readonly]
        for src, label in named:
            p = Path(src)
            try:
                p = p.resolve()
            except OSError:
                pass
            forms = {str(p), p.as_posix(), str(Path(src))}
            if p.drive:
                forms.add("/" + "/".join(p.parts[1:]))      # the form Docker Desktop's 9p mount shows
            for f in sorted((f for f in forms if f and f != "/"), key=len, reverse=True):
                out = re.sub(re.escape(f), label, out, flags=re.IGNORECASE)
        return redact_home(out)

    # -- refusals before Docker runs ------------------------------------------------
    def check(self) -> None:
        """Refuse what must not be mounted, before Docker runs: on this desktop
        Docker would create a missing source rather than refuse it."""
        home = Path.home().resolve()
        names: set[str] = set()
        places = [("the scratch", self.scratch)]
        for m in self.readonly:
            if not MOUNT_NAME.fullmatch(m.name) or m.name in (".", ".."):
                raise SandboxError(f"the mount name {m.name!r} is not a plain name")
            if m.name in names:
                raise SandboxError(f"two mounts are named {m.name!r}")
            names.add(m.name)
            places.append((f"the read-only mount {m.name!r}", Path(m.source)))
        resolved = []
        for what, src in places:
            try:
                p = Path(src).resolve(strict=True)
            except (OSError, RuntimeError):
                raise SandboxError(f"{what} does not exist") from None
            resolved.append((what, p))
            if not p.is_dir():
                raise SandboxError(f"{what} is not a directory")
            if p.parent == p:
                raise SandboxError(f"{what} is a drive or filesystem root")
            if p == home or p in home.parents:
                raise SandboxError(f"{what} is the home directory or holds it")
            if any(part.lower() in CREDENTIAL_NAMES for part in p.parts):
                raise SandboxError(f"{what} lies in a directory named for credentials")
            if any(c in str(p) for c in ",\"'\n\r"):
                raise SandboxError(f"{what} has a comma, a quote or a line break in its path, "
                                   "which --mount would misread")
        scratch = resolved[0][1]
        for what, p in resolved[1:]:
            # A read-only directory the scratch shares a tree with would be
            # writable through the scratch.
            if p == scratch or p in scratch.parents or scratch in p.parents:
                raise SandboxError(f"{what} and the scratch overlap, so it could be written "
                                   "through the scratch")

    # -- argument lists ---------------------------------------------------------------
    def run_args(self) -> list[str]:
        lim = self.limits
        args = [self.docker, "run", "-d", "--rm", "--init", "--name", self.name,
                "--label", LABEL, "--label", f"hh.run={self.run_id}",
                "--network", "none", "--read-only",
                "--tmpfs", f"/tmp:rw,nosuid,nodev,size={lim.tmp_mb}m"]
        for m in self.readonly:
            args += ["--mount", f"type=bind,source={Path(m.source).resolve()},"
                                f"target={RO_ROOT}/{m.name},readonly"]
        args += ["--mount", f"type=bind,source={self.scratch.resolve()},target={SCRATCH}",
                 "--workdir", WORK,
                 "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
                 "--pids-limit", str(lim.pids),
                 "--memory", f"{lim.memory_mb}m", "--memory-swap", f"{lim.memory_mb}m",
                 "--cpus", f"{lim.cpus:g}",
                 "--ulimit", f"fsize={lim.file_mb * 1024 * 1024}",
                 "--hostname", "sandbox"]
        for k, v in ENV.items():
            args += ["--env", f"{k}={v}"]
        return args + [self.image, "sleep", str(self.lifetime_s)]

    def exec_args(self, argv: Sequence[str], limit_s: float, *, stdin: bool = False) -> list[str]:
        """`sh` merges the call's stderr into its stdout, then becomes `timeout`,
        which runs the command in its own process group and kills that group
        at the limit."""
        return ([self.docker, "exec"] + (["-i"] if stdin else [])
                + ["--user", USER, "--workdir", WORK, self.name,
                   "sh", "-c", 'exec 2>&1; exec "$@"', "sh",
                   "timeout", "-k", str(KILL_AFTER_S), f"{limit_s:g}", *argv])

    # -- life -------------------------------------------------------------------------
    def _docker(self, args: list[str], timeout: float = DOCKER_TIMEOUT_S):
        try:
            return subprocess.run([self.docker, *args], capture_output=True, timeout=timeout)
        except (OSError, subprocess.TimeoutExpired):
            return None

    def start(self, lifetime_s: float | None = None) -> dict:
        """Start the container. lifetime_s, when given (the agent loop gives
        its budget's), replaces the one the sandbox was made with."""
        if lifetime_s is not None:
            self.lifetime_s = int(lifetime_s)
        ok, why = docker_status(self.image, self.docker)
        if not ok:
            raise SandboxUnavailable(why)
        image_id = why
        self.check()
        ps = self._docker(["ps", "--format", "{{.Names}}"])
        if ps is None or ps.returncode != 0:
            raise SandboxUnavailable("docker: docker ps did not answer")
        running = _text(ps.stdout).split()
        self._attempted = True
        r = self._docker(self.run_args()[1:])
        if r is None or r.returncode != 0:
            raise SandboxError("docker run failed: "
                               + self.redact(r.stderr if r is not None else "no answer")[:300])
        self.started = True
        v = self.shell(f"{GIT_SETUP} && python3 --version && git --version", 60)
        if v.exit_code != 0:
            raise SandboxError("the container's setup failed: "
                               + self.redact(v.head.decode("utf-8", "replace"))[:300])
        versions = _text(v.head).strip().splitlines()
        self.facts = {**self.describe(), "image_id": image_id,
                      "python": next((x for x in versions if x.startswith("Python")), None),
                      "git": next((x for x in versions if x.startswith("git")), None),
                      "running_at_start": len(running),
                      "sandboxes_running_at_start": [n for n in running if n.startswith(NAME_PREFIX)]}
        return self.facts

    def alive(self) -> bool:
        r = self._docker(["inspect", "-f", "{{.State.Running}}", self.name], timeout=30)
        return r is not None and r.returncode == 0 and _text(r.stdout).strip() == "true"

    def stop(self) -> dict:
        """Remove the container, then check that it is gone. Only this run's
        container is touched, by its exact name."""
        if not self._attempted:
            return {"removed": True, "detail": "no container was started"}
        rm = self._docker(["rm", "-f", self.name])
        ls = self._docker(["ps", "-a", "--filter", f"name=^{self.name}$", "--format", "{{.Names}}"])
        removed = ls is not None and ls.returncode == 0 and not _text(ls.stdout).strip()
        self.started = False
        if removed:
            return {"removed": True, "detail": None}
        why = _text(rm.stderr) if rm is not None else "docker did not answer"
        return {"removed": False,
                "detail": f"{self.redact(why).strip()[:300]}; the container ends by itself "
                          f"within {self.lifetime_s} s of its start"}

    # -- calls ------------------------------------------------------------------------
    def shell(self, command: str, limit_s: float) -> ExecResult:
        """A command up to INLINE_COMMAND_CHARS goes to `bash -c` as an argument.
        A longer one would pass Windows' 32767-character command line, so it is
        written through stdin to a file in /tmp and run from there, then the
        file is removed. A NUL is refused in either form, as Popen refuses one."""
        if "\x00" in command:
            raise ValueError("embedded null character in the command")
        if len(command) <= INLINE_COMMAND_CHARS:
            return self._exec(["bash", "-o", "pipefail", "-c", command], limit_s)
        path = f"/tmp/.hh-command-{secrets.token_hex(6)}"
        wrote = self._exec(["sh", "-c", 'cat > "$1"', "sh", path], limit_s,
                           stdin=command.encode("utf-8"))
        if wrote.exit_code != 0 or wrote.timed_out:
            return wrote
        try:
            return self._exec(["bash", "-o", "pipefail", path], limit_s)
        finally:
            try:
                self._exec(["rm", "-f", path], 30)
            except SandboxError:
                pass       # the call's own result, or its error, is what the run records

    def read_file(self, path: str, start: int, count: int, limit_s: float) -> ExecResult:
        return self._exec(["python3", "-c", READ_SCRIPT, path, str(start), str(count)], limit_s)

    def write_file(self, path: str, data: bytes, append: bool, limit_s: float) -> ExecResult:
        return self._exec(["python3", "-c", WRITE_SCRIPT, path, "append" if append else "write"],
                          limit_s, stdin=data)

    def _exec(self, argv: list[str], limit_s: float, stdin: bytes | None = None) -> ExecResult:
        if not self.started:
            raise SandboxError("the sandbox is not started")
        args = self.exec_args(argv, limit_s, stdin=stdin is not None)
        t0 = time.monotonic()
        try:
            proc = subprocess.Popen(args, stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except OSError as e:
            raise SandboxDied(f"docker could not be run: {type(e).__name__}") from None
        out, err = Capture(), Capture(4096, 0)
        threads = [threading.Thread(target=out.drain, args=(proc.stdout,), daemon=True),
                   threading.Thread(target=err.drain, args=(proc.stderr,), daemon=True)]
        if stdin is not None:
            threads.append(threading.Thread(target=_feed, args=(proc.stdin, stdin), daemon=True))
        for t in threads:
            t.start()
        backstop = False
        try:
            proc.wait(timeout=limit_s + KILL_AFTER_S + BACKSTOP_S)
        except subprocess.TimeoutExpired:
            backstop = True
            proc.kill()
            proc.wait()
        for t in threads:
            t.join(timeout=10)
        dt = time.monotonic() - t0
        note = _text(bytes(err.head)).strip() or None
        if (note or backstop) and not self.alive():
            raise SandboxDied("the container stopped: " + self.redact(note or "during a call")[:300])
        code = None if backstop else proc.returncode
        timed_out = backstop or (code in (124, 137) and dt >= limit_s)
        return out.result(code, timed_out=timed_out, duration_s=round(dt, 3), limit_s=limit_s,
                          note=self.redact(note)[:500] if note else None)

    # -- the scratch, read on the host ------------------------------------------------
    def scratch_bytes(self) -> int:
        total = 0
        for d, _dirs, files in os.walk(self.scratch, followlinks=False):
            for f in files:
                try:
                    total += os.lstat(os.path.join(d, f)).st_size
                except OSError:
                    pass
        return total

    def scratch_manifest(self, hash_limit: int = 64 * 1024 * 1024) -> list[dict]:
        """Each entry in the scratch: its path inside the container, its kind, its
        size, and a regular file's SHA-256 (above hash_limit, sized only).

        Nothing here follows a link. A symlink made in the container reaches the
        host as a WSL reparse point (tag 0xa000001d, P2.md 13:30:32): lstat calls
        it a regular file, while stat, exists() and is_file() raise and a read
        fails. So the kind comes from lstat and the reparse tag alone."""
        out = []
        for d, _dirs, files in os.walk(self.scratch, followlinks=False):
            for f in sorted(files):
                p = Path(d) / f
                rel = p.relative_to(self.scratch).as_posix()
                try:
                    st = os.lstat(p)
                except OSError:
                    out.append({"path": f"{SCRATCH}/{rel}", "kind": "unreadable", "bytes": None,
                                "sha256": None})
                    continue
                kind = ("link" if stat.S_ISLNK(st.st_mode) or getattr(st, "st_reparse_tag", 0)
                        else "file" if stat.S_ISREG(st.st_mode) else "other")
                sha = None
                if kind == "file" and st.st_size <= hash_limit:
                    try:
                        sha = hashlib.sha256(p.read_bytes()).hexdigest()
                    except OSError:
                        kind = "unreadable"
                out.append({"path": f"{SCRATCH}/{rel}", "kind": kind, "bytes": st.st_size, "sha256": sha})
        return sorted(out, key=lambda x: x["path"])


def _feed(pipe, data: bytes) -> None:
    try:
        pipe.write(data)
    except OSError:
        pass
    finally:
        try:
            pipe.close()
        except OSError:
            pass
