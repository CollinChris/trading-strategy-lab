import datetime as dt

from trading_lab.backtest import run_symbol_day
from trading_lab.config import Config
from trading_lab.strategies.base import EntrySignal, Strategy

CFG = Config(slippage_bps=0.0)  # zero slippage makes fills exact for assertions
DATE = dt.date(2026, 8, 17)


class SignalAtBar(Strategy):
    """Test stub: fires one entry signal at a fixed bar index."""

    name = "stub"
    max_trades_per_day = 5

    def __init__(self, at, stop_price=None, stop_pct=None, target_r=None, exit_at=None):
        self.at = at
        self.sig = EntrySignal("test", stop_price=stop_price, stop_pct=stop_pct, target_r=target_r)
        self.exit_at = exit_at

    def entry_signal(self, i):
        return self.sig if i == self.at else None

    def exit_signal(self, i):
        return self.exit_at is not None and i >= self.exit_at


def test_entry_fills_at_next_bar_open(flat_day):
    day = flat_day.copy()
    day.loc[day.index[3], "open"] = 101.0
    trades = run_symbol_day(SignalAtBar(at=2, stop_pct=0.5), "TST", DATE, day, None, CFG)
    assert len(trades) == 1
    assert trades[0].entry_price == 101.0  # bar 3's open, not bar 2's close
    assert trades[0].entry_time == day.index[3]


def test_stop_beats_target_in_same_bar(flat_day):
    day = flat_day.copy()
    # Bar 4 spans both the stop (99) and the 2R target — conservative = stop.
    day.loc[day.index[4], "high"] = 110.0
    day.loc[day.index[4], "low"] = 98.0
    trades = run_symbol_day(
        SignalAtBar(at=3, stop_price=99.0, target_r=2.0), "TST", DATE, day, None, CFG
    )
    assert len(trades) == 1
    assert trades[0].exit_reason == "stop"
    assert trades[0].exit_price == 99.0


def test_target_hit(flat_day):
    day = flat_day.copy()
    # Entry at bar 4 open = 100, stop 99 => 2R target 102. Bar 6 tags it cleanly.
    day.loc[day.index[6], "high"] = 103.0
    trades = run_symbol_day(
        SignalAtBar(at=3, stop_price=99.0, target_r=2.0), "TST", DATE, day, None, CFG
    )
    assert trades[0].exit_reason == "target"
    assert trades[0].exit_price == 102.0
    assert trades[0].pnl > 0


def test_eod_flatten(flat_day):
    trades = run_symbol_day(SignalAtBar(at=2, stop_pct=0.5), "TST", DATE, flat_day, None, CFG)
    assert len(trades) == 1
    assert trades[0].exit_reason == "eod"
    assert trades[0].exit_time == flat_day.index[-1]


def test_dynamic_exit_fills_next_open(flat_day):
    day = flat_day.copy()
    day.loc[day.index[8], "open"] = 100.7
    trades = run_symbol_day(SignalAtBar(at=2, stop_pct=0.5, exit_at=7), "TST", DATE, day, None, CFG)
    assert trades[0].exit_reason == "signal"
    assert trades[0].exit_price == 100.7  # bar 8's open, signalled on bar 7
    assert trades[0].exit_time == day.index[8]


def test_trade_cap_respected(flat_day):
    class AlwaysSignal(SignalAtBar):
        def entry_signal(self, i):
            return self.sig

    strat = AlwaysSignal(at=0, stop_pct=0.5, exit_at=None)
    strat.max_trades_per_day = 5

    class ExitNext(AlwaysSignal):
        def exit_signal(self, i):
            return True

    churner = ExitNext(at=0, stop_pct=0.5)
    churner.max_trades_per_day = 5
    trades = run_symbol_day(churner, "TST", DATE, flat_day, None, CFG)
    assert len(trades) == CFG.max_trades_per_day  # engine cap (3) binds


def test_qty_from_notional(flat_day):
    trades = run_symbol_day(SignalAtBar(at=2, stop_pct=0.5), "TST", DATE, flat_day, None, CFG)
    assert trades[0].qty == int(CFG.notional_per_trade // 100.0)


def test_trailing_stop_ratchets(flat_day):
    day = flat_day.copy()
    # Entry at bar 3 open (100). Bar 4 runs to 110 -> trail (dist 3) lifts the
    # stop to 107. Bar 5 dips to 106.5, which must hit the ratcheted stop.
    day.loc[day.index[4], "high"] = 110.0
    day.loc[day.index[5], "low"] = 106.5
    strat = SignalAtBar(at=2, stop_price=97.0)
    strat.sig = EntrySignal("trail-test", stop_price=97.0, trail_dist=3.0)
    trades = run_symbol_day(strat, "TST", DATE, day, None, CFG)
    assert len(trades) == 1
    assert trades[0].exit_reason == "stop"
    assert trades[0].exit_price == 107.0  # 110 high - 3.0 trail, not the 97 initial stop
    assert trades[0].pnl > 0  # a trailing stop that locks in profit


def test_conditions_recorded(flat_day):
    trades = run_symbol_day(
        SignalAtBar(at=2, stop_pct=0.5), "TST", DATE, flat_day, prior_close=98.0, cfg=CFG
    )
    t = trades[0]
    assert abs(t.mkt_gap_pct - ((100.0 / 98.0 - 1) * 100)) < 0.01
    assert t.weekday == "Mon"  # 2026-08-17
    assert 9.5 <= t.hour_et <= 16.0


def test_ts_conditions_causal_and_sane():
    # Rising first half, crash after bar 10 — the entry at bar 3 must only see the rise.
    import numpy as np
    from conftest import make_day
    from trading_lab.backtest import entry_conditions
    from trading_lab.indicators import session_vwap

    closes = np.concatenate([100 * 1.002 ** np.arange(11), np.full(9, 50.0)])
    day = make_day(closes, closes + 0.2, closes - 0.2, closes)
    vwap = session_vwap(day)

    cond = entry_conditions(day, 3, float(closes[3]), 100.0, vwap, None)
    assert cond["mkt_trend_slope_pct"] > 0  # crash at bar 11 is invisible at bar 3
    assert cond["mkt_realized_vol_pct"] < 0.1  # smooth compounding = near-zero vol
    assert cond["mkt_range_pos"] == 0.8  # entry 100.6 in the 99.8–100.8 day-so-far range
    assert 0 < cond["mkt_atr_pct"] < 2.0

    flat = entry_conditions(day, 3, float(closes[3]), None, vwap, None)
    assert flat["mkt_trend_slope_pct"] == cond["mkt_trend_slope_pct"]


def test_position_size_modes():
    from trading_lab.backtest import position_size

    assert position_size(100.0, 99.0, Config()) == 100  # fixed notional: 10_000 // 100
    cfg = Config(vol_sizing=True, risk_per_trade=100.0)
    assert position_size(100.0, 98.5, cfg) == 66  # $100 risk / $1.50 to the stop
    assert position_size(100.0, 99.99, cfg) == 100  # tight stop capped by notional
    assert position_size(100.0, 101.0, cfg) == 0  # stop above entry: no trade


def test_vol_sizing_uses_atr_stop(flat_day):
    # flat_day bars have a constant true range of 1.0, so ATR(14) == 1.0 and the
    # engine should replace the strategy's 5% stop with entry - 1.5 * ATR.
    cfg = Config(slippage_bps=0.0, vol_sizing=True, risk_per_trade=100.0, stop_atr_mult=1.5)
    day = flat_day.copy()
    day.loc[day.index[5], "low"] = 98.0  # dive through the ATR stop at 98.5
    trades = run_symbol_day(SignalAtBar(at=2, stop_pct=0.05), "TST", DATE, day, None, cfg)
    t = trades[0]
    assert t.qty == 66  # $100 risk / $1.50 stop distance
    assert t.exit_reason == "stop"
    assert abs(t.exit_price - 98.5) < 1e-6  # 100 - 1.5 * ATR(1.0)

    # A structural stop_price is left where the strategy put it.
    trades = run_symbol_day(SignalAtBar(at=2, stop_price=99.9), "TST", DATE, day, None, cfg)
    assert abs(trades[0].exit_price - 99.9) < 1e-6
