# Regime filters — learned from the journal, validated walk-forward

Generated 2026-09-19 · 60 sessions (2026-06-25 → 2026-09-18) ·
**walk-forward:** first 20 sessions train-only, then blocks of 5 sessions scored by a
model trained on every session before them · **40 out-of-sample sessions** · decision rule:
keep a trade when its predicted expected value is positive (classifiers: P(win)·avg_win +
(1−P(win))·avg_loss with averages from the training fold; regressors: predicted P&L) ·
"random same-size" = mean expectancy of 2,000 random subsets with the same trade count.

**Gate met on this window (pending paper confirmation).** The Gradient boosting → P&L directly filter's kept trades have positive out-of-sample expectancy ($+5.02/trade) and sit at the 100th percentile of same-size random selections — the model is selecting on regime, not luck.

## Models

| model | OOS trades | kept | exp./trade, all | exp./trade, kept | PF all → kept | random same-size | pctile vs random |
|---|---|---|---|---|---|---|---|
| Gradient boosting → P&L directly | 2040 | 312 (15%) | $-11.66 | $+5.02 | 0.72 → 1.16 | $-11.67 | 100 |
| Ridge regression → P&L directly | 2040 | 624 (31%) | $-11.66 | $-2.09 | 0.72 → 0.94 | $-11.63 | 100 |
| Gradient boosting → P(win) → EV | 2040 | 311 (15%) | $-11.66 | $-7.75 | 0.72 → 0.86 | $-11.69 | 75 |
| Logistic regression → P(win) → EV | 2040 | 249 (12%) | $-11.66 | $-1.78 | 0.72 → 0.97 | $-11.59 | 93 |

![OOS cumulative P&L with vs without the filter](regime_oos.png)

*Read the curves with care: a filtered line holds fewer trades, so its total shrinks
mechanically even under random selection. The fair comparison is expectancy per
trade against the "random same-size" column, not the gap between the curves.*

## Calibration — does a higher predicted EV actually pay? (Gradient boosting → P&L directly)

| predicted-EV quintile | trades | mean predicted EV | actual exp./trade | win rate |
|---|---|---|---|---|
| 1 (lowest) | 408 | $-66.74 | $-19.00 | 35% |
| 2 | 408 | $-39.18 | $-13.87 | 33% |
| 3 | 408 | $-24.56 | $-14.81 | 36% |
| 4 | 408 | $-7.84 | $-10.95 | 45% |
| 5 (highest) | 408 | $+7.25 | $+0.34 | 47% |

A filter is only as good as this table is monotonic. If the top quintile does not
out-earn the bottom one out of sample, the model has learned to rank trades by
something other than what pays.

## Per strategy — Gradient boosting → P&L directly filter, out-of-sample only

| strategy | OOS trades | kept | exp./trade, all | exp./trade, kept | PF all → kept | P&L all → kept | random same-size | pctile vs random |
|---|---|---|---|---|---|---|---|---|
| Gap & Go | 10 | 4 (40%) ⚠ | $+120.18 | $+274.69 | 2.22 → ∞ | $+1,201.79 → $+1,098.75 | $+119.95 | 85 |
| Opening Range Breakout | 213 | 32 (15%) | $+4.48 | $+65.09 | 1.05 → 1.94 | $+953.33 → $+2,082.97 | $+3.43 | 96 |
| VWAP Pullback | 289 | 2 (1%) ⚠ | $-23.73 | $-92.58 | 0.58 → 0.00 | $-6,858.30 → $-185.16 | $-22.90 | 13 |
| EMA 9/20 Crossover | 245 | 0 (0%) ⚠ | $-9.58 | — | 0.72 → — | $-2,347.75 → $+0.00 | — | — |
| RSI(2) Reversion | 486 | 176 (36%) | $-12.46 | $-10.91 | 0.43 → 0.53 | $-6,057.21 → $-1,920.43 | $-12.45 | 72 |
| News Momentum | 28 | 0 (0%) ⚠ | $-26.46 | — | 0.52 → — | $-740.75 → $+0.00 | — | — |
| Squeeze Breakout | 172 | 0 (0%) ⚠ | $-22.60 | — | 0.47 → — | $-3,886.69 → $+0.00 | — | — |
| High-Break ATR Trail | 169 | 7 (4%) ⚠ | $-20.37 | $+97.23 | 0.68 → 2.06 | $-3,443.16 → $+680.62 | $-19.14 | 98 |
| AR Forecast | 428 | 91 (21%) | $-6.08 | $-2.08 | 0.79 → 0.94 | $-2,603.63 → $-189.00 | $-6.18 | 74 |
| **All strategies** | 2040 | 312 (15%) | $-11.66 | $+5.02 | 0.72 → 1.16 | $-23,782.37 → $+1,567.75 | $-11.67 | 100 |

⚠ = fewer than 10 kept trades; noise, not evidence. "pctile vs random" is where
the filtered expectancy lands among 2,000 random subsets of the same size (≥95 = the selection
is doing something chance rarely does).

## Fold by fold — Gradient boosting → P&L directly

| fold | test sessions | train sessions | trades | kept | exp./trade, all | exp./trade, kept |
|---|---|---|---|---|---|---|
| 1 | 2026-07-24 → 2026-07-30 | 20 | 271 | 62 | $-17.15 | $-13.28 |
| 2 | 2026-07-31 → 2026-08-06 | 25 | 255 | 38 | $-19.50 | $-15.67 |
| 3 | 2026-08-07 → 2026-08-13 | 30 | 266 | 54 | $-23.29 | $-4.29 |
| 4 | 2026-08-14 → 2026-08-20 | 35 | 261 | 36 | $-10.09 | $+65.09 |
| 5 | 2026-08-21 → 2026-08-27 | 40 | 251 | 39 | $-16.06 | $+16.64 |
| 6 | 2026-08-28 → 2026-09-03 | 45 | 249 | 49 | $+11.44 | $-0.87 |
| 7 | 2026-09-04 → 2026-09-11 | 50 | 238 | 13 | $-7.52 | $-34.00 |
| 8 | 2026-09-14 → 2026-09-18 | 55 | 249 | 21 | $-9.49 | $+33.84 |

## What the filter looks at

Permutation importance measured on the decision that matters: how much OOS
filtered expectancy falls when one feature is shuffled in the test fold.

| feature | OOS expectancy drop when shuffled |
|---|---|
| aligned_trend_slope_pct | $+16.15 |
| aligned_change_open_pct | $+4.30 |
| mkt_gap_pct | $+3.55 |
| aligned_dist_vwap_pct | $+1.62 |
| mkt_atr_pct | $+1.48 |
| mkt_dist_vwap_pct | $+1.42 |
| hour_et | $+1.38 |
| mkt_rel_volume | $+1.20 |

Features prefixed `aligned_` are signed by trade direction (a short's SPY move is
negated), so one pooled model can treat "long in a rising tape" and "short in a
falling tape" as the same regime.

## Paper-journal check (real fills, different execution path)

A filter fitted only on backtest sessions before the paper loop's first fill
(2026-08-24) was applied to the **388 real paper trades** from
2026-08-24 to 2026-09-18. It kept 50; expectancy
$-8.10 → $-18.51/trade
(35th percentile vs same-size random selection). Small
sample — a direction check, not a verdict.

## Descriptive rules (in-sample, for reading — not evidence)

Depth-2 decision trees per strategy on the full window, so the filter's opinion is
legible. `weights: [losers, winners]` per leaf. These were fit on all sessions and
prove nothing; the walk-forward tables above are the evidence.

**Opening Range Breakout**

```
|--- mkt_change_open_pct <= 1.96
|   |--- mkt_gap_pct <= -1.64
|   |   |--- weights: [41.00, 11.00] class: 0
|   |--- mkt_gap_pct >  -1.64
|   |   |--- weights: [109.00, 94.00] class: 0
|--- mkt_change_open_pct >  1.96
|   |--- aligned_range_pos <= 0.94
|   |   |--- weights: [9.00, 33.00] class: 1
|   |--- aligned_range_pos >  0.94
|   |   |--- weights: [12.00, 8.00] class: 0
```

**VWAP Pullback**

```
|--- mkt_realized_vol_pct <= 2.83
|   |--- mkt_trend_slope_pct <= 0.04
|   |   |--- weights: [71.00, 57.00] class: 0
|   |--- mkt_trend_slope_pct >  0.04
|   |   |--- weights: [13.00, 2.00] class: 0
|--- mkt_realized_vol_pct >  2.83
|   |--- aligned_change_open_pct <= 0.81
|   |   |--- weights: [84.00, 17.00] class: 0
|   |--- aligned_change_open_pct >  0.81
|   |   |--- weights: [121.00, 63.00] class: 0
```

**EMA 9/20 Crossover**

```
|--- mkt_realized_vol_pct <= 4.40
|   |--- mkt_range_pos <= 0.30
|   |   |--- weights: [46.00, 26.00] class: 0
|   |--- mkt_range_pos >  0.30
|   |   |--- weights: [181.00, 48.00] class: 0
|--- mkt_realized_vol_pct >  4.40
|   |--- aligned_spy_pct <= -0.19
|   |   |--- weights: [5.00, 12.00] class: 1
|   |--- aligned_spy_pct >  -0.19
|   |   |--- weights: [23.00, 16.00] class: 0
```

**RSI(2) Reversion**

```
|--- aligned_spy_pct <= 0.55
|   |--- mkt_gap_pct <= 4.61
|   |   |--- weights: [341.00, 274.00] class: 0
|   |--- mkt_gap_pct >  4.61
|   |   |--- weights: [4.00, 22.00] class: 1
|--- aligned_spy_pct >  0.55
|   |--- aligned_dist_vwap_pct <= 0.44
|   |   |--- weights: [0.00, 18.00] class: 1
|   |--- aligned_dist_vwap_pct >  0.44
|   |   |--- weights: [26.00, 44.00] class: 1
```

**News Momentum**

```
|--- mkt_autocorr_1 <= 0.04
|   |--- weights: [19.00, 4.00] class: 0
|--- mkt_autocorr_1 >  0.04
|   |--- weights: [6.00, 11.00] class: 1
```

**Squeeze Breakout**

```
|--- mkt_gap_pct <= 0.92
|   |--- mkt_autocorr_1 <= 0.07
|   |   |--- weights: [105.00, 36.00] class: 0
|   |--- mkt_autocorr_1 >  0.07
|   |   |--- weights: [42.00, 2.00] class: 0
|--- mkt_gap_pct >  0.92
|   |--- hour_et <= 13.71
|   |   |--- weights: [22.00, 21.00] class: 0
|   |--- hour_et >  13.71
|   |   |--- weights: [29.00, 8.00] class: 0
```

**High-Break ATR Trail**

```
|--- mkt_rel_volume <= 0.57
|   |--- mkt_realized_vol_pct <= 3.04
|   |   |--- weights: [12.00, 3.00] class: 0
|   |--- mkt_realized_vol_pct >  3.04
|   |   |--- weights: [20.00, 0.00] class: 0
|--- mkt_rel_volume >  0.57
|   |--- aligned_spy_pct <= -0.18
|   |   |--- weights: [9.00, 18.00] class: 1
|   |--- aligned_spy_pct >  -0.18
|   |   |--- weights: [135.00, 71.00] class: 0
```

**AR Forecast**

```
|--- aligned_change_open_pct <= 5.06
|   |--- mkt_rel_volume <= 0.37
|   |   |--- weights: [46.00, 17.00] class: 0
|   |--- mkt_rel_volume >  0.37
|   |   |--- weights: [300.00, 260.00] class: 0
|--- aligned_change_open_pct >  5.06
|   |--- weights: [3.00, 18.00] class: 1
```


## The live filter

`regime_model.joblib` — Gradient boosting → P&L directly, fitted on all 60 sessions
(3060 trades). The paper scanner scores every base-strategy signal with it and
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
