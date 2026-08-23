"""Market data loading via yfinance, with a simple same-day disk cache."""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import yfinance as yf

MARKET_TZ = ZoneInfo("America/New_York")
CACHE_DIR = Path("data")
COLUMNS = ["open", "high", "low", "close", "volume"]


def market_today() -> dt.date:
    """Current date in market time — NOT the local (e.g. Singapore) date."""
    return dt.datetime.now(tz=MARKET_TZ).date()


def _normalize(frame: pd.DataFrame) -> pd.DataFrame:
    """Lowercase single-level OHLCV columns, regular-hours bars only, no NaN rows."""
    out = frame.copy()
    out.columns = [str(c).lower() for c in out.columns]
    out = out[COLUMNS].dropna()
    out = out[out["volume"] > 0]
    # yfinance intraday is already regular-hours, but be explicit and DST-safe.
    out = out.between_time("09:30", "15:59")
    return out


def load_bars(
    symbols: list[str], interval: str, period: str, cache_dir: Path = CACHE_DIR
) -> dict[str, pd.DataFrame]:
    """Intraday OHLCV per symbol (tz-aware America/New_York index).

    Cached to disk per symbol; the cache is reused only if written today,
    so repeated runs on the same day don't refetch.
    """
    cache_dir.mkdir(exist_ok=True)
    today = market_today().isoformat()
    result: dict[str, pd.DataFrame] = {}
    missing: list[str] = []

    for sym in symbols:
        path = cache_dir / f"{sym}_{interval}_{period}.pkl"
        written = (
            dt.datetime.fromtimestamp(path.stat().st_mtime, tz=MARKET_TZ) if path.exists() else None
        )
        if written is not None and written.date().isoformat() == today:
            result[sym] = pd.read_pickle(path)
        else:
            missing.append(sym)

    if missing:
        raw = yf.download(
            tickers=" ".join(missing),
            interval=interval,
            period=period,
            auto_adjust=True,
            group_by="ticker",
            progress=False,
            threads=True,
        )
        for sym in missing:
            frame = raw[sym] if len(missing) > 1 else raw.droplevel("Ticker", axis=1)
            bars = _normalize(frame)
            if bars.empty:
                raise RuntimeError(f"No data returned for {sym}")
            bars.to_pickle(cache_dir / f"{sym}_{interval}_{period}.pkl")
            result[sym] = bars

    return {sym: result[sym] for sym in symbols}


def split_days(bars: pd.DataFrame) -> list[tuple[dt.date, pd.DataFrame, float | None]]:
    """Split a symbol's bars into (date, day_bars, prior_session_close) tuples.

    prior_session_close comes from the same intraday series (last bar of the
    previous session) so gap calculations aren't skewed by mixing differently
    adjusted daily data. The first day in the window has no prior close.
    """
    out: list[tuple[dt.date, pd.DataFrame, float | None]] = []
    prior_close: float | None = None
    for date, day in bars.groupby(bars.index.date, sort=True):
        out.append((date, day, prior_close))
        prior_close = float(day["close"].iloc[-1])
    return out
