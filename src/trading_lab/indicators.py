"""Causal indicators: the value at bar i depends only on bars 0..i.

That property is what makes it safe for strategies to precompute a full
session's indicator series in new_day() and then read element i bar by bar.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def _ewm_mean(x: np.ndarray, alpha: float) -> np.ndarray:
    """pandas' ewm(alpha=..., adjust=False).mean(), operation for operation
    (same float rounding, same constant-run guard), without pandas' per-call
    overhead — which dominated 10-year backtests on 78-bar sessions."""
    out = np.empty(len(x))
    if not len(x):
        return out
    w = x[0]
    nan_w = w != w
    out[0] = w
    factor, new_wt = 1.0 - alpha, alpha
    for i in range(1, len(x)):
        cur = x[i]
        if not nan_w:
            if cur == cur and w != cur:
                w = (factor * w + new_wt * cur) / (factor + new_wt)
        elif cur == cur:
            w, nan_w = cur, False
        out[i] = w
    return out


def ema(series: pd.Series, span: int) -> pd.Series:
    return pd.Series(
        _ewm_mean(series.to_numpy(dtype=float), 2.0 / (span + 1.0)), index=series.index
    )


def rsi(close: pd.Series, period: int = 2) -> pd.Series:
    """Wilder RSI. All-gain windows read 100, all-loss 0, flat 50."""
    c = close.to_numpy(dtype=float)
    delta = np.empty_like(c)
    delta[0] = np.nan
    delta[1:] = c[1:] - c[:-1]
    gain = np.where(np.isnan(delta), np.nan, np.maximum(delta, 0.0))
    loss = np.where(np.isnan(delta), np.nan, -np.minimum(delta, 0.0))
    avg_gain = _ewm_mean(gain, 1.0 / period)
    avg_loss = _ewm_mean(loss, 1.0 / period)
    with np.errstate(divide="ignore", invalid="ignore"):
        rs = avg_gain / np.where(avg_loss == 0.0, np.nan, avg_loss)
        out = 100.0 - 100.0 / (1.0 + rs)
    out[avg_loss == 0.0] = 100.0
    out[(avg_loss == 0.0) & (avg_gain == 0.0)] = 50.0
    if len(out):
        out[0] = 50.0
    return pd.Series(out, index=close.index)


def session_vwap(day: pd.DataFrame) -> pd.Series:
    """Volume-weighted average price accumulated over one session."""
    h, lo, c = (day[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    v = day["volume"].to_numpy(dtype=float)
    typical = (h + lo + c) / 3.0
    cum_vol = np.cumsum(v)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = np.cumsum(typical * v) / np.where(cum_vol == 0, np.nan, cum_vol)
    return pd.Series(out, index=day.index)


def atr(day: pd.DataFrame, period: int = 14) -> pd.Series:
    """Wilder average true range."""
    h, lo, c = (day[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    prev_close = np.empty_like(c)
    prev_close[0] = np.nan
    prev_close[1:] = c[:-1]
    tr = np.fmax(np.fmax(h - lo, np.abs(h - prev_close)), np.abs(lo - prev_close))
    return pd.Series(_ewm_mean(tr, 1.0 / period), index=day.index)


def bollinger(
    close: pd.Series, period: int = 20, num_std: float = 2.0
) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    """(mid, upper, lower, bandwidth). Bandwidth = (upper - lower) / mid."""
    mid = close.rolling(period, min_periods=period).mean()
    std = close.rolling(period, min_periods=period).std(ddof=0)
    upper = mid + num_std * std
    lower = mid - num_std * std
    bandwidth = (upper - lower) / mid
    return mid, upper, lower, bandwidth
