"""EMA 9/20 crossover — the classic intraday trend-following entry.

Buy when the 9-EMA crosses above the 20-EMA while price is above session VWAP
(trend filter). No fixed target: ride the trend and exit when the EMAs cross
back down, with a protective stop at the recent 5-bar low.
"""

from __future__ import annotations

import pandas as pd

from ..indicators import ema, session_vwap
from .base import EntrySignal, Strategy


class EmaCrossover(Strategy):
    name = "ema_crossover"
    max_trades_per_day = 2

    def __init__(self, fast: int = 9, slow: int = 20, stop_bars: int = 5):
        self.fast_span = fast
        self.slow_span = slow
        self.stop_bars = stop_bars  # protective stop at the low of the last N bars

    def new_day(self, day: pd.DataFrame, prior_close: float | None) -> None:
        super().new_day(day, prior_close)
        self.fast = ema(day["close"], self.fast_span)
        self.slow = ema(day["close"], self.slow_span)
        self.vwap = session_vwap(day)

    def entry_signal(self, i: int) -> EntrySignal | None:
        if i < self.slow_span:
            return None
        fast_now, slow_now = float(self.fast.iloc[i]), float(self.slow.iloc[i])
        fast_prev, slow_prev = float(self.fast.iloc[i - 1]), float(self.slow.iloc[i - 1])
        close = float(self.day["close"].iloc[i])
        vwap_now = float(self.vwap.iloc[i])
        if fast_now > slow_now and fast_prev <= slow_prev and close > vwap_now:
            stop = float(self.day["low"].iloc[max(0, i - self.stop_bars + 1) : i + 1].min())
            self._side = 1
            return EntrySignal(
                reason=f"EMA{self.fast_span}/{self.slow_span} cross up above VWAP",
                stop_price=stop,
                target_r=None,
            )
        if fast_now < slow_now and fast_prev >= slow_prev and close < vwap_now:
            stop = float(self.day["high"].iloc[max(0, i - self.stop_bars + 1) : i + 1].max())
            self._side = -1
            return EntrySignal(
                reason=f"EMA{self.fast_span}/{self.slow_span} cross down below VWAP",
                stop_price=stop,
                target_r=None,
                side="short",
            )
        return None

    def exit_signal(self, i: int) -> bool:
        diff = float(self.fast.iloc[i]) - float(self.slow.iloc[i])
        return diff * getattr(self, "_side", 1) < 0  # EMAs crossed back against the position
