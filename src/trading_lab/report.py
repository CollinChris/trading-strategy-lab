"""Results artifacts: RESULTS.md, trades.csv, and the equity-curve chart."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from .config import Config
from .data import market_today

# Display names in registry order; colors are the reference categorical palette
# (light mode) assigned in this fixed order — color follows the strategy, not its rank.
STRATEGIES = {
    "gap_and_go": ("Gap & Go", "#2a78d6"),
    "orb": ("Opening Range Breakout", "#eb6834"),
    "vwap_pullback": ("VWAP Pullback", "#1baf7a"),
    "ema_crossover": ("EMA 9/20 Crossover", "#eda100"),
    "rsi2_reversion": ("RSI(2) Reversion", "#e87ba4"),
    "news_momentum": ("News Momentum", "#008300"),
    "squeeze_breakout": ("Squeeze Breakout", "#4a3aa7"),
    "high_break_trail": ("High-Break ATR Trail", "#e34948"),
}

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"


def equity_chart(trades: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 6.2), dpi=100)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    for key, (label, color) in STRATEGIES.items():
        group = trades[trades["strategy"] == key].sort_values("exit_time")
        if group.empty:
            continue
        ax.step(
            group["exit_time"],
            group["pnl"].cumsum(),
            where="post",
            color=color,
            linewidth=2,
            label=label,
            solid_capstyle="round",
        )

    ax.axhline(0, color=BASELINE, linewidth=1)
    ax.set_title(
        "Cumulative P&L by strategy", loc="left", fontsize=14, fontweight="bold", color=INK, pad=72
    )
    ax.set_ylabel("P&L per $10k trade size (USD)", color=INK_2, fontsize=10)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(BASELINE)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    # Legend in its own band above the axes so it never covers data.
    ax.legend(
        frameon=False,
        fontsize=9,
        labelcolor=INK_2,
        loc="lower left",
        bbox_to_anchor=(0, 1.0),
        ncols=3,
        columnspacing=1.4,
        handlelength=1.6,
    )
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)


def _md_table(frame: pd.DataFrame) -> str:
    header = "| " + " | ".join(frame.columns) + " |"
    divider = "|" + "|".join(["---"] * len(frame.columns)) + "|"
    rows = ["| " + " | ".join(str(v) for v in row) + " |" for row in frame.itertuples(index=False)]
    return "\n".join([header, divider, *rows])


def write_report(
    trades: pd.DataFrame, summary: pd.DataFrame, cfg: Config, out_dir: Path = Path("results")
) -> Path:
    out_dir.mkdir(exist_ok=True)
    trades.to_csv(out_dir / "trades.csv", index=False)
    equity_chart(trades, out_dir / "equity_curves.png")

    pretty = summary.copy()
    pretty["strategy"] = pretty["strategy"].map(lambda k: STRATEGIES[k][0])

    exits = trades.groupby(["strategy", "exit_reason"]).size().unstack(fill_value=0)
    exits = (exits.T / exits.sum(axis=1) * 100).T.round(1)
    exits.index = [STRATEGIES[k][0] for k in exits.index]
    exits = exits.reset_index(names="strategy")

    start, end = trades["date"].min(), trades["date"].max()
    body = f"""# Backtest results

Generated {market_today().isoformat()} · window **{start} → {end}** ·
symbols **{", ".join(cfg.symbols)}** · bars **{cfg.interval}** ·
**${cfg.notional_per_trade:,.0f}** per trade · slippage **{cfg.slippage_bps:.0f} bps/side** ·
long-only, everything flat by {cfg.eod_cutoff} ET.

## Ranking (by win rate)

{_md_table(pretty)}

Win rate alone doesn't pay — a high-win-rate strategy with avg losses larger than
avg wins can still lose money. Read it together with **profit_factor** (gross
wins / gross losses, >1 is profitable) and **expectancy** (avg $ per trade).

![Cumulative P&L by strategy](equity_curves.png)

## How each strategy's trades ended (% of trades)

{_md_table(exits)}

`stop` = protective stop hit · `target` = fixed take-profit hit ·
`signal` = strategy's own exit rule · `eod` = flattened at the session cutoff.

Full trade-by-trade log: [trades.csv](trades.csv).

*Small sample (yfinance caps 5-minute history at 60 days), one market regime,
liquid large caps rather than true low-float gappers — see the README's
limitations section before reading anything into these numbers.*
"""
    path = out_dir / "RESULTS.md"
    path.write_text(body)
    return path
