"""Study B — earnings-reaction drift (docs/research/PREREGISTRATION.md, section B).

Announcements are 8-K filings with item 2.02 (Results of Operations), timed by EDGAR's
acceptance timestamp. A big market-adjusted day-0 reaction, relative to recent
announcements, is bet to keep drifting the same way for a week.
"""

from __future__ import annotations

from collections import deque
from pathlib import Path

import numpy as np
import pandas as pd

from ..data import market_today
from . import engine
from .prices import Panel
from .sec import SUBMISSIONS_URL, SecClient, ticker_map, to_alpaca

TOP_N = 1000
LOOKBACK = 500
MIN_HISTORY = 200
HIGH, LOW = 0.9, 0.1
ENTRY_LAG, EXIT_LAG = 1, 6  # closes after day 0


def fetch_announcements(client: SecClient, ciks: dict[int, str], since: str = "2015-10-01"):
    """8-K item 2.02 acceptance times for each CIK (EDGAR submissions API, including
    the older-filings pages that `recent` overflows into)."""
    rows = []
    for n, (cik, symbol) in enumerate(ciks.items(), 1):
        data = client.get_json(SUBMISSIONS_URL.format(name=f"CIK{cik:010d}.json"))
        if not data:
            continue
        blocks = [data.get("filings", {}).get("recent", {})]
        for page in data.get("filings", {}).get("files", []):
            if page.get("filingTo", "") >= since:
                extra = client.get_json(SUBMISSIONS_URL.format(name=page["name"]))
                if extra:
                    blocks.append(extra.get("filings", {}).get("recent", extra))
        for b in blocks:
            for form, items, accepted in zip(
                b.get("form", []), b.get("items", []), b.get("acceptanceDateTime", []), strict=False
            ):
                if form == "8-K" and "2.02" in str(items).split(","):
                    rows.append((cik, symbol, accepted))
        if n % 250 == 0:
            print(f"earnings: {n}/{len(ciks)} companies, {len(rows):,} announcements")
    return pd.DataFrame(rows, columns=["cik", "symbol", "accepted_raw"])


def parse_accepted(raw: pd.Series) -> pd.Series:
    """EDGAR acceptance stamps are US Eastern wall-clock time even though the
    submissions API writes them with a trailing 'Z'; the report's time-of-day
    profile is the check (releases cluster before the open and after the close)."""
    return pd.to_datetime(raw.astype(str).str[:19], format="%Y-%m-%dT%H:%M:%S", errors="coerce")


def day_zero(accepted_et: pd.Series, sessions: pd.DatetimeIndex) -> np.ndarray:
    """Session position of day 0: the announcement session if accepted before 09:30 ET
    on a trading day, otherwise the next session (len(sessions) if beyond the data)."""
    sess = sessions.as_unit("ns").to_numpy()
    day = accepted_et.dt.normalize().to_numpy("datetime64[ns]")
    minutes = (accepted_et.dt.hour * 60 + accepted_et.dt.minute).to_numpy()
    same = np.searchsorted(sess, day, side="left")
    nxt = np.searchsorted(sess, day, side="right")
    on_session = (same < len(sess)) & (sess[np.minimum(same, len(sess) - 1)] == day)
    return np.where(on_session & (minutes < 9 * 60 + 30), same, nxt)


def percentiles(
    day_i: np.ndarray,
    reaction: np.ndarray,
    lookback: int = LOOKBACK,
    min_history: int = MIN_HISTORY,
) -> np.ndarray:
    """Each event's share of the previous `lookback` events' reactions (earlier day 0
    only) that are below its own; NaN until `min_history` events have been seen.
    Inputs must be sorted by day_i."""
    hist: deque[float] = deque(maxlen=lookback)
    out = np.full(len(day_i), np.nan)
    start = 0
    while start < len(day_i):
        end = start
        while end < len(day_i) and day_i[end] == day_i[start]:
            end += 1
        if len(hist) >= min_history:
            arr = np.fromiter(hist, dtype="float64")
            out[start:end] = (arr[None, :] < reaction[start:end, None]).mean(axis=1)
        hist.extend(reaction[start:end])
        start = end
    return out


def build_trades(
    events: pd.DataFrame, panel: Panel, rank: pd.DataFrame, beta: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Returns (eligible events with reaction and percentile, trades)."""
    sessions = panel.sessions
    ev = events.assign(day0_i=day_zero(events["accepted"], sessions))
    ev = ev[(ev["day0_i"] >= 1) & (ev["day0_i"] < len(sessions))]
    ev = ev.sort_values(["day0_i", "symbol", "accepted"]).drop_duplicates(["symbol", "day0_i"])
    ev["rank"] = engine.lookup(rank, ev["symbol"], ev["day0_i"])
    ev = ev[ev["rank"] <= TOP_N].copy()
    c1 = engine.lookup(panel.close, ev["symbol"], ev["day0_i"])
    c0 = engine.lookup(panel.close, ev["symbol"], ev["day0_i"] - 1)
    spy = panel.close["SPY"].to_numpy(dtype="float64")
    m = spy[ev["day0_i"]] / spy[ev["day0_i"] - 1] - 1
    ev["beta"] = np.nan_to_num(engine.lookup(beta, ev["symbol"], ev["day0_i"]), nan=1.0)
    ev["reaction"] = (c1 / c0 - 1) - ev["beta"] * m
    ev = ev.dropna(subset=["reaction"]).sort_values(["day0_i", "symbol"]).reset_index(drop=True)
    ev["pct"] = percentiles(ev["day0_i"].to_numpy(), ev["reaction"].to_numpy())
    pick = ev[(ev["pct"] >= HIGH) | (ev["pct"] <= LOW)].copy()
    pick["direction"] = np.where(pick["pct"] >= HIGH, 1, -1)
    pick["entry_i"] = pick["day0_i"] + ENTRY_LAG
    pick["exit_i"] = pick["day0_i"] + EXIT_LAG
    pick = pick[pick["exit_i"] < len(sessions)].copy()
    # Hedge ratio as of the entry session (data through day 0).
    pick["beta"] = np.nan_to_num(engine.lookup(beta, pick["symbol"], pick["entry_i"]), nan=1.0)
    pick["entry_at"] = "close"
    return ev, pick.reset_index(drop=True)


def run(panel_dir: Path, out: Path = Path("results/EARNINGS.md")) -> Path:
    panel = Panel.load(panel_dir)
    rank = engine.universe_rank(panel)
    start = panel.sessions.searchsorted(pd.Timestamp("2016-01-01"))
    ever = set(rank.columns[(rank.iloc[start:] <= TOP_N).any()])
    client = SecClient()
    ciks = {}
    for cik, tickers in ticker_map(client).items():
        listed = [to_alpaca(t) for t in tickers if to_alpaca(t) in ever]
        if listed:
            ciks[cik] = listed[0]
    print(f"earnings: {len(ciks):,} companies in the universe have a CIK")
    events = fetch_announcements(client, ciks)
    events["accepted"] = parse_accepted(events["accepted_raw"])
    events = events.dropna(subset=["accepted"])
    events = events[events["accepted"] >= pd.Timestamp("2015-12-01")]
    syms = sorted(set(events["symbol"]) & set(panel.close.columns) | {"SPY"})
    beta = engine.rolling_beta(panel.close[syms], panel.close["SPY"])
    ev, trades = build_trades(events, panel, rank, beta)
    results, daily = engine.simulate(trades, panel)
    return write_report(events, ev, results, daily, panel, out)


def write_report(events, ev, results, daily, panel: Panel, out: Path) -> Path:
    sessions = panel.sessions
    done = results[results["adj_ret"].notna()].copy()
    if done.empty:
        out.write_text("# Earnings-reaction drift\n\nNo tradable events — check the inputs.\n")
        return out
    port = engine.portfolio(daily, sessions)
    span = (int(daily["day_i"].min()), int(daily["day_i"].max()))
    s = engine.summarize(port)
    passed, reason = engine.decide(s, min_sharpe=0.5)
    done["leg"] = np.where(done["direction"] > 0, "long (top decile)", "short (bottom decile)")
    done["tercile"] = pd.cut(
        done["rank"], [0, 333, 666, TOP_N], labels=["1–333", "334–666", "667–1000"]
    )
    minutes = events["accepted"].dt.hour * 60 + events["accepted"].dt.minute
    pre, post = (minutes < 570).mean(), (minutes >= 960).mean()
    text = f"""# Earnings-reaction drift (pre-registered study B)

Generated {market_today()} from SEC 8-K item 2.02 filings and Alpaca daily bars. Rules
fixed in advance: [PREREGISTRATION.md](../docs/research/PREREGISTRATION.md), section B.

## Verdict: {"**PASS**" if passed else "**FAIL**"}

{reason}.

{"Next step per the pre-registration: paper-trade it in a separate Alpaca paper account, judged on tracking this backtest." if passed else "Per the pre-registration, a failed idea is archived — not re-run with new settings."}

## What was tested

- {len(events):,} earnings 8-Ks → {len(ev):,} with a day-0 reaction in the top-{TOP_N}
  universe → {len(done):,} trades (reaction in the top or bottom decile of the previous
  {LOOKBACK} announcements; {sessions[span[0]].date()} → {sessions[span[1]].date()}).
- Enter at the close of day +{ENTRY_LAG}, exit at the close of day +{EXIT_LAG}, in the
  direction of the reaction; hedged with beta × SPY; 5 bp per side plus 1 bp on the hedge.
- Calendar-time portfolio over {s["days"]:,} trading days ({s["active_days"]:,} with positions).

## Headline numbers

| measure | value |
|---|---|
| mean daily portfolio return (market-adjusted, net) | {engine.bp(s["mean_daily"])} |
| 95% range, resampled by day | {engine.bp(s["lo_daily"])} to {engine.bp(s["hi_daily"])} |
| annualised Sharpe | {engine.num(s["sharpe"])} |
| mean per trade (5 sessions) | {engine.pct(done["adj_ret"].mean())} |

## Descriptive only (cannot rescue a failed primary)

By leg:

{engine.breakdown(done, daily, done["leg"], sessions, span, "leg")}

By liquidity tercile on day 0:

{engine.breakdown(done, daily, done["tercile"].astype(str), sessions, span, "liquidity rank")}

By year (portfolio):

{engine.by_year(port)}

Data check — acceptance times (read as US Eastern): {pre:.0%} before 09:30, {post:.0%} at or
after 16:00, {1 - pre - post:.0%} during the session. Most US companies release before the
open or after the close, so a large "during the session" share would mean a time-zone error.

Accepted limitation (stated in advance): SEC's ticker map lists current companies only, so
announcements by since-delisted firms are missing.
"""
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    return out
