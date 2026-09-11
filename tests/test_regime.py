"""Regime-filter tests: fold hygiene, the EV rule, and two end-to-end checks —
a planted regime the filter must find, and pure noise it must not claim."""

from __future__ import annotations

import datetime as dt

import numpy as np
import pandas as pd
import pytest

from trading_lab.regime import (
    KINDS,
    ExpectedValue,
    RegimeFilter,
    build_features,
    quintile_table,
    random_baseline,
    walk_forward,
    walk_forward_folds,
)

FEATURES = [
    "mkt_gap_pct",
    "mkt_change_open_pct",
    "mkt_dist_vwap_pct",
    "mkt_rel_volume",
    "mkt_spy_change_pct",
    "mkt_realized_vol_pct",
    "mkt_trend_slope_pct",
    "mkt_autocorr_1",
    "mkt_atr_pct",
    "mkt_range_pos",
]


def synthetic_trades(
    n_sessions: int, per_session: int, planted: bool, seed: int = 0
) -> pd.DataFrame:
    """Sessions of random trades across three strategies. When `planted`, P&L
    is driven by a hidden regime — longs pay when SPY is green, shorts when
    it is red — plus noise. Otherwise P&L is noise with a slightly negative
    drift, like the real book."""
    rng = np.random.default_rng(seed)
    start = dt.date(2026, 6, 1)
    rows = []
    for s in range(n_sessions):
        date = start + dt.timedelta(days=s)
        for _ in range(per_session):
            side = rng.choice(["long", "short"])
            feats = {f: float(rng.normal()) for f in FEATURES}
            direction = 1.0 if side == "long" else -1.0
            noise = rng.normal(0, 40)
            pnl = 60.0 * direction * feats["mkt_spy_change_pct"] + noise if planted else noise - 8.0
            hour = float(rng.uniform(9.5, 15.5))
            rows.append(
                {
                    "strategy": rng.choice(["orb", "rsi2_reversion", "ar_forecast"]),
                    "symbol": "TEST",
                    "date": date,
                    "entry_time": pd.Timestamp(f"{date} 10:00", tz="America/New_York"),
                    "exit_time": pd.Timestamp(f"{date} 11:00", tz="America/New_York"),
                    "side": side,
                    "pnl": round(float(pnl), 2),
                    "hour_et": hour,
                    "weekday": ["Mon", "Tue", "Wed", "Thu", "Fri"][s % 5],
                    **feats,
                }
            )
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ folds


def test_folds_are_chronological_and_disjoint():
    dates = [dt.date(2026, 1, 1) + dt.timedelta(days=i) for i in range(23)]
    folds = walk_forward_folds(dates, min_train=10, block=5)
    assert [len(f.test) for f in folds] == [5, 5, 3]  # last block is the remainder
    for f in folds:
        assert max(f.train) < min(f.test)  # nothing in test precedes training
        assert not (f.train & f.test)
    # Expanding window: each fold trains on everything before its block.
    assert [len(f.train) for f in folds] == [10, 15, 20]
    # Every date after min_train is tested exactly once.
    tested = sorted(d for f in folds for d in f.test)
    assert tested == dates[10:]


def test_folds_reject_bad_arguments_and_short_histories():
    dates = [dt.date(2026, 1, 1) + dt.timedelta(days=i) for i in range(5)]
    with pytest.raises(ValueError):
        walk_forward_folds(dates, min_train=0, block=5)
    assert walk_forward_folds(dates, min_train=5, block=5) == []


# ------------------------------------------------------------------ features & EV rule


def test_features_are_direction_signed_and_strategy_one_hot():
    trades = synthetic_trades(2, 4, planted=False)
    trades.loc[0, ["side", "mkt_spy_change_pct", "strategy"]] = ["short", 0.5, "orb"]
    trades.loc[1, ["side", "mkt_spy_change_pct", "strategy"]] = ["long", 0.5, "orb_tuned"]
    x = build_features(trades)
    assert x.loc[0, "aligned_spy_pct"] == -0.5 and x.loc[0, "is_short"] == 1.0
    assert x.loc[1, "aligned_spy_pct"] == 0.5 and x.loc[1, "is_short"] == 0.0
    # `_tuned` variants share their base strategy's identity.
    assert x.loc[0, "strat_orb"] == 1.0 and x.loc[1, "strat_orb"] == 1.0
    assert x.filter(like="strat_").sum(axis=1).eq(1.0).all()


def test_expected_value_rule_uses_training_averages():
    trades = pd.DataFrame(
        {
            "strategy": ["orb"] * 10,
            "pnl": [100.0] * 5 + [-50.0] * 5,
        }
    )
    ev = ExpectedValue.from_trades(trades)
    strat = pd.Series(["orb", "orb", "unknown"])
    got = ev.ev(strat, np.array([0.5, 0.2, 0.5]))
    # 0.5*100 + 0.5*(-50) = 25 ; 0.2*100 + 0.8*(-50) = -20 ; unknown → pooled = 25
    assert got == pytest.approx([25.0, -20.0, 25.0])


def test_random_baseline_shape_and_edge_cases():
    pnl = np.arange(10, dtype=float)
    draws = random_baseline(pnl, n_keep=4, n_draws=50)
    assert draws.shape == (50,) and draws.min() >= 1.5 and draws.max() <= 7.5
    assert random_baseline(pnl, n_keep=0, n_draws=50).size == 0
    assert random_baseline(pnl, n_keep=11, n_draws=50).size == 0


# ------------------------------------------------------------------ end to end


@pytest.mark.parametrize("kind", sorted(KINDS))
def test_filter_finds_a_planted_regime_out_of_sample(kind):
    trades = synthetic_trades(n_sessions=40, per_session=30, planted=True)
    res = walk_forward(trades, kind=kind, min_train=15, block=5, n_random=100)
    o = res.overall
    # Unfiltered, the planted book is ~breakeven; the kept subset must be clearly
    # positive and far above what same-size random selection produces.
    assert o["exp_kept"] > 10.0 > o["exp_all"] - 5.0
    assert o["random_pctile"] >= 95
    assert 0 < o["kept"] < o["trades"]
    # Only sessions after min_train are ever scored.
    scored_dates = sorted(res.scored["date"].unique())
    assert len(scored_dates) == 25 and scored_dates[0] > sorted(trades["date"].unique())[14]


def test_filter_does_not_manufacture_an_edge_from_noise():
    trades = synthetic_trades(n_sessions=40, per_session=30, planted=False, seed=3)
    res = walk_forward(trades, kind="hgb_reg", min_train=15, block=5, n_random=100)
    o = res.overall
    # With no regime to learn, the kept subset's expectancy should stay near the
    # random-selection distribution — not sit far in its upper tail.
    assert o["random_pctile"] < 99
    assert abs(o["exp_kept"] - o["random_exp_mean"]) < 15.0


def test_fitted_filter_keeps_only_positive_ev_and_quintiles_cover_all_trades():
    trades = synthetic_trades(n_sessions=20, per_session=25, planted=True)
    flt = RegimeFilter.fit(trades, "ridge")
    ev = flt.expected_value(trades)
    assert (flt.keep(trades) == (ev > 0)).all()
    assert np.isnan(flt.p_win(trades)).all()  # regressors don't estimate P(win)
    clf = RegimeFilter.fit(trades, "logit")
    assert ((clf.p_win(trades) >= 0) & (clf.p_win(trades) <= 1)).all()
    scored = trades.assign(ev=ev)
    table = quintile_table(scored)
    assert table["trades"].sum() == len(trades) and len(table) == 5
