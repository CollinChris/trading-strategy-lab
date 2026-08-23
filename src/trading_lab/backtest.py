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
from dataclasses import dataclass

import pandas as pd

from .config import Config
from .data import load_bars, split_days
from .strategies import all_strategies
from .strategies.base import EntrySignal, Strategy


@dataclass
class _Open:
    entry_time: pd.Timestamp
    entry_price: float
    qty: int
    stop: float
    target: float | None
    reason: str


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
) -> list[Trade]:
    strategy.new_day(day, prior_close)
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
                    pos = _Open(ts, entry, qty, stop, target, sig.reason)
                    taken += 1
        pending_entry = None

        # 3) Intra-bar stop first (conservative), then target.
        if pos is not None:
            if bar_low <= pos.stop:
                close(pos, ts, _fill_price(pos.stop, cfg.slippage_bps, "sell"), "stop")
                pos = None
            elif pos.target is not None and bar_high >= pos.target:
                close(pos, ts, _fill_price(pos.target, cfg.slippage_bps, "sell"), "target")
                pos = None

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


def run_backtest(cfg: Config) -> pd.DataFrame:
    """Run every strategy over every symbol/day; returns one row per trade."""
    bars_by_symbol = load_bars(cfg.symbols, cfg.interval, cfg.period)
    trades: list[Trade] = []
    for symbol, bars in bars_by_symbol.items():
        days = split_days(bars)
        for strategy in all_strategies():
            for date, day, prior_close in days:
                trades.extend(run_symbol_day(strategy, symbol, date, day, prior_close, cfg))
    frame = pd.DataFrame([t.__dict__ for t in trades])
    if not frame.empty:
        frame = frame.sort_values("exit_time").reset_index(drop=True)
    return frame
