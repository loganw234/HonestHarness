"""The spending guard.

Three things hold the ceiling, from the outside in:
1. the provider's prepaid balance, which refuses calls when empty (HTTP 402);
2. this guard, which refuses a run whose worst case would cross what is left,
   of the ceiling or of the balance last read;
3. reconciliation, which checks the guard's own arithmetic against the
   provider's balance after every batch. The meter is checked against
   something that can say no.

The spend file is append-only JSON lines, one per paid call, and the total
spent is always recomputed from it, never cached.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

DEFAULT_ABS_TOLERANCE = Decimal("0.02")   # two reads of a two-decimal balance, plus rounding
DEFAULT_REL_TOLERANCE = Decimal("0.05")


class Refused(Exception):
    """A run the guard will not start."""


@dataclass(frozen=True)
class Reservation:
    """Issued by the guard for one batch; the client's live mode requires one.
    A read-only reservation (amount 0) permits GET requests only: the balance
    and the model list, which the guard needs before it can reserve spend."""
    batch: str
    amount: Decimal
    readonly: bool = False


@dataclass(frozen=True)
class Reconciliation:
    status: str            # ok | mismatch | topup | unread | matches:<model>
    computed: Decimal
    billed: Decimal | None
    tolerance: Decimal
    detail: str


class SpendGuard:
    def __init__(self, ceiling: Decimal, spend_file: str | Path):
        if ceiling <= 0:
            raise ValueError("a ceiling must be positive")
        self.ceiling = Decimal(ceiling)
        self.spend_file = Path(spend_file)

    def spent(self) -> Decimal:
        if not self.spend_file.exists():
            return Decimal("0")
        total = Decimal("0")
        for line in self.spend_file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                total += Decimal(json.loads(line)["cost_usd"])
        return total

    def remaining(self) -> Decimal:
        return self.ceiling - self.spent()

    def readonly(self, batch: str) -> Reservation:
        return Reservation(batch=batch, amount=Decimal("0"), readonly=True)

    def reserve(self, batch: str, worst_case: Decimal, balance: Decimal | None) -> Reservation:
        """Refuse unless the batch's worst case fits both what is left of the
        ceiling and the balance last read. An unread balance refuses too: the
        guard does not guess the provider's side of the cap."""
        worst_case = Decimal(worst_case)
        left = self.remaining()
        if worst_case > left:
            raise Refused(f"worst case ${worst_case} exceeds what is left of the ceiling, ${left}")
        if balance is None:
            raise Refused("the provider's balance was not read; a batch needs it")
        if worst_case > balance:
            raise Refused(f"worst case ${worst_case} exceeds the provider's balance, ${balance}")
        return Reservation(batch=batch, amount=worst_case)

    def check_run(self, reservation: Reservation, run_worst_case: Decimal, batch_spent: Decimal) -> None:
        """Before each run inside a batch: its worst case must still fit what
        the reservation has left."""
        if batch_spent + Decimal(run_worst_case) > reservation.amount:
            raise Refused(f"run worst case ${run_worst_case} would take the batch past its "
                          f"reservation of ${reservation.amount} (spent ${batch_spent})")

    def record(self, *, batch: str, record_id: str, model: str, period: str,
               price_table: str, cost: Decimal) -> None:
        line = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "batch": batch,
            "record": record_id,
            "model": model,
            "period": period,
            "price_table": price_table,
            "cost_usd": str(cost),
        }
        self.spend_file.parent.mkdir(parents=True, exist_ok=True)
        with self.spend_file.open("a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(line, sort_keys=True) + "\n")


def reconcile(before: Decimal | None, after: Decimal | None, computed: Decimal,
              alternatives: dict[str, Decimal] | None = None,
              abs_tol: Decimal = DEFAULT_ABS_TOLERANCE,
              rel_tol: Decimal = DEFAULT_REL_TOLERANCE) -> Reconciliation:
    """Compare what the guard computed for a batch with what the balance says
    was billed. `alternatives` maps another model's name to the batch's cost
    priced at that model's rates: a bill that matches one of those is a
    routing finding, not a meter fault."""
    computed = Decimal(computed)
    tol = max(abs_tol, computed * rel_tol)
    if before is None or after is None:
        return Reconciliation("unread", computed, None, tol, "a balance read is missing")
    billed = Decimal(before) - Decimal(after)
    if billed < 0:
        return Reconciliation("topup", computed, billed, tol,
                              "the balance rose during the batch; its reconciliation is void")
    if abs(billed - computed) <= tol:
        return Reconciliation("ok", computed, billed, tol, "billed matches computed")
    for name, alt in (alternatives or {}).items():
        if abs(billed - Decimal(alt)) <= tol:
            return Reconciliation(f"matches:{name}", computed, billed, tol,
                                  f"billed matches the batch priced at {name}'s rates")
    return Reconciliation("mismatch", computed, billed, tol,
                          f"billed ${billed} against computed ${computed}")
