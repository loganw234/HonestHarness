"""Round 6's gate run on the host and in P2's sandbox, compared, on a synthetic
repository with a stand-in gate: held when the two places agree, and not held
when the gate fails only on Linux, the shape CS7 L221 records. Skipped, with the
reason, when Docker or P2's pinned image is absent."""
from pathlib import Path

import pytest

from qs.agent import docker_status
from qs.suites import qs4
from test_qs4_support import GATE_SCRIPT, commit, g, put

OK, WHY = docker_status()
pytestmark = pytest.mark.skipif(not OK, reason=WHY)

LINUX_ONLY = GATE_SCRIPT.replace(
    'print("PASS: 2 of 2 checks hold")',
    'import sys\n    if sys.platform.startswith("linux"):\n        print("quoted     FAIL  a passage")\n'
    '        print("FAIL: 1 of 2 checks hold")\n        sys.exit(1)\n    print("PASS: 2 of 2 checks hold")')


def repo_with(root: Path, script: str) -> Path:
    root.mkdir(parents=True)
    g(root, "init", "-q", "-b", "main")
    put(root, ".gitattributes", "* text=auto eol=lf\n")
    put(root, "tools/check_method.py", script)
    commit(root, "a gate", "2026-10-02T20:00:00-07:00")
    return root


def compare(tmp_path: Path, script: str):
    repo = repo_with(tmp_path / "repo", script)
    (tmp_path / "work").mkdir()
    host = qs4.run_gate_host(repo, tmp_path / "work")
    box = qs4.run_gate_sandbox(repo, "r6-vcopy-P1", tmp_path / "sbx")
    assert box["removed"] and host["clean_after"]
    return qs4.compare_gate(host, box), host, box


def test_a_gate_that_means_the_same_on_the_host_and_in_the_sandbox_is_held(tmp_path):
    (held, detail), host, box = compare(tmp_path, GATE_SCRIPT)
    assert held and detail == "the verdicts match"
    assert box["gate"]["parsed"]["verdict"] == ["PASS", 2, 2] and box["control"]["parsed"]["controls"] == [2, 2]


def test_a_gate_that_fails_only_on_linux_is_not_held(tmp_path):
    (held, detail), host, box = compare(tmp_path, LINUX_ONLY)
    assert host["gate"]["parsed"]["verdict"] == ["PASS", 2, 2] and box["gate"]["parsed"]["verdict"][0] == "FAIL"
    assert not held and detail.startswith("gate:")
