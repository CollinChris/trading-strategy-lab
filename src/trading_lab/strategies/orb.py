"""Opening Range Breakout (ORB).

One of the most-backtested day-trading setups: mark the high/low of the first
15 minutes, buy the first close above that high, stop at the range low, take
profit at 2R, flat by end of day. Entries limited to the first two hours.
"""

from __future__ import annotations

import pandas as pd

from .base import EntrySignal, Strategy


class OpeningRangeBreakout(Strategy):
    name = "orb"
    max_trades_per_day = 1

    def __init__(
        self,
        range_bars: int = 3,
        entry_window_bars: int = 24,
        target_r: float = 2.0,
        stop_at_mid: bool = False,  # True = tighter stop at the range midpoint
    ):
        self.range_bars = range_bars  # 3 x 5m = 15-minute opening range
        self.entry_window_bars = entry_window_bars
        self.target_r = target_r
        self.stop_at_mid = stop_at_mid

    def new_day(self, day: pd.DataFrame, prior_close: float | None) -> None:
        super().new_day(day, prior_close)
        n = min(self.range_bars, len(day))
        self.or_high = float(day["high"].iloc[:n].max())
        self.or_low = float(day["low"].iloc[:n].min())

    def entry_signal(self, i: int) -> EntrySignal | None:
        if i < self.range_bars or i > self.entry_window_bars:
            return None
        close = float(self.day["close"].iloc[i])
        if close > self.or_high:
            stop = (self.or_high + self.or_low) / 2.0 if self.stop_at_mid else self.or_low
            return EntrySignal(
                reason=f"break of opening range high {self.or_high:.2f}",
                stop_price=stop,
                target_r=self.target_r,
            )
        return None
