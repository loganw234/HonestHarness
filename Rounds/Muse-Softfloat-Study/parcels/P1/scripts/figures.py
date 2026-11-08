"""Task 1: recompute the library's and the toy's metrics from rows at the named commits.

Writes data/figures.json and data/agents_without_rows.csv.
Everything is read with `git show <sha>:<path>` (read-only) or as a named file.
"""
import collections
import json
import os
import re
import statistics
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C


def ts(s):
    return datetime.fromisoformat(s)


def grep_lines(text, name):
    out = []
    for i, l in enumerate(text.splitlines(), 1):
        if name in l:
            out.append(i)
    return out


def main():
    a = C.args()
    lib = C.lib_repo(a.repos)
    toy = C.toy_repo(a.repos)
    F = {}
    names = ["usage", "passes", "plants", "briefs", "corrections", "escalations", "fetches"]
    rows = {n: C.lib_jsonl(a.repos, n) for n in names}
    F["library_row_counts"] = {n: len(rows[n]) for n in names}
    F["library_commits"] = {
        "main_sha": C.LIB_SHA,
        "count": int(C.git(lib, "rev-list", "--count", C.LIB_SHA).strip()),
        "first": C.git(lib, "log", "--reverse", "--format=%ci", C.LIB_SHA).splitlines()[0],
        "last": C.git(lib, "log", "-1", "--format=%ci", C.LIB_SHA).strip(),
        "first_author_date": C.git(lib, "log", "--reverse", "--format=%ai", C.LIB_SHA).splitlines()[0],
        "last_author_date": C.git(lib, "log", "-1", "--format=%ai", C.LIB_SHA).strip(),
    }
    F["toy_commits"] = {
        "main_sha": C.TOY_SHA,
        "count": int(C.git(toy, "rev-list", "--count", C.TOY_SHA).strip()),
        "first": C.git(toy, "log", "--reverse", "--format=%ci", C.TOY_SHA).splitlines()[0],
        "last": C.git(toy, "log", "-1", "--format=%ci", C.TOY_SHA).strip(),
        "first_author_date": C.git(toy, "log", "--reverse", "--format=%ai", C.TOY_SHA).splitlines()[0],
        "last_author_date": C.git(toy, "log", "-1", "--format=%ai", C.TOY_SHA).strip(),
    }

    # --- usage / tokens ---
    usage, passes = rows["usage"], rows["passes"]
    roles_of = collections.defaultdict(set)
    for p in passes:
        roles_of[p["agent"]].add(p["role"])
    by_model = collections.defaultdict(lambda: [0, 0, 0, 0])
    by_role = collections.defaultdict(lambda: [0, 0, 0, 0])
    model_of = {}
    for u in usage:
        model_of[u["agent"]] = u["model"]
        m = by_model[u["model"]]
        m[0] += 1; m[1] += u["input_tokens"]; m[2] += u["output_tokens"]; m[3] += u.get("cached_tokens", 0)
        rs = roles_of.get(u["agent"])
        role = "unjoined (no passes row)" if not rs else "+".join(sorted(rs))
        r = by_role[role]
        r[0] += 1; r[1] += u["input_tokens"]; r[2] += u["output_tokens"]; r[3] += u.get("cached_tokens", 0)
    fmt = lambda d: {k: {"usage_rows": v[0], "input": v[1], "output": v[2], "input_plus_output": v[1] + v[2], "cached": v[3]} for k, v in sorted(d.items())}
    F["tokens_by_model"] = fmt(by_model)
    F["tokens_by_role"] = fmt(by_role)
    F["tokens_total"] = {
        "input": sum(u["input_tokens"] for u in usage),
        "output": sum(u["output_tokens"] for u in usage),
        "input_plus_output": sum(u["input_tokens"] + u["output_tokens"] for u in usage),
        "cached": sum(u.get("cached_tokens", 0) for u in usage),
        "rows_with_cached": sum(1 for u in usage if "cached_tokens" in u),
        "rows_cached_exceeds_input": sum(1 for u in usage if u.get("cached_tokens", 0) > u["input_tokens"]),
        "note": "the record does not say whether cached is inside input; total here is input+output",
    }

    # --- passes ---
    F["passes_by_role"] = dict(collections.Counter(p["role"] for p in passes))
    pw = collections.defaultdict(collections.Counter)
    for p in passes:
        pw[p["wave"]][p["role"]] += 1
    F["passes_by_wave_role"] = {w: dict(c) for w, c in sorted(pw.items())}
    ver = [(i + 1, p) for i, p in enumerate(passes) if p["role"] == "verifier"]
    F["verifier_verdicts"] = dict(collections.Counter(p["verdict"] for _, p in ver))
    F["verifier_passes_by_wave"] = dict(collections.Counter(p["wave"] for _, p in ver))
    F["verifier_ab_by_wave"] = {}
    for w in sorted(set(p["wave"] for _, p in ver)):
        F["verifier_ab_by_wave"][w] = {"a": sum(p["a"] for _, p in ver if p["wave"] == w), "b": sum(p["b"] for _, p in ver if p["wave"] == w)}
    F["verifier_ab_total"] = {"a": sum(p["a"] for _, p in ver), "b": sum(p["b"] for _, p in ver)}
    F["verifier_ab_total_all_rows"] = {"a": sum(p.get("a", 0) for p in passes), "b": sum(p.get("b", 0) for p in passes)}
    F["verifier_model_split"] = dict(collections.Counter(model_of.get(p["agent"], "no usage row") for _, p in ver))
    F["roles_in_passes_rows"] = sorted(set(p["role"] for p in passes))

    # --- sent_back ---
    sb = [(i, p) for i, p in ver if p.get("sent_back")]
    F["sent_back_raw"] = len(sb)
    F["sent_back_erratum_not_revision"] = 8
    F["sent_back_erratum_remaining"] = len(sb) - 8
    cand = []
    for i, p in sb:
        later = [(j + 1, q["agent"], q["role"], q["pass"]) for j, q in enumerate(passes)
                 if j + 1 > i and q["role"] in ("author", "fixer") and q["work"] == p["work"]]
        cand.append({"passes_line": i, "agent": p["agent"], "wave": p["wave"], "work": p["work"][:70],
                     "later_author_or_fixer_rows_same_work": later})
    F["sent_back_rows"] = cand
    F["sent_back_with_later_author_or_fixer_same_work"] = sum(1 for c in cand if c["later_author_or_fixer_rows_same_work"])

    # --- plants ---
    pl = rows["plants"]
    F["plants_by_grade"] = dict(collections.Counter(r["grade"] for r in pl))
    F["plants_graded_by"] = dict(collections.Counter(r["graded_by"] for r in pl))
    F["plants_checked_by"] = dict(collections.Counter(r["checked_by"] for r in pl))
    F["plants_by_wave"] = {w: {"n": n, "caught": sum(1 for r in pl if r["wave"] == w and r["grade"] == "caught")}
                           for w, n in sorted(collections.Counter(r["wave"] for r in pl).items())}
    F["plants_distinct_key_sha256"] = len(set(r["key_sha256"] for r in pl))
    F["plants_verifiers"] = len(set(r["verifier"] for r in pl))
    F["plants_rows_with_note"] = sum(1 for r in pl if "note" in r)
    F["misses"] = [{"verifier": r["verifier"], "plant": r["plant"], "wave": r["wave"], "key_prefix": r["key_sha256"][:8],
                    "model": model_of.get(r["verifier"], "no usage row")} for r in pl if r["grade"] != "caught"]
    F["plants_by_model"] = {}
    for m in sorted(set(model_of.values())) + ["no usage row"]:
        sel = [r for r in pl if model_of.get(r["verifier"], "no usage row") == m]
        F["plants_by_model"][m] = {"n": len(sel), "caught": sum(1 for r in sel if r["grade"] == "caught"),
                                    "verifiers": len(set(r["verifier"] for r in sel))}
    pass_agents = set(p["agent"] for p in passes)
    usage_agents = set(u["agent"] for u in usage)
    plant_verifiers = set(r["verifier"] for r in pl)
    nousage = sorted(plant_verifiers - usage_agents)
    F["plant_verifiers_without_usage_row"] = {"names": nousage,
                                             "plant_rows": sum(1 for r in pl if r["verifier"] in nousage),
                                             "of_which_with_passes_row": [n for n in nousage if n in pass_agents]}

    # --- briefs, corrections, escalations ---
    F["briefs_by_wave"] = dict(collections.Counter(r["wave"] for r in rows["briefs"]))
    F["corrections"] = {"n": len(rows["corrections"]), "accepted": dict(collections.Counter(str(r["accepted"]) for r in rows["corrections"])),
                        "by_wave": dict(collections.Counter(r["wave"] for r in rows["corrections"]))}
    es = rows["escalations"]
    F["escalations"] = {"n": len(es), "test": sum(1 for e in es if e["test"]), "real": sum(1 for e in es if not e["test"]),
                        "means": dict(collections.Counter(e["means"] for e in es))}
    for label, sel in (("test", [e for e in es if e["test"]]), ("real", [e for e in es if not e["test"]])):
        lat = [(ts(e["answered"]) - ts(e["sent"])).total_seconds() for e in sel if "answered" in e]
        F["escalations"][label + "_latency_seconds"] = {
            "answered": len(lat), "unanswered": len(sel) - len(lat),
            "min": min(lat) if lat else None, "median": statistics.median(lat) if lat else None, "max": max(lat) if lat else None}
    F["escalations"]["real_rows"] = [{"from": e["from"], "wave": e["wave"],
                                      "latency_s": (ts(e["answered"]) - ts(e["sent"])).total_seconds() if "answered" in e else None}
                                     for e in es if not e["test"]]
    F["escalations"]["unanswered_rows"] = [{"from": e["from"], "test": e["test"], "wave": e["wave"]} for e in es if "answered" not in e]

    # --- agents without rows ---
    rec = C.show(lib, C.LIB_SHA, "docs/RECORD.md")
    leadmd = C.read_text(os.path.join(C.muse(a.repos), "ledger", "lead.md"))
    all_agents = set(usage_agents) | pass_agents | plant_verifiers | set(r["author"] for r in rows["briefs"]) \
        | set(r["by"] for r in rows["corrections"]) | set(r["from"] for r in es)
    all_agents.discard("lead")
    ag_rows = []
    for ag in sorted(all_agents):
        miss = []
        if ag not in usage_agents: miss.append("usage")
        if ag not in pass_agents: miss.append("passes")
        if not miss: continue
        ag_rows.append([ag, "+".join(miss), "yes" if ag in plant_verifiers else "no",
                        sum(1 for r in pl if r["verifier"] == ag),
                        ";".join(map(str, grep_lines(rec, ag)[:6])), ";".join(map(str, grep_lines(leadmd, ag)[:6]))])
    C.write_csv(os.path.join(C.DATA, "agents_without_rows.csv"),
                ["agent", "missing_from", "has_plant_rows", "plant_rows", "RECORD.md_lines@b78af18(first6)", "muse_ledger_lead.md_lines(first6)"], ag_rows)
    F["agents_without_rows_summary"] = {
        "agents_appearing_anywhere": len(all_agents),
        "missing_usage": sum(1 for r in ag_rows if "usage" in r[1]),
        "missing_passes": sum(1 for r in ag_rows if "passes" in r[1]),
        "missing_both": sum(1 for r in ag_rows if r[1] == "usage+passes"),
    }

    # --- toy ---
    tp = C.toy_plants(a.repos)
    ver_t = [r for r in tp if r.get("status") == "verdict"]
    F["toy"] = {
        "rows": len(tp), "by_status": dict(collections.Counter(r.get("status") for r in tp)),
        "verdict_plants": sum(r["plants"] for r in ver_t), "verdict_caught": sum(r["caught"] for r in ver_t),
        "verdict_rows_with_verifier_report": sum(1 for r in ver_t if r.get("verifier_report")),
        "verdict_extra_findings_total": sum(len(r.get("extra_findings", [])) for r in ver_t),
        "verdict_rows_with_extra_findings": sum(1 for r in ver_t if r.get("extra_findings")),
        "dispatched_distinct_copy_head": len(set(r["copy_head"] for r in tp if r.get("status") == "dispatched")),
        "dispatched_distinct_key_sha256": len(set(r["key_sha256"] for r in tp if r.get("status") == "dispatched")),
        "checked_by": dict(collections.Counter(r.get("checked_by") for r in tp)),
        "parcels_by_prefix": dict(collections.Counter(r["parcel"].split("-")[0] for r in ver_t)),
    }

    # --- the plan's section 4 figures (typed here as the plan's claims; recomputed values come from F) ---
    ub = F["tokens_by_model"]
    chk = [
        ("library commits", 221, F["library_commits"]["count"]),
        ("library last commit (author date, hh:mm)", "04:18", F["library_commits"]["last_author_date"][11:16]),
        ("toy commits", 224, F["toy_commits"]["count"]),
        ("toy last commit (hh:mm)", "16:39", F["toy_commits"]["last"][11:16]),
        ("usage rows", 128, F["library_row_counts"]["usage"]),
        ("passes rows", 131, F["library_row_counts"]["passes"]),
        ("plants rows", 195, F["library_row_counts"]["plants"]),
        ("briefs rows", 50, F["library_row_counts"]["briefs"]),
        ("corrections rows", 24, F["library_row_counts"]["corrections"]),
        ("escalations rows", 23, F["library_row_counts"]["escalations"]),
        ("fetches rows", 5, F["library_row_counts"]["fetches"]),
        ("wonder usage rows", 69, ub["muse-wonder-full-1.0"]["usage_rows"]),
        ("wonder input tokens", 733186697, ub["muse-wonder-full-1.0"]["input"]),
        ("wonder output tokens", 3972310, ub["muse-wonder-full-1.0"]["output"]),
        ("spark usage rows", 59, ub["muse-spark-1.3"]["usage_rows"]),
        ("spark input tokens", 677616961, ub["muse-spark-1.3"]["input"]),
        ("spark output tokens", 3289230, ub["muse-spark-1.3"]["output"]),
        ("tokens input+output", 1418065198, F["tokens_total"]["input_plus_output"]),
        ("cached tokens", 1379156504, F["tokens_total"]["cached"]),
        ("author passes", 31, F["passes_by_role"]["author"]),
        ("surveyor passes", 50, F["passes_by_role"]["surveyor"]),
        ("verifier passes", 46, F["passes_by_role"]["verifier"]),
        ("fixer passes", 4, F["passes_by_role"]["fixer"]),
        ("NOT READY", 37, F["verifier_verdicts"]["NOT READY"]),
        ("READY", 9, F["verifier_verdicts"]["READY"]),
        ("sent_back true rows", 15, F["sent_back_raw"]),
        ("plants caught", 187, F["plants_by_grade"]["caught"]),
        ("plants missed", 8, F["plants_by_grade"]["missed"]),
        ("graded_by lead", 195, F["plants_graded_by"].get("lead")),
        ("verifier passes on spark", 43, F["verifier_model_split"]["muse-spark-1.3"]),
        ("verifier passes on wonder", 3, F["verifier_model_split"]["muse-wonder-full-1.0"]),
        ("verifiers without usage row", 7, len(F["plant_verifiers_without_usage_row"]["names"])),
        ("their plant rows", 35, F["plant_verifiers_without_usage_row"]["plant_rows"]),
        ("test escalations", 11, F["escalations"]["test"]),
        ("real escalations", 12, F["escalations"]["real"]),
        ("rows checked_by integration", 65, F["plants_checked_by"].get("integration")),
        ("distinct key_sha256", 39, F["plants_distinct_key_sha256"]),
        ("toy dispatched rows", 44, F["toy"]["by_status"]["dispatched"]),
        ("toy verdict rows", 44, F["toy"]["by_status"]["verdict"]),
        ("toy lead_trim rows", 2, F["toy"]["by_status"]["lead_trim"]),
        ("toy plants in verdict rows", 220, F["toy"]["verdict_plants"]),
        ("toy caught", 220, F["toy"]["verdict_caught"]),
        ("toy total rows", 90, F["toy"]["rows"]),
    ]
    F["plan_s4_check"] = [{"figure": n, "plan_or_lead_value": p, "recomputed": r, "agrees": p == r} for n, p, r in chk]
    F["plan_s4_disagreements"] = [c for c in F["plan_s4_check"] if not c["agrees"]]
    print("plan s4 check:", len(chk), "figures,", len(F["plan_s4_disagreements"]), "disagree")

    trec = C.show(toy, C.TOY_SHA, "docs/RECORD.md")
    flat = re.sub(r"\s+", " ", trec)
    cum = []
    for m in re.finditer(r"cumulative (\d+)/(\d+) across (\d+) parcels", flat):
        cum.append({"caught": int(m.group(1)), "plants": int(m.group(2)), "parcels": int(m.group(3))})
    F["toy_record"] = {"lines": len(trec.splitlines()), "cumulative_statements": cum,
                       "75_of_75_statement": bool(re.search(r"75 planted defects, 75 caught", flat)),
                       "mentions_missed_or_not_caught": len(re.findall(r"missed|not caught|uncaught", flat))}
    print("toy record cumulative statements:", cum)

    json.dump(F, open(os.path.join(C.DATA, "figures.json"), "w", encoding="utf-8"), indent=1, sort_keys=True)
    print("rows", F["library_row_counts"])
    print("tokens total", F["tokens_total"]["input_plus_output"], "cached", F["tokens_total"]["cached"])
    print("sent_back raw", F["sent_back_raw"], "with later same-work author/fixer", F["sent_back_with_later_author_or_fixer_same_work"])
    print("plants", F["plants_by_grade"], "no-usage verifiers", len(nousage), F["plant_verifiers_without_usage_row"]["plant_rows"])
    print("escalations", {k: F["escalations"][k] for k in ("n", "test", "real")})
    print("toy", F["toy"]["by_status"], F["toy"]["verdict_plants"], F["toy"]["verdict_caught"])


main()
