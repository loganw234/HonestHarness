"""Task 4: join the curated verdicts with the measured values into data/case_report_claims.csv.

usage: python -I build_case_report.py --curated scripts/case_report_curated.txt --measures data/case_report_measures.csv --out data/case_report_claims.csv
"""
import argparse, csv, sys
from collections import Counter

def main():
    ap = argparse.ArgumentParser()
    for k in ("curated", "measures", "out"):
        ap.add_argument("--" + k, required=True)
    a = ap.parse_args()
    meas = {r["key"]: r["value"] for r in csv.DictReader(open(a.measures, encoding="utf-8"))}
    rows, errs = [], []
    for ln in open(a.curated, encoding="utf-8"):
        if ln.startswith("#") or not ln.strip():
            continue
        p = ln.rstrip("\n").split("@@")
        assert len(p) == 7, (len(p), p[0])
        cid, obs, claim, keys, src, res, why = p
        vals = []
        for k in filter(None, keys.split(";")):
            if k not in meas:
                errs.append((cid, k))
            else:
                vals.append(f"{k} = {meas[k]}")
        if res not in ("holds", "partly", "doesn't", "unverifiable"):
            errs.append((cid, "result " + res))
        rows.append([cid, obs, claim, " | ".join(vals), src, res, why])
    if errs:
        print("ERRORS", errs)
        return 1
    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "observation", "claim", "measured", "source", "result", "reason"])
        w.writerows(rows)
    print("claims", len(rows), dict(Counter(r[5] for r in rows)))
    obs = Counter(r[1] for r in rows)
    print("claims per observation (0 = setting and timeline, 18 = cost table):", dict(sorted(obs.items(), key=lambda x: int(x[0]))))
    print("observations 1-17 with at least one claim:", sum(1 for k in obs if 1 <= int(k) <= 17))
    return 0

if __name__ == "__main__":
    sys.exit(main())
