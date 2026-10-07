"""The sandbox's Docker controls, on their own, in one command:

    python sandbox/controls.py --parcelround <ParcelRound checkout> --work <a new directory>

1. It refuses, with exit 2, if Docker or the pinned image is absent, before it
   runs anything else; then it reads `docker ps`.
2. It runs tests/test_sandbox_docker.py. A skip there counts as a failure here.
3. It runs the mounted-gate control: round 6's gate, ParcelRound's
   tools/check_method.py at f42242e, on the host and inside the sandbox.
   - G1. It clones the checkout with --no-hardlinks into <work>/parcelround, so
     nothing in the source is written or linked, and checks out f42242e,
     detached. A failed clone or checkout stops the control: it never falls
     back to the source.
   - G2. It asserts what it will mount: the clone's HEAD is f42242e, its tree is
     the tree `git rev-parse f42242e^{tree}` reads in the source now, and its
     working tree is clean.
   - G3. It runs the gate on the host, in the clone.
   - G4. It runs the gate in a DockerSandbox, the clone mounted read-only at
     /work/ro/parcelround, through the same code path the agent loop uses.
   - G5. It compares each check's ok or FAIL, and the final verdict, and prints
     both outputs whole. A difference is a finding, and fails the control. The
     checks' own summaries are printed side by side, and a difference there
     alone is a note.
It exits 0 only when every control holds. Its output names no absolute path:
the source is <source>, and the work directory <work>. ParcelRound's gate masks
what it refuses, so its output holds none either.

Limits, each stated by the behaviour it concedes:
- G2 asserts the clone before the host run, G3, and not again before the mount,
  G4: a gate that wrote into its own tree on the host would reach the container
  unasserted. Round 6's gate writes nothing there (P2.md 14:56:59, measured on
  the clone after a real run);
- G5 holds when the two verdicts match, whatever they are: a gate that fails the
  same way on both sides reads "held". The control compares the two places; it
  does not judge round 6's tree.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from qs.agent.sandbox import IMAGE, DockerSandbox, Mount, SandboxError, docker_status  # noqa: E402

PARCELROUND_COMMIT = "f42242ecc1707a3d36c52e4b2a3b580ee2783e5b"   # round 6's gate (plan §6)
CHECK_LINE = re.compile(r"^(\w+)\s+(ok|FAIL)\b\s*(.*)$")
VERDICT_LINE = re.compile(r"^(PASS|FAIL): \d+ of \d+ checks hold$")
GATE_TIMEOUT_S = 900


def git(*args: str) -> subprocess.CompletedProcess:
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    try:
        return subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8", env=env)
    except OSError:
        return subprocess.CompletedProcess(["git", *args], 127, "", "git could not be run")


def verdict(text: str) -> tuple[dict, dict, str | None]:
    """Each check's ok or FAIL, each check's summary, and the final line."""
    status, ran, final = {}, {}, None
    for line in text.splitlines():
        m = CHECK_LINE.match(line)
        if m:
            status[m.group(1)], ran[m.group(1)] = m.group(2), m.group(3)
        elif VERDICT_LINE.match(line.strip()):
            final = line.strip()
    return status, ran, final


def docker_tests() -> bool:
    print("== the Docker tests: tests/test_sandbox_docker.py")
    r = subprocess.run([sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "-W", "ignore", "-rs",
                        "tests/test_sandbox_docker.py"], cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8")
    lines = [x for x in r.stdout.splitlines() if x.strip()]
    for x in lines[-12:]:
        print("   " + x)
    last = lines[-1] if lines else ""
    held = r.returncode == 0 and "passed" in last and "skipped" not in last and "failed" not in last
    print(f"   {'held' if held else 'NOT HELD'}: {last}")
    return held


def gate_control(source: Path, work: Path) -> bool:
    print("== the mounted-gate control: ParcelRound's tools/check_method.py at f42242e")
    clone, scratch = work / "parcelround", work / "scratch"
    # G1
    r = git("clone", "--no-hardlinks", "-q", str(source), str(clone))
    if r.returncode != 0:
        print("   G1 FAILED: the clone of <source> failed; the control stops, with no fallback")
        return False
    r = git("-C", str(clone), "checkout", "-q", "--detach", PARCELROUND_COMMIT)
    if r.returncode != 0:
        print("   G1 FAILED: f42242e could not be checked out in the clone; the control stops")
        return False
    print("   G1 cloned <source> into <work>/parcelround with --no-hardlinks, and checked out f42242e")
    # G2
    head = git("-C", str(clone), "rev-parse", "HEAD").stdout.strip()
    tree = git("-C", str(clone), "rev-parse", "HEAD^{tree}").stdout.strip()
    source_tree = git("-C", str(source), "rev-parse", PARCELROUND_COMMIT + "^{tree}").stdout.strip()
    dirty = git("-C", str(clone), "status", "--porcelain").stdout.strip()
    print(f"   G2 HEAD {head}; tree {tree}; the source's f42242e^{{tree}} {source_tree}; "
          f"{'clean' if not dirty else 'NOT CLEAN'}")
    if head != PARCELROUND_COMMIT or not tree or tree != source_tree or dirty:
        print("   G2 FAILED: the clone is not exactly f42242e; nothing is mounted")
        return False
    # G3
    host = subprocess.run([sys.executable, "tools/check_method.py"], cwd=clone, capture_output=True,
                          text=True, encoding="utf-8", timeout=GATE_TIMEOUT_S)
    print(f"   G3 on the host: exit {host.returncode}")
    # G4
    scratch.mkdir()
    box = DockerSandbox(scratch, [Mount(clone, "parcelround", "parcelround@f42242e")],
                        lifetime_s=GATE_TIMEOUT_S + 600)
    try:
        box.start()
        r = box.shell("cd /work/ro/parcelround && python3 tools/check_method.py", GATE_TIMEOUT_S)
        inside = (r.head + r.tail).decode("utf-8", "replace")
        inside_code = r.exit_code
        complete = r.complete and not r.timed_out
    except SandboxError as e:
        print(f"   G4 FAILED: the sandbox failed: {e}")
        return False
    finally:
        stopped = box.stop()
    print(f"   G4 in the sandbox ({IMAGE.split('@')[0]}, {box.facts.get('python')}, "
          f"{box.facts.get('git')}): exit {inside_code}; container removed: {stopped['removed']}")
    # G5
    hs, hr, hf = verdict(host.stdout)
    cs, cr, cf = verdict(inside)
    print("   G5 the host's output:")
    for x in host.stdout.splitlines():
        print("      | " + x)
    print("   G5 the container's output:")
    for x in inside.splitlines():
        print("      | " + x)
    print("   G5 each check, host against container:")
    for name in sorted(set(hs) | set(cs)):
        same = hs.get(name) == cs.get(name)
        note = "" if hr.get(name) == cr.get(name) else f"  (note: '{hr.get(name)}' against '{cr.get(name)}')"
        print(f"      {name:10} {hs.get(name)!s:5} {cs.get(name)!s:5} {'same' if same else 'DIFFERS'}{note}")
    match = bool(hf) and hs == cs and hf == cf and host.returncode == inside_code and complete
    if match:
        print(f"   G5 held: the verdicts match ({hf})")
    elif not complete:
        print("   G5 NOT HELD: the container's output was cut short or timed out, so the verdicts "
              "cannot be compared")
    else:
        print(f"   G5 NOT HELD: verdicts differ, a finding: host {hf!r} exit {host.returncode}; "
              f"container {cf!r} exit {inside_code}")
    return match and stopped["removed"]


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="The sandbox's Docker controls, on their own.")
    ap.add_argument("--parcelround", required=True, help="a ParcelRound checkout holding f42242e")
    ap.add_argument("--work", required=True, help="a new or empty directory for the clone")
    a = ap.parse_args(argv)
    source, work = Path(a.parcelround), Path(a.work)
    ok, why = docker_status()          # first: nothing runs docker before this says it is there
    if not ok:
        print(f"REFUSED: {why}")
        return 2
    print("== docker ps")
    try:
        ps = subprocess.run(["docker", "ps", "--format", "{{.Names}}"], capture_output=True, text=True,
                            timeout=60)
    except (OSError, subprocess.TimeoutExpired) as e:
        print(f"REFUSED: docker ps did not answer ({type(e).__name__})")
        return 2
    names = ps.stdout.split()
    print(f"   {len(names)} containers running; of them named hh-sbx-: {[n for n in names if n.startswith('hh-sbx-')]}")
    if not source.is_dir():
        print("REFUSED: <source> is not a directory")
        return 2
    if work.exists() and any(work.iterdir()):
        print("REFUSED: <work> is not empty; give a new directory")
        return 2
    work.mkdir(parents=True, exist_ok=True)
    held = [("the Docker tests", docker_tests()), ("the mounted gate", gate_control(source, work))]
    print("== summary")
    for name, h in held:
        print(f"   {name:18} {'held' if h else 'NOT HELD'}")
    print(f"controls: {sum(h for _, h in held)} of {len(held)} held")
    return 0 if all(h for _, h in held) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
