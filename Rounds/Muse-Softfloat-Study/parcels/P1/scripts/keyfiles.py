"""Read each hash-verified key's per-plant `file` for the 195 library plant rows.

Only keys whose sha256 equals a row's key_sha256 are opened for content (keycheck.py
established 39 of 39). Writes data/key_plants.csv: row id, verifier, plant, key file prefix,
file path altered, whether the key's shape text equals the row's shape, and the
key's old/new text lengths (the text itself is not copied).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C


def main():
    a = C.args()
    keydir = os.path.join(C.muse(a.repos), "scratch", "lead", "keys")
    lib = C.lib_jsonl(a.repos, "plants")
    by_hash = {}
    for fn in sorted(os.listdir(keydir)):
        b = open(os.path.join(keydir, fn), "rb").read()
        h = C.sha256_bytes(b)
        by_hash[h] = (fn, b)
    out = []
    bad = 0
    for i, r in enumerate(lib, 1):
        fn, b = by_hash[r["key_sha256"]]  # KeyError would mean an unmatched key: stop
        k = json.loads(b.decode("utf-8"))
        pls = k["plants"]
        p = pls[r["plant"] - 1] if r["plant"] - 1 < len(pls) else None
        same = bool(p) and p.get("shape") == r["shape"]
        if not same:
            bad += 1
        out.append([i, r["verifier"], r["plant"], fn[:-5], p.get("file", "") if p else "", "yes" if same else "NO",
                    len(p.get("old", "")) if p else "", len(p.get("new", "")) if p else "", len(pls)])
    C.write_csv(os.path.join(C.DATA, "key_plants.csv"),
                ["row", "verifier", "plant", "key_file", "altered_file", "shape_equals_row", "old_len", "new_len", "key_plants_total"], out)
    print("rows %d; shape differs from key's: %d; keys with plants != 5: %d" % (
        len(out), bad, sum(1 for o in out if o[8] != 5)))


main()
