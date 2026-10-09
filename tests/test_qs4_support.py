"""Helpers for QS4's tests, and no tests of its own.

A synthetic world in round 6's shape is built with git in a temporary directory:
- a ParcelRound-like history: a base; two parcels' tips (P1 holds both its plants
  in one file, P2 in two files); and a later main commit adding
  archive/round6-ledger.zip and CASE-STUDY-6.md, neither of which a replay
  repository may hold;
- an archive whose ledger exercises every cut rule: stamped files cut at a
  dispatch, one file wholly after it, an unstamped file kept after it, CRLF in one
  file, keys/, and each parcel's own file holding its plant's old text;
- the outside sources and a plan of record, each in its own repository;
- items and expected data in qs4's shapes, written by QS4's own tools.
Each copy's expected SHA comes by a second route, independent of the rebuilder:
the tip checked out and edited in a working tree, `git add` and `write-tree`, then
`git commit-tree` with the tip's own author, committer, dates and message.
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import re
import shutil
import stat
import subprocess
import zipfile
from dataclasses import dataclass
from pathlib import Path

from qs.agent import Mount
from qs.agent.scripted import tool_call
from qs.fake import FakeReply, reply
from qs.suites import qs4

ROOT = Path(__file__).resolve().parent.parent
LEDGER = "parcelround-r6-ledger/"
WHO = {"GIT_AUTHOR_NAME": "Parcel", "GIT_AUTHOR_EMAIL": "parcel@example.invalid",
       "GIT_COMMITTER_NAME": "Parcel", "GIT_COMMITTER_EMAIL": "parcel@example.invalid"}


def load_tool(name: str):
    spec = importlib.util.spec_from_file_location(f"hh_{name}", ROOT / "tools" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def g(repo: Path, *args: str, date: str = "2026-10-02T20:00:00-07:00", input: bytes | None = None) -> str:
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date, **WHO)
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, env=env, input=input,
                          check=True).stdout.decode("utf-8")


def put(repo: Path, rel: str, text: str) -> None:
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(text.encode("utf-8"))


def commit(repo: Path, msg: str, date: str) -> str:
    g(repo, "add", "-A")
    g(repo, "commit", "-q", "-m", msg, date=date)
    return g(repo, "rev-parse", "HEAD").strip()


def remove_tree(path: Path) -> None:
    def onexc(func, p, exc):
        os.chmod(p, stat.S_IWRITE)
        func(p)
    if path.exists():
        shutil.rmtree(path, onexc=onexc)


GATE_SCRIPT = '''import sys
if "--control" in sys.argv:
    print("control links      a link that does not resolve                     caught")
    print("control quoted     a passage dropped                                caught")
    print("controls: 2 of 2 caught")
else:
    print("links      ok    1 relative links read")
    print("quoted     ok    1 passage read")
    print("PASS: 2 of 2 checks hold")
'''
METHOD = "".join(f"rule line {n}.\n" for n in range(1, 61))
P1_PLANTS = [{"file": "METHOD.md", "old": "the verifier re-runs from clean", "new": "the verifier may re-run from clean"},
             {"file": "METHOD.md", "old": "it found five wrong answers", "new": "it found six wrong answers"}]
P2_PLANTS = [{"file": "templates/a.md", "old": "write it in your file first", "new": "message the lead first"},
             {"file": "templates/b.md", "old": "nowhere else. (§3)", "new": "nowhere else. (§8)"}]


def independent_copy(repo: Path, tip: str, plants: list, work: Path) -> str:
    """The second route to a copy's SHA (see the module's docstring)."""
    clone = work / f"ind-{tip[:7]}"
    g(work, "clone", "-q", str(repo), str(clone))
    g(clone, "checkout", "-q", "--detach", tip)
    for p in plants:
        f = clone / p["file"]
        f.write_bytes(f.read_bytes().replace(p["old"].encode(), p["new"].encode(), 1))
    g(clone, "add", "-A")
    tree = g(clone, "write-tree").strip()
    raw = subprocess.run(["git", "-C", str(clone), "cat-file", "commit", tip], capture_output=True,
                         check=True).stdout
    head, _, msg = raw.partition(b"\n\n")
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    parents = []
    for line in head.split(b"\n"):
        m = re.match(rb"^(author|committer) (.*) <(.*)> (\d+ [+-]\d{4})$", line)
        if m:
            who = m.group(1).decode().upper()
            env.update({f"GIT_{who}_NAME": m.group(2).decode(), f"GIT_{who}_EMAIL": m.group(3).decode(),
                        f"GIT_{who}_DATE": m.group(4).decode()})
        elif line.startswith(b"parent "):
            parents += ["-p", line.split()[1].decode()]
    return subprocess.run(["git", "-C", str(clone), "commit-tree", tree, *parents], input=msg,
                          capture_output=True, env=env, check=True).stdout.decode().strip()


def zipped(members: list[tuple[str, tuple, bytes]]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, when, data in members:
            z.writestr(zipfile.ZipInfo(LEDGER + name, date_time=when), data)
    return buf.getvalue()


def entry(stamp: str, headline: str, body: str) -> str:
    return f"\n## {stamp} -0700 - {headline}\n\n{body}\n"


def archive_members(c1: str, c2: str, keys: dict) -> list:
    t = lambda h, m, s=0: (2026, 10, 2, h, m, s)  # noqa: E731
    lead = ("# Round 6 - the lead's ledger\n"
            + entry("2026-10-02 20:00:00", "the round opens", "Measured: the plan.")
            + entry("2026-10-02 22:00:00", "P1 reported; verifier-P1 dispatched",
                    f"- verifier-P1 gets a copy of P1's work, a fresh repository detached at {c1[:7]}.")
            + entry("2026-10-02 22:05:00", "P2 reported; verifier-P2 dispatched",
                    f"- verifier-P2 gets a copy of P2's work, a fresh repository detached at {c2[:7]}.")
            + entry("2026-10-02 22:30:00", "keys revealed", "- the plants: it found five wrong answers, made six."))
    return [
        ("README.md", t(18, 0), b"# The round ledger\n\nRead every file here.\n"),
        ("briefs/_verifier.md", t(18, 0), b"# What every verifier's brief shares\n"),
        ("briefs/P1.md", t(18, 0), b"# P1's brief\n"),
        ("briefs/late.md", t(23, 0), b"# a brief written after both dispatches\n"),
        ("lead.md", t(22, 30), lead.encode()),
        ("P1.md", t(21, 0), ("# P1\n" + entry("2026-10-02 21:00:00", "design",
                                                "it found five wrong answers")).encode()),
        ("P2.md", t(21, 10), ("# P2\r\n" + entry("2026-10-02 21:10:00", "design", "a line")
                              .replace("\n", "\r\n")).encode()),
        ("verifier-P0.md", t(22, 10), ("# verifier-P0\n" + entry("2026-10-02 19:00:00", "starts", "a")
                                       + entry("2026-10-02 22:10:00", "later", "b")).encode()),
        ("verifier-P2.md", t(22, 20), ("# verifier-P2\n" + entry("2026-10-02 22:20:00", "starts", "c")).encode()),
        (f"keys/key-{c1[:7]}.json", t(22, 30), json.dumps(keys["P1"], indent=2).encode()),
        (f"keys/key-{c2[:7]}.json", t(22, 30), json.dumps(keys["P2"], indent=2).encode()),
    ]


@dataclass
class World:
    root: Path
    repo: Path          # the ParcelRound-like repository
    hh: Path            # a HonestHarness-like repository, holding the plan
    repos: Path         # the directory holding the outside source's repository
    items_path: Path
    expected_path: Path
    local: Path
    archive: bytes
    items: dict
    copies: dict
    tips: dict
    base: str


def build_world(root: Path) -> World:
    root.mkdir(parents=True, exist_ok=True)
    repo = root / "pr"
    repo.mkdir()
    g(repo, "init", "-q", "-b", "main")
    put(repo, ".gitattributes", "* text=auto eol=lf\n")
    put(repo, "METHOD.md", METHOD.replace("rule line 10.", "the verifier re-runs from clean anything.")
        .replace("rule line 30.", "it found five wrong answers in the tree."))
    put(repo, "ADOPTION.md", "rows\n")
    put(repo, "tools/check_method.py", GATE_SCRIPT)
    put(repo, "templates/a.md", "Escalate: write it in your file first, then message.\n")
    put(repo, "templates/b.md", "Your scratch, and nowhere else. (§3)\n")
    base = commit(repo, "base", "2026-10-02T19:00:00-07:00")
    g(repo, "checkout", "-q", "-b", "p1")
    put(repo, "METHOD.md", (repo / "METHOD.md").read_text("utf-8") + "P1 adds a rule.\n")
    t1 = commit(repo, "P1: a rule\n\nCo-Authored-By: Parcel <parcel@example.invalid>", "2026-10-02T21:50:00-07:00")
    g(repo, "checkout", "-q", "main")
    g(repo, "checkout", "-q", "-b", "p2")
    put(repo, "templates/b.md", (repo / "templates/b.md").read_text("utf-8") + "P2 adds a line.\n")
    t2 = commit(repo, "P2: the templates", "2026-10-02T21:55:00-07:00")
    g(repo, "checkout", "-q", "main")
    g(repo, "merge", "-q", "--no-ff", "-m", "merge P1", "p1", date="2026-10-02T23:00:00-07:00")
    g(repo, "merge", "-q", "--no-ff", "-m", "merge P2", "p2", date="2026-10-02T23:01:00-07:00")
    work = root / "independent"
    work.mkdir()
    c1 = independent_copy(repo, t1, P1_PLANTS, work)
    c2 = independent_copy(repo, t2, P2_PLANTS, work)
    keys = {"P1": {"real_tip": t1, "copy_commit": c1, "plants": [{**p, "shape": "s"} for p in P1_PLANTS]},
            "P2": {"real_tip": t2, "copy_commit": c2, "plants": [{**p, "shape": "s"} for p in P2_PLANTS]}}
    archive = zipped(archive_members(c1, c2, keys))
    (repo / "archive").mkdir()
    (repo / "archive" / "round6-ledger.zip").write_bytes(archive)
    put(repo, "CASE-STUDY-6.md", "the case study\n")
    main = commit(repo, "the archive and the case study", "2026-10-03T01:00:00-07:00")
    # the plan, and the outside source
    hh = root / "hh"
    hh.mkdir()
    g(hh, "init", "-q", "-b", "main")
    put(hh, "Rounds/ParcelRound-R6/PLAN.md", "# the plan of record, draft 3\n")
    plan = commit(hh, "the plan", "2026-10-02T17:00:00-07:00")
    repos = root / "repos"
    (repos / "srcrepo").mkdir(parents=True)
    g(repos / "srcrepo", "init", "-q", "-b", "main")
    put(repos / "srcrepo", "docs/V.md", "It found five wrong answers in the shipped tree.\n")
    src = commit(repos / "srcrepo", "a source", "2026-09-28T12:00:00-07:00")
    put(repos / "srcrepo", "docs/V.md", "a later version\n")
    commit(repos / "srcrepo", "later", "2026-10-05T12:00:00-07:00")
    items = {
        "format": 1,
        "archive": {"parcelround": main, "path": "archive/round6-ledger.zip", "root": LEDGER},
        "plan": {"commit": plan, "path": "Rounds/ParcelRound-R6/PLAN.md"},
        "sources": [{"name": "srcrepo", "commit": src, "paths": ["docs/V.md"]}],
        "caps": {"max_prompt_tokens": 200_000, "max_output_tokens": 20_000, "max_call_prompt_tokens": 50_000},
        "budgets": {"max_turns": 8, "max_run_seconds": 600, "call_timeout_seconds": 30, "max_output_chars": 4000,
                    "malformed_retries": 3, "nudges": 1, "max_calls_per_turn": 16, "max_scratch_bytes": 1 << 20,
                    "max_tokens_per_turn": 4096},
        "settings": {"stream": False, "tolerance": 2, "ledger_file_cap": 100_000, "first_run": "p1-planted"},
        "parcels": {
            "P1": {"copy": c1, "tip": t1, "base": base, "key": f"keys/key-{c1[:7]}.json",
                   "dispatch": "2026-10-02 22:00:00", "wave": 1, "view": "22:20:00", "report": "22:25:00",
                   "original_gate": {"recorded": "a test", "gate": [2, 2], "control": [2, 2]},
                   "plants": [{"id": "P1-p1", "index": 0, "shape": "rule", "markers": [["re-runs"]]},
                              {"id": "P1-p2", "index": 1, "shape": "figure", "markers": [["five"]]}],
                   "r6_findings": [
                       {"id": "P1-r1", "class": "restate", "file": "METHOD.md", "lines": [[40, 40]], "in_view": True,
                        "recorded": "a test", "copy_only": False},
                       {"id": "P1-r2", "class": "other", "file": "tools/check_method.py", "lines": [],
                        "in_view": False, "recorded": "a test", "copy_only": False}]},
            "P2": {"copy": c2, "tip": t2, "base": base, "key": f"keys/key-{c2[:7]}.json",
                   "dispatch": "2026-10-02 22:05:00", "wave": 2, "view": "22:20:00", "report": "22:25:00",
                   "original_gate": {"recorded": "a test", "gate": [2, 2], "control": [2, 2]},
                   "plants": [{"id": "P2-p1", "index": 0, "shape": "rule", "markers": [["entry first"]]},
                              {"id": "P2-p2", "index": 1, "shape": "rule", "markers": [["§3"]]}],
                   "r6_findings": [
                       {"id": "P2-r1", "class": "restate", "file": "<commit message>", "lines": [], "in_view": True,
                        "recorded": "a test (the copy's own)", "copy_only": True}]},
        },
        "items": [{"id": f"{p}-{k}", "parcel": p.upper(), "kind": k} for p in ("p1", "p2") for k in ("planted", "real")],
    }
    items_path, expected_path = root / "items.json", root / "expected.json"
    items_path.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
    return World(root=root, repo=repo, hh=hh, repos=repos, items_path=items_path, expected_path=expected_path,
                 local=root / "local", archive=archive, items=items, copies={"P1": c1, "P2": c2},
                 tips={"P1": t1, "P2": t2}, base=base)


def build_inputs(w: World, *, gate_image: str | None = "test-image") -> dict:
    """QS4's own tools, run on the world: the cutter, then the rebuilder without
    the Docker step. A held gate comparison is then recorded with `gate_image`,
    standing in for the step a Docker test makes for real."""
    cut, rebuild = load_tool("qs4_cut"), load_tool("qs4_rebuild")
    common = ["--local", str(w.local), "--items", str(w.items_path), "--expected", str(w.expected_path),
              "--write-expected"]
    assert cut.main(["--parcelround", str(w.repo), *common]) == 0
    assert rebuild.main(["--parcelround", str(w.repo), "--repos", str(w.repos), "--honestharness", str(w.hh),
                         "--no-gate", *common]) == 0
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
    """Prepared inputs with names only, for runs on P2's ScriptedSandbox, which
    mounts nothing: what scoring needs (file lists) from the given data."""

    def __init__(self, items: dict, expected: dict):
        self.items, self.expected, self.prepared = items, expected, []

    def prepare(self, item_id: str) -> qs4.Prepared:
        it = qs4.item_spec(self.items, item_id)
        e = self.expected["repos"][item_id]
        self.prepared.append(item_id)
        mounts = [Mount(Path("."), f"r6-vcopy-{it['parcel']}"), Mount(Path("."), qs4.LEDGER_MOUNT),
                  Mount(Path("."), qs4.PLAN_MOUNT)] + [Mount(Path("."), s["name"]) for s in self.items["sources"]]
        return qs4.Prepared(mounts=mounts, repo_files=e["files"], cut_files=self.expected["cuts"][item_id]["files"],
                            source_files={s["name"]: list(s["paths"]) for s in self.items["sources"]},
                            facts={"commit": e["commit"][:12], "gate_held": True})


def report_call(call_id: str, findings: list, verdict: str = "NOT READY", text: str = "what I ran") -> dict:
    return tool_call(call_id, "report", {"verdict": verdict, "findings": findings, "text": text})


def turn(*calls, finish: str = "tool_calls") -> FakeReply:
    return reply(None, reasoning="thinking", tool_calls=list(calls), finish=finish, usage=(0, 300, 40, 10))


def to_sse(fr: FakeReply) -> FakeReply:
    """A non-streamed fake reply as the SSE stream DeepSeek would send for it."""
    b = fr.body
    msg, finish = b["choices"][0]["message"], b["choices"][0]["finish_reason"]
    base = {"id": "fake", "object": "chat.completion.chunk", "model": b["model"],
            "system_fingerprint": b["system_fingerprint"]}
    data = lambda **kw: "data: " + json.dumps({**base, **kw})  # noqa: E731
    lines = [": keep-alive"]
    if msg.get("reasoning_content"):
        lines.append(data(choices=[{"index": 0, "delta": {"reasoning_content": msg["reasoning_content"]},
                                    "finish_reason": None}]))
    if msg.get("content"):
        lines.append(data(choices=[{"index": 0, "delta": {"content": msg["content"]}, "finish_reason": None}]))
    for i, tc in enumerate(msg.get("tool_calls") or []):
        lines.append(data(choices=[{"index": 0, "delta": {"tool_calls": [
            {"index": i, "id": tc["id"], "type": "function", "function": tc["function"]}]}, "finish_reason": None}]))
    lines.append(data(choices=[{"index": 0, "delta": {}, "finish_reason": finish}], usage=b["usage"]))
    lines.append("data: [DONE]")
    return FakeReply(stream=lines)


class Streamed:
    """Wraps a responder so a streamed request gets its reply as a stream."""

    def __init__(self, model):
        self.model = model

    def __call__(self, body):
        r = self.model(body)
        return to_sse(r) if body.get("stream") and r.body and r.status == 200 else r
