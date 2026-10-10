# Regime filters — learned from the journal, validated walk-forward

Generated 2026-10-10 · 60 sessions (2026-07-17 → 2026-10-09) ·
**walk-forward:** first 20 sessions train-only, then blocks of 5 sessions scored by a
model trained on every session before them · **40 out-of-sample sessions** · decision rule:
keep a trade when its predicted expected value is positive (classifiers: P(win)·avg_win +
(1−P(win))·avg_loss with averages from the training fold; regressors: predicted P&L) ·
"random same-size" = mean expectancy of 2,000 random subsets with the same trade count.

**Gate met on this window (pending paper confirmation).** The Gradient boosting → P&L directly filter's kept trades have positive out-of-sample expectancy ($+5.44/trade) and sit at the 98th percentile of same-size random selections — the model is selecting on regime, not luck.

## Models

| model | OOS trades | kept | exp./trade, all | exp./trade, kept | PF all → kept | random same-size | pctile vs random |
|---|---|---|---|---|---|---|---|
| Gradient boosting → P&L directly | 2021 | 165 (8%) | $-10.26 | $+5.44 | 0.73 → 1.17 | $-10.05 | 98 |
| Ridge regression → P&L directly | 2021 | 376 (19%) | $-10.26 | $+2.25 | 0.73 → 1.06 | $-10.23 | 100 |
| Gradient boosting → P(win) → EV | 2021 | 275 (14%) | $-10.26 | $+3.91 | 0.73 → 1.08 | $-10.30 | 99 |
| Logistic regression → P(win) → EV | 2021 | 172 (9%) | $-10.26 | $+9.75 | 0.73 → 1.18 | $-10.17 | 100 |

![OOS cumulative P&L with vs without the filter](regime_oos.png)

*Read the curves with care: a filtered line holds fewer trades, so its total shrinks
mechanically even under random selection. The fair comparison is expectancy per
trade against the "random same-size" column, not the gap between the curves.*

## Calibration — does a higher predicted EV actually pay? (Gradient boosting → P&L directly)

| predicted-EV quintile | trades | mean predicted EV | actual exp./trade | win rate |
|---|---|---|---|---|
| 1 (lowest) | 405 | $-65.42 | $-14.64 | 34% |
| 2 | 404 | $-37.68 | $-16.51 | 32% |
| 3 | 404 | $-24.56 | $-10.48 | 36% |
| 4 | 404 | $-10.93 | $-6.15 | 43% |
| 5 (highest) | 404 | $+2.04 | $-3.50 | 44% |

A filter is only as good as this table is monotonic. If the top quintile does not
out-earn the bottom one out of sample, the model has learned to rank trades by
something other than what pays.

## Per strategy — Gradient boosting → P&L directly filter, out-of-sample only

| strategy | OOS trades | kept | exp./trade, all | exp./trade, kept | PF all → kept | P&L all → kept | random same-size | pctile vs random |
|---|---|---|---|---|---|---|---|---|
| Gap & Go | 8 | 1 (12%) ⚠ | $+257.58 | $+424.16 | 71.52 → ∞ | $+2,060.63 → $+424.16 | $+251.56 | 77 |
| Opening Range Breakout | 194 | 15 (8%) | $+2.56 | $+54.38 | 1.03 → 1.75 | $+496.07 → $+815.71 | $+3.25 | 84 |
| VWAP Pullback | 295 | 1 (0%) ⚠ | $-20.29 | $+112.82 | 0.61 → ∞ | $-5,986.50 → $+112.82 | $-24.16 | 88 |
| EMA 9/20 Crossover | 263 | 0 (0%) ⚠ | $-12.87 | — | 0.63 → — | $-3,384.50 → $+0.00 | — | — |
| RSI(2) Reversion | 467 | 96 (21%) | $-10.97 | $-9.16 | 0.41 → 0.52 | $-5,123.06 → $-879.72 | $-10.85 | 67 |
| News Momentum | 32 | 0 (0%) ⚠ | $-22.10 | — | 0.54 → — | $-707.23 → $+0.00 | — | — |
| Squeeze Breakout | 174 | 0 (0%) ⚠ | $-14.74 | — | 0.59 → — | $-2,564.29 → $+0.00 | — | — |
| High-Break ATR Trail | 168 | 5 (3%) ⚠ | $-16.84 | $+35.64 | 0.71 → 1.37 | $-2,828.56 → $+178.18 | $-15.93 | 82 |
| AR Forecast | 420 | 47 (11%) | $-6.41 | $+5.23 | 0.75 → 1.14 | $-2,691.18 → $+246.02 | $-6.45 | 92 |
| **All strategies** | 2021 | 165 (8%) | $-10.26 | $+5.44 | 0.73 → 1.17 | $-20,728.62 → $+897.17 | $-10.05 | 98 |

⚠ = fewer than 10 kept trades; noise, not evidence. "pctile vs random" is where
the filtered expectancy lands among 2,000 random subsets of the same size (≥95 = the selection
is doing something chance rarely does).

## Long vs short — side policies, out-of-sample only (Gradient boosting → P&L directly)

| book | trades | exp./trade | profit factor | P&L | pctile vs random same-size |
|---|---|---|---|---|---|
| Unfiltered, both sides | 2021 | $-10.26 | 0.73 | $-20,728.62 | — |
| Long only (unfiltered) | 1070 | $-11.82 | 0.71 | $-12,643.55 | 22 |
| Short only (unfiltered) | 951 | $-8.50 | 0.76 | $-8,085.07 | 77 |
| Filter on every trade (`_regime` variants) | 165 | $+5.44 | 1.17 | $+897.17 | 97 |
| Live policy: shorts unfiltered, longs only when EV > 0, orb exempt | 1147 | $-6.23 | 0.84 | $-7,141.56 | 98 |

The live paper scanner runs the last row (`long_gate="regime"`). "Long only" /
"Short only" answer whether one side alone carries the losses; the live policy
is only worth keeping if it beats the unfiltered book *and* sits well above
random same-size selection. Unlike the paper journal, these are backtest fills.

## Fold by fold — Gradient boosting → P&L directly

| fold | test sessions | train sessions | trades | kept | exp./trade, all | exp./trade, kept |
|---|---|---|---|---|---|---|
| 1 | 2026-08-14 → 2026-08-20 | 20 | 264 | 20 | $-10.42 | $+18.45 |
| 2 | 2026-08-21 → 2026-08-27 | 25 | 253 | 36 | $-15.79 | $-10.59 |
| 3 | 2026-08-28 → 2026-09-03 | 30 | 249 | 29 | $+11.10 | $+27.12 |
| 4 | 2026-09-04 → 2026-09-11 | 35 | 238 | 16 | $-7.79 | $+13.83 |
| 5 | 2026-09-14 → 2026-09-18 | 40 | 252 | 14 | $-10.32 | $-5.34 |
| 6 | 2026-09-21 → 2026-09-25 | 45 | 250 | 18 | $-19.65 | $+43.63 |
| 7 | 2026-09-28 → 2026-10-02 | 50 | 258 | 17 | $-15.03 | $-18.56 |
| 8 | 2026-10-05 → 2026-10-09 | 55 | 257 | 15 | $-13.63 | $-32.90 |

## What the filter looks at

Permutation importance measured on the decision that matters: how much OOS
filtered expectancy falls when one feature is shuffled in the test fold.

| feature | OOS expectancy drop when shuffled |
|---|---|
| mkt_trend_slope_pct | $+10.41 |
| mkt_change_open_pct | $+9.48 |
| aligned_trend_slope_pct | $+6.40 |
| mkt_autocorr_1 | $+5.39 |
| aligned_range_pos | $+3.37 |
| hour_et | $+2.98 |
| mkt_range_pos | $+2.74 |
| aligned_change_open_pct | $+2.27 |

Features prefixed `aligned_` are signed by trade direction (a short's SPY move is
negated), so one pooled model can treat "long in a rising tape" and "short in a
falling tape" as the same regime.

## Paper-journal check (real fills, different execution path)

A filter fitted only on backtest sessions before the paper loop's first fill
(2026-08-24) was applied to the **704 real paper trades** from
2026-08-24 to 2026-10-09. It kept 51; expectancy
$-11.60 → $+4.10/trade
(80th percentile vs same-size random selection). Small
sample — a direction check, not a verdict.

## Descriptive rules (in-sample, for reading — not evidence)

Depth-2 decision trees per strategy on the full window, so the filter's opinion is
legible. `weights: [losers, winners]` per leaf. These were fit on all sessions and
prove nothing; the walk-forward tables above are the evidence.

**Opening Range Breakout**

```
|--- aligned_change_open_pct <= 1.48
|   |--- aligned_range_pos <= -0.13
|   |   |--- weights: [17.00, 19.00] class: 1
|   |--- aligned_range_pos >  -0.13
|   |   |--- weights: [99.00, 41.00] class: 0
|--- aligned_change_open_pct >  1.48
|   |--- mkt_rel_volume <= 0.71
|   |   |--- weights: [27.00, 48.00] class: 1
|   |--- mkt_rel_volume >  0.71
|   |   |--- weights: [34.00, 22.00] class: 0
```

**VWAP Pullback**

```
|--- mkt_realized_vol_pct <= 2.37
|   |--- mkt_realized_vol_pct <= 2.24
|   |   |--- weights: [69.00, 42.00] class: 0
|   |--- mkt_realized_vol_pct >  2.24
|   |   |--- weights: [4.00, 11.00] class: 1
|--- mkt_realized_vol_pct >  2.37
|   |--- aligned_change_open_pct <= 0.89
|   |   |--- weights: [107.00, 25.00] class: 0
|   |--- aligned_change_open_pct >  0.89
|   |   |--- weights: [124.00, 61.00] class: 0
```

**EMA 9/20 Crossover**

```
|--- mkt_realized_vol_pct <= 4.38
|   |--- aligned_range_pos <= -0.54
|   |   |--- weights: [7.00, 8.00] class: 1
|   |--- aligned_range_pos >  -0.54
|   |   |--- weights: [247.00, 82.00] class: 0
|--- mkt_realized_vol_pct >  4.38
|   |--- aligned_spy_pct <= -0.04
|   |   |--- weights: [4.00, 12.00] class: 1
|   |--- aligned_spy_pct >  -0.04
|   |   |--- weights: [16.00, 9.00] class: 0
```

**RSI(2) Reversion**

```
|--- mkt_realized_vol_pct <= 1.75
|   |--- aligned_spy_pct <= -0.21
|   |   |--- weights: [7.00, 11.00] class: 1
|   |--- aligned_spy_pct >  -0.21
|   |   |--- weights: [72.00, 18.00] class: 0
|--- mkt_realized_vol_pct >  1.75
|   |--- aligned_spy_pct <= 0.55
|   |   |--- weights: [284.00, 259.00] class: 0
|   |--- aligned_spy_pct >  0.55
|   |   |--- weights: [20.00, 45.00] class: 1
```

**News Momentum**

```
|--- mkt_autocorr_1 <= 0.07
|   |--- mkt_realized_vol_pct <= 2.00
|   |   |--- weights: [10.00, 6.00] class: 0
|   |--- mkt_realized_vol_pct >  2.00
|   |   |--- weights: [17.00, 1.00] class: 0
|--- mkt_autocorr_1 >  0.07
|   |--- weights: [6.00, 9.00] class: 1
```

**Squeeze Breakout**

```
|--- mkt_gap_pct <= 0.87
|   |--- aligned_trend_slope_pct <= 0.03
|   |   |--- weights: [95.00, 36.00] class: 0
|   |--- aligned_trend_slope_pct >  0.03
|   |   |--- weights: [40.00, 4.00] class: 0
|--- mkt_gap_pct >  0.87
|   |--- mkt_spy_change_pct <= -0.13
|   |   |--- weights: [12.00, 21.00] class: 1
|   |--- mkt_spy_change_pct >  -0.13
|   |   |--- weights: [42.00, 15.00] class: 0
```

**High-Break ATR Trail**

```
|--- aligned_spy_pct <= -0.17
|   |--- mkt_atr_pct <= 0.74
|   |   |--- weights: [12.00, 3.00] class: 0
|   |--- mkt_atr_pct >  0.74
|   |   |--- weights: [3.00, 15.00] class: 1
|--- aligned_spy_pct >  -0.17
|   |--- aligned_range_pos <= 0.98
|   |   |--- weights: [140.00, 63.00] class: 0
|   |--- aligned_range_pos >  0.98
|   |   |--- weights: [23.00, 1.00] class: 0
```

**AR Forecast**

```
|--- aligned_change_open_pct <= 5.25
|   |--- aligned_change_open_pct <= 3.60
|   |   |--- weights: [327.00, 253.00] class: 0
|   |--- aligned_change_open_pct >  3.60
|   |   |--- weights: [21.00, 4.00] class: 0
|--- aligned_change_open_pct >  5.25
|   |--- weights: [3.00, 13.00] class: 1
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
