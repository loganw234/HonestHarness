"""Task 4: check the passes rows' a, b and sent_back against what I found.

Inputs: passes.jsonl and plants.jsonl at b78af18, data/findings.csv (the non-plant findings I
enumerated, by hand, from the verifiers' ledgers/reports and the lead's grading lines), and
data/sent_back_evidence.csv (my reading of which sent_back rows were followed by a revision).
Writes data/pass_counts.csv. For each verifier pass: the record's a+b; plants caught; my
enumerated genuine findings; and whether a+b equals plant-linked findings + genuine findings.
"""
import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C


def main():
    a = C.args()
    passes = C.lib_jsonl(a.repos, "passes")
    plants = C.lib_jsonl(a.repos, "plants")
    fnd = C.read_csv(os.path.join(C.DATA, "findings.csv"))
    ev = {int(r["passes_line"]): r for r in C.read_csv(os.path.join(C.DATA, "sent_back_evidence.csv"))}
    gen = collections.Counter(int(r["pass_row"]) for r in fnd if r["pass_row"] and r["kit_class"] in ("a", "b"))
    caught = collections.Counter(r["verifier"] for r in plants if r["grade"] == "caught")
    ntot = collections.Counter(r["verifier"] for r in plants)
    rows = []
    for i, p in enumerate(passes, 1):
        if p["role"] != "verifier":
            continue
        c = caught.get(p["agent"], 0)
        g = gen.get(i, 0)
        implied = p["a"] + p["b"] - g
        # a pass is "explained" when the record's a+b = genuine findings + findings linked to caught plants;
        # for plant passes where several plants share a finding or one plant gave two, the difference is listed.
        status = "a+b - genuine = caught plants" if implied == c else "a+b - genuine = %d vs caught %d" % (implied, c)
        if ntot.get(p["agent"], 0) == 0:
            status = "no plants; all findings genuine" if g == p["a"] + p["b"] else "no plants; enumerated %d of %d" % (g, p["a"] + p["b"])
        rows.append([i, p["agent"], p["wave"], p["a"], p["b"], p["a"] + p["b"], p["verdict"], p["sent_back"], c, ntot.get(p["agent"], 0), g, implied, status])
    C.write_csv(os.path.join(C.DATA, "pass_counts.csv"),
                ["passes_line", "agent", "wave", "a", "b", "a_plus_b", "verdict", "sent_back", "plants_caught", "plants_total",
                 "genuine_findings_enumerated", "a_plus_b_minus_genuine", "check"], rows)
    n_ok = sum(1 for r in rows if r[12] in ("a+b - genuine = caught plants", "no plants; all findings genuine"))
    print("verifier passes:", len(rows), "| record a+b explained exactly:", n_ok)
    for r in rows:
        if r[12] not in ("a+b - genuine = caught plants", "no plants; all findings genuine") and (r[3] + r[4] > 0):
            print("  line", r[0], r[1], "a/b", r[3], r[4], "caught", r[8], "genuine enumerated", r[10], "->", r[12])
    print("genuine findings enumerated:", len(fnd), "of which with a passes row:", sum(1 for r in fnd if r["pass_row"]))
    sb = [(i, p) for i, p in enumerate(passes, 1) if p["role"] == "verifier" and p.get("sent_back")]
    yes = [i for i, _ in sb if ev[i]["revision_followed"] == "yes"]
    no = [i for i, _ in sb if ev[i]["revision_followed"] == "no"]
    print("sent_back true rows:", len(sb), "| revision followed (my reading):", len(yes), yes, "| not followed:", len(no), no)
    print("erratum: 8 of 15 not revision rounds, so 7 proven; my reading differs by", len(yes) - 7)


main()
