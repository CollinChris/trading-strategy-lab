"""News momentum — buy confirmed strength right after a fresh headline.

The catalyst logic behind most momentum day trading: news creates the crowd.
Rule: if a headline for this symbol landed within the last `window_min`
minutes AND the current bar confirms (breaks the prior bar's high, on volume
above the day's average, above session VWAP), buy; stop under the last three
bars' low, take profit at 2R.

Headlines come from Alpaca's news API via data.load_news(); with no keys the
strategy simply never fires.
"""

from __future__ import annotations

import pandas as pd

from ..indicators import session_vwap
from .base import EntrySignal, Strategy

NewsIndex = dict[tuple[str, "object"], list[pd.Timestamp]]


class NewsMomentum(Strategy):
    name = "news_momentum"
    max_trades_per_day = 2

    def __init__(
        self,
        news_index: NewsIndex | None = None,
        window_min: int = 45,
        vol_mult: float = 1.5,
        target_r: float = 2.0,
    ):
        self.news_index = news_index or {}
        self.window_min = window_min
        self.vol_mult = vol_mult
        self.target_r = target_r

    def new_day(self, day: pd.DataFrame, prior_close: float | None) -> None:
        super().new_day(day, prior_close)
        self.vwap = session_vwap(day)
        self.headlines = self.news_index.get((self.symbol, day.index[0].date()), [])

    def entry_signal(self, i: int) -> EntrySignal | None:
        if i < 3 or not self.headlines:
            return None
        ts = self.day.index[i]
        fresh = any(0 <= (ts - h).total_seconds() <= self.window_min * 60 for h in self.headlines)
        if not fresh:
            return None
        close = float(self.day["close"].iloc[i])
        breakout = close > float(self.day["high"].iloc[i - 1])
        avg_vol = float(self.day["volume"].iloc[:i].mean())
        confirmed_vol = float(self.day["volume"].iloc[i]) > self.vol_mult * avg_vol
        above_vwap = close > float(self.vwap.iloc[i])
        if breakout and confirmed_vol and above_vwap:
            stop = float(self.day["low"].iloc[i - 2 : i + 1].min())
            return EntrySignal(
                reason=f"fresh headline <{self.window_min}m + breakout on volume",
                stop_price=stop,
                target_r=self.target_r,
            )
        return None
