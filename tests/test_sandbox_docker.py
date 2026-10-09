"""The sandbox in Docker: its isolation, its limits, its removal on every path,
git and Python inside, and the loop end to end in a real container.

These tests skip, saying why, when Docker or the pinned image is absent: getting
the image is a download, which a test never makes. `python sandbox/controls.py`
runs them on their own, with the mounted-gate control, and counts a skip as a
failure. Every container here is the sandbox's own, named hh-sbx-, and removed."""
import importlib.util
import json
import subprocess
import time
from decimal import Decimal
from pathlib import Path

import pytest

from qs.agent import Budgets, DockerSandbox, Limits, Mount, SandboxError, builtin_tools, run_agent
from qs.agent.sandbox import ENV, IMAGE, docker_status
from qs.agent.scripted import ScriptedModel, tool_call
from qs.fake import FakeServer, reply
from qs.guard import SpendGuard
from qs.registry import Endpoint
from qs.suite import Caps, Item, Runner, Suite

DOCKER, WHY = docker_status()
pytestmark = pytest.mark.skipif(not DOCKER, reason=WHY)

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("hh_check_docker", ROOT / "tools" / "check.py")
check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check)

SMALL = Limits(cpus=1, memory_mb=256, pids=64, tmp_mb=64, file_mb=1)
VIRTUAL_FS = {"proc", "sysfs", "devpts", "mqueue", "tmpfs", "cgroup", "cgroup2"}


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), "-c", "core.autocrlf=false", "-c", "user.name=t",
                    "-c", "user.email=t@example.invalid", *args], check=True, capture_output=True)


def make_dirs(tmp_path):
    repo, ledger, scratch = tmp_path / "repo", tmp_path / "ledger", tmp_path / "scratch"
    for d in (repo, ledger, scratch):
        d.mkdir()
    (repo / "README.md").write_bytes(b"a repository the run is given\n")
    (ledger / "lead.md").write_bytes(b"# a ledger\n")
    git(repo, "init", "-q")
    git(repo, "add", "README.md")
    git(repo, "commit", "-q", "-m", "the first commit")
    return repo, ledger, scratch


@pytest.fixture
def started(tmp_path):
    repo, ledger, scratch = make_dirs(tmp_path)
    b = DockerSandbox(scratch, [Mount(repo, "repo", "a test repo"), Mount(ledger, "ledger")], limits=SMALL)
    b.start()
    yield b, scratch
    assert b.stop()["removed"]


def sh(b, command, limit=30):
    r = b.shell(command, limit)
    return r.exit_code, (r.head + r.tail).decode("utf-8", "replace")


def gone(name):
    out = subprocess.run(["docker", "ps", "-a", "--filter", f"name=^{name}$", "--format", "{{.Names}}"],
                         capture_output=True, text=True).stdout
    return out.strip() == ""


def test_the_network_is_absent(started):
    b, _ = started
    code, out = sh(b, "cat /proc/net/dev")
    assert [line.split(":")[0].strip() for line in out.splitlines()[2:]] == ["lo"]
    code, out = sh(b, "cat /proc/net/route")
    assert len(out.strip().splitlines()) == 1                       # its header, and no route
    code, out = sh(b, "python3 -c \"import socket; socket.create_connection(('192.0.2.1', 80), timeout=3)\"")
    assert code != 0 and "Network is unreachable" in out
    for name in ("example.com", "host.docker.internal"):
        code, out = sh(b, f"getent hosts {name}")
        assert code == 2 and out.strip() == "", name


def mountinfo(b):
    _, out = sh(b, "cat /proc/self/mountinfo")
    mounts = {}
    for line in out.splitlines():
        left, right = line.split(" - ", 1)
        fields = left.split()
        mounts[fields[4]] = (set(fields[5].split(",")), right.split()[0])
    return mounts


def test_a_write_persists_only_in_the_scratch(started):
    b, scratch = started
    for target in ("/x", "/usr/x", "/etc/x", "/root/x", "/work/x", "/work/ro/repo/x", "/work/ro/ledger/x"):
        code, out = sh(b, f"echo hi > {target}")
        assert code != 0 and ("Read-only file system" in out or "Permission denied" in out), target
    code, out = sh(b, "echo more >> /etc/hosts")
    assert code != 0
    code, out = sh(b, "echo kept > /work/scratch/kept.txt && cat /work/scratch/kept.txt")
    assert code == 0 and (scratch / "kept.txt").read_bytes() == b"kept\n"
    mounts = mountinfo(b)
    assert "ro" in mounts["/"][0]
    writable = {mp for mp, (opts, fs) in mounts.items() if "rw" in opts and fs not in VIRTUAL_FS}
    assert writable == {"/work/scratch"}


def test_a_link_made_in_the_scratch_is_recorded_and_never_followed(started):
    b, scratch = started
    code, out = sh(b, "ln -s /etc/passwd /work/scratch/link && echo plain > /work/scratch/plain.txt")
    assert code == 0
    manifest = {e["path"]: e for e in b.scratch_manifest()}
    assert (manifest["/work/scratch/link"]["kind"], manifest["/work/scratch/link"]["sha256"]) == ("link", None)
    assert manifest["/work/scratch/plain.txt"]["kind"] == "file" and manifest["/work/scratch/plain.txt"]["sha256"]


def test_the_mounts_are_exactly_those_given(started):
    b, _ = started
    mounts = mountinfo(b)
    assert {mp for mp in mounts if mp.startswith("/work")} == {"/work/ro/repo", "/work/ro/ledger", "/work/scratch"}
    assert "ro" in mounts["/work/ro/repo"][0] and "ro" in mounts["/work/ro/ledger"][0]
    assert "rw" in mounts["/work/scratch"][0]


def test_nothing_ambient_reaches_the_container(started):
    b, _ = started
    code, out = sh(b, "test -e /var/run/docker.sock; echo $?; id -u; id -g; echo $HOME; ls -A /home")
    assert out.split() == ["1", "65534", "65534", "/tmp"]
    image_env = json.loads(subprocess.run(["docker", "image", "inspect", "--format", "{{json .Config.Env}}",
                                           IMAGE], capture_output=True, text=True).stdout)
    expected = {e.split("=", 1)[0] for e in image_env} | set(ENV) | {"HOSTNAME"} | {"PWD", "SHLVL", "_"}
    code, out = sh(b, "python3 -c \"import os; print(' '.join(sorted(os.environ)))\"")
    assert set(out.split()) == expected


PIDS = """\
python3 -c "
import subprocess
procs = []
try:
    for _ in range(200):
        procs.append(subprocess.Popen(['sleep', '30']))
except OSError as e:
    print('refused at', len(procs), e.strerror)
for p in procs:
    p.kill()
"
"""


def test_the_limits_are_set_and_hold(started):
    b, _ = started
    inspect = json.loads(subprocess.run(["docker", "inspect", b.name], capture_output=True, text=True).stdout)[0]
    hc = inspect["HostConfig"]
    assert hc["NetworkMode"] == "none" and hc["ReadonlyRootfs"] is True and hc["CapDrop"] == ["ALL"]
    assert "no-new-privileges" in hc["SecurityOpt"] and hc["Init"] is True
    assert hc["NanoCpus"] == 1_000_000_000 and hc["Memory"] == 256 * 2**20 == hc["MemorySwap"]
    assert hc["PidsLimit"] == 64 and not inspect["Mounts"] == []
    code, out = sh(b, PIDS)
    assert "refused at" in out and "Resource temporarily unavailable" in out
    code, out = sh(b, "python3 -c \"b = bytearray(400 * 1024 * 1024); print(len(b))\"")
    assert code == 137
    code, out = sh(b, "head -c 2000000 /dev/zero > /work/scratch/big; echo $?")
    assert out.strip().endswith("153")                        # the 1 MiB file limit
    r = b.shell("sleep 30", 2)
    assert r.timed_out and r.exit_code == 124 and r.duration_s < 10
    code, out = sh(b, "ps -eo user,comm")
    assert not [line for line in out.splitlines() if line.split() == ["nobody", "sleep"]]


def test_git_and_python_run_inside(started):
    b, _ = started
    code, out = sh(b, "python3 --version && git --version")
    assert code == 0 and out.startswith("Python 3.12") and "git version" in out
    code, out = sh(b, "git -C /work/ro/repo log --oneline")
    assert code == 0 and "the first commit" in out
    code, out = sh(b, "env GIT_CONFIG_COUNT=0 HOME=/nonexistent git -C /work/ro/repo log --oneline")
    assert code == 128 and "dubious ownership" in out           # why the settings are there
    code, out = sh(b, "git clone -q /work/ro/repo /work/scratch/copy && git -C /work/scratch/copy log --oneline")
    assert code == 0 and "the first commit" in out


def test_a_command_past_the_command_line_limit_runs(started):
    b, _ = started
    payload = "x" * 100_000                       # Windows' command line holds 32767 characters
    r = b.shell(f"printf '%s' '{payload}' | wc -c", 60)
    out = (r.head + r.tail).decode()
    assert r.exit_code == 0 and out.strip() == "100000" and b.alive()
    code, listing = sh(b, "ls -A /tmp")
    assert ".hh-command-" not in listing                 # the command's file is removed


def test_a_start_that_raises_after_docker_run_still_removes_the_container(tmp_path, monkeypatch):
    _, _, scratch = make_dirs(tmp_path)
    b = DockerSandbox(scratch, [], limits=SMALL)
    real_shell = DockerSandbox.shell

    def shell_that_breaks(self, command, limit_s):
        if "git config --global" in command:      # the setup start() runs after docker run
            raise RuntimeError("a fault that is not a SandboxError")
        return real_shell(self, command, limit_s)
    monkeypatch.setattr(DockerSandbox, "shell", shell_that_breaks)
    try:
        with FakeServer(ScriptedModel(calls(tool_call("r", "report", {"text": "x"})))) as url:
            res = run_agent(context(url), messages=[{"role": "user", "content": "go"}],
                            tools=builtin_tools(), sandbox=b)
        assert res.outcome == "error" and "RuntimeError" in res.cause
        assert res.sandbox["removed"] is True and gone(b.name)
    finally:
        subprocess.run(["docker", "rm", "-f", b.name], capture_output=True)   # only if the test failed


def test_a_missing_source_is_refused_and_never_created(tmp_path):
    _, _, scratch = make_dirs(tmp_path)
    b = DockerSandbox(scratch, [Mount(tmp_path / "missing", "repo")], limits=SMALL)
    with pytest.raises(SandboxError, match="does not exist"):
        b.start()
    assert not (tmp_path / "missing").exists() and gone(b.name)
    assert b.stop()["removed"]


def test_an_unstopped_sandbox_removes_itself(tmp_path):
    _, _, scratch = make_dirs(tmp_path)
    b = DockerSandbox(scratch, [], limits=SMALL, lifetime_s=3)
    b.start()
    deadline = time.monotonic() + 30
    while not gone(b.name) and time.monotonic() < deadline:
        time.sleep(0.5)
    assert gone(b.name)


def context(url):
    from qs.client import Client
    from qs.suite import Context
    ep = Endpoint(name="fake", provider="deepseek", base_url=url, model="deepseek-flash",
                  price_table="prices/deepseek-2026-10-06.json", key_env=None)
    return Context(Client(url), ep, Caps(1_000_000, 100_000, 200_000), thinking=True, effort=None)


def calls(*tcs):
    return reply(None, reasoning="r", tool_calls=list(tcs), finish="tool_calls")


def kill_then(b, nxt):
    def respond(body):
        subprocess.run(["docker", "kill", b.name], capture_output=True)
        return nxt
    return respond


@pytest.mark.parametrize("path", ["normal", "error", "timeout"])
def test_the_container_is_removed_on_every_path(tmp_path, path):
    repo, _, scratch = make_dirs(tmp_path)
    b = DockerSandbox(scratch, [Mount(repo, "repo")], limits=SMALL)
    report = calls(tool_call("r", "report", {"text": "done"}))
    if path == "normal":
        script = [calls(tool_call("c1", "shell", {"command": "ls /work"})), report]
    elif path == "error":
        script = [calls(tool_call("c1", "shell", {"command": "ls"})),
                  kill_then(b, calls(tool_call("c2", "shell", {"command": "ls"}))), report]
    else:
        script = [calls(tool_call("c1", "shell", {"command": "sleep 30"})), report]
    with FakeServer(ScriptedModel(*script)) as url:
        res = run_agent(context(url), messages=[{"role": "user", "content": "go"}], tools=builtin_tools(),
                        sandbox=b, budgets=Budgets(call_timeout_seconds=2))
    expected = {"normal": "reported", "error": "error", "timeout": "reported"}[path]
    assert res.outcome == expected and res.sandbox["removed"] and gone(b.name)
    if path == "error":
        assert "the container stopped" in res.cause
    if path == "timeout":
        assert res.timeouts == 1


class SandboxedSuite(Suite):
    name = "sandboxed"
    version = "test-1"
    caps = Caps(max_prompt_tokens=200_000, max_output_tokens=20_000, max_call_prompt_tokens=50_000)

    def __init__(self, repo, scratch):
        self.repo, self.scratch = repo, scratch

    def items(self):
        return [Item("i0")]

    def run_item(self, ctx, item):
        box = DockerSandbox(self.scratch, [Mount(self.repo, "repo", "a test repo")], limits=SMALL)
        res = run_agent(ctx, messages=[{"role": "user", "content": "try to get out"}],
                        tools=builtin_tools(), sandbox=box, budgets=Budgets(call_timeout_seconds=10))
        return res.item_result(lambda r: ("pass", "reported"))


def test_the_loop_end_to_end_in_the_sandbox(tmp_path, prices, off_peak_clock):
    repo, _, scratch = make_dirs(tmp_path)
    tries = [("t1", "shell", {"command": "getent hosts example.com; echo rc=$?"}),
             ("t2", "shell", {"command": "python3 -c \"import socket; socket.create_connection(('192.0.2.1', 80), 3)\""}),
             ("t3", "shell", {"command": "echo x > /work/ro/repo/README.md"}),
             ("t4", "shell", {"command": "touch /usr/local/x"}),
             ("t5", "write_file", {"path": "/work/ro/repo/README.md", "content": "x"}),
             ("t6", "write_file", {"path": "notes.md", "content": "what I found\n"}),
             ("t7", "read_file", {"path": "ro/repo/README.md"})]
    model = ScriptedModel(*[calls(tool_call(i, n, a)) for i, n, a in tries],
                          calls(tool_call("r", "report", {"text": "nothing got out"})))
    with FakeServer(model, prices=prices, clock=off_peak_clock) as url:
        ep = Endpoint(name="fake", provider="deepseek", base_url=url, model="deepseek-flash",
                      price_table="prices/deepseek-2026-10-06.json", key_env=None)
        runner = Runner(ep, prices, SpendGuard(Decimal("250"), tmp_path / "records" / "spend.jsonl"),
                        records_dir=tmp_path / "records", transcripts_dir=tmp_path / "transcripts",
                        clock=off_peak_clock)
        s = runner.run_batch(SandboxedSuite(repo, scratch))
    answers = [m["content"] for m in model.bodies[-1]["messages"] if m["role"] == "tool"]
    assert "rc=2" in answers[0] and "Network is unreachable" in answers[1]
    assert "Read-only file system" in answers[2] and "Read-only file system" in answers[3]
    assert "refused" in answers[4] and "wrote 13 bytes" in answers[5]
    assert "1: a repository the run is given" in answers[6] and "\t" not in answers[6]
    assert (scratch / "notes.md").read_bytes() == b"what I found\n"
    assert (repo / "README.md").read_bytes() == b"a repository the run is given\n"
    record_text = (tmp_path / "records" / "runs" / "sandboxed.jsonl").read_text(encoding="utf-8")
    record = json.loads(record_text)
    assert record["outcome"]["status"] == "pass" and s["runs"] == 1
    agent = record["outcome"]["data"]["agent"]
    assert agent["sandbox"]["removed"] and agent["sandbox"]["image"] == IMAGE
    assert agent["sandbox"]["mounts"] == [{"target": "/work/ro/repo", "label": "a test repo"}]
    assert agent["sandbox"]["python"].startswith("Python 3.12")
    assert check.findings(record_text) == [] and str(tmp_path) not in record_text
