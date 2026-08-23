"""Per-strategy performance metrics from a trades table."""

from __future__ import annotations

import numpy as np
import pandas as pd


def summarize(trades: pd.DataFrame) -> pd.DataFrame:
    """One row per strategy: win rate, profit factor, expectancy, drawdown."""
    rows = []
    for name, group in trades.groupby("strategy"):
        group = group.sort_values("exit_time")
        pnl = group["pnl"]
        wins = pnl[pnl > 0]
        losses = pnl[pnl <= 0]
        equity = pnl.cumsum()
        drawdown = equity - equity.cummax()
        rows.append(
            {
                "strategy": name,
                "trades": len(group),
                "win_rate_pct": round(100.0 * len(wins) / len(group), 1),
                "avg_win": round(float(wins.mean()) if len(wins) else 0.0, 2),
                "avg_loss": round(float(losses.mean()) if len(losses) else 0.0, 2),
                "profit_factor": round(
                    float(wins.sum() / abs(losses.sum())) if losses.sum() != 0 else np.inf, 2
                ),
                "expectancy": round(float(pnl.mean()), 2),
                "total_pnl": round(float(pnl.sum()), 2),
                "max_drawdown": round(float(drawdown.min()), 2),
                "median_hold_min": round(float(group["hold_minutes"].median()), 0),
            }
        )
    return pd.DataFrame(rows).sort_values("win_rate_pct", ascending=False).reset_index(drop=True)
