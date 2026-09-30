"""Parameter tuning with an honest train/test split.

The trap this module is built to expose: grid-search the whole history and the
"best" parameters are usually just the ones that memorized it. So tuning here
optimizes on the FIRST train_frac of sessions only (by expectancy per trade,
never win rate — see v0.1's finding), then re-runs both the tuned and the
default parameters on the held-out remainder. The train→test gap in the report
is the overfitting, made visible.
"""

from __future__ import annotations

import datetime as dt
import json
from itertools import product
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from .backtest import run_on
from .config import Config
from .data import load_bars, load_news, market_today, split_days
from .metrics import summarize
from .report import BASELINE, GRID, INK, INK_2, MUTED, STRATEGIES, SURFACE, _md_table
from .strategies import (
    ArForecast,
    EmaCrossover,
    GapAndGo,
    HighBreakTrail,
    NewsMomentum,
    OpeningRangeBreakout,
    RsiReversion,
    SqueezeBreakout,
    Strategy,
    VwapPullback,
)

MIN_TRAIN_TRADES = 20  # fewer than this and a parameter set is noise, not evidence
# Survivor gate: a tuned set trades live only after it has been the grid's
# winner with identical parameters, AND beaten the defaults on the held-out
# split, in each of the last PROMOTE_RUNS weekly runs. Weekly winners churned
# 2-3 times in 4 runs (to 2026-09-26) and tuned variants lost more live than
# the defaults — promoting every Saturday's winner was trading noise.
PROMOTE_RUNS = 3


def _grid(**options: list[Any]) -> list[dict[str, Any]]:
    keys = list(options)
    return [dict(zip(keys, combo, strict=True)) for combo in product(*options.values())]


# Search spaces: stop placement, targets, and entry thresholds per strategy.
GRIDS: dict[str, tuple[type[Strategy], list[dict[str, Any]]]] = {
    "gap_and_go": (GapAndGo, _grid(min_gap_pct=[1.0, 2.0, 3.0], target_r=[1.5, 2.0, 3.0])),
    "orb": (
        OpeningRangeBreakout,
        _grid(range_bars=[3, 6], target_r=[1.5, 2.0, 3.0], stop_at_mid=[False, True]),
    ),
    "vwap_pullback": (
        VwapPullback,
        _grid(target_r=[1.5, 2.0, 3.0], stop_buffer=[0.997, 0.995, 0.99]),
    ),
    "ema_crossover": (
        EmaCrossover,
        _grid(fast=[5, 9, 12], slow=[13, 20, 26], stop_bars=[5, 10]),
    ),
    "rsi2_reversion": (
        RsiReversion,
        _grid(
            entry_level=[5.0, 10.0, 15.0],
            exit_level=[50.0, 60.0, 70.0],
            stop_pct=[0.005, 0.01, 0.02],
        ),
    ),
    "news_momentum": (
        NewsMomentum,
        _grid(window_min=[30, 60], vol_mult=[1.2, 1.5, 2.0], target_r=[1.5, 2.0, 3.0]),
    ),
    "squeeze_breakout": (
        SqueezeBreakout,
        _grid(bw_lookback=[6, 12], target_r=[1.5, 2.0, 3.0]),
    ),
    "high_break_trail": (
        HighBreakTrail,
        _grid(window_bars=[6, 12], trail_atr_mult=[1.5, 2.0, 3.0]),
    ),
    "ar_forecast": (
        ArForecast,
        # 12 sets, not 18: the middle threshold never separated from its
        # neighbours and the grid is the tune's runtime hotspot.
        _grid(lags=[6, 12], horizon=[3, 6, 12], threshold=[0.001, 0.002]),
    ),
}


def _factory(cls: type[Strategy], params: dict[str, Any] | None = None):
    """Bind cls/params now (not at call time) so loop variables can't leak in."""
    fixed = dict(params or {})
    return lambda: [cls(**fixed)]


def _expectancy(trades: pd.DataFrame) -> float:
    return float(trades["pnl"].mean()) if len(trades) else 0.0


def _stats(trades: pd.DataFrame) -> dict[str, Any]:
    if trades.empty:
        return {"trades": 0, "win_rate": 0.0, "profit_factor": 0.0, "expectancy": 0.0, "pnl": 0.0}
    row = summarize(trades).iloc[0]
    return {
        "trades": int(row["trades"]),
        "win_rate": float(row["win_rate_pct"]),
        "profit_factor": float(row["profit_factor"]),
        "expectancy": float(row["expectancy"]),
        "pnl": float(row["total_pnl"]),
    }


def tune(cfg: Config, train_frac: float = 0.6, out_dir: Path = Path("results")) -> Path:
    bars = load_bars(cfg.symbols, cfg.interval, cfg.period)
    news = load_news(cfg.symbols, cfg.interval, cfg.period)
    all_dates: list[dt.date] = sorted(
        {date for sym_bars in bars.values() for date, _, _ in split_days(sym_bars)}
    )
    cut = all_dates[int(len(all_dates) * train_frac)]
    train = {d for d in all_dates if d < cut}
    test = {d for d in all_dates if d >= cut}
    print(
        f"{len(train)} train sessions ({all_dates[0]} → {max(train)}), "
        f"{len(test)} test sessions ({cut} → {all_dates[-1]})\n"
    )

    rows = []
    tuned_out: dict[str, dict] = {}
    for name, (cls, grid) in GRIDS.items():
        label = STRATEGIES[name][0]
        # news_momentum needs the headline index injected alongside its params
        extra = {"news_index": news} if name == "news_momentum" else {}
        best_params: dict[str, Any] | None = None
        best_trades: pd.DataFrame | None = None
        best_score = float("-inf")
        skipped = 0
        for params in grid:
            trades = run_on(bars, _factory(cls, {**params, **extra}), cfg, train)
            if len(trades) < MIN_TRAIN_TRADES:
                skipped += 1
                continue
            score = _expectancy(trades)
            if score > best_score:
                best_score, best_params, best_trades = score, params, trades
        if best_params is None:
            print(
                f"{label}: no parameter set produced ≥{MIN_TRAIN_TRADES} train trades — not tunable on this data."
            )
            rows.append(
                {
                    "strategy": label,
                    "params": "n/a (too few trades)",
                    "train": None,
                    "test": None,
                    "default_test": _stats(run_on(bars, _factory(cls, extra), cfg, test)),
                }
            )
            continue

        train_stats = _stats(best_trades)  # the grid loop already ran this exact set
        test_stats = _stats(run_on(bars, _factory(cls, {**best_params, **extra}), cfg, test))
        default_test = _stats(run_on(bars, _factory(cls, extra), cfg, test))
        tuned_out[name] = {
            "params": best_params,
            "train_expectancy": round(train_stats["expectancy"], 2),
            "test_expectancy": round(test_stats["expectancy"], 2),
        }
        rows.append(
            {
                "strategy": label,
                "params": best_params,
                "train": train_stats,
                "test": test_stats,
                "default_test": default_test,
            }
        )
        print(
            f"{label}: best {best_params} "
            f"(searched {len(grid) - skipped}/{len(grid)} sets) — "
            f"train ${train_stats['expectancy']:+.2f}/trade → test ${test_stats['expectancy']:+.2f}/trade"
        )

    _append_history(rows, out_dir)
    promoted, held = promote(tuned_out, out_dir / "tuning_history.csv")
    for name in promoted:
        print(f"promoted → trades live as {name}_tuned")
    for name, why in held.items():
        print(f"held back {name}: {why}")
    _write_tuned_params(promoted, out_dir, held)
    return _write_report(rows, cfg, cut, len(train), len(test), out_dir, promoted, held)


def promote(
    tuned: dict[str, dict], history_path: Path, runs: int = PROMOTE_RUNS
) -> tuple[dict[str, dict], dict[str, str]]:
    """Split this run's tuned sets into (promoted, held-with-reason) by the
    survivor gate. Consecutive runs share most of their 60-day window, so
    passing is persistence, not independent confirmation — the live A/B is
    still the real test."""
    hist = pd.read_csv(history_path) if history_path.exists() else pd.DataFrame()
    promoted: dict[str, dict] = {}
    held: dict[str, str] = {}
    for name, entry in tuned.items():
        label = STRATEGIES[name][0]
        recent = (
            hist[hist["strategy"] == label].sort_values("run_date").tail(runs)
            if not hist.empty
            else hist
        )
        if len(recent) < runs:
            held[name] = f"only {len(recent)} of {runs} weekly runs so far"
        elif recent["best_params"].nunique() != 1:
            held[name] = f"best parameters changed within the last {runs} runs"
        elif not (recent["test_expectancy"] > recent["default_test_expectancy"]).all():
            held[name] = f"did not beat the defaults on held-out data in all {runs} runs"
        else:
            promoted[name] = entry
    return promoted, held


def _write_tuned_params(
    tuned: dict[str, dict], out_dir: Path, held: dict[str, str] | None = None
) -> None:
    """results/tuned_params.json — the paper scanner trades each entry under
    "strategies" as a `<name>_tuned` variant ALONGSIDE the defaults. Only
    survivor-gate passes land there; "held" records why the rest didn't."""
    payload = {
        "generated": market_today().isoformat(),
        "promotion_rule": f"identical winning params + beat defaults held-out, last {PROMOTE_RUNS} runs",
        "strategies": tuned,
        "held": held or {},
    }
    (out_dir / "tuned_params.json").write_text(json.dumps(payload, indent=2) + "\n")


def _append_history(rows, out_dir: Path) -> None:
    """One row per strategy per run in tuning_history.csv — TUNING.md is
    overwritten weekly, so this is where week-over-week parameter stability
    (or churn — a result in itself) becomes visible. Re-runs on the same
    date replace that date's rows, so a retried workflow stays clean."""
    hist_path = out_dir / "tuning_history.csv"
    today = market_today().isoformat()
    fresh = pd.DataFrame(
        [
            {
                "run_date": today,
                "strategy": r["strategy"],
                "best_params": str(r["params"]),
                "train_expectancy": r["train"]["expectancy"] if r["train"] else None,
                "test_expectancy": r["test"]["expectancy"] if r["test"] else None,
                "default_test_expectancy": r["default_test"]["expectancy"],
                "test_trades": r["test"]["trades"] if r["test"] else r["default_test"]["trades"],
            }
            for r in rows
        ]
    )
    if hist_path.exists():
        old = pd.read_csv(hist_path)
        fresh = pd.concat([old[old["run_date"] != today], fresh], ignore_index=True)
    fresh.to_csv(hist_path, index=False)


def _write_report(
    rows,
    cfg: Config,
    cut: dt.date,
    n_train: int,
    n_test: int,
    out_dir: Path,
    promoted: dict[str, dict] | None = None,
    held: dict[str, str] | None = None,
) -> Path:
    out_dir.mkdir(exist_ok=True)
    _shrinkage_chart(rows, out_dir / "tuning_shrinkage.png")

    table = pd.DataFrame(
        [
            {
                "strategy": r["strategy"],
                "best params (train)": str(r["params"]),
                "train exp./trade": f"${r['train']['expectancy']:+.2f}" if r["train"] else "—",
                "test exp./trade": f"${r['test']['expectancy']:+.2f}" if r["test"] else "—",
                "test exp. (defaults)": f"${r['default_test']['expectancy']:+.2f}",
                "test trades": r["test"]["trades"] if r["test"] else r["default_test"]["trades"],
                "test win rate": f"{r['test']['win_rate']:.1f}%" if r["test"] else "—",
                "test P&L": f"${r['test']['pnl']:+,.0f}" if r["test"] else "—",
            }
            for r in rows
        ]
    )

    gate_rows = [
        {"strategy": STRATEGIES[k][0], "live": "✓ trades as `_tuned`", "why": "passed"}
        for k in (promoted or {})
    ] + [
        {"strategy": STRATEGIES[k][0], "live": "held back", "why": why}
        for k, why in (held or {}).items()
    ]
    gate_md = (
        _md_table(pd.DataFrame(gate_rows)) if gate_rows else "_No tunable strategies this run._"
    )

    body = f"""# Parameter tuning — train/test split

Generated {market_today().isoformat()} · optimized on the first **{n_train} sessions**
(before {cut}), validated on the held-out **{n_test} sessions** · objective:
**expectancy per trade** (never win rate — see v0.1) · parameter sets with fewer
than {MIN_TRAIN_TRADES} train trades are discarded as noise.

{_md_table(table)}

![Train vs test expectancy](tuning_shrinkage.png)

## How to read this

- **train → test shrinkage is the overfitting, made visible.** Parameters that
  look best in-sample routinely give most of it back out-of-sample; the gap
  between the two columns is the honest measure of how much the grid search
  just memorized.
- **"test exp. (defaults)"** is the untuned textbook strategy on the same
  held-out sessions — the bar tuning has to beat to claim any value.
- With ~{n_test} test sessions this is still a small sample; treat survivors as
  candidates for paper trading, not conclusions.

## Live promotion (survivor gate)

A tuned set trades live as `<strategy>_tuned` only once it has been the grid's
winner with **identical parameters** and has **beaten the defaults on the held-out
split** in each of the last {PROMOTE_RUNS} weekly runs. Everything else keeps
trading on defaults only.

{gate_md}

Consecutive runs share most of their 60-day window, so passing shows the result
*persists*, not that it's independently confirmed — the live `_tuned` vs default
comparison in the paper journal is the real test.
"""
    path = out_dir / "TUNING.md"
    path.write_text(body)
    return path


def _shrinkage_chart(rows, path: Path) -> None:
    tuned = [r for r in rows if r["train"] is not None]
    labels = [r["strategy"] for r in tuned]
    train_vals = [r["train"]["expectancy"] for r in tuned]
    test_vals = [r["test"]["expectancy"] for r in tuned]

    x = range(len(tuned))
    width = 0.38
    fig, ax = plt.subplots(figsize=(10, 4.8), dpi=100)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    bars1 = ax.bar(
        [i - width / 2 for i in x],
        train_vals,
        width,
        label="Train (optimized on)",
        color="#2a78d6",
        zorder=3,
    )
    bars2 = ax.bar(
        [i + width / 2 for i in x],
        test_vals,
        width,
        label="Test (held out)",
        color="#eb6834",
        zorder=3,
    )
    for bars in (bars1, bars2):
        for b in bars:
            v = b.get_height()
            ax.annotate(
                f"{v:+.1f}",
                (b.get_x() + b.get_width() / 2, v),
                textcoords="offset points",
                xytext=(0, 4 if v >= 0 else -12),
                ha="center",
                fontsize=8,
                color=INK_2,
            )
    ax.axhline(0, color=BASELINE, linewidth=1, zorder=2)
    ax.set_title(
        "Tuned expectancy per trade: train vs held-out test",
        loc="left",
        fontsize=13,
        fontweight="bold",
        color=INK,
        pad=30,
    )
    ax.set_ylabel("$ per trade", color=INK_2, fontsize=10)
    ax.set_xticks(list(x), labels, fontsize=9)
    ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(BASELINE)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.legend(
        frameon=False,
        fontsize=9,
        labelcolor=INK_2,
        loc="lower left",
        bbox_to_anchor=(0, 1.0),
        ncols=2,
    )
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)
