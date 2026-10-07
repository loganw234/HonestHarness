"""Check QS6's key before any run, give its hash, and show an item's evidence.

    python tools/qs6_key.py --check [--key FILE] [--archive FILE]
    python tools/qs6_key.py --hash [--key FILE]
    python tools/qs6_key.py --show ITEM [--key FILE] [--archive FILE]

The key is local/qs6/qs6_key.json by default, and the archive
local/qs6/round6-ledger.zip. The key stays out of the repository until the runs
are scored; qs/suites/qs6_items.json holds its SHA-256.

--check holds each of these, and names each that fails:
  1. the key's SHA-256 is the one qs6_items.json records;
  2. its form: it names the source's SHA-256 and every cut's as committed, and
     holds, for every item at every cut, an entry the item's type allows:
     "not in the input", or a value with its evidence;
  3. the key scores 100% against itself: every entry, in every answer form
     qs6.answer_forms gives, scores exact under qs6.score;
  4. with the archive present: every line the key cites exists in its member;
     a value's evidence lies in its cut and is cited by the item; and a "not in
     the input" entry's cut holds none of the lines the item cites.
--hash prints the key's SHA-256, which is what qs6_items.json takes.
--show prints an item's question, each line it cites with the time of the unit
that holds it, and the key at every cut, for a reader such as the key's
verifier.

It prints no absolute path, and only ASCII (other characters escaped). Exit
status: 0 when everything holds, 2 when something fails, and 2 also for a
usage error, which argparse reports (restated at P3's merge, verifier-P3's
N1).
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from qs.suites import qs6  # noqa: E402


def ascii(text: str) -> str:
    return text.encode("ascii", "backslashreplace").decode("ascii")


def locate(units: list, members: dict, cite: str):
    """(the unit holding a cited line, the line's text), or (None, None)."""
    name, _, n = cite.rpartition(":")
    if name not in members or not n.isdigit():
        return None, None
    text = members[name][0]
    lines = text.split("\n")
    k = int(n)
    if not 1 <= k <= len(lines):
        return None, None
    offset = sum(len(x) + 1 for x in lines[:k - 1])
    pos = 0
    for u in (u for u in units if u.file == name):
        start = text.find(u.text, pos)
        if start <= offset < start + len(u.text):
            return u, lines[k - 1]
        pos = start + len(u.text)
    return None, lines[k - 1]


def check(key_bytes: bytes, data: dict, archive: bytes | None) -> list[str]:
    """Every failure, in the tool's own words. Empty when the key holds."""
    bad: list[str] = []
    items = data["items"]
    got = qs6.sha256_bytes(key_bytes)
    if got != items["key_sha256"]:
        bad.append(f"1. the key's SHA-256 is {got[:12]}..., not the {items['key_sha256'][:12]}... "
                   "qs6_items.json records")
    try:
        key = json.loads(key_bytes.decode("utf-8"))
    except ValueError:
        return bad + ["2. the key is not JSON"]
    if key.get("source_sha256") != data["source"]["sha256"]:
        bad.append("2. the key names another source")
    cut_shas = {c["name"]: c["sha256"] for c in data["cuts"]["cuts"]}
    if key.get("cuts") != cut_shas:
        bad.append("2. the key's cut hashes are not the ones qs6_cuts.json records")
    specs = {it["id"]: it for it in items["items"]}
    extra = sorted(set(key.get("items") or {}) - set(specs))
    if extra:
        bad.append(f"2. the key holds items qs6_items.json does not: {extra}")
    members = units = None
    if archive is not None:
        members = qs6.read_archive(archive, data["source"])
        units = qs6.timeline(members)
    times = {c["name"]: datetime.fromisoformat(c["time"]) for c in data["cuts"]["cuts"]}
    for iid, spec in specs.items():
        for cut in qs6.CUT_NAMES:
            entry = ((key.get("items") or {}).get(iid) or {}).get(cut)
            try:
                qs6.check_key_entry(spec, entry, cut)
            except ValueError as e:
                bad.append(f"2. {e}")
                continue
            names = sorted(members) if members else [c.rpartition(":")[0] for c in spec["evidence"]]
            for form in qs6.answer_forms(spec, entry):
                s = qs6.score(spec, entry, form, names)
                if s["class"] != "exact":
                    bad.append(f"3. {iid} at {cut}: one of the key's own answer forms scores "
                               f"{s['class']}")
            if units is None:
                continue
            t = times[cut]
            if entry.get("nil"):
                inside = [c for c in spec["evidence"] if (u := locate(units, members, c)[0]) and u.t <= t]
                if inside:
                    bad.append(f"4. {iid} at {cut} is 'not in the input', but the cut holds {inside}")
                continue
            for c in entry["evidence"]:
                u, _ = locate(units, members, c)
                if u is None:
                    bad.append(f"4. {iid} at {cut} cites {c}, which is no member's line")
                elif u.t > t:
                    bad.append(f"4. {iid} at {cut} cites {c}, which lies after the cut")
                if c not in spec["evidence"]:
                    bad.append(f"4. {iid} at {cut} cites {c}, which qs6_items.json does not")
    return bad


def show(iid: str, key_bytes: bytes | None, data: dict, archive: bytes | None) -> list[str]:
    specs = {it["id"]: it for it in data["items"]["items"]}
    if iid not in specs:
        return [f"no item {iid}"]
    spec = specs[iid]
    out = [f"{iid} ({spec['set']}, {spec['type']}): {spec['question']}"]
    if archive is not None:
        members = qs6.read_archive(archive, data["source"])
        units = qs6.timeline(members)
        for c in spec["evidence"]:
            u, line = locate(units, members, c)
            when = u.t.isoformat() if u else "no unit"
            out.append(f"  {c} [{when}] {line if line is not None else '(no such line)'}")
    else:
        out.append("  (no local copy: cited lines not shown) " + ", ".join(spec["evidence"]))
    if key_bytes is not None:
        key = json.loads(key_bytes.decode("utf-8"))
        for cut in qs6.CUT_NAMES:
            out.append(f"  key at {cut}: {json.dumps(((key.get('items') or {}).get(iid) or {}).get(cut))}")
    return [ascii(x) for x in out]


def _read(path: Path, what: str) -> bytes:
    if not path.is_file():
        raise qs6.SourceError(f"{what} is missing ({path.name})")
    return path.read_bytes()


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--hash", action="store_true")
    mode.add_argument("--show", metavar="ITEM")
    ap.add_argument("--key", default=str(qs6.KEY_PATH))
    ap.add_argument("--archive", default=str(qs6.ARCHIVE_PATH))
    a = ap.parse_args(argv)
    try:
        data = qs6.load_data()
        qs6.check_data(data)
        archive_path = Path(a.archive)
        archive = archive_path.read_bytes() if archive_path.is_file() else None
        if a.hash:
            print(qs6.sha256_bytes(_read(Path(a.key), "the key")))
            return 0
        if a.show:
            key_path = Path(a.key)
            print("\n".join(show(a.show, key_path.read_bytes() if key_path.is_file() else None,
                                 data, archive)))
            return 0
        bad = check(_read(Path(a.key), "the key"), data, archive)
        items = len(data["items"]["items"])
        if archive is None:
            print("note: no local copy of the archive, so check 4 (the evidence) did not run")
        for b in bad:
            print(ascii(b))
        print(f"key: {items} items at {len(qs6.CUT_NAMES)} cuts; "
              + ("holds" if not bad else f"{len(bad)} failure(s)"))
        return 0 if not bad else 2
    except qs6.SourceError as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
