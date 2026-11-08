"""Second, looser stem set for every clause marked ABSENT (or ADJACENT only).

A negative result from clauses.json's stems is not enough: the first pass missed
'The scoped re-check after a fix is the default' for P4 (see ANALYSIS.md). So
each ABSENT clause is searched again with wide stems over the method files
(tier M) and the kit's top-level files, and every line is listed for reading.

Reads data/marks.csv, writes data/loose_searches.csv.
Usage: python -I loose.py --repos <repos> --scratch <scratch>
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import args_roots, read_csv, write_csv
from corpus import entries

LOOSE = {
    ("P1", "c1"): r"provenance|first (?:act|thing|entry|line)",
    ("P1", "c2"): r"\bHEAD\b|rev-parse|\btip\b",
    ("P1", "c3"): r"\bcopy\b.{0,40}\b(?:only|unique)|\bonly\b.{0,40}\bcopy\b",
    ("P2", "c1"): r"allow|evidence path|named path|\bworld\b",
    ("P3", "c2"): r"\bfield|recount|each (?:count|number|figure)",
    ("P3", "c3"): r"expected|\bplants?\b",
    ("P4", "c1"): r"re-?check|scoped|scope it",
    ("P4", "c2"): r"independent|\bfresh\b|second verifier|other verifier",
    ("P5", "c2"): r"re-?count|recomput|re-?derive|re-?read",
    ("P5", "c3"): r"adheren|wave (?:close|boundary)|each wave|every wave",
    ("P5", "c4"): r"lead.{0,30}parcel|parcel.{0,30}lead",
    ("P6", "c1"): r"report.{0,30}(?:file|path)|(?:file|path).{0,30}report",
    ("P6", "c2"): r"summary|final message|compact",
    ("P7", "c1"): r"\bvoid|\bdead\b|abandon|discard",
    ("P7", "c2"): r"untrust|clean checkout|fresh checkout|clean clone|fresh clone",
    ("P7", "c3"): r"retry|redo|re-?dispatch|valid attempt",
    ("P8", "c1"): r"memory|wall|process|ceiling|ulimit|\bGB\b|\bMB\b",
    ("P9", "c3"): r"mechanism|seal",
    ("P10", "c1"): r"registry|every surface|surfaces|literal",
    ("P11", "c3"): r"newest|exclud|cutoff|as of",
    ("P12", "c3"): r"promot|same parcel|scratch",
    ("P13", "c2"): r"worktree|resolve|layout|main checkout",
    ("P14", "c4"): r"tolerant|lenient|verif.{0,20}(?:command|shell)",
    ("P16", "c1"): r"merge.{0,40}(?:record|row|entry)|(?:record|row|entry).{0,40}merge",
    ("P16", "c3"): r"refresh|backfill|end of the round|catch-up",
    ("P17", "c3"): r"never commit|\basset|third.party|silent",
    ("P18", "c2"): r"walk|judge|follow|reader",
}

ns = args_roots()
marks = read_csv(os.path.join(ns.data, "marks.csv"))
absent = {(m["proposal"], m["clause"]) for m in marks if m["mark"] in ("ABSENT", "ADJACENT")}
# clauses with a stronger mark elsewhere are not searched again
strong = {(m["proposal"], m["clause"]) for m in marks if m["mark"] not in ("ABSENT", "ADJACENT")}
todo = sorted(absent - strong, key=lambda k: (int(k[0][1:]), k[1]))
ents, _ = entries(ns)
rows = []
for key in todo:
    rx = re.compile(LOOSE[key], re.I) if key in LOOSE else None
    n_m = n_k = 0
    if rx is None:
        continue
    for sid, tier, src, commit, path, text in ents:
        if tier in "CN":
            continue
        if tier == "K" and (sid.startswith("KIT:examples/") or sid.startswith("KIT:tools/") or sid == "KIT:MANIFEST.txt"):
            continue
        for i, l in enumerate(text.splitlines(), 1):
            if rx.search(l):
                rows.append([key[0], key[1], tier, sid, i, l.strip()[:200]])
write_csv(os.path.join(ns.data, "loose_searches.csv"),
          ["proposal", "clause", "tier", "source_id", "line", "text"], rows)
from collections import Counter
c = Counter((r[0], r[1]) for r in rows)
print("clauses searched:", len(todo), "| lines listed:", len(rows))
print({"%s.%s" % k: v for k, v in sorted(c.items(), key=lambda kv: (int(kv[0][0][1:]), kv[0][1]))})
