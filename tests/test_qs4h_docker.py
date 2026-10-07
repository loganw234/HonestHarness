"""QS4h's sandbox image, and the project's gate on the host and in the sandbox, with real
containers: the image holds the 18 pins and no docker, and has no network; a gate that
means the same on both sides is held, and one that fails only on Linux is not. Skipped,
with the reason, when Docker or the recorded image is absent."""
from pathlib import Path

import pytest

from qs.suites import qs4, qs4h
from test_qs4h_support import commit, g, load_tool, put

try:
    IMAGE, WHY = qs4h.current_image_id(), ""
except qs4.InputError as e:
    IMAGE, WHY = None, f"the sandbox image: {e}"
pytestmark = pytest.mark.skipif(IMAGE is None, reason=WHY)

GATE = '''import sys
if "--control" in sys.argv:
    print("control tests     a failing test                                          caught")
    print("controls: 1 of 1 caught")
else:
    print("tests     ok    1 passed")
    print("PASS: 1 of 1 checks hold")
'''
LINUX_ONLY = GATE.replace('    print("PASS: 1 of 1 checks hold")',
                          '    if sys.platform.startswith("linux"):\n        print("tests     FAIL  1 failed")\n'
                          '        print("FAIL: 0 of 1 checks hold")\n        sys.exit(1)\n'
                          '    print("PASS: 1 of 1 checks hold")')


def test_the_image_holds_the_pins_and_no_docker_and_reaches_no_network(tmp_path):
    tool = load_tool("qs4h_image")
    found = tool.check_in_container(IMAGE, tmp_path / "scratch")
    want = tool.pins(tool.requirements(qs4h.DOCKERFILE_PATH.read_bytes()))
    assert {k: found["packages"].get(k) for k in want} == want and len(want) == 18
    assert found["pip_check"][0] == 0 and found["docker_absent"] and found["network_refused"] and found["removed"]
    assert found["python"].startswith("Python 3.12")


def repo_with(root: Path, script: str) -> Path:
    root.mkdir(parents=True)
    g(root, "init", "-q", "-b", "main")
    put(root, ".gitattributes", "* text=auto eol=lf\n")
    put(root, "tools/check.py", script)
    commit(root, "a gate", "2026-10-06T20:00:00-07:00")
    return root


def compare(tmp_path: Path, script: str):
    repo = repo_with(tmp_path / "repo", script)
    (tmp_path / "work").mkdir()
    host = qs4h.run_gate_host(repo, tmp_path / "work", timeout=300)
    box = qs4h.run_gate_sandbox(repo, "r1-vP1-copy", tmp_path / "sbx", image=IMAGE, timeout=300)
    assert box["removed"] and host["clean_after"] and box["clone"]["exit"] == 0
    return qs4.compare_gate(host, box), host, box


def test_a_gate_that_means_the_same_on_both_sides_is_held(tmp_path):
    (held, detail), host, box = compare(tmp_path, GATE)
    assert held and detail == "the verdicts match"
    assert box["gate"]["parsed"]["verdict"] == ["PASS", 1, 1] and box["control"]["parsed"]["controls"] == [1, 1]
    assert box["gate"]["duration_s"] > 0 and host["gate"]["duration_s"] > 0


def test_a_gate_that_fails_only_on_linux_is_not_held(tmp_path):
    (held, detail), host, box = compare(tmp_path, LINUX_ONLY)
    assert host["gate"]["parsed"]["verdict"] == ["PASS", 1, 1] and box["gate"]["parsed"]["verdict"][0] == "FAIL"
    assert not held and detail.startswith("gate:")
