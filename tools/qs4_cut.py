"""The cutter: round 6's ledger, cut at each QS4 item's dispatch.

    python tools/qs4_cut.py --parcelround <a ParcelRound checkout> [--local <dir>] [--write-expected]
    python tools/qs4_cut.py --zip <the archive> [--local <dir>] [--write-expected]

It reads round 6's archive, archive/round6-ledger.zip at f42242e, either from
ParcelRound's object store or from a file. A checkout is read with
GIT_OPTIONAL_LOCKS=0, and nothing is written in it. The archive is refused unless
it is the one qs4_expected.json pins: its blob, size and SHA-256, and every
member's SHA-256. With --write-expected, made once in phase 2, the archive's
identity is recorded first.

For each item it builds the cut with qs.suites.qs4.cut_for:
- the rule;
- a real tip's one substitution;
- the checks that keys/, the parcel's file, a later entry, a plant's text and
  the other run's SHA are absent.
Each cut goes under <local>/cuts/<first 12 hex digits of its digest>/, and a cut
whose digest differs from the pinned one is refused. A cut already there is
checked, not rewritten.

It also writes <local>/archive/round6-ledger.zip and <local>/cuts.json. <local>
defaults to local/qs4 in this checkout, which is gitignored. It prints no absolute
path of its own: an OSError's text names a path as it was given on the command
line (verifier-P4's N1). It exits 0 only when every cut is as pinned.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from qs.suites import qs4  # noqa: E402


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--parcelround", help="a ParcelRound checkout holding f42242e")
    src.add_argument("--zip", help="the archive's bytes, in a file")
    ap.add_argument("--local", default=str(qs4.LOCAL))
    ap.add_argument("--items", default=str(qs4.ITEMS_PATH), help=argparse.SUPPRESS)       # tests' worlds
    ap.add_argument("--expected", default=str(qs4.EXPECTED_PATH), help=argparse.SUPPRESS)
    ap.add_argument("--write-expected", action="store_true",
                    help="record the archive's identity and the cuts' digests in qs4_expected.json")
    a = ap.parse_args(argv)
    items, local, expected_path = qs4.load_json(Path(a.items)), Path(a.local), Path(a.expected)
    expected = qs4.load_json(expected_path) if expected_path.exists() else {"format": 1}
    try:
        data = (qs4.archive_from_git(Path(a.parcelround), items["archive"]["parcelround"], items["archive"]["path"])
                if a.parcelround else Path(a.zip).read_bytes())
        if a.write_expected:
            expected["archive"] = qs4.archive_spec(data)
        members = qs4.archive_members(data, expected["archive"])
        keys = qs4.keys_of(members, items)
    except (qs4.InputError, OSError, KeyError) as e:
        print(f"REFUSED: {type(e).__name__}: {e}")
        return 2
    print(f"archive: {len(data)} bytes, blob {expected['archive']['blob'][:12]}, "
          f"sha256 {expected['archive']['sha256'][:12]}, {len(members)} members: as pinned")
    (local / "archive").mkdir(parents=True, exist_ok=True)
    (local / "archive" / "round6-ledger.zip").write_bytes(data)
    index, bad = {}, 0
    cuts = expected.setdefault("cuts", {}) if a.write_expected else expected.get("cuts", {})
    for item in items["items"]:
        iid = item["id"]
        try:
            files = qs4.cut_for(members, items, item, keys)
            digest = qs4.tree_digest(files)
            if a.write_expected:
                cuts[iid] = {"digest": digest, "files": sorted(files), "bytes": sum(map(len, files.values()))}
            if cuts.get(iid, {}).get("digest") != digest:
                raise qs4.InputError("its digest is not the one qs4_expected.json pins")
            dest = local / "cuts" / digest[:12]
            if dest.exists():
                if qs4.tree_digest(qs4.read_files(dest)) != digest:
                    raise qs4.InputError("the cut already written there differs")
            else:
                qs4.write_files(files, dest)
            index[iid] = {"dir": f"cuts/{digest[:12]}", "digest": digest}
            print(f"{iid:11} T {items['parcels'][item['parcel']]['dispatch']}: {len(files)} files, "
                  f"{sum(map(len, files.values()))} bytes, digest {digest[:12]}: ok")
        except qs4.InputError as e:
            bad += 1
            print(f"{iid:11} REFUSED: {e}")
    (local / "cuts.json").write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if a.write_expected:
        expected_path.write_text(json.dumps(expected, indent=2, sort_keys=True) + "\n", encoding="utf-8",
                                 newline="\n")
        print("wrote qs4_expected.json: the archive and the cuts")
    print(f"cuts: {len(index)} of {len(items['items'])} as pinned")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
