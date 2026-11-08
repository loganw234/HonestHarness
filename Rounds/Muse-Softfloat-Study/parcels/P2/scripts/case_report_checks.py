"""Task 4: measure the figures behind the case report's checkable claims.

usage: python -I case_report_checks.py --repos <repos> --out data/case_report_measures.csv
Everything is read from the library repository at commits (GIT_OPTIONAL_LOCKS=0) or from named files.
The case report cites a49991f; the lead's first look used b78af18. Both are measured where they differ.
Output: key,value rows; curated verdicts live in scripts/case_report_curated.txt.
"""
import argparse, csv, json, os, re, subprocess, sys
from collections import Counter

A = "a49991f2603f2ebd55f6287be1d691de78cf5c57"
B = "b78af1801d3e2bd123fed82d933414af661a9e9a"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repos", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    muse = os.path.join(a.repos, "Muse-Softfloat")
    lib = os.path.join(muse, "muse-softfloat")
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")

    def git(*args, check=True):
        r = subprocess.run(["git", "-C", lib, *args], capture_output=True, env=env)
        if check and r.returncode != 0:
            raise SystemExit("git failed: %s %s" % (args, r.stderr.decode()[:200]))
        return r

    def show(sha, path):
        return git("show", f"{sha}:{path}").stdout.decode("utf-8")

    out = []

    def put(k, v):
        out.append([k, v])

    for tag, sha in (("a49991f", A), ("b78af18", B)):
        for f in ("usage", "passes", "plants", "briefs", "corrections", "escalations", "fetches"):
            rows = [l for l in show(sha, f"docs/metrics/{f}.jsonl").splitlines() if l.strip()]
            put(f"{tag}.rows.{f}", len(rows))
        us = [json.loads(l) for l in show(sha, "docs/metrics/usage.jsonl").splitlines() if l.strip()]
        put(f"{tag}.usage.input", sum(u["input_tokens"] for u in us))
        put(f"{tag}.usage.output", sum(u["output_tokens"] for u in us))
        put(f"{tag}.usage.input_plus_output", sum(u["input_tokens"] + u["output_tokens"] for u in us))
        pl = [json.loads(l) for l in show(sha, "docs/metrics/plants.jsonl").splitlines() if l.strip()]
        put(f"{tag}.plants.caught", sum(1 for p in pl if p["grade"] == "caught"))
        for w, c in sorted(Counter(p["wave"] for p in pl).items()):
            cw = sum(1 for p in pl if p["wave"] == w and p["grade"] == "caught")
            put(f"{tag}.plants.wave.{w}", f"{cw}/{c}")
        put(f"{tag}.plants.key0305f97a", "%d rows, %d caught" % (
            sum(1 for p in pl if p["key_sha256"].startswith("0305f97a")),
            sum(1 for p in pl if p["key_sha256"].startswith("0305f97a") and p["grade"] == "caught")))
        pk = [l.split()[0] for l in show(sha, "docs/metrics/plant_keys.sha256").splitlines() if l.strip() and not l.startswith("#")]
        covered = sum(1 for p in pl if p["key_sha256"] in set(pk))
        put(f"{tag}.plant_keys.hashes", len(pk))
        put(f"{tag}.plant_keys.rows_covered", f"{covered} of {len(pl)}")
        put(f"{tag}.record.lines", len(show(sha, "docs/RECORD.md").splitlines()))
        lines = [l for l in show(sha, "docs/COVERAGE.tsv").splitlines() if l.strip() and not l.startswith("#")]
        hdr = lines[0].split("\t")
        data = [l.split("\t") for l in lines[1:]]
        put(f"{tag}.coverage.rows", len(data))
        if "tier" in hdr:
            put(f"{tag}.coverage.tiers", dict(Counter(r[hdr.index('tier')] for r in data)))
        if "authority" in hdr:
            put(f"{tag}.coverage.authority", dict(Counter(r[hdr.index('authority')] for r in data)))
        rs = show(sha, "tools/run.sh")
        put(f"{tag}.run_sh.testfloat_lines", len(re.findall(r"(?i)testfloat", rs)))
        put(f"{tag}.run_sh.berkeley_lines", len(re.findall(r"(?i)berkeley", rs)))
    put("coverage.header", "|".join(hdr))
    # commits: trailers
    for tag, sha in (("a49991f", A), ("b78af18", B)):
        r = git("log", "--format=%H%x1f%B%x1e", sha).stdout.decode("utf-8", "replace").split("\x1e")
        commits = [c for c in r if c.strip()]
        no = [c.split("\x1f")[0].strip()[:7] for c in commits if "Co-Authored-By:" not in c.split("\x1f", 1)[1]]
        put(f"{tag}.commits", len(commits))
        put(f"{tag}.commits_without_trailer", "%d %s" % (len(no), no[:5]))
    put("tag.v1.0.0.type", git("cat-file", "-t", "v1.0.0").stdout.decode().strip())
    put("tag.v1.0.0.commit", git("rev-parse", "v1.0.0^{commit}").stdout.decode().strip()[:7])
    put("957fdae.date", git("log", "-1", "--format=%cI", "957fdae").stdout.decode().strip())
    put("cdc40ae.ancestor_of_a49991f", "yes" if git("merge-base", "--is-ancestor", "cdc40ae", A, check=False).returncode == 0 else "no")
    put("a49991f.ancestor_of_b78af18", "yes" if git("merge-base", "--is-ancestor", A, B, check=False).returncode == 0 else "no")
    put("a49991f.commits_before_b78af18", git("rev-list", "--count", f"{A}..{B}").stdout.decode().strip())
    for sha in ("caf00b0", "8751b11"):
        rec = show(A, "docs/RECORD.md")
        put(f"RECORD@a49991f mentions {sha}", len(re.findall(sha, rec)))
    rec = show(A, "docs/RECORD.md")
    put("RECORD@a49991f lines mentioning 'delta'", len([l for l in rec.splitlines() if re.search(r"(?i)\bdelta\b", l)]))
    # workspace files
    wt = os.path.join(muse, "worktrees")
    put("workspace worktrees entries (now, not at report time)", len(os.listdir(wt)) if os.path.isdir(wt) else "n/a")
    lead = open(os.path.join(muse, "ledger", "lead.md"), encoding="utf-8").read().splitlines()
    cr = next(i for i, l in enumerate(lead, 1) if l.startswith("## ") and "case report written" in l)
    put("lead.md line of the 'method case report written' heading", cr)
    put("lead.md lines before the full audit sweep heading", next(i for i, l in enumerate(lead, 1) if l.startswith("## ") and "full audit sweep" in l) - 1)
    put("lead.md total lines (now)", len(lead))
    us = [json.loads(l) for l in show(A, "docs/metrics/usage.jsonl").splitlines() if l.strip()]
    def role(ag):
        for pre in ("verifier", "rechecker", "regater"):
            if ag.startswith(pre):
                return "verifier-like (verifier, rechecker)" if pre != "regater" else "regater"
        for pre in ("parcel", "auditor", "study", "lead", "wave", "ias15", "video"):
            if ag.startswith(pre):
                return pre
        return "other"
    cnt = Counter((role(u["agent"]), u["model"]) for u in us)
    for (r, m), c in sorted(cnt.items()):
        put(f"usage rows at a49991f by agent-name prefix and model: {r} / {m}", c)
    firstv = sorted((u["wave"], u["agent"], u["model"]) for u in us if u["agent"].startswith("verifier"))[:6]
    put("first verifier usage rows (wave, agent, model)", firstv)
    pl = [json.loads(l) for l in show(A, "docs/metrics/plants.jsonl").splitlines() if l.strip()]
    put("wave6 missed plant (verifier, plant, shape)", [(p_["verifier"], p_["plant"], p_["shape"][:90]) for p_ in pl if p_["wave"] == "wave6" and p_["grade"] != "caught"])
    # ls-tree has no exclude pathspec, so list the root once (names only) and recurse into each entry except the fenced two
    roots = [r for r in git("ls-tree", "--name-only", A).stdout.decode("utf-8").splitlines() if r not in ("audit-bundle", "audit-bundle-v2")]
    tree = []
    for r_ in roots:
        tree += git("ls-tree", "-r", "--name-only", A, "--", r_).stdout.decode("utf-8").splitlines()
    top = Counter((t.split("/")[0] if "/" in t else "(root)") for t in tree)
    put("tree files at a49991f excluding the fenced folders (each non-fenced root entry listed on its own)", len(tree))
    put("tree top-level counts excluding the fenced folders", dict(top.most_common()))
    put("library core files (src, include, compat) share of that tree", "%d of %d" % (sum(top.get(d, 0) for d in ("src", "include", "compat")), len(tree)))
    bd = os.path.join(muse, "ledger", "briefs")
    bf = sorted(f for f in os.listdir(bd) if f.endswith(".md"))
    txt = {f: open(os.path.join(bd, f), encoding="utf-8", errors="replace").read() for f in bf}
    put("briefs files (ledger/briefs)", len(bf))
    put("briefs containing 'memory ceiling'", sum(1 for t in txt.values() if re.search(r"(?i)memory ceiling", t)))
    put("briefs containing 'memory ceiling' or ulimit or 'memory cap'", sum(1 for t in txt.values() if re.search(r"(?i)memory ceiling|ulimit|memory cap", t)))
    put("briefs containing 'script file' or 'no long inline'", sum(1 for t in txt.values() if re.search(r"(?i)script files?|no long inline", t)))
    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["key", "value"])
        w.writerows(out)
    for k, v in out:
        print(k, "=", v)


if __name__ == "__main__":
    sys.exit(main())
