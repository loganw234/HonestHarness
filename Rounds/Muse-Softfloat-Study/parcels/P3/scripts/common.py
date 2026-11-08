"""Shared helpers for P3's scripts. Standard library only; run with python -I.

Every script takes --repos and --scratch on the command line and holds no path.
Git is read at commits only, with GIT_OPTIONAL_LOCKS=0, through show, log,
ls-tree, cat-file or merge-base. Nothing here writes to a source.
"""
import csv
import os
import subprocess
import sys

PR_PIN = "f42242ecc1707a3d36c52e4b2a3b580ee2783e5b"
HF_PIN = "65447fd4d8253034fd6d206479c5a5371c623c60"
PR_CS7 = "894d125"
LIB_MAIN = "b78af1801d3e2bd123fed82d933414af661a9e9a"
TOY_MAIN = "084f98b29e292d0674dfa4eb9fe119c3990c726d"


def git(repo, *args, check=True):
    env = dict(os.environ)
    env["GIT_OPTIONAL_LOCKS"] = "0"
    allowed = {"show", "log", "ls-tree", "cat-file", "merge-base", "rev-list",
               "rev-parse", "branch", "diff", "grep"}
    if args[0] not in allowed:
        raise SystemExit("refused git subcommand: " + args[0])
    p = subprocess.run(["git", "-C", repo] + list(args), capture_output=True,
                       env=env)
    if check and p.returncode != 0:
        raise RuntimeError("git %s failed: %s" % (" ".join(args),
                                                  p.stderr.decode("utf-8", "replace")[:300]))
    return p.stdout.decode("utf-8", "replace")


def git_show(repo, commit, path):
    return git(repo, "show", "%s:%s" % (commit, path))


def ls_tree(repo, commit, prefix=""):
    out = git(repo, "ls-tree", "-r", "--name-only", commit, "--", prefix) if prefix else git(repo, "ls-tree", "-r", "--name-only", commit)
    return [x for x in out.splitlines() if x]


def read_file(path):
    with open(path, "rb") as f:
        return f.read().decode("utf-8", "replace")


import re as _re

_EMAIL = _re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+")
_HOME = _re.compile(r"(?:[A-Za-z]:[\/]+Users|/mnt/[a-z]/Users|/Users|/home)/[^\s`'\"),;]*")


def scrub(v):
    """Published tables must hold no address and no home path: replace them in every cell."""
    if not isinstance(v, str):
        return v
    v = _EMAIL.sub(lambda m: m.group(0) if m.group(0).startswith("noreply@") else "<address>", v)
    return _HOME.sub("<home path>", v)


def write_csv(path, header, rows):
    rows = [[scrub(c) for c in r] for r in rows]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        for r in rows:
            w.writerow(r)


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def args_roots(argv=None):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--repos", required=True)
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--out", default=None, help="data directory; default: ../data beside the scripts")
    ns = ap.parse_args(argv)
    here = os.path.dirname(os.path.abspath(__file__))
    ns.here = here
    ns.data = ns.out or os.path.join(here, "..", "data")
    ns.data = os.path.normpath(ns.data)
    ns.muse = os.path.join(ns.repos, "Muse-Softfloat")
    ns.pr = os.path.join(ns.repos, "ParcelRound")
    ns.hf = os.path.join(ns.repos, "HonestFramework")
    ns.hh = os.path.join(ns.repos, "HonestHarness")
    ns.toy = os.path.join(ns.muse, "muse-softfloat-toy")
    ns.kit = os.path.join(ns.muse, "softfloat-bootstrap-kit")
    ns.corpus = os.path.join(ns.scratch, "P3", "corpus")
    return ns


def sha256_text(s):
    import hashlib
    return hashlib.sha256(s.encode("utf-8")).hexdigest()
