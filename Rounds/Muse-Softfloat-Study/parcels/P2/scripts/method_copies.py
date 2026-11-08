"""Compare the kit's method copies with their source repositories at the kit's pins.

usage: python -I method_copies.py --repos <repos> --out data/method_copies.csv
Reads the kit as files and the sources with git show (GIT_OPTIONAL_LOCKS=0).
"""
import argparse, csv, difflib, os, subprocess, sys

PINS = {
    "parcelround": ("ParcelRound", "f42242ecc1707a3d36c52e4b2a3b580ee2783e5b"),
    "honest": ("HonestFramework", "65447fd4d8253034fd6d206479c5a5371c623c60"),
}
FILES = {
    "parcelround": ["METHOD.md", "ADOPTION.md"],
    "honest": ["METHOD.md", "ADOPTING.md", "WITH-PARCELROUND.md", "FAILURE-MODES.md"],
}


def git_show(repo, sha, path):
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    r = subprocess.run(["git", "-C", repo, "show", f"{sha}:{path}"], capture_output=True, env=env)
    return r.stdout if r.returncode == 0 else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repos", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    kit = os.path.join(a.repos, "Muse-Softfloat", "softfloat-bootstrap-kit", "method")
    rows = []
    for key, files in FILES.items():
        repo, sha = PINS[key]
        for f in files:
            src = git_show(os.path.join(a.repos, repo), sha, f)
            with open(os.path.join(kit, key, f), "rb") as fh:
                cp = fh.read()
            if src is None:
                rows.append([key, f, "source-missing", "", "", ""])
                continue
            same = src == cp
            sl = src.decode("utf-8").splitlines()
            cl = cp.decode("utf-8").splitlines()
            ins = dele = 0
            first = ""
            for ln in difflib.unified_diff(sl, cl, lineterm="", n=0):
                if ln.startswith("@@") and not first:
                    first = ln
                elif ln.startswith("+") and not ln.startswith("+++"):
                    ins += 1
                elif ln.startswith("-") and not ln.startswith("---"):
                    dele += 1
            rows.append([key, f, "identical" if same else "differs", len(sl), len(cl),
                         f"+{ins}/-{dele}; first hunk {first}" if not same else ""])
    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["method", "file", "result", "source_lines", "kit_lines", "diff"])
        w.writerows(rows)
    for r in rows:
        print(r)


if __name__ == "__main__":
    sys.exit(main())
