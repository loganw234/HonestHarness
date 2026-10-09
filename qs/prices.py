"""Pinned price tables, and the provider's rate periods.

A table is a JSON file under prices/, read once and never edited: a new price
is a new file with its own id, source URL and read date, so every recorded
cost names the table it was computed from. Money is Decimal throughout.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone
from decimal import Decimal
from pathlib import Path

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def usd(amount) -> str:
    """A dollar amount as fixed-point text, never in exponent form: Decimal
    renders 0.0000006 as "6E-7", which the run record's pattern refuses."""
    return format(Decimal(amount), "f")


@dataclass(frozen=True)
class Rates:
    cache_hit: Decimal
    cache_miss: Decimal
    output: Decimal


@dataclass(frozen=True)
class Usage:
    """Token counts as the provider reports them for one call."""
    cache_hit: int
    cache_miss: int
    output: int
    reasoning: int = 0  # part of output; recorded, not priced separately

    @property
    def prompt(self) -> int:
        return self.cache_hit + self.cache_miss


class PriceTable:
    def __init__(self, data: dict, path: str = ""):
        self.path = path
        self.id = data["id"]
        self.provider = data["provider"]
        self.currency = data["currency"]
        self.unit = Decimal(data["unit_tokens"])
        self.source_url = data["source_url"]
        self.read_date = data["read_date"]
        self.models: dict[str, dict[str, Rates]] = {}
        for model, periods in data["models"].items():
            self.models[model] = {
                period: Rates(**{k: Decimal(v) for k, v in rates.items()})
                for period, rates in periods.items()
            }
        sched = data["schedule"]
        self.peak_windows = [(_hm(a), _hm(b)) for a, b in sched["peak_windows_utc"]]
        self.peak_days = set(sched["peak_weekdays_utc"])

    @classmethod
    def load(cls, path: str | Path) -> "PriceTable":
        p = Path(path)
        return cls(json.loads(p.read_text(encoding="utf-8")), str(p))

    def period(self, when: datetime) -> str:
        """'peak' or 'off_peak' at a moment, by the table's UTC schedule.
        A window [a, b) includes its start and excludes its end."""
        if when.tzinfo is None:
            raise ValueError("a naive datetime has no time zone; give UTC")
        utc = when.astimezone(timezone.utc)
        if WEEKDAYS[utc.weekday()] not in self.peak_days:
            return "off_peak"
        t = utc.time()
        for start, end in self.peak_windows:
            if start <= t < end:
                return "peak"
        return "off_peak"

    def peak_within(self, when: datetime, margin: timedelta) -> bool:
        """True if `when` is in a peak window, or one begins before
        `when + margin`. Windows start on whole minutes, so testing each
        whole minute in the span is exact."""
        if self.period(when) == "peak":
            return True
        end = when + margin
        t = when.replace(second=0, microsecond=0) + timedelta(minutes=1)
        while t <= end:
            if self.period(t) == "peak":
                return True
            t += timedelta(minutes=1)
        return self.period(end) == "peak"

    def rates(self, model: str, period: str) -> Rates:
        if model not in self.models:
            raise KeyError(f"price table {self.id} has no prices for {model}")
        return self.models[model][period]

    def cost(self, model: str, period: str, usage: Usage) -> Decimal:
        r = self.rates(model, period)
        return (Decimal(usage.cache_hit) * r.cache_hit
                + Decimal(usage.cache_miss) * r.cache_miss
                + Decimal(usage.output) * r.output) / self.unit

    def worst_case(self, model: str, period: str, max_prompt: int, max_output: int) -> Decimal:
        """The most a call or run could cost: every prompt token a cache miss."""
        return self.cost(model, period, Usage(cache_hit=0, cache_miss=max_prompt, output=max_output))


def _hm(s: str) -> time:
    h, m = s.split(":")
    return time(int(h), int(m))
