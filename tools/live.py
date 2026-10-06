"""The lead's live entry point: the only place live mode is switched on.

    python tools/live.py --probe
    python tools/live.py <module>:<SuiteClass> [--repeats N] [--thinking on|off]
                         [--effort low|high|max] [--endpoint NAME] [--ceiling USD]
                         [--allow-peak] [--settle SECONDS]

--probe runs an empty batch: the balance read, the model list, one identity
probe, the balance read again and the reconciliation. It is the cheapest live
step there is, and the first one of the round.

Every batch goes through the runner and the spending guard: a worst case that
does not fit the ceiling's remainder or the balance is refused before anything
is spent, and a batch inside the provider's peak window is refused unless
--allow-peak is given. Parcels never run this file; their tests use the fake.
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

from qs import registry  # noqa: E402
from qs.guard import SpendGuard  # noqa: E402
from qs.prices import PriceTable  # noqa: E402
from qs.suite import Caps, Item, Runner, Suite  # noqa: E402

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


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("suite", nargs="?")
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--endpoint", default="deepseek-flash")
    ap.add_argument("--repeats", type=int, default=1)
    ap.add_argument("--thinking", choices=["on", "off"], default="on")
    ap.add_argument("--effort", choices=["low", "high", "max"])
    ap.add_argument("--ceiling", default=DEFAULT_CEILING)
    ap.add_argument("--allow-peak", action="store_true")
    ap.add_argument("--settle", type=float, default=5.0)
    a = ap.parse_args(argv)
    if not a.probe and not a.suite:
        ap.error("give a suite, or --probe")
    ep = registry.load(ROOT / "registry.json")[a.endpoint]
    prices = PriceTable.load(ROOT / ep.price_table)
    guard = SpendGuard(Decimal(a.ceiling), ROOT / "records" / "spend.jsonl")
    runner = Runner(ep, prices, guard, records_dir=ROOT / "records",
                    transcripts_dir=ROOT / "transcripts", live=True,
                    allow_peak=a.allow_peak, settle_seconds=a.settle)
    suite = Probe() if a.probe else load_suite(a.suite)
    summary = runner.run_batch(suite, repeats=a.repeats, thinking=a.thinking == "on",
                               effort=a.effort)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
