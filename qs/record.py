"""The run record: one JSON line per item run, held to a schema.

Every number a table shows comes from these lines, and every line names the
stack that produced it: provider, model sent, every distinct model and
fingerprint the responses reported, thinking setting, sampling sent and what
the API ignores, the suite's caps, and the price table and rate period behind
its cost ("mixed" when a run's calls fell in more than one). A transcript is
kept locally (gitignored) and only its hash is published.

From version 2 a line also names its code: the commit the batch ran from,
whether the checkout differed from it outside records/, and a digest of the
tools as the run's requests sent them. harness_version is a constant, so
before version 2 a change of code moved nothing in the record (HonestHarness
round 1's ledger, 11:37:12). Limits, each stated by the behaviour it concedes:
- the commit and the flag are read once, as the batch starts, so a change
  made during a batch is not seen;
- the flag says that something differed, not what. It counts every tracked
  change and every untracked file git does not ignore, outside records/:
  notes and tests as much as code. A file git ignores is not seen;
- both are None where the code's directory is not the top of a git checkout
  (one inside another repository included), or git does not answer;
- the digest covers the tools as declared to the model. A change to what a
  tool does under the same declaration moves the commit and the flag only.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import jsonschema

from . import __version__

SCHEMA_PATH = Path(__file__).parent / "schema" / "run_record.schema.json"
RECORD_VERSION = 2
CODE_ROOT = Path(__file__).resolve().parent.parent   # the checkout this package runs from
_SCHEMA = None


def schema() -> dict:
    global _SCHEMA
    if _SCHEMA is None:
        _SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return _SCHEMA


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new_record(**fields) -> dict:
    rec = {"record_version": RECORD_VERSION, "ts_utc": now_utc(),
           "harness_version": __version__}
    rec.update(fields)
    return rec


def validate(record: dict) -> None:
    jsonschema.validate(record, schema())


def append(path: str | Path, record: dict) -> None:
    validate(record)
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


COMMIT_PATTERN = re.compile(r"[0-9a-f]{40}(?:[0-9a-f]{24})?")


def _same_dir(a: str | Path, b: str | Path) -> bool:
    return os.path.normcase(os.path.realpath(a)) == os.path.normcase(os.path.realpath(b))


def code_identity(root: str | Path = CODE_ROOT) -> dict:
    """The code a batch runs from: HEAD's commit, and whether the checkout
    differs from it outside records/, by a tracked change or an untracked file
    git does not ignore. Both None where root is not the top of a git checkout,
    or git does not answer. Git takes no optional lock, lists untracked files
    whatever its config says, and its output is read as bytes."""
    git = ["git", "--no-optional-locks", "-C", str(root)]

    def out(*args: str) -> bytes:
        return subprocess.run(git + list(args), capture_output=True, timeout=60, check=True).stdout

    try:
        top = out("rev-parse", "--show-toplevel").decode("utf-8", "replace").strip()
        head = out("rev-parse", "HEAD").decode("ascii", "replace").strip()
        status = out("status", "--porcelain", "--untracked-files=normal", "--", ".", ":(exclude)records")
    except (OSError, subprocess.SubprocessError):
        return {"commit": None, "changed": None}
    if not COMMIT_PATTERN.fullmatch(head) or not _same_dir(top, root):
        return {"commit": None, "changed": None}
    return {"commit": head, "changed": bool(status.strip())}


def check_code(code: dict) -> None:
    """Refuse, before a batch spends, a code identity its records could not
    hold (the schema's "code", with the run's digest still to come)."""
    jsonschema.validate(dict(code, tools_sha256=None), schema()["properties"]["code"])


def tools_digest(calls: list[dict]) -> str | None:
    """SHA-256 of the distinct tool lists a run's requests carried, each in
    canonical form, sorted and joined by newlines; None when none carried one."""
    seen = sorted({canonical(c["request"]["tools"]) for c in calls
                   if isinstance(c.get("request"), dict) and c["request"].get("tools") is not None})
    return hashlib.sha256("\n".join(seen).encode("utf-8")).hexdigest() if seen else None


def save_transcript(directory: str | Path, record_id: str, transcript, redact=None) -> str:
    """Write a transcript locally, after redaction, and return its SHA-256."""
    text = canonical(transcript)
    if redact is not None:
        text = redact(text)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    d = Path(directory)
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{record_id}.json").write_text(text, encoding="utf-8", newline="\n")
    return digest
