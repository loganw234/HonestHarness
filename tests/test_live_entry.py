"""tools/live.py's options reach the runner. Nothing here runs a batch, builds
a client or reaches a network: the runner is only constructed, against an
endpoint on a local port that nothing listens on."""
import importlib.util
from decimal import Decimal
from pathlib import Path

import pytest

from qs.guard import SpendGuard
from qs.prices import PriceTable
from qs.registry import Endpoint
from qs.suite import MAX_UNMETERED_PER_BATCH

ROOT = Path(__file__).resolve().parent.parent


def load_live():
    spec = importlib.util.spec_from_file_location("live_entry", ROOT / "tools" / "live.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build(tmp_path, argv):
    live = load_live()
    ep = Endpoint(name="local", provider="deepseek", base_url="http://127.0.0.1:9",
                  model="deepseek-flash", price_table="prices/deepseek-2026-10-06.json", key_env=None)
    guard = SpendGuard(Decimal("1"), tmp_path / "spend.jsonl")
    return live.make_runner(live.parser().parse_args(argv), ep, PriceTable.load(ROOT / ep.price_table),
                            guard)


def test_the_batch_allowance_reaches_the_runner(tmp_path):
    assert build(tmp_path, ["--probe", "--max-unmetered", "15"]).max_unmetered == 15
    # Not given, it is the runner's own default.
    assert build(tmp_path, ["--probe"]).max_unmetered == MAX_UNMETERED_PER_BATCH == 3


@pytest.mark.parametrize("bad", ["0", "-2", "many"])
def test_the_batch_allowance_must_be_one_or_more(bad, capsys):
    with pytest.raises(SystemExit):
        load_live().parser().parse_args(["--probe", "--max-unmetered", bad])
    assert "--max-unmetered" in capsys.readouterr().err
