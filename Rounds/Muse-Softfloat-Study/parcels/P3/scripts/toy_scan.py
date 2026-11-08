"""Search the toy round's record with scripts/toy_questions.json.

Sources, read-only:
  TOY:docs/RECORD.md, WAVE-T1.md, WAVE-T2.md, TOY-0.md, metrics/README.md   at the toy's 084f98b (git show)
  MUSE:ledger/lead.md from line 889 to the end                               (file)
  TOYMSG:<scratch/toy1|toy2>/msg-plant-*.txt                                 (files the toy's plants.jsonl names:
      the lead's plant-dispatch messages, which are the toy verifiers' briefs)
Never opens <muse>/scratch/lead/ or any 'plants' key folder.

Writes data/toy_candidates.csv and data/toy_sources.csv (the file list with line counts).
Usage: python -I toy_scan.py --repos <repos> --scratch <scratch>
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import args_roots, git_show, read_file, write_csv, TOY_MAIN, sha256_text


def sources(ns):
    out = []
    for f in ["docs/RECORD.md", "docs/WAVE-T1.md", "docs/WAVE-T2.md", "docs/TOY-0.md", "docs/metrics/README.md"]:
        out.append(("TOY:" + f, git_show(ns.toy, TOY_MAIN, f).splitlines(), 1))
    lead = read_file(os.path.join(ns.muse, "ledger", "lead.md")).splitlines()
    out.append(("MUSE:ledger/lead.md", lead[888:], 889))
    for d in ("toy1", "toy2"):
        for p in sorted(glob.glob(os.path.join(ns.muse, "scratch", d, "msg-*plant*.txt"))):
            rel = "TOYMSG:scratch/%s/%s" % (d, os.path.basename(p))
            out.append((rel, read_file(p).splitlines(), 1))
    return out


def main():
    ns = args_roots()
    q = json.load(open(os.path.join(ns.here, "toy_questions.json"), encoding="utf-8"))
    srcs = sources(ns)
    write_csv(os.path.join(ns.data, "toy_sources.csv"), ["source", "first_line", "lines"],
              [[s, first, len(lines)] for s, lines, first in srcs])
    cand = []
    for pid in sorted((k for k in q if k.startswith("P")), key=lambda x: int(x[1:])):
        rxs = [(s, re.compile(s, re.I)) for s in q[pid]["stems"]]
        for s, lines, first in srcs:
            for i, l in enumerate(lines):
                for st, rx in rxs:
                    if rx.search(l):
                        cand.append([pid, s, first + i, st, l.strip()[:200]])
                        break
    write_csv(os.path.join(ns.data, "toy_candidates.csv"),
              ["proposal", "source", "line", "stem", "text"], cand)
    print("toy sources:", len(srcs), "| lines:", sum(len(x[1]) for x in srcs), "| candidate lines:", len(cand))


main()
