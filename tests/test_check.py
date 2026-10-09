"""The gate's privacy patterns: each form of a home path this desktop can
produce is caught, placeholders and URLs pass, and the gate's own source is
clean, since the privacy check reads it too. Every path here is built at run
time from pieces, so this file holds none."""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("hh_check", ROOT / "tools" / "check.py")
check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check)

U = "Us" + "ers"
NAME = "some" + "one"
BS = chr(92)    # a backslash

HOME_FORMS = [
    "C:" + BS + U + BS + NAME + BS + "x",                  # Windows
    "C:/" + U + "/" + NAME + "/x",                         # Windows, forward slashes
    BS + U + BS + NAME + BS + "x",                         # drive-less
    "/c/" + U + "/" + NAME + "/x",                         # Git Bash
    "/mnt/c/" + U + "/" + NAME + "/x",                     # WSL
    "/cygdrive/c/" + U + "/" + NAME + "/x",                # Cygwin
    "/run/desktop/mnt/host/c/" + U + "/" + NAME + "/x",    # Docker Desktop
    "/host_mnt/c/" + U + "/" + NAME + "/x",                # Docker Desktop, older
    "/" + U + "/" + NAME + "/x",                           # macOS
    "/ho" + "me/" + NAME + "/x",                           # Linux
]


@pytest.mark.parametrize("text", HOME_FORMS)
def test_each_home_path_form_is_caught(text):
    assert [kind for kind, _ in check.findings("see " + text)] == ["path"]


@pytest.mark.parametrize("text", [
    "<repos>/HonestHarness",
    "/c/" + U + "/<name>/x",
    "https://api.github.com/users/x",
    "the " + U + " of the harness",
])
def test_placeholders_and_urls_pass(text):
    assert check.findings(text) == []


def test_the_gate_reads_clean_in_its_own_source():
    assert check.findings((ROOT / "tools" / "check.py").read_text(encoding="utf-8")) == []
