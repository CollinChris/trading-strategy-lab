# Parameter tuning — train/test split

Generated 2026-09-06 · optimized on the first **36 sessions**
(before 2026-08-04), validated on the held-out **24 sessions** · objective:
**expectancy per trade** (never win rate — see v0.1) · parameter sets with fewer
than 20 train trades are discarded as noise.

| strategy | best params (train) | train exp./trade | test exp./trade | test exp. (defaults) | test trades | test win rate | test P&L |
|---|---|---|---|---|---|---|---|
| Gap & Go | n/a (too few trades) | — | — | $+186.05 | 5 | — | — |
| Opening Range Breakout | {'range_bars': 6, 'target_r': 1.5, 'stop_at_mid': False} | $+5.95 | $+3.56 | $+9.05 | 71 | 47.9% | $+253 |
| VWAP Pullback | {'target_r': 3.0, 'stop_buffer': 0.995} | $-7.55 | $-25.40 | $-25.82 | 98 | 32.7% | $-2,489 |
| EMA 9/20 Crossover | {'fast': 5, 'slow': 13, 'stop_bars': 10} | $+0.18 | $-23.44 | $-26.48 | 140 | 19.3% | $-3,281 |
| RSI(2) Reversion | {'entry_level': 15.0, 'exit_level': 70.0, 'stop_pct': 0.005} | $-9.03 | $-10.90 | $-12.83 | 218 | 47.2% | $-2,376 |
| News Momentum | {'window_min': 60, 'vol_mult': 1.5, 'target_r': 3.0} | $+7.95 | $-10.86 | $-34.25 | 14 | 28.6% | $-152 |
| Squeeze Breakout | {'bw_lookback': 6, 'target_r': 1.5} | $-9.82 | $-34.11 | $-23.53 | 77 | 23.4% | $-2,627 |
| High-Break ATR Trail | {'window_bars': 6, 'trail_atr_mult': 1.5} | $+6.69 | $+9.11 | $-7.10 | 81 | 35.8% | $+738 |
| AR Forecast | {'lags': 12, 'horizon': 12, 'threshold': 0.002} | $+0.09 | $-9.45 | $-12.55 | 198 | 37.9% | $-1,872 |

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
