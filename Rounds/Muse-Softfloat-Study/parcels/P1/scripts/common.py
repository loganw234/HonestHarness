"""Shared helpers for the P1 scripts. Standard library only.

Roots are always arguments (--repos); nothing here holds a path.
Git is read at commits only, with GIT_OPTIONAL_LOCKS=0 and read-only verbs.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys

LIB_SHA = "b78af1801d3e2bd123fed82d933414af661a9e9a"
TOY_SHA = "084f98b29e292d0674dfa4eb9fe119c3990c726d"
PR_SHA = "f42242ecc1707a3d36c52e4b2a3b580ee2783e5b"
PR_CS7_SHA = "894d125"
SEED = 20261108

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data")


def args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repos", required=True, help="the directory holding the repositories")
    ap.add_argument("--scratch", default=None, help="scratch directory for source copies")
    return ap.parse_args()


def muse(repos):
    return os.path.join(repos, "Muse-Softfloat")


def lib_repo(repos):
    return os.path.join(muse(repos), "muse-softfloat")


def toy_repo(repos):
    return os.path.join(muse(repos), "muse-softfloat-toy")


def git(repo, *a, binary=False):
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    p = subprocess.run(["git", "-C", repo] + list(a), capture_output=True, env=env)
    if p.returncode != 0:
        raise RuntimeError("git %s failed: %s" % (a, p.stderr.decode("utf-8", "replace")[:200]))
    return p.stdout if binary else p.stdout.decode("utf-8", "replace")


def show(repo, sha, path, binary=False):
    return git(repo, "show", "%s:%s" % (sha, path), binary=binary)


def jsonl(text):
    return [json.loads(l) for l in text.splitlines() if l.strip()]


def lib_jsonl(repos, name):
    return jsonl(show(lib_repo(repos), LIB_SHA, "docs/metrics/%s.jsonl" % name))


def toy_plants(repos):
    return jsonl(show(toy_repo(repos), TOY_SHA, "docs/metrics/plants.jsonl"))


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def read_text(path):
    with open(path, "rb") as f:
        return f.read().decode("utf-8", "replace")


def write_csv(path, header, rows):
    import csv
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        for r in rows:
            w.writerow(r)


def read_csv(path):
    import csv
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (round(max(0.0, c - h), 3), round(min(1.0, c + h), 3))
