"""Short-side mechanics: engine fills/stops/targets/trailing and strategy mirrors."""

import datetime as dt

from conftest import make_day

from trading_lab.backtest import position_size, run_symbol_day
from trading_lab.config import Config
from trading_lab.strategies import OpeningRangeBreakout, RsiReversion
from trading_lab.strategies.base import EntrySignal, Strategy

CFG = Config(slippage_bps=0.0)
DATE = dt.date(2026, 8, 17)


class ShortAtBar(Strategy):
    name = "short_stub"
    max_trades_per_day = 5

    def __init__(self, at, **sig_kwargs):
        self.at = at
        self.sig = EntrySignal("test-short", side="short", **sig_kwargs)

    def entry_signal(self, i):
        return self.sig if i == self.at else None


def flat20():
    n = 20
    return make_day([100] * n, [100.5] * n, [99.5] * n, [100] * n)


def test_short_entry_and_eod_pnl_sign():
    day = flat20().copy()
    day.loc[day.index[3], "open"] = 101.0  # short entry fills here
    day.iloc[10:, day.columns.get_loc("close")] = 98.0
    day.iloc[10:, day.columns.get_loc("low")] = 97.5
    day.iloc[10:, day.columns.get_loc("high")] = 98.5
    day.iloc[10:, day.columns.get_loc("open")] = 98.0
    trades = run_symbol_day(ShortAtBar(at=2, stop_pct=0.05), "TST", DATE, day, None, CFG)
    t = trades[0]
    assert t.side == "short"
    assert t.entry_price == 101.0
    assert t.exit_reason == "eod"
    assert t.pnl > 0  # price fell, short profits


def test_short_stop_above_entry_hit():
    day = flat20().copy()
    day.loc[day.index[5], "high"] = 103.0  # squeeze through the stop
    trades = run_symbol_day(ShortAtBar(at=2, stop_price=101.5), "TST", DATE, day, None, CFG)
    t = trades[0]
    assert t.exit_reason == "stop"
    assert t.exit_price == 101.5
    assert t.pnl < 0


def test_short_target_below_entry_hit():
    day = flat20().copy()
    day.loc[day.index[6], "low"] = 96.0  # entry 100, stop 102 -> 2R target 96
    trades = run_symbol_day(
        ShortAtBar(at=2, stop_price=102.0, target_r=2.0), "TST", DATE, day, None, CFG
    )
    t = trades[0]
    assert t.exit_reason == "target"
    assert t.exit_price == 96.0
    assert t.pnl > 0


def test_short_trailing_stop_ratchets_down():
    day = flat20().copy()
    # Entry 100 at bar 3. Bar 4 dives to 90 -> trail (dist 3) drops stop to 93.
    # Bar 5 pops to 93.5, hitting the ratcheted stop for a profit.
    day.loc[day.index[4], "low"] = 90.0
    day.loc[day.index[5], "high"] = 93.5
    trades = run_symbol_day(
        ShortAtBar(at=2, stop_price=105.0, trail_dist=3.0), "TST", DATE, day, None, CFG
    )
    t = trades[0]
    assert t.exit_reason == "stop"
    assert t.exit_price == 93.0
    assert t.pnl > 0


def test_short_gap_through_stop_skipped():
    day = flat20().copy()
    trades = run_symbol_day(ShortAtBar(at=2, stop_price=99.0), "TST", DATE, day, None, CFG)
    assert trades == []  # stop below a short entry is invalid


def test_position_size_short_risk():
    cfg = Config(vol_sizing=True, risk_per_trade=100.0)
    assert position_size(100.0, 101.5, cfg) == 66  # $100 / $1.50 risk, stop above


def test_orb_short_signal():
    n = 12
    closes = [100, 100, 100, 97, 97, 97, 97, 97, 97, 97, 97, 97]
    day = make_day(closes, [c + 0.5 for c in closes], [c - 0.5 for c in closes], closes)
    strat = OpeningRangeBreakout(range_bars=3)
    strat.new_day(day, None)
    sig = strat.entry_signal(3)
    assert sig is not None and sig.side == "short"
    assert sig.stop_price == strat.or_high


def test_rsi2_short_on_rip_below_vwap():
    # Grind down (keeps price below VWAP), then an up bar rips RSI(2) overbought
    # while price is still under VWAP — the short-the-pop mirror. entry_level=15
    # => short threshold RSI(2) > 85.
    closes = [100 - 0.5 * k for k in range(10)] + [96.5, 97.6]
    day = make_day(closes, [c + 0.1 for c in closes], [c - 0.1 for c in closes], closes)
    strat = RsiReversion(entry_level=15.0)
    strat.new_day(day, None)
    sig = strat.entry_signal(len(closes) - 1)
    assert sig is not None and sig.side == "short"
    assert not strat.exit_signal(len(closes) - 1)  # still overbought
