import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from qs.prices import PriceTable  # noqa: E402

PRICES = ROOT / "prices" / "deepseek-2026-10-06.json"

# Tuesday 2026-10-06 17:25 UTC: off-peak. Tuesday 02:00 UTC: peak.
OFF_PEAK = datetime(2026, 10, 6, 17, 25, tzinfo=timezone.utc)
PEAK = datetime(2026, 10, 6, 2, 0, tzinfo=timezone.utc)


@pytest.fixture
def prices():
    return PriceTable.load(PRICES)


@pytest.fixture
def off_peak_clock():
    return lambda: OFF_PEAK


@pytest.fixture
def peak_clock():
    return lambda: PEAK
