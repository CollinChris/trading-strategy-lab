"""Live plumbing for the regime filter: variant naming, one-signal scoring,
model save/load, and the scanner's keep/skip decision."""

from __future__ import annotations

import numpy as np
import pandas as pd
from test_regime import synthetic_trades

from trading_lab import paper
from trading_lab.regime import RegimeFilter, base_name, load_filter, save_filter


def test_base_name_strips_both_variant_suffixes():
    s = pd.Series(["orb", "orb_tuned", "orb_regime", "high_break_trail", "ar_forecast_regime"])
    assert base_name(s).tolist() == ["orb", "orb", "orb", "high_break_trail", "ar_forecast"]


def test_score_signal_matches_batch_scoring_and_handles_missing_features():
    trades = synthetic_trades(n_sessions=20, per_session=25, planted=True)
    flt = RegimeFilter.fit(trades, "hgb_reg")
    row = trades.iloc[0]
    conditions = {k: row[k] for k in trades.columns if k.startswith("mkt_")}
    conditions.update(hour_et=row["hour_et"], weekday=row["weekday"])
    single = flt.score_signal(row["strategy"], row["side"], conditions)
    batch = float(flt.expected_value(trades.iloc[[0]])[0])
    assert single == batch
    # A `_regime` variant scores exactly like its base strategy.
    assert flt.score_signal(row["strategy"] + "_regime", row["side"], conditions) == single
    # Live conditions can be partial (e.g. SPY unavailable): still a finite number.
    partial = {"mkt_gap_pct": 0.5, "hour_et": 10.0, "weekday": "Mon"}
    assert np.isfinite(flt.score_signal("orb", "long", partial))


def test_planted_regime_scores_aligned_signals_higher():
    trades = synthetic_trades(n_sessions=30, per_session=30, planted=True)
    flt = RegimeFilter.fit(trades, "hgb_reg")
    base = {k: 0.0 for k in trades.columns if k.startswith("mkt_")}
    base.update(hour_et=10.5, weekday="Tue")
    green = {**base, "mkt_spy_change_pct": 1.5}
    red = {**base, "mkt_spy_change_pct": -1.5}
    assert flt.score_signal("orb", "long", green) > flt.score_signal("orb", "long", red)
    assert flt.score_signal("orb", "short", red) > flt.score_signal("orb", "short", green)


def test_save_load_roundtrip_and_missing_file(tmp_path, monkeypatch):
    trades = synthetic_trades(n_sessions=20, per_session=20, planted=True)
    flt = RegimeFilter.fit(trades, "ridge")
    path = tmp_path / "regime_model.joblib"
    save_filter(flt, {"kind": "ridge", "generated": "2026-09-11", "sessions": 20}, path)
    loaded = load_filter(path)
    assert loaded is not None
    flt2, meta = loaded
    assert meta["kind"] == "ridge" and meta["sessions"] == 20
    assert np.allclose(flt2.expected_value(trades), flt.expected_value(trades))
    assert load_filter(tmp_path / "missing.joblib") is None
    # The scanner's loader goes through the same path constant.
    monkeypatch.setattr("trading_lab.regime.MODEL_PATH", tmp_path / "missing.joblib")
    assert paper._load_regime() is None
