"""Task 6: earlier rounds with planted copies.

data/earlier_input.csv is my reading of each record. This script reads the sources at their
commits (ParcelRound f42242e and 894d125, HonestHarness main) or as the round-2 ledger files,
checks the phrase I cite at its line, counts the lines matching "plant" in each case study,
and counts plants in the archived keys (round 6 and round 1 zips). Writes data/earlier_rounds.csv.
"""
import io
import json
import os
import re
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

PR_FILES = {"pr/cs1.md": ("f42242e", "CASE-STUDY.md"), "pr/cs2.md": ("f42242e", "CASE-STUDY-2.md"), "pr/cs3.md": ("f42242e", "CASE-STUDY-3.md"),
            "pr/cs4.md": ("f42242e", "CASE-STUDY-4.md"), "pr/cs5.md": ("f42242e", "CASE-STUDY-5.md"),
            "pr/cs6.md": ("f42242e", "CASE-STUDY-6.md"), "pr/cs7.md": ("894d125", "CASE-STUDY-7.md")}


def main():
    a = C.args()
    pr = os.path.join(a.repos, "ParcelRound")
    hh = os.path.join(a.repos, "HonestHarness")
    texts = {}
    for k, (sha, path) in PR_FILES.items():
        texts[k] = C.show(pr, sha, path)
    texts["pr/hh1.md"] = C.show(hh, "main", "Rounds/HonestHarness-R1/CASE-STUDY.md")
    texts["r2/lead.md"] = C.read_text(os.path.join(a.repos, "honestharness-r2-ledger", "lead.md"))
    plant_lines = {k: sum(1 for l in v.splitlines() if re.search(r"plant", l, re.I)) for k, v in texts.items()}
    # key rows in archives
    z6 = zipfile.ZipFile(io.BytesIO(C.show(pr, "f42242e", "archive/round6-ledger.zip", binary=True)))
    k6 = [json.loads(z6.read(n).decode("utf-8")) for n in z6.namelist() if "/keys/" in n and n.endswith(".json")]
    z1 = zipfile.ZipFile(io.BytesIO(C.show(hh, "main", "Rounds/HonestHarness-R1/round1-ledger.zip", binary=True)))
    k1 = [json.loads(z1.read(n).decode("utf-8")) for n in z1.namelist() if "/keys/" in n and n.endswith(".json")]
    keydir = os.path.join(a.repos, "honestharness-r2-ledger", "keys")
    k2 = [json.load(open(os.path.join(keydir, f), encoding="utf-8")) for f in sorted(os.listdir(keydir)) if f.startswith("key-")]
    key_rows = {"ParcelRound 6": (len(k6), sum(len(k["plants"]) for k in k6)),
                "HonestHarness R1 (this round's own planted copies)": (len(k1), sum(len(k["plants"]) for k in k1)),
                "HonestHarness R2": (len(k2), sum(len(k["plants"]) for k in k2))}
    rows, ok = [], 0
    for r in C.read_csv(os.path.join(C.DATA, "earlier_input.csv")):
        f, ln, ph = r["source_file"], int(r["source_line"]), r["source_phrase"]
        if ph:
            line = texts[f].splitlines()[ln - 1] if ln <= len(texts[f].splitlines()) else ""
            v = "yes" if ph in line else "NO"
        else:
            v = "n/a (count of plant lines below)"
        ok += v == "yes"
        kr = key_rows.get(r["round"], ("", ""))
        rows.append([r["round"], r["harness"], r["lead"], r["parcels"], r["verifiers"], r["planter"], r["grader"], r["plants"], r["caught"],
                     r["missed"], r["miss_shapes"], "%s line %s" % (f, ln) if ph else f, v, plant_lines.get(f, ""), kr[0], kr[1]])
    C.write_csv(os.path.join(C.DATA, "earlier_rounds.csv"),
                ["round", "harness", "lead", "parcels", "verifiers", "planter", "grader", "plants", "caught", "missed", "miss_shapes",
                 "source", "cited_phrase_found", "lines_matching_plant_in_source", "archived_key_files", "archived_key_rows"], rows)
    print("cited phrases found:", ok, "of", sum(1 for r in rows if r[12] == "yes" or r[12] == "NO"))
    print("lines matching 'plant':", {k: v for k, v in plant_lines.items()})
    print("archived keys (files, rows):", key_rows)


main()
