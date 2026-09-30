"""Survivor gate (tune promotion), long gate (paper), side-policy books (regime)."""

import pandas as pd

from trading_lab.config import Config
from trading_lab.paper import _long_gated
from trading_lab.regime import side_policies
from trading_lab.tune import promote

ORB = {"params": {"range_bars": 6}, "train_expectancy": 1.0, "test_expectancy": 2.0}


def _history(tmp_path, rows):
    path = tmp_path / "tuning_history.csv"
    pd.DataFrame(
        rows,
        columns=[
            "run_date",
            "strategy",
            "best_params",
            "test_expectancy",
            "default_test_expectancy",
        ],
    ).to_csv(path, index=False)
    return path


def test_promotes_stable_winner(tmp_path):
    rows = [
        (f"2026-09-{d}", "Opening Range Breakout", "{'range_bars': 6}", 5.0, 1.0)
        for d in (12, 19, 26)
    ]
    promoted, held = promote({"orb": ORB}, _history(tmp_path, rows))
    assert "orb" in promoted and not held


def test_holds_when_params_churn(tmp_path):
    rows = [
        ("2026-09-12", "Opening Range Breakout", "{'range_bars': 3}", 5.0, 1.0),
        ("2026-09-19", "Opening Range Breakout", "{'range_bars': 6}", 5.0, 1.0),
        ("2026-09-26", "Opening Range Breakout", "{'range_bars': 6}", 5.0, 1.0),
    ]
    promoted, held = promote({"orb": ORB}, _history(tmp_path, rows))
    assert not promoted and "changed" in held["orb"]


def test_holds_when_one_week_loses_to_defaults(tmp_path):
    rows = [
        ("2026-09-12", "Opening Range Breakout", "{'range_bars': 6}", 5.0, 1.0),
        ("2026-09-19", "Opening Range Breakout", "{'range_bars': 6}", 0.5, 1.0),
        ("2026-09-26", "Opening Range Breakout", "{'range_bars': 6}", 5.0, 1.0),
    ]
    _, held = promote({"orb": ORB}, _history(tmp_path, rows))
    assert "beat the defaults" in held["orb"]


def test_holds_with_too_little_history(tmp_path):
    rows = [("2026-09-26", "Opening Range Breakout", "{'range_bars': 6}", 5.0, 1.0)]
    _, held = promote({"orb": ORB}, _history(tmp_path, rows))
    assert "1 of 3" in held["orb"]
    _, held = promote({"orb": ORB}, tmp_path / "missing.csv")
    assert "0 of 3" in held["orb"]


def test_long_gate_rules():
    cfg = Config()  # long_gate="regime", orb exempt
    assert _long_gated(cfg, "vwap_pullback", "long", True)
    assert _long_gated(cfg, "vwap_pullback_tuned", "long", True)
    assert not _long_gated(cfg, "vwap_pullback", "short", True)  # shorts never gated
    assert not _long_gated(cfg, "orb", "long", True)  # ORB untouched
    assert not _long_gated(cfg, "orb_tuned", "long", True)
    assert not _long_gated(cfg, "vwap_pullback", "long", False)  # no filter: fail open
    assert not _long_gated(Config(long_gate="none"), "vwap_pullback", "long", True)


def test_side_policy_books():
    scored = pd.DataFrame(
        {
            "strategy": ["orb", "vwap_pullback", "vwap_pullback", "rsi2_reversion"],
            "side": ["long", "long", "short", "long"],
            "keep": [False, True, False, False],
            "pnl": [10.0, 20.0, -5.0, -40.0],
        }
    )
    t = side_policies(scored, ("orb",), n_random=50).set_index("book")
    assert t.loc["Long only (unfiltered)", "trades"] == 3
    assert t.loc["Short only (unfiltered)", "trades"] == 1
    live = next(b for b in t.index if b.startswith("Live policy"))
    # ORB long (exempt) + filtered vwap long + the short; the rejected rsi2 long is dropped.
    assert t.loc[live, "trades"] == 3
    assert t.loc[live, "P&L"] == "$+25.00"
