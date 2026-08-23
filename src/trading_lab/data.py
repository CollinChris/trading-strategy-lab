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


def load_news(
    symbols: list[str], interval: str, period: str, cache_dir: Path = CACHE_DIR
) -> dict[tuple[str, dt.date], list[pd.Timestamp]]:
    """Headline timestamps per (symbol, session date) from Alpaca's news API.

    Best-effort: returns {} (and warns) without keys or on any API failure, so
    everything except the news strategy works keyless. Cached for the day.
    """
    import json
    import os
    import urllib.parse
    import urllib.request

    from dotenv import load_dotenv

    load_dotenv()
    key, secret = os.getenv("ALPACA_API_KEY"), os.getenv("ALPACA_SECRET_KEY")
    if not key or not secret:
        print("warning: no Alpaca keys — news_momentum will take no trades")
        return {}

    cache_dir.mkdir(exist_ok=True)
    cache = cache_dir / f"news_{'-'.join(sorted(symbols))}_{period}.pkl"
    if (
        cache.exists()
        and dt.datetime.fromtimestamp(cache.stat().st_mtime, tz=MARKET_TZ).date() == market_today()
    ):
        return pd.read_pickle(cache)

    # +35d buffer: yfinance's "60d" of intraday bars spans more calendar days
    # than 60, and the news window must cover every session that has bars.
    days = int("".join(ch for ch in period if ch.isdigit()) or 60) + 35
    start = (market_today() - dt.timedelta(days=days)).isoformat()
    index: dict[tuple[str, dt.date], list[pd.Timestamp]] = {}
    try:
        for sym in symbols:
            token: str | None = None
            for _ in range(40):  # page cap per symbol
                params = {"symbols": sym, "start": start, "limit": "50"}
                if token:
                    params["page_token"] = token
                req = urllib.request.Request(
                    "https://data.alpaca.markets/v1beta1/news?" + urllib.parse.urlencode(params),
                    headers={"APCA-API-KEY-ID": key, "APCA-API-SECRET-KEY": secret},
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    payload = json.loads(resp.read())
                for item in payload.get("news", []):
                    ts = pd.Timestamp(item["created_at"]).tz_convert(MARKET_TZ)
                    index.setdefault((sym, ts.date()), []).append(ts)
                token = payload.get("next_page_token")
                if not token:
                    break
    except Exception as exc:  # noqa: BLE001 — news is best-effort; never fail the run
        print(f"warning: news fetch failed ({exc}) — news_momentum will take no trades")
        return {}

    for stamps in index.values():
        stamps.sort()
    pd.to_pickle(index, cache)
    total = sum(len(v) for v in index.values())
    print(f"news: {total} headlines across {len(symbols)} symbols since {start}")
    return index


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
