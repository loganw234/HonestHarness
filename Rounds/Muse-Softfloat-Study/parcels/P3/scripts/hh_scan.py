"""Search HonestHarness rounds 1 and 2 for each proposal's failure and practice.

Round 1: Rounds/HonestHarness-R1/{CASE-STUDY,PLAN,AMENDMENT-1,harness-notes,TABLE}.md on main
  (git show at the SHA printed below), and the markdown files at the top of its archived
  ledger zip (round1-ledger.zip, copied from git show to <scratch>/P3/hh/ and read with zipfile).
Round 2: <repos>/honestharness-r2-ledger/ lead.md, AMENDMENT-1.md, README.md, P*.md, PA*.md,
  verifier-*.md (as files), and Rounds/HonestHarness-R2/PLAN.md on the branch round2.
Never opens keys/, briefs/, drafts/, reports/ or the stackdump in the round 2 ledger.

Writes data/hh_sources.csv and data/hh_candidates.csv.
Usage: python -I hh_scan.py --repos <repos> --scratch <scratch>
"""
import glob
import io
import json
import os
import re
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import args_roots, git, git_show, read_file, write_csv

HH_MAIN = "b69ed7613bdb655fb4b42acd1517b0b30631af7a"
HH_R2 = "8e392dd33b860a9eb8fd4baa4a0351e3e64be660"


def sources(ns):
    out = []
    for f in ["CASE-STUDY.md", "PLAN.md", "AMENDMENT-1.md", "harness-notes.md", "TABLE.md"]:
        out.append(("R1", "HH1:Rounds/HonestHarness-R1/" + f, git_show(ns.hh, HH_MAIN, "Rounds/HonestHarness-R1/" + f).splitlines()))
    zpath = os.path.join(ns.scratch, "P3", "hh", "round1-ledger.zip")
    os.makedirs(os.path.dirname(zpath), exist_ok=True)
    import subprocess
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    data = subprocess.run(["git", "-C", ns.hh, "show", HH_MAIN + ":Rounds/HonestHarness-R1/round1-ledger.zip"],
                          capture_output=True, env=env).stdout
    with open(zpath, "wb") as f:
        f.write(data)
    z = zipfile.ZipFile(io.BytesIO(data))
    for n in sorted(z.namelist()):
        parts = n.split("/")
        if len(parts) == 2 and n.endswith(".md"):
            out.append(("R1", "HH1ZIP:" + parts[1], z.read(n).decode("utf-8", "replace").splitlines()))
    r2 = os.path.join(ns.repos, "honestharness-r2-ledger")
    names = ["lead.md", "AMENDMENT-1.md", "README.md"] + sorted(
        os.path.basename(p) for p in glob.glob(os.path.join(r2, "*.md"))
        if re.match(r"(P\d|PA\d|verifier-).*\.md$", os.path.basename(p)))
    for n in names:
        out.append(("R2", "HH2:" + n, read_file(os.path.join(r2, n)).splitlines()))
    out.append(("R2", "HH2B:Rounds/HonestHarness-R2/PLAN.md", git_show(ns.hh, HH_R2, "Rounds/HonestHarness-R2/PLAN.md").splitlines()))
    return out


def main():
    ns = args_roots()
    q = json.load(open(os.path.join(ns.here, "hh_questions.json"), encoding="utf-8"))
    srcs = sources(ns)
    write_csv(os.path.join(ns.data, "hh_sources.csv"), ["round", "source", "lines"],
              [[r, s, len(l)] for r, s, l in srcs])
    cand = []
    for pid in sorted((k for k in q if k.startswith("P")), key=lambda x: int(x[1:])):
        for kind in ("failure", "practice"):
            rxs = [(s, re.compile(s, re.I)) for s in q[pid][kind]]
            for rnd, s, lines in srcs:
                for i, l in enumerate(lines, 1):
                    for st, rx in rxs:
                        if rx.search(l):
                            cand.append([pid, kind, rnd, s, i, st, l.strip()[:220]])
                            break
    write_csv(os.path.join(ns.data, "hh_candidates.csv"),
              ["proposal", "kind", "round", "source", "line", "stem", "text"], cand)
    print("HonestHarness main:", HH_MAIN[:7], "round2:", HH_R2[:7])
    print("sources:", len(srcs), "| lines:", sum(len(x[2]) for x in srcs), "| candidate lines:", len(cand))
    from collections import Counter
    print(dict(Counter((c[0]) for c in cand)))


main()
