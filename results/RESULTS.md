# Backtest results

Generated 2026-09-12 · window **2026-06-17 → 2026-09-11** ·
symbols **TSLA, NVDA, AMD, PLTR, COIN, MSTR** · bars **5m** ·
**$10,000** per trade · slippage **5 bps/side** ·
**1638 long / 1445 short**, everything flat by 15:55 ET.

## Ranking (by win rate)

| strategy | trades | win_rate_pct | avg_win | avg_loss | profit_factor | expectancy | total_pnl | max_drawdown | median_hold_min |
|---|---|---|---|---|---|---|---|---|---|
| Gap & Go | 12 | 66.7 | 306.62 | -374.61 | 1.64 | 79.55 | 954.55 | -1498.43 | 328.0 |
| RSI(2) Reversion | 734 | 50.1 | 22.11 | -43.35 | 0.51 | -10.53 | -7728.54 | -7873.5 | 15.0 |
| Opening Range Breakout | 319 | 45.8 | 188.47 | -168.44 | 0.94 | -5.09 | -1623.35 | -4680.6 | 340.0 |
| AR Forecast | 651 | 45.0 | 52.05 | -52.18 | 0.82 | -5.27 | -3429.97 | -4314.46 | 20.0 |
| News Momentum | 44 | 43.2 | 80.02 | -75.77 | 0.8 | -8.5 | -373.87 | -738.31 | 55.0 |
| High-Break ATR Trail | 270 | 34.4 | 125.4 | -100.07 | 0.66 | -22.41 | -6049.61 | -8100.65 | 140.0 |
| VWAP Pullback | 430 | 32.6 | 117.73 | -85.43 | 0.67 | -19.28 | -8292.1 | -8289.04 | 60.0 |
| EMA 9/20 Crossover | 359 | 30.6 | 83.21 | -53.24 | 0.69 | -11.43 | -4102.04 | -4675.22 | 65.0 |
| Squeeze Breakout | 264 | 26.1 | 75.87 | -66.64 | 0.4 | -29.39 | -7759.52 | -8001.4 | 45.0 |

Win rate alone doesn't pay — a high-win-rate strategy with avg losses larger than
avg wins can still lose money. Read it together with **profit_factor** (gross
wins / gross losses, >1 is profitable) and **expectancy** (avg $ per trade).

![Cumulative P&L by strategy](equity_curves.png)

## How each strategy's trades ended (% of trades)

| strategy | eod | signal | stop | target |
|---|---|---|---|---|
| AR Forecast | 0.0 | 86.2 | 13.8 | 0.0 |
| EMA 9/20 Crossover | 24.5 | 56.0 | 19.5 | 0.0 |
| Gap & Go | 66.7 | 0.0 | 33.3 | 0.0 |
| High-Break ATR Trail | 30.7 | 0.0 | 69.3 | 0.0 |
| News Momentum | 38.6 | 0.0 | 43.2 | 18.2 |
| Opening Range Breakout | 69.0 | 0.0 | 25.1 | 6.0 |
| RSI(2) Reversion | 0.5 | 85.1 | 14.3 | 0.0 |
| Squeeze Breakout | 26.1 | 0.0 | 63.3 | 10.6 |
| VWAP Pullback | 19.8 | 0.0 | 60.9 | 19.3 |

`stop` = protective stop hit · `target` = fixed take-profit hit ·
`signal` = strategy's own exit rule · `eod` = flattened at the session cutoff.

Full trade-by-trade log: [trades.csv](trades.csv).

*Small sample (yfinance caps 5-minute history at 60 days), one market regime,
liquid large caps rather than true low-float gappers — see the README's
limitations section before reading anything into these numbers.*
