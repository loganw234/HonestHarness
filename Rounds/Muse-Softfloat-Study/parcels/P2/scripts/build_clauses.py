"""Task 1, step 3: check the curated clause list against the kit and write data/clauses.csv.

usage: python -I build_clauses.py --repos <repos> --curated scripts/clauses_curated.txt \
           --out data/clauses.csv [--cand <candidates.csv>]

Checks: each row's fragment occurs in its cited lines (whitespace folded); each
also_in file:line exists; ids are unique. Prints the counts the analysis quotes:
rows, rows by marking, kit lines covered by the rows' own lines, and with also_in.
"""
import argparse, csv, os, re, sys
from collections import Counter

MARKS = {"DONE", "ADAPTED", "SKIPPED", "NA", "UNKNOWN"}
KIT_OWN = {"START-HERE.md", "WORKFLOW.md", "ROLES.md", "OWNER.md", "AGENTS.md", "CLEAN-ROOM.md",
           "METRICS.md", "HARNESS.md", "BOARD.md", "PROJECT.md"}


def fold(s):
    return re.sub(r"\s+", " ", s).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repos", required=True)
    ap.add_argument("--curated", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cand")
    a = ap.parse_args()
    kit = os.path.join(a.repos, "Muse-Softfloat", "softfloat-bootstrap-kit")
    cache = {}

    def lines_of(f):
        if f not in cache:
            with open(os.path.join(kit, f), encoding="utf-8") as fh:
                cache[f] = fh.read().splitlines()
        return cache[f]

    rows, errors, ids = [], [], set()
    for ln in open(a.curated, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if not ln or ln.startswith("#"):
            continue
        p = ln.split("@@")
        if len(p) != 10:
            errors.append(f"bad field count {len(p)}: {ln[:60]}")
            continue
        cid, f, line, frag, clause, kind, also, mark, ev, note = p
        if cid in ids:
            errors.append(f"duplicate id {cid}")
        ids.add(cid)
        if mark not in MARKS:
            errors.append(f"{cid}: bad marking {mark}")
        lo, hi = (line.split("-") + [line])[:2] if "-" in line else (line, line)
        lo, hi = int(lo), int(hi)
        text = lines_of(f)
        if hi > len(text):
            errors.append(f"{cid}: line {hi} beyond {f} ({len(text)})")
            continue
        joined = fold(" ".join(text[lo - 1:hi]))
        if fold(frag) not in joined:
            errors.append(f"{cid}: fragment not in {f}:{line}: {frag!r}")
        for ref in filter(None, also.split(";")):
            rf, rl = ref.rsplit(":", 1)
            if int(rl) > len(lines_of(rf)):
                errors.append(f"{cid}: also_in {ref} beyond file")
        rows.append([cid, f, line, clause, kind, also, mark, ev, note])

    if errors:
        print("ERRORS:")
        print("\n".join(errors))
        return 1
    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["id", "file", "line", "clause", "kind", "also_in", "marking", "evidence", "note"])
        w.writerows(rows)
    print("rows", len(rows))
    print("by marking", dict(sorted(Counter(r[6] for r in rows).items())))
    own, alls = set(), set()
    for r in rows:
        lo, hi = (r[2].split("-") + [r[2]])[:2] if "-" in r[2] else (r[2], r[2])
        for n in range(int(lo), int(hi) + 1):
            own.add((r[1], n))
            alls.add((r[1], n))
        for ref in filter(None, r[5].split(";")):
            rf, rl = ref.rsplit(":", 1)
            alls.add((rf, int(rl)))
    kit_own = {x for x in own if x[0] in KIT_OWN}
    print("distinct file lines cited as the clause's own line:", len(own),
          "(kit's ten own files:", len(kit_own), "; the five method files:", len(own) - len(kit_own), ")")
    print("distinct file lines incl. also_in:", len(alls))
    print("by file", dict(sorted(Counter(r[1] for r in rows).items())))
    if a.cand:
        n = sum(1 for _ in csv.reader(open(a.cand, encoding="utf-8"))) - 1
        print("candidate lines from extract_candidates.py:", n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
