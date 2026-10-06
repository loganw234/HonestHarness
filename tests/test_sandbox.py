"""The sandbox without Docker: the argument lists it builds, the mounts it
refuses before Docker runs, and the host paths it keeps out of records. Every
home path here is built at run time from pieces, so this file holds none."""
import importlib.util
import re
import subprocess
from pathlib import Path

import pytest

from qs.agent import sandbox as sb
from qs.agent.sandbox import (ENV, IMAGE, SCRATCH, DockerSandbox, Mount, SandboxError,
                              SandboxUnavailable, docker_status, redact_home)

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("hh_check_sandbox", ROOT / "tools" / "check.py")
check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check)

U = "Us" + "ers"
BS = chr(92)


@pytest.fixture
def dirs(tmp_path):
    (tmp_path / "repo").mkdir()
    (tmp_path / "ledger").mkdir()
    (tmp_path / "scratch").mkdir()
    return tmp_path


def box(dirs, **kw):
    return DockerSandbox(dirs / "scratch", [Mount(dirs / "repo", "repo", "the repo"),
                                            Mount(dirs / "ledger", "ledger")], **kw)


def test_the_image_is_pinned_by_digest():
    assert re.fullmatch(r"python:3\.12-trixie@sha256:[0-9a-f]{64}", IMAGE)


def test_the_run_arguments_hold_every_isolation_setting(dirs):
    b = box(dirs)
    args = b.run_args()
    joined = " ".join(args)
    pairs = list(zip(args, args[1:]))
    for flag, value in [("--network", "none"), ("--cap-drop", "ALL"),
                        ("--security-opt", "no-new-privileges"), ("--pids-limit", "256"),
                        ("--memory", "2048m"), ("--memory-swap", "2048m"), ("--cpus", "2"),
                        ("--ulimit", f"fsize={512 * 1024 * 1024}"), ("--workdir", "/work"),
                        ("--tmpfs", "/tmp:rw,nosuid,nodev,size=512m"), ("--name", b.name),
                        ("--label", "hh.sandbox=qs.agent")]:
        assert (flag, value) in pairs, flag
    for flag in ("--read-only", "--rm", "--init", "-d"):
        assert flag in args
    assert b.name.startswith("hh-sbx-")
    mounts = [v for f, v in pairs if f == "--mount"]
    assert mounts == [f"type=bind,source={(dirs / 'repo').resolve()},target=/work/ro/repo,readonly",
                      f"type=bind,source={(dirs / 'ledger').resolve()},target=/work/ro/ledger,readonly",
                      f"type=bind,source={(dirs / 'scratch').resolve()},target={SCRATCH}"]
    for banned in ("-v", "--volume", "--privileged", "--env-file", "-e", "--network=host", "--net",
                   "--cap-add", "--device", "--pid", "--ipc"):
        assert banned not in args, banned
    assert "docker.sock" not in joined and "host" not in [v for f, v in pairs if f == "--network"]
    assert [v for f, v in pairs if f == "--env"] == [f"{k}={v}" for k, v in ENV.items()]
    assert args[-3:] == [IMAGE, "sleep", str(b.lifetime_s)]


def test_each_call_runs_as_nobody_under_timeout_with_stderr_merged(dirs):
    args = box(dirs).exec_args(["bash", "-o", "pipefail", "-c", "ls"], 30)
    i = args.index("exec")
    assert args[i + 1:i + 5] == ["--user", "65534:65534", "--workdir", "/work"]
    tail = args[i + 6:]
    assert tail[:4] == ["sh", "-c", 'exec 2>&1; exec "$@"', "sh"]
    assert tail[4:8] == ["timeout", "-k", "5", "30"] and tail[8:] == ["bash", "-o", "pipefail", "-c", "ls"]
    assert "-i" not in args and "-i" in box(dirs).exec_args(["cat"], 5, stdin=True)


def test_git_is_settled_inside_the_container():
    assert (ENV["GIT_CONFIG_KEY_0"], ENV["GIT_CONFIG_VALUE_0"]) == ("safe.directory", "*")
    assert ENV["GIT_CONFIG_COUNT"] == "3" and ENV["HOME"] == "/tmp"


@pytest.mark.parametrize("make, says", [
    (lambda d: Mount(d / "missing", "repo"), "does not exist"),
    (lambda d: Mount(d / "file.txt", "repo"), "is not a directory"),
    (lambda d: Mount(Path(Path.home().anchor), "root"), "root"),
    (lambda d: Mount(Path.home(), "home"), "home directory"),
    (lambda d: Mount(Path.home().parent, "homes"), "home directory"),
    (lambda d: Mount(d / ".ssh", "keys"), "credentials"),
    (lambda d: Mount(d / "a,b", "comma"), "comma"),
    (lambda d: Mount(d / "repo", "../up"), "plain name"),
    (lambda d: Mount(d / "repo", "a b"), "plain name"),
])
def test_a_mount_that_must_not_be_given_is_refused(dirs, make, says):
    (dirs / "file.txt").write_bytes(b"x")
    (dirs / ".ssh").mkdir()
    (dirs / "a,b").mkdir()
    m = make(dirs)
    b = DockerSandbox(dirs / "scratch", [m])
    with pytest.raises(SandboxError) as e:
        b.check()
    assert says in str(e.value)
    assert check.findings(str(e.value)) == []          # the refusal names no host path


@pytest.mark.parametrize("scratch, source", [("scratch", "scratch"), ("repo/inner", "repo"),
                                             ("scratch", "scratch/inner")])
def test_a_read_only_mount_may_not_overlap_the_scratch(dirs, scratch, source):
    (dirs / "repo" / "inner").mkdir()
    (dirs / "scratch" / "inner").mkdir()
    b = DockerSandbox(dirs / scratch, [Mount(dirs / source, "repo")])
    with pytest.raises(SandboxError, match="overlap"):
        b.check()


def test_two_mounts_may_not_share_a_name(dirs):
    b = DockerSandbox(dirs / "scratch", [Mount(dirs / "repo", "x"), Mount(dirs / "ledger", "x")])
    with pytest.raises(SandboxError, match="two mounts"):
        b.check()


def test_a_missing_scratch_is_refused(dirs):
    with pytest.raises(SandboxError, match="the scratch does not exist"):
        DockerSandbox(dirs / "nowhere", []).check()


class Recorder:
    """Stands in for subprocess: answers docker version and image inspect as a
    working daemon would, and records every command."""

    def __init__(self):
        self.commands = []

    def run(self, args, **kw):
        self.commands.append(list(args))
        out = {"version": "29.2.1\n", "image": "sha256:" + "0" * 64 + "\n"}.get(args[1], "")
        return subprocess.CompletedProcess(args, 0, out if kw.get("text") else out.encode(), "")


def test_a_missing_source_is_refused_before_docker_runs_and_nothing_is_created(dirs, monkeypatch):
    rec = Recorder()
    monkeypatch.setattr(sb.subprocess, "run", rec.run)
    b = DockerSandbox(dirs / "scratch", [Mount(dirs / "missing", "repo")])
    with pytest.raises(SandboxError, match="does not exist"):
        b.start()
    assert [c[1] for c in rec.commands] == ["version", "image"]     # never ps, never run
    assert not (dirs / "missing").exists() and b.stop()["removed"]


def test_docker_status_says_why_when_docker_is_missing():
    ok, why = docker_status(docker="hh-no-such-docker-command")
    assert not ok and why == "docker: the docker command is not installed"


def test_an_unavailable_docker_refuses_the_start(dirs):
    b = box(dirs, docker="hh-no-such-docker-command")
    with pytest.raises(SandboxUnavailable):
        b.start()
    assert b.stop() == {"removed": True, "detail": "no container was started"}


def _home_forms(rest):
    name = "some" + "one"
    return ["C:" + BS + U + BS + name + BS + rest.replace("/", BS),
            "C:/" + U + "/" + name + "/" + rest,
            "/" + U + "/" + name + "/" + rest,                      # Docker Desktop's 9p root
            "/run/desktop/mnt/host/c/" + U + "/" + name + "/" + rest,
            "/mnt/host/c/" + U + "/" + name + "/" + rest,
            "/home/" + name + "/" + rest]


@pytest.mark.parametrize("form", _home_forms("AppData/Local/x/scratch"))
def test_redaction_leaves_no_home_path(form):
    text = f"Error response from daemon: invalid mount config: bind source path does not exist: {form}"
    out = redact_home(text)
    assert check.findings(out) == [] and "<a host path>" in out


def test_a_sandbox_redacts_its_own_sources_by_label(dirs):
    b = box(dirs)
    for p in (dirs / "repo", dirs / "scratch"):
        r = p.resolve()
        forms = [str(r), r.as_posix(), "/" + "/".join(r.parts[1:])]
        for f in forms:
            out = b.redact(f"cannot read {f}/x.txt")
            assert check.findings(out) == []
            assert ("<mount:repo>" in out) if p.name == "repo" else ("<scratch>" in out)


def test_the_description_holds_no_host_path(dirs):
    import json
    text = json.dumps(box(dirs).describe())
    assert check.findings(text) == [] and str(dirs) not in text and "the repo" in text
