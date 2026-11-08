"""Task 2: apply the rubric. Joins data/class_input.csv (my hand classing, written from
shape + note, with the key's altered-file path where the shape did not decide) with the
plants rows and data/key_plants.csv. Writes data/plants_class_blind.csv WITHOUT grades:
recall.py joins grades afterwards, so the classing cannot depend on the outcome.

Also prints the rows where the class differs from a path-only rule, as a review list.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

NAMES = {"C": "code", "T": "test data", "D": "claim in docs", "M": "metadata or provenance",
         "R": "record arithmetic", "O": "other"}


def path_rule(p):
    """A path-only class, used only to flag disagreements for review."""
    if p.startswith("docs/metrics/"):
        return "metrics file (M or R by what is altered)"
    if p.startswith(("tests/vectors/", "tests/gen_", "tests/interval_catalogue")) or "expected" in os.path.basename(p):
        return "T"
    if p.startswith(("src/", "include/", "compat/", "board/", "tools/", ".github/", "tables/", "video/segments/", "video/assemble", "video/captions")) \
            or p in ("demo/fetch.py", "demo/run_demo.sh", "examples/host/build.sh"):
        return "C"
    if p == "site/app.js":
        return "C or D (TB8)"
    if p.endswith((".md", ".html", ".json")) or p.startswith(("site/", "docs/")):
        return "D"
    return "?"


def main():
    a = C.args()
    lib = C.lib_jsonl(a.repos, "plants")
    inp = {int(r["row"]): r for r in C.read_csv(os.path.join(C.DATA, "class_input.csv"))}
    kp = {int(r["row"]): r for r in C.read_csv(os.path.join(C.DATA, "key_plants.csv"))}
    assert len(inp) == len(lib) == len(kp) == 195, (len(inp), len(lib), len(kp))
    rows, review = [], []
    for i, r in enumerate(lib, 1):
        h = inp[i]
        cls = NAMES[h["cls"]]
        k = kp[i]
        pr = path_rule(k["altered_file"])
        agree = pr == h["cls"]
        if not agree:
            review.append((i, h["cls"], pr, k["altered_file"]))
        rows.append([i, r["wave"], r["verifier"], r["plant"], r["key_sha256"][:8], r["shape"], k["altered_file"],
                     cls, h["basis"], h["tiebreak"], "yes" if agree else "no", pr if not agree else "", h["reason"]])
    C.write_csv(os.path.join(C.DATA, "plants_class_blind.csv"),
                ["row", "wave", "verifier", "plant", "key_prefix", "shape", "altered_file", "class", "basis", "tiebreak",
                 "path_rule_agrees", "path_rule_class", "reason"], rows)
    from collections import Counter
    cc = Counter(r[7] for r in rows)
    print("classed", len(rows), dict(cc))
    print("rows with a tie-break rule logged:", sum(1 for r in rows if r[9]))
    print("rows where class differs from the path-only rule:", len(review))
    for x in review:
        print("  row", x[0], "class", x[1], "path rule", x[2], x[3])
    print("share other: %.1f%%" % (100.0 * cc["other"] / len(rows)))


main()
