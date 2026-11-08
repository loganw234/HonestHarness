"""The methods' newer commits: everything reachable from a local ref and not from the pin.

Reads local refs only (git rev-list --all, never a fetch). For each commit above
the pin, lists the files changed; then searches every text file those commits
add or change with scripts/clauses.json and writes the hits.

Writes data/newer_refs.csv and data/newer_candidates.csv.
Usage: python -I newer.py --repos <repos> --scratch <scratch>
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import args_roots, git, write_csv, PR_PIN, HF_PIN

ns = args_roots()
clauses = json.load(open(os.path.join(ns.here, "clauses.json"), encoding="utf-8"))
refs_rows = []
cand = []
for name, repo, pin in (("ParcelRound", ns.pr, PR_PIN), ("HonestFramework", ns.hf, HF_PIN)):
    tips = git(repo, "rev-list", "--all", "--not", pin).split()
    heads = git(repo, "branch", "-a", "--format=%(refname:short) %(objectname:short)").splitlines()
    print(name, "| commits reachable from a local ref and not from the pin:", len(tips),
          "| local refs:", len(heads))
    changed_files = {}
    for c in tips:
        meta = git(repo, "log", "-1", "--format=%h|%ad|%s", "--date=short", c).strip()
        files = [f for f in git(repo, "diff", "--name-only", c + "^", c).split() if f]
        isanc = "no"
        refs_rows.append([name, meta.split("|")[0], meta.split("|")[1], meta.split("|", 2)[2], ";".join(files)])
        for f in files:
            changed_files[f] = c
    # search the text files the newer commits changed, at the newest such commit
    for f, c in sorted(changed_files.items()):
        if not f.lower().endswith((".md", ".txt", ".py", ".sh")):
            continue
        try:
            text = git(repo, "show", "%s:%s" % (c, f))
        except RuntimeError:
            continue
        lines = text.splitlines()
        for pid in sorted((k for k in clauses if k.startswith("P")), key=lambda x: int(x[1:])):
            for cid, cl in clauses[pid]["clauses"].items():
                for s in cl["stems"]:
                    rx = re.compile(s, re.I)
                    for i, l in enumerate(lines, 1):
                        if rx.search(l):
                            cand.append([name, pid, cid, f, c, i, s, l.strip()[:200]])
                            break
write_csv(os.path.join(ns.data, "newer_refs.csv"),
          ["repo", "commit", "date", "subject", "files_changed"], refs_rows)
write_csv(os.path.join(ns.data, "newer_candidates.csv"),
          ["repo", "proposal", "clause", "path", "commit", "first_matching_line", "stem", "text"], cand)
print("newer_refs rows:", len(refs_rows), "| newer_candidates rows (first line per stem):", len(cand))
for r in refs_rows:
    print(r[0], r[1], r[2], r[4])
