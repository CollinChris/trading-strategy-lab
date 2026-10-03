# Backtest results

Generated 2026-10-03 · window **2026-07-10 → 2026-10-02** ·
symbols **TSLA, NVDA, AMD, PLTR, COIN, MSTR** · bars **5m** ·
**$10,000** per trade · slippage **5 bps/side** ·
**1621 long / 1436 short**, everything flat by 15:55 ET.

## Ranking (by win rate)

| strategy | trades | win_rate_pct | avg_win | avg_loss | profit_factor | expectancy | total_pnl | max_drawdown | median_hold_min |
|---|---|---|---|---|---|---|---|---|---|
| Gap & Go | 11 | 72.7 | 273.4 | -415.83 | 1.75 | 85.43 | 939.73 | -985.44 | 335.0 |
| RSI(2) Reversion | 717 | 47.0 | 20.09 | -40.62 | 0.44 | -12.09 | -8665.29 | -8979.78 | 15.0 |
| Opening Range Breakout | 308 | 44.5 | 186.18 | -143.04 | 1.04 | 3.4 | 1047.56 | -4455.23 | 340.0 |
| AR Forecast | 629 | 44.2 | 50.01 | -50.01 | 0.79 | -5.81 | -3652.87 | -3901.5 | 20.0 |
| News Momentum | 44 | 31.8 | 60.7 | -68.7 | 0.41 | -27.52 | -1211.03 | -1180.18 | 55.0 |
| VWAP Pullback | 444 | 31.8 | 101.93 | -81.5 | 0.58 | -23.25 | -10321.08 | -10669.46 | 60.0 |
| High-Break ATR Trail | 262 | 31.7 | 114.94 | -93.67 | 0.57 | -27.58 | -7226.26 | -7773.05 | 145.0 |
| EMA 9/20 Crossover | 383 | 27.9 | 74.99 | -50.91 | 0.57 | -15.74 | -6027.34 | -6222.99 | 60.0 |
| Squeeze Breakout | 259 | 27.8 | 67.72 | -60.18 | 0.43 | -24.63 | -6378.25 | -6423.0 | 50.0 |

Win rate alone doesn't pay — a high-win-rate strategy with avg losses larger than
avg wins can still lose money. Read it together with **profit_factor** (gross
wins / gross losses, >1 is profitable) and **expectancy** (avg $ per trade).

![Cumulative P&L by strategy](equity_curves.png)

## How each strategy's trades ended (% of trades)

| strategy | eod | signal | stop | target |
|---|---|---|---|---|
| AR Forecast | 0.2 | 86.8 | 13.0 | 0.0 |
| EMA 9/20 Crossover | 22.2 | 57.7 | 20.1 | 0.0 |
| Gap & Go | 72.7 | 0.0 | 27.3 | 0.0 |
| High-Break ATR Trail | 30.5 | 0.0 | 69.5 | 0.0 |
| News Momentum | 40.9 | 0.0 | 47.7 | 11.4 |
| Opening Range Breakout | 70.8 | 0.0 | 22.7 | 6.5 |
| RSI(2) Reversion | 0.4 | 85.9 | 13.7 | 0.0 |
| Squeeze Breakout | 29.3 | 0.0 | 59.5 | 11.2 |
| VWAP Pullback | 22.1 | 0.0 | 61.3 | 16.7 |

`stop` = protective stop hit · `target` = fixed take-profit hit ·
`signal` = strategy's own exit rule · `eod` = flattened at the session cutoff.

## Long vs short, per strategy

| strategy | long trades | long exp./trade | short trades | short exp./trade |
|---|---|---|---|---|
| Gap & Go | 8 | $+108.05 | 3 | $+25.10 |
| Opening Range Breakout | 159 | $+12.37 | 149 | $-6.17 |
| VWAP Pullback | 222 | $-25.85 | 222 | $-20.64 |
| EMA 9/20 Crossover | 190 | $-22.12 | 193 | $-9.46 |
| RSI(2) Reversion | 371 | $-11.52 | 346 | $-12.70 |
| News Momentum | 25 | $-41.17 | 19 | $-9.56 |
| Squeeze Breakout | 150 | $-27.63 | 109 | $-20.50 |
| High-Break ATR Trail | 139 | $-14.00 | 123 | $-42.93 |
| AR Forecast | 357 | $-5.62 | 272 | $-6.06 |

Each side read as its own book. The walk-forward version of this question — with
the live long-gate policy scored against random selection — is in REGIME.md.

Full trade-by-trade log: [trades.csv](trades.csv).

*Small sample (yfinance caps 5-minute history at 60 days), one market regime,
liquid large caps rather than true low-float gappers — see the README's
limitations section before reading anything into these numbers.*
