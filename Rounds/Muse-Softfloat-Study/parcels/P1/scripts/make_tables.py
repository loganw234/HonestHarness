"""Render the derived tables as Markdown (data/tables.md) so ANALYSIS.md can quote them without retyping.

Reads only data/figures.json and the other files in data/. Nothing is recomputed here.
"""
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C


def md(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out) + "\n"


def fmt(n):
    return "{:,}".format(n)


def main():
    F = json.load(open(os.path.join(C.DATA, "figures.json"), encoding="utf-8"))
    o = []
    o.append("## T1 Tokens by model (figures.json `tokens_by_model`)\n")
    o.append(md(["model", "usage rows", "input", "output", "input+output", "cached"],
                [[m, v["usage_rows"], fmt(v["input"]), fmt(v["output"]), fmt(v["input_plus_output"]), fmt(v["cached"])]
                 for m, v in F["tokens_by_model"].items()]))
    o.append("## T2 Tokens by role (role from the agent's passes row; `tokens_by_role`)\n")
    o.append(md(["role", "usage rows", "input", "output", "input+output"],
                [[m, v["usage_rows"], fmt(v["input"]), fmt(v["output"]), fmt(v["input_plus_output"])] for m, v in F["tokens_by_role"].items()]))
    o.append("## T3 Passes by wave and role (`passes_by_wave_role`)\n")
    roles = ["author", "fixer", "surveyor", "verifier"]
    o.append(md(["wave"] + roles, [[w] + [c.get(r, 0) for r in roles] for w, c in F["passes_by_wave_role"].items()]))
    o.append("## T4 Verifier passes by wave: count, a, b (`verifier_passes_by_wave`, `verifier_ab_by_wave`)\n")
    o.append(md(["wave", "verifier passes", "a", "b"],
                [[w, F["verifier_passes_by_wave"][w], F["verifier_ab_by_wave"][w]["a"], F["verifier_ab_by_wave"][w]["b"]] for w in F["verifier_passes_by_wave"]]))
    o.append("## T5 Plants by wave (`plants_by_wave`)\n")
    o.append(md(["wave", "plants", "caught", "missed"], [[w, v["n"], v["caught"], v["n"] - v["caught"]] for w, v in F["plants_by_wave"].items()]))
    for name, title in (("class", "T6 Recall by class"), ("model", "T7 Recall by verifier model"), ("project", "T8 Recall by project")):
        rows = list(csv.reader(open(os.path.join(C.DATA, "recall_by_%s.csv" % name), encoding="utf-8")))
        o.append("## %s (recall_by_%s.csv)\n" % (title, name))
        o.append(md(rows[0], rows[1:]))
    rows = list(csv.reader(open(os.path.join(C.DATA, "recall_by_wave.csv"), encoding="utf-8")))
    o.append("## T9 Recall by wave (recall_by_wave.csv)\n")
    o.append(md(rows[0], rows[1:]))
    rows = list(csv.reader(open(os.path.join(C.DATA, "recall_by_verifier.csv"), encoding="utf-8")))
    o.append("## T10 Verifiers below 5 of 5 (from recall_by_verifier.csv; the other verifiers are 5 of 5)\n")
    o.append(md(rows[0], [r for r in rows[1:] if r[2] != r[1]]))
    o.append("## T11 Escalations (`escalations`)\n")
    e = F["escalations"]
    o.append(md(["kind", "n", "answered", "unanswered", "min s", "median s", "max s"],
                [["test", e["test"], e["test_latency_seconds"]["answered"], e["test_latency_seconds"]["unanswered"],
                  e["test_latency_seconds"]["min"], e["test_latency_seconds"]["median"], e["test_latency_seconds"]["max"]],
                 ["real", e["real"], e["real_latency_seconds"]["answered"], e["real_latency_seconds"]["unanswered"],
                  e["real_latency_seconds"]["min"], e["real_latency_seconds"]["median"], e["real_latency_seconds"]["max"]]]))
    o.append("## T12 Agents with no usage and no passes row (agents_without_rows.csv)\n")
    rows = list(csv.reader(open(os.path.join(C.DATA, "agents_without_rows.csv"), encoding="utf-8")))
    o.append(md(["agent", "plant rows"], [[r[0], r[3]] for r in rows[1:]]))
    open(os.path.join(C.DATA, "tables.md"), "w", encoding="utf-8", newline="\n").write("\n".join(o))
    print("wrote data/tables.md,", sum(1 for x in o if x.startswith("##")), "tables")


main()
