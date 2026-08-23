"""Gap & Go — Ross Cameron's signature open-drive momentum play.

Original: stock gaps up big on news, buy the break of the pre-market/opening
high on volume, stop at the low of the opening pullback, sell into strength.
Adapted here for regular-hours bars on liquid large caps: on a day that gaps
up >= min_gap_pct vs the prior session close, buy the first close above the
opening bar's high on above-average volume within the first hour; stop at the
opening bar's low, take profit at 2R.
"""

from __future__ import annotations

import pandas as pd

from .base import EntrySignal, Strategy


class GapAndGo(Strategy):
    name = "gap_and_go"
    max_trades_per_day = 1

    def __init__(self, min_gap_pct: float = 2.0, entry_window_bars: int = 12):
        self.min_gap_pct = min_gap_pct
        self.entry_window_bars = entry_window_bars  # 12 x 5m = first hour

    def new_day(self, day: pd.DataFrame, prior_close: float | None) -> None:
        super().new_day(day, prior_close)
        if prior_close is None:
            self.gap_pct = 0.0
        else:
            self.gap_pct = (float(day["open"].iloc[0]) / prior_close - 1.0) * 100.0
        self.active = self.gap_pct >= self.min_gap_pct
        self.opening_high = float(day["high"].iloc[0])
        self.opening_low = float(day["low"].iloc[0])

    def entry_signal(self, i: int) -> EntrySignal | None:
        if not self.active or i < 1 or i > self.entry_window_bars:
            return None
        close = float(self.day["close"].iloc[i])
        volume = float(self.day["volume"].iloc[i])
        avg_volume = float(self.day["volume"].iloc[:i].mean())
        if close > self.opening_high and volume > 1.2 * avg_volume:
            return EntrySignal(
                reason=f"gap {self.gap_pct:.1f}%, break of opening high {self.opening_high:.2f}",
                stop_price=self.opening_low,
                target_r=2.0,
            )
        return None
