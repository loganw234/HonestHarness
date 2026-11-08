"""Parse the case report's proposals P1-P18 into data/proposals_raw.csv.

Reads <muse>/CASE-REPORT-muse-softfloat.md as a file, from the heading
'What the method files should say differently' to the next '## ' heading.
Usage: python -I proposals.py --repos <repos> --scratch <scratch>
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import args_roots, read_file, write_csv

ns = args_roots()
path = os.path.join(ns.muse, "CASE-REPORT-muse-softfloat.md")
lines = read_file(path).splitlines()
start = next(i for i, l in enumerate(lines) if l.startswith("## What the method files should say differently"))
end = next(i for i in range(start + 1, len(lines)) if lines[i].startswith("## "))

group = ""
rows = []
cur = None
for i in range(start + 1, end):
    l = lines[i]
    m_group = re.match(r"\*\*(.+?)\*\*\s*$", l)
    if m_group:
        group = m_group.group(1)
        continue
    m = re.match(r"- \*\*P(\d+)\. ", l)
    if m:
        if cur:
            rows.append(cur)
        cur = {"id": "P" + m.group(1), "group": group, "first_line": i + 1, "text": l}
        continue
    if cur is not None:
        if l.startswith("  ") and l.strip():
            cur["text"] += " " + l.strip()
        else:
            rows.append(cur)
            cur = None
if cur:
    rows.append(cur)

out = []
for r in rows:
    t = " ".join(r["text"].split())
    # the case report's label is the parenthesis that follows the bold text;
    # the bracketed number after it is the report's pointer to its evidence note.
    m = re.search(r"\*\*\s*\(([^)]*)\)\.?\s*(\[[^\]]*\])?", t)
    label_text = m.group(1) if m else ""
    ref = m.group(2) if m and m.group(2) else ""
    low = label_text.lower()
    label = ""
    for k in ("new", "reinforcement", "extension", "adoption"):
        if low.startswith(k) or (" " + k) in (" " + low):
            label = k
            break
    out.append([r["id"], r["group"], r["first_line"], label, label_text, ref, t])

ids = [r[0] for r in out]
assert ids == ["P%d" % n for n in range(1, 19)], ids
write_csv(os.path.join(ns.data, "proposals_raw.csv"),
          ["id", "group", "case_report_line", "case_report_label", "label_text", "evidence_ref", "text"], out)
print("proposals parsed:", len(out), "from lines %d-%d of the case report" % (start + 1, end))
for r in out:
    print(r[0], "|", r[3], "|", r[4], "|", r[5])
