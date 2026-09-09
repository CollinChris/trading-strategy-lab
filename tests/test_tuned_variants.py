"""Tuned-variant plumbing: registry overrides, dedup, JSON roundtrip."""

from pathlib import Path

from trading_lab.strategies import RsiReversion, all_strategies


def test_tuned_variant_added_with_params():
    tuned = {"rsi2_reversion": {"entry_level": 15.0, "exit_level": 70.0, "stop_pct": 0.005}}
    strats = all_strategies(tuned=tuned)
    assert len(strats) == 10  # nine defaults + one variant
    variant = strats[-1]
    assert variant.name == "rsi2_reversion_tuned"
    assert isinstance(variant, RsiReversion)
    assert variant.entry_level == 15.0 and variant.stop_pct == 0.005
    assert RsiReversion().name == "rsi2_reversion"  # class attribute untouched


def test_tuned_equal_to_defaults_skipped():
    tuned = {"rsi2_reversion": {"entry_level": 10.0, "exit_level": 60.0, "stop_pct": 0.01}}
    assert len(all_strategies(tuned=tuned)) == 9  # would duplicate the base instance


def test_unknown_strategy_ignored():
    assert len(all_strategies(tuned={"no_such": {"x": 1}})) == 9


def test_json_roundtrip(tmp_path, monkeypatch):
    from trading_lab import paper
    from trading_lab.tune import _write_tuned_params

    _write_tuned_params(
        {"orb": {"params": {"range_bars": 6, "target_r": 1.5, "stop_at_mid": False},
                 "train_expectancy": 5.95, "test_expectancy": 3.56}},
        tmp_path,
    )
    monkeypatch.setattr(paper, "TUNED_PATH", tmp_path / "tuned_params.json")
    assert paper._load_tuned() == {"orb": {"range_bars": 6, "target_r": 1.5, "stop_at_mid": False}}
    monkeypatch.setattr(paper, "TUNED_PATH", tmp_path / "missing.json")
    assert paper._load_tuned() == {}
