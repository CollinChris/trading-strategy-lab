"""Ten-year study: every strategy over Alpaca's 5-minute history (2016+),
judged SPY-adjusted, with walk-forward tuning — results/HISTORY.md.

The weekly backtest only ever sees yfinance's 60 days, so every verdict there
rests on one stretch of market. Here each strategy runs across many regimes,
and tuning is honest about time: parameters for year Y are picked on years
Y-2..Y-1 only, then scored on Y against the untuned defaults.
"""

from __future__ import annotations

import datetime as dt
import json
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd

from .backtest import run_on
from .config import Config
from .data import load_history, market_today, split_days
from .report import STRATEGIES, _md_table
from .tune import GRIDS, _factory

HISTORY_DIR = Path("data/history")
TRAIN_YEARS = 2
MIN_TRAIN_TRADES = 50
# No 10 years of news to replay: Alpaca's news API pages out long before that.
EXCLUDED = {"news_momentum": "needs a 10-year headline archive the lab doesn't have"}
# Defaults only (no walk-forward tuning) unless --full-grid: the AR model refits
# on every bar, so its 12-set grid alone was ~40% of a 2-hour run.
DEFAULTS_ONLY = {"ar_forecast"}


def _job(
    strategy: str, params: dict | None, symbol: str, start: dt.date, end: dt.date
) -> pd.DataFrame:
    """One (strategy, parameter set, symbol) run over the whole window.
    Runs in a worker process; bars come from the on-disk cache."""
    bars = load_history([symbol, "SPY"], start, end)
    if symbol not in bars or "SPY" not in bars:
        return pd.DataFrame()
    spy_by_date = {d: day for d, day, _ in split_days(bars["SPY"])}
    cls = GRIDS[strategy][0]
    trades = run_on(
        {symbol: bars[symbol]},
        _factory(cls, params or {}),
        Config(symbols=[symbol]),
        spy_by_date=spy_by_date,
    )
    if trades.empty:
        return trades
    trades["params"] = "default" if params is None else json.dumps(params, sort_keys=True)
    return trades[["strategy", "params", "symbol", "date", "side", "pnl", "pnl_vs_spy"]]


def run(
    start: dt.date,
    end: dt.date,
    symbols: list[str],
    workers: int = 7,
    out: Path = Path("results/HISTORY.md"),
    full_grid: bool = False,
) -> Path:
    print(f"loading {len(symbols)} symbols + SPY, {start} → {end} (cached after the first run)")
    load_history([*symbols, "SPY"], start, end)  # fill the cache once, in this process
    jobs = []
    for name, (_cls, grid) in GRIDS.items():
        if name in EXCLUDED:
            continue
        sets = [None] if (name in DEFAULTS_ONLY and not full_grid) else [None, *grid]
        for params in sets:
            for sym in symbols:
                jobs.append((name, params, sym))
    print(f"{len(jobs)} runs on {workers} workers…", flush=True)
    frames, done = [], 0
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futs = [pool.submit(_job, n, p, s, start, end) for n, p, s in jobs]
        for fut in as_completed(futs):
            frames.append(fut.result())
            done += 1
            if done % 50 == 0 or done == len(jobs):
                print(f"  {done}/{len(jobs)} runs done", flush=True)
    trades = pd.concat([f for f in frames if not f.empty], ignore_index=True)
    trades["date"] = pd.to_datetime(trades["date"])
    trades["year"] = trades["date"].dt.year
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    trades.to_pickle(HISTORY_DIR / "trades.pkl")
    out.write_text(render(trades, start, end, symbols, full_grid))
    return out


def day_clustered_ci(
    t: pd.DataFrame, col: str = "pnl_vs_spy", seed: int = 0, n: int = 2000
) -> tuple[float, float]:
    """95% range of the per-trade mean, resampling whole trading days: trades
    on the same day share the same market and aren't independent."""
    g = t.dropna(subset=[col]).groupby("date")[col].agg(["sum", "count"])
    if len(g) < 20:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(g), (n, len(g)))
    s, c = g["sum"].to_numpy()[idx].sum(axis=1), g["count"].to_numpy()[idx].sum(axis=1)
    means = s / c
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def _money(x: float) -> str:
    return "—" if pd.isna(x) else f"${x:+,.2f}"


def _verdict(lo: float, hi: float) -> str:
    if pd.isna(lo):
        return "too few days"
    if lo > 0:
        return "**beats the market**"
    if hi < 0:
        return "loses beyond the market"
    return "no evidence of edge"


def walk_forward(trades: pd.DataFrame) -> pd.DataFrame:
    """Per strategy and test year: pick the parameter set with the best
    SPY-adjusted expectancy over the previous TRAIN_YEARS years (all symbols
    pooled, >= MIN_TRAIN_TRADES trades), then score it on the test year."""
    agg = (
        trades.groupby(["strategy", "params", "year"])["pnl_vs_spy"]
        .agg(["sum", "count"])
        .reset_index()
    )
    years = sorted(agg["year"].unique())
    rows = []
    for strat, g in agg.groupby("strategy"):
        for y in years[TRAIN_YEARS:]:
            train = (
                g[g["year"].between(y - TRAIN_YEARS, y - 1)]
                .groupby("params")[["sum", "count"]]
                .sum()
            )
            train = train[train["count"] >= MIN_TRAIN_TRADES]
            test = g[g["year"] == y].set_index("params")
            if train.empty or "default" not in test.index:
                continue
            pick = (train["sum"] / train["count"]).idxmax()
            if pick not in test.index:
                continue
            rows.append(
                {
                    "strategy": strat,
                    "year": y,
                    "picked": pick,
                    "tuned_sum": test.loc[pick, "sum"],
                    "tuned_n": test.loc[pick, "count"],
                    "default_sum": test.loc["default", "sum"],
                    "default_n": test.loc["default", "count"],
                }
            )
    return pd.DataFrame(rows)


def render(
    trades: pd.DataFrame, start: dt.date, end: dt.date, symbols: list[str], full_grid: bool = False
) -> str:
    d = trades[trades["params"] == "default"]
    years = sorted(d["year"].unique())

    rows = []
    for k, (strat, g) in enumerate(sorted(d.groupby("strategy"), key=lambda kv: -len(kv[1]))):
        lo, hi = day_clustered_ci(g, seed=k)
        rows.append(
            {
                "strategy": STRATEGIES.get(strat, (strat,))[0],
                "trades": len(g),
                "trading days": g["date"].nunique(),
                "raw $/trade": _money(g["pnl"].mean()),
                "SPY-adjusted $/trade": _money(g["pnl_vs_spy"].mean()),
                "95% range (day-resampled)": f"{_money(lo)} to {_money(hi)}",
                "verdict": _verdict(lo, hi),
            }
        )
    overall = pd.DataFrame(rows)

    yearly = d.pivot_table(index="strategy", columns="year", values="pnl_vs_spy", aggfunc="mean")
    yearly.index = [STRATEGIES.get(s, (s,))[0] for s in yearly.index]
    yearly_md = yearly.map(lambda v: "—" if pd.isna(v) else f"{v:+.1f}").reset_index(
        names="strategy"
    )
    pos_years = (yearly > 0).sum(axis=1)

    side_rows = []
    for k, ((strat, side), g) in enumerate(d.groupby(["strategy", "side"])):
        lo, hi = day_clustered_ci(g, seed=100 + k)
        side_rows.append(
            {
                "strategy": STRATEGIES.get(strat, (strat,))[0],
                "side": side,
                "trades": len(g),
                "SPY-adjusted $/trade": _money(g["pnl_vs_spy"].mean()),
                "95% range": f"{_money(lo)} to {_money(hi)}",
                "verdict": _verdict(lo, hi),
            }
        )

    wf = walk_forward(trades)
    wf_rows = []
    for strat, g in wf.groupby("strategy"):
        tuned = g["tuned_sum"].sum() / g["tuned_n"].sum()
        default = g["default_sum"].sum() / g["default_n"].sum()
        beat = (g["tuned_sum"] / g["tuned_n"] > g["default_sum"] / g["default_n"]).sum()
        wf_rows.append(
            {
                "strategy": STRATEGIES.get(strat, (strat,))[0],
                "test years": len(g),
                "tuned, out of sample": _money(tuned),
                "defaults, same years": _money(default),
                "years tuned beat defaults": f"{beat}/{len(g)}",
                "distinct parameter picks": g["picked"].nunique(),
            }
        )
    wf_md = (
        _md_table(pd.DataFrame(wf_rows))
        if wf_rows
        else "_Not enough years for walk-forward tuning._"
    )

    winners = [r["strategy"] for r in rows if r["verdict"] == "**beats the market**"]
    if winners:
        headline = (
            f"**{', '.join(winners)} beat the market over {len(years)} years** (SPY-adjusted, day-resampled "
            "95% range above zero). Worth a closer, out-of-sample look before trusting it."
        )
    else:
        headline = (
            f"**No strategy beats the market over {len(years)} years.** Once SPY's intraday move is "
            "removed, none of these rules has an edge after costs on these symbols."
        )
    excluded = "\n".join(f"- {STRATEGIES[k][0]}: excluded — {v}." for k, v in EXCLUDED.items())
    if not full_grid:
        excluded += "".join(
            f"\n- {STRATEGIES[k][0]}: defaults only, no walk-forward tuning (compute; `--full-grid` adds it)."
            for k in DEFAULTS_ONLY
        )

    return f"""# Ten-year history — does anything beat the market?

Generated {market_today().isoformat()} · **{start} → {end}** · {len(symbols)} symbols
({", ".join(symbols)}) · Alpaca 5-minute bars, consolidated feed, split/dividend-adjusted ·
{len(d):,} default-parameter trades over {d["date"].nunique():,} trading days. Same engine,
costs and SPY adjustment as the live lab (`results/REVIEW.md`).

{headline}

## Every strategy at its default parameters

{_md_table(overall)}

The 95% range resamples **whole trading days**, not individual trades — trades on the same day
share one market, so per-trade resampling would overstate the precision.

## Year by year (SPY-adjusted $/trade, default parameters)

{_md_table(yearly_md)}

Years with a positive SPY-adjusted mean, per strategy: {", ".join(f"{s} {n}/{len(years)}" for s, n in pos_years.items())}.
A strategy that works only in some kinds of market shows up here as a run of positive years.

## Long and short separately

{_md_table(pd.DataFrame(side_rows))}

## Walk-forward tuning — does picking parameters on the past help the future?

Each year, every parameter set in the tuning grid is scored on the previous {TRAIN_YEARS} years
(SPY-adjusted, at least {MIN_TRAIN_TRADES} trades), the best one is kept, and it is then scored on
the year itself — which it has never seen — next to the untuned defaults.

{wf_md}

"Distinct parameter picks" counts how often the winner changed. A tuned set that keeps changing
and doesn't beat the defaults is fitting noise.

## Notes

{excluded}
- The ten symbols were chosen in 2026 — survivors with hindsight. Losses here are, if anything,
  understated; apparent edges deserve suspicion.
- COIN listed in April 2021; its history starts there.
- Raw per-trade results: `data/history/trades.pkl` (gitignored, regenerable).
"""
