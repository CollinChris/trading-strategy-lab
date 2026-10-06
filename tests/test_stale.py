"""close_stale_positions(): only shares held over from a previous session are closed."""

import datetime as dt
import types

import trading_lab.paper as paper
from trading_lab.data import MARKET_TZ

TODAY = dt.date(2026, 10, 6)
MORNING = dt.datetime(2026, 10, 6, 10, 0, tzinfo=MARKET_TZ)
YESTERDAY = dt.datetime(2026, 10, 5, 11, 0, tzinfo=MARKET_TZ)


def order(symbol, side, qty, filled_at, legs=()):
    return types.SimpleNamespace(
        symbol=symbol,
        side=f"OrderSide.{side}",
        filled_qty=str(qty),
        filled_at=filled_at,
        legs=list(legs),
    )


def pos(symbol, qty):
    return types.SimpleNamespace(symbol=symbol, qty=str(qty))


class FakeClient:
    def __init__(self, positions, orders):
        self.positions, self.orders, self.closed = positions, orders, []

    def get_all_positions(self):
        return self.positions

    def get_orders(self, *a, **k):
        return self.orders

    def close_position(self, symbol, close_options=None):
        self.closed.append((symbol, int(close_options.qty)))


def run(monkeypatch, positions, orders):
    monkeypatch.setattr(paper, "market_today", lambda: TODAY)
    client = FakeClient(positions, orders)
    paper.close_stale_positions(client)
    return client.closed


def test_overnight_positions_fully_closed(monkeypatch):
    # The 2026-10-05 case: entries yesterday, no fills today -> close everything.
    orders = [order("TSLA", "BUY", 78, YESTERDAY), order("PLTR", "SELL", 158, YESTERDAY)]
    closed = run(monkeypatch, [pos("TSLA", 78), pos("PLTR", -158)], orders)
    assert sorted(closed) == [("PLTR", 158), ("TSLA", 78)]


def test_todays_positions_untouched(monkeypatch):
    orders = [order("AMD", "BUY", 15, MORNING)]
    assert run(monkeypatch, [pos("AMD", 15)], orders) == []


def test_mixed_position_closes_only_held_over_part(monkeypatch):
    # Short 50 from yesterday, shorted 20 more today -> close the 50, keep today's 20.
    orders = [order("COIN", "SELL", 50, YESTERDAY), order("COIN", "SELL", 20, MORNING)]
    assert run(monkeypatch, [pos("COIN", -70)], orders) == [("COIN", 50)]


def test_partial_exit_today_counts_through_bracket_legs(monkeypatch):
    # Long 15 from yesterday; a stop leg sold 5 this morning -> 10 left, all stale.
    parent = order("AMD", "BUY", 15, YESTERDAY, legs=[order("AMD", "SELL", 5, MORNING)])
    assert run(monkeypatch, [pos("AMD", 10)], [parent]) == [("AMD", 10)]


def test_no_positions_no_calls(monkeypatch):
    assert run(monkeypatch, [], [order("AMD", "BUY", 15, YESTERDAY)]) == []
