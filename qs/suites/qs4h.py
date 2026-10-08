"""QS4h: QS4's code slice. This round's own four planted copies, and their four real
tips, each replayed to a model working as this round's Sonnet verifier of it worked
(the plan's amendment 1, Rounds/HonestHarness-R1/AMENDMENT-1.md, approved at b310f82).

Eight items, one suite class each, so that tools/live.py builds each with no arguments
and each run is its own batch: h1 (P1's QS1), h2 (P2's agent loop and sandbox), h3 (P3's
QS6 slice) and h4 (P4's QS4), each planted and real. The real tips are the false-alarm
set. The names stand apart from QS4's p1 to p5, which are round 6's.

What a run has, what that verifier had (A1.3):
- the repository, read-only, one commit above the parcel's base in both conditions, and
  holding only the objects its commit reaches;
- this round's ledger, cut at the stamp of the lead's entry that records the copy and
  its sealed key hash, without keys/ and without the parcel's own file;
- ParcelRound at f42242e, for h2 to h4, at <repos>/parcelround-worktrees/P0, the path
  the ledger and the briefs name;
- DeepSeek's documentation copies, the whole directory as it stood at every dispatch,
  for h1 and h3 (lead.md 14:32:37, answer 8);
- for h4, the twelve outside files QS4 pins, as plain files (answer 2);
- a dispatch message rebuilt from the lead's entries, with roots in place of paths, and
  the adaptation the sandbox needs. That text, qs4h_prompt.md, is the prompt version.
  It shares no sentence with qs4_prompt.md that plant P4-A touches.
QS6's answer key, which verifier-P3 had, is withheld (A1.3).

The inputs. tools/qs4h_rebuild.py and tools/qs4h_cut.py build them under local/qs4h/,
which is gitignored. qs4h_expected.json pins what each must be.
- The rebuild rule (A1.3). A copy's parent is its base; its tree is the real tip's tree
  with the key's plants, each file's plants in turn; its message is the oldest commit
  above the base; its author and committer lines are the real tip's. It must reproduce
  the key's copy_commit, or the item stops. A real tip is built by the same rule with
  the tip's own tree. For P2 and P3, one commit above their bases already, the build is
  the tip itself.
- A replay repository is QS4's: a local clone with --no-hardlinks, detached, its refs,
  remote and reflogs removed, pruned to its commit's closure, which is asserted. Its
  forbidden blobs: the other condition's versions of the planted files, and the keys.
- The cut is QS4's build_cut over one copy of the live ledger, each file's kept time
  its mtime at -07:00, the stamps' zone. Then:
  - for P1 and P2, the two shared briefs are rebuilt without the desktop-priority item
    added at 15:35:17 and amended at 16:39:34: exactly their pinned lines removed, an
    adaptation the record names by its hashes;
  - both SHAs are mapped: every hex token of 7 to 40 characters that prefixes the real
    tip, the copy or the real-tip build becomes the same-length prefix of the item's own
    commit, so both conditions read alike;
  - a cut is refused when it still holds a prefix of another of those commits, a
    plant's old or new text, a key's description, keys/, the parcel's own file or an
    entry after the stamp, or when it lacks a brief its verifier read. A planted item's
    cut and its real tip's must differ only where the item's own commit stands.
- Host directories are named by SHA or digest, never planted or real.

The guards, each failing closed, at construction (so before any spend) and again in
run_item: the cut's digest, its briefs and its SHAs; the repository's HEAD, tree, object
closure and forbidden blobs, with no refs, no remote and a clean tree; ParcelRound's
repository, the sources' and the ds files' hashes; the image in use, the one built from
sandbox/qs4h.Dockerfile and recorded in local/qs4h/image.json; and the project's own
gate, tools/check.py and its --control, run at the repository on the host (Docker made
unreachable, so both sides skip the same tests, and the clone left clean, ignored files
included) and in the sandbox with that image, whose verdicts matched, or differed only
by a test the data pins as unable to pass on Linux (limit 16). A failure at
construction raises, so tools/live.py spends nothing; in run_item it is recorded as
error, with no call.

The image and the sandbox (A1.4): P2's pinned python:3.12-trixie with the project's
dependency closure installed at build time, 18 wheels pinned by version and SHA-256.
A run's container is P2's sandbox, with no network and no Docker, so the tests that
need Docker skip there, and with one change, HOME (QS4hSandbox, limit 15).

The score. Only the report's findings are scored by script.
- Each plant holds one span per edit, from the line diff of the copy against its
  real-tip build: a replacement is the planted lines it occupies, met within
  settings.tolerance lines; a deletion is its join, the planted lines on either side,
  met within settings.deletion_tolerance lines.
- Located: a finding whose file is an edit's file and whose lines meet that edit's span.
  Stated: its statement holds one of the plant's pre-registered marker sets, as QS4's
  screen matches them. Caught by the screen: located and stated.
- A finding is matched to a plant only when the screen catches it. A located finding
  that is not stated goes on to be matched against this round's recorded findings, so a
  real finding beside a plant is not hidden by it.
- Every other finding is matched by location against the recorded findings of the
  parcel's verifier, for the lead to adjudicate. None is assumed false. The score of
  record is the lead's judgement, checked by a verifier, kept in qs4h_judgements.json.

Statuses, QS4's: stopped and error are P2's loop's, and the judge is never asked about
them; a planted item passes when the screen catches every plant, and fails otherwise,
an empty report included; a real tip passes when it reported; either fails with no
report; an input that fails its checks is error.

What is recorded: outcome.data["qs4h"] holds no model text, only normalised file names
from closed sets, lines, classes, matches, counts and digests' prefixes;
ItemResult.local["qs4h"] holds the report, the verifier's ledger file and each finding's
statement, which stay in the local transcript.

Cost and time. Each run is one batch through P0's runner, at QS4's caps (40,000,000
prompt tokens, 500,000 output, 900,000 a call) on deepseek-flash: one batch reserves
$9.0315264 off-peak at P0's default allowance of three unmetered attempts, and
$27.5780064 at the lead's N = 28. tests/test_qs4h.py works both by hand. The budgets
are QS4's but two, in qs4h_items.json with their derivation: a tool call's timeout is
320 s, 1.5 times a model's --control at h4 in the sandbox, and a run's budget 5,960 s,
so that a run fits the lead's 2 hours (lead.md 19:54:31).

Limits, each stated by the behaviour it concedes:
1. QS4's own limits carry over, by their numbers in qs4.py (A1.10.1): 1 no network,
   3 a file that postdates the cut is absent, 4 the replay's date, 5 the read-only
   copy, 6 the tools, 7 and 8 the screen and location by file and lines, 13 the per-call
   cap, 14 the fixed reply to an escalation, 16 reasoning returned with each request,
   17 mount paths that show host names, 18 a stopped run's findings kept locally and
   unscored, 19 the ledger file read back to a cap, and 21 the history's author lines,
   which carry the owner's address to the provider (allowed, lead.md 12:48:48).
2. This round's verifiers worked in Claude Code on the host, with mutation pools, real
   containers and a registry read. The replay's model has P2's sandbox: 2 CPUs, 2 GiB,
   no network and no Docker. Verifier-P2's Docker items cannot be run here.
3. The false-alarm set is told plants exist: _verifier.md and the dispatch entries say
   the copy holds planted faults, of a real tip that holds none.
4. QS6's answer key is withheld, so plant P3-B shows only from round 6's ledger.
5. The replay reads its own machinery. h4's copy holds QS4's prompt template and its
   screen, and QS4h scores with qs4.py's functions. h1 to h3 hold smaller parts: the
   suites and the loop that run it.
6. The two rebuilt shared briefs cannot be checked byte for byte against what P1's and
   P2's verifiers read; their removal is pinned by its hashes.
7. Each cut holds the lead's entries to its stamp, with both SHAs mapped, so the two
   conditions' cuts differ wherever the item's own commit stands. The dispatch message
   is rebuilt from the lead's summaries, not verbatim.
8. A deletion's span is its join, met within a fixed deletion_tolerance. A finding about
   a deletion that cites only lines farther off, such as the docstring the deletion
   contradicts, is not located.
9. Plant P3-A's marker set is its change's two names, and its evidence line beside it
   holds one of them, so a quotation of lines 76 and 77 passes the screen. Plant P4-B's
   span holds the judge's detail line, and a statement quoting a planted run's rendered
   detail ("1 of 2 plants caught") passes its [1 of 2] set without stating the plant.
10. In h4, tools/qs4_rebuild.py cannot run whole, since the outside sources are plain
    files and there is no Docker; P4's own build, which verifier-P4 compared with its
    own, is not given.
11. The cuts come from one copy of the live ledger. A shared brief edited after it, or a
    file changed, makes a rebuild of the inputs refuse; nothing is guessed.
12. A1.8's code fields exist only on records written after b79217a; the live entry's
    flags are in no run record.
13. Contamination: DeepSeek's models predate this round by release date. A model
    trained after the ledger and keys/ are published has the plants.
14. The baseline is Sonnet's, each verifier on its first pass. Opus did not verify these
    copies.
15. QS4h's sandbox sets HOME to /tmp/home, its own tmpfs, where P2's sets /tmp: a
    difference from P2's sandbox and from QS4's runs, accepted at lead.md 15:13:14.
    Under /tmp, P2's own tests/test_sandbox.py fails in a container, since the home's
    parent is the filesystem root there.
16. One of P4's tests cannot pass on Linux: test_qs4_inputs.py's reparse-point case of
    test_a_link_or_reparse_point_in_an_input_directory_is_refused builds an
    os.stat_result with st_reparse_tag, which Linux drops. So in h4's sandbox the gate
    reads FAIL 4 of 5 and --control refuses, where verifier-P4, on the Windows host, read
    5 of 5 and 9 of 9. h4's comparison holds only with that one test pinned
    (parcels.P4.platform_failures; lead.md 15:13:14): the suite passes there without it,
    and it fails alone. A finding that it cannot pass on Linux is true of P4's work.
17. Behaviours no test pins. verifier-P5's mutation sweep (verifier-P5.md 19:50:21, L2)
    left 39 of 140 operator mutants of this module alive against the three test files
    that need no Docker; none is a stated property or a fault today. The recorded
    match's located flag and the unmatched and recorded_in_view_located counts are
    pinned since, in tests/test_qs4h.py. Still unpinned: the results table's judged
    mapping; run_item's status_basis; normalise_file's ledger-prefix case;
    judgement_problems' finding form; which plant owns a diff block that only inserts;
    the ledger copy's link refusal and manifest checks, since this account cannot make
    a link; and rebuild_brief's line boundaries. The lines that face Docker were outside
    the sweep, with tests/test_qs4h_docker.py, the file that pins them.
"""
from __future__ import annotations

import difflib
import hashlib
import json
import os
import re
import secrets
import stat
import string
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable

from ..agent import Budgets, DockerSandbox, Mount, run_agent
from ..agent.sandbox import IMAGE as BASE_IMAGE
from ..agent.sandbox import RO_ROOT, SCRATCH, SandboxError
from ..suite import Caps, Item, ItemResult, Suite
from . import qs4
from .qs4 import InputError, Prepared, git, sha256

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
LOCAL = ROOT / "local" / "qs4h"
ITEMS_PATH = HERE / "qs4h_items.json"
PROMPT_PATH = HERE / "qs4h_prompt.md"
EXPECTED_PATH = HERE / "qs4h_expected.json"
JUDGEMENTS_PATH = HERE / "qs4h_judgements.json"
DOCKERFILE_PATH = ROOT / "sandbox" / "qs4h.Dockerfile"

LEDGER_MOUNT = "honestharness-r1-ledger"
LEDGER_ROOT = LEDGER_MOUNT + "/"
PR_MOUNT, PR_DIR = "parcelround-worktrees", "P0"
DS_MOUNT = "ds"
ZONE = timezone(timedelta(hours=-7))     # every stamp of this round's ledger is -0700
COMMIT_MESSAGE, UNLISTED = qs4.COMMIT_MESSAGE, qs4.UNLISTED
HISTORY = "<history>"
HISTORY_NAMES = {"history", "git log", "git history", "commit history", "author lines", "the history"}
CLASSES = qs4.CLASSES
BUILD_PREFIX = "hh-qs4h-"                # the build's and the tests' containers; live runs are hh-sbx-
IMAGE_REPO = "hh-qs4h-sandbox"
UNREACHABLE_DOCKER = "tcp://127.0.0.1:9"  # the host's half of the gate: Docker unreachable
HEX = re.compile(rb"(?<![0-9a-fA-F])[0-9a-fA-F]{7,40}(?![0-9a-fA-F])")
PROMPT_SECTIONS = ("system", "dispatch", "adaptation", "report-tool", "escalate-tool", "escalate-reply")


# -- the committed data ------------------------------------------------------------------
def _norm(p: Path) -> bytes:
    return qs4._norm(p)


def compute_version() -> str:
    """"1." plus 12 hex digits of the data's SHA-256 (items, prompt, expected and the
    image's Dockerfile) and 12 of the code's (this file and qs4.py, whose functions
    score it), line endings normalised. The lead's judgements do not enter it."""
    data = hashlib.sha256(b"\0".join(_norm(p) for p in (ITEMS_PATH, PROMPT_PATH, EXPECTED_PATH,
                                                         DOCKERFILE_PATH)))
    code = hashlib.sha256(_norm(Path(__file__)) + b"\0" + _norm(Path(qs4.__file__)))
    return f"1.{data.hexdigest()[:12]}.{code.hexdigest()[:12]}"


ITEMS = qs4.load_json(ITEMS_PATH)
PROMPT = qs4.load_prompt(PROMPT_PATH)
EXPECTED = qs4.load_json(EXPECTED_PATH) if EXPECTED_PATH.exists() else {}
VERSION = compute_version()


def item_spec(items: dict, item_id: str) -> dict:
    for it in items["items"]:
        if it["id"] == item_id:
            return it
    raise KeyError(f"no QS4h item {item_id!r}")


def copy_mount(parcel: str) -> str:
    return f"r1-v{parcel}-copy"


def parcel_shas(items: dict, expected: dict, parcel: str) -> dict[str, str]:
    """The copy, the real tip and the real-tip build, full SHAs."""
    p = items["parcels"][parcel]
    build = (expected.get("builds") or {}).get(parcel)
    if not build:
        raise InputError(f"qs4h_expected.json pins no real-tip build for {parcel}: run tools/qs4h_rebuild.py")
    return {"copy": p["copy"], "tip": p["tip"], "build": build}


def own_commit(items: dict, expected: dict, item: dict) -> str:
    shas = parcel_shas(items, expected, item["parcel"])
    return shas["copy"] if item["kind"] == "planted" else shas["build"]


# -- the rebuild (A1.3) ------------------------------------------------------------------
def commits_above(work: Path, base: str, tip: str) -> list[str]:
    return git(work, "rev-list", f"{base}..{tip}").decode().split()


def oldest_above(work: Path, base: str, tip: str) -> str:
    """The one commit above the base that has no parent above it. Two such roots, as
    when a branch merged another line of work in from below the base, are refused: the
    rule names one oldest commit, and nothing is guessed."""
    above = commits_above(work, base, tip)
    if not above:
        raise InputError("the tip is not above its base")
    inside = set(above)
    roots = []
    for c in above:
        parents = git(work, "rev-list", "--parents", "-n", "1", c).decode().split()[1:]
        if not any(x in inside for x in parents):
            roots.append(c)
    if len(roots) != 1:
        raise InputError(f"{len(roots)} commits above the base have no parent above it, not one")
    return roots[0]


def _header(raw: bytes) -> tuple[list[bytes], bytes]:
    head, sep, msg = raw.partition(b"\n\n")
    if not sep:
        raise InputError("a commit object has no message")
    return head.split(b"\n"), msg


def squash_commit(work: Path, base: str, tip: str, tree: str) -> str:
    """A1.3's commit: parent the base, the given tree, the message of the oldest commit
    above the base, and the tip's author and committer lines, written and hashed. A tip
    or oldest commit with any other header (a signature, an encoding) is refused."""
    tip_lines, _ = _header(git(work, "cat-file", "commit", tip))
    oldest = oldest_above(work, base, tip)
    old_lines, msg = _header(git(work, "cat-file", "commit", oldest))
    for lines in (tip_lines, old_lines):
        if any(not x.startswith((b"tree ", b"parent ", b"author ", b"committer ")) for x in lines):
            raise InputError("a commit carries a header besides tree, parent, author and committer")
    who = [x for x in tip_lines if x.startswith((b"author ", b"committer "))]
    if [x.split(b" ", 1)[0] for x in who] != [b"author", b"committer"]:
        raise InputError("the tip's commit does not hold one author line, then one committer line")
    full_base = git(work, "rev-parse", "--verify", f"{base}^{{commit}}").decode().strip()
    body = (b"tree " + tree.encode() + b"\nparent " + full_base.encode() + b"\n" + b"\n".join(who)
            + b"\n\n" + msg)
    return git(work, "hash-object", "-t", "commit", "-w", "--stdin", input=body).decode().strip()


def rebuild_parcel(work: Path, key: dict, base: str) -> dict:
    """The copy, refused unless it reproduces the key's copy_commit, and the real-tip
    build. Returns their SHAs, the planted files' bytes and the oldest commit."""
    tip = key["real_tip"]
    if key.get("base") and key["base"] != base:
        raise InputError("the key's base is not the parcel's")
    blobs = qs4.planted_blobs(work, tip, key["plants"])
    planted = qs4.planted_tree(work, tip, blobs)
    copy = squash_commit(work, base, tip, planted)
    if copy != key["copy_commit"]:
        raise InputError(f"the rebuilt copy is {copy[:7]}, not the key's {key['copy_commit'][:7]}")
    tip_tree = git(work, "rev-parse", f"{tip}^{{tree}}").decode().strip()
    build = squash_commit(work, base, tip, tip_tree)
    return {"copy": copy, "build": build, "blobs": blobs, "oldest": oldest_above(work, base, tip)}


def _opcodes(a: list[bytes], b: list[bytes]):
    return [op for op in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes() if op[0] != "equal"]


def plant_edits(work: Path, tip: str, key: dict, blobs: dict[str, bytes]) -> dict[str, list[dict]]:
    """Each plant's edits, by the key's plant id, from the line diff of each planted
    file against the real tip's.
    - A replacement or an insertion is the planted lines it occupies.
    - A deletion is its join: the planted lines on either side of the removed block.
    Each block of the diff goes to the one plant whose old text alone changes the same
    tip lines; a block no single plant explains is refused, as is a plant whose old text
    is not unique in the tip's file."""
    out: dict[str, list[dict]] = {}
    for file, planted in blobs.items():
        tip_bytes = git(work, "cat-file", "blob", f"{tip}:{file}")
        a, b = tip_bytes.split(b"\n"), planted.split(b"\n")
        owners = []
        for p in key["plants"]:
            if p["file"] != file:
                continue
            old, new = p["old"].encode("utf-8"), p["new"].encode("utf-8")
            if tip_bytes.count(old) != 1:
                raise InputError(f"a plant's old text is not unique in the tip's {file}")
            touched, points = set(), set()
            for _tag, i1, i2, _j1, _j2 in _opcodes(a, tip_bytes.replace(old, new, 1).split(b"\n")):
                touched |= set(range(i1, i2))
                if i1 == i2:
                    points.add(i1)
            owners.append((p["id"], touched, points))
        for tag, i1, i2, j1, j2 in _opcodes(a, b):
            span = set(range(i1, i2))
            ids = {pid for pid, t, pts in owners if (span & t) or (i1 == i2 and i1 in pts)}
            if len(ids) != 1:
                raise InputError(f"a diff block of {file} that no single plant explains")
            if tag == "delete":
                edit = {"file": file, "kind": "deletion", "lines": [max(j1, 1), j1 + 1], "tip_lines": [i1 + 1, i2]}
            else:
                edit = {"file": file, "kind": "replacement" if tag == "replace" else "insertion",
                        "lines": [j1 + 1, j2], "tip_lines": [i1 + 1, i2] if i2 > i1 else [i1, i1]}
            out.setdefault(ids.pop(), []).append(edit)
    return out


def tip_lines_of(spans: list, copy_blob: bytes | None, tip_blob: bytes | None) -> list:
    """A recorded finding's spans at the copy, mapped to the real-tip build's lines by
    QS4's line map; a file the plants did not touch maps to itself."""
    if not spans or copy_blob is None or tip_blob is None or copy_blob == tip_blob:
        return [list(s) for s in spans]
    m = qs4.map_lines(copy_blob.split(b"\n"), tip_blob.split(b"\n"))
    if any(s not in m or e not in m for s, e in spans):
        raise InputError("a recorded finding cites a line its file at the copy does not have")
    return [[m[s], m[e]] for s, e in spans]


# -- the ledger's copy and the cut -----------------------------------------------------------
def kept_time(mtime: float) -> str:
    return datetime.fromtimestamp(mtime, ZONE).strftime("%Y-%m-%d %H:%M:%S")


def snapshot_ledger(src: Path) -> list[dict]:
    """The live ledger read once: every regular file, with its bytes, SHA-256, size and
    kept time (its mtime at -07:00, to the second). A link, or any entry that is not a
    regular file, is refused, never followed. Nothing in the source is written."""
    src = Path(src)
    if not src.is_dir():
        raise InputError("the ledger directory is absent")
    out = []
    for d, dirs, names in os.walk(src, followlinks=False):
        dirs.sort()
        for name in dirs + names:
            st = os.lstat(Path(d) / name)
            if stat.S_ISLNK(st.st_mode) or getattr(st, "st_reparse_tag", 0):
                raise InputError("the ledger holds a link")
        for name in sorted(names):
            p = Path(d) / name
            data = p.read_bytes()
            st = os.lstat(p)
            if not stat.S_ISREG(st.st_mode):
                raise InputError("the ledger holds an entry that is not a regular file")
            out.append({"path": p.relative_to(src).as_posix(), "sha256": sha256(data), "bytes": len(data),
                        "kept": kept_time(st.st_mtime), "data": data})
    return out


def write_snapshot(entries: list[dict], local: Path) -> Path:
    """The copy under <local>/ledger/<12 hex of its manifest's digest>/: files/ and
    manifest.json. A copy already there is checked, not rewritten."""
    manifest = [{k: e[k] for k in ("path", "sha256", "bytes", "kept")} for e in entries]
    text = json.dumps(manifest, indent=1, sort_keys=True) + "\n"
    dest = Path(local) / "ledger" / sha256(text.encode("utf-8"))[:12]
    if dest.exists():
        if load_snapshot(dest)[1] != manifest:
            raise InputError("a ledger copy of that digest holds other files")
        return dest
    qs4.write_files({e["path"]: e["data"] for e in entries}, dest / "files")
    (dest / "manifest.json").write_text(text, encoding="utf-8", newline="\n")
    return dest


def load_snapshot(dest: Path) -> tuple[dict[str, tuple[bytes, str]], list[dict]]:
    """The copy's members, as QS4's build_cut takes them, each checked against its
    manifest entry."""
    manifest = json.loads((Path(dest) / "manifest.json").read_text(encoding="utf-8"))
    files = qs4.read_files(Path(dest) / "files")
    if sorted(files) != sorted(m["path"] for m in manifest):
        raise InputError("the ledger copy's files are not its manifest's")
    members = {}
    for m in manifest:
        data = files[m["path"]]
        if sha256(data) != m["sha256"] or len(data) != m["bytes"]:
            raise InputError("a file of the ledger copy is not its manifest's")
        members[LEDGER_ROOT + m["path"]] = (data, m["kept"])
    return members, manifest


def rebuild_brief(data: bytes, edit: dict) -> bytes:
    """A shared brief as dispatched: its pinned lines removed. The source must be the
    text pinned, the lines removed must hash as pinned, and the result must name none of
    edit["absent"]."""
    if sha256(data) != edit["source_sha256"]:
        raise InputError(f"{edit['file']} is not the text its rebuild was pinned on")
    lines = data.splitlines(keepends=True)
    a, b = edit["lines"]
    if not 1 <= a <= b <= len(lines) or sha256(b"".join(lines[a - 1:b])) != edit["removed_sha256"]:
        raise InputError(f"the lines removed from {edit['file']} are not the pinned ones")
    out = b"".join(lines[:a - 1] + lines[b:])
    if any(t.encode("utf-8") in out for t in edit["absent"]):
        raise InputError(f"the rebuilt {edit['file']} still names the item it should not")
    return out


def map_shas(files: dict[str, bytes], shas: list[str], own: str) -> dict[str, bytes]:
    """Every hex token of 7 to 40 characters that prefixes one of `shas` becomes the
    same-length prefix of `own`, the item's own commit."""
    def sub(m: re.Match) -> bytes:
        t = m.group(0).decode().lower()
        return own[:len(t)].encode() if any(s.startswith(t) for s in shas) else m.group(0)
    return {k: HEX.sub(sub, v) for k, v in files.items()}


def sha_problems(files: dict[str, bytes], forbidden: list[str]) -> list[str]:
    """A hex token of 7 or more characters, any case, that prefixes a forbidden SHA."""
    probs = []
    for rel, data in sorted(files.items()):
        for m in HEX.finditer(data):
            t = m.group(0).decode().lower()
            if any(s.startswith(t) for s in forbidden):
                probs.append(f"{rel}: a SHA the cut should have mapped")
                break
    return probs


def mask_own(files: dict[str, bytes], own: str) -> dict[str, bytes]:
    """The cut with every prefix of its own commit masked, for comparing the two
    conditions."""
    return {k: HEX.sub(lambda m: b"#" * len(m.group(0)) if own.startswith(m.group(0).decode().lower())
                       else m.group(0), v) for k, v in files.items()}


def required_files(items: dict, parcel: str) -> list[str]:
    return list(items["required_briefs"]) + [f"briefs/{parcel}.md", f"briefs/verifier-{parcel}.md"]


def absent_texts(keys: dict, parcel: str) -> list[bytes]:
    out = []
    for p in keys[parcel]["plants"]:
        for t in (p["old"], p["new"], p.get("shape", "")):
            if t:
                out.append(t.encode("utf-8"))
    return out


def cut_for(members: dict, items: dict, expected: dict, item: dict, keys: dict) -> dict[str, bytes]:
    """An item's cut: QS4's rule at its stamp, the two briefs rebuilt where the item's
    parcel needs them, both SHAs mapped, then checked."""
    parcel = item["parcel"]
    p = items["parcels"][parcel]
    files = qs4.build_cut(members, LEDGER_ROOT, p["stamp"], parcel)
    rebuild = items["briefs_rebuild"]
    if parcel in rebuild["parcels"]:
        for edit in rebuild["edits"]:
            if edit["file"] in files:
                raise InputError(f"{edit['file']} entered the cut by its time, so its rebuild does not apply")
            src = members.get(LEDGER_ROOT + edit["file"])
            if src is None:
                raise InputError(f"{edit['file']} is not in the ledger")
            files[edit["file"]] = rebuild_brief(src[0], edit)
    shas = parcel_shas(items, expected, parcel)
    own = own_commit(items, expected, item)
    files = map_shas(files, list(shas.values()), own)
    probs = qs4.cut_problems(files, p["stamp"], parcel, absent_texts(keys, parcel))
    probs += sha_problems(files, sorted({s for s in shas.values() if s != own}))
    probs += [f"{f}: a brief its verifier read is missing" for f in required_files(items, parcel) if f not in files]
    if probs:
        raise InputError("the cut fails its checks: " + "; ".join(probs))
    return files


# -- the image (A1.4) and the sandbox ----------------------------------------------------------
SANDBOX_HOME = "/tmp/home"


class QS4hSandbox(DockerSandbox):
    """P2's sandbox, with one change: HOME is /tmp/home, its own small tmpfs, where P2's
    is /tmp. Under HOME=/tmp the home's parent is the filesystem root, so P2's own test of
    the mount checks (tests/test_sandbox.py, the home's parent refused as "the home
    directory") fails in the container, as it never did on the host this round's
    verifiers used: the gate's comparison at P2's copy found it (P5.md). One level
    deeper, the home's parent is /tmp, and the test means the same in both places.
    Everything else is P2's: the network, the read-only root and mounts, the user, the
    limits, the scratch, and git's settings, written to the new HOME."""

    def run_args(self) -> list[str]:
        args = super().run_args()
        if args.count("HOME=/tmp") != 1 or args.count(self.image) != 1:
            raise SandboxError("P2's sandbox no longer starts as QS4h's sandbox expects")
        args[args.index("HOME=/tmp")] = f"HOME={SANDBOX_HOME}"
        i = args.index(self.image)
        return args[:i] + ["--tmpfs", f"{SANDBOX_HOME}:rw,nosuid,nodev,size=64m"] + args[i:]


class BuildSandbox(QS4hSandbox):
    """QS4h's sandbox as its own build and tests start it: the same container, named
    hh-qs4h-<id>, so it is told apart from a live run's hh-sbx-<id>."""

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.name = BUILD_PREFIX + self.run_id


def image_record(local: Path = LOCAL) -> dict:
    p = Path(local) / "image.json"
    if not p.is_file():
        raise InputError("no image.json under local/qs4h: build the image with tools/qs4h_image.py")
    return qs4.load_json(p)


def inspect_image(ref: str) -> str | None:
    """The image's ID, or None when it is absent or Docker does not answer. It never
    pulls."""
    try:
        r = subprocess.run(["docker", "image", "inspect", "--format", "{{.Id}}", ref], capture_output=True,
                           text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None


def current_image_id(local: Path = LOCAL) -> str:
    """The recorded image's ID, refused unless Docker holds it and it was built from the
    committed Dockerfile."""
    rec = image_record(local)
    if rec.get("dockerfile_sha256") != sha256(DOCKERFILE_PATH.read_bytes()):
        raise InputError("the recorded image was built from another sandbox/qs4h.Dockerfile")
    if inspect_image(rec["id"]) != rec["id"]:
        raise InputError("the recorded sandbox image is not in Docker")
    return rec["id"]


# -- the project's gate, on the host and in the sandbox ---------------------------------------
def run_gate_host(repo: Path, work: Path, *, timeout: float, script: str = "tools/check.py") -> dict:
    """The gate and its --control on the host, in a fresh clone of the replay repository
    under `work`, so the input is never touched. TMP, TEMP and TMPDIR point inside
    `work`, and DOCKER_HOST at a closed loopback port, so the tests that need Docker skip
    as they must in the sandbox; PYTHONDONTWRITEBYTECODE is set, as the sandbox sets it,
    so Python's caches are not written. The rest of the environment goes to the child
    unread. The clone must be clean afterwards, ignored files included, as QS4's check
    reads it (verifier-P5's F3): a gate that wrote any file does not hold."""
    clone, tmp = Path(work) / f"host-{secrets.token_hex(4)}", Path(work) / f"tmp-{secrets.token_hex(4)}"
    head = git(repo, "rev-parse", "HEAD").decode().strip()
    git(Path(work), "clone", "-q", "--no-hardlinks", str(Path(repo).resolve()), str(clone.resolve()))
    out: dict = {}
    try:
        git(clone, "checkout", "-q", "--detach", head)
        tmp.mkdir()
        env = dict(os.environ, TMP=str(tmp), TEMP=str(tmp), TMPDIR=str(tmp), DOCKER_HOST=UNREACHABLE_DOCKER,
                   PYTHONDONTWRITEBYTECODE="1")
        for mode, extra in (("gate", []), ("control", ["--control"])):
            t0 = time.monotonic()
            r = subprocess.run([sys.executable, script, *extra], cwd=clone, capture_output=True, env=env,
                               timeout=timeout)
            text = r.stdout.decode("utf-8", "replace")
            out[mode] = {"exit": r.returncode, "parsed": qs4.parse_gate(text), "complete": True,
                         "sha256": sha256(text.encode("utf-8")), "duration_s": round(time.monotonic() - t0, 1)}
        out["clean_after"] = not git(clone, "status", "--porcelain", "--ignored").strip()
        return out
    finally:
        qs4._remove(clone)
        qs4._remove(tmp)


PYTEST_COUNTS = re.compile(r"(\d+) (passed|failed|error|errors)\b")


def _pytest_counts(text: str) -> dict:
    out = {}
    for n, kind in PYTEST_COUNTS.findall(text):
        out[kind.rstrip("s") if kind == "errors" else kind] = int(n)
    return out


def run_gate_sandbox(repo: Path, mount: str, scratch: Path, *, image: str, timeout: float,
                     factory: Callable | None = None, platform_tests: list[str] | None = None) -> dict:
    """The gate and its --control in the sandbox with the given image: the repository
    mounted read-only as a run mounts it, cloned under the scratch as the adaptation
    tells a run to work, the gate run in the clone. With platform_tests, two pytest runs
    follow in the same clone: the suite without those tests, and those tests alone. The
    container is removed."""
    import shlex
    Path(scratch).mkdir(parents=True, exist_ok=False)
    box = (factory or BuildSandbox)(Path(scratch), [Mount(Path(repo), mount, f"{mount}@gate")], image=image,
                                    lifetime_s=int(3 * timeout + 900))
    out: dict = {}
    try:
        facts = box.start()
        out["image_id"] = facts.get("image_id")
        c = box.shell(f"git clone -q {RO_ROOT}/{mount} {SCRATCH}/gate", 600)
        out["clone"] = {"exit": c.exit_code, "duration_s": c.duration_s}
        for mode, extra in (("gate", ""), ("control", " --control")):
            r = box.shell(f"cd {SCRATCH}/gate && python3 tools/check.py{extra}", timeout)
            text = (r.head + r.tail).decode("utf-8", "replace")
            out[mode] = {"exit": r.exit_code, "parsed": qs4.parse_gate(text),
                         "complete": bool(r.complete and not r.timed_out), "sha256": sha256(text.encode("utf-8")),
                         "duration_s": r.duration_s}
        if platform_tests:
            # pyproject's addopts give -q already; a second would drop the count line read here
            base = f"cd {SCRATCH}/gate && python3 -m pytest -p no:cacheprovider -W ignore"
            out["platform"] = {}
            for name, args in (("without", " ".join(f"--deselect {shlex.quote(t)}" for t in platform_tests)),
                               ("alone", " ".join(shlex.quote(t) for t in platform_tests))):
                r = box.shell(f"{base} {args}", timeout)
                text = (r.head + r.tail).decode("utf-8", "replace")
                out["platform"][name] = {"exit": r.exit_code, "counts": _pytest_counts(text),
                                         "complete": bool(r.complete and not r.timed_out), "duration_s": r.duration_s}
    finally:
        out["removed"] = bool(box.stop().get("removed"))
    return out


def compare_gate(host: dict, box: dict, platform_tests: list[str] | None = None) -> tuple[bool, str]:
    """QS4's comparison; or, for a parcel whose data pins tests that cannot pass on Linux,
    held when those tests are the sandbox's only difference: the host passes the gate
    and its controls; in the sandbox every check but `tests` reads as on the host; the
    suite passes there without the pinned tests, and each pinned test fails alone; and
    the sandbox's --control refused, as a failing base makes it."""
    held, detail = qs4.compare_gate(host, box)
    if held or not platform_tests:
        return held, detail
    hg, bg, bc = host["gate"]["parsed"], box["gate"], box["control"]
    p = box.get("platform") or {}
    without, alone = p.get("without") or {}, p.get("alone") or {}
    checks = set(hg["checks"]) | set(bg["parsed"]["checks"])
    differ = {k for k in checks if hg["checks"].get(k) != bg["parsed"]["checks"].get(k)}
    if not (hg["verdict"] and hg["verdict"][0] == "PASS" and host["control"]["exit"] == 0 and bg["complete"]):
        return False, detail
    if differ != {"tests"} or bg["parsed"]["checks"].get("tests") != "FAIL":
        return False, detail + "; and the sandbox differs beyond its tests"
    if not (without.get("complete") and without.get("exit") == 0 and without.get("counts", {}).get("failed", 0) == 0):
        return False, detail + "; and the suite fails in the sandbox without the pinned tests"
    if not (alone.get("complete") and alone.get("counts", {}).get("failed") == len(platform_tests)
            and not alone.get("counts", {}).get("passed")):
        return False, detail + "; and the pinned tests do not each fail alone"
    if bc["exit"] == 0 or bc["parsed"]["controls"] is not None:
        return False, detail + "; and the sandbox's controls ran where its base fails"
    return True, f"the verdicts differ only by the {len(platform_tests)} pinned platform test(s)"


# -- the local inputs ----------------------------------------------------------------------------
class LocalInputs:
    """The inputs under local/qs4h/, written by tools/qs4h_image.py, tools/qs4h_rebuild.py
    and tools/qs4h_cut.py, each checked against qs4h_expected.json whenever it is
    prepared."""

    def __init__(self, local: Path = LOCAL, *, items: dict | None = None, expected: dict | None = None,
                 image_id: Callable[[], str] | None = None):
        self.local, self.items = Path(local), items or ITEMS
        self.expected = EXPECTED if expected is None else expected
        self.image_id = image_id or (lambda: current_image_id(self.local))

    def _index(self, name: str) -> dict:
        p = self.local / name
        if not p.is_file():
            raise InputError(f"no {name} under local/qs4h: build the inputs with tools/qs4h_rebuild.py and "
                             f"tools/qs4h_cut.py")
        return qs4.load_json(p)

    def prepare(self, item_id: str) -> Prepared:
        item = item_spec(self.items, item_id)
        parcel = item["parcel"]
        p = self.items["parcels"][parcel]
        exp = self.expected
        if item_id not in (exp.get("repos") or {}) or item_id not in (exp.get("cuts") or {}):
            raise InputError(f"qs4h_expected.json pins no inputs for {item_id}")
        cuts, built = self._index("cuts.json"), self._index("built.json")
        if item_id not in cuts or item_id not in built.get("items", {}):
            raise InputError(f"{item_id} was not built")
        own = own_commit(self.items, exp, item)
        shas = parcel_shas(self.items, exp, parcel)
        # the cut
        cut_dir = self.local / cuts[item_id]["dir"]
        files = qs4.read_files(cut_dir)
        if qs4.tree_digest(files) != exp["cuts"][item_id]["digest"]:
            raise InputError("the cut's digest is not the one qs4h_expected.json pins")
        missing = [f for f in required_files(self.items, parcel) if f not in files]
        if missing or sha_problems(files, sorted({s for s in shas.values() if s != own})):
            raise InputError("the cut lacks a brief, or holds a SHA it should have mapped")
        # the repository
        b, e = built["items"][item_id], exp["repos"][item_id]
        if e["commit"] != own:
            raise InputError("qs4h_expected.json pins another commit for this item")
        repo = self.local / b["repo"]
        probs = qs4.repo_problems(repo, e["commit"], e["tree"], e["objects"],
                                  forbidden_blobs=tuple(e["forbidden_blobs"]), forbidden_names=())
        if probs:
            raise InputError("the replay repository fails its checks: " + "; ".join(probs))
        # the gate, held at this commit with the image in use
        g = b.get("gate") or {}
        if not g.get("held") or g.get("commit") != e["commit"]:
            raise InputError("the project's gate was not shown to mean the same on the host and in the sandbox "
                             "for this repository")
        image = self.image_id()
        if g.get("image_id") != image:
            raise InputError("the gate was compared with another sandbox image")
        if (g.get("platform_tests") or []) != ((p.get("platform_failures") or {}).get("tests") or []):
            raise InputError("the gate was compared under another set of pinned platform tests")
        mounts = [Mount(repo, copy_mount(parcel), f"{copy_mount(parcel)}@{own[:7]}"),
                  Mount(cut_dir, LEDGER_MOUNT, f"ledger-cut@{exp['cuts'][item_id]['digest'][:12]}")]
        sources: dict[str, dict] = {}
        facts = {"commit": own[:12], "base": p["base"][:12], "cut": exp["cuts"][item_id]["digest"][:12],
                 "image": image[:19], "dockerfile": sha256(DOCKERFILE_PATH.read_bytes())[:12], "gate_held": True}
        if "parcelround" in p["inputs"]:
            pe = exp["parcelround"]
            holder = self.local / built["parcelround"]["dir"]
            probs = qs4.repo_problems(holder / PR_DIR, pe["commit"], pe["tree"], pe["objects"], forbidden_names=())
            if probs or sorted(os.listdir(holder)) != [PR_DIR]:
                raise InputError("ParcelRound's replay repository fails its checks")
            mounts.append(Mount(holder, PR_MOUNT, f"parcelround@{pe['commit'][:7]}"))
            sources["parcelround"] = {"prefixes": [f"{RO_ROOT}/{PR_MOUNT}/{PR_DIR}/", f"<repos>/{PR_MOUNT}/{PR_DIR}/",
                                                   f"{PR_MOUNT}/{PR_DIR}/", "parcelround/"],
                                      "paths": pe["files"]}
            facts["parcelround"] = pe["tree"][:12]
        if "ds" in p["inputs"]:
            de = exp["ds"]
            ds_dir = self.local / built["ds"]["dir"]
            ds_files = qs4.read_files(ds_dir)
            if {k: sha256(v) for k, v in ds_files.items()} != de["files"]:
                raise InputError("DeepSeek's documentation copies are not the ones qs4h_expected.json pins")
            mounts.append(Mount(ds_dir, DS_MOUNT, f"ds@{de['digest'][:12]}"))
            sources["ds"] = {"prefixes": [f"{RO_ROOT}/{DS_MOUNT}/", f"<repos>/{DS_MOUNT}/", "<scratch>/ds/",
                                          f"{SCRATCH}/ds/", "ds/"], "paths": sorted(ds_files)}
            facts["ds"] = de["digest"][:12]
        if "sources" in p["inputs"]:
            se = exp["sources"]
            src_dir = self.local / built["sources"]["dir"]
            src_files = qs4.read_files(src_dir)
            if {k: sha256(v) for k, v in src_files.items()} != se["files"]:
                raise InputError("the outside sources are not the ones qs4h_expected.json pins")
            for s in self.items["sources"]:
                mounts.append(Mount(src_dir / s["name"], s["name"], f"{s['name']}@{s['commit'][:7]}"))
                sources[s["name"]] = {"prefixes": [f"{RO_ROOT}/{s['name']}/", f"<repos>/{s['name']}/",
                                                   f"{s['name']}/"], "paths": list(s["paths"])}
            facts["sources"] = se["digest"][:12]
        return Prepared(mounts=mounts, repo_files=e["files"], cut_files=sorted(files), source_files=sources,
                        facts=facts)


# -- the run -------------------------------------------------------------------------------------
def render_messages(prompt: dict, items: dict, item: dict, commit: str) -> list[dict]:
    """The system message, and the dispatch with its adaptation. A parcel's own lines of
    the adaptation are its `line-*` sections, in the order its `adaptation` list gives."""
    p = item["parcel"]
    parcel = items["parcels"][p]
    values = {"parcel": p, "repos": RO_ROOT, "scratch": SCRATCH, "commit": commit[:7], "base": parcel["base"][:7]}
    lines = [string.Template(prompt["line-" + n]).substitute(values).strip() for n in parcel["adaptation"]]
    values["extra"] = "\n".join(lines)
    fill = lambda name: string.Template(prompt[name]).substitute(values).strip()  # noqa: E731
    return [{"role": "system", "content": fill("system")},
            {"role": "user", "content": fill("dispatch") + "\n\n" + fill("adaptation")}]


def image_factory(image: str):
    def factory(scratch: Path, mounts: list, budgets: Budgets):
        return QS4hSandbox(scratch, mounts, image=image)    # run_agent gives it its lifetime at start
    return factory


# -- the score -----------------------------------------------------------------------------------
def normalise_file(raw, parcel: str, repo: list, cut: list, sources: dict) -> tuple[str, list | None]:
    """A finding's file, as one of: a file of the repository at its commit; a file of the
    cut ("ledger/<path>"); a file of another mount ("<mount>/<path>": parcelround, ds or
    an outside source); the commit message; the history; or "<unlisted>". A line number
    written into it is returned too. A path in a clone elsewhere, as under the scratch,
    is taken as the copy's file its path ends with."""
    s = str(raw).strip().strip("`'\"").replace("\\", "/").strip()
    lines = None
    m = re.search(r"(?:#L|:)(\d+)(?:-L?(\d+))?$", s)
    if m:
        lines, s = qs4.parse_lines(m.group(1) + ("-" + m.group(2) if m.group(2) else "")), s[:m.start()]
    low = s.lower()
    if "commit message" in low:
        return COMMIT_MESSAGE, lines
    if low.strip("<> ") in HISTORY_NAMES:
        return HISTORY, lines
    copy = copy_mount(parcel)
    for prefix in (f"{RO_ROOT}/{copy}/", f"<repos>/{copy}/", f"{copy}/", f"<scratch>/r1-v{parcel}/copy/",
                   f"{SCRATCH}/r1-v{parcel}/copy/", f"r1-v{parcel}/copy/"):
        if s.startswith(prefix):
            s = s[len(prefix):]
            break
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
    for name, spec in sources.items():
        for prefix in spec["prefixes"]:
            if s.startswith(prefix) and s[len(prefix):] in spec["paths"]:
                return f"{name}/{s[len(prefix):]}", lines
    if "/" in s and not s.startswith((f"{RO_ROOT}/", "<repos>/")):
        tails = [f for f in repo if ("/" + s).lower().endswith("/" + f.lower())]
        if tails:
            return max(tails, key=len), lines
    return UNLISTED, lines


def _tolerance(settings: dict, edit: dict) -> int:
    return settings["deletion_tolerance"] if edit["kind"] == "deletion" else settings["tolerance"]


def recorded_places(r: dict, kind: str, expected: dict) -> list[dict]:
    """A recorded finding's places: as its verifier cited them at the copy, or, for a
    real tip, at the real-tip build's lines, as qs4h_expected.json maps them."""
    if kind == "planted":
        return r["places"]
    mapped = (expected.get("recorded_tip_lines") or {}).get(r["id"])
    if mapped is None:
        return r["places"]
    return [{"file": pl["file"], "lines": spans} for pl, spans in zip(r["places"], mapped)]


def score_report(report: dict | None, items: dict, item: dict, expected: dict, prep: Prepared) -> tuple[dict, list]:
    """The script's score: what goes in outcome.data (no model text), and each finding's
    statement and given file for the local transcript."""
    parcel = items["parcels"][item["parcel"]]
    settings = items["settings"]
    if report is None:
        return {"reported": False, "verdict": None, "findings": [], "plants": [], "recorded": []}, []
    found, detail = [], []
    for i, f in enumerate(report.get("findings") or []):
        file, inline = normalise_file(f.get("file", ""), item["parcel"], prep.repo_files, prep.cut_files,
                                      prep.source_files)
        found.append({"file": file, "lines": qs4.parse_lines(f.get("lines")) or inline, "class": f.get("class"),
                      "located": [], "stated": [], "matched": None, "matched_by": None})
        detail.append({"index": i, "file_as_given": f.get("file"), "lines_as_given": f.get("lines"),
                       "statement": f.get("statement")})
    plants = []
    if item["kind"] == "planted":
        for pl in parcel["plants"]:
            edits = expected["plant_spans"][pl["id"]]
            located = [k for k, f in enumerate(found)
                       if any(f["file"] == e["file"] and qs4.meets(f["lines"], [e["lines"]], _tolerance(settings, e))
                              for e in edits)]
            stated = [k for k in located if qs4.markers_hit(detail[k]["statement"], pl["markers"])]
            for k in located:
                found[k]["located"].append(pl["id"])
            for k in stated:
                found[k]["stated"].append(pl["id"])
                if found[k]["matched"] is None:
                    found[k].update(matched=pl["id"], matched_by="screen")
            plants.append({"id": pl["id"], "edits": len(edits), "located": bool(located), "stated": bool(stated),
                           "caught": bool(stated)})
    recorded = []
    for r in parcel["recorded"]:
        if r["copy_only"] and item["kind"] == "real":
            continue
        places = recorded_places(r, item["kind"], expected)
        hit = False
        for f in found:
            for pl in places:
                if f["file"] != pl["file"]:
                    continue
                spans = pl["lines"]
                by = ("lines" if spans and qs4.meets(f["lines"], spans, settings["tolerance"])
                      else "file" if not spans else None)
                if by:
                    hit = True
                    if f["matched"] is None:
                        f.update(matched=r["id"], matched_by=by)
                    break
        recorded.append({"id": r["id"], "class": r["class"], "in_view": r["in_view"], "located": hit})
    return {"reported": True, "verdict": report.get("verdict"), "findings": found, "plants": plants,
            "recorded": recorded}, detail


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
            "recorded_in_view": sum(1 for r in sc["recorded"] if r["in_view"]),
            "recorded_in_view_located": sum(1 for r in sc["recorded"] if r["in_view"] and r["located"])}


# -- the suite -----------------------------------------------------------------------------------
class QS4H(Suite):
    """One QS4h item, run as this round's verifier of its parcel. Each subclass names one
    item, so tools/live.py builds it with no arguments and its run is one batch. Building
    it checks the item's inputs, so a missing or changed input is refused before any
    spend."""

    ITEM = ""
    caps = Caps(**ITEMS["caps"])
    version = VERSION

    def __init__(self, *, inputs=None, sandbox_factory: Callable | None = None, items: dict | None = None,
                 expected: dict | None = None, prompt: dict | None = None, run_dir: Path | None = None,
                 stream: bool | None = None, local: Path | None = None):
        if not self.ITEM:
            raise TypeError("QS4h is run through one of its item classes, such as QS4hH3Planted")
        self.spec = items or ITEMS
        self.expected = EXPECTED if expected is None else expected
        self.prompt = prompt or PROMPT
        self.item = item_spec(self.spec, self.ITEM)
        needed = list(PROMPT_SECTIONS) + ["line-" + n for n in self.spec["parcels"][self.item["parcel"]]["adaptation"]]
        missing = [s for s in needed if s not in self.prompt]
        if missing:
            raise InputError(f"qs4h_prompt.md lacks the sections {missing}")
        self.inputs = inputs if inputs is not None else LocalInputs(local or LOCAL, items=self.spec,
                                                                    expected=self.expected)
        self.inputs.prepare(self.ITEM)                   # refuse before any spend
        self.sandbox_factory = sandbox_factory
        self.run_dir = Path(run_dir) if run_dir else Path(local or LOCAL) / "runs"
        self.budgets = Budgets(**self.spec["budgets"])
        self.stream = self.spec["settings"]["stream"] if stream is None else stream

    def items(self) -> list[Item]:
        return [Item(self.item["id"], {"parcel": self.item["parcel"], "kind": self.item["kind"]})]

    def _data(self, **kw) -> dict:
        return {"format": 1, "item": self.item["id"], "parcel": self.item["parcel"], "kind": self.item["kind"],
                **kw}

    def run_item(self, ctx, item: Item) -> ItemResult:
        parcel = self.item["parcel"]
        try:
            prep = self.inputs.prepare(item.id)          # again, immediately before mounting
            commit = own_commit(self.spec, self.expected, self.item)
            factory = self.sandbox_factory or image_factory(self.inputs.image_id())
        except InputError as e:
            return ItemResult("error", f"an input failed its checks, so nothing was mounted and no call was "
                                       f"made: {e}", {"qs4h": self._data(status_basis="input")})
        scratch = self.run_dir / secrets.token_hex(6)
        (scratch / f"r1-v{parcel}").mkdir(parents=True)
        box = factory(scratch, prep.mounts, self.budgets)
        res = run_agent(ctx, messages=render_messages(self.prompt, self.spec, self.item, commit),
                        tools=qs4.qs4_tools(self.budgets, self.prompt), sandbox=box, budgets=self.budgets,
                        stream=self.stream)
        ledger = qs4.read_back(box, f"{SCRATCH}/verifier-{parcel}.md", self.spec["settings"]["ledger_file_cap"])
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
                        f"{qs4._n(c['findings'], 'finding')}; the lead's judgement is the score of record")
            return "pass", (f"reported: {qs4._n(c['findings'], 'finding')}, for the lead to adjudicate against "
                            f"this round's recorded findings")

        result = res.item_result(judge)
        basis = ("agent" if res.outcome in ("stopped", "error") else
                 "screen" if kind == "planted" and report is not None else "reported")
        # A stopped or errored run never reported, so its score is empty: nothing of a
        # run that did not finish is scored as "found nothing".
        result.data["qs4h"] = self._data(
            inputs=prep.facts, **sc, counts=c if report is not None else None,
            escalations=res.tool_calls.get("escalate", 0),
            ledger_file={"kind": ledger["kind"], "bytes": ledger["bytes"]}, status_basis=basis)
        result.local["qs4h"] = {"report": res.report, "ledger_file": ledger, "findings": detail,
                                "scored": res.outcome == "reported"}
        return result


def _suite(item_id: str) -> type:
    name = "QS4h" + "".join(part.capitalize() for part in item_id.split("-"))
    return type(name, (QS4H,), {"ITEM": item_id, "name": f"qs4h-{item_id}", "__module__": __name__,
                                "__doc__": f"QS4h's item {item_id}: one run, one batch."})


QS4hH1Planted = _suite("h1-planted")
QS4hH1Real = _suite("h1-real")
QS4hH2Planted = _suite("h2-planted")
QS4hH2Real = _suite("h2-real")
QS4hH3Planted = _suite("h3-planted")
QS4hH3Real = _suite("h3-real")
QS4hH4Planted = _suite("h4-planted")
QS4hH4Real = _suite("h4-real")
SUITES = [QS4hH1Planted, QS4hH1Real, QS4hH2Planted, QS4hH2Real, QS4hH3Planted, QS4hH3Real, QS4hH4Planted,
          QS4hH4Real]


# -- the table and the judgements --------------------------------------------------------------------
PLANT_VERDICTS = qs4.PLANT_VERDICTS
FINDING_VERDICTS = qs4.FINDING_VERDICTS
JUDGEMENT_KEYS = {"record_id", "plant", "finding", "verdict", "recorded", "by", "checked_by", "note"}


def load_judgements(path: Path = JUDGEMENTS_PATH) -> list[dict]:
    return qs4.load_json(path)["judgements"]


def judgement_problems(judgements: list[dict], items: dict = ITEMS) -> list[str]:
    """What is wrong with the lead's judgements' form: each judges either a plant (caught
    or missed) or a finding by its index (a match to a named recorded finding, new and
    true, or a false alarm), and names who judged and who checked."""
    plants = {pl["id"] for p in items["parcels"].values() for pl in p["plants"]}
    recorded = {r["id"] for p in items["parcels"].values() for r in p["recorded"]}
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
                                           or (j["verdict"] == "match") != (j["recorded"] in recorded)):
            probs.append(f"{k}: a finding's verdict not in {FINDING_VERDICTS}, or a match without its recorded id")
        if not (isinstance(j["record_id"], str) and j["by"] and j["checked_by"]):
            probs.append(f"{k}: no record, judge or checker named")
    return probs


def table(records: list[dict], judgements: list[dict] | None = None) -> dict:
    """QS4h's results by run: the status, the plants caught by the screen and, once every
    plant of the run is judged, by judgement; the findings, and the recorded findings in
    view located; tokens and cost. Planted runs are pooled by parcel."""
    judged = {}
    for j in judgements or []:
        if j.get("plant"):
            judged[(j["record_id"], j["plant"])] = j["verdict"] == "caught"
    rows = {}
    for r in records:
        q = (r.get("outcome", {}).get("data") or {}).get("qs4h")
        if not q:
            continue
        c = q.get("counts") or {}
        plants = [p["id"] for p in q.get("plants", [])]
        verdicts = [judged[(r["record_id"], p)] for p in plants if (r["record_id"], p) in judged]
        rows[r["record_id"]] = {
            "item": q["item"], "parcel": q["parcel"], "kind": q["kind"], "status": r["outcome"]["status"],
            "verdict": q.get("verdict"), "plants_caught_screen": c.get("plants_caught"),
            "plants_caught_judged": sum(verdicts) if plants and len(verdicts) == len(plants) else None,
            "findings": c.get("findings"), "unmatched": c.get("unmatched"),
            "recorded_in_view_located": c.get("recorded_in_view_located"),
            "recorded_in_view": c.get("recorded_in_view"),
            "read": r["usage"]["cache_hit"] + r["usage"]["cache_miss"], "cache_hit": r["usage"]["cache_hit"],
            "output": r["usage"]["output"], "cost_usd": r["cost_usd"], "calls": r["calls"]}
    by_parcel = {}
    for x in rows.values():
        if x["kind"] == "planted":
            t = by_parcel.setdefault(x["parcel"], {"runs": 0, "plants_caught_screen": 0})
            t["runs"] += 1
            t["plants_caught_screen"] += x["plants_caught_screen"] or 0
    return {"rows": rows, "planted_by_parcel": by_parcel}
