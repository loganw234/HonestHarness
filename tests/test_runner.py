"""The runner end to end, against the fake endpoint: records, spend,
reconciliation, routing, refusals and caps."""
import json
from decimal import Decimal

import pytest

from qs import record as rec
from qs.fake import FakeServer, error, reply
from qs.guard import Refused, SpendGuard
from qs.registry import Endpoint
from qs.suite import Caps, Item, ItemResult, MeterMismatch, Runner, Suite


class Echo(Suite):
    name = "echo"
    version = "test-1"
    caps = Caps(max_prompt_tokens=10_000, max_output_tokens=2_000, max_call_prompt_tokens=5_000)

    def __init__(self, n=2):
        self.n = n

    def items(self):
        return [Item(f"i{k}") for k in range(self.n)]

    def run_item(self, ctx, item):
        t = ctx.chat([{"role": "user", "content": f"say {item.id}"}])
        return ItemResult("pass" if t.content else "fail", "", {"content": t.content})


class Greedy(Suite):
    """Calls until its cap stops it."""
    name = "greedy"
    version = "test-1"
    caps = Caps(max_prompt_tokens=50, max_output_tokens=10_000, max_call_prompt_tokens=1_000)

    def items(self):
        return [Item("g")]

    def run_item(self, ctx, item):
        while True:
            ctx.chat([{"role": "user", "content": "again"}])


def endpoint(url):
    return Endpoint(name="fake", provider="deepseek", base_url=url, model="deepseek-flash",
                    price_table="prices/deepseek-2026-10-06.json", key_env=None)


def runner(tmp_path, url, prices, clock, **kw):
    g = SpendGuard(Decimal(kw.pop("ceiling", "250")), tmp_path / "records" / "spend.jsonl")
    return Runner(endpoint(url), prices, g, records_dir=tmp_path / "records",
                  transcripts_dir=tmp_path / "transcripts", clock=clock, **kw), g


def lines(p):
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def test_batch_records_and_reconciles(tmp_path, prices, off_peak_clock):
    with FakeServer(lambda body: reply("hello", usage=(100, 1000, 200, 50)), prices=prices,
                    clock=off_peak_clock) as url:
        r, g = runner(tmp_path, url, prices, off_peak_clock)
        s = r.run_batch(Echo(2), repeats=2)
    assert s["runs"] == 4 and s["reconciliation"] == "ok" and s["stopped_for"] is None
    runs = lines(tmp_path / "records" / "runs" / "echo.jsonl")
    assert len(runs) == 4
    for line in runs:
        rec.validate(line)
        assert line["usage"] == {"cache_hit": 100, "cache_miss": 1000, "output": 200,
                                 "reasoning": 50}
        assert line["rate_period"] == "off_peak" and line["outcome"]["status"] == "pass"
    spend = lines(tmp_path / "records" / "spend.jsonl")
    assert len(spend) == 5                              # the probe and four runs
    assert g.spent() == Decimal(s["computed_usd"])
    ident = lines(tmp_path / "records" / "identity.jsonl")
    assert ident[0]["display_names"] == {"deepseek-flash": "DeepSeek-V4.1-Flash"}
    assert (tmp_path / "transcripts" / s["batch"]).is_dir()


class Routed(Echo):
    """Large enough calls that pro's and flash's bills differ by more than the
    two-cent tolerance."""
    name = "routed"
    caps = Caps(max_prompt_tokens=300_000, max_output_tokens=30_000,
                max_call_prompt_tokens=250_000)


def test_routing_is_found_by_billing(tmp_path, prices, off_peak_clock):
    # The fake bills at pro's rates: the bill matches pro's table, not the meter.
    with FakeServer(lambda body: reply("x", usage=(0, 200_000, 20_000)), prices=prices,
                    billing_model="deepseek-v4-pro", clock=off_peak_clock) as url:
        r, _ = runner(tmp_path, url, prices, off_peak_clock)
        s = r.run_batch(Routed(2), repeats=1)
    assert s["reconciliation"] == "matches:deepseek-v4-pro"


def test_overspent_reservation_stops_the_batch_and_still_reconciles(tmp_path, prices,
                                                                     off_peak_clock):
    # Usage far above the suite's declared caps: the guard stops the next run,
    # and the batch still reads the balance and reconciles.
    with FakeServer(lambda body: reply("x", usage=(0, 200_000, 20_000)), prices=prices,
                    clock=off_peak_clock) as url:
        r, _ = runner(tmp_path, url, prices, off_peak_clock)
        s = r.run_batch(Echo(3), repeats=1)
    assert s["stopped_for"] and "guard refused" in s["stopped_for"]
    assert s["reconciliation"] == "ok"


def test_mismatch_stops(tmp_path, prices, off_peak_clock):
    # The fake bills nothing while the meter computes about 30 cents.
    with FakeServer(lambda body: reply("x", usage=(0, 1_000_000, 0)), prices=None,
                    clock=off_peak_clock) as url:
        r, _ = runner(tmp_path, url, prices, off_peak_clock)
        with pytest.raises(MeterMismatch):
            r.run_batch(Big(), repeats=1)


class Big(Echo):
    name = "big"
    caps = Caps(max_prompt_tokens=2_000_000, max_output_tokens=2_000,
                max_call_prompt_tokens=1_100_000)

    def __init__(self):
        super().__init__(2)


def test_peak_is_refused(tmp_path, prices, peak_clock):
    with FakeServer(prices=prices, clock=peak_clock) as url:
        r, _ = runner(tmp_path, url, prices, peak_clock)
        with pytest.raises(Refused):
            r.run_batch(Echo(1))


def test_low_balance_is_refused(tmp_path, prices, off_peak_clock):
    with FakeServer(balance="0.00", prices=prices, clock=off_peak_clock) as url:
        r, _ = runner(tmp_path, url, prices, off_peak_clock)
        with pytest.raises(Refused):
            r.run_batch(Echo(1))


def test_ceiling_is_refused(tmp_path, prices, off_peak_clock):
    with FakeServer(prices=prices, clock=off_peak_clock) as url:
        r, _ = runner(tmp_path, url, prices, off_peak_clock, ceiling="0.000001")
        with pytest.raises(Refused):
            r.run_batch(Echo(1))


def test_cap_stops_a_run(tmp_path, prices, off_peak_clock):
    with FakeServer(lambda body: reply("x", usage=(0, 30, 1)), prices=prices,
                    clock=off_peak_clock) as url:
        r, _ = runner(tmp_path, url, prices, off_peak_clock)
        s = r.run_batch(Greedy(), repeats=1)
    run = lines(tmp_path / "records" / "runs" / "greedy.jsonl")[0]
    assert run["outcome"]["status"] == "stopped" and run["calls"] == 2
    assert s["reconciliation"] == "ok"


def test_provider_error_is_recorded(tmp_path, prices, off_peak_clock):
    with FakeServer(lambda body: error(400, "bad request"), prices=prices,
                    clock=off_peak_clock) as url:
        r, _ = runner(tmp_path, url, prices, off_peak_clock)
        # The identity probe also gets the 400, so the batch fails at its start.
        with pytest.raises(Exception):
            r.run_batch(Echo(1))
