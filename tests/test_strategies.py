from conftest import make_day

from trading_lab.strategies import GapAndGo, OpeningRangeBreakout, RsiReversion


def breakout_day():
    """15m opening range 100-101, clean breakout close at bar 4."""
    opens = [100.5, 100.6, 100.4, 100.8, 101.2, 101.6]
    highs = [101.0, 100.9, 100.8, 101.1, 101.8, 102.0]
    lows = [100.0, 100.2, 100.1, 100.5, 101.0, 101.4]
    closes = [100.6, 100.5, 100.6, 100.9, 101.7, 101.9]
    return make_day(opens, highs, lows, closes)


def test_orb_fires_only_after_breakout():
    day = breakout_day()
    strat = OpeningRangeBreakout()
    strat.new_day(day, prior_close=None)
    assert strat.entry_signal(3) is None  # close 100.9 still inside the range
    sig = strat.entry_signal(4)  # close 101.7 > OR high 101.0
    assert sig is not None
    assert sig.stop_price == 100.0  # OR low
    assert sig.target_r == 2.0


def test_orb_ignores_bars_inside_range_window():
    day = breakout_day()
    strat = OpeningRangeBreakout()
    strat.new_day(day, prior_close=None)
    assert strat.entry_signal(1) is None  # opening range still forming


def test_gap_and_go_requires_gap():
    day = breakout_day()
    strat = GapAndGo(min_gap_pct=2.0)
    strat.new_day(day, prior_close=100.4)  # open 100.5 => +0.1% gap: inactive
    assert strat.entry_signal(4) is None
    strat.new_day(day, prior_close=95.0)  # open 100.5 => +5.8% gap: active
    day.loc[day.index[4], "volume"] = 5000  # breakout bar needs above-average volume
    sig = strat.entry_signal(4)
    assert sig is not None
    assert sig.stop_price == 100.0  # opening bar low


def test_rsi_reversion_buys_dip_above_vwap():
    # A long steady climb leaves VWAP well below price; then a sharp two-bar
    # dip drives Wilder RSI(2) under 10 while price still holds above VWAP.
    closes = [100 + 0.5 * k for k in range(30)] + [112.5, 110.5]
    opens = [c - 0.2 for c in closes]
    highs = [c + 0.4 for c in closes]
    lows = [c - 0.4 for c in closes]
    day = make_day(opens, highs, lows, closes)
    strat = RsiReversion()
    strat.new_day(day, prior_close=None)
    assert strat.entry_signal(29) is None  # no dip yet
    sig = strat.entry_signal(31)
    assert sig is not None
    assert sig.stop_pct == 0.01
