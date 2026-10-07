"""The lead's live entry point: the only place live mode is switched on.

    python tools/live.py --probe
    python tools/live.py <module>:<SuiteClass> [--repeats N] [--thinking on|off]
                         [--effort low|high|max] [--endpoint NAME] [--ceiling USD]
                         [--allow-peak] [--peak-margin MINUTES] [--settle SECONDS]
                         [--acknowledge BATCH] [--max-unmetered N]
                         [--retry-delays S,S,...] [--concurrent]
    python tools/live.py --recheck

--probe runs an empty batch: the balance read, the model list, one identity
probe, the balance read again and the reconciliation. It is the cheapest live
step there is, and the first one of the round. It costs about $0.00001, too
little to move a two-decimal balance, so it cannot test the balance's
precision or how soon a bill shows; the first batch that moves the balance by
several cents does, with a long --settle and a --recheck after it.

Every batch goes through the runner and the spending guard: a worst case that
does not fit the ceiling's remainder or the balance is refused before anything
is spent, and a batch is refused inside the provider's peak window, or within
the margin before one, unless --allow-peak is given. A batch whose
reconciliation is not ok holds the next one: --recheck reads the balance again
and reconciles the last batch anew, and --acknowledge BATCH lifts the hold by
naming that batch. Errors are printed redacted, with an exit status that says
which kind they are. Parcels never run this file; their tests use the fake.

--max-unmetered N is the batch's allowance of attempts the server closes with
no reply (3 when not given). Such an attempt is retried, once for each of the
call's retry delays. The batch stops at the Nth, or sooner, when one call
fails once more than it has delays; at N = 1 nothing is retried. The
reservation covers N calls more, each the dearest single call at either
period, since each may be billed without a meter reading.

--retry-delays S,S,... are those delays, in seconds, one per retry (2,5 when
not given: two retries). More delays retry a call more often; the batch's
allowance still bounds the attempts, and the reservation does not change.

--concurrent marks a batch run beside others from the same balance: it is
not reconciled alone and holds nothing, and the lead reconciles the batches
together afterwards.

The spend file is this checkout's, records/spend.jsonl. Round 1's live runs
were made from one checkout until its concurrent lanes, each a clone with its
own records; their spend, run records and batch lines are merged into this
checkout's afterwards, so one file holds the round's spend.
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from datetime import timedelta  # noqa: E402

from qs import registry  # noqa: E402
from qs.guard import Refused, SpendGuard  # noqa: E402
from qs.prices import PriceTable  # noqa: E402
from qs.suite import (DEFAULT_RETRY_DELAYS, MAX_UNMETERED_PER_BATCH, Caps, Item,  # noqa: E402
                      MeterMismatch, Runner, Suite)

DEFAULT_CEILING = "250"   # Logan, 2026-10-06: the pilot testing's ceiling


class Probe(Suite):
    """No items: the batch is the balance reads, the model list and the probe."""
    name = "probe"
    version = "probe-1"
    caps = Caps(max_prompt_tokens=1, max_output_tokens=1, max_call_prompt_tokens=1)

    def items(self) -> list[Item]:
        return []

    def run_item(self, ctx, item):  # pragma: no cover - never called
        raise AssertionError("the probe suite has no items")


def load_suite(spec: str) -> Suite:
    module, _, cls = spec.partition(":")
    return getattr(importlib.import_module(module), cls)()


def _at_least_one(value: str) -> int:
    n = int(value)
    if n < 1:
        raise argparse.ArgumentTypeError("must be 1 or more")
    return n


def _delays(value: str) -> tuple[float, ...]:
    """One to six waits, each from 0 to 120 seconds, separated by commas."""
    try:
        out = tuple(float(x) for x in value.split(","))
    except ValueError:
        raise argparse.ArgumentTypeError("give seconds separated by commas, such as 2,5,15") from None
    if not 1 <= len(out) <= 6 or any(not 0 <= d <= 120 for d in out):
        raise argparse.ArgumentTypeError("give one to six delays, each from 0 to 120 seconds")
    return out


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("suite", nargs="?")
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--endpoint", default="deepseek-flash")
    ap.add_argument("--repeats", type=int, default=1)
    ap.add_argument("--thinking", choices=["on", "off"], default="on")
    ap.add_argument("--effort", choices=["low", "high", "max"])
    ap.add_argument("--ceiling", default=DEFAULT_CEILING)
    ap.add_argument("--allow-peak", action="store_true")
    ap.add_argument("--peak-margin", type=int, default=10, metavar="MINUTES")
    # How soon the balance shows a bill is undocumented (D18): an open point
    # the first batch that moves the balance settles.
    ap.add_argument("--settle", type=float, default=5.0)
    ap.add_argument("--acknowledge", metavar="BATCH")
    ap.add_argument("--recheck", action="store_true")
    # Attempts the server may close with no reply before the batch stops; the
    # reservation covers this many calls more (the round's ledger, 20:01:46).
    ap.add_argument("--max-unmetered", type=_at_least_one, default=MAX_UNMETERED_PER_BATCH,
                    metavar="N")
    # The wait before each retry of a call closed with no reply: as many
    # retries as delays (the round's ledger, 08:57:42 and 08:58:08).
    ap.add_argument("--retry-delays", type=_delays, default=DEFAULT_RETRY_DELAYS,
                    metavar="S,S,...")
    # Logan, 2026-10-07: exact per-batch tracking may go, for parallel runs.
    ap.add_argument("--concurrent", action="store_true")
    return ap


def make_runner(a: argparse.Namespace, ep, prices: PriceTable, guard: SpendGuard) -> Runner:
    return Runner(ep, prices, guard, records_dir=ROOT / "records",
                  transcripts_dir=ROOT / "transcripts", live=True,
                  allow_peak=a.allow_peak, settle_seconds=a.settle,
                  peak_margin=timedelta(minutes=a.peak_margin), max_unmetered=a.max_unmetered,
                  retry_delays=a.retry_delays, concurrent=a.concurrent)


def main(argv: list[str]) -> int:
    ap = parser()
    a = ap.parse_args(argv)
    if not (a.probe or a.suite or a.recheck):
        ap.error("give a suite, --probe or --recheck")
    ep = registry.load(ROOT / "registry.json")[a.endpoint]
    prices = PriceTable.load(ROOT / ep.price_table)
    guard = SpendGuard(Decimal(a.ceiling), ROOT / "records" / "spend.jsonl")
    runner = make_runner(a, ep, prices, guard)
    try:
        if a.recheck:
            print(json.dumps(runner.recheck(), indent=2))
            return 0
        suite = Probe() if a.probe else load_suite(a.suite)
        summary = runner.run_batch(suite, repeats=a.repeats, thinking=a.thinking == "on",
                                   effort=a.effort, acknowledge=a.acknowledge)
    except MeterMismatch as e:
        print(json.dumps(e.summary, indent=2))
        print(f"MISMATCH: {e}", file=sys.stderr)
        return 2
    except Refused as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 3
    except Exception as e:  # noqa: BLE001 - the client's errors are redacted at source
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        return 4
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
