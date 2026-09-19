# Parameter tuning — train/test split

Generated 2026-09-19 · optimized on the first **36 sessions**
(before 2026-08-17), validated on the held-out **24 sessions** · objective:
**expectancy per trade** (never win rate — see v0.1) · parameter sets with fewer
than 20 train trades are discarded as noise.

| strategy | best params (train) | train exp./trade | test exp./trade | test exp. (defaults) | test trades | test win rate | test P&L |
|---|---|---|---|---|---|---|---|
| Gap & Go | n/a (too few trades) | — | — | $+298.55 | 7 | — | — |
| Opening Range Breakout | {'range_bars': 3, 'target_r': 2.0, 'stop_at_mid': False} | $-10.52 | $+31.11 | $+31.11 | 121 | 47.1% | $+3,765 |
| VWAP Pullback | {'target_r': 1.5, 'stop_buffer': 0.995} | $-19.31 | $-24.48 | $-22.55 | 161 | 35.4% | $-3,941 |
| EMA 9/20 Crossover | {'fast': 5, 'slow': 13, 'stop_bars': 5} | $-8.09 | $-17.58 | $-14.46 | 227 | 21.1% | $-3,991 |
| RSI(2) Reversion | {'entry_level': 10.0, 'exit_level': 70.0, 'stop_pct': 0.02} | $-9.08 | $-10.76 | $-12.52 | 270 | 49.6% | $-2,905 |
| News Momentum | {'window_min': 30, 'vol_mult': 1.2, 'target_r': 2.0} | $-7.48 | $-37.63 | $-32.59 | 22 | 22.7% | $-828 |
| Squeeze Breakout | {'bw_lookback': 12, 'target_r': 1.5} | $-21.18 | $-21.43 | $-21.71 | 100 | 25.0% | $-2,143 |
| High-Break ATR Trail | {'window_bars': 12, 'trail_atr_mult': 1.5} | $-22.04 | $+2.13 | $-0.82 | 100 | 36.0% | $+213 |
| AR Forecast | {'lags': 12, 'horizon': 6, 'threshold': 0.002} | $+1.23 | $-9.43 | $-8.88 | 220 | 41.4% | $-2,075 |

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
