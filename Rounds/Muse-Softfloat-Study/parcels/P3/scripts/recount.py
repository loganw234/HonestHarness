"""A second route to the proposal marks, written without importing check_marks.py.

Reads data/marks.csv and scripts/clauses.json directly and re-derives, by a
different method (set arithmetic on clause marks, not a loop over strongest
rows), each proposal's mark and the count of proposals by mark. Compares them
with data/proposal_marks.csv and prints both.

Usage: python -I recount.py --repos <repos> --scratch <scratch>
"""
import csv
import json
import os
import sys
from collections import Counter, defaultdict

here = os.path.dirname(os.path.abspath(__file__))
data = os.path.normpath(os.path.join(here, "..", "data"))
cl = json.load(open(os.path.join(here, "clauses.json"), encoding="utf-8"))
ctx = set(cl["_context"])
rank = {"RULE-M": 0, "RULE-K": 1, "ADVICE": 2, "PART": 3, "CASE": 4, "NEWER": 5, "ADJACENT": 6, "ABSENT": 7}
by = defaultdict(lambda: defaultdict(set))
for r in csv.DictReader(open(os.path.join(data, "marks.csv"), encoding="utf-8")):
    by[r["proposal"]][r["clause"]].add(r["mark"])
mine = {}
for p in by:
    kinds = set()
    for c, ms in by[p].items():
        if "%s.%s" % (p, c) in ctx:
            continue
        kinds.add(min(ms, key=lambda m: rank[m]) if min(rank[m] for m in ms) < 6 else "ABSENT")
    rules = {"RULE-M", "RULE-K"}
    if kinds <= rules:
        mine[p] = "RULE" if kinds == {"RULE-M"} else "RULE (kit)"
    elif kinds & {"RULE-M", "RULE-K", "ADVICE", "PART"}:
        mine[p] = "PARTIAL"
    elif "CASE" in kinds:
        mine[p] = "CASE-ONLY"
    elif "NEWER" in kinds:
        mine[p] = "NEWER-ONLY"
    else:
        mine[p] = "ABSENT"
first = {r["proposal"]: r["mark"] for r in csv.DictReader(open(os.path.join(data, "proposal_marks.csv"), encoding="utf-8"))}
diff = [p for p in first if first[p] != mine.get(p)]
print("proposals:", len(mine), "| first route:", dict(Counter(first.values())), "| second route:", dict(Counter(mine.values())))
print("disagreements:", diff)
sys.exit(1 if diff else 0)
