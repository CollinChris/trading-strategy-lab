"""SPY adjustment: beta, hold-window SPY return, hedged P&L, engine + review wiring."""

import datetime as dt

import numpy as np
import pandas as pd
from conftest import make_day

from trading_lab import market
from trading_lab.backtest import run_symbol_day
from trading_lab.config import Config
from trading_lab.review import verdict
from trading_lab.strategies.base import EntrySignal, Strategy


def _two_sessions(returns: np.ndarray, start: float = 100.0):
    """Two 78-bar sessions from a vector of per-bar log returns."""
    frames = []
    for k, date in enumerate(["2026-08-17", "2026-08-18"]):
        r = returns[k * 78 : (k + 1) * 78]
        c = start * np.exp(np.cumsum(r))
        frames.append(make_day(c, c * 1.001, c * 0.999, c, date=date))
    return pd.concat(frames)


def test_beta_recovers_known_multiple():
    rng = np.random.default_rng(1)
    m = rng.normal(0, 0.001, 156)
    spy = _two_sessions(m)
    stock = _two_sessions(2.5 * m + rng.normal(0, 0.0002, 156))
    assert abs(market.beta(stock, spy, min_obs=100) - 2.5) < 0.1


def test_beta_falls_back_to_one_without_overlap():
    rng = np.random.default_rng(2)
    spy = _two_sessions(rng.normal(0, 0.001, 156))
    assert market.beta(spy.iloc[:10], spy) == 1.0


def test_spy_return_and_window_guard():
    spy = make_day(
        np.linspace(100, 110, 20),
        np.linspace(100, 110, 20) + 0.1,
        np.linspace(100, 110, 20) - 0.1,
        np.linspace(100, 110, 20),
    )
    t0, t1 = spy.index[5], spy.index[15]
    ret = market.spy_return(spy, t0, t1)
    assert ret is not None and ret > 0
    assert (
        market.spy_return(spy, t0 - pd.Timedelta(days=3), t1) is None
    )  # outside the data: no guess
    with_us = t0 + pd.Timedelta(microseconds=123456)  # Alpaca-style fill time
    assert market.price_at(spy, with_us) == market.price_at(spy, t0)


def test_adjusted_pnl_removes_market_move():
    # Long $10k of a beta-2 stock that rode a +1% SPY move to +$200: no alpha left.
    adj = market.adjusted_pnl(200.0, +1, 10_000, 2.0, 0.01, slippage_bps=0.0)
    assert abs(adj) < 1e-9
    # Short that "won" $150 on a -1% SPY day at beta 1.5: also nothing left.
    assert abs(market.adjusted_pnl(150.0, -1, 10_000, 1.5, -0.01, 0.0)) < 1e-9
    # Hedge slippage is charged: 2 x 1bp x beta 2 x $10k = $4.
    assert abs(market.adjusted_pnl(0.0, +1, 10_000, 2.0, 0.0, 1.0) + 4.0) < 1e-9


class _BuyAt(Strategy):
    name = "stub"

    def entry_signal(self, i):
        return EntrySignal("t", stop_pct=0.5) if i == 2 else None


def test_engine_records_spy_adjusted_pnl():
    n = 20
    stock = make_day(np.full(n, 100.0), np.full(n, 100.5), np.full(n, 99.5), np.full(n, 100.0))
    spy_close = np.linspace(400, 404, n)  # SPY drifts up during the hold
    spy = make_day(spy_close, spy_close + 0.1, spy_close - 0.1, spy_close)
    cfg = Config(slippage_bps=0.0, hedge_slippage_bps=0.0)
    t = run_symbol_day(_BuyAt(), "TST", dt.date(2026, 8, 17), stock, None, cfg, spy, beta=1.0)[0]
    assert t.pnl == 0.0 and t.spy_ret_pct > 0
    assert t.pnl_vs_spy < 0  # flat stock + rising market = negative alpha for a long


def test_review_verdicts():
    rng = np.random.default_rng(3)
    assert verdict(pd.Series(rng.normal(20, 50, 150)))["verdict"] == "**beats the market**"
    assert verdict(pd.Series(rng.normal(20, 50, 60)))["verdict"] == "promising (needs more trades)"
    assert verdict(pd.Series(rng.normal(-20, 50, 150)))["verdict"] == "loses beyond the market"
    assert verdict(pd.Series(rng.normal(0, 50, 150)))["verdict"] == "no evidence of edge"
    assert verdict(pd.Series(rng.normal(0, 50, 10)))["verdict"] == "too few trades"


def test_retired_variants_off_by_default():
    cfg = Config()
    assert not cfg.trade_tuned_variants and not cfg.trade_regime_variants
    assert cfg.long_gate == "none"
    assert len(cfg.symbols) == 10 and "JPM" in cfg.symbols
