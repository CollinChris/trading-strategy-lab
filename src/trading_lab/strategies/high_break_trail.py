"""First-hour high breakout with an ATR trailing stop.

Momentum entry, but the exit is the experiment: no fixed target — the stop
trails the highest price seen by `trail_atr_mult` ATRs, so winners run until
the trend actually bends. This is the "smarter exits" candidate from the
roadmap, made comparable against the fixed-2R strategies.
"""

from __future__ import annotations

import pandas as pd

from ..indicators import atr, session_vwap
from .base import EntrySignal, Strategy


class HighBreakTrail(Strategy):
    name = "high_break_trail"
    max_trades_per_day = 1

    def __init__(self, window_bars: int = 12, trail_atr_mult: float = 2.0):
        self.window_bars = window_bars  # 12 x 5m = first hour sets the level
        self.trail_atr_mult = trail_atr_mult

    def new_day(self, day: pd.DataFrame, prior_close: float | None) -> None:
        super().new_day(day, prior_close)
        self.atr = atr(day)
        self.vwap = session_vwap(day)
        n = min(self.window_bars, len(day))
        self.opening_high = float(day["high"].iloc[:n].max())

    def entry_signal(self, i: int) -> EntrySignal | None:
        if i < self.window_bars:
            return None
        close = float(self.day["close"].iloc[i])
        above_vwap = close > float(self.vwap.iloc[i])
        if close > self.opening_high and above_vwap:
            dist = self.trail_atr_mult * float(self.atr.iloc[i])
            if dist <= 0:
                return None
            return EntrySignal(
                reason=f"break of first-hour high {self.opening_high:.2f}, {self.trail_atr_mult}xATR trail",
                stop_price=close - dist,
                trail_dist=dist,
                target_r=None,
            )
        return None
