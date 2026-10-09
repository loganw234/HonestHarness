"""The loop's budgets. The token caps are not here: they are the suite's Caps,
which Context.chat enforces and the runner reserves for. These only stop a run
sooner, and each one that stops a run is named in its record."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Budgets:
    max_turns: int = 50                  # model calls in one run
    max_run_seconds: float = 1800.0      # checked before each model call and each tool call
    call_timeout_seconds: float = 120.0  # wall clock for one tool call, inside the container
    max_output_chars: int = 16_000       # of one tool's output, as the model sees it
    malformed_retries: int = 3           # malformed calls in a row answered; the next stops the run
    nudges: int = 1                      # reminders after a turn without a tool call
    max_calls_per_turn: int = 16         # calls past this in one turn are answered "cancelled"
    max_scratch_bytes: int = 1 << 30     # the scratch's size, checked after each turn
    max_tokens_per_turn: int | None = None   # None: Context clamps to what the run has left

    def __post_init__(self):
        for name in ("max_turns", "max_output_chars", "max_calls_per_turn", "max_scratch_bytes"):
            if getattr(self, name) < 1:
                raise ValueError(f"{name} must be at least 1")
        for name in ("malformed_retries", "nudges"):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} must not be negative")
        if self.max_run_seconds <= 0 or self.call_timeout_seconds <= 0:
            raise ValueError("time budgets must be positive")
