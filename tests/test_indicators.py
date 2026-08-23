import pandas as pd
from conftest import make_day

from trading_lab.indicators import ema, rsi, session_vwap


def test_rsi_extremes():
    up = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
    down = pd.Series([5.0, 4.0, 3.0, 2.0, 1.0])
    assert rsi(up, 2).iloc[-1] == 100.0
    assert rsi(down, 2).iloc[-1] == 0.0
    flat = pd.Series([3.0] * 5)
    assert rsi(flat, 2).iloc[-1] == 50.0


def test_rsi_bounded():
    prices = pd.Series([10, 11, 10.5, 12, 11.8, 12.5, 11.9, 13.0])
    values = rsi(prices, 2)
    assert ((values >= 0) & (values <= 100)).all()


def test_vwap_manual():
    day = make_day(
        opens=[10, 20], highs=[10, 20], lows=[10, 20], closes=[10, 20], volumes=[100, 300]
    )
    vwap = session_vwap(day)
    assert vwap.iloc[0] == 10.0
    # (10*100 + 20*300) / 400 = 17.5
    assert vwap.iloc[1] == 17.5


def test_ema_is_causal():
    a = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
    b = a.copy()
    b.iloc[-1] = 500.0  # changing the future must not change the past
    assert (ema(a, 3).iloc[:-1] == ema(b, 3).iloc[:-1]).all()
