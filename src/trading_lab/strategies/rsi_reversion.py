"""RSI(2) mean reversion — the popular Connors-style dip-buy, adapted intraday.

Counter-trend contrast to the four momentum strategies: when the 2-period RSI
drops below 10 while price still holds above session VWAP (so the dip is
against an intact uptrend), buy the dip; exit when RSI(2) recovers above 60.
Protective stop 1% below entry, flat by end of day.
"""

from __future__ import annotations

import pandas as pd

from ..indicators import rsi, session_vwap
from .base import EntrySignal, Strategy


class RsiReversion(Strategy):
    name = "rsi2_reversion"
    max_trades_per_day = 3

    def __init__(self, entry_level: float = 10.0, exit_level: float = 60.0, stop_pct: float = 0.01):
        self.entry_level = entry_level
        self.exit_level = exit_level
        self.stop_pct = stop_pct

    def new_day(self, day: pd.DataFrame, prior_close: float | None) -> None:
        super().new_day(day, prior_close)
        self.rsi2 = rsi(day["close"], period=2)
        self.vwap = session_vwap(day)

    def entry_signal(self, i: int) -> EntrySignal | None:
        if i < 5:
            return None
        dip = float(self.rsi2.iloc[i]) < self.entry_level
        uptrend = float(self.day["close"].iloc[i]) > float(self.vwap.iloc[i])
        if dip and uptrend:
            return EntrySignal(
                reason=f"RSI(2)={float(self.rsi2.iloc[i]):.0f} dip above VWAP",
                stop_pct=self.stop_pct,
                target_r=None,
            )
        return None

    def exit_signal(self, i: int) -> bool:
        return float(self.rsi2.iloc[i]) > self.exit_level
