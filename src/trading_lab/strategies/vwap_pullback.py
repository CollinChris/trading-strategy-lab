"""VWAP pullback — the Warrior-Trading-style momentum continuation play.

On a green day, wait for price to pull back and tag the session VWAP while
still closing above it, then buy the bounce confirmation (a close back above
the pullback bar's high). Stop just under VWAP, take profit at 2R.
"""

from __future__ import annotations

import pandas as pd

from ..indicators import session_vwap
from .base import EntrySignal, Strategy


class VwapPullback(Strategy):
    name = "vwap_pullback"
    max_trades_per_day = 2

    def __init__(self, touch_tolerance: float = 0.001, warmup_bars: int = 7):
        self.touch_tolerance = touch_tolerance
        self.warmup_bars = warmup_bars

    def new_day(self, day: pd.DataFrame, prior_close: float | None) -> None:
        super().new_day(day, prior_close)
        self.vwap = session_vwap(day)

    def entry_signal(self, i: int) -> EntrySignal | None:
        if i < self.warmup_bars:
            return None
        vwap_prev = float(self.vwap.iloc[i - 1])
        vwap_now = float(self.vwap.iloc[i])
        touched = float(self.day["low"].iloc[i - 1]) <= vwap_prev * (1 + self.touch_tolerance)
        held = float(self.day["close"].iloc[i - 1]) >= vwap_prev * (1 - self.touch_tolerance)
        bounced = float(self.day["close"].iloc[i]) > float(self.day["high"].iloc[i - 1])
        green_day = float(self.day["close"].iloc[i]) > float(self.day["open"].iloc[0])
        if touched and held and bounced and green_day:
            return EntrySignal(
                reason=f"bounce off session VWAP {vwap_now:.2f}",
                stop_price=vwap_now * 0.997,
                target_r=2.0,
            )
        return None
