# Parameter tuning — train/test split

Generated 2026-09-26 · optimized on the first **36 sessions**
(before 2026-08-24), validated on the held-out **24 sessions** · objective:
**expectancy per trade** (never win rate — see v0.1) · parameter sets with fewer
than 20 train trades are discarded as noise.

| strategy | best params (train) | train exp./trade | test exp./trade | test exp. (defaults) | test trades | test win rate | test P&L |
|---|---|---|---|---|---|---|---|
| Gap & Go | n/a (too few trades) | — | — | $+268.92 | 6 | — | — |
| Opening Range Breakout | {'range_bars': 3, 'target_r': 2.0, 'stop_at_mid': False} | $-17.29 | $+27.94 | $+27.94 | 117 | 47.0% | $+3,269 |
| VWAP Pullback | {'target_r': 2.0, 'stop_buffer': 0.997} | $-20.25 | $-20.79 | $-20.79 | 172 | 32.6% | $-3,575 |
| EMA 9/20 Crossover | {'fast': 12, 'slow': 13, 'stop_bars': 5} | $-10.89 | $-24.07 | $-20.66 | 175 | 22.3% | $-4,212 |
| RSI(2) Reversion | {'entry_level': 10.0, 'exit_level': 70.0, 'stop_pct': 0.02} | $-10.33 | $-9.34 | $-12.11 | 258 | 50.8% | $-2,410 |
| News Momentum | {'window_min': 60, 'vol_mult': 1.2, 'target_r': 1.5} | $-13.20 | $-9.36 | $-33.70 | 49 | 36.7% | $-459 |
| Squeeze Breakout | {'bw_lookback': 12, 'target_r': 1.5} | $-26.13 | $-11.16 | $-12.19 | 100 | 32.0% | $-1,116 |
| High-Break ATR Trail | {'window_bars': 6, 'trail_atr_mult': 1.5} | $-25.93 | $-7.80 | $-9.09 | 126 | 34.9% | $-983 |
| AR Forecast | {'lags': 12, 'horizon': 6, 'threshold': 0.001} | $-2.05 | $-2.43 | $-6.45 | 272 | 48.5% | $-661 |

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
