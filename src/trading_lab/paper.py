"""Alpaca paper-trading executor (stage 2 of the lab).

Runs one scan: fetch today's bars so far, ask every strategy for a signal on
the latest completed bar, and submit bracket market orders to the Alpaca PAPER
account for any that fire. Designed to be run repeatedly during US market
hours (cron / GitHub Actions), mirroring the backtest's next-bar execution.

Simplifications vs the backtest (documented in the README):
- one paper trade per strategy+symbol per day (tracked in data/paper_state.json)
- dynamic-exit strategies (EMA crossover, RSI reversion) trade with a stop-only
  bracket; run `trading-lab paper --flatten` at ~15:55 ET for the EOD exit.

Requires ALPACA_API_KEY / ALPACA_SECRET_KEY in .env — paper keys only.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv

from .config import Config
from .data import load_bars, market_today, split_days
from .strategies import all_strategies

STATE_PATH = Path("data/paper_state.json")


def _client():
    load_dotenv()
    key = os.getenv("ALPACA_API_KEY")
    secret = os.getenv("ALPACA_SECRET_KEY")
    if not key or not secret:
        raise SystemExit(
            "Missing ALPACA_API_KEY / ALPACA_SECRET_KEY. Copy .env.example to .env "
            "and add PAPER keys from https://alpaca.markets (free)."
        )
    from alpaca.trading.client import TradingClient

    return TradingClient(key, secret, paper=True)


def _load_state() -> dict[str, list[str]]:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {}


def _save_state(state: dict[str, list[str]]) -> None:
    STATE_PATH.parent.mkdir(exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2))


def scan_and_trade(cfg: Config, dry_run: bool = False) -> None:
    """One pass: signal on the latest completed bar -> bracket market order."""
    today = market_today().isoformat()  # market date, not the local (SGT) date
    state = _load_state()
    done_today: list[str] = state.get(today, [])

    bars_by_symbol = load_bars(cfg.symbols, cfg.interval, period="5d")
    client = None if dry_run else _client()
    placed = 0

    for symbol, bars in bars_by_symbol.items():
        days = split_days(bars)
        date, day, prior_close = days[-1]
        if date.isoformat() != today:
            print(f"{symbol}: latest session is {date}, not today — market closed? skipping.")
            continue
        if len(day) < 2:
            continue
        last_price = float(day["close"].iloc[-1])

        for strategy in all_strategies():
            tag = f"{strategy.name}--{symbol}--{today}"
            if tag in done_today:
                continue
            strategy.new_day(day, prior_close)
            sig = strategy.entry_signal(len(day) - 1)
            if sig is None:
                continue

            stop = (
                sig.stop_price
                if sig.stop_price is not None
                else last_price * (1 - (sig.stop_pct or 0.01))
            )
            if stop >= last_price:
                continue
            qty = int(cfg.notional_per_trade // last_price)
            if qty < 1:
                continue
            target = last_price + sig.target_r * (last_price - stop) if sig.target_r else None

            line = (
                f"{strategy.name:15s} BUY {qty} {symbol} ~{last_price:.2f} "
                f"stop {stop:.2f}"
                + (f" target {target:.2f}" if target else " (no target)")
                + f" — {sig.reason}"
            )
            if dry_run:
                print(f"[dry-run] {line}")
            else:
                _submit(client, symbol, qty, stop, target, tag)
                print(f"[submitted] {line}")
                done_today.append(tag)
                placed += 1

    if not dry_run:
        state[today] = done_today
        _save_state(state)
    print(f"Scan complete — {placed} order(s) submitted." if not dry_run else "Dry run complete.")


def _submit(client, symbol: str, qty: int, stop: float, target: float | None, tag: str) -> None:
    from alpaca.trading.enums import OrderClass, OrderSide, TimeInForce
    from alpaca.trading.requests import MarketOrderRequest, StopLossRequest, TakeProfitRequest

    request = MarketOrderRequest(
        symbol=symbol,
        qty=qty,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.DAY,
        order_class=OrderClass.BRACKET if target else OrderClass.OTO,
        stop_loss=StopLossRequest(stop_price=round(stop, 2)),
        take_profit=TakeProfitRequest(limit_price=round(target, 2)) if target else None,
        client_order_id=tag,
    )
    client.submit_order(request)


def flatten() -> None:
    """Close all paper positions and cancel open orders (EOD discipline)."""
    client = _client()
    client.cancel_orders()
    closed = client.close_all_positions(cancel_orders=True)
    print(f"Flattened {len(closed)} position(s); all open orders cancelled.")


def status() -> None:
    client = _client()
    positions = client.get_all_positions()
    if not positions:
        print("No open paper positions.")
    for p in positions:
        print(
            f"{p.symbol}: {p.qty} @ {float(p.avg_entry_price):.2f} "
            f"→ {float(p.current_price):.2f} ({float(p.unrealized_plpc) * 100:+.2f}%)"
        )
