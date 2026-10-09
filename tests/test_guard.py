from decimal import Decimal

import pytest

from qs.guard import Refused, Reservation, SpendGuard, reconcile


def guard(tmp_path, ceiling="250"):
    return SpendGuard(Decimal(ceiling), tmp_path / "spend.jsonl")


def test_reserve_fits(tmp_path):
    r = guard(tmp_path).reserve("b1", Decimal("1.00"), Decimal("12.00"))
    assert isinstance(r, Reservation) and r.amount == Decimal("1.00") and not r.readonly


def test_reserve_refuses_over_ceiling(tmp_path):
    g = guard(tmp_path, ceiling="1")
    with pytest.raises(Refused):
        g.reserve("b1", Decimal("1.01"), Decimal("100"))


def test_reserve_refuses_over_balance(tmp_path):
    with pytest.raises(Refused):
        guard(tmp_path).reserve("b1", Decimal("12.01"), Decimal("12.00"))


def test_reserve_refuses_unread_balance(tmp_path):
    with pytest.raises(Refused):
        guard(tmp_path).reserve("b1", Decimal("0.01"), None)


def test_spent_is_recomputed_from_the_file(tmp_path):
    g = guard(tmp_path, ceiling="1")
    g.record(batch="b", record_id="r1", model="m", period="off_peak", price_table="t",
             cost=Decimal("0.4"))
    g.record(batch="b", record_id="r2", model="m", period="off_peak", price_table="t",
             cost=Decimal("0.35"))
    assert g.spent() == Decimal("0.75")
    assert g.remaining() == Decimal("0.25")
    with pytest.raises(Refused):
        g.reserve("b2", Decimal("0.26"), Decimal("100"))


def test_check_run_holds_the_reservation(tmp_path):
    g = guard(tmp_path)
    r = g.reserve("b", Decimal("1.00"), Decimal("12"))
    g.check_run(r, Decimal("0.5"), Decimal("0.5"))
    with pytest.raises(Refused):
        g.check_run(r, Decimal("0.5"), Decimal("0.51"))


def test_readonly_reservation(tmp_path):
    r = guard(tmp_path).readonly("b")
    assert r.readonly and r.amount == 0


def test_reconcile_statuses():
    assert reconcile(Decimal("12.00"), Decimal("11.90"), Decimal("0.10")).status == "ok"
    assert reconcile(Decimal("12.00"), Decimal("11.00"), Decimal("0.10")).status == "mismatch"
    assert reconcile(Decimal("12.00"), Decimal("13.00"), Decimal("0.10")).status == "topup"
    assert reconcile(None, Decimal("11.90"), Decimal("0.10")).status == "unread"
    r = reconcile(Decimal("12.00"), Decimal("11.56"), Decimal("0.10"),
                  alternatives={"deepseek-v4-pro": Decimal("0.44")})
    assert r.status == "matches:deepseek-v4-pro"


def test_reconcile_tolerance_scales():
    # 5% of a large batch, or two cents, whichever is more
    assert reconcile(Decimal("100"), Decimal("90.4"), Decimal("10")).status == "ok"        # 0.4 off
    assert reconcile(Decimal("100"), Decimal("89.4"), Decimal("10")).status == "mismatch"  # 0.6 off
