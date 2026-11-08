"""Task 3: the lead's errors. Joins corrections.jsonl (library b78af18), my judgements, and git ancestry.

usage: python -I build_lead_errors.py --repos <repos> --judge scripts/corrections_judgement.txt \
          --other scripts/lead_errors_other.txt --out data/lead_errors.csv
Git facts (read-only, GIT_OPTIONAL_LOCKS=0): whether a commit named as "introduced" or "fixed" is an ancestor of
main (b78af18) and of the seal (751d1d6).
"""
import argparse, csv, json, os, subprocess, sys
from collections import Counter

MAIN = "b78af1801d3e2bd123fed82d933414af661a9e9a"
SEAL = "751d1d6"

def main():
    ap = argparse.ArgumentParser()
    for k in ("repos", "judge", "other", "out"):
        ap.add_argument("--" + k, required=True)
    a = ap.parse_args()
    lib = os.path.join(a.repos, "Muse-Softfloat", "muse-softfloat")
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")

    def git(*args):
        return subprocess.run(["git", "-C", lib, *args], capture_output=True, env=env)

    def anc(sha, tip):
        if not sha:
            return ""
        if git("cat-file", "-e", sha + "^{commit}").returncode != 0:
            return "missing"
        return "yes" if git("merge-base", "--is-ancestor", sha, tip).returncode == 0 else "no"

    rows = []
    corr = git("show", f"{MAIN}:docs/metrics/corrections.jsonl").stdout.decode("utf-8").splitlines()
    judge = {}
    for ln in open(a.judge, encoding="utf-8"):
        if ln.startswith("#") or not ln.strip():
            continue
        p = ln.rstrip("\n").split("@@")
        assert len(p) == 7, p
        judge[int(p[0])] = p
    assert len(corr) == len(judge) == 24, (len(corr), len(judge))
    for n, ln in enumerate(corr, 1):
        d = json.loads(ln)
        j = judge[n]
        rows.append([f"CJ{n:02d}", f"corrections.jsonl:{n}", d["text"], j[1], d["by"], d["at"], j[2], j[3], j[4], j[5], j[6]])
    for ln in open(a.other, encoding="utf-8"):
        if ln.startswith("#") or not ln.strip():
            continue
        p = ln.rstrip("\n").split("@@")
        assert len(p) == 11, (len(p), p[0])
        rows.append([p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9], p[10]])
    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "source", "what", "owner", "caught_by", "caught_at", "introduced", "fixed",
                    "introduced_ancestor_of_main", "fixed_ancestor_of_seal", "fixed_ancestor_of_main",
                    "reached_main", "reached_seal", "note"])
        for r in rows:
            w.writerow([r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], anc(r[6], MAIN), anc(r[7], SEAL), anc(r[7], MAIN), r[8], r[9], r[10]])
    print("rows", len(rows))
    cj = [r for r in rows if r[0].startswith("CJ")]
    print("corrections rows by owner:", dict(Counter(r[3].split(" (")[0].split(",")[0] for r in cj)))
    print("corrections rows whose owner is a brief of the lead:", sum(1 for r in cj if r[3] == "lead (brief)"))
    print("other rows:", len(rows) - len(cj), "owners:", dict(Counter(r[3].split(" (")[0] for r in rows if not r[0].startswith("CJ"))))
    bad = [(r[0], r[6], r[7]) for r in rows for s in (r[6], r[7]) if s and git("cat-file", "-e", s + "^{commit}").returncode != 0]
    print("named commits missing from the library:", bad)

if __name__ == "__main__":
    sys.exit(main())
