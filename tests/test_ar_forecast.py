"""ArForecast: causality, cross-session state, and signal behavior."""

import numpy as np
from conftest import make_day

from trading_lab.strategies import ArForecast

DATES = ["2026-08-17", "2026-08-18", "2026-08-19"]


def day_from_closes(closes, date):
    closes = np.asarray(closes, dtype=float)
    return make_day(closes, closes + 0.1, closes - 0.1, closes, date=date)


def trending_closes(n=80, start=100.0, drift=0.002):
    """A session whose close compounds by `drift` every bar — maximally predictable."""
    return start * (1 + drift) ** np.arange(n)


def feed(strategy, sessions):
    """Run new_day over sessions in order, return the strategy ready on the last."""
    for closes, date in zip(sessions, DATES):
        strategy.new_day(day_from_closes(closes, date), None)
    return strategy


def test_fires_on_predictable_trend():
    sessions = [trending_closes() for _ in range(3)]
    strat = feed(ArForecast(), sessions)
    sig = strat.entry_signal(30)
    assert sig is not None
    assert "AR(12)" in sig.reason


def test_silent_on_flat_prices():
    sessions = [np.full(80, 100.0) for _ in range(3)]
    strat = feed(ArForecast(), sessions)
    assert strat.entry_signal(30) is None


def test_needs_history_before_trading():
    # One lone session (~60 training rows) is below min_obs=100: no signal.
    strat = ArForecast()
    strat.new_day(day_from_closes(trending_closes(), DATES[0]), None)
    assert strat.entry_signal(30) is None


def test_no_lookahead():
    # The signal at bar i must not change when bars after i change.
    rng = np.random.default_rng(7)
    sessions = [
        100.0 * np.exp(np.cumsum(rng.normal(0.0004, 0.002, 80))) for _ in range(3)
    ]
    i = 40
    baseline = feed(ArForecast(), sessions)._forecast(i)

    mutated = [s.copy() for s in sessions]
    mutated[2][i + 1 :] = 5.0  # crash every future bar of the live session
    assert feed(ArForecast(), mutated)._forecast(i) == baseline


def test_exit_after_horizon():
    sessions = [trending_closes() for _ in range(3)]
    strat = feed(ArForecast(horizon=6), sessions)
    assert strat.entry_signal(30) is not None
    assert not strat.exit_signal(35)  # trend intact, horizon not lapsed
    assert strat.exit_signal(36)  # horizon bars after the signal


def test_window_drops_old_sessions():
    strat = ArForecast(window_sessions=2)
    for k in range(4):
        strat.new_day(day_from_closes(trending_closes(), f"2026-08-{17 + k}"), None)
    assert len(strat._past) == 2
