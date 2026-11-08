"""Task 3, toy part: draw up to 10 toy copies with the same seed.

The toy's keys are not in any folder its record names (data/keycheck.csv: 0 of 44 toy
key hashes match a file in the permitted keys folder), so a key-based re-grade is not
possible. The sample is of copies; data/toy_regrade_input.csv records, per copy, what the
lead's ledger prose lists as planted (where it lists them) and what the verifier's report
names. Writes data/toy_sample_blind.csv.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C


def main():
    a = C.args()
    rng = random.Random(C.SEED)
    toy = C.toy_plants(a.repos)
    disp = {r["parcel"]: r for r in toy if r.get("status") == "dispatched"}
    ver = {r["parcel"]: r for r in toy if r.get("status") == "verdict"}
    names = sorted(ver)
    pick = rng.sample(names, 10)
    rows = []
    for i, p in enumerate(sorted(pick), 1):
        rows.append(["T%02d" % i, p, disp[p]["copy_head"][:7], disp[p]["key_sha256"][:8], ver[p]["plants"], ver[p]["caught"],
                     ver[p]["verifier_report"], len(ver[p].get("extra_findings", []))])
    C.write_csv(os.path.join(C.DATA, "toy_sample_blind.csv"),
                ["sample_id", "parcel", "copy_head7", "key_prefix", "plants", "lead_caught", "verifier_report", "extra_findings"], rows)
    print("toy copies sampled:", len(rows), [r[1] for r in rows])


main()
