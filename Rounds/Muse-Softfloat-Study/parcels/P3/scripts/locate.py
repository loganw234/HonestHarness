"""Search the corpus with scripts/clauses.json stems.

Writes data/candidates.csv (every matching line, with the clause and stem) and
data/windows.csv (windows of 12 lines in which two or more clauses of one
proposal match, ranked, to be read by a person). The search finds lines; it
does not mark them.

Usage: python -I locate.py --repos <repos> --scratch <scratch>
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import args_roots, write_csv
from corpus import entries

W = 12


def load_corpus(ns):
    ents, _ = entries(ns)
    return [(sid, tier, commit, path, text.splitlines()) for sid, tier, src, commit, path, text in ents]


def main():
    ns = args_roots()
    clauses = json.load(open(os.path.join(ns.here, "clauses.json"), encoding="utf-8"))
    corpus = load_corpus(ns)
    cand = []
    wins = []
    neg = []
    for pid in sorted((k for k in clauses if k.startswith("P")), key=lambda x: int(x[1:])):
        compiled = {}
        for cid, c in clauses[pid]["clauses"].items():
            compiled[cid] = [(s, re.compile(s, re.I)) for s in c["stems"]]
        hits_by_src = {}
        per_clause_pin = {cid: 0 for cid in compiled}
        for sid, tier, commit, path, lines in corpus:
            hits = {}
            for i, l in enumerate(lines, 1):
                for cid, stems in compiled.items():
                    for s, rx in stems:
                        if rx.search(l):
                            cand.append([pid, cid, tier, sid, commit, i, s, l.strip()[:220]])
                            hits.setdefault(i, set()).add(cid)
                            if tier in "MC":
                                per_clause_pin[cid] += 1
                            break
            hits_by_src[sid] = (tier, commit, hits, lines)
        for cid in compiled:
            neg.append([pid, cid, per_clause_pin[cid]])
        # windows
        for sid, (tier, commit, hits, lines) in hits_by_src.items():
            n = len(lines)
            best = []
            for a in range(1, max(2, n - W + 2)):
                cs = set()
                for i in range(a, min(n, a + W - 1) + 1):
                    cs |= hits.get(i, set())
                if len(cs) >= 2:
                    best.append((len(cs), a, sorted(cs)))
            # merge overlapping windows, keep the best score of each cluster
            best.sort(key=lambda x: x[1])
            merged = []
            for sc, a, cs in best:
                if merged and a <= merged[-1][2] + W:
                    if sc > merged[-1][0]:
                        merged[-1][0] = sc
                        merged[-1][3] = cs
                    merged[-1][2] = a
                else:
                    merged.append([sc, a, a, cs])
            for sc, a0, a1, cs in merged:
                wins.append([pid, sc, tier, sid, commit, a0, min(n, a1 + W - 1), "+".join(cs)])
    write_csv(os.path.join(ns.data, "candidates.csv"),
              ["proposal", "clause", "tier", "source_id", "commit", "line", "stem", "text"], cand)
    wins.sort(key=lambda r: (int(r[0][1:]), -r[1], {"M": 0, "K": 1, "C": 2, "N": 3}[r[2]], r[3], r[5]))
    write_csv(os.path.join(ns.data, "windows.csv"),
              ["proposal", "clauses_hit", "tier", "source_id", "commit", "from_line", "to_line", "clauses"], wins)
    write_csv(os.path.join(ns.data, "negative_searches.csv"),
              ["proposal", "clause", "matching_lines_in_method_and_case_files_at_pins"], neg)
    print("candidate lines:", len(cand), "| windows:", len(wins))
    print("clauses with zero matching lines in method+case files:", [(r[0], r[1]) for r in neg if r[2] == 0])


if __name__ == "__main__":
    main()
