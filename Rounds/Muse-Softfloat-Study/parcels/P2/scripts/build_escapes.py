"""Task 2, step 3: join the parsed full-audit findings, my record search, and my curated judgements.

usage: python -I build_escapes.py --findings data/full_audit_findings.csv --search data/escape_search.csv \
         --curated scripts/escapes_curated.txt --slips scripts/adherence_slips.txt --out data/escapes.csv
Checks every full-audit finding has a curated row, and prints the tallies the analysis quotes.
"""
import argparse, csv, sys
from collections import Counter

def read_curated(path, nfields):
    out = {}
    for ln in open(path, encoding="utf-8"):
        if ln.startswith("#") or not ln.strip():
            continue
        p = ln.rstrip("\n").split("@@")
        assert len(p) == nfields, (len(p), ln[:50])
        out[p[0]] = p
    return out

def main():
    ap = argparse.ArgumentParser()
    for k in ("findings", "search", "curated", "slips", "out"):
        ap.add_argument("--" + k, required=True)
    a = ap.parse_args()
    finds = list(csv.DictReader(open(a.findings, encoding="utf-8")))
    srch = {r["id"]: r for r in csv.DictReader(open(a.search, encoding="utf-8"))}
    cur = read_curated(a.curated, 7)
    slips = read_curated(a.slips, 10)
    assert {f["id"] for f in finds} == set(cur), ({f["id"] for f in finds} ^ set(cur))
    rows = []
    for f in finds:
        c = cur[f["id"]]
        own = c[1]
        rows.append([f["id"], "full audit", f["severity"], f["source"] + ":" + f["line"], f["text"][:160], srch[f["id"]]["hit_count"],
                     own, "yes" if own in ("not-raised", "examined-passed") else "no", c[2], c[3], c[4], c[5], c[6]])
    for sid, s in slips.items():
        own = s[4]
        rows.append([sid, "adherence audit " + s[1], "slip", "audit report line %s" % s[2], s[3], "", own,
                     "yes" if own in ("not-raised", "examined-passed") else "no", s[5], s[6], s[7], s[8], s[9]])
    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["id", "from", "severity", "source", "finding", "search_hits", "own_verification", "escape", "evidence",
                    "earlier_audit", "failure_family", "mechanism", "why_not_caught"])
        w.writerows(rows)
    print("rows", len(rows))
    for src in ("full audit", "adherence audit A2", "adherence audit AF", "adherence audit AS"):
        sub = [r for r in rows if r[1] == src]
        print(src, len(sub), dict(Counter(r[6] for r in sub)), "escapes:", sum(1 for r in sub if r[7] == "yes"))
    fa = [r for r in rows if r[1] == "full audit"]
    for sev in ("major (lead-verified)", "major-suspected", "minor", "nit"):
        sub = [r for r in fa if r[2] == sev]
        print(" ", sev, len(sub), dict(Counter(r[6] for r in sub)))
    print("full-audit escapes by family:", dict(Counter(r[10].split()[0] for r in fa if r[7] == "yes")))
    print("zero-hit findings that are not-raised:", sum(1 for r in fa if r[6] == "not-raised" and r[5] == "0"))

if __name__ == "__main__":
    sys.exit(main())
