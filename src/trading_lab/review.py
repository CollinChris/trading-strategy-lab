"""results/REVIEW.md — is anything beating the market? Refreshed nightly.

Every number here is judged SPY-adjusted (see market.py): raw P&L in this lab
mostly measured which way the market drifted intraday. The decision gate at
the bottom is the lab's stopping rule, written down before the data arrives.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import numpy as np
import pandas as pd

from .data import market_today
from .report import _md_table

DECISION_DATE = dt.date(2026, 12, 21)
ADJUSTED_SINCE = dt.date(2026, 10, 21)  # SPY adjustment + 10-symbol universe went live
MIN_TRADES = 100  # a strategy needs this many SPY-adjusted paper trades to be judged


def _boot(values: np.ndarray, seed: int, n: int = 4000) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    means = rng.choice(values, (n, len(values))).mean(axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def verdict(adj: pd.Series, seed: int = 0) -> dict:
    v = adj.dropna().to_numpy(dtype=float)
    out = {
        "trades": len(v),
        "adj_exp": float(v.mean()) if len(v) else float("nan"),
        "lo": float("nan"),
        "hi": float("nan"),
        "verdict": "no trades",
    }
    if len(v) < 2:
        return out
    out["lo"], out["hi"] = _boot(v, seed)
    if len(v) < 30:
        out["verdict"] = "too few trades"
    elif out["lo"] > 0:
        out["verdict"] = (
            "**beats the market**" if len(v) >= MIN_TRADES else "promising (needs more trades)"
        )
    elif out["hi"] < 0:
        out["verdict"] = "loses beyond the market"
    else:
        out["verdict"] = "no evidence of edge"
    return out


def _money(x: float) -> str:
    return "—" if pd.isna(x) else f"${x:+,.2f}"


def _table(frame: pd.DataFrame, by: str, seed0: int) -> pd.DataFrame:
    rows = []
    for k, (key, g) in enumerate(sorted(frame.groupby(by), key=lambda kv: -len(kv[1]))):
        v = verdict(g["pnl_vs_spy"], seed=seed0 + k)
        rows.append(
            {
                by: key,
                "trades": len(g),
                "raw $/trade": _money(g["pnl"].mean()),
                "SPY-adjusted $/trade": _money(v["adj_exp"]),
                "95% range": "—" if pd.isna(v["lo"]) else f"{_money(v['lo'])} to {_money(v['hi'])}",
                "verdict": v["verdict"],
            }
        )
    return pd.DataFrame(rows)


def _base(strategy: pd.Series) -> pd.Series:
    return strategy.str.replace(r"_(tuned|regime)$", "", regex=True)


def build(journal_path: Path, trades_path: Path, out: Path) -> Path:
    j = pd.read_csv(journal_path)
    j = j[j["exit_price"].notna()].copy()
    if "pnl_vs_spy" not in j:
        j["pnl_vs_spy"] = np.nan
    j["date"] = pd.to_datetime(j["date"]).dt.date
    j["strategy_base"] = _base(j["strategy"])
    adjusted = j["pnl_vs_spy"].notna()

    sections = []
    strat = _table(j[adjusted], "strategy_base", 0)
    sections.append(("Paper trading, by strategy (variants pooled)", strat))
    sections.append(("Paper trading, by side", _table(j[adjusted], "side", 100)))
    sections.append(("Paper trading, by symbol", _table(j[adjusted], "symbol", 200)))

    orb = j[adjusted & (j["strategy_base"] == "orb")]
    neutral = [{"book": "ORB, paper", **{k: v for k, v in verdict(orb["pnl_vs_spy"], 300).items()}}]
    bt_note = ""
    if trades_path.exists():
        bt = pd.read_csv(trades_path)
        if "pnl_vs_spy" in bt and bt["pnl_vs_spy"].notna().any():
            sections.append(
                (
                    "Backtest (60-day window), by strategy",
                    _table(bt[bt["pnl_vs_spy"].notna()], "strategy", 400),
                )
            )
            neutral.append(
                {
                    "book": "ORB, backtest",
                    **verdict(bt.loc[bt["strategy"] == "orb", "pnl_vs_spy"], 301),
                }
            )
        else:
            bt_note = "\n_The backtest has no SPY-adjusted columns yet; it gains them on the next weekly refresh._\n"
    neutral_df = pd.DataFrame(
        [
            {
                "book": n["book"],
                "trades": n["trades"],
                "SPY-adjusted $/trade": _money(n["adj_exp"]),
                "95% range": "—" if pd.isna(n["lo"]) else f"{_money(n['lo'])} to {_money(n['hi'])}",
                "verdict": n["verdict"],
            }
            for n in neutral
        ]
    )

    # Decision gate: judged on the strategies' SPY-adjusted paper record.
    winners = [
        r["strategy_base"] for _, r in strat.iterrows() if r["verdict"] == "**beats the market**"
    ]
    today = market_today()
    days_left = (DECISION_DATE - today).days
    if winners:
        gate = f"**Continue — {', '.join(winners)} beat the market** with at least {MIN_TRADES} trades and a 95% range above zero."
    elif days_left > 0:
        gate = f"**Undecided — {days_left} days to the decision date.** No strategy beats the market yet."
    else:
        gate = (
            "**Decision date reached with no strategy beating the market.** Conclude the "
            "day-trading study: these rules don't beat costs on these names once the market's "
            "own move is removed."
        )

    body = [
        "# Lab review — is anything beating the market?",
        "",
        f"Generated {today.isoformat()} · {len(j)} settled paper trades over "
        f"{j['date'].nunique()} sessions ({j['date'].min()} → {j['date'].max()}) · "
        f"{adjusted.sum()} SPY-adjusted.",
        "",
        "**SPY-adjusted** = the trade's P&L plus an opposite, beta-weighted SPY position held "
        "for the same minutes, minus that hedge's slippage. It removes the market's intraday "
        "drift, which raw P&L can't tell apart from skill (in Sep–Oct 2026 SPY fell intraday "
        "on 27 of 43 days, so shorts looked profitable and longs looked broken).",
        "",
        "## Decision gate",
        "",
        gate,
        "",
        f"Rule, set {ADJUSTED_SINCE}: by **{DECISION_DATE}**, a strategy that has at least "
        f"{MIN_TRADES} SPY-adjusted paper trades and a 95% range entirely above zero keeps "
        "running. If none does, the study concludes.",
        "",
    ]
    for title, df in sections:
        body += [f"## {title}", "", _md_table(df), ""]
    body += [
        "## Market-neutral ORB",
        "",
        "ORB was the lab's best raw performer. Hedged against SPY, does anything remain?",
        "",
        _md_table(neutral_df),
        bt_note,
        "## How to read this",
        "",
        "- The 95% range is a bootstrap interval of the SPY-adjusted mean. A range that "
        "crosses zero means the data can't distinguish the strategy from luck.",
        "- Variants (`_tuned`, `_regime`) are pooled into their base strategy; both were "
        "switched off on 2026-10-21 after losing more than the defaults.",
        f"- The traded universe widened from 6 high-beta tech/crypto names to 10 across "
        f"sectors on {ADJUSTED_SINCE}; the by-symbol table shows whether that helps.",
        "",
    ]
    out.write_text("\n".join(body))
    return out
