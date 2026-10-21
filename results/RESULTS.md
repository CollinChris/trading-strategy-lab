# Backtest results

Generated 2026-10-20 · window **2026-07-28 → 2026-10-20** ·
symbols **NVDA, TSLA, COIN, AMZN, JPM, XOM, UNH, WMT, CAT, LLY** · bars **5m** ·
**$10,000** per trade · slippage **5 bps/side** ·
**2323 long / 2322 short**, everything flat by 15:55 ET.

## Ranking (by win rate)

| strategy | trades | win_rate_pct | avg_win | avg_loss | profit_factor | expectancy | total_pnl | max_drawdown | median_hold_min |
|---|---|---|---|---|---|---|---|---|---|
| Gap & Go | 5 | 60.0 | 263.2 | -108.04 | 3.65 | 114.7 | 573.51 | -166.04 | 350.0 |
| Opening Range Breakout | 503 | 41.7 | 102.79 | -94.2 | 0.78 | -11.95 | -6012.9 | -8457.78 | 340.0 |
| AR Forecast | 670 | 40.6 | 32.42 | -36.1 | 0.61 | -8.28 | -5547.94 | -5710.63 | 25.0 |
| RSI(2) Reversion | 1173 | 36.1 | 11.63 | -21.14 | 0.31 | -9.32 | -10937.76 | -11048.23 | 15.0 |
| VWAP Pullback | 714 | 35.4 | 70.93 | -58.88 | 0.66 | -12.88 | -9196.87 | -10932.21 | 125.0 |
| High-Break ATR Trail | 437 | 33.2 | 67.26 | -57.9 | 0.58 | -16.37 | -7154.44 | -8462.71 | 150.0 |
| News Momentum | 72 | 29.2 | 63.17 | -51.07 | 0.51 | -17.75 | -1277.96 | -1507.81 | 80.0 |
| Squeeze Breakout | 421 | 27.3 | 44.9 | -38.63 | 0.44 | -15.82 | -6659.24 | -6919.02 | 50.0 |
| EMA 9/20 Crossover | 650 | 24.8 | 53.89 | -34.23 | 0.52 | -12.4 | -8060.99 | -8112.84 | 58.0 |

Win rate alone doesn't pay — a high-win-rate strategy with avg losses larger than
avg wins can still lose money. Read it together with **profit_factor** (gross
wins / gross losses, >1 is profitable) and **expectancy** (avg $ per trade).

![Cumulative P&L by strategy](equity_curves.png)

## How each strategy's trades ended (% of trades)

| strategy | eod | signal | stop | target |
|---|---|---|---|---|
| AR Forecast | 0.0 | 94.3 | 5.7 | 0.0 |
| EMA 9/20 Crossover | 21.5 | 58.0 | 20.5 | 0.0 |
| Gap & Go | 80.0 | 0.0 | 20.0 | 0.0 |
| High-Break ATR Trail | 32.7 | 0.0 | 67.3 | 0.0 |
| News Momentum | 40.3 | 0.0 | 50.0 | 9.7 |
| Opening Range Breakout | 72.2 | 0.0 | 23.9 | 4.0 |
| RSI(2) Reversion | 1.0 | 94.5 | 4.4 | 0.0 |
| Squeeze Breakout | 28.5 | 0.0 | 59.9 | 11.6 |
| VWAP Pullback | 37.7 | 0.0 | 49.9 | 12.5 |

`stop` = protective stop hit · `target` = fixed take-profit hit ·
`signal` = strategy's own exit rule · `eod` = flattened at the session cutoff.

## Long vs short, per strategy

| strategy | long trades | long exp./trade | short trades | short exp./trade |
|---|---|---|---|---|
| Gap & Go | 3 | $+144.22 | 2 | $+70.43 |
| Opening Range Breakout | 253 | $-20.45 | 250 | $-3.36 |
| VWAP Pullback | 358 | $-18.57 | 356 | $-7.16 |
| EMA 9/20 Crossover | 339 | $-17.20 | 311 | $-7.18 |
| RSI(2) Reversion | 563 | $-9.55 | 610 | $-9.11 |
| News Momentum | 37 | $-18.94 | 35 | $-16.50 |
| Squeeze Breakout | 217 | $-17.74 | 204 | $-13.77 |
| High-Break ATR Trail | 226 | $-18.43 | 211 | $-14.16 |
| AR Forecast | 327 | $-9.85 | 343 | $-6.78 |

Each side read as its own book. The walk-forward version of this question — with
the live long-gate policy scored against random selection — is in REGIME.md.

Full trade-by-trade log: [trades.csv](trades.csv).

*Small sample (yfinance caps 5-minute history at 60 days), one market regime,
liquid large caps rather than true low-float gappers — see the README's
limitations section before reading anything into these numbers.*
