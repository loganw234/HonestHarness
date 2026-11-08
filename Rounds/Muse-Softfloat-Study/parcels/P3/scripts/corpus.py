"""Build the numbered corpus for Task 1 and its manifest.

Method files and case studies are read with git show at the kit's pins;
the kit's own files are read as files. Writes the corpus to
<scratch>/P3/corpus/<id>.txt (one line per source line, numbered by script)
and data/corpus_manifest.csv.

Usage: python -I corpus.py --repos <repos> --scratch <scratch>
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (args_roots, git_show, ls_tree, read_file, write_csv,
                    sha256_text, PR_PIN, HF_PIN)

PR_CS7_FULL = "894d125"


def entries(ns):
    """Yield (id, tier, source, commit, path, text). Tier M = method file, C = case study, K = kit file."""
    pr_files = ls_tree(ns.pr, PR_PIN)
    hf_files = ls_tree(ns.hf, HF_PIN)
    missing = []

    def want(repo, commit, name, files, tier, source, sid_prefix):
        if name not in files:
            missing.append((source, name))
            return None
        text = git_show(repo, commit, name)
        return ("%s:%s" % (sid_prefix, name), tier, source, commit, name, text)

    out = []
    for name in ["METHOD.md", "ADOPTION.md"]:
        out.append(want(ns.pr, PR_PIN, name, pr_files, "M", "ParcelRound", "PR"))
    for name in sorted(x for x in pr_files if x.startswith("templates/")):
        out.append(want(ns.pr, PR_PIN, name, pr_files, "M", "ParcelRound", "PR"))
    for name in ["CASE-STUDY.md"] + ["CASE-STUDY-%d.md" % n for n in range(2, 7)] + ["archive/round6-practice-survey.md"]:
        out.append(want(ns.pr, PR_PIN, name, pr_files, "C", "ParcelRound", "PR"))
    for name in ["METHOD.md", "ADOPTING.md", "FAILURE-MODES.md", "WITH-PARCELROUND.md"]:
        out.append(want(ns.hf, HF_PIN, name, hf_files, "M", "HonestFramework", "HF"))
    for name in sorted(x for x in hf_files if x.startswith("templates/")):
        out.append(want(ns.hf, HF_PIN, name, hf_files, "M", "HonestFramework", "HF"))
    out.append(want(ns.hf, HF_PIN, "CASE-STUDY.md", hf_files, "C", "HonestFramework", "HF"))
    # the one file above the pin that any local ref holds (see newer.py): tier N
    out.append(("NEW:CASE-STUDY-7.md", "N", "ParcelRound", PR_CS7_FULL, "CASE-STUDY-7.md",
                git_show(ns.pr, PR_CS7_FULL, "CASE-STUDY-7.md")))

    # the kit's own files (read as files). method/ holds copies of the method
    # files and is left out: the SHA-pinned texts above are the source.
    kit = ns.kit
    names = sorted(f for f in os.listdir(kit) if f.endswith(".md") or f.endswith(".txt"))
    for f in names:
        out.append(("KIT:" + f, "K", "kit", "file", f, read_file(os.path.join(kit, f))))
    ex = os.path.join(kit, "examples")
    out.append(("KIT:examples/README.md", "K", "kit", "file", "examples/README.md", read_file(os.path.join(ex, "README.md"))))
    for f in sorted(os.listdir(os.path.join(ex, "cases"))):
        out.append(("KIT:examples/cases/" + f, "K", "kit", "file", "examples/cases/" + f,
                    read_file(os.path.join(ex, "cases", f))))
    for f in sorted(x for x in os.listdir(os.path.join(kit, "tools")) if os.path.isfile(os.path.join(kit, "tools", x))):
        out.append(("KIT:tools/" + f, "K", "kit", "file", "tools/" + f, read_file(os.path.join(kit, "tools", f))))
    return [e for e in out if e], missing


if __name__ == "__main__":
    ns = args_roots()
    os.makedirs(ns.corpus, exist_ok=True)
    ents, missing = entries(ns)
    rows = []
    for sid, tier, source, commit, path, text in ents:
        fn = sid.replace("/", "__").replace(":", "__") + ".txt"
        lines = text.splitlines()
        with open(os.path.join(ns.corpus, fn), "w", encoding="utf-8", newline="\n") as f:
            for i, l in enumerate(lines, 1):
                f.write("%d\t%s\n" % (i, l))
        rows.append([sid, tier, source, commit, path, len(lines), sha256_text(text)])
    write_csv(os.path.join(ns.data, "corpus_manifest.csv"),
              ["source_id", "tier", "source", "commit", "path", "lines", "sha256_of_text"], rows)
    print("corpus files:", len(rows), "| by tier:", {t: sum(1 for r in rows if r[1] == t) for t in "MCK"})
    print("lines in all:", sum(r[5] for r in rows))
    print("named files missing at the pin:", missing)
