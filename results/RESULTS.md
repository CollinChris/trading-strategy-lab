# Backtest results

Generated 2026-08-28 · window **2026-06-03 → 2026-08-27** ·
symbols **TSLA, NVDA, AMD, PLTR, COIN, MSTR** · bars **5m** ·
**$10,000** per trade · slippage **5 bps/side** ·
long-only, everything flat by 15:55 ET.

## Ranking (by win rate)

| strategy | trades | win_rate_pct | avg_win | avg_loss | profit_factor | expectancy | total_pnl | max_drawdown | median_hold_min |
|---|---|---|---|---|---|---|---|---|---|
| Gap & Go | 5 | 60.0 | 332.62 | -331.13 | 1.51 | 67.12 | 335.6 | -400.2 | 330.0 |
| RSI(2) Reversion | 385 | 51.9 | 23.39 | -48.31 | 0.52 | -11.06 | -4259.1 | -4273.74 | 15.0 |
| Opening Range Breakout | 177 | 44.6 | 198.47 | -174.12 | 0.92 | -7.82 | -1384.78 | -4592.22 | 335.0 |
| AR Forecast | 545 | 43.5 | 50.04 | -53.45 | 0.72 | -8.44 | -4602.52 | -4947.63 | 20.0 |
| News Momentum | 27 | 40.7 | 86.19 | -79.41 | 0.75 | -11.94 | -322.38 | -516.84 | 50.0 |
| High-Break ATR Trail | 150 | 33.3 | 134.32 | -95.35 | 0.7 | -18.79 | -2819.04 | -3271.2 | 132.0 |
| VWAP Pullback | 247 | 31.6 | 116.75 | -85.59 | 0.63 | -21.7 | -5358.91 | -6171.79 | 45.0 |
| EMA 9/20 Crossover | 230 | 26.1 | 91.28 | -54.96 | 0.59 | -16.81 | -3865.34 | -4229.42 | 50.0 |
| Squeeze Breakout | 145 | 24.1 | 70.21 | -71.32 | 0.31 | -37.16 | -5387.61 | -5330.82 | 40.0 |

Win rate alone doesn't pay — a high-win-rate strategy with avg losses larger than
avg wins can still lose money. Read it together with **profit_factor** (gross
wins / gross losses, >1 is profitable) and **expectancy** (avg $ per trade).

![Cumulative P&L by strategy](equity_curves.png)

## How each strategy's trades ended (% of trades)

| strategy | eod | signal | stop | target |
|---|---|---|---|---|
| AR Forecast | 0.0 | 85.5 | 14.5 | 0.0 |
| EMA 9/20 Crossover | 20.9 | 57.4 | 21.7 | 0.0 |
| Gap & Go | 60.0 | 0.0 | 40.0 | 0.0 |
| High-Break ATR Trail | 29.3 | 0.0 | 70.7 | 0.0 |
| News Momentum | 25.9 | 0.0 | 51.9 | 22.2 |
| Opening Range Breakout | 67.2 | 0.0 | 26.6 | 6.2 |
| RSI(2) Reversion | 0.0 | 84.2 | 15.8 | 0.0 |
| Squeeze Breakout | 26.2 | 0.0 | 67.6 | 6.2 |
| VWAP Pullback | 18.2 | 0.0 | 62.8 | 19.0 |

`stop` = protective stop hit · `target` = fixed take-profit hit ·
`signal` = strategy's own exit rule · `eod` = flattened at the session cutoff.

Full trade-by-trade log: [trades.csv](trades.csv).

*Small sample (yfinance caps 5-minute history at 60 days), one market regime,
liquid large caps rather than true low-float gappers — see the README's
limitations section before reading anything into these numbers.*
