"""Task 5: voided and redone attempts.

data/attempts_input.csv is my reading of the record. This script checks that each cited line of
<muse>/ledger/lead.md holds the phrase I rely on, checks the plants/usage/passes rows that tie
attempts to key hashes, and writes data/attempts.csv with those checks added.
"""
import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C


def main():
    a = C.args()
    lead = C.read_text(os.path.join(C.muse(a.repos), "ledger", "lead.md")).splitlines()
    plants = C.lib_jsonl(a.repos, "plants")
    usage = set(u["agent"] for u in C.lib_jsonl(a.repos, "usage"))
    passes = set(p["agent"] for p in C.lib_jsonl(a.repos, "passes"))
    by_name = collections.defaultdict(list)
    for r in plants:
        by_name[r["verifier"]].append(r)
    rows = []
    ok = 0
    for r in C.read_csv(os.path.join(C.DATA, "attempts_input.csv")):
        line = int(r["cite_line"])
        text = lead[line - 1] if 0 < line <= len(lead) else ""
        v = "yes" if r["cite_phrase"] in text else "NO"
        ok += v == "yes"
        rows.append([r["id"], r["kind"], r["work"], r["what_happened"], r["what_was_graded_again"], r["plant_rows_by_key"],
                     "<muse>/ledger/lead.md line %d" % line, v])
    C.write_csv(os.path.join(C.DATA, "attempts.csv"),
                ["id", "kind", "work", "what_happened", "what_was_graded_again", "plant_rows_by_key", "record_line", "cited_phrase_found_on_line"], rows)
    print("attempts:", len(rows), "| cited phrase found on its line:", ok)
    for name in ("verifier-psbench", "verifier-psbench2", "verifier-psbench2b", "verifier-w5exp2", "verifier-w6captions"):
        rs = by_name.get(name, [])
        print(" %-22s plant rows %d keys %s caught %d | usage row %s | passes row %s" % (
            name, len(rs), sorted(set(x["key_sha256"][:8] for x in rs)), sum(1 for x in rs if x["grade"] == "caught"),
            name in usage, name in passes))
    # RECORD lines for the bench attempts at b78af18
    rec = C.show(C.lib_repo(a.repos), C.LIB_SHA, "docs/RECORD.md").splitlines()
    for ln, ph in ((1390, "First verifier attempt void"), (1396, "verifier-psbench2b"), (890, "second-attempt verifier")):
        print(" RECORD.md@b78af18 line %d holds %r: %s" % (ln, ph, ph in rec[ln - 1]))


main()
