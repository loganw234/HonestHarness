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
round 1's harness note 43). Limits: the commit and the flag are read once, as
the batch starts, so a change made during a batch is not seen; the flag says
that something differed, not what; and they are None where the code is not in
a git checkout, or git does not answer.
"""
from __future__ import annotations

import hashlib
import json
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


def code_identity(root: str | Path = CODE_ROOT) -> dict:
    """The code a batch runs from: HEAD's commit, and whether any file outside
    records/ differs from it, untracked files included. Both None where root is
    not a git checkout or git does not answer. Git takes no optional lock."""
    git = ["git", "--no-optional-locks", "-C", str(root)]
    try:
        head = subprocess.run(git + ["rev-parse", "HEAD"], capture_output=True, text=True,
                              timeout=60, check=True).stdout.strip()
        status = subprocess.run(git + ["status", "--porcelain", "--", ".", ":(exclude)records"],
                                capture_output=True, text=True, timeout=60, check=True).stdout
    except (OSError, subprocess.SubprocessError):
        return {"commit": None, "changed": None}
    return {"commit": head, "changed": bool(status.strip())}


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
