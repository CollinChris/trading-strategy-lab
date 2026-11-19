"""Study A — insider cluster purchases (docs/research/PREREGISTRATION.md, section A).

Source: SEC's quarterly Insider Transactions Data Sets (flattened Forms 3/4/5;
tab-delimited UTF-8; dates as DD-MON-YYYY). A cluster is two or more directors or
officers buying their own company's stock within a week of each other — the
Cohen-Malloy-Pomorski "opportunistic" signal in its simplest form.
"""

from __future__ import annotations

import csv
import datetime as dt
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from ..data import market_today
from . import engine
from .prices import Panel
from .sec import FORM345_URL, SEC_DIR, SecClient, ticker_map, to_alpaca

TOP_N = 1000
HOLD = 40  # sessions, entry session counted as the first
WINDOW_DAYS = 7
COOLDOWN_DAYS = 60
FIRST_YEAR = 2016

_COLS = {
    "SUBMISSION": {"ACCESSION_NUMBER", "FILING_DATE", "DOCUMENT_TYPE", "ISSUERCIK"}
    | {"ISSUERTRADINGSYMBOL"},
    "REPORTINGOWNER": {"ACCESSION_NUMBER", "RPTOWNERCIK", "RPTOWNER_RELATIONSHIP"},
    "NONDERIV_TRANS": {
        "ACCESSION_NUMBER",
        "TRANS_DATE",
        "TRANS_CODE",
        "TRANS_PRICEPERSHARE",
        "TRANS_ACQUIRED_DISP_CD",
    },
}


def _sec_date(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s.str.strip(), format="%d-%b-%Y", errors="coerce")


def _read(z: zipfile.ZipFile, table: str) -> pd.DataFrame:
    name = next(n for n in z.namelist() if Path(n).stem.upper() == table)
    want = _COLS[table]
    with z.open(name) as fh:
        return pd.read_csv(
            fh,
            sep="\t",
            dtype=str,
            quoting=csv.QUOTE_NONE,
            encoding_errors="replace",
            on_bad_lines="skip",
            # the Rule 10b5-1 flag (AFF10B5ONE) exists only in 2023+ files
            usecols=lambda c: c.upper() in want or "10B5" in c.upper(),
        ).rename(columns=str.upper)


def qualifying(sub: pd.DataFrame, owners: pd.DataFrame, trans: pd.DataFrame) -> pd.DataFrame:
    """Purchases that count: original Form 4, code P, acquired, price > 0, by a
    director or officer, not flagged as a Rule 10b5-1 plan trade."""
    sub = sub[sub["DOCUMENT_TYPE"].str.strip() == "4"]
    flag = [c for c in sub.columns if "10B5" in c]
    if flag:
        planned = sub[flag[0]].fillna("").str.strip().str.lower().isin({"1", "true", "y", "yes"})
        sub = sub[~planned]
    price = pd.to_numeric(trans["TRANS_PRICEPERSHARE"], errors="coerce")
    trans = trans[
        (trans["TRANS_CODE"].str.strip() == "P")
        & (trans["TRANS_ACQUIRED_DISP_CD"].str.strip() == "A")
        & (price > 0)
    ]
    rel = owners["RPTOWNER_RELATIONSHIP"].fillna("").str.upper()
    owners = owners[rel.str.contains("DIRECTOR") | rel.str.contains("OFFICER")]
    df = (
        trans[["ACCESSION_NUMBER", "TRANS_DATE"]]
        .merge(sub, on="ACCESSION_NUMBER")
        .merge(owners[["ACCESSION_NUMBER", "RPTOWNERCIK"]], on="ACCESSION_NUMBER")
    )
    out = pd.DataFrame(
        {
            "filing_date": _sec_date(df["FILING_DATE"]),
            "trans_date": _sec_date(df["TRANS_DATE"]),
            "issuer_cik": pd.to_numeric(df["ISSUERCIK"], errors="coerce"),
            "symbol": df["ISSUERTRADINGSYMBOL"].fillna("").str.strip().str.upper(),
            "owner_cik": pd.to_numeric(df["RPTOWNERCIK"], errors="coerce"),
        }
    ).dropna(subset=["filing_date", "trans_date", "issuer_cik", "owner_cik"])
    out[["issuer_cik", "owner_cik"]] = out[["issuer_cik", "owner_cik"]].astype("int64")
    return out.drop_duplicates()


def load_purchases(client: SecClient, first_year: int = FIRST_YEAR) -> pd.DataFrame:
    parts = []
    today = market_today()
    for year in range(first_year, today.year + 1):
        for quarter in range(1, 5):
            if dt.date(year, 3 * quarter - 2, 1) > today:
                break
            path = client.cached(
                FORM345_URL.format(year=year, quarter=quarter),
                SEC_DIR / "form345" / f"{year}q{quarter}.zip",
            )
            if path is None:
                print(f"insiders: {year}q{quarter} not published yet")
                continue
            with zipfile.ZipFile(path) as z:
                q = qualifying(
                    _read(z, "SUBMISSION"), _read(z, "REPORTINGOWNER"), _read(z, "NONDERIV_TRANS")
                )
            print(f"insiders: {year}q{quarter}: {len(q):,} qualifying purchases")
            parts.append(q)
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()


def find_clusters(
    purchases: pd.DataFrame, window_days: int = WINDOW_DAYS, cooldown_days: int = COOLDOWN_DAYS
) -> pd.DataFrame:
    """First filing date on which ≥2 distinct insiders' purchase dates fall within
    `window_days` of each other; at most one event per issuer per `cooldown_days`."""
    window = np.timedelta64(window_days, "D")
    events = []
    for cik, g in purchases.sort_values(["filing_date", "trans_date"]).groupby("issuer_cik"):
        filed = g["filing_date"].to_numpy()
        traded = g["trans_date"].to_numpy()
        owner = g["owner_cik"].to_numpy()
        last_event = None
        for fdate in np.unique(filed):
            if last_event is not None and fdate < last_event + np.timedelta64(cooldown_days, "D"):
                continue
            known = filed <= fdate
            best = 0
            for t in traded[filed == fdate]:
                near = known & (np.abs(traded - t) <= window)
                best = max(best, len(set(owner[near])))
            if best >= 2:
                last_event = fdate
                events.append(
                    {
                        "issuer_cik": cik,
                        "reported_symbol": g["symbol"].iloc[-1],
                        "filing_date": pd.Timestamp(fdate),
                        "insiders": best,
                    }
                )
    return pd.DataFrame(events)


def build_trades(events: pd.DataFrame, panel: Panel, rank: pd.DataFrame, beta: pd.DataFrame):
    sessions = panel.sessions
    entry_i = sessions.searchsorted(events["filing_date"].to_numpy(), side="right")
    t = events.assign(entry_i=entry_i, exit_i=entry_i + HOLD - 1)
    t = t[t["exit_i"] < len(sessions)].copy()  # the full hold must be in the data
    t["rank"] = engine.lookup(rank, t["symbol"], t["entry_i"])
    t = t[t["rank"] <= TOP_N].copy()
    t["beta"] = engine.lookup(beta, t["symbol"], t["entry_i"])
    t["beta"] = t["beta"].fillna(1.0)
    t["entry_at"] = "open"
    t["direction"] = 1
    return t.reset_index(drop=True)


def run(panel_dir: Path, out: Path = Path("results/INSIDERS.md")) -> Path:
    client = SecClient()
    purchases = load_purchases(client)
    tickers = ticker_map(client)
    events = find_clusters(purchases)
    events["symbol"] = [
        to_alpaca(tickers[c][0]) if c in tickers else to_alpaca(s)
        for c, s in zip(events["issuer_cik"], events["reported_symbol"], strict=True)
    ]
    panel = Panel.load(panel_dir)
    rank = engine.universe_rank(panel)
    syms = sorted(set(events["symbol"]) & set(panel.close.columns) | {"SPY"})
    beta = engine.rolling_beta(panel.close[syms], panel.close["SPY"])
    trades = build_trades(events, panel, rank, beta)
    results, daily = engine.simulate(trades, panel)
    return write_report(purchases, events, results, daily, panel, out)


def write_report(purchases, events, results, daily, panel: Panel, out: Path) -> Path:
    sessions = panel.sessions
    done = results[results["adj_ret"].notna()].copy()
    if done.empty:
        out.write_text("# Insider cluster purchases\n\nNo tradable events — check the inputs.\n")
        return out
    port = engine.portfolio(daily, sessions)
    span = (int(daily["day_i"].min()), int(daily["day_i"].max()))
    s = engine.summarize(port)
    passed, reason = engine.decide(s, min_sharpe=0.45, monthly_rule=True)
    done["year"] = sessions[done["entry_i"].to_numpy()].year
    done["tercile"] = pd.cut(
        done["rank"], [0, 333, 666, TOP_N], labels=["1–333", "334–666", "667–1000"]
    )
    done["cluster"] = np.where(done["insiders"] >= 3, "3+ insiders", "2 insiders")
    lo, hi = engine.boot_ci(done["adj_ret"].to_numpy())
    text = f"""# Insider cluster purchases (pre-registered study A)

Generated {market_today()} from SEC Form 4 data sets and Alpaca daily bars. Rules fixed
in advance: [PREREGISTRATION.md](../docs/research/PREREGISTRATION.md), section A.

## Verdict: {"**PASS**" if passed else "**FAIL**"}

{reason}.

{"Next step per the pre-registration: paper-trade it in a separate Alpaca paper account, judged on tracking this backtest." if passed else "Per the pre-registration, a failed idea is archived — not re-run with new settings."}

## What was tested

- {len(purchases):,} qualifying director/officer purchases → {len(events):,} cluster events
  ({events["symbol"].isin(panel.close.columns).sum():,} in stocks with Alpaca prices; insider
  buying is mostly a small-cap phenomenon) → {len(done):,} trades in the top-{TOP_N}
  liquidity universe at entry
  ({done["symbol"].nunique():,} stocks, {sessions[span[0]].date()} → {sessions[span[1]].date()}).
- Long at the next open after the filing date, out at the close of the {HOLD}th session;
  every trade hedged with beta × SPY; 5 bp per side on the stock and 1 bp on the hedge.
- Calendar-time portfolio: equal weight across open positions, {s["days"]:,} trading days
  ({s["active_days"]:,} with positions), {s["months"]} months.

## Headline numbers

| measure | value |
|---|---|
| mean monthly return (market-adjusted, net) | {engine.pct(s["mean_monthly"])} |
| 95% range, resampled by month | {engine.pct(s["lo_monthly"])} to {engine.pct(s["hi_monthly"])} |
| annualised IR (daily) | {engine.num(s["sharpe"])} |
| mean per trade ({HOLD} sessions) | {engine.pct(done["adj_ret"].mean())} (95% range {engine.pct(lo)} to {engine.pct(hi)}, trades resampled independently — optimistic) |
| raw stock return per trade, before hedge and costs | {engine.pct(done["stock_ret"].mean())} |

## Descriptive only (cannot rescue a failed primary)

By year (portfolio):

{engine.by_year(port)}

By liquidity tercile at entry:

{engine.breakdown(done, daily, done["tercile"].astype(str), sessions, span, "liquidity rank")}

By cluster size:

{engine.breakdown(done, daily, done["cluster"], sessions, span, "cluster")}

Accepted limitations (stated in advance): the Rule 10b5-1 flag exists only from 2023;
SEC's ticker map lists current companies, so some delisted issuers can't be priced. Alpaca's
price history starts in January 2016 and the screens need 250 sessions of it, so trades start
in 2017.
"""
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    return out
