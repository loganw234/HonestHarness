"""Round 1's table, computed by script from the committed records.

    python tools/table.py [--select PATH] [--json PATH]

The batches that enter are named in a selection file, each batch left out with
its reason, and the script refuses a live batch the file does not name: no
batch is pooled, or dropped, unseen. Each suite pools its own records with its
own function: QS1's metrics(), QS6's table() and QS4's table(). This script
selects the records, calls those, and adds each batch's runs, statuses,
dropped attempts, tokens and cost.

Cost is given twice. "Computed" is the meter's, at the price table's rate for
the period each reply arrived in. "Billed" is the balance's change, read at
the batch's close or at its last recheck, to two decimals. Where they differ
(a holiday the table does not model, a slow balance), the provider's usage
export is the authority, and the table says so rather than choosing.

Limits, each stated by the behaviour it concedes:
- the table holds what the records say. A record that matches its schema and
  says something false passes through;
- a batch's billed figure has the balance's precision, two decimals, so a
  batch that cost less than a cent shows 0.00;
- the selection file's reasons are the lead's words, judged by its verifier;
- a batch is listed from its summary line in batches.jsonl. One interrupted
  before its summary (Ctrl-C, or a job's limit) is in the spend file only, so
  its metered cost is outside the table's total: the spend file's own sum is
  the round's metered spend (verifier-I's R2).
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

DEFAULT_SELECT = ROOT / "Rounds" / "HonestHarness-R1" / "table-batches.json"


class SelectionError(Exception):
    """The selection file and the records disagree: no table is drawn."""


def read_lines(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def load(records_dir: Path) -> tuple[list[dict], list[dict]]:
    """Every run record, and every line of batches.jsonl."""
    runs = []
    for p in sorted((records_dir / "runs").glob("*.jsonl")):
        runs.extend(read_lines(p))
    return runs, read_lines(records_dir / "batches.jsonl")


def select(runs: list[dict], lines: list[dict], selection: dict) -> tuple[list[dict], dict]:
    """The run records of the included batches, and each batch's summary line.
    Refuses a live batch with runs that the selection does not name, a batch
    named twice or named but absent, and an included batch whose run records do
    not number its summary's runs."""
    include, exclude = selection.get("include") or {}, selection.get("exclude") or {}
    both = sorted(set(include) & set(exclude))
    if both:
        raise SelectionError(f"named both included and excluded: {both}")
    summaries = {x["batch"]: x for x in lines if x.get("kind") == "batch"}
    named = set(include) | set(exclude)
    unnamed = sorted(b for b, s in summaries.items() if s.get("live") and s.get("runs") and b not in named)
    if unnamed:
        raise SelectionError(f"live batches with runs that the selection does not name: {unnamed}")
    absent = sorted(b for b in named if b not in summaries)
    if absent:
        raise SelectionError(f"named but not in batches.jsonl: {absent}")
    by_batch: dict[str, list[dict]] = {}
    for r in runs:
        by_batch.setdefault(r["batch"], []).append(r)
    for b in include:
        if len(by_batch.get(b, [])) != summaries[b]["runs"]:
            raise SelectionError(f"{b}: {len(by_batch.get(b, []))} run records, but its summary "
                                 f"says {summaries[b]['runs']} runs")
    return [r for b in include for r in by_batch.get(b, [])], summaries


def billed(lines: list[dict], batch: str) -> tuple[str | None, str | None]:
    """A batch's billed figure and reconciliation: its last recheck's, or else
    its summary's."""
    last = None
    for x in lines:
        if x.get("batch") == batch and x.get("kind") in ("batch", "recheck"):
            last = x
    return (None, None) if last is None else (last.get("billed_usd"), last.get("reconciliation"))


def batch_rows(runs: list[dict], lines: list[dict], summaries: dict, selection: dict) -> list[dict]:
    """Every live batch with a summary line, included or not, with its cost and
    what its runs met."""
    include, exclude = selection.get("include") or {}, selection.get("exclude") or {}
    by_batch: dict[str, list[dict]] = {}
    for r in runs:
        by_batch.setdefault(r["batch"], []).append(r)
    rows = []
    for b, s in summaries.items():
        if not s.get("live"):
            continue
        rs = by_batch.get(b, [])
        bill, recon = billed(lines, b)
        rows.append({
            "batch": b, "suite": s.get("suite"), "suite_version": s.get("suite_version"),
            "thinking": sorted({r.get("thinking") for r in rs}) if rs else [],
            "runs": s.get("runs"), "stopped_for": s.get("stopped_for"),
            "statuses": dict(Counter(r["outcome"]["status"] for r in rs)),
            "unmetered_attempts": s.get("unmetered_attempts"),
            "cache_hit": sum(r["usage"]["cache_hit"] for r in rs),
            "cache_miss": sum(r["usage"]["cache_miss"] for r in rs),
            "output": sum(r["usage"]["output"] for r in rs),
            "computed_usd": s.get("computed_usd"), "billed_usd": bill, "reconciliation": recon,
            "entered": b in include,
            "why": include.get(b) or exclude.get(b) or "no runs, so not named"})
    return rows


def qs1_rows(selected: list[dict]) -> list[dict]:
    from qs.suites import qs1
    groups: dict = {}
    for r in selected:
        if r.get("suite") == "qs1":
            groups.setdefault((r.get("thinking"), r.get("suite_version")), []).append(r)
    rows = []
    for (thinking, version), rs in sorted(groups.items(), key=lambda kv: (str(kv[0][0]), str(kv[0][1]))):
        m = qs1.metrics([(r["outcome"].get("data") or {}) for r in rs])
        rows.append({"thinking": thinking, "suite_version": version, "runs": len(rs),
                     "statuses": dict(Counter(r["outcome"]["status"] for r in rs)), **m})
    return rows


def qs6_rows(selected: list[dict]) -> list[dict]:
    from qs.suites import qs6
    return qs6.table([r for r in selected if str(r.get("suite", "")).startswith("qs6-")])


def qs4_rows(selected: list[dict]) -> dict | None:
    recs = [r for r in selected if str(r.get("suite", "")).startswith("qs4-")]
    if not recs:
        return None
    from qs.suites import qs4
    return qs4.table(recs, qs4.load_judgements())


def compute(records_dir: Path, selection: dict) -> dict:
    runs, lines = load(records_dir)
    selected, summaries = select(runs, lines, selection)
    batches = batch_rows(runs, lines, summaries, selection)
    total = sum((Decimal(b["computed_usd"] or "0") for b in batches), Decimal("0"))
    return {"qs1": qs1_rows(selected), "qs6": qs6_rows(selected), "qs4": qs4_rows(selected),
            "batches": batches, "computed_usd_all_live_batches": str(total)}


# -- Markdown ---------------------------------------------------------------------------------
def _frac(num, den) -> str:
    return "n/a" if not den else f"{num}/{den} ({num / den:.3f})"


def _counts(d: dict) -> str:
    return ", ".join(f"{k} {v}" for k, v in sorted(d.items())) or "none"


def _num(x) -> str:
    """None as n/a (a batch from before a field existed), and a whole float
    without its .0."""
    if x is None:
        return "n/a"
    return str(int(x)) if isinstance(x, float) and x.is_integer() else str(x)


def markdown(t: dict) -> str:
    out = ["## QS1", "",
           "| thinking | suite version | runs | statuses | trigger F1 (tp/fp/fn/tn) | agreement | "
           "schema valid | reasoning emitted |",
           "|---|---|---|---|---|---|---|---|"]
    for r in t["qs1"]:
        tr, sc, rs = r["trigger"], r["schema"], r["reasoning"]
        f1 = "n/a" if tr["f1"] is None else f"{tr['f1']:.3f}"
        out.append(f"| {'on' if r['thinking'] else 'off'} | {r['suite_version']} | {r['runs']} | "
                   f"{_counts(r['statuses'])} | {f1} ({tr['tp']}/{tr['fp']}/{tr['fn']}/{tr['tn']}) | "
                   f"{_frac(tr['tp'] + tr['tn'], tr['n'])} | {_frac(sc['valid'], sc['calls'])} | "
                   f"{_frac(rs['emitted'], rs['turns'])} |")
    out += ["", "## QS6", "",
            "| cut | set | thinking | exact | overclaimed | not scored | median prompt tokens |",
            "|---|---|---|---|---|---|---|"]
    for r in t["qs6"]:
        out.append(f"| {r['cut']} | {r['set']} | {'on' if r['thinking'] else 'off'} | "
                   f"{_frac(r['value']['exact'], r['accuracy_denominator'])} | "
                   f"{_frac(r['not_in_input']['overclaim'], r['overclaim_denominator'])} | "
                   f"{_counts(r['not_scored'])} | {_num(r['median_prompt_tokens'])} |")
    if t["qs4"]:
        out += ["", "## QS4", "",
                "| run | item | status | plants caught, screen | plants caught, judged | findings | "
                "round 6's in-view findings located | read | output | cost |",
                "|---|---|---|---|---|---|---|---|---|---|"]
        for rid, r in t["qs4"]["rows"].items():
            out.append(f"| {rid} | {r['item']} | {r['status']} | {r['plants_caught_screen']} | "
                       f"{r['plants_caught_judged']} | {r['findings']} | "
                       f"{r['r6_in_view_located']}/{r['r6_in_view']} | {r['read']} | {r['output']} | "
                       f"{r['cost_usd']} |")
    out += ["", "## Batches", "",
            "| batch | thinking | entered | runs | statuses | dropped attempts | read (hit/miss) | "
            "output | computed $ | billed $ | reconciliation | why |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for b in t["batches"]:
        thinking = "/".join("on" if x else "off" for x in b["thinking"]) or "n/a"
        out.append(f"| {b['batch']} | {thinking} | {'yes' if b['entered'] else 'no'} | {b['runs']} | "
                   f"{_counts(b['statuses'])} | {_num(b['unmetered_attempts'])} | "
                   f"{b['cache_hit']}/{b['cache_miss']} | {b['output']} | {b['computed_usd']} | "
                   f"{b['billed_usd']} | {b['reconciliation']} | {b['why']} |")
    out += ["", f"Computed over every live batch with a summary line: "
                f"${t['computed_usd_all_live_batches']}. A batch interrupted before its summary is in "
                "the spend file only. Billed figures are the balance's, to two decimals; the usage "
                "export is the authority."]
    return "\n".join(out) + "\n"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--select", default=str(DEFAULT_SELECT))
    ap.add_argument("--records", default=str(ROOT / "records"))
    ap.add_argument("--json", metavar="PATH")
    a = ap.parse_args(argv)
    selection = json.loads(Path(a.select).read_text(encoding="utf-8"))
    try:
        t = compute(Path(a.records), selection)
    except SelectionError as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 3
    if a.json:
        Path(a.json).write_text(json.dumps(t, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    sys.stdout.write(markdown(t))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
