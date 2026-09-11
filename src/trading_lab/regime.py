"""Regime filters learned from the trade journal, validated walk-forward.

The question this module answers is the one v0.2's tuning left open: every
strategy bled in the held-out month regardless of parameters, so the lever to
test is *when* to trade, not *how* to exit. Each trade in results/trades.csv
carries a market-condition snapshot taken at entry (gap, VWAP distance,
relative volume, SPY move, realized vol, trend slope, ...). A model scores each
trade's expected value from those conditions (plus strategy and side) and the
trade is kept only when that expected value is positive. Two families are
compared: classifiers of P(win), converted to dollars with the training fold's
per-strategy average win/loss; and regressors of P&L directly. (The first run
showed why both matter: P(win) was mildly predictable out of sample, yet the
highest-P(win) trades had the *worst* expectancy — the v0.1 win-rate trap,
rediscovered by a model.)

Honesty rules, in code rather than in prose:

- **Walk-forward, never one split.** Sessions are sorted; the model is trained
  on all sessions before a block and scored on that block only, block by
  block. Every out-of-sample number below is a concatenation of those blocks.
  Nothing is ever scored by a model that saw its session.
- **Random-selection baseline.** Keeping N trades at random out of M also
  changes expectancy by chance. The filter's out-of-sample expectancy is
  compared against many random subsets of the same size; the percentile is
  reported. A filter that isn't clearly above that distribution learned
  nothing.
- **Descriptive rules are labelled in-sample.** The depth-2 decision tree per
  strategy exists to make the model's opinion readable, not to prove it.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from .data import market_today
from .report import BASELINE, GRID, INK, INK_2, MUTED, STRATEGIES, SURFACE, _md_table

# Raw journal columns used as features. All are computed at the entry bar from
# bars 0..i of the session (see backtest.entry_conditions) — no lookahead.
RAW_FEATURES = [
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
    "hour_et",
]
# Direction-signed copies: a short in a falling SPY and a long in a rising SPY
# are the same regime for a pooled model, so the sign is folded in.
SIGNED_FEATURES = {
    "aligned_spy_pct": "mkt_spy_change_pct",
    "aligned_change_open_pct": "mkt_change_open_pct",
    "aligned_dist_vwap_pct": "mkt_dist_vwap_pct",
    "aligned_trend_slope_pct": "mkt_trend_slope_pct",
    "aligned_range_pos": "mkt_range_pos",
}
WEEKDAYS = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4}
MIN_FOLD_TRADES = 10  # per-strategy OOS cells with fewer trades are shown but flagged
MODEL_PATH = Path("results/regime_model.joblib")  # the live filter the paper scanner loads
VARIANT_SUFFIXES = ("_tuned", "_regime")


def base_name(strategy: pd.Series) -> pd.Series:
    """`orb_tuned` and `orb_regime` are still ORB to the model — variants share
    their base strategy's identity and its average win/loss."""
    return strategy.str.replace(r"_(tuned|regime)$", "", regex=True)


@dataclass(frozen=True)
class Fold:
    train: frozenset[dt.date]
    test: frozenset[dt.date]


def walk_forward_folds(dates: list[dt.date], min_train: int, block: int) -> list[Fold]:
    """Expanding-window folds over sorted session dates: train on everything
    before a block of `block` sessions, test on that block. The first
    `min_train` sessions are never tested (nothing precedes them to learn from)."""
    dates = sorted(set(dates))
    if min_train < 1 or block < 1:
        raise ValueError("min_train and block must be positive")
    folds = []
    start = min_train
    while start < len(dates):
        test = dates[start : start + block]
        folds.append(Fold(frozenset(dates[:start]), frozenset(test)))
        start += block
    return folds


# --------------------------------------------------------------------------- features


def build_features(trades: pd.DataFrame) -> pd.DataFrame:
    """Model matrix from a trades table. Strategy is one-hot so a pooled model
    can hold a per-strategy baseline while sharing regime knowledge."""
    base = base_name(trades["strategy"])
    direction = np.where(trades["side"].eq("short"), -1.0, 1.0)
    out = pd.DataFrame(index=trades.index)
    for col in RAW_FEATURES:
        out[col] = pd.to_numeric(trades.get(col), errors="coerce")
    for name, src in SIGNED_FEATURES.items():
        out[name] = out[src] * direction
    out["is_short"] = (direction < 0).astype(float)
    out["weekday_num"] = trades["weekday"].map(WEEKDAYS).astype(float)
    for key in STRATEGIES:
        out[f"strat_{key}"] = (base == key).astype(float)
    return out


KINDS = {
    "hgb": "Gradient boosting → P(win) → EV",
    "logit": "Logistic regression → P(win) → EV",
    "hgb_reg": "Gradient boosting → P&L directly",
    "ridge": "Ridge regression → P&L directly",
}
REGRESSORS = {"hgb_reg", "ridge"}


def _make_model(kind: str):
    if kind == "hgb_reg":
        return HistGradientBoostingRegressor(
            loss="absolute_error",  # heavy-tailed P&L: don't let one $500 print steer the fit
            max_depth=3,
            learning_rate=0.05,
            max_iter=150,
            min_samples_leaf=30,
            l2_regularization=1.0,
            random_state=0,
        )
    if kind == "ridge":
        return Pipeline([("scale", StandardScaler()), ("reg", Ridge(alpha=10.0))])
    if kind == "hgb":
        return HistGradientBoostingClassifier(
            max_depth=3,
            learning_rate=0.05,
            max_iter=150,
            min_samples_leaf=30,
            l2_regularization=1.0,
            random_state=0,
        )
    if kind == "logit":
        return Pipeline(
            [
                ("scale", StandardScaler()),
                ("clf", LogisticRegression(C=0.3, max_iter=2000)),
            ]
        )
    raise ValueError(f"unknown model kind {kind!r}")


def _fill(x: pd.DataFrame, medians: pd.Series | None = None) -> tuple[pd.DataFrame, pd.Series]:
    """Median-impute (from the training fold) — the logistic pipeline can't take NaN."""
    medians = x.median(numeric_only=True).fillna(0.0) if medians is None else medians
    return x.fillna(medians).fillna(0.0), medians


@dataclass
class ExpectedValue:
    """Per-strategy average win/loss from the training fold; pooled fallback."""

    avg_win: dict[str, float]
    avg_loss: dict[str, float]
    pooled_win: float
    pooled_loss: float

    @classmethod
    def from_trades(cls, trades: pd.DataFrame) -> ExpectedValue:
        base = base_name(trades["strategy"])
        pnl = trades["pnl"]
        wins, losses = pnl[pnl > 0], pnl[pnl <= 0]
        pooled_win = float(wins.mean()) if len(wins) else 0.0
        pooled_loss = float(losses.mean()) if len(losses) else 0.0
        avg_win, avg_loss = {}, {}
        for name, grp in pnl.groupby(base):
            w, l = grp[grp > 0], grp[grp <= 0]
            avg_win[name] = float(w.mean()) if len(w) >= 5 else pooled_win
            avg_loss[name] = float(l.mean()) if len(l) >= 5 else pooled_loss
        return cls(avg_win, avg_loss, pooled_win, pooled_loss)

    def ev(self, strategy: pd.Series, p_win: np.ndarray) -> np.ndarray:
        base = base_name(strategy)
        w = base.map(self.avg_win).fillna(self.pooled_win).to_numpy()
        l = base.map(self.avg_loss).fillna(self.pooled_loss).to_numpy()
        return p_win * w + (1.0 - p_win) * l


# --------------------------------------------------------------------------- fitted filter


@dataclass
class RegimeFilter:
    """A fitted P(win) model plus the EV rule. `keep()` is the only decision
    the rest of the lab needs: trade this signal, or stand aside."""

    kind: str
    model: object
    medians: pd.Series
    columns: list[str]
    ev: ExpectedValue

    @classmethod
    def fit(cls, trades: pd.DataFrame, kind: str = "hgb") -> RegimeFilter:
        if kind not in KINDS:
            raise ValueError(f"unknown model kind {kind!r}; choose from {sorted(KINDS)}")
        x = build_features(trades)
        x, medians = _fill(x)
        if kind in REGRESSORS:
            y = trades["pnl"].to_numpy(dtype=float)
        else:
            y = (trades["pnl"] > 0).astype(int).to_numpy()
        model = _make_model(kind)
        model.fit(x, y)
        return cls(kind, model, medians, list(x.columns), ExpectedValue.from_trades(trades))

    def _matrix(self, trades: pd.DataFrame) -> pd.DataFrame:
        x, _ = _fill(build_features(trades)[self.columns], self.medians)
        return x

    def p_win(self, trades: pd.DataFrame) -> np.ndarray:
        """P(win) for the classifier kinds; NaN for regressors (they never estimate it)."""
        if self.kind in REGRESSORS:
            return np.full(len(trades), np.nan)
        return self.model.predict_proba(self._matrix(trades))[:, 1]

    def expected_value(self, trades: pd.DataFrame) -> np.ndarray:
        return self._ev_from_matrix(trades["strategy"], self._matrix(trades))

    def _ev_from_matrix(self, strategy: pd.Series, x: pd.DataFrame) -> np.ndarray:
        if self.kind in REGRESSORS:
            return np.asarray(self.model.predict(x), dtype=float)
        return self.ev.ev(strategy, self.model.predict_proba(x)[:, 1])

    def keep(self, trades: pd.DataFrame) -> np.ndarray:
        return self.expected_value(trades) > 0.0

    def score_signal(self, strategy: str, side: str, conditions: dict) -> float:
        """Predicted EV ($) for one live signal, from the same condition dict the
        backtest and journal record. Missing features are median-imputed."""
        row = {"strategy": strategy, "side": side, "weekday": conditions.get("weekday", "")}
        row.update({k: conditions.get(k, float("nan")) for k in RAW_FEATURES})
        return float(self.expected_value(pd.DataFrame([row]))[0])


def save_filter(flt: RegimeFilter, meta: dict, path: Path = MODEL_PATH) -> None:
    """Persist the live filter with its provenance (what data, which kind, when)."""
    path.parent.mkdir(exist_ok=True)
    joblib.dump({"filter": flt, "meta": meta}, path)


def load_filter(path: Path = MODEL_PATH) -> tuple[RegimeFilter, dict] | None:
    """The saved filter, or None when there isn't one (paper trades unfiltered then)."""
    try:
        payload = joblib.load(path)
        return payload["filter"], payload["meta"]
    except (OSError, KeyError, ValueError, EOFError, AttributeError, ImportError, TypeError):
        return None


# --------------------------------------------------------------------------- evaluation


def _stats(pnl: pd.Series) -> dict:
    if len(pnl) == 0:
        return {"trades": 0, "expectancy": float("nan"), "profit_factor": float("nan"), "pnl": 0.0}
    wins, losses = pnl[pnl > 0], pnl[pnl <= 0]
    pf = float(wins.sum() / abs(losses.sum())) if losses.sum() != 0 else float("inf")
    return {
        "trades": len(pnl),
        "expectancy": float(pnl.mean()),
        "profit_factor": pf,
        "pnl": float(pnl.sum()),
    }


def random_baseline(pnl: np.ndarray, n_keep: int, n_draws: int, seed: int = 0) -> np.ndarray:
    """Expectancy of `n_draws` random subsets of size n_keep — what 'skill' has to beat."""
    if n_keep <= 0 or n_keep > len(pnl):
        return np.array([])
    rng = np.random.default_rng(seed)
    return np.array(
        [pnl[rng.choice(len(pnl), n_keep, replace=False)].mean() for _ in range(n_draws)]
    )


def percentile_of(value: float, draws: np.ndarray) -> float:
    return float((draws < value).mean() * 100.0) if len(draws) else float("nan")


@dataclass
class WalkForwardResult:
    kind: str
    scored: pd.DataFrame  # OOS trades with p_win / ev / keep columns
    per_fold: pd.DataFrame
    per_strategy: pd.DataFrame
    overall: dict
    permutation_importance: pd.Series = field(default_factory=pd.Series)


def walk_forward(
    trades: pd.DataFrame,
    kind: str = "hgb",
    min_train: int = 20,
    block: int = 5,
    n_random: int = 2000,
    importance: bool = False,
) -> WalkForwardResult:
    trades = trades.copy()
    trades["date"] = pd.to_datetime(trades["date"]).dt.date
    folds = walk_forward_folds(sorted(trades["date"].unique()), min_train, block)
    if not folds:
        raise ValueError("not enough sessions for a single walk-forward fold")

    pieces, fold_rows = [], []
    for k, fold in enumerate(folds, start=1):
        train = trades[trades["date"].isin(fold.train)]
        test = trades[trades["date"].isin(fold.test)]
        if test.empty or train["pnl"].gt(0).nunique() < 2:
            continue
        flt = RegimeFilter.fit(train, kind)
        scored = test.copy()
        scored["fold"] = k
        scored["p_win"] = flt.p_win(test)
        scored["ev"] = flt.expected_value(test)
        scored["keep"] = scored["ev"] > 0.0
        pieces.append(scored)
        before, after = _stats(scored["pnl"]), _stats(scored.loc[scored["keep"], "pnl"])
        fold_rows.append(
            {
                "fold": k,
                "test_sessions": f"{min(fold.test)} → {max(fold.test)}",
                "train_sessions": len(fold.train),
                "trades": before["trades"],
                "kept": after["trades"],
                "exp_all": before["expectancy"],
                "exp_kept": after["expectancy"],
            }
        )
    scored = pd.concat(pieces, ignore_index=True)

    strat_rows = []
    base = base_name(scored["strategy"])
    for seed, name in enumerate(list(STRATEGIES) + ["ALL"]):
        grp = scored if name == "ALL" else scored[base == name]
        if grp.empty:
            continue
        before = _stats(grp["pnl"])
        kept = grp[grp["keep"]]
        after = _stats(kept["pnl"])
        # Fixed seed per row so the report is reproducible run to run.
        draws = random_baseline(grp["pnl"].to_numpy(), len(kept), n_random, seed=seed)
        strat_rows.append(
            {
                "strategy": name,
                "trades": before["trades"],
                "kept": after["trades"],
                "retention_pct": 100.0 * after["trades"] / before["trades"],
                "exp_all": before["expectancy"],
                "exp_kept": after["expectancy"],
                "pf_all": before["profit_factor"],
                "pf_kept": after["profit_factor"],
                "pnl_all": before["pnl"],
                "pnl_kept": after["pnl"],
                "random_exp_mean": float(draws.mean()) if len(draws) else float("nan"),
                "random_pctile": percentile_of(after["expectancy"], draws),
            }
        )
    per_strategy = pd.DataFrame(strat_rows)
    overall = per_strategy[per_strategy["strategy"] == "ALL"].iloc[0].to_dict()

    return WalkForwardResult(
        kind=kind,
        scored=scored,
        per_fold=pd.DataFrame(fold_rows),
        per_strategy=per_strategy,
        overall=overall,
        permutation_importance=(
            _oos_permutation_importance(trades, folds, kind)
            if importance
            else pd.Series(dtype=float)
        ),
    )


def _oos_permutation_importance(
    trades: pd.DataFrame, folds: list[Fold], kind: str, n_repeats: int = 5
) -> pd.Series:
    """Drop in OOS filtered expectancy when one feature column is shuffled
    (test fold only, model untouched) — importance measured on the decision
    that matters, not on log-loss. Strategy one-hots are excluded: they are
    identity, not regime."""
    from collections import defaultdict

    rng = np.random.default_rng(0)
    drops: dict[str, list[float]] = defaultdict(list)
    for fold in folds:
        train = trades[trades["date"].isin(fold.train)]
        test = trades[trades["date"].isin(fold.test)]
        if test.empty or train["pnl"].gt(0).nunique() < 2:
            continue
        flt = RegimeFilter.fit(train, kind)
        x = flt._matrix(test)
        base_keep = flt._ev_from_matrix(test["strategy"], x) > 0
        base_exp = test["pnl"].to_numpy()[base_keep].mean() if base_keep.any() else 0.0
        for col in [c for c in flt.columns if not c.startswith("strat_")]:
            for _ in range(n_repeats):
                xp = x.copy()
                xp[col] = rng.permutation(xp[col].to_numpy())
                keep = flt._ev_from_matrix(test["strategy"], xp) > 0
                exp = test["pnl"].to_numpy()[keep].mean() if keep.any() else 0.0
                drops[col].append(base_exp - exp)
    return pd.Series({c: float(np.mean(v)) for c, v in drops.items()}).sort_values(ascending=False)


def descriptive_rules(trades: pd.DataFrame, max_depth: int = 2) -> dict[str, str]:
    """IN-SAMPLE depth-2 tree per strategy, rendered as text — a readable
    caricature of where each strategy's wins cluster. Explanation, not evidence."""
    from sklearn.tree import export_text

    rules = {}
    base = base_name(trades["strategy"])
    cols = RAW_FEATURES + list(SIGNED_FEATURES) + ["is_short", "weekday_num"]
    for name in STRATEGIES:
        grp = trades[base == name]
        if len(grp) < 40:
            continue
        x, _ = _fill(build_features(grp)[cols])
        y = (grp["pnl"] > 0).astype(int)
        if y.nunique() < 2:
            continue
        tree = DecisionTreeClassifier(max_depth=max_depth, min_samples_leaf=15, random_state=0)
        tree.fit(x, y)
        text = export_text(tree, feature_names=cols, show_weights=True, decimals=2)
        rules[name] = text
    return rules


# --------------------------------------------------------------------------- report


def _ordinal(v: float) -> str:
    n = round(v)
    suffix = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def quintile_table(scored: pd.DataFrame) -> pd.DataFrame:
    """OOS expectancy by predicted-EV quintile — the calibration check that
    catches a model ranking trades by something other than what pays."""
    s = scored.copy()
    s["q"] = pd.qcut(s["ev"].rank(method="first"), 5, labels=False)
    rows = []
    for q, grp in s.groupby("q"):
        rows.append(
            {
                "predicted-EV quintile": ["1 (lowest)", "2", "3", "4", "5 (highest)"][int(q)],
                "trades": len(grp),
                "mean predicted EV": _fmt_money(grp["ev"].mean()),
                "actual exp./trade": _fmt_money(grp["pnl"].mean()),
                "win rate": f"{100.0 * (grp['pnl'] > 0).mean():.0f}%",
            }
        )
    return pd.DataFrame(rows)


def _fmt_money(v: float) -> str:
    return "—" if pd.isna(v) else f"${v:+,.2f}"


def _fmt_pf(v: float) -> str:
    if pd.isna(v):
        return "—"
    return "∞" if np.isinf(v) else f"{v:.2f}"


def _strategy_table(res: WalkForwardResult) -> pd.DataFrame:
    rows = []
    for r in res.per_strategy.itertuples(index=False):
        label = "**All strategies**" if r.strategy == "ALL" else STRATEGIES[r.strategy][0]
        flag = " ⚠" if r.kept < MIN_FOLD_TRADES else ""
        rows.append(
            {
                "strategy": label,
                "OOS trades": r.trades,
                "kept": f"{r.kept} ({r.retention_pct:.0f}%){flag}",
                "exp./trade, all": _fmt_money(r.exp_all),
                "exp./trade, kept": _fmt_money(r.exp_kept),
                "PF all → kept": f"{_fmt_pf(r.pf_all)} → {_fmt_pf(r.pf_kept)}",
                "P&L all → kept": f"{_fmt_money(r.pnl_all)} → {_fmt_money(r.pnl_kept)}",
                "random same-size": _fmt_money(r.random_exp_mean),
                "pctile vs random": "—" if pd.isna(r.random_pctile) else f"{r.random_pctile:.0f}",
            }
        )
    return pd.DataFrame(rows)


def _fold_table(res: WalkForwardResult) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "fold": r.fold,
                "test sessions": r.test_sessions,
                "train sessions": r.train_sessions,
                "trades": r.trades,
                "kept": r.kept,
                "exp./trade, all": _fmt_money(r.exp_all),
                "exp./trade, kept": _fmt_money(r.exp_kept),
            }
            for r in res.per_fold.itertuples(index=False)
        ]
    )


def _verdict(res: WalkForwardResult) -> str:
    o = res.overall
    exp_kept, pct = o["exp_kept"], o["random_pctile"]
    label = KINDS.get(res.kind, res.kind)
    if exp_kept > 0 and pct >= 95:
        return (
            f"**Gate met on this window (pending paper confirmation).** The {label} filter's kept "
            f"trades have positive out-of-sample expectancy ({_fmt_money(exp_kept)}/trade) and sit at "
            f"the {_ordinal(pct)} percentile of same-size random selections — the model is selecting "
            f"on regime, not luck."
        )
    if exp_kept > 0:
        return (
            f"**Positive but not yet distinguishable from luck.** Filtered OOS expectancy is "
            f"{_fmt_money(exp_kept)}/trade, but only the {_ordinal(pct)} percentile of same-size "
            f"random selections — a random subset of the same size lands here often enough that this "
            f"cannot be called an edge."
        )
    if pct >= 95:
        return (
            f"**The filter learns something real, but not enough.** It lifts OOS expectancy from "
            f"{_fmt_money(o['exp_all'])} to {_fmt_money(exp_kept)}/trade ({_ordinal(pct)} percentile "
            f"vs random) — clearly better than chance, still a losing book. Standing aside more "
            f"often helps; it does not create an edge that isn't in the entries."
        )
    if pct >= 80:
        return (
            f"**Suggestive, not established.** The {label} filter lifts OOS expectancy from "
            f"{_fmt_money(o['exp_all'])} to {_fmt_money(exp_kept)}/trade, at the {_ordinal(pct)} "
            f"percentile of same-size random selections — better than most random subsets, but "
            f"not clearly enough to rule out chance, and still a losing book. Worth carrying into "
            f"the paper loop as an advisory signal; not worth believing yet."
        )
    if pct <= 5:
        return (
            f"**Worse than chance.** The {label} filter's kept trades lose {_fmt_money(exp_kept)}/trade "
            f"out of sample against {_fmt_money(o['exp_all'])} unfiltered — the {_ordinal(pct)} "
            f"percentile of same-size random selections. The model ranks trades by something that "
            f"anti-correlates with P&L out of sample (see the quintile table)."
        )
    return (
        f"**No regime edge found.** Filtered OOS expectancy {_fmt_money(exp_kept)}/trade, "
        f"{_ordinal(pct)} percentile vs random same-size selection — the conditions at entry do not "
        f"predict which of these trades pay, out of sample."
    )


def _oos_chart(results: dict[str, WalkForwardResult], path: Path) -> None:
    """Cumulative OOS P&L, every strategy pooled: unfiltered vs each filter."""
    fig, ax = plt.subplots(figsize=(11, 5.4), dpi=100)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    first = next(iter(results.values()))
    scored = first.scored.sort_values("exit_time")
    ax.step(
        pd.to_datetime(scored["exit_time"], utc=True),
        scored["pnl"].cumsum(),
        where="post",
        color=MUTED,
        linewidth=2,
        label="Unfiltered (every OOS trade)",
    )
    colors = {"hgb": "#2a78d6", "logit": "#eb6834", "hgb_reg": "#1baf7a", "ridge": "#eda100"}
    for kind, res in results.items():
        kept = res.scored[res.scored["keep"]].sort_values("exit_time")
        ax.step(
            pd.to_datetime(kept["exit_time"], utc=True),
            kept["pnl"].cumsum(),
            where="post",
            color=colors.get(kind, INK_2),
            linewidth=2,
            label=f"{KINDS.get(kind, kind)} — kept only",
        )
    ax.axhline(0, color=BASELINE, linewidth=1)
    ax.set_title(
        "Out-of-sample cumulative P&L, all strategies: with vs without the regime filter",
        loc="left",
        fontsize=13,
        fontweight="bold",
        color=INK,
        pad=64,
    )
    ax.set_ylabel("P&L per $10k trade size (USD)", color=INK_2, fontsize=10)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(BASELINE)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.legend(
        frameon=False,
        fontsize=9,
        labelcolor=INK_2,
        loc="lower left",
        bbox_to_anchor=(0, 1.0),
        ncols=2,
    )
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)


def paper_check(flt: RegimeFilter, journal: pd.DataFrame, trained_through: dt.date) -> dict | None:
    """Apply a filter fitted on backtest sessions ≤ trained_through to the real
    paper fills that came AFTER it — different execution path, genuinely unseen."""
    if journal.empty or "pnl" not in journal:
        return None
    j = journal.copy()
    j["date"] = pd.to_datetime(j["date"]).dt.date
    j = j[j["date"] > trained_through].dropna(subset=["pnl"])
    if len(j) < MIN_FOLD_TRADES:
        return None
    if "side" not in j:
        j["side"] = "long"
    j["side"] = j["side"].fillna("long")
    keep = flt.keep(j)
    before, after = _stats(j["pnl"]), _stats(j.loc[keep, "pnl"])
    draws = random_baseline(j["pnl"].to_numpy(), int(keep.sum()), 2000, seed=7)
    return {
        "from": min(j["date"]),
        "to": max(j["date"]),
        "trades": before["trades"],
        "kept": after["trades"],
        "exp_all": before["expectancy"],
        "exp_kept": after["expectancy"],
        "random_pctile": percentile_of(after["expectancy"], draws),
    }


def run_regime(
    trades_path: Path = Path("results/trades.csv"),
    journal_path: Path = Path("results/paper_journal.csv"),
    out_dir: Path = Path("results"),
    min_train: int = 20,
    block: int = 5,
    kinds: tuple[str, ...] = ("hgb_reg", "ridge", "hgb", "logit"),
) -> Path:
    trades = pd.read_csv(trades_path)
    trades["date"] = pd.to_datetime(trades["date"]).dt.date
    if "side" not in trades:
        trades["side"] = "long"
    sessions = sorted(trades["date"].unique())

    results = {
        kind: walk_forward(trades, kind, min_train, block, importance=(kind == kinds[0]))
        for kind in kinds
    }
    for kind, res in results.items():
        o = res.overall
        print(
            f"{kind}: OOS {o['trades']} trades → kept {o['kept']} ({o['retention_pct']:.0f}%), "
            f"expectancy {_fmt_money(o['exp_all'])} → {_fmt_money(o['exp_kept'])}/trade, "
            f"{_ordinal(o['random_pctile'])} pctile vs random"
        )

    out_dir.mkdir(exist_ok=True)
    _oos_chart(results, out_dir / "regime_oos.png")

    # Paper-journal check: fit on the backtest sessions that precede the paper
    # loop's first fill, score the fills themselves.
    paper = None
    if journal_path.exists():
        journal = pd.read_csv(journal_path)
        if not journal.empty:
            first_paper = pd.to_datetime(journal["date"]).dt.date.min()
            pre = trades[trades["date"] < first_paper]
            if pre["date"].nunique() >= min_train:
                paper = paper_check(
                    RegimeFilter.fit(pre, kinds[0]), journal, first_paper - dt.timedelta(days=1)
                )

    # The live filter: the primary kind fitted on every session in the window.
    # The paper scanner trades `<name>_regime` variants off this file; the
    # weekly workflow re-fits it as the 60-day window rolls forward.
    primary = results[kinds[0]]
    live = RegimeFilter.fit(trades, kinds[0])
    meta = {
        "generated": market_today().isoformat(),
        "kind": kinds[0],
        "sessions": len(sessions),
        "window": f"{sessions[0]} → {sessions[-1]}",
        "trades": len(trades),
        "oos_exp_all": round(float(primary.overall["exp_all"]), 2),
        "oos_exp_kept": round(float(primary.overall["exp_kept"]), 2),
        "oos_random_pctile": round(float(primary.overall["random_pctile"]), 1),
    }
    save_filter(live, meta, out_dir / MODEL_PATH.name)
    print(f"live filter ({kinds[0]}, {len(sessions)} sessions) → {out_dir / MODEL_PATH.name}")

    rules = descriptive_rules(trades)
    path = out_dir / "REGIME.md"
    path.write_text(_render(results, primary, rules, paper, sessions, min_train, block, meta))
    return path


def _render(
    results, primary: WalkForwardResult, rules, paper, sessions, min_train, block, live_meta
) -> str:
    n_oos = len({d for d in primary.scored["date"]})
    model_rows = pd.DataFrame(
        [
            {
                "model": KINDS.get(k, k),
                "OOS trades": r.overall["trades"],
                "kept": f"{r.overall['kept']} ({r.overall['retention_pct']:.0f}%)",
                "exp./trade, all": _fmt_money(r.overall["exp_all"]),
                "exp./trade, kept": _fmt_money(r.overall["exp_kept"]),
                "PF all → kept": f"{_fmt_pf(r.overall['pf_all'])} → {_fmt_pf(r.overall['pf_kept'])}",
                "random same-size": _fmt_money(r.overall["random_exp_mean"]),
                "pctile vs random": f"{r.overall['random_pctile']:.0f}",
            }
            for k, r in results.items()
        ]
    )
    imp = primary.permutation_importance.head(8)
    imp_table = pd.DataFrame(
        {
            "feature": imp.index,
            "OOS expectancy drop when shuffled": [f"${v:+.2f}" for v in imp.values],
        }
    )
    rules_md = "\n".join(
        f"**{STRATEGIES[name][0]}**\n\n```\n{text.rstrip()}\n```\n" for name, text in rules.items()
    )
    if paper:
        paper_md = f"""## Paper-journal check (real fills, different execution path)

A filter fitted only on backtest sessions before the paper loop's first fill
({paper['from']}) was applied to the **{paper['trades']} real paper trades** from
{paper['from']} to {paper['to']}. It kept {paper['kept']}; expectancy
{_fmt_money(paper['exp_all'])} → {_fmt_money(paper['exp_kept'])}/trade
({_ordinal(paper['random_pctile'])} percentile vs same-size random selection). Small
sample — a direction check, not a verdict.
"""
    else:
        paper_md = ""

    return f"""# Regime filters — learned from the journal, validated walk-forward

Generated {market_today().isoformat()} · {len(sessions)} sessions ({sessions[0]} → {sessions[-1]}) ·
**walk-forward:** first {min_train} sessions train-only, then blocks of {block} sessions scored by a
model trained on every session before them · **{n_oos} out-of-sample sessions** · decision rule:
keep a trade when its predicted expected value is positive (classifiers: P(win)·avg_win +
(1−P(win))·avg_loss with averages from the training fold; regressors: predicted P&L) ·
"random same-size" = mean expectancy of 2,000 random subsets with the same trade count.

{_verdict(primary)}

## Models

{_md_table(model_rows)}

![OOS cumulative P&L with vs without the filter](regime_oos.png)

*Read the curves with care: a filtered line holds fewer trades, so its total shrinks
mechanically even under random selection. The fair comparison is expectancy per
trade against the "random same-size" column, not the gap between the curves.*

## Calibration — does a higher predicted EV actually pay? ({KINDS[primary.kind]})

{_md_table(quintile_table(primary.scored))}

A filter is only as good as this table is monotonic. If the top quintile does not
out-earn the bottom one out of sample, the model has learned to rank trades by
something other than what pays.

## Per strategy — {KINDS[primary.kind]} filter, out-of-sample only

{_md_table(_strategy_table(primary))}

⚠ = fewer than {MIN_FOLD_TRADES} kept trades; noise, not evidence. "pctile vs random" is where
the filtered expectancy lands among 2,000 random subsets of the same size (≥95 = the selection
is doing something chance rarely does).

## Fold by fold — {KINDS[primary.kind]}

{_md_table(_fold_table(primary))}

## What the filter looks at

Permutation importance measured on the decision that matters: how much OOS
filtered expectancy falls when one feature is shuffled in the test fold.

{_md_table(imp_table)}

Features prefixed `aligned_` are signed by trade direction (a short's SPY move is
negated), so one pooled model can treat "long in a rising tape" and "short in a
falling tape" as the same regime.

{paper_md}
## Descriptive rules (in-sample, for reading — not evidence)

Depth-2 decision trees per strategy on the full window, so the filter's opinion is
legible. `weights: [losers, winners]` per leaf. These were fit on all sessions and
prove nothing; the walk-forward tables above are the evidence.

{rules_md}

## The live filter

`{MODEL_PATH.name}` — {KINDS[live_meta["kind"]]}, fitted on all {live_meta["sessions"]} sessions
({live_meta["trades"]} trades). The paper scanner scores every base-strategy signal with it and
places a second order tagged `<strategy>_regime` only when predicted EV > 0, so
`paper_journal.csv` accumulates a live filtered-vs-unfiltered comparison; every journal row also
carries `regime_ev`, the filter's verdict at entry. Re-fitted each Saturday as the window rolls.

## How to read this honestly

- Every OOS number comes from a model that never saw the session it scored.
- A filter can only *remove* trades. If the entries have no edge in any regime,
  the best it can do is lose less — the "PF all → kept" column shows whether it
  found a subset that actually pays.
- With ~{n_oos} OOS sessions in one market regime, "gate met" here means *earned a
  paper-trading test*, not "trade it".
"""
