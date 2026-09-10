# Backtest results

Generated 2026-09-09 · window **2026-06-15 → 2026-09-09** ·
symbols **TSLA, NVDA, AMD, PLTR, COIN, MSTR** · bars **5m** ·
**$10,000** per trade · slippage **5 bps/side** ·
**1632 long / 1460 short**, everything flat by 15:55 ET.

## Ranking (by win rate)

| strategy | trades | win_rate_pct | avg_win | avg_loss | profit_factor | expectancy | total_pnl | max_drawdown | median_hold_min |
|---|---|---|---|---|---|---|---|---|---|
| Gap & Go | 12 | 66.7 | 306.62 | -374.61 | 1.64 | 79.55 | 954.55 | -1498.43 | 328.0 |
| RSI(2) Reversion | 742 | 50.4 | 22.28 | -43.07 | 0.53 | -10.13 | -7519.47 | -7942.74 | 15.0 |
| Opening Range Breakout | 319 | 46.4 | 189.88 | -169.12 | 0.97 | -2.57 | -818.43 | -4921.83 | 340.0 |
| AR Forecast | 654 | 44.6 | 52.65 | -52.78 | 0.8 | -5.71 | -3734.08 | -4314.46 | 20.0 |
| News Momentum | 44 | 43.2 | 80.02 | -75.77 | 0.8 | -8.5 | -373.87 | -738.31 | 55.0 |
| High-Break ATR Trail | 275 | 35.3 | 128.21 | -100.89 | 0.69 | -20.08 | -5522.47 | -8100.65 | 150.0 |
| VWAP Pullback | 430 | 32.8 | 121.02 | -86.61 | 0.68 | -18.52 | -7965.48 | -8526.21 | 60.0 |
| EMA 9/20 Crossover | 358 | 29.6 | 84.43 | -52.79 | 0.67 | -12.16 | -4352.47 | -4522.04 | 65.0 |
| Squeeze Breakout | 258 | 26.0 | 76.21 | -67.12 | 0.4 | -29.9 | -7713.41 | -8251.4 | 45.0 |

Win rate alone doesn't pay — a high-win-rate strategy with avg losses larger than
avg wins can still lose money. Read it together with **profit_factor** (gross
wins / gross losses, >1 is profitable) and **expectancy** (avg $ per trade).

![Cumulative P&L by strategy](equity_curves.png)

## How each strategy's trades ended (% of trades)

| strategy | eod | signal | stop | target |
|---|---|---|---|---|
| AR Forecast | 0.0 | 85.6 | 14.4 | 0.0 |
| EMA 9/20 Crossover | 23.7 | 56.7 | 19.6 | 0.0 |
| Gap & Go | 66.7 | 0.0 | 33.3 | 0.0 |
| High-Break ATR Trail | 32.0 | 0.0 | 68.0 | 0.0 |
| News Momentum | 38.6 | 0.0 | 43.2 | 18.2 |
| Opening Range Breakout | 69.0 | 0.0 | 24.8 | 6.3 |
| RSI(2) Reversion | 0.5 | 85.4 | 14.0 | 0.0 |
| Squeeze Breakout | 26.0 | 0.0 | 63.6 | 10.5 |
| VWAP Pullback | 19.1 | 0.0 | 60.9 | 20.0 |

`stop` = protective stop hit · `target` = fixed take-profit hit ·
`signal` = strategy's own exit rule · `eod` = flattened at the session cutoff.

Full trade-by-trade log: [trades.csv](trades.csv).

*Small sample (yfinance caps 5-minute history at 60 days), one market regime,
liquid large caps rather than true low-float gappers — see the README's
limitations section before reading anything into these numbers.*
