"""The run record: one JSON line per item run, held to a schema.

Every number a table shows comes from these lines, and every line names the
stack that produced it: provider, model sent and reported, fingerprint,
thinking setting, sampling sent and what the API ignores, the price table and
rate period behind its cost. A transcript is kept locally (gitignored) and
only its hash is published.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import jsonschema

from . import __version__

SCHEMA_PATH = Path(__file__).parent / "schema" / "run_record.schema.json"
RECORD_VERSION = 1
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
