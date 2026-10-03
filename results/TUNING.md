# Parameter tuning — train/test split

Generated 2026-10-03 · optimized on the first **36 sessions**
(before 2026-08-31), validated on the held-out **24 sessions** · objective:
**expectancy per trade** (never win rate — see v0.1) · parameter sets with fewer
than 20 train trades are discarded as noise.

| strategy | best params (train) | train exp./trade | test exp./trade | test exp. (defaults) | test trades | test win rate | test P&L |
|---|---|---|---|---|---|---|---|
| Gap & Go | n/a (too few trades) | — | — | $+176.27 | 3 | — | — |
| Opening Range Breakout | {'range_bars': 3, 'target_r': 2.0, 'stop_at_mid': False} | $-0.74 | $+10.35 | $+10.35 | 115 | 42.6% | $+1,190 |
| VWAP Pullback | {'target_r': 2.0, 'stop_buffer': 0.997} | $-19.57 | $-28.74 | $-28.74 | 178 | 30.3% | $-5,115 |
| EMA 9/20 Crossover | {'fast': 5, 'slow': 13, 'stop_bars': 5} | $-12.12 | $-23.91 | $-18.54 | 236 | 19.1% | $-5,643 |
| RSI(2) Reversion | {'entry_level': 10.0, 'exit_level': 70.0, 'stop_pct': 0.005} | $-11.66 | $-10.84 | $-10.15 | 269 | 46.5% | $-2,916 |
| News Momentum | {'window_min': 60, 'vol_mult': 1.5, 'target_r': 3.0} | $-15.36 | $-30.58 | $-29.49 | 24 | 29.2% | $-734 |
| Squeeze Breakout | {'bw_lookback': 12, 'target_r': 1.5} | $-28.63 | $-4.56 | $-4.25 | 104 | 39.4% | $-474 |
| High-Break ATR Trail | {'window_bars': 6, 'trail_atr_mult': 3.0} | $-19.79 | $-11.87 | $-9.03 | 122 | 41.8% | $-1,448 |
| AR Forecast | {'lags': 6, 'horizon': 3, 'threshold': 0.002} | $-3.98 | $-12.85 | $-3.73 | 99 | 39.4% | $-1,273 |

![Train vs test expectancy](tuning_shrinkage.png)

## How to read this

- **train → test shrinkage is the overfitting, made visible.** Parameters that
  look best in-sample routinely give most of it back out-of-sample; the gap
  between the two columns is the honest measure of how much the grid search
  just memorized.
- **"test exp. (defaults)"** is the untuned textbook strategy on the same
  held-out sessions — the bar tuning has to beat to claim any value.
- With ~24 test sessions this is still a small sample; treat survivors as
  candidates for paper trading, not conclusions.

## Live promotion (survivor gate)

A tuned set trades live as `<strategy>_tuned` only once it has been the grid's
winner with **identical parameters** and has **beaten the defaults on the held-out
split** in each of the last 3 weekly runs. Everything else keeps
trading on defaults only.

| strategy | live | why |
|---|---|---|
| Opening Range Breakout | held back | did not beat the defaults on held-out data in all 3 runs |
| VWAP Pullback | held back | best parameters changed within the last 3 runs |
| EMA 9/20 Crossover | held back | best parameters changed within the last 3 runs |
| RSI(2) Reversion | held back | best parameters changed within the last 3 runs |
| News Momentum | held back | best parameters changed within the last 3 runs |
| Squeeze Breakout | held back | did not beat the defaults on held-out data in all 3 runs |
| High-Break ATR Trail | held back | best parameters changed within the last 3 runs |
| AR Forecast | held back | best parameters changed within the last 3 runs |

Consecutive runs share most of their 60-day window, so passing shows the result
*persists*, not that it's independently confirmed — the live `_tuned` vs default
comparison in the paper journal is the real test.
