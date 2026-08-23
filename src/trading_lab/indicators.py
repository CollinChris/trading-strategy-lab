"""Causal indicators: the value at bar i depends only on bars 0..i.

That property is what makes it safe for strategies to precompute a full
session's indicator series in new_day() and then read .iloc[i] bar by bar.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def rsi(close: pd.Series, period: int = 2) -> pd.Series:
    """Wilder RSI. All-gain windows read 100, all-loss 0, flat 50."""
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1.0 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    out = 100.0 - 100.0 / (1.0 + rs)
    out[avg_loss == 0.0] = 100.0
    out[(avg_loss == 0.0) & (avg_gain == 0.0)] = 50.0
    out.iloc[0] = 50.0
    return out


def session_vwap(day: pd.DataFrame) -> pd.Series:
    """Volume-weighted average price accumulated over one session."""
    typical = (day["high"] + day["low"] + day["close"]) / 3.0
    cum_vol = day["volume"].cumsum()
    return (typical * day["volume"]).cumsum() / cum_vol.replace(0, np.nan)
