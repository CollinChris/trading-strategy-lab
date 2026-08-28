"""AR(p) return forecast — the lab's first time-series model.

Unlike the eight rule-based strategies, this one fits a statistical model:
an autoregression on 5-minute log returns, refit on every bar by numpy least
squares (no new dependencies), forecasting the CUMULATIVE return over the
next `horizon` bars directly. Enter long when the forecast clears round-trip
slippage with margin; exit when the horizon lapses or a fresh forecast turns
negative. Protective stop below entry, flat by end of day.

Cross-session state: the engine feeds sessions chronologically (see
Strategy), so new_day() banks each finished session's returns into a rolling
window and fits on the last `window_sessions` sessions plus today so far.
Lag windows never span a session boundary — overnight gaps are not 5-minute
returns.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

from .base import EntrySignal, Strategy


class ArForecast(Strategy):
    name = "ar_forecast"
    max_trades_per_day = 2

    def __init__(
        self,
        lags: int = 12,  # one hour of 5-minute returns
        horizon: int = 6,  # forecast the next 30 minutes
        threshold: float = 0.0015,  # enter above 15 bps — round-trip slippage plus margin
        window_sessions: int = 5,
        min_obs: int = 100,  # training rows required before the model may trade
        stop_pct: float = 0.01,
    ):
        self.lags = lags
        self.horizon = horizon
        self.threshold = threshold
        self.window_sessions = window_sessions
        self.min_obs = min_obs
        self.stop_pct = stop_pct
        self._past: list[np.ndarray] = []  # finished sessions' return series, oldest first
        self._today_r: np.ndarray = np.empty(0)
        self._entry_bar: int | None = None
        self._forecasts: dict[int, float] = {}

    def new_day(self, day: pd.DataFrame, prior_close: float | None) -> None:
        if len(self._today_r):  # bank the session that just finished
            self._past.append(self._today_r)
            self._past = self._past[-self.window_sessions :]
        super().new_day(day, prior_close)
        self._today_r = np.diff(np.log(day["close"].to_numpy(dtype=float)))
        self._entry_bar = None
        self._forecasts = {}

    def _design(self, seg: np.ndarray) -> tuple[np.ndarray, np.ndarray] | None:
        """(X, y) pairs from one session: lag window -> next-horizon cumulative return."""
        n = len(seg)
        rows = n - self.lags - self.horizon + 1
        if rows < 1:
            return None
        x = sliding_window_view(seg, self.lags)[:rows]
        c = np.concatenate(([0.0], np.cumsum(seg)))
        y = c[self.lags + self.horizon : n + 1] - c[self.lags : n - self.horizon + 1]
        return x, y

    def _forecast(self, i: int) -> float | None:
        """Fit on everything strictly before bar i's close and predict the next
        `horizon` bars. Causal: uses past sessions plus today's returns [:i] only."""
        if i in self._forecasts:
            return self._forecasts[i]
        today = self._today_r[:i]
        if len(today) < self.lags:
            return None
        parts = [self._design(seg) for seg in [*self._past, today]]
        parts = [p for p in parts if p is not None]
        if not parts:
            return None
        x = np.vstack([p[0] for p in parts])
        y = np.concatenate([p[1] for p in parts])
        if len(y) < self.min_obs:
            return None
        a = np.column_stack([np.ones(len(x)), x])
        beta, *_ = np.linalg.lstsq(a, y, rcond=None)
        pred = float(np.concatenate(([1.0], today[-self.lags :])) @ beta)
        if not np.isfinite(pred):
            return None
        self._forecasts[i] = pred
        return pred

    def entry_signal(self, i: int) -> EntrySignal | None:
        pred = self._forecast(i)
        if pred is not None and pred > self.threshold:
            self._entry_bar = i
            return EntrySignal(
                reason=f"AR({self.lags}) forecasts {pred * 100:+.2f}% over {self.horizon} bars",
                stop_pct=self.stop_pct,
                target_r=None,
            )
        return None

    def exit_signal(self, i: int) -> bool:
        if self._entry_bar is not None and i - self._entry_bar >= self.horizon:
            return True
        pred = self._forecast(i)
        return pred is not None and pred < 0.0
