"""Check the primary citation of kit_use.csv, toy_practice.csv and honestharness_rounds.csv.

Each row names evidence_source, evidence_line and evidence_quote. The source is
re-read and the quote must be in that line (whitespace folded). Sources:
  LIB:<path>        the library repository at b78af18 (git show)
  TOY:<path>        the toy repository at 084f98b (git show)
  MUSE:<path>       a file under <muse>
  HH1:<path>        HonestHarness main at the SHA below (git show)
  HH1ZIP:<member>   a top-level member of round 1's archived ledger zip (git show, zipfile)
  HH2:<file>        a file in <repos>/honestharness-r2-ledger/
  HH2B:<path>       HonestHarness branch round2 at the SHA below (git show)
  HHLOG:<sha>       the subject of a HonestHarness commit (git log), line 1
Rows with no evidence_source (SILENT, NEITHER, NOT APPLICABLE) are counted, not checked.

Usage: python -I cite_check.py --repos <repos> --scratch <scratch>
"""
import io
import os
import subprocess
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import args_roots, git, git_show, read_csv, read_file, TOY_MAIN, LIB_MAIN

HH_MAIN = "b69ed7613bdb655fb4b42acd1517b0b30631af7a"
HH_R2 = "8e392dd33b860a9eb8fd4baa4a0351e3e64be660"


def fold(s):
    return " ".join(s.split())


def main():
    ns = args_roots()
    lib = os.path.join(ns.muse, "muse-softfloat")
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    zdata = subprocess.run(["git", "-C", ns.hh, "show", HH_MAIN + ":Rounds/HonestHarness-R1/round1-ledger.zip"],
                           capture_output=True, env=env).stdout
    z = zipfile.ZipFile(io.BytesIO(zdata))
    cache = {}

    def lines(src):
        if src in cache:
            return cache[src]
        kind, _, path = src.partition(":")
        if kind == "LIB":
            t = git_show(lib, LIB_MAIN, path)
        elif kind == "TOY":
            t = git_show(ns.toy, TOY_MAIN, path)
        elif kind == "MUSE":
            t = read_file(os.path.join(ns.muse, path))
        elif kind == "HH1":
            t = git_show(ns.hh, HH_MAIN, path)
        elif kind == "HH1ZIP":
            t = z.read("honestharness-r1-ledger/" + path).decode("utf-8", "replace")
        elif kind == "HH2":
            t = read_file(os.path.join(ns.repos, "honestharness-r2-ledger", path))
        elif kind == "HH2B":
            t = git_show(ns.hh, HH_R2, path)
        elif kind == "HHLOG":
            t = git(ns.hh, "log", "-1", "--format=%s", path)
        else:
            raise SystemExit("unknown source kind " + kind)
        cache[src] = t.splitlines()
        return cache[src]

    bad = 0
    for fn in ("kit_use.csv", "toy_practice.csv", "honestharness_rounds.csv"):
        rows = read_csv(os.path.join(ns.data, fn))
        checked = unchecked = 0
        for r in rows:
            src = r["evidence_source"]
            if not src:
                unchecked += 1
                continue
            ls = lines(src)
            n = int(r["evidence_line"])
            ok = 1 <= n <= len(ls) and fold(r["evidence_quote"]) in fold(ls[n - 1])
            if len(r["evidence_quote"].split()) > 15:
                ok = False
            if not ok:
                bad += 1
                print("FAIL", fn, r["proposal"], src, n, "|", r["evidence_quote"])
            checked += 1
        print(fn, "rows:", len(rows), "| citations checked:", checked, "| rows without a citation:", unchecked)
    print("failures:", bad)
    sys.exit(1 if bad else 0)


main()
