"""Check every cited line in data/marks.csv, then derive the marks by rule.

1. Each row that cites a source must quote text that is in that source's cited
   line (whitespace folded). Any miss is printed and the script exits 1.
2. Each clause's mark is the strongest of its rows; context clauses (named in
   clauses.json) are shown but not counted.
3. Each proposal's mark is derived: RULE (all counted clauses are rules),
   PARTIAL, CASE-ONLY, NEWER-ONLY or ABSENT.
4. The case report's label is set beside it.

Writes data/clause_marks.csv and data/proposal_marks.csv.
Usage: python -I check_marks.py --repos <repos> --scratch <scratch>
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import args_roots, read_csv, write_csv
from corpus import entries

ORDER = ["RULE-M", "RULE-K", "ADVICE", "PART", "CASE", "NEWER", "ADJACENT", "ABSENT"]
PRESENT = {"RULE-M", "RULE-K", "ADVICE", "PART"}


def fold(s):
    return " ".join(s.split())


def main():
    ns = args_roots()
    clauses = json.load(open(os.path.join(ns.here, "clauses.json"), encoding="utf-8"))
    context = set(clauses["_context"])
    marks = read_csv(os.path.join(ns.data, "marks.csv"))
    raw = {r["id"]: r for r in read_csv(os.path.join(ns.data, "proposals_raw.csv"))}
    ents, _ = entries(ns)
    lines = {e[0]: e[5].splitlines() for e in ents}
    bad = 0
    for m in marks:
        if m["mark"] not in ORDER:
            print("unknown mark", m)
            bad += 1
        if m["source_id"]:
            src = lines.get(m["source_id"])
            if src is None:
                print("no such source", m["source_id"])
                bad += 1
                continue
            n = int(m["line"])
            if not (1 <= n <= len(src)) or fold(m["quote"]) not in fold(src[n - 1]):
                print("QUOTE NOT IN LINE:", m["proposal"], m["clause"], m["source_id"], n, "|", m["quote"])
                bad += 1
            if len(m["quote"].split()) > 15:
                print("quote over 15 words:", m["proposal"], m["clause"])
                bad += 1
        elif m["mark"] not in ("ABSENT",):
            print("mark without a source:", m["proposal"], m["clause"], m["mark"])
            bad += 1
    # every clause has a row
    cm_rows, pm_rows = [], []
    for pid in sorted((k for k in clauses if re.fullmatch(r"P\d+", k)), key=lambda x: int(x[1:])):
        cmark = {}
        best = {}
        for cid in clauses[pid]["clauses"]:
            rows = [m for m in marks if m["proposal"] == pid and m["clause"] == cid]
            if not rows:
                print("clause with no row:", pid, cid)
                bad += 1
                continue
            rows.sort(key=lambda m: ORDER.index(m["mark"]))
            top = rows[0]
            mk = top["mark"] if top["mark"] != "ADJACENT" else "ABSENT"
            cmark[cid] = mk
            best[cid] = top
            cm_rows.append([pid, cid, "context" if "%s.%s" % (pid, cid) in context else "counted", mk,
                            "%s:%s" % (top["source_id"], top["line"]) if top["source_id"] else "",
                            ";".join(sorted({m["mark"] for m in rows})),
                            clauses[pid]["clauses"][cid]["desc"]])
        counted = {c: v for c, v in cmark.items() if "%s.%s" % (pid, c) not in context}
        vals = set(counted.values())
        if vals and vals <= {"RULE-M", "RULE-K"}:
            pm = "RULE" if "RULE-K" not in vals else "RULE (kit)"
        elif vals & PRESENT:
            pm = "PARTIAL"
        elif "CASE" in vals:
            pm = "CASE-ONLY"
        elif "NEWER" in vals:
            pm = "NEWER-ONLY"
        else:
            pm = "ABSENT"
        present = ",".join(sorted(c for c, v in counted.items() if v in PRESENT))
        case = ",".join(sorted(c for c, v in counted.items() if v == "CASE"))
        newer = ",".join(sorted(c for c, v in counted.items() if v == "NEWER"))
        absent = ",".join(sorted(c for c, v in counted.items() if v == "ABSENT"))
        base_present = any(cmark.get(c.split(".")[1]) in PRESENT | {"CASE"} for c in context if c.startswith(pid + "."))
        label = raw[pid]["case_report_label"]
        if label == "new":
            agrees = "agrees" if pm in ("ABSENT", "CASE-ONLY", "NEWER-ONLY") else "overstated: %s already present" % (present or "-")
        elif label in ("extension", "reinforcement", "adoption"):
            if pm == "ABSENT" and not base_present:
                agrees = "base not found in the texts"
            else:
                agrees = "has a base (clauses present: %s)" % (present or "context clause only")
        else:
            agrees = "unlabelled"
        pm_rows.append([pid, raw[pid]["group"], label, raw[pid]["label_text"], pm, present, case, newer, absent, agrees])
    write_csv(os.path.join(ns.data, "clause_marks.csv"),
              ["proposal", "clause", "role", "mark", "best_source", "marks_seen", "clause"], cm_rows)
    write_csv(os.path.join(ns.data, "proposal_marks.csv"),
              ["proposal", "group", "case_report_label", "case_report_label_text", "mark",
               "clauses_present", "clauses_case_only", "clauses_newer_only", "clauses_absent", "label_check"], pm_rows)
    from collections import Counter
    print("marks rows:", len(marks), "| cited lines checked:", sum(1 for m in marks if m["source_id"]), "| failures:", bad)
    print("proposal marks:", dict(Counter(r[4] for r in pm_rows)))
    for r in pm_rows:
        print(r[0], "|", r[2], "|", r[4], "| present:", r[5], "| case:", r[6], "| newer:", r[7], "| absent:", r[8], "|", r[9])
    sys.exit(1 if bad else 0)


main()
