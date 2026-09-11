# Regime filters — learned from the journal, validated walk-forward

Generated 2026-09-10 · 60 sessions (2026-06-15 → 2026-09-09) ·
**walk-forward:** first 20 sessions train-only, then blocks of 5 sessions scored by a
model trained on every session before them · **40 out-of-sample sessions** · decision rule:
keep a trade when its predicted expected value is positive (classifiers: P(win)·avg_win +
(1−P(win))·avg_loss with averages from the training fold; regressors: predicted P&L) ·
"random same-size" = mean expectancy of 2,000 random subsets with the same trade count.

**Suggestive, not established.** The Gradient boosting → P&L directly filter lifts OOS expectancy from $-13.03 to $-4.82/trade, at the 92nd percentile of same-size random selections — better than most random subsets, but not clearly enough to rule out chance, and still a losing book. Worth carrying into the paper loop as an advisory signal; not worth believing yet.

## Models

| model | OOS trades | kept | exp./trade, all | exp./trade, kept | PF all → kept | random same-size | pctile vs random |
|---|---|---|---|---|---|---|---|
| Gradient boosting → P&L directly | 2063 | 295 (14%) | $-13.03 | $-4.82 | 0.70 → 0.87 | $-12.97 | 92 |
| Ridge regression → P&L directly | 2063 | 565 (27%) | $-13.03 | $-8.21 | 0.70 → 0.77 | $-12.89 | 88 |
| Gradient boosting → P(win) → EV | 2063 | 324 (16%) | $-13.03 | $-22.96 | 0.70 → 0.62 | $-13.03 | 3 |
| Logistic regression → P(win) → EV | 2063 | 183 (9%) | $-13.03 | $-12.55 | 0.70 → 0.80 | $-13.25 | 53 |

![OOS cumulative P&L with vs without the filter](regime_oos.png)

*Read the curves with care: a filtered line holds fewer trades, so its total shrinks
mechanically even under random selection. The fair comparison is expectancy per
trade against the "random same-size" column, not the gap between the curves.*

## Calibration — does a higher predicted EV actually pay? (Gradient boosting → P&L directly)

| predicted-EV quintile | trades | mean predicted EV | actual exp./trade | win rate |
|---|---|---|---|---|
| 1 (lowest) | 413 | $-68.70 | $-20.36 | 34% |
| 2 | 412 | $-38.98 | $-18.84 | 32% |
| 3 | 413 | $-22.39 | $-12.87 | 38% |
| 4 | 412 | $-7.68 | $-9.58 | 45% |
| 5 (highest) | 413 | $+6.00 | $-3.52 | 46% |

A filter is only as good as this table is monotonic. If the top quintile does not
out-earn the bottom one out of sample, the model has learned to rank trades by
something other than what pays.

## Per strategy — Gradient boosting → P&L directly filter, out-of-sample only

| strategy | OOS trades | kept | exp./trade, all | exp./trade, kept | PF all → kept | P&L all → kept | random same-size | pctile vs random |
|---|---|---|---|---|---|---|---|---|
| Gap & Go | 10 | 3 (30%) ⚠ | $+83.88 | $+86.49 | 1.67 → 1.99 | $+838.84 → $+259.48 | $+83.16 | 53 |
| Opening Range Breakout | 215 | 31 (14%) | $-0.27 | $+17.32 | 1.00 → 1.19 | $-58.41 → $+536.96 | $-0.81 | 70 |
| VWAP Pullback | 294 | 2 (1%) ⚠ | $-18.94 | $-68.49 | 0.66 → 0.00 | $-5,569.11 → $-136.98 | $-17.38 | 31 |
| EMA 9/20 Crossover | 234 | 0 (0%) ⚠ | $-11.53 | — | 0.66 → — | $-2,697.83 → $+0.00 | — | — |
| RSI(2) Reversion | 495 | 192 (39%) | $-12.66 | $-15.08 | 0.44 → 0.44 | $-6,266.10 → $-2,896.09 | $-12.69 | 18 |
| News Momentum | 27 | 0 (0%) ⚠ | $-20.29 | — | 0.51 → — | $-547.91 → $+0.00 | — | — |
| Squeeze Breakout | 173 | 0 (0%) ⚠ | $-29.11 | — | 0.39 → — | $-5,035.63 → $+0.00 | — | — |
| High-Break ATR Trail | 180 | 4 (2%) ⚠ | $-24.83 | $+195.43 | 0.62 → 3.91 | $-4,470.25 → $+781.70 | $-25.27 | 100 |
| AR Forecast | 435 | 63 (14%) | $-7.08 | $+0.54 | 0.76 → 1.02 | $-3,081.17 → $+34.15 | $-7.26 | 82 |
| **All strategies** | 2063 | 295 (14%) | $-13.03 | $-4.82 | 0.70 → 0.87 | $-26,887.57 → $-1,420.78 | $-12.97 | 92 |

⚠ = fewer than 10 kept trades; noise, not evidence. "pctile vs random" is where
the filtered expectancy lands among 2,000 random subsets of the same size (≥95 = the selection
is doing something chance rarely does).

## Fold by fold — Gradient boosting → P&L directly

| fold | test sessions | train sessions | trades | kept | exp./trade, all | exp./trade, kept |
|---|---|---|---|---|---|---|
| 1 | 2026-07-15 → 2026-07-21 | 20 | 262 | 57 | $-26.86 | $-27.86 |
| 2 | 2026-07-22 → 2026-07-28 | 25 | 264 | 53 | $-13.93 | $-23.46 |
| 3 | 2026-07-29 → 2026-08-04 | 30 | 255 | 44 | $-9.54 | $-30.09 |
| 4 | 2026-08-05 → 2026-08-11 | 35 | 281 | 43 | $-31.97 | $-17.31 |
| 5 | 2026-08-12 → 2026-08-18 | 40 | 247 | 17 | $-18.47 | $-15.89 |
| 6 | 2026-08-19 → 2026-08-25 | 45 | 268 | 29 | $-10.09 | $+42.40 |
| 7 | 2026-08-26 → 2026-09-01 | 50 | 241 | 28 | $+1.54 | $+16.54 |
| 8 | 2026-09-02 → 2026-09-09 | 55 | 245 | 24 | $+8.72 | $+85.68 |

## What the filter looks at

Permutation importance measured on the decision that matters: how much OOS
filtered expectancy falls when one feature is shuffled in the test fold.

| feature | OOS expectancy drop when shuffled |
|---|---|
| aligned_trend_slope_pct | $+15.20 |
| mkt_gap_pct | $+9.85 |
| mkt_change_open_pct | $+4.12 |
| mkt_trend_slope_pct | $+3.95 |
| mkt_range_pos | $+1.05 |
| mkt_autocorr_1 | $+0.31 |
| aligned_change_open_pct | $+0.03 |
| is_short | $+0.00 |

Features prefixed `aligned_` are signed by trade direction (a short's SPY move is
negated), so one pooled model can treat "long in a rising tape" and "short in a
falling tape" as the same regime.

## Paper-journal check (real fills, different execution path)

A filter fitted only on backtest sessions before the paper loop's first fill
(2026-08-24) was applied to the **159 real paper trades** from
2026-08-24 to 2026-09-10. It kept 15; expectancy
$-25.86 → $+118.91/trade
(100th percentile vs same-size random selection). Small
sample — a direction check, not a verdict.

## Descriptive rules (in-sample, for reading — not evidence)

Depth-2 decision trees per strategy on the full window, so the filter's opinion is
legible. `weights: [losers, winners]` per leaf. These were fit on all sessions and
prove nothing; the walk-forward tables above are the evidence.

**Opening Range Breakout**

```
|--- mkt_change_open_pct <= 1.87
|   |--- mkt_atr_pct <= 0.94
|   |   |--- weights: [33.00, 44.00] class: 1
|   |--- mkt_atr_pct >  0.94
|   |   |--- weights: [109.00, 61.00] class: 0
|--- mkt_change_open_pct >  1.87
|   |--- aligned_range_pos <= 0.90
|   |   |--- weights: [8.00, 27.00] class: 1
|   |--- aligned_range_pos >  0.90
|   |   |--- weights: [21.00, 16.00] class: 0
```

**VWAP Pullback**

```
|--- mkt_realized_vol_pct <= 2.83
|   |--- mkt_trend_slope_pct <= -0.03
|   |   |--- weights: [7.00, 13.00] class: 1
|   |--- mkt_trend_slope_pct >  -0.03
|   |   |--- weights: [70.00, 45.00] class: 0
|--- mkt_realized_vol_pct >  2.83
|   |--- aligned_change_open_pct <= 0.77
|   |   |--- weights: [82.00, 14.00] class: 0
|   |--- aligned_change_open_pct >  0.77
|   |   |--- weights: [130.00, 69.00] class: 0
```

**EMA 9/20 Crossover**

```
|--- mkt_rel_volume <= 1.14
|   |--- aligned_spy_pct <= -0.18
|   |   |--- weights: [46.00, 32.00] class: 0
|   |--- aligned_spy_pct >  -0.18
|   |   |--- weights: [197.00, 61.00] class: 0
|--- mkt_rel_volume >  1.14
|   |--- weights: [9.00, 13.00] class: 1
```

**RSI(2) Reversion**

```
|--- mkt_gap_pct <= 2.95
|   |--- aligned_spy_pct <= 0.56
|   |   |--- weights: [327.00, 266.00] class: 0
|   |--- aligned_spy_pct >  0.56
|   |   |--- weights: [19.00, 50.00] class: 1
|--- mkt_gap_pct >  2.95
|   |--- mkt_change_open_pct <= -1.31
|   |   |--- weights: [2.00, 23.00] class: 1
|   |--- mkt_change_open_pct >  -1.31
|   |   |--- weights: [20.00, 35.00] class: 1
```

**News Momentum**

```
|--- aligned_spy_pct <= 0.33
|   |--- weights: [12.00, 16.00] class: 1
|--- aligned_spy_pct >  0.33
|   |--- weights: [13.00, 3.00] class: 0
```

**Squeeze Breakout**

```
|--- mkt_gap_pct <= 0.92
|   |--- aligned_range_pos <= -0.05
|   |   |--- weights: [37.00, 20.00] class: 0
|   |--- aligned_range_pos >  -0.05
|   |   |--- weights: [108.00, 21.00] class: 0
|--- mkt_gap_pct >  0.92
|   |--- weekday_num <= 0.50
|   |   |--- weights: [6.00, 10.00] class: 1
|   |--- weekday_num >  0.50
|   |   |--- weights: [40.00, 16.00] class: 0
```

**High-Break ATR Trail**

```
|--- mkt_rel_volume <= 0.57
|   |--- mkt_spy_change_pct <= -0.12
|   |   |--- weights: [12.00, 3.00] class: 0
|   |--- mkt_spy_change_pct >  -0.12
|   |   |--- weights: [19.00, 0.00] class: 0
|--- mkt_rel_volume >  0.57
|   |--- hour_et <= 11.79
|   |   |--- weights: [96.00, 77.00] class: 0
|   |--- hour_et >  11.79
|   |   |--- weights: [51.00, 17.00] class: 0
```

**AR Forecast**

```
|--- mkt_change_open_pct <= 4.48
|   |--- mkt_change_open_pct <= 3.73
|   |   |--- weights: [332.00, 261.00] class: 0
|   |--- mkt_change_open_pct >  3.73
|   |   |--- weights: [18.00, 0.00] class: 0
|--- mkt_change_open_pct >  4.48
|   |--- aligned_spy_pct <= -0.07
|   |   |--- weights: [9.00, 8.00] class: 0
|   |--- aligned_spy_pct >  -0.07
|   |   |--- weights: [3.00, 23.00] class: 1
```


## The live filter

`regime_model.joblib` — Gradient boosting → P&L directly, fitted on all 60 sessions
(3092 trades). The paper scanner scores every base-strategy signal with it and
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
