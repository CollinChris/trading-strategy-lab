"""Ten-year history study and options study: statistics and no-lookahead."""

import numpy as np
import pandas as pd

from trading_lab import options_study as opt
from trading_lab.history import day_clustered_ci, walk_forward


def test_capm_recovers_alpha_and_beta():
    rng = np.random.default_rng(0)
    mkt = pd.Series(rng.normal(0.007, 0.04, 400))
    strat = 0.002 + 0.6 * mkt + rng.normal(0, 0.005, 400)  # 0.2%/month alpha
    r = opt.capm(strat, mkt)
    assert abs(r["beta"] - 0.6) < 0.03 and abs(r["alpha"] - 0.024) < 0.01 and r["t"] > 3


def test_timed_putwrite_has_no_lookahead():
    idx = pd.date_range("2000-01-31", periods=120, freq="ME")
    rng = np.random.default_rng(1)
    put = pd.Series(rng.normal(0.006, 0.03, 120), index=idx)
    rf = pd.Series(0.001, index=idx)
    sig = pd.Series(rng.normal(3, 2, 120), index=idx)
    base = opt.timed_putwrite(put, rf, sig, min_history=24)
    shocked = sig.copy()
    shocked.iloc[90:] = -50.0  # change only the future
    assert base.iloc[:91].equals(opt.timed_putwrite(put, rf, shocked, min_history=24).iloc[:91])
    held = base.dropna()
    assert set(np.round(held.where(held != rf.reindex(held.index)).dropna(), 12)) <= set(
        np.round(put, 12)
    )


def test_sparse_prefix_is_trimmed(tmp_path, monkeypatch):
    monkeypatch.setattr(opt, "CACHE", tmp_path)
    dates = [
        *pd.date_range("1995-01-02", periods=5, freq="180D"),
        *pd.bdate_range("2007-01-02", periods=300),
    ]
    lines = ["DATE,PUT", *[f"{d:%m/%d/%Y},{100 + k}" for k, d in enumerate(dates)]]
    (tmp_path / "PUT.csv").write_text("\n".join(lines))
    s = opt.load_cboe("PUT", max_age_days=10_000)
    assert s.index[0] >= pd.Timestamp("2006-12-01") and len(s) == 300


def test_day_clustered_ci_and_walk_forward():
    # Deterministic noise so the true means are known exactly.
    rows = []
    for year in (2018, 2019, 2020, 2021):
        for d, day in enumerate(pd.bdate_range(f"{year}-01-02", periods=60)):
            noise = 10.0 if d % 2 else -10.0  # whole days up or down: true mean exactly 0
            for params, edge in (("default", 0.0), ('{"a": 1}', 5.0 if year < 2021 else -5.0)):
                for _ in range(3):
                    rows.append(
                        {
                            "strategy": "orb",
                            "params": params,
                            "date": day,
                            "year": year,
                            "pnl_vs_spy": edge + noise,
                        }
                    )
    t = pd.DataFrame(rows)
    lo, hi = day_clustered_ci(t[t["params"] == "default"])
    assert lo < 0 < hi  # zero-mean strategy: no edge
    lo, hi = day_clustered_ci(t[(t["params"] != "default") & (t["year"] < 2021)])
    assert lo > 0  # a real +5 edge is detected
    wf = walk_forward(t)
    assert list(wf["year"]) == [2020, 2021] and (wf["picked"] == '{"a": 1}').all()
    # 2021 is a regime change: the pick, chosen on 2019-2020, loses out of sample.
    y21 = wf[wf["year"] == 2021].iloc[0]
    assert y21["tuned_sum"] / y21["tuned_n"] < y21["default_sum"] / y21["default_n"]
