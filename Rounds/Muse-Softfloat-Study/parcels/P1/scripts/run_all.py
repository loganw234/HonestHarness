"""Run every P1 script in order, so every table in data/ can be remade.

    python -I scripts/run_all.py --repos <repos> [--scratch <scratch>]

The hand inputs (data/class_input.csv, model_map.csv, regrade_input.csv,
toy_regrade_input.csv, findings.csv, sent_back_evidence.csv, attempts_input.csv,
earlier_input.csv) are read, not remade: they are my readings of the sources.
"""
import os
import subprocess
import sys

ORDER = ["keycheck", "keyfiles", "figures", "classify", "recall", "sample", "toy_sample", "regrade_join",
         "passes_check", "attempts", "earlier", "check_alt", "make_tables"]


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    args = sys.argv[1:]
    for name in ORDER:
        extra = args if name != "sample" else args  # sample.py writes its key sheet only if --scratch is given
        print("== " + name)
        r = subprocess.run([sys.executable, "-I", os.path.join(here, name + ".py")] + extra)
        if r.returncode != 0:
            print("stopped: %s exited %d" % (name, r.returncode))
            sys.exit(r.returncode)


main()
