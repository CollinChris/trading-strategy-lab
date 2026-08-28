"""Event-driven backtest engine.

Execution model (chosen to avoid lookahead bias):
- Signals are evaluated on COMPLETED bars and fill at the NEXT bar's open.
- Stops and fixed targets are monitored intra-bar against the bar's low/high.
  If a bar's range covers both the stop and the target, the STOP is assumed to
  have been hit first (conservative).
- A position opened at a bar's open can be stopped out within that same bar.
- Everything is flattened at the session's cutoff bar — these are day-trading
  strategies; nothing is held overnight.
- Slippage is charged on every fill, both sides.
"""

from __future__ import annotations

import datetime as dt
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .config import Config
from .data import load_bars, load_news, split_days
from .indicators import atr, session_vwap
from .strategies import all_strategies
from .strategies.base import EntrySignal, Strategy


@dataclass
class _Open:
    entry_time: pd.Timestamp
    entry_price: float
    qty: int
    stop: float
    target: float | None
    trail_dist: float | None
    reason: str
    conditions: dict


@dataclass(frozen=True)
class Trade:
    strategy: str
    symbol: str
    date: dt.date
    entry_time: pd.Timestamp
    entry_price: float
    exit_time: pd.Timestamp
    exit_price: float
    qty: int
    pnl: float
    pnl_pct: float
    hold_minutes: float
    entry_reason: str
    exit_reason: str
    # Market-condition snapshot at entry — the tuning dataset of the future.
    mkt_gap_pct: float = float("nan")  # overnight gap vs prior session close
    mkt_change_open_pct: float = float("nan")  # session open -> entry
    mkt_dist_vwap_pct: float = float("nan")  # entry price vs session VWAP
    mkt_rel_volume: float = float("nan")  # signal-bar volume vs day-so-far average
    mkt_spy_change_pct: float = float("nan")  # SPY session open -> entry time
    # Time-series features of the session so far (all causal, bars 0..i):
    mkt_realized_vol_pct: float = float("nan")  # daily-ized std of 5m log returns
    mkt_trend_slope_pct: float = float("nan")  # OLS drift of log close, % per bar
    mkt_autocorr_1: float = float("nan")  # lag-1 autocorrelation of returns
    mkt_atr_pct: float = float("nan")  # ATR(14) as % of the signal bar's close
    mkt_range_pos: float = float("nan")  # entry inside day-so-far range (0=low, 1=high)
    hour_et: float = float("nan")  # entry hour (US/Eastern, decimal)
    weekday: str = ""


def entry_conditions(
    day: pd.DataFrame,
    i: int,
    entry_price: float,
    prior_close: float | None,
    vwap: pd.Series,
    spy_day: pd.DataFrame | None,
) -> dict:
    """Snapshot of market context at the entry bar (index i)."""
    ts = day.index[i]
    day_open = float(day["open"].iloc[0])
    gap = (day_open / prior_close - 1.0) * 100.0 if prior_close else float("nan")
    vol_so_far = day["volume"].iloc[:i]
    rel_vol = (
        float(day["volume"].iloc[i - 1] / vol_so_far.mean())
        if i >= 1 and vol_so_far.mean() > 0
        else float("nan")
    )
    spy_change = float("nan")
    if spy_day is not None and not spy_day.empty:
        spy_close = spy_day["close"].asof(ts)
        if pd.notna(spy_close):
            spy_change = (float(spy_close) / float(spy_day["open"].iloc[0]) - 1.0) * 100.0

    # Time-series features from bars 0..i only. sqrt(78) daily-izes 5m bar vol
    # (78 regular-hours bars per session — the lab's fixed interval).
    closes = day["close"].iloc[: i + 1].to_numpy(dtype=float)
    rets = np.diff(np.log(closes))
    rvol = float(np.std(rets, ddof=1) * np.sqrt(78.0) * 100.0) if len(rets) >= 2 else float("nan")
    slope = (
        float(np.polyfit(np.arange(len(closes)), np.log(closes), 1)[0] * 100.0)
        if len(closes) >= 3
        else float("nan")
    )
    ac1 = float("nan")
    if len(rets) >= 3 and np.std(rets[:-1]) > 0 and np.std(rets[1:]) > 0:
        ac1 = float(np.corrcoef(rets[:-1], rets[1:])[0, 1])
    atr_pct = float(atr(day).iloc[i] / closes[-1] * 100.0) if i >= 1 else float("nan")
    hi = float(day["high"].iloc[: i + 1].max())
    lo = float(day["low"].iloc[: i + 1].min())
    range_pos = (entry_price - lo) / (hi - lo) if hi > lo else float("nan")

    return {
        "mkt_gap_pct": round(gap, 3),
        "mkt_change_open_pct": round((entry_price / day_open - 1.0) * 100.0, 3),
        "mkt_dist_vwap_pct": round((entry_price / float(vwap.iloc[i]) - 1.0) * 100.0, 3),
        "mkt_rel_volume": round(rel_vol, 2),
        "mkt_spy_change_pct": round(spy_change, 3),
        "mkt_realized_vol_pct": round(rvol, 3),
        "mkt_trend_slope_pct": round(slope, 4),
        "mkt_autocorr_1": round(ac1, 3),
        "mkt_atr_pct": round(atr_pct, 3),
        "mkt_range_pos": round(range_pos, 3),
        "hour_et": round(ts.hour + ts.minute / 60.0, 2),
        "weekday": ts.strftime("%a"),
    }


def _fill_price(price: float, slippage_bps: float, side: str) -> float:
    adj = slippage_bps / 10_000.0
    return price * (1 + adj) if side == "buy" else price * (1 - adj)


def run_symbol_day(
    strategy: Strategy,
    symbol: str,
    date: dt.date,
    day: pd.DataFrame,
    prior_close: float | None,
    cfg: Config,
    spy_day: pd.DataFrame | None = None,
) -> list[Trade]:
    strategy.symbol = symbol
    strategy.new_day(day, prior_close)
    vwap = session_vwap(day)
    entry_cutoff = dt.time.fromisoformat(cfg.entry_cutoff)
    eod_cutoff = dt.time.fromisoformat(cfg.eod_cutoff)
    trade_cap = min(cfg.max_trades_per_day, strategy.max_trades_per_day)

    trades: list[Trade] = []
    pos: _Open | None = None
    pending_entry: EntrySignal | None = None
    pending_exit = False
    taken = 0
    last_i = len(day) - 1

    def close(pos_: _Open, ts: pd.Timestamp, price: float, why: str) -> None:
        pnl = (price - pos_.entry_price) * pos_.qty
        trades.append(
            Trade(
                strategy=strategy.name,
                symbol=symbol,
                date=date,
                entry_time=pos_.entry_time,
                entry_price=round(pos_.entry_price, 4),
                exit_time=ts,
                exit_price=round(price, 4),
                qty=pos_.qty,
                pnl=round(pnl, 2),
                pnl_pct=round((price / pos_.entry_price - 1.0) * 100.0, 4),
                hold_minutes=(ts - pos_.entry_time).total_seconds() / 60.0,
                entry_reason=pos_.reason,
                exit_reason=why,
                **pos_.conditions,
            )
        )

    for i in range(len(day)):
        ts = day.index[i]
        bar_open = float(day["open"].iloc[i])
        bar_high = float(day["high"].iloc[i])
        bar_low = float(day["low"].iloc[i])
        bar_close = float(day["close"].iloc[i])

        # 1) Dynamic exit signalled on the previous bar fills at this open.
        if pos is not None and pending_exit:
            close(pos, ts, _fill_price(bar_open, cfg.slippage_bps, "sell"), "signal")
            pos = None
        pending_exit = False

        # 2) Entry signalled on the previous bar fills at this open.
        if pos is None and pending_entry is not None:
            entry = _fill_price(bar_open, cfg.slippage_bps, "buy")
            sig = pending_entry
            stop = (
                sig.stop_price
                if sig.stop_price is not None
                else entry * (1 - (sig.stop_pct or 0.01))
            )
            if stop < entry:  # skip entries that gap through their own stop
                qty = int(cfg.notional_per_trade // entry)
                if qty > 0:
                    target = entry + sig.target_r * (entry - stop) if sig.target_r else None
                    conditions = entry_conditions(day, i, entry, prior_close, vwap, spy_day)
                    pos = _Open(
                        ts, entry, qty, stop, target, sig.trail_dist, sig.reason, conditions
                    )
                    taken += 1
        pending_entry = None

        # 3) Intra-bar stop first (conservative), then target; then ratchet any
        #    trailing stop using this bar's high (applies from the next bar on).
        if pos is not None:
            if bar_low <= pos.stop:
                close(pos, ts, _fill_price(pos.stop, cfg.slippage_bps, "sell"), "stop")
                pos = None
            elif pos.target is not None and bar_high >= pos.target:
                close(pos, ts, _fill_price(pos.target, cfg.slippage_bps, "sell"), "target")
                pos = None
            elif pos.trail_dist is not None:
                pos.stop = max(pos.stop, bar_high - pos.trail_dist)

        # 4) End of day: flatten and stop trading.
        at_eod = i == last_i or ts.time() >= eod_cutoff
        if at_eod:
            if pos is not None:
                close(pos, ts, _fill_price(bar_close, cfg.slippage_bps, "sell"), "eod")
                pos = None
            if ts.time() >= eod_cutoff:
                break
            continue

        # 5) Evaluate signals on this completed bar (for the next bar's open).
        if pos is not None:
            pending_exit = strategy.exit_signal(i)
        elif taken < trade_cap and ts.time() < entry_cutoff and i < last_i:
            pending_entry = strategy.entry_signal(i)

    return trades


def run_on(
    bars_by_symbol: dict[str, pd.DataFrame],
    make_strategies: Callable[[], list[Strategy]],
    cfg: Config,
    dates: set[dt.date] | None = None,
    spy_by_date: dict[dt.date, pd.DataFrame] | None = None,
) -> pd.DataFrame:
    """Run strategies over preloaded bars, optionally restricted to a set of
    session dates (prior closes still come from the full series, so a filtered
    day keeps its true previous-session close)."""
    trades: list[Trade] = []
    for symbol, bars in bars_by_symbol.items():
        days = split_days(bars)
        for strategy in make_strategies():
            strategy.symbol = symbol
            for date, day, prior_close in days:
                if dates is not None and date not in dates:
                    # Show the session to the strategy anyway (still causal —
                    # days arrive in order) so cross-session state like the AR
                    # model's return window stays continuous across a split.
                    strategy.new_day(day, prior_close)
                    continue
                spy_day = spy_by_date.get(date) if spy_by_date else None
                trades.extend(
                    run_symbol_day(strategy, symbol, date, day, prior_close, cfg, spy_day)
                )
    frame = pd.DataFrame([t.__dict__ for t in trades])
    if not frame.empty:
        frame = frame.sort_values("exit_time").reset_index(drop=True)
    return frame


def load_spy_by_date(cfg: Config) -> dict[dt.date, pd.DataFrame]:
    """SPY session frames keyed by date — market context for the trade journal."""
    try:
        spy = load_bars(["SPY"], cfg.interval, cfg.period)["SPY"]
    except Exception as exc:  # noqa: BLE001 — market-context is best-effort, never fatal
        print(f"warning: SPY context unavailable ({exc})")
        return {}
    return {date: day for date, day, _ in split_days(spy)}


def run_backtest(cfg: Config) -> pd.DataFrame:
    """Run every strategy over every symbol/day; returns one row per trade."""
    bars_by_symbol = load_bars(cfg.symbols, cfg.interval, cfg.period)
    news = load_news(cfg.symbols, cfg.interval, cfg.period)
    spy_by_date = load_spy_by_date(cfg)
    return run_on(bars_by_symbol, lambda: all_strategies(news), cfg, spy_by_date=spy_by_date)
