# Regime filters — learned from the journal, validated walk-forward

Generated 2026-09-26 · 60 sessions (2026-07-02 → 2026-09-25) ·
**walk-forward:** first 20 sessions train-only, then blocks of 5 sessions scored by a
model trained on every session before them · **40 out-of-sample sessions** · decision rule:
keep a trade when its predicted expected value is positive (classifiers: P(win)·avg_win +
(1−P(win))·avg_loss with averages from the training fold; regressors: predicted P&L) ·
"random same-size" = mean expectancy of 2,000 random subsets with the same trade count.

**Gate met on this window (pending paper confirmation).** The Gradient boosting → P&L directly filter's kept trades have positive out-of-sample expectancy ($+9.56/trade) and sit at the 100th percentile of same-size random selections — the model is selecting on regime, not luck.

## Models

| model | OOS trades | kept | exp./trade, all | exp./trade, kept | PF all → kept | random same-size | pctile vs random |
|---|---|---|---|---|---|---|---|
| Gradient boosting → P&L directly | 2021 | 253 (13%) | $-12.03 | $+9.56 | 0.71 → 1.29 | $-12.38 | 100 |
| Ridge regression → P&L directly | 2021 | 493 (24%) | $-12.03 | $-3.28 | 0.71 → 0.91 | $-12.07 | 99 |
| Gradient boosting → P(win) → EV | 2021 | 255 (13%) | $-12.03 | $-13.53 | 0.71 → 0.77 | $-11.94 | 40 |
| Logistic regression → P(win) → EV | 2021 | 171 (8%) | $-12.03 | $+0.41 | 0.71 → 1.01 | $-12.23 | 95 |

![OOS cumulative P&L with vs without the filter](regime_oos.png)

*Read the curves with care: a filtered line holds fewer trades, so its total shrinks
mechanically even under random selection. The fair comparison is expectancy per
trade against the "random same-size" column, not the gap between the curves.*

## Calibration — does a higher predicted EV actually pay? (Gradient boosting → P&L directly)

| predicted-EV quintile | trades | mean predicted EV | actual exp./trade | win rate |
|---|---|---|---|---|
| 1 (lowest) | 405 | $-66.22 | $-19.58 | 37% |
| 2 | 404 | $-39.43 | $-20.09 | 29% |
| 3 | 404 | $-25.50 | $-16.51 | 35% |
| 4 | 404 | $-9.96 | $-6.10 | 45% |
| 5 (highest) | 404 | $+5.21 | $+2.16 | 46% |

A filter is only as good as this table is monotonic. If the top quintile does not
out-earn the bottom one out of sample, the model has learned to rank trades by
something other than what pays.

## Per strategy — Gradient boosting → P&L directly filter, out-of-sample only

| strategy | OOS trades | kept | exp./trade, all | exp./trade, kept | PF all → kept | P&L all → kept | random same-size | pctile vs random |
|---|---|---|---|---|---|---|---|---|
| Gap & Go | 10 | 2 (20%) ⚠ | $+120.18 | $+450.24 | 2.22 → ∞ | $+1,201.79 → $+900.48 | $+119.03 | 98 |
| Opening Range Breakout | 206 | 30 (15%) | $+0.82 | $+84.91 | 1.01 → 2.11 | $+168.28 → $+2,547.39 | $+0.98 | 99 |
| VWAP Pullback | 290 | 0 (0%) ⚠ | $-23.55 | — | 0.57 → — | $-6,830.25 → $+0.00 | — | — |
| EMA 9/20 Crossover | 260 | 2 (1%) ⚠ | $-14.25 | $-53.79 | 0.60 → 0.00 | $-3,704.11 → $-107.57 | $-13.64 | 17 |
| RSI(2) Reversion | 471 | 150 (32%) | $-11.16 | $-9.84 | 0.45 → 0.55 | $-5,255.40 → $-1,475.84 | $-11.17 | 67 |
| News Momentum | 27 | 0 (0%) ⚠ | $-25.70 | — | 0.49 → — | $-693.79 → $+0.00 | — | — |
| Squeeze Breakout | 172 | 0 (0%) ⚠ | $-22.00 | — | 0.46 → — | $-3,783.59 → $+0.00 | — | — |
| High-Break ATR Trail | 165 | 5 (3%) ⚠ | $-19.67 | $+133.87 | 0.68 → 2.69 | $-3,246.06 → $+669.35 | $-18.45 | 98 |
| AR Forecast | 420 | 64 (15%) | $-5.15 | $-1.79 | 0.81 → 0.95 | $-2,162.92 → $-114.43 | $-5.36 | 68 |
| **All strategies** | 2021 | 253 (13%) | $-12.03 | $+9.56 | 0.71 → 1.29 | $-24,306.05 → $+2,419.38 | $-12.38 | 100 |

⚠ = fewer than 10 kept trades; noise, not evidence. "pctile vs random" is where
the filtered expectancy lands among 2,000 random subsets of the same size (≥95 = the selection
is doing something chance rarely does).

## Fold by fold — Gradient boosting → P&L directly

| fold | test sessions | train sessions | trades | kept | exp./trade, all | exp./trade, kept |
|---|---|---|---|---|---|---|
| 1 | 2026-07-31 → 2026-08-06 | 20 | 255 | 55 | $-19.50 | $-8.10 |
| 2 | 2026-08-07 → 2026-08-13 | 25 | 266 | 42 | $-23.29 | $-13.58 |
| 3 | 2026-08-14 → 2026-08-20 | 30 | 261 | 30 | $-10.09 | $+46.27 |
| 4 | 2026-08-21 → 2026-08-27 | 35 | 251 | 37 | $-16.06 | $+11.01 |
| 5 | 2026-08-28 → 2026-09-03 | 40 | 249 | 32 | $+11.44 | $+9.59 |
| 6 | 2026-09-04 → 2026-09-11 | 45 | 238 | 14 | $-7.52 | $-10.94 |
| 7 | 2026-09-14 → 2026-09-18 | 50 | 250 | 19 | $-9.94 | $+55.31 |
| 8 | 2026-09-21 → 2026-09-25 | 55 | 251 | 24 | $-20.11 | $+18.13 |

## What the filter looks at

Permutation importance measured on the decision that matters: how much OOS
filtered expectancy falls when one feature is shuffled in the test fold.

| feature | OOS expectancy drop when shuffled |
|---|---|
| aligned_trend_slope_pct | $+20.75 |
| mkt_gap_pct | $+11.36 |
| mkt_trend_slope_pct | $+8.12 |
| mkt_change_open_pct | $+7.17 |
| mkt_realized_vol_pct | $+5.70 |
| aligned_change_open_pct | $+4.31 |
| mkt_dist_vwap_pct | $+2.64 |
| hour_et | $+1.28 |

Features prefixed `aligned_` are signed by trade direction (a short's SPY move is
negated), so one pooled model can treat "long in a rising tape" and "short in a
falling tape" as the same regime.

## Paper-journal check (real fills, different execution path)

A filter fitted only on backtest sessions before the paper loop's first fill
(2026-08-24) was applied to the **506 real paper trades** from
2026-08-24 to 2026-09-25. It kept 53; expectancy
$-10.53 → $+49.57/trade
(100th percentile vs same-size random selection). Small
sample — a direction check, not a verdict.

## Descriptive rules (in-sample, for reading — not evidence)

Depth-2 decision trees per strategy on the full window, so the filter's opinion is
legible. `weights: [losers, winners]` per leaf. These were fit on all sessions and
prove nothing; the walk-forward tables above are the evidence.

**Opening Range Breakout**

```
|--- mkt_range_pos <= 0.13
|   |--- mkt_gap_pct <= 1.17
|   |   |--- weights: [56.00, 19.00] class: 0
|   |--- mkt_gap_pct >  1.17
|   |   |--- weights: [8.00, 10.00] class: 1
|--- mkt_range_pos >  0.13
|   |--- aligned_range_pos <= 0.90
|   |   |--- weights: [56.00, 81.00] class: 1
|   |--- aligned_range_pos >  0.90
|   |   |--- weights: [53.00, 28.00] class: 0
```

**VWAP Pullback**

```
|--- mkt_atr_pct <= 0.54
|   |--- mkt_gap_pct <= -1.71
|   |   |--- weights: [19.00, 4.00] class: 0
|   |--- mkt_gap_pct >  -1.71
|   |   |--- weights: [64.00, 55.00] class: 0
|--- mkt_atr_pct >  0.54
|   |--- mkt_change_open_pct <= 0.97
|   |   |--- weights: [164.00, 52.00] class: 0
|   |--- mkt_change_open_pct >  0.97
|   |   |--- weights: [51.00, 32.00] class: 0
```

**EMA 9/20 Crossover**

```
|--- mkt_realized_vol_pct <= 4.40
|   |--- mkt_rel_volume <= 0.64
|   |   |--- weights: [147.00, 63.00] class: 0
|   |--- mkt_rel_volume >  0.64
|   |   |--- weights: [96.00, 16.00] class: 0
|--- mkt_realized_vol_pct >  4.40
|   |--- aligned_spy_pct <= -0.19
|   |   |--- weights: [5.00, 11.00] class: 1
|   |--- aligned_spy_pct >  -0.19
|   |   |--- weights: [23.00, 12.00] class: 0
```

**RSI(2) Reversion**

```
|--- mkt_realized_vol_pct <= 1.45
|   |--- mkt_change_open_pct <= -0.32
|   |   |--- weights: [21.00, 0.00] class: 0
|   |--- mkt_change_open_pct >  -0.32
|   |   |--- weights: [14.00, 7.00] class: 0
|--- mkt_realized_vol_pct >  1.45
|   |--- aligned_spy_pct <= 0.45
|   |   |--- weights: [308.00, 275.00] class: 0
|   |--- aligned_spy_pct >  0.45
|   |   |--- weights: [29.00, 64.00] class: 1
```

**News Momentum**

```
|--- mkt_autocorr_1 <= 0.04
|   |--- weights: [23.00, 5.00] class: 0
|--- mkt_autocorr_1 >  0.04
|   |--- weights: [7.00, 10.00] class: 1
```

**Squeeze Breakout**

```
|--- mkt_gap_pct <= 0.92
|   |--- mkt_autocorr_1 <= 0.07
|   |   |--- weights: [103.00, 36.00] class: 0
|   |--- mkt_autocorr_1 >  0.07
|   |   |--- weights: [42.00, 2.00] class: 0
|--- mkt_gap_pct >  0.92
|   |--- aligned_spy_pct <= -0.13
|   |   |--- weights: [12.00, 15.00] class: 1
|   |--- aligned_spy_pct >  -0.13
|   |   |--- weights: [34.00, 14.00] class: 0
```

**High-Break ATR Trail**

```
|--- aligned_spy_pct <= -0.18
|   |--- weights: [10.00, 18.00] class: 1
|--- aligned_spy_pct >  -0.18
|   |--- mkt_spy_change_pct <= -0.29
|   |   |--- weights: [32.00, 2.00] class: 0
|   |--- mkt_spy_change_pct >  -0.29
|   |   |--- weights: [134.00, 66.00] class: 0
```

**AR Forecast**

```
|--- aligned_change_open_pct <= 5.30
|   |--- aligned_dist_vwap_pct <= -0.80
|   |   |--- weights: [62.00, 71.00] class: 1
|   |--- aligned_dist_vwap_pct >  -0.80
|   |   |--- weights: [287.00, 201.00] class: 0
|--- aligned_change_open_pct >  5.30
|   |--- weights: [3.00, 14.00] class: 1
```


## The live filter

`regime_model.joblib` — Gradient boosting → P&L directly, fitted on all 60 sessions
(3058 trades). The paper scanner scores every base-strategy signal with it and
places a second order tagged `<strategy>_regime` only when predicted EV > 0, so
`paper_journal.csv` accumulates a live filtered-vs-unfiltered comparison; every journal row also
carries `regime_ev`, the filter's verdict at entry. Re-fitted each Saturday as the window rolls.

## How to read this honestly

- Every OOS number comes from a model that never saw the session it scored.
- A filter can only *remove* trades. If the entries have no edge in any regime,
  the best it can do is lose less — the "PF all → kept" column shows whether it
  found a subset that actually pays.
- With ~40 OOS sessions in one market regime, "gate met" here means *earned a
  paper-trading test*, not "trade it".
