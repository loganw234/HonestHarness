from datetime import datetime, timezone
from decimal import Decimal

import pytest

from qs.prices import Usage


def utc(y, mo, d, h, mi=0, s=0):
    return datetime(y, mo, d, h, mi, s, tzinfo=timezone.utc)


@pytest.mark.parametrize("when,expected", [
    (utc(2026, 10, 5, 0, 59, 59), "off_peak"),   # Monday, before the first window
    (utc(2026, 10, 5, 1, 0, 0), "peak"),         # a window includes its start
    (utc(2026, 10, 5, 3, 59, 59), "peak"),
    (utc(2026, 10, 5, 4, 0, 0), "off_peak"),     # and excludes its end
    (utc(2026, 10, 5, 6, 0, 0), "peak"),
    (utc(2026, 10, 5, 9, 59, 59), "peak"),
    (utc(2026, 10, 5, 10, 0, 0), "off_peak"),
    (utc(2026, 10, 9, 2, 0, 0), "peak"),         # Friday
    (utc(2026, 10, 10, 2, 0, 0), "off_peak"),    # Saturday
    (utc(2026, 10, 11, 7, 0, 0), "off_peak"),    # Sunday
])
def test_period(prices, when, expected):
    assert prices.period(when) == expected


def test_naive_datetime_refused(prices):
    with pytest.raises(ValueError):
        prices.period(datetime(2026, 10, 5, 2, 0))


def test_cost_per_million(prices):
    m = "deepseek-flash"
    assert prices.cost(m, "off_peak", Usage(0, 1_000_000, 0)) == Decimal("0.15")
    assert prices.cost(m, "off_peak", Usage(1_000_000, 0, 0)) == Decimal("0.003")
    assert prices.cost(m, "off_peak", Usage(0, 0, 1_000_000)) == Decimal("0.6")
    assert prices.cost(m, "peak", Usage(0, 1_000_000, 0)) == Decimal("0.3")
    # off-peak is half of peak, by the source
    u = Usage(123_456, 7_890, 4_321)
    assert prices.cost(m, "peak", u) == 2 * prices.cost(m, "off_peak", u)


def test_reasoning_is_not_priced_twice(prices):
    a = prices.cost("deepseek-flash", "off_peak", Usage(0, 0, 1000, reasoning=0))
    b = prices.cost("deepseek-flash", "off_peak", Usage(0, 0, 1000, reasoning=900))
    assert a == b


def test_worst_case_is_all_miss(prices):
    w = prices.worst_case("deepseek-flash", "off_peak", 40_000_000, 500_000)
    assert w == Decimal("6.3")


def test_unknown_model(prices):
    with pytest.raises(KeyError):
        prices.cost("no-such-model", "peak", Usage(1, 1, 1))
