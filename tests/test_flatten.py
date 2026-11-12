"""flatten(): session-clock guards and the cancel/close/verify retry loop."""

import datetime as dt
import types

import trading_lab.paper as paper


class FakeClient:
    def __init__(self, is_open=True, positions=None, close_after_attempt=1, minutes_left=20):
        self._is_open = is_open
        self._minutes_left = minutes_left  # minutes to the session close
        # positions returned until `close_after_attempt` close calls have run
        self._positions = list(positions or [])
        self._close_after = close_after_attempt
        self.close_calls = 0
        self.cancel_calls = 0
        self.orders = []

    def get_clock(self):
        return clock(self._is_open, self._minutes_left)

    def get_orders(self, *a, **k):
        return self.orders

    def cancel_orders(self):
        self.cancel_calls += 1
        self.orders = []

    def close_all_positions(self, cancel_orders=False):
        self.close_calls += 1
        if self.close_calls >= self._close_after:
            self._positions = []
        return []

    def get_all_positions(self):
        return self._positions


def clock(is_open: bool, minutes_left: float):
    now = dt.datetime(2026, 11, 11, 15, 0, tzinfo=dt.UTC)
    return types.SimpleNamespace(
        is_open=is_open, timestamp=now, next_close=now + dt.timedelta(minutes=minutes_left)
    )


def _patch(monkeypatch, client):
    monkeypatch.setattr(paper, "_client", lambda: client)
    monkeypatch.setattr(paper.time, "sleep", lambda *_: None)  # no real waiting


def test_skips_when_market_closed(monkeypatch, capsys):
    pos = [types.SimpleNamespace(symbol="COIN", qty="232")]
    client = FakeClient(is_open=False, positions=pos)
    _patch(monkeypatch, client)
    paper.flatten()
    assert client.close_calls == 0 and client.cancel_calls == 0  # never touches orders
    assert "Market closed" in capsys.readouterr().out


def test_closes_when_open(monkeypatch, capsys):
    pos = [types.SimpleNamespace(symbol="COIN", qty="232")]
    client = FakeClient(is_open=True, positions=pos, close_after_attempt=1)
    _patch(monkeypatch, client)
    paper.flatten()
    assert client.close_calls == 1
    assert "Flattened" in capsys.readouterr().out


def test_retries_when_first_close_leaves_positions(monkeypatch, capsys):
    # The 2026-09-17 bug: first close leaves the position; the retry clears it.
    pos = [types.SimpleNamespace(symbol="PLTR", qty="168")]
    client = FakeClient(is_open=True, positions=pos, close_after_attempt=2)
    _patch(monkeypatch, client)
    paper.flatten()
    assert client.close_calls == 2 and client.cancel_calls == 2
    assert "Flattened" in capsys.readouterr().out


def test_warns_when_stuck(monkeypatch, capsys):
    pos = [types.SimpleNamespace(symbol="PLTR", qty="168")]
    client = FakeClient(is_open=True, positions=pos, close_after_attempt=99)
    _patch(monkeypatch, client)
    paper.flatten()
    assert "WARNING" in capsys.readouterr().out


def test_symbol_cap_blocks_crowding():
    # The 2026-09-17 scenario: many strategies agree on one symbol. With a
    # $30k cap and $10k orders, only the first three fit; the rest are blocked.
    from trading_lab.paper import _fits_symbol_cap

    cap = 30_000.0
    committed = {}
    fits = 0
    for _ in range(10):  # ten strategies pile into PLTR
        if _fits_symbol_cap(committed, "PLTR", 10_000.0, cap):
            committed["PLTR"] = committed.get("PLTR", 0.0) + 10_000.0
            fits += 1
    assert fits == 3
    assert committed["PLTR"] == 30_000.0


def test_symbol_cap_counts_existing_position():
    from trading_lab.paper import _fits_symbol_cap

    committed = {"COIN": 25_000.0}  # already open from earlier scans today
    assert _fits_symbol_cap(committed, "COIN", 5_000.0, 30_000.0)  # fits exactly
    assert not _fits_symbol_cap(committed, "COIN", 6_000.0, 30_000.0)  # would exceed
    assert _fits_symbol_cap(committed, "NVDA", 10_000.0, 30_000.0)  # other symbol unaffected


def test_session_phase_uses_real_close():
    assert paper.session_phase(clock(False, 0)) == "closed"
    assert paper.session_phase(clock(True, 20)) == "sweep"  # 15:40 on a normal day
    assert paper.session_phase(clock(True, 10)) == "sweep"  # 15:50 scan
    assert paper.session_phase(clock(True, 28)) == "no_entries"
    assert paper.session_phase(clock(True, 80)) == "open"  # 14:40 ET: winter GitHub cron
    # Half-day (13:00 close): 12:40 is already the flatten window.
    assert paper.session_phase(clock(True, 20)) == "sweep"


def test_too_early_does_not_flatten(monkeypatch, capsys):
    pos = [types.SimpleNamespace(symbol="NVDA", qty="169")]
    client = FakeClient(positions=pos, minutes_left=80)
    _patch(monkeypatch, client)
    paper.flatten()
    assert client.close_calls == 0 and "too early" in capsys.readouterr().out
    paper.flatten(force=True)
    assert client.close_calls == 1


def test_scan_sweeps_in_closing_window(monkeypatch, capsys):
    """The 2026-11-11 case: the flatten job never ran, but the 15:50 scan did."""
    pos = [types.SimpleNamespace(symbol="NVDA", qty="169")]
    client = FakeClient(positions=pos, minutes_left=10)
    _patch(monkeypatch, client)
    paper.scan_and_trade(paper.Config())
    assert client.close_calls == 1 and client.get_all_positions() == []
    assert "End-of-day sweep" in capsys.readouterr().out


def test_scan_stops_entries_before_early_close(monkeypatch, capsys):
    client = FakeClient(positions=[], minutes_left=28)
    _patch(monkeypatch, client)
    monkeypatch.setattr(paper, "close_stale_positions", lambda c: 0)
    paper.scan_and_trade(paper.Config())
    assert client.close_calls == 0 and "no new entries" in capsys.readouterr().out
