"""Market adjustment: what a trade earned beyond SPY's move over the same hold.

Two months of paper trading showed why raw P&L misleads here: SPY was flat
overall but fell intraday on most days, so shorts "won" and longs "lost" with
no skill involved (short P&L tracked SPY's intraday move at r = -0.64). Every
trade is therefore also scored as if it carried a beta-weighted SPY hedge in
the opposite direction — a synthetic market-neutral version of the same trade,
charged the hedge's own round-trip slippage.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def _intraday_returns(bars: pd.DataFrame) -> pd.Series:
    """5-minute log returns within each session (overnight gaps excluded)."""
    logc = np.log(bars["close"].astype(float))
    return logc.groupby(bars.index.date).diff().dropna()


def beta(symbol_bars: pd.DataFrame, spy_bars: pd.DataFrame, min_obs: int = 300) -> float:
    """Intraday beta of a symbol to SPY from matching 5-minute returns.
    Falls back to 1.0 (a plain dollar hedge) when there is too little overlap."""
    joined = pd.concat(
        [_intraday_returns(symbol_bars).rename("s"), _intraday_returns(spy_bars).rename("m")],
        axis=1,
        join="inner",
    )
    if len(joined) < min_obs or joined["m"].var() == 0:
        return 1.0
    return float(joined["s"].cov(joined["m"]) / joined["m"].var())


def price_at(bars: pd.DataFrame, ts: pd.Timestamp) -> float | None:
    """Last completed 5-minute close at or before ts (same convention at entry
    and exit, so the measured SPY move covers the trade's hold)."""
    if bars is None or bars.empty:
        return None
    t = ts.tz_convert(bars.index.tz) if ts.tzinfo is not None else ts
    # Alpaca fill times carry microseconds; match the bar index's resolution.
    unit = bars.index.unit
    t = t.floor(unit).as_unit(unit) if unit != "ns" else t
    if t < bars.index[0] or t > bars.index[-1] + pd.Timedelta(minutes=10):
        return None  # outside the data window — never guess
    px = bars["close"].asof(t - pd.Timedelta(minutes=5))
    if pd.isna(px):  # inside the very first bar
        px = bars["open"].iloc[0]
    return float(px)


def spy_return(
    spy_bars: pd.DataFrame | None, entry: pd.Timestamp, exit_: pd.Timestamp
) -> float | None:
    p0, p1 = price_at(spy_bars, entry), price_at(spy_bars, exit_)
    if p0 is None or p1 is None or p0 == 0:
        return None
    return p1 / p0 - 1.0


def adjusted_pnl(
    pnl: float,
    direction: int,
    notional: float,
    beta_: float,
    spy_ret: float | None,
    slippage_bps: float,
) -> float | None:
    """P&L of the trade plus an opposite, beta-weighted SPY position held over
    the same window, minus that hedge's round-trip slippage."""
    if spy_ret is None:
        return None
    hedge = -direction * beta_ * notional * spy_ret
    cost = 2.0 * slippage_bps / 10_000.0 * abs(beta_) * notional
    return pnl + hedge - cost
