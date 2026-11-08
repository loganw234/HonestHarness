"""Task 2, step 1: list the findings of the full audit's consolidated report.

usage: python -I parse_full_audit.py --repos <repos> --out data/full_audit_findings.csv
Reads <muse>/scratch/audit-full/REPORT.md (the Muse auditors' report; the Claude audits are fenced and not read)
and, for a count only, the Findings section of each area file beside it.
Ids: M1-M4 majors, S5-S6 major-suspected, N<n> minors in report order, T<n> nits in report order.
"""
import argparse, csv, os, re, sys

AREA = ["library-core", "board-demo-examples", "docs", "metrics", "repo-hygiene", "site-video", "tests-gates-ci"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repos", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    base = os.path.join(a.repos, "Muse-Softfloat", "scratch", "audit-full")
    lines = open(os.path.join(base, "REPORT.md"), encoding="utf-8").read().splitlines()
    sec = None
    items = []  # (section, start_line, text)
    cur = None
    area = ""
    for i, ln in enumerate(lines, 1):
        if ln.startswith("## "):
            sec = ln[3:].strip()
            cur = None
            continue
        if sec is None:
            continue
        if sec.startswith("Major (lead-verified)") or sec.startswith("Major-suspected"):
            m = re.match(r"^(\d+)\. (.*)", ln)
            if m:
                cur = [sec, i, m.group(1), m.group(2)]
                items.append(cur)
            elif cur and ln.startswith("   "):
                cur[3] += " " + ln.strip()
            elif not ln.strip():
                cur = None
        elif sec.startswith("Minor") or sec.startswith("Nits"):
            if re.match(r"^[A-Za-z/-]+.*:$", ln) and not ln.startswith("-"):
                area = ln.rstrip(":")
                cur = None
                continue
            if ln.startswith("- "):
                cur = [sec, i, area, ln[2:]]
                items.append(cur)
            elif cur and ln.startswith("  "):
                cur[3] += " " + ln.strip()
            elif not ln.strip():
                cur = None
    rows = []
    nm = nn = nt = 0
    for sec, i, tag, text in items:
        if sec.startswith("Major (lead"):
            fid, sev = f"M{tag}", "major (lead-verified)"
        elif sec.startswith("Major-suspected"):
            fid, sev = f"S{tag}", "major-suspected"
        elif sec.startswith("Minor"):
            nn += 1
            fid, sev = f"N{nn}", "minor"
        else:
            nt += 1
            fid, sev = f"T{nt}", "nit"
        rows.append([fid, sev, "audit-full/REPORT.md", i, tag if sev == "minor" else "", re.sub(r"\s+", " ", text).strip()])
    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "severity", "source", "line", "area", "text"])
        w.writerows(rows)
    from collections import Counter
    print("findings in REPORT.md:", len(rows), dict(Counter(r[1] for r in rows)))
    # area files: count top-level finding bullets/numbered items under their Findings heading
    for f in AREA:
        t = open(os.path.join(base, f + ".md"), encoding="utf-8").read().splitlines()
        on = False
        n = 0
        for ln in t:
            if ln.startswith("## Findings"):
                on = True
                continue
            if on and ln.startswith("## "):
                break
            if on and re.match(r"^(\d+\.|- ) ?", ln) and not ln.startswith("  "):
                n += 1
        print("area file", f, "top-level finding items:", n)
    for r in rows:
        print(r[0], r[1], r[3], r[5][:90])


if __name__ == "__main__":
    sys.exit(main())
