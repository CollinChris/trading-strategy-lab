# Backtest results

Generated 2026-11-14 · window **2026-08-21 → 2026-11-13** ·
symbols **NVDA, TSLA, COIN, AMZN, JPM, XOM, UNH, WMT, CAT, LLY** · bars **5m** ·
**$10,000** per trade · slippage **5 bps/side** ·
**2362 long / 2288 short**, everything flat by 15:55 ET.

## Ranking (by win rate)

| strategy | trades | win_rate_pct | avg_win | avg_loss | profit_factor | expectancy | total_pnl | max_drawdown | median_hold_min |
|---|---|---|---|---|---|---|---|---|---|
| Gap & Go | 4 | 75.0 | 263.2 | -58.27 | 13.55 | 182.83 | 731.32 | -58.27 | 348.0 |
| Opening Range Breakout | 495 | 40.0 | 104.91 | -94.62 | 0.74 | -14.81 | -7329.26 | -7678.62 | 340.0 |
| AR Forecast | 703 | 39.1 | 30.33 | -38.53 | 0.51 | -11.6 | -8152.08 | -8263.27 | 25.0 |
| RSI(2) Reversion | 1140 | 37.8 | 12.58 | -20.56 | 0.37 | -8.03 | -9155.59 | -9219.49 | 15.0 |
| VWAP Pullback | 692 | 36.4 | 75.48 | -57.31 | 0.75 | -8.95 | -6195.13 | -7201.56 | 135.0 |
| High-Break ATR Trail | 438 | 34.2 | 65.63 | -63.23 | 0.54 | -19.1 | -8366.25 | -8298.21 | 165.0 |
| News Momentum | 102 | 32.4 | 54.4 | -51.39 | 0.51 | -17.16 | -1750.66 | -1826.28 | 78.0 |
| Squeeze Breakout | 432 | 28.2 | 50.33 | -37.95 | 0.52 | -13.02 | -5624.63 | -5646.85 | 50.0 |
| EMA 9/20 Crossover | 644 | 23.4 | 56.26 | -33.78 | 0.51 | -12.67 | -8157.28 | -8239.24 | 60.0 |

Win rate alone doesn't pay — a high-win-rate strategy with avg losses larger than
avg wins can still lose money. Read it together with **profit_factor** (gross
wins / gross losses, >1 is profitable) and **expectancy** (avg $ per trade).

![Cumulative P&L by strategy](equity_curves.png)

## How each strategy's trades ended (% of trades)

| strategy | eod | signal | stop | target |
|---|---|---|---|---|
| AR Forecast | 0.0 | 91.7 | 8.3 | 0.0 |
| EMA 9/20 Crossover | 22.0 | 57.1 | 20.8 | 0.0 |
| Gap & Go | 100.0 | 0.0 | 0.0 | 0.0 |
| High-Break ATR Trail | 32.4 | 0.0 | 67.6 | 0.0 |
| News Momentum | 46.1 | 0.0 | 44.1 | 9.8 |
| Opening Range Breakout | 74.1 | 0.0 | 22.0 | 3.8 |
| RSI(2) Reversion | 0.9 | 95.0 | 4.1 | 0.0 |
| Squeeze Breakout | 28.0 | 0.0 | 59.3 | 12.7 |
| VWAP Pullback | 38.9 | 0.0 | 46.5 | 14.6 |

`stop` = protective stop hit · `target` = fixed take-profit hit ·
`signal` = strategy's own exit rule · `eod` = flattened at the session cutoff.

## Long vs short, per strategy

| strategy | long trades | long exp./trade | short trades | short exp./trade |
|---|---|---|---|---|
| Gap & Go | 2 | $+241.35 | 2 | $+124.31 |
| Opening Range Breakout | 251 | $-24.74 | 244 | $-4.59 |
| VWAP Pullback | 350 | $-13.98 | 342 | $-3.81 |
| EMA 9/20 Crossover | 343 | $-17.94 | 301 | $-6.66 |
| RSI(2) Reversion | 588 | $-8.47 | 552 | $-7.57 |
| News Momentum | 57 | $-23.52 | 45 | $-9.11 |
| Squeeze Breakout | 223 | $-15.97 | 209 | $-9.87 |
| High-Break ATR Trail | 229 | $-22.01 | 209 | $-15.91 |
| AR Forecast | 319 | $-10.91 | 384 | $-12.16 |

Each side read as its own book. The walk-forward version of this question — with
the live long-gate policy scored against random selection — is in REGIME.md.

Full trade-by-trade log: [trades.csv](trades.csv).

*Small sample (yfinance caps 5-minute history at 60 days), one market regime,
liquid large caps rather than true low-float gappers — see the README's
limitations section before reading anything into these numbers.*
