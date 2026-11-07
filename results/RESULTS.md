# Backtest results

Generated 2026-11-07 · window **2026-08-14 → 2026-11-06** ·
symbols **NVDA, TSLA, COIN, AMZN, JPM, XOM, UNH, WMT, CAT, LLY** · bars **5m** ·
**$10,000** per trade · slippage **5 bps/side** ·
**2283 long / 2358 short**, everything flat by 15:55 ET.

## Ranking (by win rate)

| strategy | trades | win_rate_pct | avg_win | avg_loss | profit_factor | expectancy | total_pnl | max_drawdown | median_hold_min |
|---|---|---|---|---|---|---|---|---|---|
| Gap & Go | 4 | 75.0 | 263.2 | -58.27 | 13.55 | 182.83 | 731.32 | -58.27 | 348.0 |
| Opening Range Breakout | 500 | 39.6 | 105.43 | -94.21 | 0.73 | -15.15 | -7576.77 | -9014.44 | 340.0 |
| AR Forecast | 676 | 39.5 | 30.68 | -39.78 | 0.5 | -11.95 | -8080.24 | -8429.48 | 25.0 |
| RSI(2) Reversion | 1139 | 37.1 | 12.48 | -20.76 | 0.36 | -8.42 | -9587.3 | -9689.78 | 15.0 |
| VWAP Pullback | 709 | 35.7 | 74.75 | -57.51 | 0.72 | -10.31 | -7311.02 | -8505.88 | 135.0 |
| High-Break ATR Trail | 437 | 34.1 | 67.79 | -61.8 | 0.57 | -17.62 | -7698.27 | -7746.01 | 155.0 |
| News Momentum | 84 | 28.6 | 52.98 | -52.95 | 0.4 | -22.68 | -1905.36 | -1946.93 | 82.0 |
| Squeeze Breakout | 440 | 28.0 | 49.68 | -37.6 | 0.51 | -13.2 | -5808.95 | -6133.05 | 50.0 |
| EMA 9/20 Crossover | 652 | 23.6 | 55.64 | -33.5 | 0.51 | -12.45 | -8115.71 | -8180.82 | 60.0 |

Win rate alone doesn't pay — a high-win-rate strategy with avg losses larger than
avg wins can still lose money. Read it together with **profit_factor** (gross
wins / gross losses, >1 is profitable) and **expectancy** (avg $ per trade).

![Cumulative P&L by strategy](equity_curves.png)

## How each strategy's trades ended (% of trades)

| strategy | eod | signal | stop | target |
|---|---|---|---|---|
| AR Forecast | 0.0 | 91.6 | 8.4 | 0.0 |
| EMA 9/20 Crossover | 22.2 | 57.2 | 20.6 | 0.0 |
| Gap & Go | 100.0 | 0.0 | 0.0 | 0.0 |
| High-Break ATR Trail | 33.0 | 0.0 | 67.0 | 0.0 |
| News Momentum | 42.9 | 0.0 | 48.8 | 8.3 |
| Opening Range Breakout | 72.6 | 0.0 | 23.4 | 4.0 |
| RSI(2) Reversion | 0.7 | 94.8 | 4.5 | 0.0 |
| Squeeze Breakout | 28.4 | 0.0 | 59.1 | 12.5 |
| VWAP Pullback | 38.1 | 0.0 | 48.0 | 14.0 |

`stop` = protective stop hit · `target` = fixed take-profit hit ·
`signal` = strategy's own exit rule · `eod` = flattened at the session cutoff.

## Long vs short, per strategy

| strategy | long trades | long exp./trade | short trades | short exp./trade |
|---|---|---|---|---|
| Gap & Go | 2 | $+241.35 | 2 | $+124.31 |
| Opening Range Breakout | 249 | $-28.60 | 251 | $-1.81 |
| VWAP Pullback | 356 | $-18.81 | 353 | $-1.74 |
| EMA 9/20 Crossover | 336 | $-18.99 | 316 | $-5.49 |
| RSI(2) Reversion | 570 | $-8.89 | 569 | $-7.94 |
| News Momentum | 41 | $-29.59 | 43 | $-16.09 |
| Squeeze Breakout | 220 | $-17.84 | 220 | $-8.56 |
| High-Break ATR Trail | 218 | $-23.15 | 219 | $-12.11 |
| AR Forecast | 291 | $-12.08 | 385 | $-11.85 |

Each side read as its own book. The walk-forward version of this question — with
the live long-gate policy scored against random selection — is in REGIME.md.

Full trade-by-trade log: [trades.csv](trades.csv).

*Small sample (yfinance caps 5-minute history at 60 days), one market regime,
liquid large caps rather than true low-float gappers — see the README's
limitations section before reading anything into these numbers.*
