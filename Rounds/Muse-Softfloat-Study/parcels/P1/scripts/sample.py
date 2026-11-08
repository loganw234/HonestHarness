"""Task 3: draw the re-grade sample (seeded) and write the blind sheet.

Library: all 8 misses; 30 catches, allocated across waves in proportion to each wave's
catches (floor, minimum 1, remainders by largest remainder), then within a wave taken
round-robin across the rubric's classes in a seeded random order.
Writes data/sample_blind.csv (no lead grade) and, for my own reading only, a key
detail sheet in the scratch directory (the keys' old/new text is never committed).
"""
import collections
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C


def allocate(counts, total):
    s = sum(counts.values())
    base = {w: max(1, int(total * c / s)) for w, c in counts.items()}
    while sum(base.values()) > total:  # minimum-1 may overshoot: trim the largest
        w = max(base, key=lambda k: base[k]); base[w] -= 1
    rem = sorted(counts, key=lambda w: -(total * counts[w] / s - int(total * counts[w] / s)))
    i = 0
    while sum(base.values()) < total:
        base[rem[i % len(rem)]] += 1; i += 1
    return base


def main():
    a = C.args()
    rng = random.Random(C.SEED)
    lib = C.lib_jsonl(a.repos, "plants")
    cls = {int(r["row"]): r for r in C.read_csv(os.path.join(C.DATA, "plants_class_blind.csv"))}
    rows = sorted(enumerate(lib, 1), key=lambda t: (t[1]["wave"], t[1]["verifier"], t[1]["plant"]))
    misses = [t for t in rows if t[1]["grade"] != "caught"]
    caught = [t for t in rows if t[1]["grade"] == "caught"]
    counts = collections.Counter(t[1]["wave"] for t in caught)
    alloc = allocate(counts, 30)
    picked = []
    for w in sorted(counts):
        pool = [t for t in caught if t[1]["wave"] == w]
        byc = collections.defaultdict(list)
        for t in pool:
            byc[cls[t[0]]["class"]].append(t)
        order = sorted(byc)
        rng.shuffle(order)
        for c in order:
            rng.shuffle(byc[c])
        got = []
        while len(got) < alloc[w]:
            for c in order:
                if byc[c] and len(got) < alloc[w]:
                    got.append(byc[c].pop())
        picked += got
    sample = [("miss", t) for t in misses] + [("catch:" + t[1]["wave"], t) for t in picked]
    out = []
    for sid, (st, (i, r)) in enumerate(sample, 1):
        out.append(["L%02d" % sid, st, i, r["wave"], r["verifier"], r["plant"], cls[i]["class"], r["shape"], r["key_sha256"][:8]])
    C.write_csv(os.path.join(C.DATA, "sample_blind.csv"),
                ["sample_id", "stratum", "plants_row", "wave", "verifier", "plant", "class", "shape", "key_prefix"], out)
    print("allocation of 30 catches by wave:", dict(sorted(alloc.items())), "sum", sum(alloc.values()))
    print("sample size:", len(out), "misses:", len(misses), "catches:", len(picked))
    print("catches by class:", dict(collections.Counter(cls[t[0]]["class"] for t in picked)))
    # my own reading sheet (scratch only): the key's file/old/new for each sampled plant
    if a.scratch:
        keydir = os.path.join(C.muse(a.repos), "scratch", "lead", "keys")
        by_hash = {}
        for fn in os.listdir(keydir):
            b = open(os.path.join(keydir, fn), "rb").read()
            by_hash[C.sha256_bytes(b)] = b
        sheet = []
        for sid, (st, (i, r)) in enumerate(sample, 1):
            k = json.loads(by_hash[r["key_sha256"]].decode("utf-8"))
            p = k["plants"][r["plant"] - 1]
            sheet.append({"id": "L%02d" % sid, "verifier": r["verifier"], "plant": r["plant"], "shape": r["shape"],
                          "file": p.get("file"), "old": p.get("old", "")[:400], "new": p.get("new", "")[:400],
                          "copy_commit": k.get("copy_commit")})
        os.makedirs(a.scratch, exist_ok=True)
        json.dump(sheet, open(os.path.join(a.scratch, "keysheet.json"), "w", encoding="utf-8"), indent=1)


main()
