"""Join the four tables into data/proposals.csv: one row per proposal.

Reads data/proposal_marks.csv (made by check_marks.py), kit_use.csv,
toy_practice.csv and honestharness_rounds.csv. Run check_marks.py first.

Usage: python -I assemble.py --repos <repos> --scratch <scratch>
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import args_roots, read_csv, write_csv

ns = args_roots()
pm = read_csv(os.path.join(ns.data, "proposal_marks.csv"))
cm = read_csv(os.path.join(ns.data, "clause_marks.csv"))
ku = read_csv(os.path.join(ns.data, "kit_use.csv"))
toy = {r["proposal"]: r for r in read_csv(os.path.join(ns.data, "toy_practice.csv"))}
hh = {r["proposal"]: r for r in read_csv(os.path.join(ns.data, "honestharness_rounds.csv"))}
out = []
for r in pm:
    pid = r["proposal"]
    best = "; ".join("%s=%s %s" % (c["clause"], c["mark"], c["best_source"])
                     for c in cm if c["proposal"] == pid and c["role"] == "counted" and c["best_source"])
    use = "; ".join("%s %s" % (k["clause"], k["round_use"]) for k in ku if k["proposal"] == pid) or "n/a (no kit clause)"
    out.append([pid, r["group"], r["case_report_label"], r["mark"], r["label_check"],
                r["clauses_present"], r["clauses_case_only"], r["clauses_newer_only"], r["clauses_absent"],
                best, use, toy[pid]["toy_practice"], hh[pid]["hh_mark"]])
write_csv(os.path.join(ns.data, "proposals.csv"),
          ["proposal", "group", "case_report_label", "mark_at_the_pins", "label_check",
           "clauses_present", "clauses_case_only", "clauses_newer_only", "clauses_absent",
           "strongest_source_per_clause", "round_use_of_kit_clauses", "toy_round", "honestharness_rounds"], out)
for o in out:
    print(o[0], "|", o[2], "|", o[3], "|", o[10], "|", o[11], "|", o[12])
