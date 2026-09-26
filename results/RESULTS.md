# Backtest results

Generated 2026-09-26 · window **2026-07-02 → 2026-09-25** ·
symbols **TSLA, NVDA, AMD, PLTR, COIN, MSTR** · bars **5m** ·
**$10,000** per trade · slippage **5 bps/side** ·
**1667 long / 1391 short**, everything flat by 15:55 ET.

## Ranking (by win rate)

| strategy | trades | win_rate_pct | avg_win | avg_loss | profit_factor | expectancy | total_pnl | max_drawdown | median_hold_min |
|---|---|---|---|---|---|---|---|---|---|
| Gap & Go | 12 | 66.7 | 273.4 | -374.61 | 1.46 | 57.4 | 688.8 | -1247.5 | 332.0 |
| RSI(2) Reversion | 718 | 48.2 | 21.3 | -42.78 | 0.46 | -11.9 | -8543.56 | -8955.65 | 15.0 |
| AR Forecast | 638 | 44.8 | 48.56 | -48.84 | 0.81 | -5.18 | -3301.86 | -4211.69 | 20.0 |
| Opening Range Breakout | 311 | 44.4 | 188.86 | -151.14 | 1.0 | -0.27 | -85.19 | -4680.6 | 340.0 |
| News Momentum | 45 | 33.3 | 68.83 | -73.95 | 0.47 | -26.36 | -1185.98 | -1246.18 | 55.0 |
| High-Break ATR Trail | 262 | 32.8 | 116.13 | -98.43 | 0.58 | -28.0 | -7337.1 | -8100.65 | 140.0 |
| VWAP Pullback | 441 | 32.4 | 110.85 | -83.47 | 0.64 | -20.46 | -9022.32 | -9655.88 | 60.0 |
| EMA 9/20 Crossover | 373 | 27.3 | 74.45 | -51.56 | 0.54 | -17.1 | -6377.68 | -6282.69 | 60.0 |
| Squeeze Breakout | 258 | 26.0 | 69.81 | -63.64 | 0.38 | -28.98 | -7477.11 | -7577.2 | 50.0 |

Win rate alone doesn't pay — a high-win-rate strategy with avg losses larger than
avg wins can still lose money. Read it together with **profit_factor** (gross
wins / gross losses, >1 is profitable) and **expectancy** (avg $ per trade).

![Cumulative P&L by strategy](equity_curves.png)

## How each strategy's trades ended (% of trades)

| strategy | eod | signal | stop | target |
|---|---|---|---|---|
| AR Forecast | 0.0 | 87.9 | 12.1 | 0.0 |
| EMA 9/20 Crossover | 22.3 | 57.9 | 19.8 | 0.0 |
| Gap & Go | 66.7 | 0.0 | 33.3 | 0.0 |
| High-Break ATR Trail | 30.2 | 0.0 | 69.8 | 0.0 |
| News Momentum | 37.8 | 0.0 | 48.9 | 13.3 |
| Opening Range Breakout | 70.4 | 0.0 | 23.5 | 6.1 |
| RSI(2) Reversion | 0.3 | 85.1 | 14.6 | 0.0 |
| Squeeze Breakout | 27.9 | 0.0 | 62.0 | 10.1 |
| VWAP Pullback | 20.6 | 0.0 | 60.5 | 18.8 |

`stop` = protective stop hit · `target` = fixed take-profit hit ·
`signal` = strategy's own exit rule · `eod` = flattened at the session cutoff.

Full trade-by-trade log: [trades.csv](trades.csv).

*Small sample (yfinance caps 5-minute history at 60 days), one market regime,
liquid large caps rather than true low-float gappers — see the README's
limitations section before reading anything into these numbers.*
