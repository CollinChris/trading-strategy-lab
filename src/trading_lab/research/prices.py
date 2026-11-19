"""Daily price panels for the event studies: every listed US stock, 2015+, from Alpaca.

Two passes over Alpaca's daily bars (consolidated SIP feed): split- and dividend-adjusted
open/close for returns, and unadjusted close/volume for the liquidity screen (an adjusted
price would put pre-split NVDA under $5). Stored wide — sessions × symbols, float32 — and
pruned to symbols that could ever pass the screen, so a run's panel is a few hundred MB.

Raw REST instead of alpaca-py: tens of millions of bars as SDK objects is far too slow.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

BARS_URL = "https://data.alpaca.markets/v2/stocks/bars"
ASSETS_URL = "https://paper-api.alpaca.markets/v2/assets"
EXCHANGES = {"NYSE", "NASDAQ", "ARCA", "AMEX", "BATS"}  # major venues; OTC excluded
PANEL_DIR = Path("data/research/panel")
FIELDS = ("open", "close", "close_raw", "volume_raw")
BATCH = 200  # symbols per request (URL length)
MIN_INTERVAL = 60 / 190  # stay under the free plan's 200 requests/minute


def _headers() -> dict[str, str]:
    from dotenv import load_dotenv

    load_dotenv(Path.cwd() / ".env")
    return {
        "APCA-API-KEY-ID": os.environ["ALPACA_API_KEY"],
        "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"],
    }


_last_call = 0.0


def _rate_limit_wait(exc: urllib.error.HTTPError, attempt: int) -> float:
    """Seconds to wait after a 429: until Alpaca's window resets if it says when."""
    reset = exc.headers.get("X-RateLimit-Reset") if exc.headers else None
    if reset and reset.isdigit():
        return min(65.0, max(1.0, int(reset) - time.time() + 1))
    return min(60.0, 5.0 * (attempt + 1))


def get_json(url: str, params: dict, headers: dict, tries: int = 6) -> dict | list:
    """GET with a global request pace and bounded retries. Rate limits (429) are
    shared across every job using the account — e.g. a price download and the news
    archive at once — so 429s wait for the window to reset, up to 40 times, while
    server errors and network failures get `tries` attempts."""
    global _last_call
    query = url + ("?" + urllib.parse.urlencode(params) if params else "")
    failures = limited = 0
    while True:
        wait = _last_call + MIN_INTERVAL - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        _last_call = time.monotonic()
        try:
            req = urllib.request.Request(query, headers=headers)
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and limited < 40:
                limited += 1
                time.sleep(_rate_limit_wait(exc, limited))
                continue
            if exc.code not in (500, 502, 503, 504) or failures == tries - 1:
                raise
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            if failures == tries - 1:
                raise
        failures += 1
        time.sleep(min(60, 5 * 2**failures))


TICKER = re.compile(r"^[A-Z]{1,5}(\.[A-Z]{1,2})?$")  # plain tickers + share classes (BRK.B)


def list_symbols(headers: dict) -> list[str]:
    """Active and delisted US equities on major exchanges, plus SPY for the hedge.
    (Alpaca also lists CUSIP-style codes for some dead assets — skipped.)"""
    symbols = {"SPY"}
    for status in ("active", "inactive"):
        assets = get_json(ASSETS_URL, {"status": status, "asset_class": "us_equity"}, headers)
        symbols.update(
            a["symbol"]
            for a in assets
            if a.get("exchange") in EXCHANGES and TICKER.match(a["symbol"])
        )
    return sorted(symbols)


def _fetch(symbols: list[str], start: dt.date, end: dt.date, adjustment: str, headers: dict):
    """Yield (symbol, dates, opens, closes, volumes) for one batch, all pages."""
    params = {
        "symbols": ",".join(symbols),
        "timeframe": "1Day",
        "start": start.isoformat(),
        "end": end.isoformat(),
        "adjustment": adjustment,
        "feed": "sip",
        "limit": 10000,
    }
    acc: dict[str, list] = {}
    while True:
        payload = get_json(BARS_URL, params, headers)
        for sym, bars in (payload.get("bars") or {}).items():
            acc.setdefault(sym, []).extend(bars)
        token = payload.get("next_page_token")
        if not token:
            break
        params["page_token"] = token
    for sym, bars in acc.items():
        # Daily bars are stamped at midnight New York in UTC: the first 10 chars are the date.
        yield (
            sym,
            [b["t"][:10] for b in bars],
            [b["o"] for b in bars],
            [b["c"] for b in bars],
            [b["v"] for b in bars],
        )


@dataclass
class Panel:
    """Wide daily panels, index = sessions (SPY's trading days), columns = symbols."""

    open: pd.DataFrame
    close: pd.DataFrame
    close_raw: pd.DataFrame
    volume_raw: pd.DataFrame

    @property
    def sessions(self) -> pd.DatetimeIndex:
        return self.close.index

    def save(self, out: Path = PANEL_DIR) -> Path:
        out.mkdir(parents=True, exist_ok=True)
        for name in FIELDS:
            getattr(self, name).to_pickle(out / f"{name}.pkl")
        return out

    @classmethod
    def load(cls, path: Path = PANEL_DIR) -> Panel:
        return cls(*(pd.read_pickle(path / f"{name}.pkl") for name in FIELDS))


def _wide(rows: list[tuple[str, list[str], list[float]]]) -> pd.DataFrame:
    """(symbol, dates, values) rows → one float32 column per symbol."""
    return pd.DataFrame(
        {
            sym: pd.Series(np.asarray(vals, dtype=np.float32), index=pd.DatetimeIndex(dates))
            for sym, dates, vals in rows
            if dates
        }
    )


def fetch_panel(
    start: dt.date, end: dt.date, symbols: list[str] | None = None, min_price: float = 5.0
) -> Panel:
    headers = _headers()
    symbols = symbols or list_symbols(headers)
    print(f"bars: {len(symbols)} symbols, {start} → {end}")
    parts: dict[str, list[pd.DataFrame]] = {f: [] for f in FIELDS}
    t0 = time.monotonic()
    for i in range(0, len(symbols), BATCH):
        batch = symbols[i : i + BATCH]
        adj = list(_fetch(batch, start, end, "all", headers))
        raw = list(_fetch(batch, start, end, "raw", headers))
        parts["open"].append(_wide([(s, d, o) for s, d, o, _, _ in adj]))
        parts["close"].append(_wide([(s, d, c) for s, d, _, c, _ in adj]))
        parts["close_raw"].append(_wide([(s, d, c) for s, d, _, c, _ in raw]))
        parts["volume_raw"].append(_wide([(s, d, v) for s, d, _, _, v in raw]))
        done = min(i + BATCH, len(symbols))
        if (i // BATCH) % 10 == 0 or done == len(symbols):
            print(f"  {done}/{len(symbols)} symbols, {time.monotonic() - t0:.0f}s")
    frames = {f: pd.concat(p, axis=1) for f, p in parts.items()}
    sessions = frames["close"]["SPY"].dropna().index.sort_values()
    frames = {f: x.reindex(sessions).sort_index(axis=1) for f, x in frames.items()}
    # Prune symbols that can never pass the screen: never at the minimum price, or too short.
    raw = frames["close_raw"]
    keep = raw.columns[(raw.max() >= min_price) & (raw.notna().sum() >= 250)]
    keep = keep.union(pd.Index(["SPY"]))
    panel = Panel(*(frames[f][keep] for f in FIELDS))
    print(f"bars: kept {len(keep)} symbols × {len(sessions)} sessions")
    return panel
