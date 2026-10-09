"""Helpers for QS4h's tests, and no tests of their own.

A synthetic world in this round's shape is built with git in a temporary directory:
- a HonestHarness-like history: a root, a base, and two parcels' tips. P1's tip is
  three commits above the base, a merge of the base among them, so its copy is a squash
  (P4's shape); P2's is one commit above the base (P2's and P3's shape). P1 has a plant
  of two edits and a plant of one; P2 has two deletions, a line and a block;
- a ledger directory: stamped files the cut cuts at each stamp, the lead's entries
  naming each tip and copy by short and full SHA, the shared briefs with a priority item
  to remove and a time after both stamps, briefs before them, each parcel's own file,
  keys/ and a later entry that names the plants;
- a ParcelRound-like repository, an outside source's repository, and two documentation
  copies;
- items and expected data in qs4h's shapes, the expected written by QS4h's own tools.
Each copy's expected SHA comes by a second route, independent of the rebuilder: the
planted tree from a working tree and `git write-tree`, then `git commit-tree` on the
base with the tip's author and committer and the oldest commit's message.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from qs.agent import Mount
from qs.agent.scripted import tool_call
from qs.fake import FakeReply, reply
from qs.suites import qs4, qs4h

ROOT = Path(__file__).resolve().parent.parent
ZONE = timezone(timedelta(hours=-7))
WHO = {"GIT_AUTHOR_NAME": "Parcel", "GIT_AUTHOR_EMAIL": "parcel@example.invalid",
       "GIT_COMMITTER_NAME": "Parcel", "GIT_COMMITTER_EMAIL": "parcel@example.invalid"}


def load_tool(name: str):
    spec = importlib.util.spec_from_file_location(f"hh_{name}", ROOT / "tools" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def g(repo: Path, *args: str, date: str = "2026-10-06T09:00:00-07:00", input: bytes | None = None) -> str:
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date, **WHO)
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, env=env, input=input,
                          check=True).stdout.decode("utf-8")


def put(root: Path, rel: str, text: str | bytes, when: str | None = None) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(text.encode("utf-8") if isinstance(text, str) else text)
    if when:
        t = datetime.strptime(when, "%Y-%m-%d %H:%M:%S").replace(tzinfo=ZONE).timestamp()
        os.utime(p, (t, t))
    return p


def commit(repo: Path, msg: str, date: str) -> str:
    g(repo, "add", "-A")
    g(repo, "commit", "-q", "-m", msg, date=date)
    return g(repo, "rev-parse", "HEAD").strip()


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def entry(stamp: str, headline: str, body: str) -> str:
    return f"\n## {stamp} -0700 - {headline}\n\n{body}\n"


# P1's files: a golden in a JSON-like data file (plant A, two edits) and a scan (plant B).
CASES = "".join(f'  "line {n}": {n},\n' for n in range(1, 31))
CASES = (CASES.replace('  "line 10": 10,\n', '  "priority": {"equals": "high"},\n')
         .replace('  "line 20": 20,\n', '  "priority": "high",\n'))
SCAN = "".join(f"step_{n} = {n}\n" for n in range(1, 41)).replace(
    "step_25 = 25\n", "places += [(\"call's name\", name), (\"call's arguments\", args)]\n")
P1_PLANTS = [
    {"id": "A", "file": "qs/cases.json", "old": '  "priority": {"equals": "high"},\n',
     "new": '  "priority": {"equals": "normal"},\n', "shape": "a golden that contradicts its prompt (edit 1 of 2)"},
    {"id": "A", "file": "qs/cases.json", "old": '  "priority": "high",\n', "new": '  "priority": "normal",\n',
     "shape": "the same golden's canonical value (edit 2 of 2)"},
    {"id": "B", "file": "qs/scan.py", "old": "places += [(\"call's name\", name), (\"call's arguments\", args)]\n",
     "new": "places += [(\"call's arguments\", args)]\n", "shape": "the scan drops a call's name"}]
# P2's file: a loop with a reset (plant A deletes it) and a time check (plant B deletes it).
LOOP = "".join(f"line_{n} = {n}\n" for n in range(1, 61))
LOOP = (LOOP.replace("line_20 = 20\n", "if elapsed() >= budget:\n    end('run_seconds')\n    continue\n")
        .replace("line_40 = 40\n", "    continue\nstreak = 0\ntry:\n"))
P2_PLANTS = [
    {"id": "A", "file": "qs/loop.py", "old": "    continue\nstreak = 0\ntry:\n", "new": "    continue\ntry:\n",
     "shape": "the streak is never reset"},
    {"id": "B", "file": "qs/loop.py", "old": "if elapsed() >= budget:\n    end('run_seconds')\n    continue\n",
     "new": "", "shape": "the time is checked only before turns"}]
STAMPS = {"P1": "2026-10-06 13:00:00", "P2": "2026-10-06 17:00:00"}   # the shared briefs' times fall between
PRIORITY = ("- Run a test at low priority while the owner uses the desktop: set at 15:35:17, lifted at\n"
            "  16:39:34; run through `lowprio.py`.\n")


def independent_copy(repo: Path, base: str, tip: str, oldest: str, plants: list, work: Path) -> str:
    """The second route to a copy's SHA (see the module's docstring)."""
    clone = work / f"ind-{tip[:7]}"
    g(work, "clone", "-q", str(repo), str(clone))
    g(clone, "checkout", "-q", "--detach", tip)
    for p in plants:
        f = clone / p["file"]
        f.write_bytes(f.read_bytes().replace(p["old"].encode(), p["new"].encode(), 1))
    g(clone, "add", "-A")
    tree = g(clone, "write-tree").strip()
    raw = subprocess.run(["git", "-C", str(clone), "cat-file", "commit", tip], capture_output=True, check=True).stdout
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    for line in raw.partition(b"\n\n")[0].split(b"\n"):
        m = re.match(rb"^(author|committer) (.*) <(.*)> (\d+ [+-]\d{4})$", line)
        if m:
            who = m.group(1).decode().upper()
            env.update({f"GIT_{who}_NAME": m.group(2).decode(), f"GIT_{who}_EMAIL": m.group(3).decode(),
                        f"GIT_{who}_DATE": m.group(4).decode()})
    msg = subprocess.run(["git", "-C", str(clone), "cat-file", "commit", oldest], capture_output=True,
                         check=True).stdout.partition(b"\n\n")[2]
    return subprocess.run(["git", "-C", str(clone), "commit-tree", tree, "-p", base], input=msg, capture_output=True,
                          env=env, check=True).stdout.decode().strip()


@dataclass
class World:
    root: Path
    hh: Path
    ledger: Path
    pr: Path
    repos: Path
    ds: Path
    items_path: Path
    expected_path: Path
    qs4_expected: Path
    local: Path
    items: dict
    keys: dict
    copies: dict
    tips: dict
    base: str
    oldest: dict


def build_world(root: Path) -> World:
    root.mkdir(parents=True, exist_ok=True)
    hh = root / "hh"
    hh.mkdir()
    g(hh, "init", "-q", "-b", "main")
    put(hh, ".gitattributes", "* text=auto eol=lf\n")
    put(hh, "Rounds/ParcelRound-R6/PLAN.md", "# round 6's plan\n")
    first = commit(hh, "the root", "2026-10-06T08:00:00-07:00")
    put(hh, "README.md", "the project\n")
    base = commit(hh, "the base", "2026-10-06T10:00:00-07:00")
    # P1: a branch from below the base, the base merged in, then the tip
    g(hh, "checkout", "-q", "-b", "p1", first)
    put(hh, "qs/cases.json", "{\n" + CASES + "}\n")
    put(hh, "qs/scan.py", SCAN)
    p1a = commit(hh, "P1: the suite, 95 tests\n\nCo-Authored-By: Parcel <parcel@example.invalid>",
                 "2026-10-06T11:00:00-07:00")
    g(hh, "merge", "-q", "--no-ff", "-m", "merge the base", base, date="2026-10-06T11:30:00-07:00")
    put(hh, "qs/scan.py", SCAN + "step_41 = 41\n")
    t1 = commit(hh, "P1: one more step, 96 tests", "2026-10-06T12:00:00-07:00")
    # P2: one commit above the base
    g(hh, "checkout", "-q", "-b", "p2", base)
    put(hh, "qs/loop.py", LOOP)
    t2 = commit(hh, "P2: the loop", "2026-10-06T12:30:00-07:00")
    g(hh, "checkout", "-q", "main")
    work = root / "independent"
    work.mkdir()
    c1 = independent_copy(hh, base, t1, p1a, P1_PLANTS, work)
    c2 = independent_copy(hh, base, t2, t2, P2_PLANTS, work)
    keys = {"P1": {"real_tip": t1, "base": base, "copy_commit": c1, "plants": P1_PLANTS},
            "P2": {"real_tip": t2, "base": base, "copy_commit": c2, "plants": P2_PLANTS}}
    # the ledger
    ledger = root / "ledger"
    lead = ("# the lead's ledger\n"
            + entry("2026-10-06 10:00:00", "the round opens", "Measured: the plan.")
            + entry(STAMPS["P1"], "verifier-P1's copy is built",
                    f"- P1 committed at {t1[:7]} on r1-p1; its first commit is {p1a[:7]}.\n"
                    f"- The copy is at commit {c1[:7]}, full {c1}, on the base {base[:7]}; "
                    f"key-{c1[:7]}.json is sealed.")
            + entry(STAMPS["P2"], "verifier-P2's copy is built",
                    f"- P2 at {t2[:7]}, also {t2[:12]}; the copy {c2[:7]} on {base[:7]}.")
            + entry("2026-10-06 22:00:00", "the keys", "- P1-A made the priority normal; the streak is never reset."))
    put(ledger, "lead.md", lead, "2026-10-06 22:00:00")
    put(ledger, "README.md", "# The round ledger\n\nRead every file here.\n", "2026-10-06 09:00:00")
    common = "# What every parcel's brief shares\n\n## Do not\n\n- Commit to main.\n" + PRIORITY + "\n## Report\n"
    verifier = "# What every verifier's brief shares\n\n1. Read.\n2. Stop.\n" + PRIORITY + "\n## A copy\n"
    put(ledger, "briefs/_common.md", common, "2026-10-06 16:39:42")
    put(ledger, "briefs/_verifier.md", verifier, "2026-10-06 16:39:44")
    for p in ("P1", "P2"):
        put(ledger, f"briefs/{p}.md", f"# {p}'s brief\n", "2026-10-06 09:30:00")
        put(ledger, f"briefs/verifier-{p}.md", f"# verifier-{p}'s brief\n", "2026-10-06 09:31:00")
        put(ledger, f"{p}.md", f"# {p}\n" + entry("2026-10-06 11:00:00", "design", "my design"), "2026-10-06 11:00:00")
    put(ledger, "briefs/late.md", "# a brief written between the stamps\n", "2026-10-06 13:30:00")
    put(ledger, "verifier-P0.md", "# verifier-P0\n" + entry("2026-10-06 10:30:00", "starts", "a")
        + entry("2026-10-06 13:45:00", "later", "b"), "2026-10-06 13:45:00")
    key_files = {}
    for p, k in keys.items():
        data = json.dumps(k, indent=2).encode()
        put(ledger, f"keys/key-{k['copy_commit'][:7]}.json", data, "2026-10-06 22:00:00")
        key_files[p] = (f"keys/key-{k['copy_commit'][:7]}.json", sha(data))
    # ParcelRound, an outside source, and the documentation copies
    pr = root / "pr"
    pr.mkdir()
    g(pr, "init", "-q", "-b", "main")
    put(pr, "README.md", "ParcelRound\n")
    put(pr, "archive/round6-ledger.zip", b"PK\x05\x06" + b"\0" * 18)
    pr_commit = commit(pr, "round 6's archive", "2026-10-03T01:00:00-07:00")
    repos = root / "repos"
    (repos / "srcrepo").mkdir(parents=True)
    g(repos / "srcrepo", "init", "-q", "-b", "main")
    put(repos / "srcrepo", "docs/V.md", "It found five wrong answers.\n")
    src_commit = commit(repos / "srcrepo", "a source", "2026-09-28T12:00:00-07:00")
    ds = root / "ds"
    put(ds, "thinking.txt", "the thinking page\n", "2026-10-06 09:08:00")
    put(ds, "chat_completion_full.txt", "the chat page\n", "2026-10-06 10:49:38")
    src_files = {"srcrepo/docs/V.md": b"It found five wrong answers.\n"}
    qs4_expected = root / "qs4_expected.json"
    qs4_expected.write_text(json.dumps({"sources": {"digest": qs4.tree_digest(src_files)}}), encoding="utf-8")
    # the items
    rebuild = {"about": "a test", "parcels": ["P1"], "edits": []}
    for rel in ("briefs/_common.md", "briefs/_verifier.md"):
        data = (ledger / rel).read_bytes()
        lines = data.splitlines(keepends=True)
        a = next(i for i, x in enumerate(lines, 1) if x.startswith(b"- Run a test at low priority"))
        rebuild["edits"].append({"file": rel, "lines": [a, a + 1], "source_sha256": sha(data),
                                 "removed_sha256": sha(b"".join(lines[a - 1:a + 1])),
                                 "absent": ["15:35:17", "16:39:34", "lowprio"]})
    items = {
        "format": 1, "ledger": {"name": qs4h.LEDGER_MOUNT, "zone": "-07:00"},
        "parcelround": {"commit": pr_commit, "mount": qs4h.PR_MOUNT, "dir": qs4h.PR_DIR},
        "sources": [{"name": "srcrepo", "commit": src_commit, "paths": ["docs/V.md"]}],
        "caps": {"max_prompt_tokens": 200_000, "max_output_tokens": 20_000, "max_call_prompt_tokens": 50_000},
        "budgets": {"max_turns": 8, "max_run_seconds": 600, "call_timeout_seconds": 30, "max_output_chars": 4000,
                    "malformed_retries": 3, "nudges": 1, "max_calls_per_turn": 16, "max_scratch_bytes": 1 << 20,
                    "max_tokens_per_turn": 4096},
        "settings": {"stream": False, "tolerance": 2, "deletion_tolerance": 6, "ledger_file_cap": 100_000,
                     "first_run": "h1-planted"},
        "required_briefs": ["README.md", "lead.md", "briefs/_verifier.md", "briefs/_common.md"],
        "briefs_rebuild": rebuild,
        "parcels": {
            "P1": {"copy": c1, "tip": t1, "base": base, "key": key_files["P1"][0], "key_sha256": key_files["P1"][1],
                   "stamp": STAMPS["P1"], "view": "13:20:00", "report": "13:30:00",
                   "original_gate": {"recorded": "a test", "gate": [2, 2], "control": [2, 2]},
                   "inputs": ["ds"], "adaptation": ["ds"],
                   "plants": [{"id": "P1-A", "key_id": "A", "shape": "figure", "about": "a test",
                               "markers": [["high", "normal"]]},
                              {"id": "P1-B", "key_id": "B", "shape": "rule", "about": "a test", "markers": [["name"]]}],
                   "recorded": [
                       {"id": "P1-v1", "class": "restate", "places": [{"file": "<commit message>", "lines": []}],
                        "in_view": True, "recorded": "a test", "copy_only": False},
                       {"id": "P1-v2", "class": "known limit", "places": [{"file": "qs/scan.py", "lines": [[5, 6]]}],
                        "in_view": False, "recorded": "a test", "copy_only": False}]},
            "P2": {"copy": c2, "tip": t2, "base": base, "key": key_files["P2"][0], "key_sha256": key_files["P2"][1],
                   "stamp": STAMPS["P2"], "view": "14:20:00", "report": "14:30:00",
                   "original_gate": {"recorded": "a test", "gate": [2, 2], "control": [2, 2]},
                   "inputs": ["parcelround", "sources"], "adaptation": ["parcelround", "docker"],
                   "plants": [{"id": "P2-A", "key_id": "A", "shape": "rule", "about": "a test", "markers": [["reset*"]]},
                              {"id": "P2-B", "key_id": "B", "shape": "rule", "about": "a test",
                               "markers": [["elapsed"]]}],
                   "recorded": [
                       {"id": "P2-v1", "class": "wrong answer", "places": [{"file": "qs/loop.py", "lines": [[50, 50]]}],
                        "in_view": True, "recorded": "a test", "copy_only": False},
                       {"id": "P2-v2", "class": "other", "places": [{"file": "ledger/lead.md", "lines": []}],
                        "in_view": False, "recorded": "a test", "copy_only": True}]}},
        "items": [{"id": f"h{n}-{k}", "parcel": f"P{n}", "kind": k} for n in (1, 2) for k in ("planted", "real")],
    }
    items_path, expected_path = root / "items.json", root / "expected.json"
    items_path.write_text(json.dumps(items, indent=1), encoding="utf-8")
    return World(root=root, hh=hh, ledger=ledger, pr=pr, repos=repos, ds=ds, items_path=items_path,
                 expected_path=expected_path, qs4_expected=qs4_expected, local=root / "local", items=items,
                 keys=keys, copies={"P1": c1, "P2": c2}, tips={"P1": t1, "P2": t2}, base=base,
                 oldest={"P1": p1a, "P2": t2})


def tool_args(w: World) -> dict[str, list[str]]:
    common = ["--local", str(w.local), "--items", str(w.items_path), "--expected", str(w.expected_path)]
    return {"rebuild": ["--ledger", str(w.ledger), "--parcelround", str(w.pr), "--repos", str(w.repos), "--ds",
                        str(w.ds), "--honestharness", str(w.hh), "--qs4-expected", str(w.qs4_expected),
                        "--no-gate", *common],
            "cut": ["--ledger", str(w.ledger), *common]}


def build_inputs(w: World, *, gate_image: str | None = "sha256:test-image") -> dict:
    """QS4h's own tools on the world: the rebuilder without the Docker step, then the
    cutter. A held gate comparison is then recorded with `gate_image`, standing in for
    the step a Docker test makes for real."""
    rebuild, cut = load_tool("qs4h_rebuild"), load_tool("qs4h_cut")
    args = tool_args(w)
    assert rebuild.main(args["rebuild"] + ["--write-expected"]) == 0
    assert cut.main(args["cut"] + ["--write-expected"]) == 0
    expected = json.loads(w.expected_path.read_text(encoding="utf-8"))
    if gate_image is not None:
        built = json.loads((w.local / "built.json").read_text(encoding="utf-8"))
        for iid, b in built["items"].items():
            b["gate"] = {"held": True, "commit": expected["repos"][iid]["commit"], "image_id": gate_image}
        (w.local / "built.json").write_text(json.dumps(built), encoding="utf-8")
    return expected


def copy_local(w: World, dest: Path) -> Path:
    shutil.copytree(w.local, dest)
    return dest


class StubInputs:
    """Prepared inputs with names only, for runs on P2's ScriptedSandbox, which mounts
    nothing: what scoring needs (file lists) from the given data."""

    def __init__(self, items: dict, expected: dict):
        self.items, self.expected, self.prepared = items, expected, []

    def prepare(self, item_id: str) -> qs4.Prepared:
        it = qs4h.item_spec(self.items, item_id)
        e = self.expected["repos"][item_id]
        self.prepared.append(item_id)
        mounts = [Mount(Path("."), qs4h.copy_mount(it["parcel"])), Mount(Path("."), qs4h.LEDGER_MOUNT)]
        return qs4.Prepared(mounts=mounts, repo_files=e["files"], cut_files=self.expected["cuts"][item_id]["files"],
                            source_files={}, facts={"commit": e["commit"][:12], "gate_held": True})

    def image_id(self) -> str:
        return "sha256:stub"


def report_call(call_id: str, findings: list, verdict: str = "NOT READY", text: str = "what I ran") -> dict:
    return tool_call(call_id, "report", {"verdict": verdict, "findings": findings, "text": text})


def turn(*calls, finish: str = "tool_calls") -> FakeReply:
    return reply(None, reasoning="thinking", tool_calls=list(calls), finish=finish, usage=(0, 300, 40, 10))
