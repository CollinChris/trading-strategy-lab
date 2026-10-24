# Backtest results

Generated 2026-10-24 · window **2026-07-31 → 2026-10-23** ·
symbols **NVDA, TSLA, COIN, AMZN, JPM, XOM, UNH, WMT, CAT, LLY** · bars **5m** ·
**$10,000** per trade · slippage **5 bps/side** ·
**2328 long / 2293 short**, everything flat by 15:55 ET.

## Ranking (by win rate)

| strategy | trades | win_rate_pct | avg_win | avg_loss | profit_factor | expectancy | total_pnl | max_drawdown | median_hold_min |
|---|---|---|---|---|---|---|---|---|---|
| Gap & Go | 5 | 60.0 | 263.2 | -112.65 | 3.5 | 112.86 | 564.29 | -58.27 | 345.0 |
| Opening Range Breakout | 498 | 41.8 | 99.34 | -94.94 | 0.75 | -13.8 | -6870.69 | -7934.18 | 340.0 |
| AR Forecast | 659 | 40.8 | 28.88 | -35.58 | 0.56 | -9.26 | -6105.43 | -6113.23 | 25.0 |
| RSI(2) Reversion | 1160 | 35.9 | 11.33 | -20.97 | 0.3 | -9.39 | -10887.41 | -10784.61 | 15.0 |
| VWAP Pullback | 710 | 34.9 | 71.55 | -57.71 | 0.67 | -12.56 | -8915.18 | -10236.83 | 135.0 |
| High-Break ATR Trail | 429 | 33.3 | 66.1 | -57.08 | 0.58 | -16.02 | -6871.44 | -7765.36 | 155.0 |
| News Momentum | 78 | 28.2 | 56.56 | -54.59 | 0.41 | -23.24 | -1812.44 | -1866.36 | 88.0 |
| Squeeze Breakout | 438 | 26.0 | 45.58 | -37.84 | 0.42 | -16.13 | -7063.05 | -7196.76 | 55.0 |
| EMA 9/20 Crossover | 644 | 23.9 | 53.53 | -33.5 | 0.5 | -12.69 | -8170.97 | -8222.54 | 58.0 |

Win rate alone doesn't pay — a high-win-rate strategy with avg losses larger than
avg wins can still lose money. Read it together with **profit_factor** (gross
wins / gross losses, >1 is profitable) and **expectancy** (avg $ per trade).

![Cumulative P&L by strategy](equity_curves.png)

## How each strategy's trades ended (% of trades)

| strategy | eod | signal | stop | target |
|---|---|---|---|---|
| AR Forecast | 0.0 | 94.4 | 5.6 | 0.0 |
| EMA 9/20 Crossover | 21.4 | 58.1 | 20.5 | 0.0 |
| Gap & Go | 80.0 | 0.0 | 20.0 | 0.0 |
| High-Break ATR Trail | 33.1 | 0.0 | 66.9 | 0.0 |
| News Momentum | 42.3 | 0.0 | 50.0 | 7.7 |
| Opening Range Breakout | 72.5 | 0.0 | 23.3 | 4.2 |
| RSI(2) Reversion | 1.0 | 94.8 | 4.1 | 0.0 |
| Squeeze Breakout | 28.1 | 0.0 | 60.7 | 11.2 |
| VWAP Pullback | 38.2 | 0.0 | 49.3 | 12.5 |

`stop` = protective stop hit · `target` = fixed take-profit hit ·
`signal` = strategy's own exit rule · `eod` = flattened at the session cutoff.

## Long vs short, per strategy

| strategy | long trades | long exp./trade | short trades | short exp./trade |
|---|---|---|---|---|
| Gap & Go | 2 | $+241.35 | 3 | $+27.20 |
| Opening Range Breakout | 250 | $-21.22 | 248 | $-6.31 |
| VWAP Pullback | 361 | $-18.57 | 349 | $-6.34 |
| EMA 9/20 Crossover | 336 | $-17.31 | 308 | $-7.65 |
| RSI(2) Reversion | 570 | $-9.47 | 590 | $-9.31 |
| News Momentum | 37 | $-28.94 | 41 | $-18.09 |
| Squeeze Breakout | 222 | $-17.60 | 216 | $-14.61 |
| High-Break ATR Trail | 222 | $-19.73 | 207 | $-12.04 |
| AR Forecast | 328 | $-11.18 | 331 | $-7.37 |

Each side read as its own book. The walk-forward version of this question — with
the live long-gate policy scored against random selection — is in REGIME.md.

Full trade-by-trade log: [trades.csv](trades.csv).

*Small sample (yfinance caps 5-minute history at 60 days), one market regime,
liquid large caps rather than true low-float gappers — see the README's
limitations section before reading anything into these numbers.*
