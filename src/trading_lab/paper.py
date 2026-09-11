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

import datetime as dt
import json
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from .backtest import entry_conditions, position_size
from .config import Config
from .data import MARKET_TZ, load_bars, load_news, market_today, split_days
from .indicators import atr, session_vwap
from .regime import RegimeFilter, load_filter
from .strategies import all_strategies

STATE_PATH = Path("data/paper_state.json")
JOURNAL_PATH = Path("results/paper_journal.csv")
TUNED_PATH = Path("results/tuned_params.json")


def _load_tuned() -> dict[str, dict]:
    """Saturday's tuned parameters — traded as `<name>_tuned` variants
    alongside the defaults. Absent or unreadable file just means no variants."""
    try:
        payload = json.loads(TUNED_PATH.read_text())
        return {name: entry["params"] for name, entry in payload["strategies"].items()}
    except (OSError, KeyError, ValueError):
        return {}


def _load_regime() -> RegimeFilter | None:
    """The walk-forward-validated regime filter (results/regime_model.joblib),
    traded as `<name>_regime` variants: the base strategy's signal, taken only
    when the filter's predicted EV for the live conditions is positive. No
    file → no variants, base strategies unaffected."""
    loaded = load_filter()
    if loaded is None:
        return None
    flt, meta = loaded
    print(
        f"regime filter: {meta.get('kind')} fitted {meta.get('generated')} on "
        f"{meta.get('sessions')} sessions (OOS {meta.get('oos_exp_all'):+.2f} → "
        f"{meta.get('oos_exp_kept'):+.2f}/trade)"
    )
    return flt


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
    now_et = dt.datetime.now(tz=MARKET_TZ)
    entry_cutoff = dt.time.fromisoformat(cfg.entry_cutoff)
    if not dt.time(9, 35) <= now_et.time() < entry_cutoff:
        print(
            f"{now_et:%H:%M} ET is outside the entry window (09:35–{cfg.entry_cutoff}) — no scan."
        )
        return

    today = market_today().isoformat()  # market date, not the local (SGT) date
    state = _load_state()
    done_today: list[str] = state.get(today, [])

    bars_by_symbol = load_bars(cfg.symbols, cfg.interval, period="5d", on_missing="skip")
    news = load_news(cfg.symbols, cfg.interval, period="3d")
    tuned = _load_tuned()
    regime = _load_regime()
    spy_today = None
    if regime is not None:
        # SPY context feeds the filter's mkt_spy_change_pct; best-effort.
        spy = load_bars(["SPY"], cfg.interval, period="5d", on_missing="skip").get("SPY")
        if spy is not None and not spy.empty:
            spy_date, spy_day, _ = split_days(spy)[-1]
            spy_today = spy_day if spy_date.isoformat() == today else None
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
        vwap = session_vwap(day) if regime is not None else None

        for strategy in all_strategies(news, tuned=tuned):
            tag = f"{strategy.name}--{symbol}--{today}"
            if tag in done_today:
                continue
            strategy.symbol = symbol
            # Replay the loaded window's earlier sessions first so strategies
            # with cross-session state (the AR model) see the same history in
            # paper mode as in a backtest.
            for _, past_day, past_prior in days[:-1]:
                strategy.new_day(past_day, past_prior)
            strategy.new_day(day, prior_close)
            sig = strategy.entry_signal(len(day) - 1)
            if sig is None:
                continue

            d = sig.direction  # +1 long, -1 short
            stop = (
                sig.stop_price
                if sig.stop_price is not None
                else last_price * (1 - d * (sig.stop_pct or 0.01))
            )
            if cfg.vol_sizing and sig.stop_price is None:
                stop = last_price - d * cfg.stop_atr_mult * float(atr(day).iloc[-1])
            if d * (last_price - stop) <= 0:  # stop on the wrong side of entry
                continue
            qty = position_size(last_price, stop, cfg)
            if qty < 1:
                continue
            target = (
                last_price + d * sig.target_r * abs(last_price - stop) if sig.target_r else None
            )

            line = (
                f"{strategy.name:15s} {'BUY' if d == 1 else 'SELL SHORT'} {qty} {symbol} "
                f"~{last_price:.2f} stop {stop:.2f}"
                + (f" target {target:.2f}" if target else " (no target)")
                + f" — {sig.reason}"
            )
            # The regime variant: same signal, second order, only when the
            # filter's predicted EV for right-now conditions is positive.
            # Tuned variants don't get one — keep the live A/B two-way.
            orders = [(strategy.name, tag, line)]
            if regime is not None and not strategy.name.endswith("_tuned"):
                conditions = entry_conditions(
                    day, len(day) - 1, last_price, prior_close, vwap, spy_today
                )
                ev = regime.score_signal(strategy.name, sig.side, conditions)
                if ev > 0:
                    rname = f"{strategy.name}_regime"
                    rtag = f"{rname}--{symbol}--{today}"
                    if rtag not in done_today:
                        orders.append(
                            (
                                rname,
                                rtag,
                                f"{rname:15s} [regime EV {ev:+.2f}] " + line.split(" ", 1)[1],
                            )
                        )
                else:
                    print(f"[regime skip] {strategy.name} {symbol} EV {ev:+.2f}")
            for name, otag, oline in orders:
                if dry_run:
                    print(f"[dry-run] {oline}")
                    continue
                try:
                    _submit(client, symbol, qty, stop, target, otag, sig.side)
                except Exception as exc:  # noqa: BLE001 — one bad order must not stop the scan
                    # Deterministic client_order_id doubles as the dedup key on
                    # stateless runners: Alpaca rejects a reused id.
                    if "client_order_id" in str(exc) or "unique" in str(exc).lower():
                        print(f"[already today] {name} {symbol}")
                        done_today.append(otag)
                    else:
                        print(f"[error] {oline}\n        {exc}")
                    continue
                print(f"[submitted] {oline}")
                done_today.append(otag)
                placed += 1

    if not dry_run:
        state[today] = done_today
        _save_state(state)
    print(f"Scan complete — {placed} order(s) submitted." if not dry_run else "Dry run complete.")


def _submit(
    client, symbol: str, qty: int, stop: float, target: float | None, tag: str, side: str = "long"
) -> None:
    from alpaca.trading.enums import OrderClass, OrderSide, TimeInForce
    from alpaca.trading.requests import MarketOrderRequest, StopLossRequest, TakeProfitRequest

    request = MarketOrderRequest(
        symbol=symbol,
        qty=qty,
        side=OrderSide.BUY if side == "long" else OrderSide.SELL,
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


def journal(cfg: Config) -> None:
    """Append today's filled paper trades to results/paper_journal.csv.

    Each row = one strategy entry (identified by our client_order_id tag)
    with entry/exit fills from Alpaca plus the same market-condition snapshot
    the backtester records — so paper results accumulate into a tuning dataset.
    Exits closed by --flatten instead of a bracket leg are matched best-effort
    to the earliest sell fill for that symbol after the entry. A trade whose
    position is still open is journaled with exit_reason="open" and re-visited
    on later runs; once its exit fills, the placeholder row is replaced.
    """
    from alpaca.trading.enums import QueryOrderStatus
    from alpaca.trading.requests import GetOrdersRequest

    from .backtest import load_spy_by_date

    client = _client()
    regime = _load_regime()
    today = market_today()
    day_start = dt.datetime.combine(today, dt.time(0, 0), tzinfo=MARKET_TZ)
    # Look back several days, not just today, so an entry journaled while the
    # position was still open (e.g. held overnight after a missed flatten) is
    # found again and its exit fill can be recorded.
    orders = client.get_orders(
        GetOrdersRequest(
            status=QueryOrderStatus.CLOSED,
            after=day_start - dt.timedelta(days=5),
            limit=500,
            nested=True,
        )
    )

    bars_by_symbol = load_bars(cfg.symbols, cfg.interval, period="5d", on_missing="skip")
    try:
        spy_by_date = load_spy_by_date(Config(symbols=cfg.symbols, period="5d"))
    except Exception as exc:  # noqa: BLE001 — conditions are best-effort; journal regardless
        print(f"warning: SPY conditions unavailable ({exc})")
        spy_by_date = {}

    existing = pd.read_csv(JOURNAL_PATH) if JOURNAL_PATH.exists() else None
    already: set[str] = set()
    open_already: set[str] = set()
    if existing is not None:
        ids = existing["client_order_id"].astype(str)
        open_already = set(ids[existing["exit_reason"] == "open"])
        already = set(ids) - open_already

    # Non-ours fills from --flatten / close_all_positions: sells close longs,
    # buys cover shorts.
    flatten_sells: dict[str, list] = {}
    flatten_buys: dict[str, list] = {}
    for o in orders:
        ours = o.client_order_id and "--" in str(o.client_order_id)
        if not ours and o.filled_at is not None:
            bucket = flatten_sells if "SELL" in str(o.side).upper() else flatten_buys
            bucket.setdefault(o.symbol, []).append(o)

    rows = []
    for o in orders:
        tag = str(o.client_order_id or "")
        if "--" not in tag or tag in already or o.filled_at is None:
            continue  # not one of ours / already journaled / never filled
        strategy_name = tag.split("--")[0]
        entry_price = float(o.filled_avg_price)
        entry_time = pd.Timestamp(o.filled_at).tz_convert(MARKET_TZ)
        entry_date = entry_time.date()
        qty = int(float(o.filled_qty))
        side = "short" if "SELL" in str(o.side).upper() else "long"
        d = -1 if side == "short" else 1

        exit_price, exit_time, exit_reason = None, None, "open"
        for leg in o.legs or []:
            if leg.filled_at is not None:
                exit_price = float(leg.filled_avg_price)
                exit_time = pd.Timestamp(leg.filled_at).tz_convert(MARKET_TZ)
                exit_reason = "stop" if "stop" in str(leg.type).lower() else "target"
        if exit_price is None:
            # Earliest flatten fill after the entry (sell for longs, buy-to-
            # cover for shorts): an overnight hold closes at the next open,
            # before any later same-symbol trade that day.
            closers = flatten_sells if d == 1 else flatten_buys
            fills = [s for s in closers.get(o.symbol, []) if s.filled_at > o.filled_at]
            if fills:
                fill = min(fills, key=lambda s: s.filled_at)
                exit_price = float(fill.filled_avg_price)
                exit_time = pd.Timestamp(fill.filled_at).tz_convert(MARKET_TZ)
                exit_reason = "eod"
        if exit_price is None and tag in open_already:
            continue  # still open and already journaled as such — nothing new

        conditions = {}
        bars = bars_by_symbol.get(o.symbol)
        if bars is not None:
            days = {date: (day, prior) for date, day, prior in split_days(bars)}
            if entry_date in days:
                day, prior_close = days[entry_date]
                # Alpaca fill times carry sub-second precision; match the bar
                # index's datetime unit or searchsorted refuses the conversion.
                i = max(0, day.index.searchsorted(entry_time.as_unit(day.index.unit)) - 1)
                conditions = entry_conditions(
                    day,
                    int(i),
                    entry_price,
                    prior_close,
                    session_vwap(day),
                    spy_by_date.get(entry_date),
                )

        # The filter's verdict at entry on EVERY row (not just `_regime` ones),
        # so kept-vs-skipped can be compared on the base strategies' real fills.
        regime_ev = (
            round(regime.score_signal(strategy_name, side, conditions), 2)
            if regime is not None and conditions
            else None
        )
        rows.append(
            {
                "client_order_id": tag,
                "date": entry_date.isoformat(),
                "strategy": strategy_name,
                "symbol": o.symbol,
                "qty": qty,
                "side": side,
                "entry_time": entry_time,
                "entry_price": entry_price,
                "exit_time": exit_time,
                "exit_price": exit_price,
                "exit_reason": exit_reason,
                "pnl": round((exit_price - entry_price) * qty * d, 2) if exit_price else None,
                **conditions,
                "regime_ev": regime_ev,
            }
        )

    if not rows:
        print("No new filled paper trades to journal.")
        return
    frame = pd.DataFrame(rows)
    updated = sum(1 for r in rows if r["client_order_id"] in open_already)
    if existing is not None:
        # A re-visited trade replaces its open placeholder row.
        kept = existing[
            ~existing["client_order_id"].astype(str).isin(set(frame["client_order_id"]))
        ]
        frame = pd.concat([kept, frame], ignore_index=True)
    if "side" in frame.columns:
        # Rows journaled before the short side existed were all longs.
        frame["side"] = frame["side"].fillna("long")
    JOURNAL_PATH.parent.mkdir(exist_ok=True)
    frame.to_csv(JOURNAL_PATH, index=False)
    print(f"Journaled {len(rows)} trade(s), {updated} exit update(s) → {JOURNAL_PATH}")
