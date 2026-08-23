"""Bollinger squeeze breakout — volatility contraction then expansion.

A widely traded pattern: when the Bollinger bands pinch to their tightest in a
while (the "squeeze"), energy is building; the first close above the upper
band bets on the expansion. Stop at the middle band, take profit at 2R.
"""

from __future__ import annotations

import pandas as pd

from ..indicators import bollinger, session_vwap
from .base import EntrySignal, Strategy


class SqueezeBreakout(Strategy):
    name = "squeeze_breakout"
    max_trades_per_day = 2

    def __init__(
        self,
        bb_period: int = 20,
        bw_lookback: int = 12,
        target_r: float = 2.0,
    ):
        self.bb_period = bb_period
        self.bw_lookback = bw_lookback  # squeeze = tightest bandwidth of the last N bars
        self.target_r = target_r

    def new_day(self, day: pd.DataFrame, prior_close: float | None) -> None:
        super().new_day(day, prior_close)
        self.mid, self.upper, self.lower, self.bandwidth = bollinger(day["close"], self.bb_period)
        self.vwap = session_vwap(day)

    def entry_signal(self, i: int) -> EntrySignal | None:
        if i < self.bb_period + self.bw_lookback:
            return None
        window = self.bandwidth.iloc[i - self.bw_lookback : i]
        if window.isna().any():
            return None
        was_squeezed = float(self.bandwidth.iloc[i - 1]) <= float(window.min()) * 1.05
        close = float(self.day["close"].iloc[i])
        breakout = close > float(self.upper.iloc[i])
        above_vwap = close > float(self.vwap.iloc[i])
        if was_squeezed and breakout and above_vwap:
            return EntrySignal(
                reason=f"squeeze breakout above upper band {float(self.upper.iloc[i]):.2f}",
                stop_price=float(self.mid.iloc[i]),
                target_r=self.target_r,
            )
        return None
