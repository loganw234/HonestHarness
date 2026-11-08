"""Task 2: recall by class, wave, verifier, model and project.

Joins data/plants_class_blind.csv (classes, written before grades) with the plants rows'
grades and the verifier's model (usage.jsonl row, else data/model_map.csv, else not recorded).
Writes data/plants_classed.csv, data/recall_by_{class,wave,verifier,model,project}.csv.
"""
import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C


def table(path, key, rows, name):
    g = collections.OrderedDict()
    for r in rows:
        g.setdefault(r[key], []).append(r)
    out = []
    for k, rs in sorted(g.items(), key=lambda kv: (-len(kv[1]), str(kv[0]))):
        n = len(rs)
        c = sum(1 for r in rs if r["grade"] == "caught")
        lo, hi = C.wilson(c, n)
        out.append([k, n, c, n - c, "%.3f" % (c / n), lo, hi, "n < 10: too small to rank" if n < 10 else ""])
    C.write_csv(path, [name, "n", "caught", "missed", "recall", "wilson95_lo", "wilson95_hi", "note"], out)
    return out


def main():
    a = C.args()
    lib = C.lib_jsonl(a.repos, "plants")
    usage = {u["agent"]: u["model"] for u in C.lib_jsonl(a.repos, "usage")}
    mm = {r["verifier"]: r for r in C.read_csv(os.path.join(C.DATA, "model_map.csv"))}
    blind = C.read_csv(os.path.join(C.DATA, "plants_class_blind.csv"))
    rows = []
    for i, (r, b) in enumerate(zip(lib, blind), 1):
        assert int(b["row"]) == i and b["verifier"] == r["verifier"] and int(b["plant"]) == r["plant"]
        if r["verifier"] in usage:
            model, msrc = usage[r["verifier"]], "usage.jsonl"
        elif r["verifier"] in mm:
            model, msrc = mm[r["verifier"]]["model"], ("lead ledger line (see model_map.csv)" if mm[r["verifier"]]["model"] != "not recorded" else "none")
        else:
            model, msrc = "not recorded", "none"
        d = dict(b)
        d.update({"grade": r["grade"], "graded_by": r["graded_by"], "checked_by": r["checked_by"], "model": model, "model_source": msrc,
                  "project": "library"})
        rows.append(d)
    hdr = ["row", "wave", "verifier", "plant", "key_prefix", "shape", "altered_file", "class", "basis", "tiebreak",
           "path_rule_agrees", "path_rule_class", "reason", "grade", "graded_by", "checked_by", "model", "model_source"]
    C.write_csv(os.path.join(C.DATA, "plants_classed.csv"), hdr, [[d[h] for h in hdr] for d in rows])
    for key, nm in (("class", "class"), ("wave", "wave"), ("verifier", "verifier"), ("model", "model")):
        t = table(os.path.join(C.DATA, "recall_by_%s.csv" % nm), key, rows, key)
        print("by", nm, [(x[0], x[1], x[2]) for x in t][:12])
    # project: library per plant; toy per copy (no shape), from the toy rows
    toy = [r for r in C.toy_plants(a.repos) if r.get("status") == "verdict"]
    proj = [["library", len(rows), sum(1 for d in rows if d["grade"] == "caught")],
            ["toy (plants inside verdict rows)", sum(r["plants"] for r in toy), sum(r["caught"] for r in toy)]]
    out = []
    for nm, n, c in proj:
        lo, hi = C.wilson(c, n)
        out.append([nm, n, c, n - c, "%.3f" % (c / n), lo, hi, ""])
    C.write_csv(os.path.join(C.DATA, "recall_by_project.csv"), ["project", "n", "caught", "missed", "recall", "wilson95_lo", "wilson95_hi", "note"], out)
    print("project", [(x[0], x[1], x[2]) for x in out])
    # sensitivity: spark only, usage-row model only
    sp = [d for d in rows if d["model"] == "muse-spark-1.3"]
    spu = [d for d in sp if d["model_source"] == "usage.jsonl"]
    print("spark all", len(sp), sum(1 for d in sp if d["grade"] == "caught"), "| spark usage-row only", len(spu), sum(1 for d in spu if d["grade"] == "caught"))
    print("misses by class:", collections.Counter(d["class"] for d in rows if d["grade"] != "caught"))
    print("misses by model:", collections.Counter(d["model"] for d in rows if d["grade"] != "caught"))


main()
