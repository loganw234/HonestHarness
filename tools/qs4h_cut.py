"""The cutter: this round's ledger, copied once, then cut at each QS4h item's stamp.

    python tools/qs4h_cut.py --ledger <the round's ledger> [--local <dir>] [--write-expected]

Run tools/qs4h_rebuild.py first: the cut maps each item's SHAs to its own commit, and
reads the real-tip builds from qs4h_expected.json.
1. The live ledger is read once, every regular file with its SHA-256, size and kept
   time (its mtime at -07:00, the stamps' zone), and copied to
   <local>/ledger/<12 hex of the manifest's digest>/. A link is refused. Nothing in the
   ledger is written. The keys are taken from that copy, each refused unless its SHA-256
   is the hash the lead sealed.
2. Each item's cut, from the copy (qs.suites.qs4h.cut_for): QS4's rule at the stamp;
   for P1 and P2 the two shared briefs rebuilt without their pinned lines; both SHAs
   mapped to the item's own commit; refused when it holds another of the parcel's
   commits, a plant's text, a key's description, keys/, the parcel's own file or a later
   entry, or lacks a brief its verifier read.
3. A planted item's cut and its real tip's must differ only where each item's own
   commit stands.
4. Each cut goes under <local>/cuts/<12 hex of its digest>/, and a cut whose digest
   differs from the pinned one is refused. A cut already there is checked, not
   rewritten. It writes <local>/cuts.json. With --write-expected, made once, the cuts'
   digests, file lists and sizes and the rebuilt briefs' SHA-256 go into
   qs4h_expected.json.

It prints no absolute path, and exits 0 only when every cut is as pinned.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from qs.suites import qs4, qs4h  # noqa: E402
from qs.suites.qs4h import InputError, sha256  # noqa: E402


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ledger", required=True, help="the round's ledger directory, read only")
    ap.add_argument("--local", default=str(qs4h.LOCAL))
    ap.add_argument("--items", default=str(qs4h.ITEMS_PATH), help=argparse.SUPPRESS)       # tests' worlds
    ap.add_argument("--expected", default=str(qs4h.EXPECTED_PATH), help=argparse.SUPPRESS)
    ap.add_argument("--write-expected", action="store_true",
                    help="record the cuts' digests and the rebuilt briefs' hashes in qs4h_expected.json")
    a = ap.parse_args(argv)
    items, local, expected_path = qs4.load_json(Path(a.items)), Path(a.local), Path(a.expected)
    expected = qs4.load_json(expected_path) if expected_path.exists() else {"format": 1}
    try:
        entries = qs4h.snapshot_ledger(Path(a.ledger))
        copy = qs4h.write_snapshot(entries, local)
        members, manifest = qs4h.load_snapshot(copy)
        keys = {}
        for p, spec in items["parcels"].items():
            data = members[qs4h.LEDGER_ROOT + spec["key"]][0]
            if sha256(data) != spec["key_sha256"]:
                raise InputError(f"{spec['key']} is not the key whose hash the lead sealed")
            keys[p] = json.loads(data)
        if not expected.get("builds"):
            raise InputError("qs4h_expected.json pins no real-tip builds: run tools/qs4h_rebuild.py first")
    except (InputError, OSError, KeyError, ValueError) as e:
        print(f"REFUSED: {type(e).__name__}: {e}")
        return 2
    print(f"ledger copy: {len(manifest)} files, copy {copy.name}; keys {len(keys)}, each the sealed hash")
    cuts = expected.setdefault("cuts", {}) if a.write_expected else expected.get("cuts", {})
    index, bad, made = {}, 0, {}
    for item in items["items"]:
        iid = item["id"]
        try:
            files = qs4h.cut_for(members, items, expected, item, keys)
            digest = qs4.tree_digest(files)
            if a.write_expected:
                cuts[iid] = {"digest": digest, "files": sorted(files), "bytes": sum(map(len, files.values()))}
            if cuts.get(iid, {}).get("digest") != digest:
                raise InputError("its digest is not the one qs4h_expected.json pins")
            dest = local / "cuts" / digest[:12]
            if dest.exists():
                if qs4.tree_digest(qs4.read_files(dest)) != digest:
                    raise InputError("the cut already written there differs")
            else:
                qs4.write_files(files, dest)
            index[iid], made[iid] = {"dir": f"cuts/{digest[:12]}", "digest": digest}, files
            print(f"{iid:11} T {items['parcels'][item['parcel']]['stamp']}: {len(files)} files, "
                  f"{sum(map(len, files.values()))} bytes, lead.md {files['lead.md'].count(b'\n')} lines, "
                  f"digest {digest[:12]}: ok")
        except InputError as e:
            bad += 1
            print(f"{iid:11} REFUSED: {e}")
    # the two conditions read alike: they differ only where each item's own commit stands
    for p in items["parcels"]:
        pl, rl = f"h{p[1]}-planted", f"h{p[1]}-real"
        if pl in made and rl in made:
            shas = qs4h.parcel_shas(items, expected, p)
            if qs4h.mask_own(made[pl], shas["copy"]) != qs4h.mask_own(made[rl], shas["build"]):
                bad += 1
                print(f"{p}: REFUSED: its two cuts differ beyond the item's own commit")
            else:
                print(f"{p}: the planted and real cuts differ only where each item's own commit stands")
    rebuilt = {}
    rebuilt_for = [i for i in made if qs4h.item_spec(items, i)["parcel"] in items["briefs_rebuild"]["parcels"]]
    for edit in items["briefs_rebuild"]["edits"]:
        texts = {sha256(made[i][edit["file"]]) for i in rebuilt_for}
        if len(texts) == 1:
            rebuilt[edit["file"]] = texts.pop()
    if a.write_expected:
        expected["briefs_rebuilt"] = rebuilt
    elif expected.get("briefs_rebuilt") != rebuilt:
        bad += 1
        print("REFUSED: the rebuilt briefs are not the pinned ones")
    (local / "cuts.json").write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if a.write_expected:
        expected_path.write_text(json.dumps(expected, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        print("wrote qs4h_expected.json: the cuts and the rebuilt briefs")
    print(f"rebuilt briefs: " + ", ".join(f"{k} {v[:12]}" for k, v in sorted(rebuilt.items())))
    print(f"cuts: {len(index)} of {len(items['items'])} as pinned")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
