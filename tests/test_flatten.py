"""flatten(): market-hours guard and the cancel/close/verify retry loop."""

import types

import trading_lab.paper as paper


class FakeClient:
    def __init__(self, is_open=True, positions=None, close_after_attempt=1):
        self._is_open = is_open
        # positions returned until `close_after_attempt` close calls have run
        self._positions = list(positions or [])
        self._close_after = close_after_attempt
        self.close_calls = 0
        self.cancel_calls = 0
        self.orders = []

    def get_clock(self):
        return types.SimpleNamespace(is_open=self._is_open)

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
