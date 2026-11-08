"""Task 3: join my blind grades (data/regrade_input.csv) to the lead's grades and measure agreement.

My grades were written from the hash-checked keys and the verifiers' own reports before
this script attaches the lead's grade. Writes data/regrade.csv (library rows, then toy rows)
and prints agreement counts.
"""
import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C


def main():
    a = C.args()
    lib = C.lib_jsonl(a.repos, "plants")
    cls = {int(r["row"]): r for r in C.read_csv(os.path.join(C.DATA, "plants_class_blind.csv"))}
    kc = {r["sha256_prefix"]: r for r in C.read_csv(os.path.join(C.DATA, "keycheck.csv")) if r["kind"] == "final"}
    blind = C.read_csv(os.path.join(C.DATA, "sample_blind.csv"))
    mine = {r["sample_id"]: r for r in C.read_csv(os.path.join(C.DATA, "regrade_input.csv"))}
    assert set(mine) == set(b["sample_id"] for b in blind), "every sampled plant needs my grade"
    rows, tally = [], collections.Counter()
    dis = []
    for b in blind:
        i = int(b["plants_row"])
        lead = lib[i - 1]["grade"]
        m = mine[b["sample_id"]]
        if m["my_grade"] == "unclear":
            agree = "not comparable (unclear)"
        else:
            agree = "yes" if m["my_grade"] == lead else "NO"
        tally[(b["stratum"].split(":")[0], m["my_grade"], lead)] += 1
        if agree != "yes":
            dis.append((b["sample_id"], b["verifier"], b["plant"], m["my_grade"], lead))
        rows.append(["library", b["sample_id"], b["stratum"], b["wave"], b["verifier"], b["plant"], b["class"], b["key_prefix"],
                     "yes" if b["key_prefix"] in kc else "NO", m["my_grade"], lead, agree, m["evidence_file"], m["evidence_line"], m["note"]])
    toy_blind = C.read_csv(os.path.join(C.DATA, "toy_sample_blind.csv"))
    toy_mine = {r["sample_id"]: r for r in C.read_csv(os.path.join(C.DATA, "toy_regrade_input.csv"))}
    for t in toy_blind:
        m = toy_mine[t["sample_id"]]
        rows.append(["toy", t["sample_id"], "copy", "", t["parcel"], "", "", t["key_prefix"], "NO key available", "count only: " + m["defects_named_by_report"],
                     "%s/%s caught, %s extra" % (t["lead_caught"], t["plants"], t["extra_findings"]),
                     "consistent" if m["consistent"] == "yes" else "NOT consistent", t["verifier_report"], m["report_lines"], m["note"]])
    C.write_csv(os.path.join(C.DATA, "regrade.csv"),
                ["project", "sample_id", "stratum", "wave", "verifier_or_parcel", "plant", "class", "key_prefix", "key_hash_verified",
                 "p1_grade", "lead_grade", "agree", "evidence_file_under_muse", "evidence_line", "note"], rows)
    lib_rows = [r for r in rows if r[0] == "library"]
    for st in ("miss", "catch"):
        sel = [r for r in lib_rows if r[2].startswith(st)]
        print(st, "n=%d" % len(sel), dict(collections.Counter(r[11] for r in sel)))
    print("library total n=%d agree=%d disagree=%d not comparable=%d" % (
        len(lib_rows), sum(1 for r in lib_rows if r[11] == "yes"), sum(1 for r in lib_rows if r[11] == "NO"),
        sum(1 for r in lib_rows if r[11].startswith("not"))))
    print("all sampled keys hash-verified:", all(r[8] == "yes" for r in lib_rows))
    print("disagreements / not comparable:", dis)
    print("toy copies consistent:", sum(1 for r in rows if r[0] == "toy" and r[11] == "consistent"), "of", sum(1 for r in rows if r[0] == "toy"))


main()
