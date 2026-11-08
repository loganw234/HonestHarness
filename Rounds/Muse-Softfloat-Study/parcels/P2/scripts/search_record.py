"""Task 2, step 2: search the round's own record for each finding's terms.

usage: python -I search_record.py --repos <repos> --terms scripts/escape_terms.txt --out data/escape_search.csv [--max N]
--max N keeps at most N hits per finding in first_hits (default 100, enough for every finding here). The script sets
its own output encoding to UTF-8, so it needs no -X utf8 or PYTHONIOENCODING.
terms file: id@@regex (case-insensitive; the regex is mine, taken from the finding's own words).

Corpus (the round's own verification and record, before the audits it is compared with):
  - <muse>/ledger/lead.md, lines before the heading "full audit sweep" (the full audit's dispatch)
  - docs/RECORD.md at a49991f (the full audit's tree)
  - <muse>/ledger/verifier-*.md and parcel-*.md and rechecker*.md (the round's verifiers and parcels), except the
    post-audit edge-case parcel (psedge)
  - <muse>/scratch/verifier-*/report.md and scratch/rechecker*/report.md
Not in the corpus: any auditor file (auditor-*, scratch/audit-*), anything fenced.
Each hit is file:line. A hit is a lead for me to read, not a verdict.
"""
import argparse, csv, glob, os, re, subprocess, sys

LIB_AUDIT = "a49991f2603f2ebd55f6287be1d691de78cf5c57"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--repos", required=True)
    ap.add_argument("--terms", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--max", type=int, default=100)
    a = ap.parse_args()
    muse = os.path.join(a.repos, "Muse-Softfloat")
    corpus = []  # (label, [lines])

    lead = open(os.path.join(muse, "ledger", "lead.md"), encoding="utf-8").read().splitlines()
    cut = next(i for i, ln in enumerate(lead) if ln.startswith("## ") and "full audit sweep" in ln)
    corpus.append(("ledger/lead.md", lead[:cut]))
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    rec = subprocess.run(["git", "-C", os.path.join(muse, "muse-softfloat"), "show", f"{LIB_AUDIT}:docs/RECORD.md"],
                         capture_output=True, env=env, check=True).stdout.decode("utf-8").splitlines()
    corpus.append(("docs/RECORD.md@a49991f", rec))
    pats = ["ledger/verifier-*.md", "ledger/parcel-*.md", "ledger/rechecker*.md",
            "scratch/verifier-*/report.md", "scratch/rechecker*/report.md", "ledger/study-*.md"]
    nfiles = 0
    for pat in pats:
        for f in sorted(glob.glob(os.path.join(muse, pat))):
            rel = os.path.relpath(f, muse).replace(os.sep, "/")
            if "psedge" in rel:
                continue
            corpus.append((rel, open(f, encoding="utf-8", errors="replace").read().splitlines()))
            nfiles += 1
    print("lead.md lines searched:", cut, "of", len(lead), "; RECORD lines:", len(rec), "; other files:", nfiles)

    out = []
    for ln in open(a.terms, encoding="utf-8"):
        if ln.startswith("#") or not ln.strip():
            continue
        fid, rx = ln.rstrip("\n").split("@@", 1)
        cre = re.compile(rx, re.I)
        hits = []
        for label, lines in corpus:
            for i, t in enumerate(lines, 1):
                if cre.search(t):
                    hits.append((label, i, re.sub(r"[A-Za-z]:[/\][^\s]*", "<path>", re.sub(r"\s+", " ", t.strip()))[:110]))
        out.append([fid, rx, len(hits), " || ".join(f"{h[0]}:{h[1]} {h[2]}" for h in hits[:a.max])])
    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["id", "regex", "hit_count", "first_hits"])
        w.writerows(out)
    for r in out:
        print(r[0], r[2], r[3][:300])


if __name__ == "__main__":
    sys.exit(main())
