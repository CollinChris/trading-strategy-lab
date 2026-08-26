"""Market data loading via yfinance, with a simple same-day disk cache."""

from __future__ import annotations

import datetime as dt
import time
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


def _download(symbols: list[str], interval: str, period: str, threads: bool) -> dict[str, pd.DataFrame]:
    """One yf.download pass, normalized per symbol; a failed symbol comes back empty."""
    raw = yf.download(
        tickers=" ".join(symbols),
        interval=interval,
        period=period,
        auto_adjust=True,
        group_by="ticker",
        progress=False,
        threads=threads,
    )
    out: dict[str, pd.DataFrame] = {}
    for sym in symbols:
        try:
            frame = raw[sym] if len(symbols) > 1 else raw.droplevel("Ticker", axis=1)
            out[sym] = _normalize(frame)
        except Exception:  # noqa: BLE001 — a symbol absent from the batch is just a failed download
            out[sym] = pd.DataFrame(columns=COLUMNS)
    return out


def load_bars(
    symbols: list[str],
    interval: str,
    period: str,
    cache_dir: Path = CACHE_DIR,
    on_missing: str = "raise",
) -> dict[str, pd.DataFrame]:
    """Intraday OHLCV per symbol (tz-aware America/New_York index).

    Cached to disk per symbol; the cache is reused only if written today,
    so repeated runs on the same day don't refetch.

    Symbols whose download fails are retried single-threaded (yfinance's
    sqlite cache throws transient 'database is locked' errors under its own
    threading). If a symbol still has no data: on_missing="raise" aborts
    (backtests must not silently drop a symbol), "skip" warns and leaves it
    out of the result (paper runs repeat all day — missing one pass is fine).
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
        frames = _download(missing, interval, period, threads=True)
        for attempt in (1, 2):
            failed = [sym for sym in missing if frames[sym].empty]
            if not failed:
                break
            time.sleep(2 * attempt)
            frames.update(_download(failed, interval, period, threads=False))
        for sym in missing:
            bars = frames[sym]
            if bars.empty:
                if on_missing == "skip":
                    print(f"warning: no data for {sym} after retries — skipping it this run")
                    continue
                raise RuntimeError(f"No data returned for {sym}")
            bars.to_pickle(cache_dir / f"{sym}_{interval}_{period}.pkl")
            result[sym] = bars

    return {sym: result[sym] for sym in symbols if sym in result}


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
