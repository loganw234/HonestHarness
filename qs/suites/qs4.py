"""QS4: round 6's planted copies, and their real tips, replayed to a model
working as round 6's verifiers worked (the plan's §6, wave 2, "P4").

Ten items, one suite class each, so that tools/live.py builds each with no
arguments and each run is its own batch. For each of round 6's five parcels there
is its planted copy, rebuilt from the parcel's real tip and its key, and its real
tip, the false-alarm set. A run gives the model what round 6's verifier had:
- the repository, read-only, holding only the objects its commit reaches;
- round 6's ledger, cut at that verifier's dispatch, without keys/ and without
  the parcel's own file;
- round 6's plan of record, and the outside files the round's text and gate cite,
  each at its pinned commit;
- a dispatch message reconstructed from the ledger, with roots in place of paths,
  and the adaptation the sandbox needs. That text, qs4_prompt.md, is the prompt
  version. Round 6's own briefs stay byte for byte in the cut.
The model works through P2's agent loop and Docker sandbox, and ends with a
structured report.

The inputs. tools/qs4_cut.py and tools/qs4_rebuild.py build them under
local/qs4/, which is gitignored, from ParcelRound at f42242e: its archive (keys,
briefs, ledger, dispatch times) and its history. qs4_expected.json pins what each
must hash to.
- A planted copy is its real tip's commit object, with only the tree line
  replaced by the tip's tree with the key's plants applied, each file's plants
  in turn. Its SHA must equal the key's copy_commit, or the item stops.
- A replay repository is cloned locally with --no-hardlinks from a temporary
  branch, then detached, with no branch, tag, remote or reflog, and pruned. It
  holds exactly the objects its commit reaches, which is asserted.
- A cut holds every stamped entry at or before the dispatch, each file's
  bytes as archived, and each unstamped file whose kept time is at or before
  the dispatch. keys/ and the parcel's own file never enter. In a real tip's
  cut, the copy's short SHA in the lead's dispatch entry becomes the tip's, so
  the two runs read alike (lead.md 17:47:24, answer 4).
- Host directories are named by SHA, digest or random id, never planted or real.
  The sandbox shows mount paths to the model.

The guards, each failing closed. Before every mount, at construction (so
before any spend) and again in run_item:
- the repository's HEAD, tree and object closure, with no refs, no remote and a
  clean working tree;
- the cut's digest, and that it holds no link;
- the plan's and the outside sources' digests;
- round 6's gate, run on the host and in the sandbox at the repository with the
  same image, whose verdicts matched (tools/qs4_rebuild.py records it).
A failure at construction raises, so tools/live.py spends nothing. A failure in
run_item is recorded as error, with no model call.

The score. Only the report's findings are scored by script.
- A plant is located when a finding names its file and its lines meet the
  plant's span, widened by settings.tolerance lines.
- The fault screen holds when that finding's statement holds one of the plant's
  pre-registered marker sets.
- Caught by the screen is located and screened. The score of record is the
  lead's judgement of each located finding, checked by a verifier and kept in
  qs4_judgements.json, recorded as judgement.
- Every other finding is matched by location against round 6's recorded
  findings for the parcel, for the lead to adjudicate. None is assumed false.

Statuses:
- stopped and error are P2's, and the judge is never asked about them, so a
  capped run is never "found nothing";
- a planted item passes when the screen catches both plants, and fails
  otherwise, a report with no findings included;
- a real tip passes when it reported;
- either fails with no report;
- an input that fails its assertions is error.

What is recorded:
- outcome.data["qs4"] holds no model text: normalised file names from closed
  sets, lines, classes, matches, counts and digests' prefixes;
- ItemResult.local["qs4"] holds the report, the verifier's ledger file and
  each finding's statement, which stay in the local transcript.

Cost and time. Each run is one batch through P0's runner. At QS4's caps
(40,000,000 prompt tokens, 500,000 output, 900,000 a call) on deepseek-flash,
a batch reserves $9.0315264 off-peak and $15.0956160 with --allow-peak. Both
include P0's unmetered margin of $2.2255776: three times the dearest single
call, for attempts the server closes with no reply. tests/test_qs4.py works
both figures by hand.
- A run's wall clock is budgets.max_run_seconds, 6,000 s. The lead's
  background jobs stop at 2 hours, and a batch interrupted there writes no
  summary. 6,000 s leaves about 20 minutes for the input checks, the probe,
  the settle and the closing read (budgets_about in qs4_items.json).
- The budget is checked before each model call and each tool call. So a run
  can end later, by its last call: a tool call's call_timeout_seconds and
  P2's grace, or one model call of up to max_tokens_per_turn tokens.
- Without --allow-peak, P0's runner refuses a start within its margin of a
  peak window, and stops the batch at the first call that would fall in one.

Limits, each stated by the behaviour it concedes:
1. There is no network: a check an original made over it (verifier-P5's render
   check through GitHub's API) cannot be made, and no link is fetched.
2. The parcel's own ledger file is withheld. The originals read it after their
   views; what they found through it is not comparable, and only in-view
   findings are counted.
3. The cut ends at the dispatch entry's stamp. An entry written after it that an
   original read is absent (lead.md 00:24:40, whose notice the dispatch message
   carries instead). So is a file whose archived version postdates the cut:
   briefs/P5.md is absent from wave 1's cuts.
4. The model's `date` is the replay's, days after round 6's stamps.
5. The copy is read-only, where round 6's was writable and its brief forbade
   edits.
6. The tools are P2's shell, read_file and write_file, with a
   max_output_chars cap, and a structured report: not Claude Code's.
7. The screen is a heuristic of markers. The score of record is the lead's
   judgement. A finding near a plant whose statement holds a marker for
   another reason passes the screen: P4's first plant (METHOD.md:694-695)
   and round 6's D1 finding at 696-697 are an instance.
8. A finding is located only by its file and lines. One that quotes the text
   with no line number, or cites another line, is not located.
9. Only the report's findings are scored. A finding written only in its text,
   or only in the ledger file, is left to the lead's reading.
10. A real tip's pass means it reported. Its findings are adjudicated.
11. A real tip's cut differs from its copy's by one short SHA, in the lead's
    dispatch entry.
12. One run per item, so there is no estimate of variance.
13. A request past the per-call cap stops the run as stopped (caps): about
    half DeepSeek's context for English text, by P0's estimate.
14. The escalation is answered by a fixed text, where the originals' were
    answered by a lead.
15. The plan of record is mounted as committed in HonestHarness at 809ed2f, after
    round 6. Round 6's ledger records its edits only before the dispatches.
16. Every turn's reasoning goes back with every later request (D8), so the
    prompt grows by reasoning as well as by tool output.
17. The container's mountinfo shows host paths (P2's limit). The names here show
    nothing of an item's kind, though they do show the owner's user name.
18. A stopped or unreported run's partial findings, in its ledger file, are kept
    locally and not scored.
19. The ledger file is read back up to settings.ledger_file_cap bytes, and only
    where P2's scratch manifest calls it a regular file whose hash matches.
20. Round 6's record has been public since 2026-10-03. Both models predate it by
    release date, unless upgraded in place since (plan §4).
21. The replay repositories' commits carry the owner's address in their author
    lines, as ParcelRound's public history does. A model's git log shows it,
    so the provider receives it: plan §3's K6 lets every repository's content
    go to the providers used (verifier-P4's L2).
"""
from __future__ import annotations

import difflib
import hashlib
import io
import json
import os
import re
import secrets
import shutil
import stat
import string
import subprocess
import sys
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from ..agent import Budgets, DockerSandbox, Mount, Tool, ToolOutcome, builtin_tools, run_agent
from ..agent.sandbox import RO_ROOT, SCRATCH
from ..suite import Caps, Item, ItemResult, Suite

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
LOCAL = ROOT / "local" / "qs4"
ITEMS_PATH = HERE / "qs4_items.json"
PROMPT_PATH = HERE / "qs4_prompt.md"
EXPECTED_PATH = HERE / "qs4_expected.json"
JUDGEMENTS_PATH = HERE / "qs4_judgements.json"

LEDGER_MOUNT = "parcelround-r6-ledger"
PLAN_MOUNT = "HonestHarness"
PROMPT_SECTIONS = ("system", "dispatch", "adaptation", "p5-extra", "report-tool", "escalate-tool",
                   "escalate-reply")
CLASSES = ("wrong answer", "regression", "known limit", "restate", "other")
COMMIT_MESSAGE, UNLISTED = "<commit message>", "<unlisted>"
STAMPED = re.compile(rb"^## (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) -0700 - ", re.M)
SHA = re.compile(r"[0-9a-f]{40}")
GATE_TIMEOUT_S = 900
FORBIDDEN_NAMES = ("CASE-STUDY-6.md",)      # nothing later than round 6's copies goes in


class InputError(Exception):
    """An input that is absent, or not what it must be: its item is refused. The
    message is QS4's own words and names no host path."""


# -- the committed data ---------------------------------------------------------
def _norm(p: Path) -> bytes:
    try:
        return p.read_bytes().replace(b"\r\n", b"\n")
    except OSError:
        return b""


def load_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


SECTION = re.compile(r"^## ([a-z0-9-]+)[ \t]*$", re.M)


def load_prompt(path: Path = PROMPT_PATH) -> dict[str, str]:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    heads = list(SECTION.finditer(text))
    out = {}
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        out[m.group(1)] = text[m.end():end].strip("\n")
    return out


def compute_version() -> str:
    """"1." plus 12 hex digits of the data's SHA-256 (items, prompt, expected)
    and 12 of this file's, line endings normalised: a record names its exact
    prompt, inputs and scorer. The lead's judgements do not enter it."""
    data = hashlib.sha256(b"\0".join(_norm(p) for p in (ITEMS_PATH, PROMPT_PATH, EXPECTED_PATH)))
    code = hashlib.sha256(_norm(Path(__file__)))
    return f"1.{data.hexdigest()[:12]}.{code.hexdigest()[:12]}"


ITEMS = load_json(ITEMS_PATH)
PROMPT = load_prompt()
EXPECTED = load_json(EXPECTED_PATH) if EXPECTED_PATH.exists() else {}
VERSION = compute_version()


def item_spec(items: dict, item_id: str) -> dict:
    for it in items["items"]:
        if it["id"] == item_id:
            return it
    raise KeyError(f"no QS4 item {item_id!r}")


def item_commit(items: dict, item: dict) -> str:
    p = items["parcels"][item["parcel"]]
    return p["copy"] if item["kind"] == "planted" else p["tip"]


# -- small helpers ------------------------------------------------------------------
def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def blob_id(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()


def git(repo: Path | str, *args: str, input: bytes | None = None, ok: tuple = (0,),
        env: dict | None = None) -> bytes:
    """git with optional locks off and no prompt. The inherited environment goes
    to the child unread. A failure raises InputError naming only the subcommand,
    since git's own text may name a host path."""
    e = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0", **(env or {}))
    try:
        r = subprocess.run(["git", "-C", str(repo), *args], input=input, capture_output=True, env=e)
    except OSError:
        raise InputError(f"git {args[0]} could not be run") from None
    if r.returncode not in ok:
        raise InputError(f"git {args[0]} failed (exit {r.returncode})")
    return r.stdout


def _remove(path: Path) -> None:
    """Remove a directory tree QS4 made, read-only files (git's objects) included."""
    def onexc(func, p, exc):
        os.chmod(p, stat.S_IWRITE)
        func(p)
    if path.exists():
        shutil.rmtree(path, onexc=onexc)


def tree_digest(files: dict[str, bytes]) -> str:
    """SHA-256 over the sorted list of each file's path, SHA-256 and size."""
    manifest = sorted([k, sha256(v), len(v)] for k, v in files.items())
    return sha256(json.dumps(manifest, separators=(",", ":")).encode("utf-8"))


def write_files(files: dict[str, bytes], dest: Path) -> None:
    if dest.exists():
        raise InputError("a destination exists already")
    for rel, data in files.items():
        p = dest / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)


def read_files(root: Path) -> dict[str, bytes]:
    """Every regular file under root, by its relative path. A link, a reparse
    point (a link made inside the sandbox reaches the host as one) or any other
    kind of entry is refused, never followed."""
    if not root.is_dir():
        raise InputError("an input directory is absent")
    out = {}
    for d, dirs, names in os.walk(root, followlinks=False):
        for name in dirs + names:
            st = os.lstat(Path(d) / name)
            if stat.S_ISLNK(st.st_mode) or getattr(st, "st_reparse_tag", 0):
                raise InputError("an input directory holds a link")
        for name in names:
            p = Path(d) / name
            if not stat.S_ISREG(os.lstat(p).st_mode):
                raise InputError("an input directory holds an entry that is not a regular file")
            out[p.relative_to(root).as_posix()] = p.read_bytes()
    return out


# -- the archive ----------------------------------------------------------------
def archive_from_git(checkout: Path, commit: str, path: str) -> bytes:
    """The archive's bytes, read from ParcelRound's object store at the commit
    (cat-file blob: git show's plumbing, the raw blob, no checkout)."""
    return git(checkout, "cat-file", "blob", f"{commit}:{path}")


def archive_spec(data: bytes) -> dict:
    z = zipfile.ZipFile(io.BytesIO(data))
    return {"blob": blob_id(data), "bytes": len(data), "sha256": sha256(data),
            "members": {i.filename: sha256(z.read(i)) for i in z.infolist() if not i.is_dir()}}


def archive_members(data: bytes, spec: dict) -> dict[str, tuple[bytes, str]]:
    """Each member's bytes and kept time ("YYYY-MM-DD HH:MM:SS", local -0700, as
    P3 measured), refused unless the archive and every member match spec."""
    if sha256(data) != spec["sha256"] or blob_id(data) != spec["blob"] or len(data) != spec["bytes"]:
        raise InputError("the archive is not the one qs4_expected.json pins")
    z = zipfile.ZipFile(io.BytesIO(data))
    out = {}
    for i in z.infolist():
        if i.is_dir():
            continue
        b = z.read(i)
        out[i.filename] = (b, "%04d-%02d-%02d %02d:%02d:%02d" % i.date_time)
    if {k: sha256(v[0]) for k, v in out.items()} != spec["members"]:
        raise InputError("the archive's members are not the ones qs4_expected.json pins")
    return out


def keys_of(members: dict, items: dict) -> dict[str, dict]:
    root = items["archive"]["root"]
    return {p: json.loads(members[root + v["key"]][0]) for p, v in items["parcels"].items()}


# -- the cut ------------------------------------------------------------------------
def build_cut(members: dict, root: str, cut_time: str, parcel: str) -> dict[str, bytes]:
    """Round 6's ledger as verifier-<parcel> found it at its dispatch:
    - a stamped file up to its first entry stamped after the dispatch; a file
      whose first entry is after it is absent;
    - an unstamped file when its kept time is at or before it;
    - never keys/, never the parcel's own file.
    Bytes are kept as archived, line endings included."""
    files = {}
    for name, (data, kept) in members.items():
        if not name.startswith(root):
            raise InputError("an archive member lies outside the ledger's root")
        rel = name[len(root):]
        if rel.startswith("keys/") or rel == f"{parcel}.md":
            continue
        stamps = [(m.start(), m.group(1).decode()) for m in STAMPED.finditer(data)]
        if not stamps:
            if kept <= cut_time:
                files[rel] = data
            continue
        if any(a[1] > b[1] for a, b in zip(stamps, stamps[1:])):
            raise InputError(f"{rel}'s stamps are out of order, so it has no prefix to cut")
        if stamps[0][1] > cut_time:
            continue
        later = [pos for pos, s in stamps if s > cut_time]
        files[rel] = data[:later[0]] if later else data
    return files


def substitute_sha(files: dict[str, bytes], old: str, new: str) -> dict[str, bytes]:
    """A real tip's cut: the copy's short SHA, which the lead's dispatch entry
    names, becomes the tip's. It must occur exactly once, in lead.md."""
    o, n = old.encode(), new.encode()
    lead = files.get("lead.md", b"")
    if lead.count(o) != 1 or any(v.count(o) for k, v in files.items() if k != "lead.md"):
        raise InputError("the copy's short SHA does not occur exactly once in the cut, in lead.md")
    out = dict(files)
    out["lead.md"] = lead.replace(o, n, 1)
    return out


def cut_problems(files: dict[str, bytes], cut_time: str, parcel: str, absent: list[bytes]) -> list[str]:
    """What a cut must not hold: keys/, the parcel's file, an entry stamped after
    the dispatch, or any of `absent` (each plant's text, and the other run's
    short SHA)."""
    probs = []
    for rel, data in sorted(files.items()):
        if rel.startswith("keys/"):
            probs.append(f"{rel}: keys/ is in the cut")
        if rel == f"{parcel}.md":
            probs.append(f"{rel}: the parcel's own file is in the cut")
        if any(m.group(1).decode() > cut_time for m in STAMPED.finditer(data)):
            probs.append(f"{rel}: an entry stamped after the dispatch")
        if any(t and t in data for t in absent):
            probs.append(f"{rel}: a text the cut must not hold")
    return probs


def cut_for(members: dict, items: dict, item: dict, keys: dict) -> dict[str, bytes]:
    """An item's cut, built and checked, ready to write."""
    p = items["parcels"][item["parcel"]]
    files = build_cut(members, items["archive"]["root"], p["dispatch"], item["parcel"])
    if item["kind"] == "real":
        files = substitute_sha(files, p["copy"][:7], p["tip"][:7])
    other = p["tip"][:7] if item["kind"] == "planted" else p["copy"][:7]
    texts = [x.encode("utf-8") for pl in keys[item["parcel"]]["plants"] for x in (pl["old"], pl["new"])]
    probs = cut_problems(files, p["dispatch"], item["parcel"], texts + [other.encode()])
    if probs:
        raise InputError("the cut fails its checks: " + "; ".join(probs))
    return files


# -- the repositories -------------------------------------------------------------
def planted_blobs(work: Path, tip: str, plants: list[dict]) -> dict[str, bytes]:
    """Each planted file's bytes: the key's plants applied in turn to the tip's
    blob, each `old` found exactly once. A file holding two plants gets both."""
    texts: dict[str, bytes] = {}
    for p in plants:
        data = texts[p["file"]] if p["file"] in texts else git(work, "cat-file", "blob", f"{tip}:{p['file']}")
        old, new = p["old"].encode("utf-8"), p["new"].encode("utf-8")
        if data.count(old) != 1:
            raise InputError(f"a plant's old text occurs {data.count(old)} times in {p['file']}, not once")
        texts[p["file"]] = data.replace(old, new, 1)
    for p in plants:
        data, old, new = texts[p["file"]], p["old"].encode("utf-8"), p["new"].encode("utf-8")
        if new not in data or (old not in new and old in data):
            raise InputError(f"a plant of {p['file']} is not in place")
    return texts


def planted_tree(work: Path, tip: str, blobs: dict[str, bytes]) -> str:
    idx = Path(work).resolve() / ".git" / f"qs4-index-{secrets.token_hex(4)}"
    env = {"GIT_INDEX_FILE": str(idx)}
    try:
        git(work, "read-tree", tip, env=env)
        for path, data in blobs.items():
            row = git(work, "ls-tree", tip, "--", path).decode().split()
            if len(row) < 3 or row[1] != "blob":
                raise InputError(f"{path} is not a file at the tip")
            blob = git(work, "hash-object", "-w", "--stdin", input=data).decode().strip()
            git(work, "update-index", "--cacheinfo", f"{row[0]},{blob},{path}", env=env)
        return git(work, "write-tree", env=env).decode().strip()
    finally:
        idx.unlink(missing_ok=True)


def rebuilt_commit(work: Path, tip: str, tree: str) -> str:
    """The tip's commit object, byte for byte, with only its tree line replaced,
    written and hashed (draft 4's verifier's method, lead.md 17:47:24)."""
    raw = git(work, "cat-file", "commit", tip)
    head, sep, msg = raw.partition(b"\n\n")
    lines = head.split(b"\n")
    if not lines[0].startswith(b"tree ") or sum(x.startswith(b"tree ") for x in lines) != 1:
        raise InputError("the tip's commit object does not open with one tree line")
    lines[0] = b"tree " + tree.encode()
    return git(work, "hash-object", "-t", "commit", "-w", "--stdin",
               input=b"\n".join(lines) + sep + msg).decode().strip()


def rebuild_copy(work: Path, key: dict) -> tuple[str, dict[str, bytes]]:
    """The planted copy's commit, refused unless it reproduces the key's
    copy_commit: the brief's first control."""
    blobs = planted_blobs(work, key["real_tip"], key["plants"])
    sha = rebuilt_commit(work, key["real_tip"], planted_tree(work, key["real_tip"], blobs))
    if sha != key["copy_commit"]:
        raise InputError(f"the rebuilt copy is {sha[:7]}, not the key's {key['copy_commit'][:7]}")
    return sha, blobs


def plant_span(blob: bytes, new: str) -> list[int]:
    n = new.encode("utf-8")
    at = blob.index(n)
    start = blob[:at].count(b"\n") + 1
    return [start, start + n.rstrip(b"\n").count(b"\n")]


def make_replay_repo(work: Path, commit: str, dest: Path) -> None:
    """A repository holding only what `commit` reaches. It is cloned locally from a
    temporary branch, with --no-hardlinks, so the objects are copied, never
    linked. It is then detached, its branch, remote and reflogs are removed, and
    `git gc --prune=now` drops every object the commit does not reach.
    repo_problems() then asserts that the store equals the commit's closure.
    (A --no-local clone would send only reachable objects, but on Windows its
    upload-pack refuses a source path past MAX_PATH: "'$GIT_DIR' too big",
    measured.)"""
    if dest.exists():
        raise InputError("a replay repository's directory exists already")
    branch = f"qs4-replay-{secrets.token_hex(4)}"
    work, dest = Path(work).resolve(), Path(dest).resolve()
    git(work, "branch", "-f", branch, commit)
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        git(dest.parent, "clone", "-q", "--no-hardlinks", "--single-branch", "--no-tags", "--branch", branch,
            str(work), str(dest))
        git(dest, "checkout", "-q", "--detach")
        git(dest, "branch", "-D", "-q", branch)
        git(dest, "remote", "remove", "origin")
        git(dest, "reflog", "expire", "--expire=now", "--all")
        git(dest, "gc", "-q", "--prune=now")
    finally:
        git(work, "branch", "-D", "-q", branch, ok=(0, 1))


def repo_problems(dest: Path, commit: str, tree: str, objects: int,
                  forbidden_blobs: tuple = (), forbidden_names: tuple = FORBIDDEN_NAMES) -> list[str]:
    """Everything a replay repository must be, asserted before it is mounted."""
    dest = Path(dest)
    if not (dest / ".git").is_dir():
        return ["it is not a repository with its own .git directory (a worktree's is a file)"]
    probs = []
    if git(dest, "rev-parse", "HEAD").decode().strip() != commit:
        probs.append("HEAD is not the expected commit")
    if git(dest, "symbolic-ref", "-q", "HEAD", ok=(0, 1)).strip():
        probs.append("HEAD is not detached")
    if git(dest, "rev-parse", "HEAD^{tree}").decode().strip() != tree:
        probs.append("HEAD's tree is not the expected tree")
    if git(dest, "for-each-ref").strip():
        probs.append("it holds refs")
    cfg = git(dest, "config", "--local", "--list").decode("utf-8", "replace")
    if re.search(r"^(remote|branch)\.", cfg, re.M) or "url=" in cfg:
        probs.append("its config names a remote or a branch")
    stored = set(git(dest, "cat-file", "--batch-all-objects", "--batch-check=%(objectname)").decode().split())
    reach = git(dest, "rev-list", "--objects", "HEAD").decode().splitlines()
    reached = {x.split(" ", 1)[0] for x in reach}
    if stored != reached:
        probs.append(f"it stores {len(stored - reached)} objects HEAD does not reach")
    if len(reached) != objects:
        probs.append(f"HEAD reaches {len(reached)} objects, not {objects}")
    if any(b in stored for b in forbidden_blobs):
        probs.append("it holds a blob that must not be in it")
    names = {Path(x.split(" ", 1)[1]).name for x in reach if " " in x}
    if names & set(forbidden_names):
        probs.append("it holds a path that must not be in it")
    if git(dest, "status", "--porcelain", "--ignored").strip():
        probs.append("its working tree is not clean")
    packed = dest / ".git" / "packed-refs"
    if packed.exists() and any(x and not x.startswith("#") for x in packed.read_text("utf-8").splitlines()):
        probs.append("its packed-refs holds a ref")
    logs = dest / ".git" / "logs"
    if logs.exists() and any(p.is_file() and p.stat().st_size for p in logs.rglob("*")):
        probs.append("it keeps a reflog")
    return probs


def repo_files(dest: Path) -> list[str]:
    return sorted(git(dest, "ls-tree", "-r", "--name-only", "HEAD").decode("utf-8").splitlines())


def map_lines(a: list[bytes], b: list[bytes]) -> dict[int, int]:
    """Each line of `a` to its line in `b`, by difflib: a line inside a changed
    block maps to that block's first line in `b`."""
    out = {}
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
        for k in range(i1, i2):
            out[k + 1] = (j1 + (k - i1) + 1) if tag == "equal" else max(j1 + 1, 1)
    return out


# -- the outside sources and the plan ------------------------------------------------
def extract_files(repo: Path, commit: str, paths: list[str]) -> dict[str, bytes]:
    """Files at a pinned commit, read from the repository's object store with
    cat-file blob (git show's plumbing): nothing is written there."""
    return {p: git(repo, "cat-file", "blob", f"{commit}:{p}") for p in paths}


# -- round 6's gate, on the host and in the sandbox ------------------------------------
CHECK_LINE = re.compile(r"^(\w+)\s+(ok|FAIL)\b")
VERDICT_LINE = re.compile(r"^(PASS|FAIL): (\d+) of (\d+) checks hold$")
CONTROL_LINE = re.compile(r"^control\s+(\w+)\s+(.*?)\s+(caught|NOT CAUGHT)$")
CONTROLS_LINE = re.compile(r"^controls: (\d+) of (\d+) caught$")


def parse_gate(text: str) -> dict:
    checks, verdict, controls, lines = {}, None, None, []
    for raw in text.splitlines():
        line = raw.rstrip()
        if m := CONTROL_LINE.match(line):
            lines.append([m.group(1), m.group(2), m.group(3)])
        elif m := CONTROLS_LINE.match(line.strip()):
            controls = [int(m.group(1)), int(m.group(2))]
        elif m := VERDICT_LINE.match(line.strip()):
            verdict = [m.group(1), int(m.group(2)), int(m.group(3))]
        elif m := CHECK_LINE.match(line):
            checks[m.group(1)] = m.group(2)
    return {"checks": checks, "verdict": verdict, "controls": controls, "control_lines": lines}


def compare_gate(host: dict, box: dict) -> tuple[bool, str]:
    """Whether round 6's gate means the same on the host and in the sandbox: each
    check's ok or FAIL, each verdict line and each exit code, for the gate and
    its --control. A control line is compared as a line only when it ends
    "caught" or "NOT CAUGHT"; the gate's other endings ("caught, and masked",
    "NOT CAUGHT: ...", "REFUSED", "CRASHED", "SKIPPED") are compared through the
    controls' summary count alone (verifier-P4's L1: 47 of 48 lines at wave 1's
    copies, 49 of 50 at P5's, are compared as lines)."""
    for mode in ("gate", "control"):
        h, b = host[mode], box[mode]
        if not b.get("complete", False):
            return False, f"{mode}: the sandbox's output was cut short or timed out"
        if h["exit"] != b["exit"]:
            return False, f"{mode}: exit {h['exit']} on the host, {b['exit']} in the sandbox"
        hp, bp = h["parsed"], b["parsed"]
        if mode == "gate":
            if hp["verdict"] is None or bp["verdict"] is None:
                return False, "gate: a verdict line is missing"
            if hp["checks"] != bp["checks"] or hp["verdict"] != bp["verdict"]:
                return False, "gate: the verdicts differ"
        else:
            if hp["controls"] is None or bp["controls"] is None:
                return False, "control: a summary line is missing"
            if hp["controls"] != bp["controls"] or hp["control_lines"] != bp["control_lines"]:
                return False, "control: the verdicts differ"
    return True, "the verdicts match"


def run_gate_host(repo: Path, work: Path, *, script: str = "tools/check_method.py",
                  timeout: float = GATE_TIMEOUT_S) -> dict:
    """The gate and its --control on the host, in a fresh clone of the replay
    repository, so the mounted input is never touched. TMP, TEMP and TMPDIR point
    inside `work`, which QS4 owns; the rest of the environment goes unread."""
    clone, tmp = Path(work) / f"host-{secrets.token_hex(4)}", Path(work) / f"tmp-{secrets.token_hex(4)}"
    head = git(repo, "rev-parse", "HEAD").decode().strip()
    git(Path(work), "clone", "-q", "--no-hardlinks", str(Path(repo).resolve()), str(clone.resolve()))
    try:
        git(clone, "checkout", "-q", "--detach", head)
        tmp.mkdir()
        env = dict(os.environ, TMP=str(tmp), TEMP=str(tmp), TMPDIR=str(tmp))
        out = {}
        for mode, extra in (("gate", []), ("control", ["--control"])):
            r = subprocess.run([sys.executable, script, *extra], cwd=clone, capture_output=True, env=env,
                               timeout=timeout)
            text = r.stdout.decode("utf-8", "replace")
            out[mode] = {"exit": r.returncode, "parsed": parse_gate(text), "complete": True,
                         "sha256": sha256(text.encode("utf-8"))}
        out["clean_after"] = not git(clone, "status", "--porcelain", "--ignored").strip()
        return out
    finally:
        _remove(clone)
        _remove(tmp)


def run_gate_sandbox(repo: Path, mount: str, scratch: Path, *, script: str = "tools/check_method.py",
                     timeout: float = GATE_TIMEOUT_S, factory=None) -> dict:
    """The gate and its --control in a DockerSandbox, the repository mounted
    read-only at /work/ro/<mount> as a run mounts it. The container is removed."""
    scratch.mkdir(parents=True, exist_ok=False)
    box = (factory or DockerSandbox)(scratch, [Mount(Path(repo), mount, f"{mount}@gate")],
                                     lifetime_s=int(2 * timeout + 600))
    out: dict = {}
    try:
        facts = box.start()
        out["image_id"] = facts.get("image_id")
        for mode, extra in (("gate", ""), ("control", " --control")):
            r = box.shell(f"cd {RO_ROOT}/{mount} && python3 {script}{extra}", timeout)
            text = (r.head + r.tail).decode("utf-8", "replace")
            out[mode] = {"exit": r.exit_code, "parsed": parse_gate(text),
                         "complete": bool(r.complete and not r.timed_out), "sha256": sha256(text.encode("utf-8"))}
    finally:
        out["removed"] = bool(box.stop().get("removed"))
    return out


# -- the local inputs ----------------------------------------------------------------
@dataclass
class Prepared:
    """What a run mounts, and what scoring and the record need to know of it."""
    mounts: list
    repo_files: list
    cut_files: list
    source_files: dict
    facts: dict = field(default_factory=dict)


def current_image_id() -> str:
    from ..agent import docker_status
    ok, why = docker_status()
    if not ok:
        raise InputError("Docker or the sandbox's image is not there, so no input can be mounted")
    return why


class LocalInputs:
    """The round's inputs under local/qs4/, written by tools/qs4_cut.py and
    tools/qs4_rebuild.py, each checked against the committed qs4_expected.json
    whenever it is prepared."""

    def __init__(self, local: Path = LOCAL, *, items: dict | None = None, expected: dict | None = None,
                 image_id: Callable[[], str] = current_image_id):
        self.local, self.items = Path(local), items or ITEMS
        self.expected = EXPECTED if expected is None else expected
        self.image_id = image_id

    def _index(self, name: str) -> dict:
        p = self.local / name
        if not p.is_file():
            raise InputError(f"no {name} under local/qs4: build the inputs with tools/qs4_cut.py and "
                             f"tools/qs4_rebuild.py")
        return load_json(p)

    def prepare(self, item_id: str) -> Prepared:
        item = item_spec(self.items, item_id)
        parcel = self.items["parcels"][item["parcel"]]
        exp = self.expected
        if item_id not in (exp.get("repos") or {}) or item_id not in (exp.get("cuts") or {}):
            raise InputError(f"qs4_expected.json pins no inputs for {item_id}")
        cuts, built = self._index("cuts.json"), self._index("built.json")
        if item_id not in cuts or item_id not in built.get("items", {}):
            raise InputError(f"{item_id} was not built")
        # the cut
        cut_dir = self.local / cuts[item_id]["dir"]
        files = read_files(cut_dir)
        if tree_digest(files) != exp["cuts"][item_id]["digest"]:
            raise InputError("the cut's digest is not the one qs4_expected.json pins")
        # the repository
        b, e = built["items"][item_id], exp["repos"][item_id]
        repo = self.local / b["repo"]
        probs = repo_problems(repo, e["commit"], e["tree"], e["objects"],
                              forbidden_blobs=(exp["archive"]["blob"],))
        if probs:
            raise InputError("the replay repository fails its checks: " + "; ".join(probs))
        if e["commit"] != item_commit(self.items, item):
            raise InputError("qs4_expected.json pins another commit for this item")
        # round 6's gate, compared on these inputs with this image
        g = b.get("gate") or {}
        if not g.get("held") or g.get("commit") != e["commit"]:
            raise InputError("round 6's gate was not shown to mean the same on the host and in the sandbox "
                             "for this repository")
        if g.get("image_id") != self.image_id():
            raise InputError("round 6's gate was compared with another sandbox image")
        # the plan and the outside sources
        plan_dir = self.local / built["plan"]["dir"]
        plan_files = read_files(plan_dir)
        if {k: sha256(v) for k, v in plan_files.items()} != {self.items["plan"]["path"]: exp["plan"]["sha256"]}:
            raise InputError("the plan of record is not the one qs4_expected.json pins")
        src_dir = self.local / built["sources"]["dir"]
        src_files = read_files(src_dir)
        if {k: sha256(v) for k, v in src_files.items()} != exp["sources"]["files"]:
            raise InputError("the outside sources are not the ones qs4_expected.json pins")
        p = item["parcel"]
        mounts = [Mount(repo, f"r6-vcopy-{p}", f"r6-vcopy-{p}@{e['commit'][:7]}"),
                  Mount(cut_dir, LEDGER_MOUNT, f"ledger-cut@{exp['cuts'][item_id]['digest'][:12]}"),
                  Mount(plan_dir, PLAN_MOUNT, f"plan@{exp['plan']['sha256'][:12]}")]
        source_files: dict[str, list] = {}
        for s in self.items["sources"]:
            mounts.append(Mount(src_dir / s["name"], s["name"], f"{s['name']}@{s['commit'][:7]}"))
            source_files[s["name"]] = sorted(k.split("/", 1)[1] for k in src_files
                                             if k.split("/", 1)[0] == s["name"])
        return Prepared(mounts=mounts, repo_files=e["files"], cut_files=sorted(files),
                        source_files=source_files,
                        facts={"commit": e["commit"][:12], "cut": exp["cuts"][item_id]["digest"][:12],
                               "plan": exp["plan"]["sha256"][:12],
                               "sources": exp["sources"]["digest"][:12], "gate_held": True,
                               "parcel_base": parcel["base"][:12]})


# -- the run -----------------------------------------------------------------------
REPORT_SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {"enum": ["READY", "NOT READY"]},
        "findings": {"type": "array", "items": {
            "type": "object",
            "properties": {
                "class": {"enum": list(CLASSES)},
                "file": {"type": "string", "minLength": 1},
                "lines": {"type": "string", "pattern": "^[0-9]+(-[0-9]+)?$"},
                "statement": {"type": "string", "minLength": 1}},
            "required": ["class", "file", "statement"],
            "additionalProperties": False}},
        "text": {"type": "string"}},
    "required": ["verdict", "findings", "text"],
    "additionalProperties": False,
}
ESCALATE_SCHEMA = {"type": "object", "properties": {"question": {"type": "string", "minLength": 1}},
                   "required": ["question"], "additionalProperties": False}


def qs4_tools(budgets: Budgets, prompt: dict) -> list[Tool]:
    reply = prompt["escalate-reply"]
    return builtin_tools(budgets, report=False) + [
        Tool("escalate", prompt["escalate-tool"], ESCALATE_SCHEMA, lambda args, env: ToolOutcome(text=reply)),
        Tool("report", prompt["report-tool"], REPORT_SCHEMA,
             lambda args, env: ToolOutcome(text="the report is received, and the run ends"), ends_run=True),
    ]


def render_messages(prompt: dict, items: dict, item: dict) -> list[dict]:
    """The system message, and the dispatch message with its adaptation."""
    p = items["parcels"][item["parcel"]]
    values = {"parcel": item["parcel"], "repos": RO_ROOT, "scratch": SCRATCH,
              "commit": item_commit(items, item)[:7], "parent": p["base"][:7],
              "extra": prompt["p5-extra"] if p["wave"] == 2 else ""}
    fill = lambda name: string.Template(prompt[name]).substitute(values).strip()  # noqa: E731
    return [{"role": "system", "content": fill("system")},
            {"role": "user", "content": fill("dispatch") + "\n\n" + fill("adaptation")}]


def docker_factory(scratch: Path, mounts: list, budgets: Budgets):
    return DockerSandbox(scratch, mounts)       # run_agent gives it its lifetime at start


def read_back(sandbox, path: str, cap: int) -> dict:
    """The verifier's ledger file, read through P2's scratch manifest: only a
    regular file is read, up to `cap` bytes, and its bytes must hash as the
    manifest says. A link, an unreadable entry or an absence is recorded as such,
    never followed."""
    try:
        entry = next((e for e in sandbox.scratch_manifest() if e["path"] == path), None)
    except Exception as e:  # noqa: BLE001 - the read-back must not lose the run
        return {"kind": "unreadable", "bytes": None, "text": None, "why": type(e).__name__}
    if entry is None:
        return {"kind": "absent", "bytes": None, "text": None}
    if entry["kind"] != "file":
        return {"kind": entry["kind"], "bytes": entry.get("bytes"), "text": None}
    if entry["bytes"] is not None and entry["bytes"] > cap:
        return {"kind": "too large", "bytes": entry["bytes"], "text": None}
    try:
        if hasattr(sandbox, "files"):                       # P2's ScriptedSandbox
            data = sandbox.files[path]
        else:
            rel = path[len(SCRATCH) + 1:]
            with open(Path(sandbox.scratch) / rel, "rb") as f:
                data = f.read(cap + 1)
    except (OSError, KeyError) as e:
        return {"kind": "unreadable", "bytes": entry.get("bytes"), "text": None, "why": type(e).__name__}
    if entry.get("sha256") and sha256(data) != entry["sha256"]:
        return {"kind": "changed", "bytes": len(data), "text": None}
    return {"kind": "file", "bytes": len(data), "text": data.decode("utf-8", "replace")}


# -- the score -----------------------------------------------------------------------
def parse_lines(value) -> list[int] | None:
    if value is None:
        return None
    m = re.fullmatch(r"\s*(\d+)\s*(?:-\s*(\d+))?\s*", str(value))
    if not m:
        return None
    a, b = int(m.group(1)), int(m.group(2) or m.group(1))
    return [min(a, b), max(a, b)]


def normalise_file(raw: str, parcel: str, repo: list, cut: list, sources: dict) -> tuple[str, list | None]:
    """A finding's file, as one of: a file of the repository at its commit, a
    file of the cut ("ledger/<path>"), an outside source ("<repo>/<path>"), the
    commit message, or "<unlisted>"; with any line number written into it."""
    s = str(raw).strip().strip("`'\"").replace("\\", "/").strip()
    lines = None
    m = re.search(r"(?:#L|:)(\d+)(?:-L?(\d+))?$", s)
    if m:
        lines, s = parse_lines(m.group(1) + ("-" + m.group(2) if m.group(2) else "")), s[:m.start()]
    if "commit message" in s.lower():
        return COMMIT_MESSAGE, lines
    for prefix in (f"{RO_ROOT}/r6-vcopy-{parcel}/", f"<repos>/r6-vcopy-{parcel}/", f"r6-vcopy-{parcel}/"):
        if s.startswith(prefix):
            s = s[len(prefix):]
    while s.startswith("./"):
        s = s[2:]
    folded = {f.lower(): f for f in repo}
    if s.lower() in folded:
        return folded[s.lower()], lines
    for prefix in (f"{RO_ROOT}/{LEDGER_MOUNT}/", f"<repos>/{LEDGER_MOUNT}/", f"{LEDGER_MOUNT}/", "ledger/"):
        if s.startswith(prefix) and s[len(prefix):] in cut:
            return "ledger/" + s[len(prefix):], lines
    if s in cut:
        return "ledger/" + s, lines
    for name, paths in sources.items():
        for prefix in (f"{RO_ROOT}/{name}/", f"<repos>/{name}/", f"{name}/"):
            if s.startswith(prefix) and s[len(prefix):] in paths:
                return f"{name}/{s[len(prefix):]}", lines
    return UNLISTED, lines


def meets(lines: list | None, spans: list, tol: int) -> bool:
    if lines is None:
        return False
    a, b = lines
    return any(a <= e + tol and b >= s - tol for s, e in spans)


def _phrase(p: str) -> re.Pattern:
    parts = [re.escape(w.rstrip("*")) + (r"[A-Za-z0-9-]*" if w.endswith("*") else "") for w in p.split()]
    return re.compile(r"(?<![A-Za-z0-9])" + r"\s+".join(parts) + r"(?![A-Za-z0-9])", re.IGNORECASE)


def markers_hit(statement: str, markers: list) -> bool:
    """True when one marker set's phrases all occur in the statement, each as
    whole words, case folded. A phrase ending in * matches a word's start."""
    return any(all(_phrase(ph).search(statement or "") for ph in alt) for alt in markers)


def score_report(report: dict | None, items: dict, item: dict, expected: dict, prep: Prepared) -> tuple[dict, list]:
    """The script's score: what goes in outcome.data (no model text), and each
    finding's detail for the local transcript."""
    parcel = items["parcels"][item["parcel"]]
    tol = items["settings"]["tolerance"]
    if report is None:
        return {"reported": False, "verdict": None, "findings": [], "plants": [], "r6": []}, []
    found, detail = [], []
    for i, f in enumerate(report.get("findings") or []):
        file, inline = normalise_file(f.get("file", ""), item["parcel"], prep.repo_files, prep.cut_files,
                                      prep.source_files)
        lines = parse_lines(f.get("lines")) or inline
        found.append({"file": file, "lines": lines, "class": f.get("class"), "matched": None,
                      "matched_by": None, "stated": None})
        detail.append({"index": i, "file_as_given": f.get("file"), "lines_as_given": f.get("lines"),
                       "statement": f.get("statement")})
    plants = []
    if item["kind"] == "planted":
        for pl in parcel["plants"]:
            span = expected["plant_spans"][pl["id"]]
            located = [k for k, f in enumerate(found)
                       if f["file"] == span["file"] and meets(f["lines"], [span["lines"]], tol)]
            stated = [k for k in located if markers_hit(detail[k]["statement"], pl["markers"])]
            for k in located:
                if found[k]["matched"] is None:
                    found[k].update(matched=f"plant:{pl['id']}", matched_by="lines", stated=k in stated)
            plants.append({"id": pl["id"], "shape": pl["shape"], "located": bool(located),
                           "stated": bool(stated), "caught": bool(stated)})
    tip_lines = expected.get("r6_tip_lines", {})
    r6 = []
    for r in parcel["r6_findings"]:
        if r["copy_only"] and item["kind"] == "real":
            continue
        spans = r["lines"] if item["kind"] == "planted" else tip_lines.get(r["id"], r["lines"])
        hit = False
        for f in found:
            if f["file"] != r["file"]:
                continue
            by = "lines" if spans and meets(f["lines"], spans, tol) else ("file" if not spans else None)
            if by:
                hit = True
                if f["matched"] is None:
                    f.update(matched=f"r6:{r['id']}", matched_by=by)
        r6.append({"id": r["id"], "class": r["class"], "in_view": r["in_view"], "located": hit})
    return {"reported": True, "verdict": report.get("verdict"), "findings": found, "plants": plants, "r6": r6}, detail


def _n(k: int, noun: str) -> str:
    return f"{k} {noun}" + ("" if k == 1 else "s")


def counts(sc: dict) -> dict:
    found = sc["findings"]
    by_class: dict = {}
    for f in found:
        by_class[f["class"]] = by_class.get(f["class"], 0) + 1
    return {"findings": len(found), "by_class": by_class,
            "unmatched": sum(1 for f in found if f["matched"] is None),
            "plants": len(sc["plants"]),
            "plants_located": sum(p["located"] for p in sc["plants"]),
            "plants_caught": sum(p["caught"] for p in sc["plants"]),
            "r6_in_view": sum(1 for r in sc["r6"] if r["in_view"]),
            "r6_in_view_located": sum(1 for r in sc["r6"] if r["in_view"] and r["located"])}


# -- the suite -----------------------------------------------------------------------
class QS4(Suite):
    """One QS4 item, run as round 6's verifier of its parcel. Each subclass names
    one item, so tools/live.py builds it with no arguments and its run is one
    batch. Building it checks the item's inputs, so a missing or changed input
    is refused before any spend."""

    ITEM = ""
    caps = Caps(**ITEMS["caps"])
    version = VERSION

    def __init__(self, *, inputs=None, sandbox_factory: Callable | None = None, items: dict | None = None,
                 expected: dict | None = None, prompt: dict | None = None, run_dir: Path | None = None,
                 stream: bool | None = None, local: Path | None = None):
        if not self.ITEM:
            raise TypeError("QS4 is run through one of its item classes, such as QS4P2Planted")
        self.spec = items or ITEMS
        self.expected = EXPECTED if expected is None else expected
        self.prompt = prompt or PROMPT
        missing = [s for s in PROMPT_SECTIONS if s not in self.prompt]
        if missing:
            raise InputError(f"qs4_prompt.md lacks the sections {missing}")
        self.item = item_spec(self.spec, self.ITEM)
        self.inputs = inputs if inputs is not None else LocalInputs(
            local or LOCAL, items=self.spec, expected=self.expected)
        self.inputs.prepare(self.ITEM)                   # refuse before any spend
        self.sandbox_factory = sandbox_factory or docker_factory
        self.run_dir = Path(run_dir) if run_dir else Path(local or LOCAL) / "runs"
        self.budgets = Budgets(**self.spec["budgets"])
        self.stream = self.spec["settings"]["stream"] if stream is None else stream

    def items(self) -> list[Item]:
        return [Item(self.item["id"], {"parcel": self.item["parcel"], "kind": self.item["kind"]})]

    def _data(self, **kw) -> dict:
        p = self.spec["parcels"][self.item["parcel"]]
        return {"format": 1, "item": self.item["id"], "parcel": self.item["parcel"], "kind": self.item["kind"],
                "wave": p["wave"], **kw}

    def run_item(self, ctx, item: Item) -> ItemResult:
        parcel = self.item["parcel"]
        try:
            prep = self.inputs.prepare(item.id)          # again, immediately before mounting
        except InputError as e:
            return ItemResult("error", f"an input failed its checks, so nothing was mounted and no call was "
                                       f"made: {e}", {"qs4": self._data(status_basis="input")})
        scratch = self.run_dir / secrets.token_hex(6)
        (scratch / f"r6-v{parcel}").mkdir(parents=True)
        box = self.sandbox_factory(scratch, prep.mounts, self.budgets)
        res = run_agent(ctx, messages=render_messages(self.prompt, self.spec, self.item),
                        tools=qs4_tools(self.budgets, self.prompt), sandbox=box, budgets=self.budgets,
                        stream=self.stream)
        ledger = read_back(box, f"{SCRATCH}/verifier-{parcel}.md", self.spec["settings"]["ledger_file_cap"])
        report = res.report if res.outcome == "reported" else None
        sc, detail = score_report(report, self.spec, self.item, self.expected, prep)
        c = counts(sc)
        kind = self.item["kind"]

        def judge(r) -> tuple[str, str]:
            if r.outcome != "reported":
                return "fail", "the run ended without a report"
            if kind == "planted":
                return (("pass" if c["plants_caught"] == c["plants"] else "fail"),
                        f"reported: {c['plants_caught']} of {c['plants']} plants caught by the screen, in "
                        f"{_n(c['findings'], 'finding')}; the lead's judgement is the score of record")
            return "pass", (f"reported: {_n(c['findings'], 'finding')}, for the lead to adjudicate against "
                            f"round 6's record")

        result = res.item_result(judge)
        basis = ("agent" if res.outcome in ("stopped", "error") else
                 "screen" if kind == "planted" and report is not None else "reported")
        # A stopped or errored run never reported, so its score is empty: nothing
        # of a run that did not finish is scored as "found nothing".
        result.data["qs4"] = self._data(
            inputs=prep.facts, **sc, counts=c if report is not None else None,
            escalations=res.tool_calls.get("escalate", 0),
            ledger_file={"kind": ledger["kind"], "bytes": ledger["bytes"]}, status_basis=basis)
        result.local["qs4"] = {"report": res.report, "ledger_file": ledger, "findings": detail,
                               "scored": res.outcome == "reported"}
        return result


def _suite(item_id: str) -> type:
    name = "QS4" + "".join(part.capitalize() for part in item_id.split("-"))
    return type(name, (QS4,), {"ITEM": item_id, "name": f"qs4-{item_id}", "__module__": __name__,
                               "__doc__": f"QS4's item {item_id}: one run, one batch."})


QS4P1Planted = _suite("p1-planted")
QS4P1Real = _suite("p1-real")
QS4P2Planted = _suite("p2-planted")
QS4P2Real = _suite("p2-real")
QS4P3Planted = _suite("p3-planted")
QS4P3Real = _suite("p3-real")
QS4P4Planted = _suite("p4-planted")
QS4P4Real = _suite("p4-real")
QS4P5Planted = _suite("p5-planted")
QS4P5Real = _suite("p5-real")
SUITES = [QS4P1Planted, QS4P1Real, QS4P2Planted, QS4P2Real, QS4P3Planted, QS4P3Real, QS4P4Planted,
          QS4P4Real, QS4P5Planted, QS4P5Real]


# -- the table -----------------------------------------------------------------------
PLANT_VERDICTS = ("caught", "missed")
FINDING_VERDICTS = ("match", "new true", "false alarm")
JUDGEMENT_KEYS = {"record_id", "plant", "finding", "verdict", "r6", "by", "checked_by", "note"}


def load_judgements(path: Path = JUDGEMENTS_PATH) -> list[dict]:
    return load_json(path)["judgements"]


def judgement_problems(judgements: list[dict], items: dict = ITEMS) -> list[str]:
    """What is wrong with the lead's judgements' form: each judges either a plant
    (caught or missed) or a finding by its index (a match to a named round-6
    finding, new and true, or a false alarm), and names who judged and who
    checked."""
    plants = {pl["id"] for p in items["parcels"].values() for pl in p["plants"]}
    r6 = {r["id"] for p in items["parcels"].values() for r in p["r6_findings"]}
    probs = []
    for k, j in enumerate(judgements):
        if set(j) != JUDGEMENT_KEYS:
            probs.append(f"{k}: its keys are not {sorted(JUDGEMENT_KEYS)}")
            continue
        if (j["plant"] is None) == (j["finding"] is None):
            probs.append(f"{k}: it judges neither or both of a plant and a finding")
        elif j["plant"] is not None and (j["plant"] not in plants or j["verdict"] not in PLANT_VERDICTS):
            probs.append(f"{k}: an unknown plant, or a verdict not in {PLANT_VERDICTS}")
        elif j["finding"] is not None and (not isinstance(j["finding"], int) or j["verdict"] not in FINDING_VERDICTS
                                           or (j["verdict"] == "match") != (j["r6"] in r6)):
            probs.append(f"{k}: a finding's verdict not in {FINDING_VERDICTS}, or a match without its round-6 id")
        if not (isinstance(j["record_id"], str) and j["by"] and j["checked_by"]):
            probs.append(f"{k}: no record, judge or checker named")
    return probs


def table(records: list[dict], judgements: list[dict] | None = None) -> dict:
    """QS4's results by item, with wave 1 and P5 apart: the status, the plants
    caught by the screen and, where the lead has judged, by judgement; the
    findings and those matched to round 6's record; tokens and cost."""
    judged = {}
    for j in judgements or []:
        if j.get("plant"):
            judged[(j["record_id"], j["plant"])] = j["verdict"] == "caught"
    rows = {}
    for r in records:
        q = (r.get("outcome", {}).get("data") or {}).get("qs4")
        if not q:
            continue
        c = q.get("counts") or {}
        plants = [p["id"] for p in q.get("plants", [])]
        verdicts = [judged[(r["record_id"], p)] for p in plants if (r["record_id"], p) in judged]
        rows[r["record_id"]] = {
            "item": q["item"], "parcel": q["parcel"], "kind": q["kind"], "wave": q["wave"],
            "status": r["outcome"]["status"], "verdict": q.get("verdict"),
            "plants_caught_screen": c.get("plants_caught"),
            # judged only once every plant of the run is: a partial judgement counts nothing
            "plants_caught_judged": sum(verdicts) if plants and len(verdicts) == len(plants) else None,
            "findings": c.get("findings"), "unmatched": c.get("unmatched"),
            "r6_in_view_located": c.get("r6_in_view_located"), "r6_in_view": c.get("r6_in_view"),
            "read": r["usage"]["cache_hit"] + r["usage"]["cache_miss"], "cache_hit": r["usage"]["cache_hit"],
            "output": r["usage"]["output"], "cost_usd": r["cost_usd"], "calls": r["calls"]}
    waves = {}
    for w in (1, 2):
        sel = [x for x in rows.values() if x["wave"] == w and x["kind"] == "planted"]
        waves[f"wave{w}"] = {"runs": len(sel),
                             "plants_caught_screen": sum(x["plants_caught_screen"] or 0 for x in sel)}
    return {"rows": rows, "planted_by_wave": waves}
