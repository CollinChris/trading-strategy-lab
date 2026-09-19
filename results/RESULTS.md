# Backtest results

Generated 2026-09-19 · window **2026-06-25 → 2026-09-18** ·
symbols **TSLA, NVDA, AMD, PLTR, COIN, MSTR** · bars **5m** ·
**$10,000** per trade · slippage **5 bps/side** ·
**1698 long / 1362 short**, everything flat by 15:55 ET.

## Ranking (by win rate)

| strategy | trades | win_rate_pct | avg_win | avg_loss | profit_factor | expectancy | total_pnl | max_drawdown | median_hold_min |
|---|---|---|---|---|---|---|---|---|---|
| Gap & Go | 12 | 66.7 | 273.4 | -374.61 | 1.46 | 57.4 | 688.8 | -1247.5 | 332.0 |
| RSI(2) Reversion | 729 | 49.1 | 21.99 | -43.59 | 0.49 | -11.38 | -8297.89 | -8785.02 | 15.0 |
| Opening Range Breakout | 317 | 46.1 | 196.21 | -157.57 | 1.06 | 5.37 | 1701.96 | -4680.6 | 340.0 |
| AR Forecast | 644 | 45.8 | 52.57 | -52.37 | 0.85 | -4.3 | -2766.48 | -4679.28 | 20.0 |
| News Momentum | 40 | 37.5 | 76.17 | -81.6 | 0.56 | -22.43 | -897.34 | -971.34 | 55.0 |
| High-Break ATR Trail | 268 | 34.3 | 122.45 | -98.94 | 0.65 | -22.94 | -6147.23 | -8155.61 | 158.0 |
| VWAP Pullback | 428 | 32.5 | 112.79 | -85.23 | 0.64 | -20.92 | -8953.55 | -8901.09 | 60.0 |
| EMA 9/20 Crossover | 357 | 28.6 | 86.41 | -51.08 | 0.68 | -11.8 | -4210.95 | -5257.58 | 60.0 |
| Squeeze Breakout | 265 | 25.3 | 76.81 | -64.99 | 0.4 | -29.14 | -7722.05 | -7899.04 | 45.0 |

Win rate alone doesn't pay — a high-win-rate strategy with avg losses larger than
avg wins can still lose money. Read it together with **profit_factor** (gross
wins / gross losses, >1 is profitable) and **expectancy** (avg $ per trade).

![Cumulative P&L by strategy](equity_curves.png)

## How each strategy's trades ended (% of trades)

| strategy | eod | signal | stop | target |
|---|---|---|---|---|
| AR Forecast | 0.0 | 86.6 | 13.4 | 0.0 |
| EMA 9/20 Crossover | 24.4 | 56.3 | 19.3 | 0.0 |
| Gap & Go | 66.7 | 0.0 | 33.3 | 0.0 |
| High-Break ATR Trail | 31.3 | 0.0 | 68.7 | 0.0 |
| News Momentum | 40.0 | 0.0 | 45.0 | 15.0 |
| Opening Range Breakout | 70.0 | 0.0 | 23.3 | 6.6 |
| RSI(2) Reversion | 0.3 | 85.0 | 14.7 | 0.0 |
| Squeeze Breakout | 26.0 | 0.0 | 63.8 | 10.2 |
| VWAP Pullback | 20.3 | 0.0 | 60.5 | 19.2 |

`stop` = protective stop hit · `target` = fixed take-profit hit ·
`signal` = strategy's own exit rule · `eod` = flattened at the session cutoff.

Full trade-by-trade log: [trades.csv](trades.csv).

*Small sample (yfinance caps 5-minute history at 60 days), one market regime,
liquid large caps rather than true low-float gappers — see the README's
limitations section before reading anything into these numbers.*
