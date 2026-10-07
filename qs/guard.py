"""The spending guard.

Three things hold the ceiling, from the outside in:
1. the provider's prepaid balance, which refuses calls when empty (HTTP 402);
2. this guard, which refuses a run whose worst case would cross what is left,
   of the ceiling or of the balance last read;
3. reconciliation, which checks the guard's own arithmetic against the
   provider's balance after every batch not marked concurrent. The meter is
   checked against something that can say no. A bill above the meter is added
   to the spend file as an adjustment, so the ceiling counts what was billed.
   The runner holds the next batch until a reconciliation that is neither ok
   nor concurrent is acknowledged or rechecked. A batch marked concurrent,
   run beside others from the same balance, gets none of this alone: the
   lead reconciles the marked batches together (qs/suite.py's limits).

Limits, each stated by the behaviour it concedes: a top-up smaller than a
batch's bill hides that much of the bill from its reconciliation, and the
balance's precision is not documented (D18). The tolerance below assumes two
decimals, as D18's example shows; P0's first live batch large enough to move
the balance tests it.

The spend file is append-only JSON lines, one per metered call, written as
each reply arrives, and the total spent is always recomputed from it, never
cached. A call whose reply never arrives cannot be metered; reconciliation is
what sees its bill, beyond its tolerance, and for a batch marked concurrent
only the lead's combined reconciliation can.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from .prices import usd

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

    def spent_in(self, batch: str) -> Decimal:
        """What the spend file holds for one batch: its calls and adjustments."""
        if not self.spend_file.exists():
            return Decimal("0")
        total = Decimal("0")
        for line in self.spend_file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                d = json.loads(line)
                if d["batch"] == batch:
                    total += Decimal(d["cost_usd"])
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
               price_table: str, cost: Decimal, kind: str = "call") -> None:
        """Append one spend line. kind is "call" for a metered reply, or
        "adjustment" for a bill found above the meter at reconciliation."""
        line = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "kind": kind,
            "batch": batch,
            "record": record_id,
            "model": model,
            "period": period,
            "price_table": price_table,
            "cost_usd": usd(cost),
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
