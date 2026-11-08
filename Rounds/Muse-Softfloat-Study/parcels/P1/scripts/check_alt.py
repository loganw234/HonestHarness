"""Second route for the figures: raw-text regex and string counting, no json module.

Recounts from the jsonl text at b78af18 (and the toy file at 084f98b) the figures that
figures.py and recall.py produced from parsed rows, and compares. Prints one line per check.
"""
import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C


def lines(text):
    return [l for l in text.splitlines() if l.strip()]


def main():
    a = C.args()
    lib = C.lib_repo(a.repos)
    t = {n: C.show(lib, C.LIB_SHA, "docs/metrics/%s.jsonl" % n) for n in ("usage", "passes", "plants", "escalations")}
    checks = []

    def chk(name, alt, main_val):
        checks.append((name, alt, main_val, "OK" if alt == main_val else "DIFFERENT"))

    import json as _json  # only to read the first route's own output file figures.json
    F = _json.load(open(os.path.join(C.DATA, "figures.json"), encoding="utf-8"))
    chk("usage rows", len(lines(t["usage"])), F["library_row_counts"]["usage"])
    chk("plants caught (string count)", t["plants"].count('"grade": "caught"'), F["plants_by_grade"]["caught"])
    chk("plants missed (string count)", t["plants"].count('"grade": "missed"'), F["plants_by_grade"]["missed"])
    chk("passes role verifier", t["passes"].count('"role":"verifier"'), F["passes_by_role"]["verifier"])
    chk("passes role surveyor", t["passes"].count('"role":"surveyor"'), F["passes_by_role"]["surveyor"])
    chk("sent_back true (string count)", t["passes"].count('"sent_back":true'), F["sent_back_raw"])
    chk("NOT READY", t["passes"].count('"verdict":"NOT READY"'), F["verifier_verdicts"]["NOT READY"])
    out = sum(int(x) for x in re.findall(r'"output_tokens":(\d+)', t["usage"]))
    inp = sum(int(x) for x in re.findall(r'"input_tokens":(\d+)', t["usage"]))
    chk("tokens input+output (regex sum)", out + inp, F["tokens_total"]["input_plus_output"])
    cac = sum(int(x) for x in re.findall(r'"cached_tokens":(\d+)', t["usage"]))
    chk("cached tokens (regex sum)", cac, F["tokens_total"]["cached"])
    sp = [(m.group(1)) for m in re.finditer(r'"model":"(muse-spark-1.3)"', t["usage"])]
    chk("spark usage rows", len(sp), F["tokens_by_model"]["muse-spark-1.3"]["usage_rows"])
    chk("escalations test true", t["escalations"].count('"test": true'), F["escalations"]["test"])
    chk("checked_by integration", t["plants"].count('"checked_by": "integration"'), F["plants_checked_by"]["integration"])
    for w in ("wave5", "wave6", "postseal", "wave4"):
        chk("plants rows wave " + w, t["plants"].count('"wave": "%s"' % w), F["plants_by_wave"][w]["n"])
    # verifiers without usage rows, by set difference of names in raw text
    pv = set(re.findall(r'"verifier": "([^"]+)"', t["plants"]))
    ua = set(re.findall(r'"agent":"([^"]+)"', t["usage"]))
    nu = sorted(pv - ua)
    chk("verifiers on plant rows without a usage row", len(nu), len(F["plant_verifiers_without_usage_row"]["names"]))
    # class counts from the csv with the csv module (not the recall tables)
    rows = list(csv.DictReader(open(os.path.join(C.DATA, "plants_classed.csv"), encoding="utf-8")))
    rc = {r["class"]: r for r in csv.DictReader(open(os.path.join(C.DATA, "recall_by_class.csv"), encoding="utf-8"))}
    for cls in rc:
        n = sum(1 for r in rows if r["class"] == cls)
        c = sum(1 for r in rows if r["class"] == cls and r["grade"] == "caught")
        chk("class %s n/caught" % cls, "%d/%d" % (n, c), "%s/%s" % (rc[cls]["n"], rc[cls]["caught"]))
    toy = C.show(C.toy_repo(a.repos), C.TOY_SHA, "docs/metrics/plants.jsonl")
    chk("toy rows", len(lines(toy)), F["toy"]["rows"])
    chk("toy verdict caught-5 rows", toy.count('"caught": 5'), 44)
    bad = 0
    for n, alt, m, s in checks:
        print("%-45s second route %-12s first route %-12s %s" % (n, alt, m, s))
        bad += s != "OK"
    print("checks:", len(checks), "different:", bad)


main()
