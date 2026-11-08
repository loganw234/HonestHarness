"""Task 1, step 1: list candidate clause lines from the kit's 15 method texts.

usage: python -I extract_candidates.py --repos <repos> --out <path.csv>

It reads the kit as files and judges nothing: a candidate is any line with a
modal keyword, or a list item, or a bold lead-in. The curated list in
clauses_curated.tsv is made by hand from these (plus reading), and
check_clauses.py checks the curated list against the files.
"""
import argparse, csv, os, re, sys

FILES = [
    "START-HERE.md", "WORKFLOW.md", "ROLES.md", "OWNER.md", "AGENTS.md",
    "CLEAN-ROOM.md", "METRICS.md", "HARNESS.md", "BOARD.md", "PROJECT.md",
    "method/parcelround/METHOD.md", "method/parcelround/ADOPTION.md",
    "method/honest/METHOD.md", "method/honest/ADOPTING.md",
    "method/honest/WITH-PARCELROUND.md",
]
MODAL = re.compile(r"\b(must|never|always|shall|do not|don't|required|only when|has to|have to|no agent)\b", re.I)
ITEM = re.compile(r"^\s*(\d+\.|[-*])\s+")
BOLD = re.compile(r"^\s*(\d+\.|[-*])?\s*\*\*[^*]+\*\*")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repos", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    kit = os.path.join(a.repos, "Muse-Softfloat", "softfloat-bootstrap-kit")
    rows = []
    per = {}
    for f in FILES:
        with open(os.path.join(kit, f), encoding="utf-8") as fh:
            lines = fh.read().splitlines()
        n = 0
        for i, ln in enumerate(lines, 1):
            kinds = []
            if MODAL.search(ln):
                kinds.append("modal")
            if ITEM.match(ln):
                kinds.append("item")
            if BOLD.match(ln):
                kinds.append("bold")
            if kinds:
                rows.append([f, i, "+".join(kinds), ln.strip()[:200]])
                n += 1
        per[f] = (len(lines), n)
    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["file", "line", "kinds", "text"])
        w.writerows(rows)
    tl = tc = 0
    for f, (nl, nc) in per.items():
        print(f"{f}\tlines={nl}\tcandidates={nc}")
        tl += nl
        tc += nc
    print(f"TOTAL\tlines={tl}\tcandidates={tc}")


if __name__ == "__main__":
    sys.exit(main())
