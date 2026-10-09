"""The HonestHarness gate: `python tools/check.py`, and `python tools/check.py
--control` to watch each check fail on a planted fault.

Threat model (stated before the gate's first verifier pass, as ParcelRound's
case study 6 proposes, CS6#1). The gate guards against two things:
- drift by honest, fallible authors:
  - code that stops doing what its tests say;
  - a run record that no longer matches its schema;
  - the spending guard's arithmetic drifting from its pinned fixtures:
    costs, rate periods, refusals and reconciliation classes;
  - live mode, which spends money, switched on outside the lead's live entry
    point;
- accidental publication: a provider key, a personal address or a
  home-directory path written into a tracked file or a commit message, the
  way pasted output or a careless note carries one.

It does not guard against deliberate evasion, meaning code written to pass
the gate, and it does not judge content: whether a suite measures what it
claims, or whether a record says what happened. Verifiers do that.

A fault built against the gate is judged against this paragraph. Inside the
threat model, the gate must catch the fault or a limit below must state it.
Outside the model, the fault is out of scope.

Checks:
  tests     the unit tests pass (pytest).
  schema    every run record under records/runs/ validates against
            qs/schema/run_record.schema.json. Every spend line has its fields
            and a decimal cost. The other record files are JSON lines.
  guard     the guard's arithmetic equals tests/fixtures/guard_fixtures.json,
            values computed by hand: costs, rate periods, reconciliation
            classes and refusals.
  privacy   no personal path, address or key-shaped token appears in a file
            git would commit (tracked, or untracked and not ignored), this
            gate's own source included, nor in a commit message on HEAD's
            history. A finding is printed masked. The home-path forms are
            listed at PATTERNS: Windows, drive-less, Git Bash, WSL, Cygwin,
            Docker Desktop's host mounts, macOS and Linux.
  livegate  no Python file sets live=True except the lead's live entry point,
            tools/live.py, and the live gate's own tests,
            tests/test_client_and_keys.py, which set it to prove the refusals
            and reach no network. No test names the real key's variable.

What it cannot see (each limit stated by the behaviour it concedes):
  - tests: a behaviour no test exercises can change unseen. The tests are
    content, and verifiers judge them. The spending guard's bounds each have
    a test: the reconciliation tolerance, the worst case with
    max_call_prompt_tokens, the token estimate, the max_tokens clamp, the
    per-call size check, the peak stop inside a batch, and redaction of
    provider errors.
  - schema: a record that matches its schema and says something false
    passes.
  - guard: the price table itself is checked only against the fixtures, and
    the fixtures only against hand arithmetic. A price that is wrong in both
    passes. The live reconciliation is what checks prices against a bill.
  - privacy:
    - a home path in a form not listed at PATTERNS passes;
    - a value spelled out, split across lines, or encoded passes;
    - an address in an allowed or reserved domain passes;
    - a key in a shape not listed passes;
    - in a copy with no git history, commit messages are not read.
  - livegate: live mode switched on by any other spelling passes: a
    variable, keyword expansion, or reflection. A Client built directly
    against a provider host still fails at runtime, without a reservation.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ALLOWED_ADDRESSES = {"noreply@anthropic.com"}
RESERVED = re.compile(r"(?i)(^|\.)(example\.(com|org|net)|invalid|test|localhost)$")
_HOME_NAME = r"[A-Za-z0-9][A-Za-z0-9._-]*"
PATTERNS = {
    # A home directory, in the forms one reaches this desktop by: Windows
    # (C:\Users\<name>, C:/Users/<name>), drive-less (\Users\<name>), Git Bash
    # (/c/Users/<name>), WSL (/mnt/c/Users/<name>), Cygwin
    # (/cygdrive/c/Users/<name>), Docker Desktop's host mounts
    # (/run/desktop/mnt/host/c/Users/<name>, /host_mnt/c/Users/<name>), and
    # macOS and Linux (/Users/<name>, /home/<name>).
    "path": re.compile(
        r"(?i)(?<![A-Za-z0-9])[a-z]:[\\/]+(users|documents and settings)[\\/]+" + _HOME_NAME
        + r"|(?<![A-Za-z0-9.:\\])\\users\\" + _HOME_NAME
        + r"|(?<![A-Za-z0-9.])(/mnt|/cygdrive|/host_mnt|/run/desktop/mnt/host)?/[a-z]/users/"
        + _HOME_NAME
        + r"|(?<![A-Za-z0-9.])/(users|home)/" + _HOME_NAME),
    "address": re.compile(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9-]+\.)+[A-Za-z]{2,}"),
    "key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}|(?i:\bbearer\s+)[A-Za-z0-9._~+/-]{24,}"
                      r"|(?i:DEEPSEEK_API_KEY\s*[=:]\s*)[\"']?[A-Za-z0-9_-]{16,}"),
}
# Placeholders a document may use for a home: <name>, <user>, and the like.
PLACEHOLDER = re.compile(r"[\\/](<[^>]*>|\{[^}]*\}|\$\w+|%\w+%)")
LIVE_ENTRY = "tools/live.py"
LIVE_ALLOWED = {LIVE_ENTRY, "tools/check.py", "tests/test_client_and_keys.py"}
KEY_VAR = "DEEPSEEK_API_KEY"


# -- helpers ------------------------------------------------------------------
def files(root: Path) -> list[Path]:
    if (root / ".git").exists():
        out = subprocess.run(["git", "-C", str(root), "ls-files", "-co", "--exclude-standard"],
                             capture_output=True, text=True, check=True).stdout
        return [root / p for p in out.splitlines() if p]
    skip = {".git", "__pycache__", ".pytest_cache", "transcripts"}
    return [Path(d) / f for d, ds, fs in os.walk(root)
            for f in fs if not (set(Path(d).relative_to(root).parts) & skip)]


def read(p: Path) -> str | None:
    try:
        data = p.read_bytes()
    except OSError:
        return None
    if b"\0" in data[:4096]:
        return None
    return data.decode("utf-8", errors="replace")


def mask(s: str) -> str:
    return s[:4] + "..." + f"[{len(s)} chars]"


def findings(text: str) -> list[tuple[str, str]]:
    out = []
    for kind, pat in PATTERNS.items():
        for m in pat.finditer(text):
            s = m.group(0)
            if kind == "address":
                domain = s.split("@", 1)[1].lower()
                if s.lower() in ALLOWED_ADDRESSES or RESERVED.search(domain):
                    continue
            if kind == "path" and PLACEHOLDER.search(s[-len(m.group(0)):]):
                continue
            out.append((kind, s))
    return out


# -- checks -------------------------------------------------------------------
def check_tests(root: Path) -> tuple[list[str], str]:
    # pyproject's addopts already give -q; a second -q would drop the count line.
    r = subprocess.run([sys.executable, "-m", "pytest", "-p", "no:cacheprovider",
                        "-W", "ignore"], cwd=root, capture_output=True, text=True)
    tail = (r.stdout.strip().splitlines() or [""])[-1]
    return ([] if r.returncode == 0 else [f"pytest failed: {tail}"]), tail


def check_schema(root: Path) -> tuple[list[str], str]:
    sys.path.insert(0, str(root))
    try:
        import importlib
        rec = importlib.import_module("qs.record")
        importlib.reload(rec)
        bad, n = [], 0
        runs = root / "records" / "runs"
        for p in sorted(runs.glob("*.jsonl")) if runs.is_dir() else []:
            for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                if not line.strip():
                    continue
                n += 1
                try:
                    rec.validate(json.loads(line))
                except Exception as e:  # noqa: BLE001
                    bad.append(f"{p.relative_to(root)}:{i}: {str(e).splitlines()[0]}")
        spend = root / "records" / "spend.jsonl"
        if spend.exists():
            for i, line in enumerate(spend.read_text(encoding="utf-8").splitlines(), 1):
                if not line.strip():
                    continue
                n += 1
                try:
                    d = json.loads(line)
                    Decimal(d["cost_usd"])
                    for k in ("batch", "record", "model", "period", "price_table"):
                        d[k]
                except Exception as e:  # noqa: BLE001
                    bad.append(f"records/spend.jsonl:{i}: {e!r}")
        for name in ("batches.jsonl", "identity.jsonl"):
            p = root / "records" / name
            if p.exists():
                for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                    if line.strip():
                        n += 1
                        try:
                            json.loads(line)
                        except ValueError as e:
                            bad.append(f"records/{name}:{i}: {e}")
        return bad, f"{n} record lines read"
    finally:
        sys.path.remove(str(root))


def check_guard(root: Path) -> tuple[list[str], str]:
    sys.path.insert(0, str(root))
    try:
        import importlib
        from datetime import datetime
        prices_mod = importlib.reload(importlib.import_module("qs.prices"))
        guard_mod = importlib.reload(importlib.import_module("qs.guard"))
        fx = json.loads((root / "tests" / "fixtures" / "guard_fixtures.json").read_text(encoding="utf-8"))
        table = prices_mod.PriceTable.load(root / fx["price_table"])
        bad, n = [], 0
        for c in fx["costs"]:
            n += 1
            got = table.cost(c["model"], c["period"], prices_mod.Usage(*c["usage"]))
            if got != Decimal(c["cost"]):
                bad.append(f"cost {c['model']} {c['period']} {c['usage']}: {got} != {c['cost']}")
        for c in fx["periods"]:
            n += 1
            got = table.period(datetime.fromisoformat(c["utc"]))
            if got != c["period"]:
                bad.append(f"period {c['utc']}: {got} != {c['period']}")
        for c in fx["reconcile"]:
            n += 1
            d = lambda v: None if v is None else Decimal(v)  # noqa: E731
            got = guard_mod.reconcile(d(c["before"]), d(c["after"]), Decimal(c["computed"]),
                                      {k: Decimal(v) for k, v in c["alternatives"].items()}).status
            if got != c["status"]:
                bad.append(f"reconcile {c}: {got} != {c['status']}")
        for c in fx["refusals"]:
            n += 1
            with tempfile.TemporaryDirectory() as td:
                g = guard_mod.SpendGuard(Decimal(c["ceiling"]), Path(td) / "spend.jsonl")
                if Decimal(c["spent"]):
                    g.record(batch="x", record_id="x", model="m", period="off_peak",
                             price_table="t", cost=Decimal(c["spent"]))
                try:
                    g.reserve("x", Decimal(c["worst"]), None if c["balance"] is None
                              else Decimal(c["balance"]))
                    refused = False
                except guard_mod.Refused:
                    refused = True
            if refused != c["refused"]:
                bad.append(f"refusal {c}: refused={refused}")
        return bad, f"{n} fixtures checked"
    finally:
        sys.path.remove(str(root))


def check_privacy(root: Path) -> tuple[list[str], str]:
    bad, n = [], 0
    for p in files(root):
        text = read(p)
        if text is None:
            continue
        n += 1
        for kind, s in findings(text):
            bad.append(f"{p.relative_to(root)}: a {kind}, {mask(s)}")
    msgs = 0
    if (root / ".git").exists():
        out = subprocess.run(["git", "-C", str(root), "log", "--format=%H%x00%B%x01"],
                             capture_output=True, text=True, encoding="utf-8").stdout
        for entry in out.split("\x01"):
            if "\x00" not in entry:
                continue
            sha, body = entry.split("\x00", 1)
            msgs += 1
            for kind, s in findings(body):
                bad.append(f"commit {sha.strip()[:7]}: a {kind}, {mask(s)}")
    return bad, f"{n} files and {msgs} commit messages read"


def check_livegate(root: Path) -> tuple[list[str], str]:
    bad, n = [], 0
    live = re.compile(r"\blive\s*=\s*True\b")
    for p in files(root):
        if p.suffix != ".py":
            continue
        rel = p.relative_to(root).as_posix()
        text = read(p) or ""
        n += 1
        if rel not in LIVE_ALLOWED and live.search(text):
            bad.append(f"{rel}: sets live=True outside {LIVE_ENTRY}")
        if rel.startswith("tests/") and KEY_VAR in text:
            bad.append(f"{rel}: a test names {KEY_VAR}")
    return bad, f"{n} Python files read"


CHECKS = [("tests", check_tests), ("schema", check_schema), ("guard", check_guard),
          ("privacy", check_privacy), ("livegate", check_livegate)]


def run(root: Path) -> int:
    failed = 0
    for name, fn in CHECKS:
        bad, summary = fn(root)
        print(f"{name:9} {'ok' if not bad else 'FAIL':5} {summary}")
        for b in bad[:20]:
            print(f"          {b}")
        failed += bool(bad)
    print(f"{'PASS' if not failed else 'FAIL'}: {len(CHECKS) - failed} of {len(CHECKS)} checks hold")
    return 1 if failed else 0


# -- controls: each check watched to fail -----------------------------------------
def _copy(root: Path, dest: Path) -> Path:
    for p in files(root):
        rel = p.relative_to(root)
        if rel.parts and rel.parts[0] in ("transcripts",):
            continue
        t = dest / rel
        t.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, t)
    return dest


def _plant_test(r: Path):
    (r / "tests" / "test_planted.py").write_text("def test_planted():\n    assert False\n")


def _plant_record(r: Path):
    d = r / "records" / "runs"
    d.mkdir(parents=True, exist_ok=True)
    (d / "planted.jsonl").write_text(json.dumps({"record_version": 1, "record_id": "x"}) + "\n")


def _plant_price(r: Path):
    p = r / "prices" / "deepseek-2026-10-06.json"
    p.write_text(p.read_text(encoding="utf-8").replace('"cache_miss": "0.15"',
                                                       '"cache_miss": "0.16"', 1))


def _plant_key(r: Path):
    (r / "notes.md").write_text("pasted: sk-" + "Ab3" * 11 + "\n")


def _plant_address(r: Path):
    # Built at run time, so the gate's own source holds no address: the
    # privacy check reads this file too.
    (r / "notes.md").write_text("mail someone" + "@" + "personal-domain.net\n")


def _plant_path(r: Path):
    (r / "notes.md").write_text("see " + "C:" + "\\" + "Users" + "\\" + "someone\\x.txt\n")


def _plant_wsl_path(r: Path):
    (r / "notes.md").write_text("see /mnt/c/" + "Users" + "/someone/x.txt\n")


def _plant_path_in_gate(r: Path):
    p = r / "tools" / "check.py"
    p.write_text(p.read_text(encoding="utf-8") + "# pasted: /c/" + "Users" + "/someone/x\n",
                 encoding="utf-8")


def _plant_live(r: Path):
    (r / "qs" / "planted.py").write_text("from qs.client import Client\n"
                                         "c = Client('https://api.deepseek.com', live=True)\n")


CONTROLS = [
    ("tests", "a failing test", _plant_test),
    ("schema", "a run record missing its fields", _plant_record),
    ("guard", "a price drifted from the fixtures", _plant_price),
    ("privacy", "a key-shaped token", _plant_key),
    ("privacy", "a personal address", _plant_address),
    ("privacy", "a home-directory path", _plant_path),
    ("privacy", "a home path in WSL's form", _plant_wsl_path),
    ("privacy", "a home path pasted into the gate itself", _plant_path_in_gate),
    ("livegate", "live mode switched on outside the live entry point", _plant_live),
]


def control(root: Path) -> int:
    base_bad = [n for n, fn in CHECKS if fn(root)[0]]
    if base_bad:
        print(f"CONTROL REFUSED: the tree fails before any plant ({', '.join(base_bad)})")
        return 1
    caught = 0
    for check, what, plant in CONTROLS:
        with tempfile.TemporaryDirectory() as td:
            r = _copy(root, Path(td) / "copy")
            plant(r)
            fn = dict(CHECKS)[check]
            ok = bool(fn(r)[0])
        print(f"control {check:9} {what:55} {'caught' if ok else 'NOT CAUGHT'}")
        caught += ok
    print(f"controls: {caught} of {len(CONTROLS)} caught")
    return 0 if caught == len(CONTROLS) else 1


if __name__ == "__main__":
    root = ROOT
    sys.exit(control(root) if "--control" in sys.argv[1:] else run(root))
