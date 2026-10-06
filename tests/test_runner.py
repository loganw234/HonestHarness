"""The runner end to end, against the fake endpoint: records, spend,
reconciliation, routing, refusals and caps."""
import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from qs import record as rec
from qs.fake import FakeReply, FakeServer, error, reply, stream_reply
from qs.guard import Refused, SpendGuard
from qs.registry import Endpoint
from qs.suite import (Caps, Held, Item, ItemResult, MeterMismatch, Runner, Suite,
                      estimate_tokens)


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
        r, g = runner(tmp_path, url, prices, off_peak_clock)
        s = r.run_batch(Routed(2), repeats=1)
    assert s["reconciliation"] == "matches:deepseek-v4-pro"
    # The spend file is brought up to the bill, and the next batch is held.
    assert Decimal(s["adjustment_usd"]) > 0 and g.spent() == Decimal(s["billed_usd"])
    assert r.hold()["batch"] == s["batch"]


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


def is_probe(body):
    """The identity probe is the one call sent with thinking disabled here."""
    return body["thinking"]["type"] == "disabled"


def test_a_probe_error_is_recorded_and_stops_the_batch(tmp_path, prices, off_peak_clock):
    with FakeServer(lambda body: error(400, "bad request"), prices=prices,
                    clock=off_peak_clock) as url:
        r, _ = runner(tmp_path, url, prices, off_peak_clock)
        s = r.run_batch(Echo(1))
    assert s["runs"] == 0 and "identity probe failed" in s["stopped_for"]
    assert s["reconciliation"] == "ok"
    ident = lines(tmp_path / "records" / "identity.jsonl")[0]
    assert ident["error"].startswith("ProviderError: HTTP 400")
    assert lines(tmp_path / "records" / "batches.jsonl")[-1]["batch"] == s["batch"]


def test_a_runs_400_is_recorded_and_the_batch_goes_on(tmp_path, prices, off_peak_clock):
    respond = lambda body: reply("ready") if is_probe(body) else error(400, "bad")  # noqa: E731
    with FakeServer(respond, prices=prices, clock=off_peak_clock) as url:
        r, _ = runner(tmp_path, url, prices, off_peak_clock)
        s = r.run_batch(Echo(2))
    assert s["runs"] == 2 and s["stopped_for"] is None
    runs = lines(tmp_path / "records" / "runs" / "echo.jsonl")
    assert [x["outcome"]["status"] for x in runs] == ["error", "error"]
    assert "HTTP 400" in runs[0]["outcome"]["detail"]


def test_a_402_stops_the_batch(tmp_path, prices, off_peak_clock):
    respond = lambda body: (reply("ready") if is_probe(body)  # noqa: E731
                            else error(402, "Insufficient Balance"))
    with FakeServer(respond, prices=prices, clock=off_peak_clock) as url:
        r, _ = runner(tmp_path, url, prices, off_peak_clock)
        s = r.run_batch(Echo(3))
    assert s["runs"] == 1 and "HTTP 402" in s["stopped_for"]


class TwoCalls(Suite):
    name = "two"
    version = "test-1"
    caps = Caps(max_prompt_tokens=300_000, max_output_tokens=30_000,
                max_call_prompt_tokens=250_000)

    def items(self):
        return [Item("t")]

    def run_item(self, ctx, item):
        ctx.chat([{"role": "user", "content": "one"}])
        ctx.chat([{"role": "user", "content": "two"}])
        return ItemResult("pass", "")


def test_a_dropped_reply_keeps_metered_spend_and_stops_the_batch(tmp_path, prices,
                                                                 off_peak_clock):
    n = {"run_calls": 0}

    def respond(body):
        if is_probe(body):
            return reply("ready")
        n["run_calls"] += 1
        r = reply("x", usage=(0, 200_000, 20_000))
        return r if n["run_calls"] == 1 else FakeReply(body=r.body, drop=True)

    with FakeServer(respond, prices=prices, clock=off_peak_clock) as url:
        r, g = runner(tmp_path, url, prices, off_peak_clock)
        with pytest.raises(MeterMismatch) as e:
            r.run_batch(TwoCalls())
    s = e.value.summary
    assert "did not arrive whole" in s["stopped_for"]
    run = lines(tmp_path / "records" / "runs" / "two.jsonl")[0]
    assert run["outcome"]["status"] == "error" and run["calls"] == 2
    spend = lines(tmp_path / "records" / "spend.jsonl")
    assert [x["kind"] for x in spend] == ["call", "call", "adjustment"]
    # The bill's rest is added, so the ceiling counts what was billed.
    assert g.spent() == Decimal(s["billed_usd"])
    assert lines(tmp_path / "records" / "batches.jsonl")[-1]["batch"] == s["batch"]


class Swallows(Echo):
    """A suite that catches every error: it cannot hide an unmetered reply."""
    name = "swallows"

    def run_item(self, ctx, item):
        try:
            ctx.chat([{"role": "user", "content": "x"}])
        except Exception:  # noqa: BLE001
            pass
        return ItemResult("pass", "swallowed")


def test_a_swallowed_unmetered_error_still_stops_the_batch(tmp_path, prices, off_peak_clock):
    respond = lambda body: (reply("ready") if is_probe(body)  # noqa: E731
                            else FakeReply(body=reply("x").body, drop=True))
    with FakeServer(respond, prices=prices, clock=off_peak_clock) as url:
        r, _ = runner(tmp_path, url, prices, off_peak_clock)
        s = r.run_batch(Swallows(3))
    assert s["runs"] == 1 and "did not arrive whole" in s["stopped_for"]
    # The suite's "pass" after an unmetered reply is not the model's.
    run = lines(tmp_path / "records" / "runs" / "swallows.jsonl")[0]
    assert run["outcome"]["status"] == "error" and run["stop_reason"] == s["stopped_for"]
    assert "the suite returned pass" in run["outcome"]["detail"]


def test_a_reply_without_usage_stops_the_batch(tmp_path, prices, off_peak_clock):
    def respond(body):
        r = reply("ready" if is_probe(body) else "x")
        if not is_probe(body):
            del r.body["usage"]
        return r
    with FakeServer(respond, prices=prices, clock=off_peak_clock) as url:
        r, _ = runner(tmp_path, url, prices, off_peak_clock)
        s = r.run_batch(Echo(3))
    assert s["runs"] == 1 and "IncompleteReply" in s["stopped_for"]


class Streams(Echo):
    name = "streams"

    def run_item(self, ctx, item):
        ctx.chat([{"role": "user", "content": "x"}], stream=True)
        return ItemResult("pass", "")


def test_a_stream_cut_short_stops_the_batch(tmp_path, prices, off_peak_clock):
    def respond(body):
        if is_probe(body):
            return reply("ready")
        fr = stream_reply("hello")
        fr.cut_after = 2           # the keep-alive and the content: no usage, no [DONE]
        return fr
    with FakeServer(respond, prices=prices, clock=off_peak_clock) as url:
        r, _ = runner(tmp_path, url, prices, off_peak_clock)
        s = r.run_batch(Streams(2))
    assert s["runs"] == 1 and "IncompleteReply" in s["stopped_for"]
    run = lines(tmp_path / "records" / "runs" / "streams.jsonl")[0]
    assert run["outcome"]["status"] == "error"


class Severs(Echo):
    """Stops the fake after its run, so the closing balance read fails."""
    name = "severs"

    def __init__(self, fake):
        super().__init__(1)
        self.fake = fake

    def run_item(self, ctx, item):
        result = super().run_item(ctx, item)
        self.fake.stop()
        return result


def test_a_failed_closing_read_is_unread_and_holds_the_next_batch(tmp_path, prices,
                                                                  off_peak_clock):
    fake = FakeServer(prices=prices, clock=off_peak_clock)
    url = fake.start()
    try:
        r, _ = runner(tmp_path, url, prices, off_peak_clock)
        s = r.run_batch(Severs(fake))
    finally:
        fake.stop()
    assert s["reconciliation"] == "unread" and "closing balance read failed" in s["detail"]
    assert r.hold()["batch"] == s["batch"]
    with pytest.raises(Held):
        r.run_batch(Echo(1))


def test_a_tiny_cost_is_written_in_fixed_point(tmp_path, prices, off_peak_clock):
    with FakeServer(lambda body: reply("x", usage=(0, 4, 0)), prices=prices,
                    clock=off_peak_clock) as url:
        r, _ = runner(tmp_path, url, prices, off_peak_clock)
        r.run_batch(Echo(1))
    run = lines(tmp_path / "records" / "runs" / "echo.jsonl")[0]
    assert "E" not in run["cost_usd"] and Decimal(run["cost_usd"]) == Decimal("0.0000006")


class Clock:
    """A clock the fake moves on: each reply takes as long as the test says."""

    def __init__(self, t):
        self.t = t

    def __call__(self):
        return self.t

    def advance(self, minutes):
        self.t += timedelta(minutes=minutes)


class Calls(Suite):
    name = "calls"
    version = "test-1"
    caps = Caps(max_prompt_tokens=10_000, max_output_tokens=2_000, max_call_prompt_tokens=5_000)

    def __init__(self, items=1, calls=3):
        self.n_items, self.n_calls = items, calls

    def items(self):
        return [Item(f"i{k}") for k in range(self.n_items)]

    def run_item(self, ctx, item):
        for k in range(self.n_calls):
            ctx.chat([{"role": "user", "content": f"call {k}"}])
        return ItemResult("pass", "")


def test_no_call_is_sent_into_the_peak_margin(tmp_path, prices):
    clock = Clock(datetime(2026, 10, 5, 0, 40, tzinfo=timezone.utc))   # Monday, off-peak

    def respond(body):
        clock.advance(6)              # each reply takes six minutes
        return reply("ready") if is_probe(body) else reply("x", usage=(0, 1000, 100))
    with FakeServer(respond, prices=prices, clock=clock) as url:
        r, _ = runner(tmp_path, url, prices, clock)
        s = r.run_batch(Calls(items=2, calls=3))
    runs = lines(tmp_path / "records" / "runs" / "calls.jsonl")
    assert len(runs) == 1 and runs[0]["outcome"]["status"] == "stopped"
    assert "peak" in s["stopped_for"] and s["reconciliation"] == "ok"
    assert runs[0]["stop_reason"] == s["stopped_for"]
    assert {x["period"] for x in lines(tmp_path / "records" / "spend.jsonl")} == {"off_peak"}


def test_with_peak_allowed_the_reservation_is_priced_at_peak(tmp_path, prices):
    clock = Clock(datetime(2026, 10, 5, 0, 44, tzinfo=timezone.utc))

    def respond(body):
        clock.advance(6)
        return reply("ready") if is_probe(body) else reply("x", usage=(0, 1000, 100))
    with FakeServer(respond, prices=prices, clock=clock) as url:
        r, _ = runner(tmp_path, url, prices, clock, allow_peak=True)
        s = r.run_batch(Calls(items=1, calls=3))
    assert s["reserved_at"] == ["off_peak", "peak"] and s["reconciliation"] == "ok"
    run = lines(tmp_path / "records" / "runs" / "calls.jsonl")[0]
    assert run["rate_period"] == "mixed" and run["outcome"]["status"] == "pass"
    # (10,000 + 5,000) prompt at $0.30 and 2,000 output at $1.20 per million,
    # plus the probe's 64 and 16 at the same rates: 0.0069 + 0.0000384.
    assert Decimal(s["reserved_usd"]) == Decimal("0.0069384")
    assert Decimal(s["computed_usd"]) <= Decimal(s["reserved_usd"])


def test_the_reservation_is_the_hand_computed_worst_case(tmp_path, prices, off_peak_clock):
    with FakeServer(prices=prices, clock=off_peak_clock) as url:
        r, _ = runner(tmp_path, url, prices, off_peak_clock)
        s = r.run_batch(Echo(1))
    # (10,000 + 5,000) prompt at $0.15 and 2,000 output at $0.60 per million,
    # plus the probe's 64 and 16 at the same rates: 0.00345 + 0.0000192. Plus
    # one call's peak premium: 5,000 and 2,000 at $0.30 and $1.20 (0.0039)
    # less the same at off-peak rates (0.00195): 0.00195.
    assert Decimal(s["reserved_usd"]) == Decimal("0.0054192")
    assert Decimal(s["crossing_margin_usd"]) == Decimal("0.00195")
    assert s["reserved_at"] == ["off_peak"]


class Huge(Echo):
    name = "huge"
    caps = Caps(max_prompt_tokens=40_000_000, max_output_tokens=500_000,
                max_call_prompt_tokens=1_000_000)

    def __init__(self):
        super().__init__(1)


def test_max_tokens_never_passes_the_providers_limit(tmp_path, prices, off_peak_clock):
    fake = FakeServer(prices=prices, clock=off_peak_clock)
    with fake as url:
        r, _ = runner(tmp_path, url, prices, off_peak_clock)
        r.run_batch(Huge())
    assert [b["max_tokens"] for b in fake.requests if not is_probe(b)] == [393216]


class Overrides(Echo):
    name = "overrides"

    def run_item(self, ctx, item):
        ctx.chat([{"role": "user", "content": "x"}], thinking=False)
        return ItemResult("pass", "")


def test_a_per_call_thinking_setting_is_refused(tmp_path, prices, off_peak_clock):
    with FakeServer(prices=prices, clock=off_peak_clock) as url:
        r, _ = runner(tmp_path, url, prices, off_peak_clock)
        r.run_batch(Overrides(1), thinking=True, effort="max")
    run = lines(tmp_path / "records" / "runs" / "overrides.jsonl")[0]
    assert run["outcome"]["status"] == "error" and "batch's setting" in run["outcome"]["detail"]
    assert run["calls"] == 0 and run["thinking"] is True and run["effort"] == "max"


class Oversized(Echo):
    name = "oversized"
    caps = Caps(max_prompt_tokens=10_000, max_output_tokens=2_000, max_call_prompt_tokens=100)

    def run_item(self, ctx, item):
        ctx.chat([{"role": "user", "content": "x" * 1000}])
        return ItemResult("pass", "")


def test_a_request_over_the_call_cap_is_never_sent(tmp_path, prices, off_peak_clock):
    fake = FakeServer(prices=prices, clock=off_peak_clock)
    with fake as url:
        r, _ = runner(tmp_path, url, prices, off_peak_clock)
        r.run_batch(Oversized(1))
    run = lines(tmp_path / "records" / "runs" / "oversized.jsonl")[0]
    assert run["outcome"]["status"] == "stopped" and run["calls"] == 0
    assert [b for b in fake.requests if not is_probe(b)] == []


def test_the_token_estimate_is_two_characters_a_token():
    assert estimate_tokens("x" * 100) == 51


def test_a_mismatch_holds_the_next_batch_until_acknowledged(tmp_path, prices, off_peak_clock):
    fake = FakeServer(lambda body: reply("x", usage=(0, 1_000_000, 0)), prices=None,
                      clock=off_peak_clock)
    with fake as url:
        r, _ = runner(tmp_path, url, prices, off_peak_clock)
        with pytest.raises(MeterMismatch):
            r.run_batch(Big(), batch="b1")
        with pytest.raises(Held):
            r.run_batch(Echo(1), batch="b2")
        with pytest.raises(Held):
            r.run_batch(Echo(1), batch="b2", acknowledge="b0")
        fake.responder = lambda body: reply("x")       # small calls from here on
        s = r.run_batch(Echo(1), batch="b2", acknowledge="b1")
    assert s["acknowledged"] == "b1" and s["reconciliation"] == "ok"
    acks = [x for x in lines(tmp_path / "records" / "batches.jsonl") if x["kind"] == "acknowledge"]
    assert [a["batch"] for a in acks] == ["b1"]


def test_a_recheck_reconciles_a_slow_balance(tmp_path, prices, off_peak_clock):
    fake = FakeServer(lambda body: reply("x", usage=(0, 1_000_000, 0)), prices=None,
                      clock=off_peak_clock)
    with fake as url:
        r, _ = runner(tmp_path, url, prices, off_peak_clock)
        with pytest.raises(MeterMismatch) as e:
            r.run_batch(Big(), batch="b1")
        fake.balance -= Decimal(e.value.summary["computed_usd"])   # the bill lands late
        line = r.recheck()
        assert line["reconciliation"] == "ok" and r.hold() is None
        fake.responder = lambda body: reply("x")
        r.run_batch(Echo(1), batch="b2")


def test_an_id_with_a_colon_is_refused(tmp_path, prices, off_peak_clock):
    with FakeServer(prices=prices, clock=off_peak_clock) as url:
        r, _ = runner(tmp_path, url, prices, off_peak_clock)
        with pytest.raises(ValueError):
            r.run_batch(Echo(1), batch="b1:cut16k")
    assert not (tmp_path / "records").exists()


def test_an_acknowledgment_refused_at_the_start_lifts_nothing(tmp_path, prices, off_peak_clock):
    fake = FakeServer(lambda body: reply("x", usage=(0, 1_000_000, 0)), prices=None,
                      clock=off_peak_clock)
    with fake as url:
        r, _ = runner(tmp_path, url, prices, off_peak_clock)
        with pytest.raises(MeterMismatch):
            r.run_batch(Big(), batch="b1")
        tight, _ = runner(tmp_path, url, prices, off_peak_clock, ceiling="0.000001")
        with pytest.raises(Refused):
            tight.run_batch(Echo(1), batch="b2", acknowledge="b1")
    assert r.hold()["batch"] == "b1"
    assert [x for x in lines(tmp_path / "records" / "batches.jsonl")
            if x["kind"] == "acknowledge"] == []


class Retries(Echo):
    """Retries a failed call up to five times, catching everything."""
    name = "retries"

    def run_item(self, ctx, item):
        for _ in range(6):
            try:
                ctx.chat([{"role": "user", "content": "x"}])
                return ItemResult("pass", "")
            except Exception:  # noqa: BLE001
                continue
        return ItemResult("fail", "gave up")


@pytest.mark.parametrize("failure", ["drop", "503"])
def test_a_retrying_suite_cannot_send_past_a_stop(tmp_path, prices, off_peak_clock, failure):
    def respond(body):
        if is_probe(body):
            return reply("ready")
        if failure == "drop":
            return FakeReply(body=reply("x").body, drop=True)
        return error(503, "Server Overloaded")
    fake = FakeServer(respond, prices=prices, clock=off_peak_clock)
    with fake as url:
        r, _ = runner(tmp_path, url, prices, off_peak_clock)
        s = r.run_batch(Retries(3))
    assert len([b for b in fake.requests if not is_probe(b)]) == 1
    assert s["runs"] == 1 and s["stopped_for"]
    run = lines(tmp_path / "records" / "runs" / "retries.jsonl")[0]
    assert run["outcome"]["status"] == "error" and run["stop_reason"] == s["stopped_for"]


def test_one_call_crossing_into_peak_stays_inside_the_reservation(tmp_path, prices):
    clock = Clock(datetime(2026, 10, 5, 0, 40, tzinfo=timezone.utc))   # Monday, off-peak

    def respond(body):
        if is_probe(body):
            clock.advance(9)          # the probe answers at 00:49
            return reply("ready")
        clock.advance(15)             # the run's call, sent at 00:49, answers at 01:04
        return reply("x", usage=(0, 5_000, 2_000))
    with FakeServer(respond, prices=prices, clock=clock) as url:
        r, _ = runner(tmp_path, url, prices, clock)
        s = r.run_batch(Calls(items=1, calls=1))
    run = lines(tmp_path / "records" / "runs" / "calls.jsonl")[0]
    assert run["rate_period"] == "peak" and s["reconciliation"] == "ok"
    # Billed at peak: 5,000 at $0.30 and 2,000 at $1.20 per million, 0.0039,
    # with the probe's 0.0000045. Without the crossing margin the reservation
    # would be 0.0034692, below it.
    assert Decimal(s["computed_usd"]) == Decimal("0.0039045")
    assert Decimal(s["computed_usd"]) <= Decimal(s["reserved_usd"])


class Fingerprints(Echo):
    name = "fingerprints"

    def run_item(self, ctx, item):
        for _ in range(3):
            ctx.chat([{"role": "user", "content": "x"}])
        return ItemResult("pass", "")


def test_the_record_lists_every_model_and_fingerprint_reported(tmp_path, prices,
                                                              off_peak_clock):
    seen = iter([("deepseek-flash", "fp_1"), ("deepseek-v4-pro", "fp_2"),
                 ("deepseek-flash", "fp_3")])

    def respond(body):
        if is_probe(body):
            return reply("ready")
        model, fp = next(seen)
        return reply("x", model=model, fingerprint=fp)
    with FakeServer(respond, prices=prices, clock=off_peak_clock) as url:
        r, _ = runner(tmp_path, url, prices, off_peak_clock)
        r.run_batch(Fingerprints(1))
    run = lines(tmp_path / "records" / "runs" / "fingerprints.jsonl")[0]
    assert run["model_reported"] == ["deepseek-flash", "deepseek-v4-pro"]
    assert run["system_fingerprint"] == ["fp_1", "fp_2", "fp_3"]


def test_an_id_ending_in_a_newline_is_refused(tmp_path, prices, off_peak_clock):
    with FakeServer(prices=prices, clock=off_peak_clock) as url:
        r, _ = runner(tmp_path, url, prices, off_peak_clock)
        with pytest.raises(ValueError):
            r.run_batch(Echo(1), batch="b1" + chr(10))


class CatchesPeak(Calls):
    """Catches the peak stop and calls its run a failure: a harness limit is
    still recorded as stopped."""
    name = "catchespeak"

    def run_item(self, ctx, item):
        try:
            return super().run_item(ctx, item)
        except Exception:  # noqa: BLE001
            return ItemResult("fail", "caught the stop")


def test_a_caught_peak_stop_is_recorded_as_stopped(tmp_path, prices):
    clock = Clock(datetime(2026, 10, 5, 0, 40, tzinfo=timezone.utc))

    def respond(body):
        clock.advance(6)
        return reply("ready") if is_probe(body) else reply("x", usage=(0, 1000, 100))
    with FakeServer(respond, prices=prices, clock=clock) as url:
        r, _ = runner(tmp_path, url, prices, clock)
        s = r.run_batch(CatchesPeak(items=1, calls=3))
    run = lines(tmp_path / "records" / "runs" / "catchespeak.jsonl")[0]
    assert run["outcome"]["status"] == "stopped" and "peak" in run["stop_reason"]
    assert "the suite returned fail" in run["outcome"]["detail"]
