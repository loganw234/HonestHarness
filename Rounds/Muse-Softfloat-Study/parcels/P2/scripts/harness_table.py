"""Task 1, harness fallbacks: join the kit's HARNESS.md table, the round's filled docs/HARNESS.md
(library b78af18) and the curated verdicts into data/harness.csv.

usage: python -I harness_table.py --repos <repos> --curated scripts/harness_curated.txt --out data/harness.csv
"""
import argparse, csv, os, subprocess, sys

LIB = "b78af1801d3e2bd123fed82d933414af661a9e9a"


def table_rows(text):
    rows = []
    for ln in text.splitlines():
        if ln.startswith("|") and not ln.startswith("|---") and "mechanism" not in ln.split("|")[1]:
            rows.append([c.strip() for c in ln.strip().strip("|").split("|")])
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repos", required=True)
    ap.add_argument("--curated", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    kit = open(os.path.join(a.repos, "Muse-Softfloat", "softfloat-bootstrap-kit", "HARNESS.md"), encoding="utf-8").read()
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    filled = subprocess.run(["git", "-C", os.path.join(a.repos, "Muse-Softfloat", "muse-softfloat"), "show",
                             f"{LIB}:docs/HARNESS.md"], capture_output=True, env=env, check=True).stdout.decode("utf-8")
    kr, fr = table_rows(kit), table_rows(filled)
    assert len(kr) == 14 and len(fr) == 14, (len(kr), len(fr))
    cur = {}
    for ln in open(a.curated, encoding="utf-8"):
        if ln.startswith("#") or not ln.strip():
            continue
        n, v, e = ln.rstrip("\n").split("@@")
        cur[int(n)] = (v, e)
    assert sorted(cur) == list(range(1, 15))
    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["row", "mechanism", "kit_fallback", "round_answer", "round_used", "verdict", "evidence"])
        for i, (k, f) in enumerate(zip(kr, fr), 1):
            assert k[0].startswith(f[0][:15]) or f[0].startswith(k[0][:15]), (i, k[0], f[0])  # same mechanism; the filled table shortens some names
            w.writerow([i, k[0], k[2], f[1], f[2], cur[i][0], cur[i][1]])
    from collections import Counter
    print("rows", len(kr))
    print(dict(Counter(cur[i][0] for i in cur)))


if __name__ == "__main__":
    sys.exit(main())
