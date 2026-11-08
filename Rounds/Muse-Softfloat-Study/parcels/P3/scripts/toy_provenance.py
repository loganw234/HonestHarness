"""P1 in the toy round: does each verifier report quote its copy's HEAD, and where?

Reads docs/metrics/plants.jsonl at the toy's 084f98b (git show). For each parcel,
the dispatch row gives copy_head and the verdict row gives verifier_report (a path
under <muse>/scratch/toy1 or toy2, which the plant rows name). For each report
file the script finds the first line that holds the copy's HEAD (full 40 hex, or
its first 7 characters) and says how far down the report that line is.
It does not read any key.

Writes data/toy_provenance.csv.
Usage: python -I toy_provenance.py --repos <repos> --scratch <scratch>
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import args_roots, git_show, read_file, write_csv, TOY_MAIN

ns = args_roots()
rows = [json.loads(l) for l in git_show(ns.toy, TOY_MAIN, "docs/metrics/plants.jsonl").splitlines() if l.strip()]
disp = {r["parcel"]: r for r in rows if r.get("status") == "dispatched"}
verd = {r["parcel"]: r for r in rows if r.get("status") == "verdict"}
out = []
for parcel in disp:
    head = disp[parcel]["copy_head"]
    rep = verd.get(parcel, {}).get("verifier_report", "")
    path = os.path.join(ns.muse, rep) if rep else ""
    status, first, total, form = "no report named", "", "", ""
    if rep and os.path.isfile(path):
        lines = read_file(path).splitlines()
        total = len(lines)
        status = "report holds no copy_head"
        for i, l in enumerate(lines, 1):
            if head in l:
                status, first, form = "quotes copy_head", i, "full 40"
                break
            if head[:7] in l:
                status, first, form = "quotes copy_head", i, "7-char prefix"
                break
    elif rep:
        status = "report file not found"
    out.append([parcel, rep, head[:7], status, first, form, total,
                disp[parcel].get("checked_by", "")])
write_csv(os.path.join(ns.data, "toy_provenance.csv"),
          ["parcel", "verifier_report", "copy_head_7", "result", "first_line_quoting_head", "form", "report_lines", "checked_by"], out)
from collections import Counter
print("dispatch rows:", len(disp), "| verdict rows:", len(verd))
print(Counter(r[3] for r in out))
fl = sorted(int(r[4]) for r in out if r[4] != "")
if fl:
    print("first line of the HEAD quote: min %d, median %d, max %d" % (fl[0], fl[len(fl) // 2], fl[-1]))
    print("within the first 15 lines:", sum(1 for x in fl if x <= 15), "of", len(fl))
