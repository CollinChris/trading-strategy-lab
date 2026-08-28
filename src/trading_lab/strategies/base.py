"""Strategy interface.

Contract (enforced by the engine, relied on for zero lookahead):
- new_day() is called once per session with the full day's bars; strategies may
  precompute CAUSAL indicator series (ema/rsi/vwap) but must only read values
  at index <= i inside entry_signal/exit_signal.
- A strategy instance sees one symbol's sessions in chronological order, so it
  may accumulate cross-session state in new_day() (e.g. a return history for
  time-series models) — but only from sessions already handed to it.
- entry_signal(i) is evaluated on the COMPLETED bar i; a resulting entry fills
  at bar i+1's open.
- exit_signal(i, ...) likewise fills at bar i+1's open. Stops and targets are
  monitored intra-bar by the engine itself.

All strategies are long-only in this MVP (see README).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class EntrySignal:
    reason: str
    stop_price: float | None = None  # absolute stop, or...
    stop_pct: float | None = None  # ...fractional stop below entry (e.g. 0.01)
    target_r: float | None = None  # take-profit at N x risk; None = no fixed target
    trail_dist: float | None = None  # trailing stop: ratchet stop to (high - trail_dist)


class Strategy(ABC):
    name: str = "base"
    max_trades_per_day: int = 1
    symbol: str = ""  # set by the engine before new_day() — for context-aware strategies

    def new_day(self, day: pd.DataFrame, prior_close: float | None) -> None:
        """Reset state and precompute causal indicators for one session."""
        self.day = day
        self.prior_close = prior_close

    @abstractmethod
    def entry_signal(self, i: int) -> EntrySignal | None:
        """Return a signal on completed bar i to buy at bar i+1's open."""

    def exit_signal(self, i: int) -> bool:
        """Dynamic exit on completed bar i (fills at bar i+1's open)."""
        return False
