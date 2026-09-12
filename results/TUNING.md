# Parameter tuning — train/test split

Generated 2026-09-12 · optimized on the first **36 sessions**
(before 2026-08-10), validated on the held-out **24 sessions** · objective:
**expectancy per trade** (never win rate — see v0.1) · parameter sets with fewer
than 20 train trades are discarded as noise.

| strategy | best params (train) | train exp./trade | test exp./trade | test exp. (defaults) | test trades | test win rate | test P&L |
|---|---|---|---|---|---|---|---|
| Gap & Go | n/a (too few trades) | — | — | $+331.49 | 6 | — | — |
| Opening Range Breakout | {'range_bars': 3, 'target_r': 1.5, 'stop_at_mid': False} | $-8.20 | $-6.87 | $-0.10 | 126 | 44.4% | $-865 |
| VWAP Pullback | {'target_r': 3.0, 'stop_buffer': 0.995} | $-21.16 | $-13.53 | $-15.73 | 159 | 35.8% | $-2,151 |
| EMA 9/20 Crossover | {'fast': 12, 'slow': 13, 'stop_bars': 5} | $-11.84 | $-11.58 | $-9.62 | 175 | 26.3% | $-2,027 |
| RSI(2) Reversion | {'entry_level': 10.0, 'exit_level': 70.0, 'stop_pct': 0.02} | $-7.49 | $-11.05 | $-12.02 | 277 | 48.0% | $-3,060 |
| News Momentum | {'window_min': 30, 'vol_mult': 1.2, 'target_r': 1.5} | $-11.87 | $-18.92 | $+0.75 | 18 | 22.2% | $-341 |
| Squeeze Breakout | {'bw_lookback': 6, 'target_r': 1.5} | $-19.93 | $-19.45 | $-16.15 | 128 | 26.6% | $-2,489 |
| High-Break ATR Trail | {'window_bars': 12, 'trail_atr_mult': 1.5} | $-16.40 | $-7.65 | $-10.98 | 100 | 34.0% | $-765 |
| AR Forecast | {'lags': 12, 'horizon': 6, 'threshold': 0.002} | $-0.70 | $-5.85 | $-8.21 | 213 | 43.2% | $-1,246 |

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
