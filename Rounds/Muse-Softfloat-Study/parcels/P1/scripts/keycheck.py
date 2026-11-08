"""Task 3 step 1: hash every file in <muse>/scratch/lead/keys/ and match to rows.

Matches against (a) the library plants rows' key_sha256, (b) the toy plants
rows' key_sha256, (c) plant_keys.sha256 at the library commit.
Writes data/keycheck.csv. Never prints a key's content.
"""
import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C


def main():
    a = C.args()
    keydir = os.path.join(C.muse(a.repos), "scratch", "lead", "keys")
    lib = C.lib_jsonl(a.repos, "plants")
    toy = [r for r in C.toy_plants(a.repos) if r.get("key_sha256")]
    lib_hash = {}
    for r in lib:
        lib_hash.setdefault(r["key_sha256"], set()).add(r["verifier"])
    toy_hash = {}
    for r in toy:
        toy_hash.setdefault(r["key_sha256"], set()).add(r["parcel"])
    pk = {}
    for line in C.show(C.lib_repo(a.repos), C.LIB_SHA, "docs/metrics/plant_keys.sha256").splitlines():
        m = re.match(r"^([0-9a-f]{64})\s+(.*)$", line)
        if m:
            pk[m.group(1)] = m.group(2)
    rows = []
    seen_files = {}
    for fn in sorted(os.listdir(keydir)):
        with open(os.path.join(keydir, fn), "rb") as f:
            h = C.sha256_bytes(f.read())
        seen_files[h] = fn
        in_lib = sorted(lib_hash.get(h, []))
        in_toy = sorted(toy_hash.get(h, []))
        kind = "draft" if fn.endswith("-draft.json") else "final"
        if in_lib or in_toy:
            status = "match"
        else:
            status = "UNMATCHED_DRAFT" if kind == "draft" else "FINDING_UNMATCHED_KEY"
        rows.append([fn, kind, h[:8], status, ";".join(in_lib), ";".join(in_toy), "yes" if h in pk else "no"])
    C.write_csv(os.path.join(C.DATA, "keycheck.csv"),
                ["file", "kind", "sha256_prefix", "status", "library_verifiers", "toy_parcels", "in_plant_keys_sha256"], rows)
    n_match = sum(1 for r in rows if r[3] == "match")
    print("key files: %d; match: %d; unmatched drafts: %d; unmatched final keys (findings): %d" % (
        len(rows), n_match, sum(1 for r in rows if r[3] == "UNMATCHED_DRAFT"),
        sum(1 for r in rows if r[3] == "FINDING_UNMATCHED_KEY")))
    print("library row hashes: %d distinct; found as files: %d" % (len(lib_hash), sum(1 for h in lib_hash if h in seen_files)))
    print("toy row hashes: %d distinct; found as files: %d" % (len(toy_hash), sum(1 for h in toy_hash if h in seen_files)))
    print("plant_keys.sha256 hashes: %d; found as files: %d; rows covered: %d" % (
        len(pk), sum(1 for h in pk if h in seen_files),
        sum(1 for r in lib if r["key_sha256"] in pk)))
    print("misses covered by plant_keys.sha256: %d" % sum(1 for r in lib if r["grade"] != "caught" and r["key_sha256"] in pk))


main()
