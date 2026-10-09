"""QS6, a slice: questions put to ParcelRound round 6's ledger alone, at five
lengths, each answer scored by script.

It measures reading, which is narrower than REQ's QS6, where a candidate drafts
a whole record entry (REQ section 8.2). The plan of record's section 6, "Wave
2", "P3", is the authority; the design is in the round's ledger, P3.md
2026-10-06 15:21:02, as the lead accepted it at lead.md 15:25:54.

The lead runs one batch per cut and thinking setting, smallest cut first:

    python tools/qs6_extract.py --parcelround <repos>/parcelround-worktrees/P0
    python tools/qs6_key.py --check
    python tools/live.py qs.suites.qs6:QS6C016K --repeats 3 --thinking off
    python tools/live.py qs.suites.qs6:QS6C016K --repeats 3 --thinking on --effort high
    ... then QS6C032K, QS6C064K, QS6C128K and QS6Whole the same way.

The source
- ParcelRound's archive/round6-ledger.zip at f42242e, read from a local,
  gitignored copy, local/qs6/round6-ledger.zip, which tools/qs6_extract.py puts
  in place. qs6_source.json, beside this file, holds its SHA-256 and each
  member's, and nothing of its text. Members under keys/ are never read.
- The zip keeps each member's modification time as a DOS time, with no zone.
  They are read as -07:00, the zone of every stamp in the ledger: each stamped
  file's kept time equals its own last stamp, to the zip's two-second
  resolution (qs6_source.json records each difference).

The cuts
- The ledger as of a cut time T is every entry stamped at or before T, from
  every file, and every unstamped file (the README, a brief) whose kept time is
  at or before T, in time order; ties go by file name, then by place in the
  file. A file's lines before its first stamped heading go with that entry.
- A cut is rendered as one text: each unit headed by a line naming its file,
  "=== lead.md ===" or "=== README.md (a whole file) ===", line endings LF.
- Five cuts, chosen by the plan's own measure, UTF-8 bytes / 4: the last time
  at which the rendered text is at or under 16,000, 32,000, 64,000 and 128,000,
  and the whole ledger. qs6_cuts.json holds each cut's time, its measures, the
  SHA-256 of its text and its caps. The API's prompt tokens measure each cut at
  run time, in the record's usage and in outcome.data.prompt_tokens.
- Each cut is its own suite class, so its own batch: QS6C016K, QS6C032K,
  QS6C064K, QS6C128K and QS6Whole, named qs6-c016k and so on.

A run: one call, Context.chat([system, user]), unstreamed, with no tools and no
sampling parameter. The user message is the cut, then the question, then a
reminder of the answer form, so every request of a batch shares the system
text and the cut as its prefix (D11's long-text example, ds/kv_cache.txt:
33-46). The prompt's text is in qs6_items.json.

The key, and refusal before any call
- The items, with the ledger file and line that holds each answer, are in
  qs6_items.json. The key, an answer or "not in the input" for each item at
  each cut, is not in the repository until the runs are scored. It is read from
  local/qs6/qs6_key.json, and qs6_items.json holds its SHA-256.
- A suite class refuses, before any call and so before any spend, when the
  local copy is missing or its hash or a member's differs, when its rendered
  cut's hash differs from qs6_cuts.json's, or when the key is missing, its hash
  differs, or it lacks an entry for an item at this cut. The key's own record
  of the cut and source hashes it was built from is checked by
  tools/qs6_key.py --check, not by the suite, so that check is run before each
  batch (restated at P3's merge, verifier-P3's F3).

The score, by script, on the answer field of content alone
- The answer field is the last line of content that reads "ANSWER: <value>"
  and holds a value; case, bold, a list marker and backticks are allowed.
  reasoning_content is never read.
- "not in the input" is that phrase or one of NIL_PHRASES, alone or followed
  by punctuation and more.
- Each type's normal form, from the first value of the type in the answer:
  - sha and hex: a hex token of 7 digits or more, lower-cased. Exact when one of
    it and the key is a prefix of the other, at MIN_HEX[type] digits or more;
  - time: HH:MM:SS. A time without seconds is wrong, flagged;
  - count: the first integer, or a number word up to ninety-nine, never the
    digits of a name such as verifier-P0 or 49a9266;
  - figure: a number, an optional magnitude (k, K, thousand, M, million, B,
    billion) and a unit, compared exactly as a decimal;
  - file: a member's name, case folded, with ".md" and a leading
    "parcelround-r6-ledger/" optional. A name ending ".md" that is no member is
    "unlisted".
- The classes:
  - exact: the normal form equals the key, or "not in the input" where the key
    is;
  - overclaim: a value of the item's type where the key is "not in the input";
  - dropped_unit: a figure whose value, or the key's written significand,
    matches, with no unit;
  - wrong: any other value of the type, a unit not the key's, or "not in the
    input" where the key holds a value (flagged nil_answer);
  - no_answer: no answer field, or one holding no value of the type and no
    "not in the input".

The statuses
- pass: exact. fail: wrong, overclaim, dropped_unit or no_answer.
- stopped: a RunStopped (CapReached, PeakReached, BatchStopping), or a
  `length` finish whose output reached the max_tokens the harness sent.
- error, never the model's: a provider condition (content_filter,
  insufficient_system_resource, aborted; D10), a `length` finish below the
  request's max_tokens, any other finish than stop, a ProviderError, or a reply
  that never arrived whole. A status the next request would meet too stops the
  batch through ctx.stop_reason. refused and skipped are not used: no QS6
  request is documented as refused.

outcome.data holds no model text: only the suite's own words, enums, numbers
and closed forms. Its answer is a normal form (hex, HH:MM:SS, an integer, a
decimal with a unit from the item's list or a closed word, a member's name or
"unlisted", "not in the input") or null. The model's raw answer line goes in
ItemResult.local, which stays in the local transcript; the transcript holds the
whole reply too. Details are in the suite's own words.

Caps, per cut class: Caps(MAX_PROMPT_TOKENS = 1, MAX_OUTPUT_TOKENS = 32,000,
max_call_prompt_tokens from qs6_cuts.json). With max_prompt_tokens 1 a run
makes one call, the one that crosses it; a second would meet CapReached.
max_call_prompt_tokens is P0's estimate of the cut's largest request (its
longest question) plus 2%, rounded up to a thousand. tests/test_qs6.py holds
each batch's reservation at 3 repeats against a hand computation.

Limits, each stated by the behaviour it concedes:
1. Free text beyond the answer field is not scored. An answer given anywhere
   but an answer line scores no_answer.
2. Only content is scored. An answer in reasoning_content alone scores
   no_answer.
3. The first value of the item's type is scored. An answer that lists several
   is scored by its first; flags.values_in_answer counts them.
4. "Not in the input" is known by NIL_PHRASES. A refusal in other words scores
   no_answer, or is read as a value if it holds one.
5. A figure in a unit outside the item's list scores wrong, even when it would
   convert to the key, as milliseconds would against a key in seconds.
6. A time is compared by HH:MM:SS; a date beside it is not checked.
7. A SHA is exact when one of it and the key is a prefix of the other. Digits
   beyond those the ledger gives cannot be checked.
8. In a checkout without the local copy, the gate's tests hold the scorer and
   the cut builder on synthetic data only. The real key's 100%, the real cut
   hashes and the evidence lines are held by tools/qs6_key.py --check,
   tools/qs6_extract.py --cuts, and tests that skip without the local copy.
9. The kept times are read as -07:00, which the zip cannot state; the stamped
   files' kept times are the evidence.
10. Sizes before a run are estimates by bytes / 4; the API's prompt tokens are
    recorded. P0's estimate is about twice the real count for this text, but
    the output cap is priced exactly, so by DeepSeek's own 0.3 tokens a
    character a run's reservation is about 1.1 to 1.4 times its real worst
    case (restated at P3's merge, verifier-P3's F4).
11. No sampling parameter is sent, so non-thinking mode samples at the API's
    default temperature, 1 (D10), and repeats vary as that makes them.
12. Cache hits are best-effort (D11): a batch's cost is bounded by its
    reservation, not by any estimate.
13. Round 6's ledger was published on 2026-10-03. Both DeepSeek models predate
    it by release date (plan section 4), unless upgraded in place since.
14. Each run's transcript holds its whole cut: about 198 MB of requests over the
    ten batches, local and gitignored.
15. A reply whose reasoning passes MAX_OUTPUT_TOKENS stops the run as stopped,
    never fail: it is not scored.
"""
from __future__ import annotations

import hashlib
import io
import json
import re
import statistics
import zipfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

from ..client import ProviderError
from ..record import canonical
from ..suite import ID_PATTERN, Caps, Item, ItemResult, RunStopped, Suite, estimate_tokens

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SOURCE_PATH = HERE / "qs6_source.json"
CUTS_PATH = HERE / "qs6_cuts.json"
ITEMS_PATH = HERE / "qs6_items.json"
LOCAL_DIR = ROOT / "local" / "qs6"
ARCHIVE_PATH = LOCAL_DIR / "round6-ledger.zip"
KEY_PATH = LOCAL_DIR / "qs6_key.json"

CUT_NAMES = ("c016k", "c032k", "c064k", "c128k", "whole")
TARGETS = {"c016k": 16_000, "c032k": 32_000, "c064k": 64_000, "c128k": 128_000}
TYPES = frozenset({"sha", "hex", "time", "count", "figure", "file"})
SETS = frozenset({"length", "reach"})
CLASSES = ("exact", "wrong", "overclaim", "dropped_unit", "no_answer")
NIL = "not in the input"
NIL_PHRASES = ("not in the input", "not in input", "not in the ledger", "not in the text",
               "not stated", "not given", "unknown", "cannot be determined")
MIN_HEX = {"sha": 7, "hex": 8}
PROVIDER_CONDITIONS = frozenset({"content_filter", "insufficient_system_resource", "aborted"})
MAX_PROMPT_TOKENS = 1          # one call per run: its only call is the one that crosses it
MAX_OUTPUT_TOKENS = 32_000
CAP_MARGIN_PERCENT = 2         # max_call_prompt_tokens = estimate + 2%, rounded up to 1,000
ERROR_BODY = 200               # characters of a provider's error body kept, as QS1 keeps them
FILE_PREFIXES = ("parcelround-r6-ledger/", "ledger/", "./")
# Units a figure may be given in. A unit outside an item's own list, but in
# this one, is a unit other than the key's; any other word after a number is no
# unit at all.
KNOWN_UNITS = ("%", "percent", "per cent", "tokens", "token", "subagent tokens",
               "subagent token", "seconds", "second", "secs", "sec", "s", "milliseconds",
               "millisecond", "ms", "minutes", "minute", "mins", "min", "hours", "hour", "hrs",
               "hr", "h", "days", "day", "bytes", "byte", "kb", "mb", "gb", "lines", "line",
               "characters", "chars", "words", "rows", "row", "calls", "usd", "dollars", "$")
MAGNITUDES = {"thousand": 1_000, "k": 1_000, "million": 1_000_000, "m": 1_000_000,
              "billion": 1_000_000_000, "b": 1_000_000_000}


class SourceError(Exception):
    """A local input that is missing, or whose hash is not the committed one.
    It is raised before any call, so a batch refused for it spends nothing."""


# -- hashes and data -----------------------------------------------------------------
def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def _normalised(path: Path) -> bytes:
    """A committed file's bytes, unchanged by a checkout's line endings."""
    return Path(path).read_bytes().replace(b"\r\n", b"\n")


def load_json(path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_data(source=SOURCE_PATH, cuts=CUTS_PATH, items=ITEMS_PATH) -> dict:
    return {"source": load_json(source), "cuts": load_json(cuts), "items": load_json(items)}


def version_of(paths, code: Path) -> str:
    """"1.", 12 hex digits of the data files' hash, ".", 12 of this file's: so a
    record names the exact source, cuts, prompt, items, key hash and scorer."""
    h = hashlib.sha256()
    for p in paths:
        h.update(_normalised(p))
        h.update(b"\0")
    return f"1.{h.hexdigest()[:12]}.{sha256_bytes(_normalised(code))[:12]}"


def check_data(data: dict) -> None:
    """The committed data's own consistency, without the local copy. Raises
    ValueError naming what is wrong."""
    source, cuts, items = data["source"], data["cuts"], data["items"]
    names = {m["name"] for m in source["members"]}
    if not re.fullmatch(r"[0-9a-f]{64}", source.get("sha256", "")):
        raise ValueError("qs6_source.json: the archive's sha256 is not 64 hex digits")
    for m in source["members"]:
        if m["name"].startswith("keys/") or not re.fullmatch(r"[0-9a-f]{64}", m["sha256"]):
            raise ValueError(f"qs6_source.json: member {m['name']!r} is malformed")
    specs = cuts["cuts"]
    if [c["name"] for c in specs] != list(CUT_NAMES):
        raise ValueError(f"qs6_cuts.json: the cuts must be {list(CUT_NAMES)}, in order")
    times = [datetime.fromisoformat(c["time"]) for c in specs]
    if any(a >= b for a, b in zip(times, times[1:])):
        raise ValueError("qs6_cuts.json: cut times must increase")
    for c in specs:
        caps = c["caps"]
        if (caps["max_prompt_tokens"] != MAX_PROMPT_TOKENS
                or caps["max_output_tokens"] != MAX_OUTPUT_TOKENS
                or caps["max_call_prompt_tokens"] != cap_for(c["p0_largest_request"])):
            raise ValueError(f"qs6_cuts.json: cut {c['name']}'s caps are not the rule's")
        if not re.fullmatch(r"[0-9a-f]{64}", c["sha256"]):
            raise ValueError(f"qs6_cuts.json: cut {c['name']}'s sha256 is malformed")
    if not re.fullmatch(r"[0-9a-f]{64}", items.get("key_sha256", "")):
        raise ValueError("qs6_items.json: key_sha256 is not 64 hex digits")
    seen = set()
    for it in items["items"]:
        iid = it["id"]
        if not ID_PATTERN.fullmatch(iid) or iid in seen:
            raise ValueError(f"qs6_items.json: item id {iid!r} is not a valid, unique id")
        seen.add(iid)
        if it["type"] not in TYPES or it["set"] not in SETS or not it["question"].strip():
            raise ValueError(f"qs6_items.json: item {iid} has a bad type, set or question")
        if it["type"] == "figure" and not it.get("units"):
            raise ValueError(f"qs6_items.json: figure item {iid} names no units")
        if not it.get("evidence"):
            raise ValueError(f"qs6_items.json: item {iid} cites no evidence")
        for cite in it["evidence"]:
            f, _, n = cite.rpartition(":")
            if f not in names or not n.isdigit() or int(n) < 1:
                raise ValueError(f"qs6_items.json: item {iid} cites {cite!r}, not a member's line")


def cap_for(estimate: int) -> int:
    """max_call_prompt_tokens for a cut whose largest request P0 estimates at
    `estimate`: the estimate plus CAP_MARGIN_PERCENT, rounded up to a thousand."""
    need = (estimate * (100 + CAP_MARGIN_PERCENT) + 99) // 100
    return (need + 999) // 1000 * 1000


# -- the archive and the cuts ----------------------------------------------------------------
STAMP = re.compile(r"^## (\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}) ([+-])(\d{2})(\d{2}) - ", re.M)


@dataclass(frozen=True)
class Unit:
    t: datetime        # an entry's stamp, or a whole file's kept time
    file: str          # the member's name below the archive's top directory
    kind: str          # "entry" or "file"
    n: int             # an entry's place in its file, from 1; 0 for a whole file
    text: str


def kept_zone(source: dict) -> timezone:
    sign, hh, mm = re.fullmatch(r"([+-])(\d{2}):(\d{2})", source["kept_time_zone"]).groups()
    delta = timedelta(hours=int(hh), minutes=int(mm))
    return timezone(-delta if sign == "-" else delta)


def read_archive(data: bytes, source: dict) -> dict[str, tuple[str, datetime]]:
    """Check the archive against its source spec, and return its members outside
    keys/ as name -> (text with LF line endings, kept time). A member under keys/
    is named in the spec and never read."""
    if len(data) != source["bytes"] or sha256_bytes(data) != source["sha256"]:
        raise SourceError("the archive's size or SHA-256 is not the one qs6_source.json records")
    zone = kept_zone(source)
    expected = {m["name"]: m for m in source["members"]}
    excluded = set(source["excluded"])
    top = source["top"]
    out: dict[str, tuple[str, datetime]] = {}
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            if not info.filename.startswith(top):
                raise SourceError("the archive holds a member outside its top directory")
            name = info.filename[len(top):]
            if name.startswith("keys/"):
                if name not in excluded:
                    raise SourceError("the archive holds a keys/ member qs6_source.json does not name")
                continue
            spec = expected.get(name)
            if spec is None:
                raise SourceError(f"the archive holds a member qs6_source.json does not list: {name}")
            raw = z.read(info)
            kept = datetime(*info.date_time, tzinfo=zone)
            if sha256_bytes(raw) != spec["sha256"] or kept.isoformat() != spec["kept"]:
                raise SourceError(f"member {name} is not the one qs6_source.json records")
            out[name] = (raw.decode("utf-8").replace("\r\n", "\n"), kept)
    missing = sorted(set(expected) - set(out))
    if missing:
        raise SourceError(f"the archive lacks members qs6_source.json lists: {missing}")
    return out


def split_units(name: str, text: str, kept: datetime) -> list[Unit]:
    """A stamped file's entries, each from its stamped heading to the next; the
    lines before the first heading go with the first. An unstamped file is one
    unit, at its kept time."""
    marks = list(STAMP.finditer(text))
    if not marks:
        return [Unit(kept, name, "file", 0, text)]
    out = []
    for k, m in enumerate(marks):
        start = 0 if k == 0 else m.start()
        end = marks[k + 1].start() if k + 1 < len(marks) else len(text)
        delta = timedelta(hours=int(m.group(4)), minutes=int(m.group(5)))
        zone = timezone(-delta if m.group(3) == "-" else delta)
        t = datetime.fromisoformat(f"{m.group(1)}T{m.group(2)}").replace(tzinfo=zone)
        out.append(Unit(t, name, "entry", k + 1, text[start:end]))
    return out


def timeline(members: dict[str, tuple[str, datetime]]) -> list[Unit]:
    units = [u for name, (text, kept) in members.items() for u in split_units(name, text, kept)]
    units.sort(key=lambda u: (u.t, u.file, u.n))
    return units


def render_unit(u: Unit) -> str:
    head = f"=== {u.file} (a whole file) ===" if u.kind == "file" else f"=== {u.file} ==="
    return head + "\n" + u.text.strip("\n") + "\n\n"


def cut_units(units: list[Unit], t: datetime) -> list[Unit]:
    return [u for u in units if u.t <= t]


def cut_text(units: list[Unit], t: datetime) -> str:
    return "".join(render_unit(u) for u in cut_units(units, t))


def measures(text: str) -> dict:
    n = len(text)
    b = len(text.encode("utf-8"))
    return {"chars": n, "bytes": b, "bytes_over_4": b // 4, "deepseek_ratio": (3 * n + 5) // 10}


def choose_cut_times(units: list[Unit]) -> dict[str, datetime]:
    """Each target's cut time: the latest time at which the cut's rendered text
    is at or under the target by bytes / 4. All units at one time enter
    together, so a cut never splits a time. "whole" is the last unit's time."""
    sizes, total, ends = [], 0, {}
    for u in units:
        total += len(render_unit(u).encode("utf-8"))
        sizes.append(total)
        ends[u.t] = total       # the cut at time t ends after the last unit at t
    out = {}
    for name, target in TARGETS.items():
        fit = [t for t, size in ends.items() if size // 4 <= target]
        if not fit:
            raise ValueError(f"no cut of the ledger fits {target}")
        out[name] = max(fit)
    out["whole"] = units[-1].t
    return out


# -- the prompt --------------------------------------------------------------------------------
def request_messages(prompt: dict, text: str, question: str) -> list[dict]:
    user = (prompt["before_ledger"] + text + prompt["after_ledger"] + question
            + prompt["after_question"])
    return [{"role": "system", "content": prompt["system"]}, {"role": "user", "content": user}]


def request_estimate(prompt: dict, text: str, question: str) -> int:
    """P0's estimate of the request, as Context.chat makes it (qs/suite.py)."""
    return estimate_tokens(canonical({"m": request_messages(prompt, text, question), "t": None}))


def largest_request(prompt: dict, text: str, questions) -> int:
    return max(request_estimate(prompt, text, q) for q in questions)


# -- the answer field ----------------------------------------------------------------------------
ANSWER_LINE = re.compile(r"^[\s>*#_`\-]*answer[\s*_`]*:[\s*_`]*(.*?)[\s*_`]*$", re.IGNORECASE)
_STRIP = " \t\"'`*“”‘’"


def _clean(value: str) -> str:
    v = value.strip(_STRIP)
    v = v.rstrip(".;,").strip(_STRIP)
    return re.sub(r"\s+", " ", v)


def answer_field(content) -> tuple[str | None, str | None, int]:
    """(value, raw line, answer lines found): the last answer line that holds a
    value. reasoning_content is never passed here."""
    if not isinstance(content, str):
        return None, None, 0
    found = [(m.group(1), line) for line in content.splitlines()
             if (m := ANSWER_LINE.match(line))]
    for value, raw in reversed(found):
        v = _clean(value)
        if v:
            return v, raw, len(found)
    return None, None, len(found)


def nil_match(value: str) -> tuple[bool, bool]:
    """(is "not in the input", with more after it)."""
    v = value.casefold()
    for p in NIL_PHRASES:
        if v == p:
            return True, False
        if v.startswith(p) and not v[len(p)].isalnum():
            return True, True
    return False, False


# -- the types' normal forms ----------------------------------------------------------------------
HEX_TOKEN = re.compile(r"(?<![0-9A-Za-z])([0-9a-fA-F]{7,64})(?![0-9A-Za-z])")
TIME_TOKEN = re.compile(r"(?<![\d:])(\d{1,2}):(\d{2})(?::(\d{2}))?(?![\d:])")
# A number is not read out of a name, a decimal, a time or a digit group: no
# letter, digit, ".", ":" or "," before it (so not the 0 of "verifier-P0"), and
# no digit, ":", or "." or "," with a digit after it. A count takes no letter
# after it either (not the 49 of "49a9266"); a figure may, its unit ("6.0s").
INT_TOKEN = re.compile(r"(?<![\w.:,])(\d{1,3}(?:,\d{3})+|\d+)(?![\w:]|[.,]\d)")
NUM_TOKEN = re.compile(r"(?<![\w.:,])(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?(?![\d:]|[.,]\d)")
_ONES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
         "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen",
         "eighteen", "nineteen"]
_TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
         "eighty": 80, "ninety": 90}
WORD_TOKEN = re.compile(r"\b(?:(" + "|".join(_TENS) + r")(?:[- ](" + "|".join(_ONES[1:10])
                        + r"))?|(" + "|".join(_ONES) + r"))\b", re.IGNORECASE)


def _hexes(value: str, spec: dict, members) -> list:
    return [m.group(1).lower() for m in HEX_TOKEN.finditer(value)]


def _times(value: str, spec: dict, members) -> list:
    out = []
    for m in TIME_TOKEN.finditer(value):
        hh, mm, ss = int(m.group(1)), int(m.group(2)), m.group(3)
        if hh > 23 or mm > 59 or (ss is not None and int(ss) > 59):
            continue
        out.append(f"{hh:02d}:{mm:02d}" + (f":{int(ss):02d}" if ss is not None else ""))
    return out


def _counts(value: str, spec: dict, members) -> list:
    found = [(m.start(), int(m.group(1).replace(",", ""))) for m in INT_TOKEN.finditer(value)]
    for m in WORD_TOKEN.finditer(value):
        if m.group(3):
            n = _ONES.index(m.group(3).lower())
        else:
            n = _TENS[m.group(1).lower()] + (_ONES.index(m.group(2).lower()) if m.group(2) else 0)
        found.append((m.start(), n))
    return [n for _, n in sorted(found)]


def _unit_at(rest: str, units) -> str | None:
    """The unit phrase rest starts with, from units, or None."""
    r = rest.casefold()
    for u in sorted(units, key=len, reverse=True):
        if r.startswith(u) and (len(r) == len(u) or not (r[len(u)].isalnum() and u[-1].isalnum())):
            return u
    return None


def _figures(value: str, spec: dict, members) -> list:
    out = []
    accepted = [u.casefold() for u in spec.get("units", [])]
    for m in NUM_TOKEN.finditer(value):
        number = Decimal(m.group(1).replace(",", "") + (m.group(2) or ""))
        rest = value[m.end():]
        mult = 1
        mag = re.match(r"\s*(thousand|million|billion|[kKMB])(?![A-Za-z])", rest)
        if mag:
            mult = MAGNITUDES[mag.group(1).lower()]
            rest = rest[mag.end():]
        rest = rest.lstrip()
        unit = _unit_at(rest, accepted)
        given = "given" if unit else ("other" if _unit_at(rest, KNOWN_UNITS) else "absent")
        out.append({"number": number, "value": number * mult, "unit": given})
    return out


def _files(value: str, spec: dict, members) -> list:
    names = {m.casefold(): m for m in members}
    out = []
    for tok in re.findall(r"[A-Za-z0-9_./\\'\-]+", value):
        t = tok.replace("\\", "/").strip(".'-")
        t = re.sub(r"'s$", "", t, flags=re.IGNORECASE)
        for prefix in FILE_PREFIXES:
            if t.casefold().startswith(prefix):
                t = t[len(prefix):]
        hit = names.get(t.casefold()) or names.get(t.casefold() + ".md")
        if hit:
            out.append(hit)
        elif t.casefold().endswith(".md"):
            out.append("unlisted")
    return out


PARSERS = {"sha": _hexes, "hex": _hexes, "time": _times, "count": _counts,
           "figure": _figures, "file": _files}


def _written_significand(written: str) -> Decimal | None:
    m = NUM_TOKEN.search(written)
    return None if m is None else Decimal(m.group(1).replace(",", "") + (m.group(2) or ""))


def compare(spec: dict, entry: dict, got) -> tuple[str, dict]:
    """The class of a parsed value against a key entry holding a value."""
    kind, want = spec["type"], entry["value"]
    if kind in ("sha", "hex"):
        ok = (len(got) >= MIN_HEX[kind]
              and (got.startswith(want) or want.startswith(got)))
        return ("exact" if ok else "wrong"), {}
    if kind == "time":
        if len(got) == 5:
            return "wrong", {"precision": "minutes"}
        return ("exact" if got == want else "wrong"), {"precision": "seconds"}
    if kind == "count":
        return ("exact" if got == int(want) else "wrong"), {}
    if kind == "file":
        return ("exact" if got == want else "wrong"), {}
    # a figure
    flags = {"unit": got["unit"]}
    key_value = Decimal(entry["value"])
    if got["unit"] == "given":
        return ("exact" if got["value"] == key_value else "wrong"), flags
    if got["unit"] == "other":
        return "wrong", flags
    significand = _written_significand(entry.get("written", ""))
    if got["value"] == key_value or (significand is not None and got["number"] == significand):
        return "dropped_unit", flags
    return "wrong", flags


def normal_form(spec: dict, got):
    """What outcome.data records of a parsed value: closed forms only."""
    if spec["type"] == "figure":
        return {"value": format(got["value"].normalize(), "f"), "unit": got["unit"]}
    return got


def score(spec: dict, entry: dict, content, members) -> dict:
    """{class, answer, answer_form, flags, raw}: the reply's content scored
    against one key entry. raw is the model's answer line, for the transcript
    only."""
    flags: dict = {}
    value, raw, lines = answer_field(content)
    flags["answer_lines"] = lines
    key_nil = bool(entry.get("nil"))
    out = {"class": None, "answer": None, "answer_form": None, "flags": flags, "raw": raw}
    if value is None:
        out.update({"class": "no_answer", "answer_form": "absent"})
        return out
    is_nil, more = nil_match(value)
    if is_nil:
        flags["nil_with_more"] = more
        flags["nil_answer"] = not key_nil
        out.update({"class": "exact" if key_nil else "wrong", "answer": NIL,
                    "answer_form": "not_in_input"})
        return out
    parsed = PARSERS[spec["type"]](value, spec, members)
    flags["values_in_answer"] = len(parsed)
    if not parsed:
        out.update({"class": "no_answer", "answer_form": "unparsed"})
        return out
    got = parsed[0]
    out["answer"] = normal_form(spec, got)
    out["answer_form"] = "value"
    if key_nil:
        out["class"] = "overclaim"
        if spec["type"] == "figure":
            flags["unit"] = got["unit"]
        return out
    cls, more_flags = compare(spec, entry, got)
    flags.update(more_flags)
    out["class"] = cls
    return out


def answer_forms(spec: dict, entry: dict) -> list[str]:
    """Replies that hold the key's own answer, in the canonical form and in
    variants the scorer accepts: the key must score exact in every one of them
    (the control that the key scores 100%)."""
    if entry.get("nil"):
        return ["ANSWER: not in the input",
                "The ledger above has no entry that says.\n\n**ANSWER:** Not in the input."]
    v = entry["value"]
    kind = spec["type"]
    if kind in ("sha", "hex"):
        return [f"ANSWER: {v}", f"It is commit `{v}`.\n\nANSWER: `{v}`"]
    if kind == "time":
        return [f"ANSWER: {v}", f"- **ANSWER**: {v} -0700"]
    if kind == "count":
        n = int(v)
        forms = [f"ANSWER: {n}", f"ANSWER: {n:,} in all"]
        if n < 20:
            forms.append(f"ANSWER: {_ONES[n]}")
        return forms
    if kind == "figure":
        return [f"ANSWER: {entry['written']}", f"ANSWER: {v} {entry['unit']}"]
    stem = v[:-3] if v.endswith(".md") else v
    return [f"ANSWER: {v}", f"ANSWER: `{v}`", f"ANSWER: {stem}"]


# -- the key ---------------------------------------------------------------------------------------
def check_key_entry(spec: dict, entry, cut: str) -> None:
    """A key entry's form for one item at one cut. Raises ValueError."""
    iid = spec["id"]
    if not isinstance(entry, dict):
        raise ValueError(f"the key has no entry for {iid} at {cut}")
    if entry.get("nil") is True:
        return
    if "value" not in entry or not entry.get("evidence"):
        raise ValueError(f"the key's entry for {iid} at {cut} has no value or no evidence")
    kind, v = spec["type"], entry["value"]
    ok = {
        "sha": lambda: bool(re.fullmatch(r"[0-9a-f]{7,40}", v)),
        "hex": lambda: bool(re.fullmatch(r"[0-9a-f]{8,64}", v)),
        "time": lambda: bool(re.fullmatch(r"\d{2}:\d{2}:\d{2}", v)),
        "count": lambda: isinstance(v, int) and v >= 0,
        "figure": lambda: (entry.get("unit", "").casefold() in [u.casefold() for u in spec["units"]]
                           and bool(entry.get("written")) and _decimal(v) is not None),
        "file": lambda: isinstance(v, str) and bool(v),
    }[kind]()
    if not ok:
        raise ValueError(f"the key's value for {iid} at {cut} is not a {kind}")


def _decimal(v):
    try:
        return Decimal(str(v))
    except InvalidOperation:
        return None


def read_key(data: bytes, items: dict) -> dict:
    if sha256_bytes(data) != items["key_sha256"]:
        raise SourceError("the key's SHA-256 is not the one qs6_items.json records")
    return json.loads(data.decode("utf-8"))


def _read_local(path, what: str, hint: str) -> bytes:
    p = Path(path)
    if not p.is_file():
        raise SourceError(f"{what} is missing ({p.name}): {hint}")
    return p.read_bytes()


# -- the suite ----------------------------------------------------------------------------------------
def _cut_spec(data: dict, cut: str) -> dict:
    return next(c for c in data["cuts"]["cuts"] if c["name"] == cut)


def caps_of(spec: dict) -> Caps:
    c = spec["caps"]
    return Caps(max_prompt_tokens=c["max_prompt_tokens"], max_output_tokens=c["max_output_tokens"],
                max_call_prompt_tokens=c["max_call_prompt_tokens"])


def _content_form(content) -> str:
    if content is None:
        return "null"
    if isinstance(content, str):
        return "empty" if not content.strip() else "text"
    return "other"


_COMMITTED = load_data()
VERSION = version_of([SOURCE_PATH, CUTS_PATH, ITEMS_PATH], Path(__file__))


class QS6(Suite):
    """The QS6 slice at one cut. Use a cut class: QS6C016K, QS6C032K, QS6C064K,
    QS6C128K or QS6Whole. Each takes no arguments in tools/live.py; tests pass
    a synthetic archive, key and data."""
    cut = ""
    name = "qs6"
    version = VERSION

    def __init__(self, *, archive=None, key=None, data: dict | None = None):
        if self.cut not in CUT_NAMES:
            raise TypeError("QS6 runs through a cut class, such as QS6C016K")
        data = data if data is not None else load_data()
        check_data(data)
        self.data = data
        spec = _cut_spec(data, self.cut)
        self.name = f"qs6-{self.cut}"
        self.caps = caps_of(spec)
        self.cut_time = datetime.fromisoformat(spec["time"])
        members = read_archive(
            _read_local(archive or ARCHIVE_PATH, "the local copy of round 6's archive",
                        "put it in place with tools/qs6_extract.py"), data["source"])
        self.members = sorted(members)
        self.text = cut_text(timeline(members), self.cut_time)
        if sha256_text(self.text) != spec["sha256"]:
            raise SourceError(f"cut {self.cut}'s text is not the one qs6_cuts.json records")
        self.cut_sha = spec["sha256"]
        items = data["items"]
        self.key_sha = items["key_sha256"]
        key_doc = read_key(_read_local(key or KEY_PATH, "the key",
                                       "the lead places it at local/qs6/qs6_key.json"), items)
        self.prompt = items["prompt"]
        self.specs = {it["id"]: it for it in items["items"]}
        self.key = {}
        for iid, it in self.specs.items():
            entry = (key_doc.get("items") or {}).get(iid, {}).get(self.cut)
            check_key_entry(it, entry, self.cut)
            self.key[iid] = entry

    def items(self) -> list[Item]:
        return [Item(iid, {"set": it["set"], "type": it["type"]}) for iid, it in self.specs.items()]

    def run_item(self, ctx, item: Item) -> ItemResult:
        spec, entry = self.specs[item.id], self.key[item.id]
        data = {
            "qs6": 1, "cut": self.cut, "cut_time": self.cut_time.isoformat(), "item": item.id,
            "set": spec["set"], "type": spec["type"],
            "key_kind": "not_in_input" if entry.get("nil") else "value",
            "class": None, "answer": None, "answer_form": None, "flags": {},
            "status_basis": None, "http": None, "finish_reason": None, "max_tokens_sent": None,
            "prompt_tokens": None, "output_tokens": None, "reasoning_tokens": None,
            "length_cause": None, "content": None,
            "key_sha256_12": self.key_sha[:12], "cut_sha256_12": self.cut_sha[:12],
        }
        try:
            turn = ctx.chat(request_messages(self.prompt, self.text, spec["question"]))
        except RunStopped as e:
            data["status_basis"] = "harness_cap"
            return ItemResult("stopped", f"stopped: {type(e).__name__}: {e}", data)
        except ProviderError as e:
            data["status_basis"] = "provider_error"
            data["http"] = e.status
            return ItemResult("error", f"error: HTTP {e.status}: {str(e.body or '')[:ERROR_BODY]}",
                              data)
        except Exception as e:  # noqa: BLE001 - a reply that never arrived whole
            data["status_basis"] = "transport"
            return ItemResult("error", f"error: {type(e).__name__}; "
                              f"{ctx.stop_reason or 'no stop reason set'}", data)
        usage = turn.usage
        request = ctx.calls[-1].get("request", {}) if ctx.calls else {}
        sent_max = request.get("max_tokens")
        finish = turn.finish_reason
        documented = frozenset(getattr(ctx.provider, "FINISH_REASONS", ()))
        data.update({
            "finish_reason": finish if isinstance(finish, str) and finish in documented
            else "undocumented",
            "max_tokens_sent": sent_max, "prompt_tokens": usage.prompt,
            "output_tokens": usage.output, "reasoning_tokens": usage.reasoning,
            "content": _content_form(turn.content),
        })
        if finish == "length":
            if isinstance(sent_max, int) and usage.output >= sent_max:
                limit = getattr(ctx.provider, "MAX_TOKENS", None)
                data["length_cause"] = ("provider_limit" if limit and sent_max >= limit
                                        else "harness_clamp")
                data["status_basis"] = "harness_cap"
                return ItemResult("stopped", f"stopped: the reply reached the max_tokens the "
                                  f"harness sent ({sent_max}): {data['length_cause']}", data)
            data["length_cause"] = "below_request_max_tokens"
            data["status_basis"] = "provider_condition"
            return ItemResult("error", "error: a length finish below the request's max_tokens",
                              data)
        if finish in PROVIDER_CONDITIONS:
            data["status_basis"] = "provider_condition"
            return ItemResult("error", f"error: the provider's finish_reason {finish}", data)
        if finish != "stop":
            data["status_basis"] = "unexpected_finish"
            return ItemResult("error", f"error: a finish_reason QS6 does not score "
                              f"({data['finish_reason']})", data)
        s = score(spec, entry, turn.content, self.members)
        data.update({"class": s["class"], "answer": s["answer"], "answer_form": s["answer_form"],
                     "flags": s["flags"], "status_basis": "scored"})
        status = "pass" if s["class"] == "exact" else "fail"
        return ItemResult(status, f"{status}: {s['class']}, {item.id} at {self.cut}", data,
                          local={"answer_line": s["raw"]})


def _cut_class(cut: str):
    spec = _cut_spec(_COMMITTED, cut)
    return type(f"QS6{cut.upper()}" if cut != "whole" else "QS6Whole", (QS6,), {
        "cut": cut, "name": f"qs6-{cut}", "caps": caps_of(spec),
        "__doc__": f"The QS6 slice at cut {cut}, the ledger to {spec['time']}.",
        "__module__": __name__})


QS6C016K = _cut_class("c016k")
QS6C032K = _cut_class("c032k")
QS6C064K = _cut_class("c064k")
QS6C128K = _cut_class("c128k")
QS6Whole = _cut_class("whole")
CUT_CLASSES = {"c016k": QS6C016K, "c032k": QS6C032K, "c064k": QS6C064K, "c128k": QS6C128K,
               "whole": QS6Whole}


# -- the table ------------------------------------------------------------------------------------------
def table(records) -> list[dict]:
    """Pool QS6 run records by cut, set and thinking setting: each class's count
    by key kind, accuracy over runs keyed with a value, overclaims over runs
    keyed "not in the input", runs not scored by status, and the median prompt
    tokens, which is the cut's measured size."""
    rows: dict = {}
    for r in records:
        if not str(r.get("suite", "")).startswith("qs6-"):
            continue
        d = (r.get("outcome") or {}).get("data") or {}
        k = (d.get("cut"), d.get("set"), r.get("thinking"))
        row = rows.setdefault(k, {"cut": k[0], "set": k[1], "thinking": k[2],
                                  "value": {c: 0 for c in CLASSES},
                                  "not_in_input": {c: 0 for c in CLASSES},
                                  "not_scored": {}, "prompt_tokens": []})
        cls = d.get("class")
        if cls in CLASSES:
            row["value" if d.get("key_kind") == "value" else "not_in_input"][cls] += 1
        else:
            status = (r.get("outcome") or {}).get("status")
            row["not_scored"][status] = row["not_scored"].get(status, 0) + 1
        if isinstance(d.get("prompt_tokens"), int):
            row["prompt_tokens"].append(d["prompt_tokens"])
    out = []
    order = {c: i for i, c in enumerate(CUT_NAMES)}
    for k in sorted(rows, key=lambda k: (order.get(k[0], 99), str(k[1]), str(k[2]))):
        row = rows[k]
        v, n = row["value"], row["not_in_input"]
        nv, nn = sum(v.values()), sum(n.values())
        row["accuracy"] = None if nv == 0 else v["exact"] / nv
        row["accuracy_denominator"] = nv
        row["overclaim_rate"] = None if nn == 0 else n["overclaim"] / nn
        row["overclaim_denominator"] = nn
        tokens = row.pop("prompt_tokens")
        row["median_prompt_tokens"] = statistics.median(tokens) if tokens else None
        out.append(row)
    return out
