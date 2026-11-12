# Lab review — is anything beating the market?

Generated 2026-11-12 · 1402 settled paper trades over 56 sessions (2026-08-24 → 2026-11-12) · 1402 SPY-adjusted.

**SPY-adjusted** = the trade's P&L plus an opposite, beta-weighted SPY position held for the same minutes, minus that hedge's slippage. It removes the market's intraday drift, which raw P&L can't tell apart from skill (in Sep–Oct 2026 SPY fell intraday on 27 of 43 days, so shorts looked profitable and longs looked broken).

## Decision gate

**Undecided — 39 days to the decision date.** No strategy beats the market yet.

Rule, set 2026-10-21: by **2026-12-21**, a strategy that has at least 100 SPY-adjusted paper trades and a 95% range entirely above zero keeps running. If none does, the study concludes.

## Paper trading, by strategy (variants pooled)

| strategy_base | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| orb | 341 | $-2.18 | $-16.26 | $-35.28 to $+3.75 | no evidence of edge |
| ar_forecast | 246 | $-7.84 | $-20.26 | $-33.21 to $-7.21 | loses beyond the market |
| high_break_trail | 241 | $-14.00 | $-24.05 | $-42.44 to $-7.01 | loses beyond the market |
| vwap_pullback | 232 | $-2.97 | $-15.89 | $-27.53 to $-4.63 | loses beyond the market |
| rsi2_reversion | 177 | $-8.10 | $-16.49 | $-29.25 to $-3.15 | loses beyond the market |
| ema_crossover | 76 | $-10.20 | $-15.38 | $-33.02 to $+2.48 | no evidence of edge |
| squeeze_breakout | 50 | $-2.93 | $-2.91 | $-22.53 to $+16.80 | no evidence of edge |
| news_momentum | 28 | $-85.80 | $-88.85 | $-201.01 to $-6.87 | too few trades |
| gap_and_go | 11 | $+89.10 | $-28.85 | $-95.33 to $+45.02 | too few trades |

## Paper trading, by side

| side | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| long | 751 | $-22.84 | $-29.20 | $-40.11 to $-18.39 | loses beyond the market |
| short | 651 | $+10.20 | $-7.87 | $-16.30 to $+0.41 | no evidence of edge |

## Paper trading, by symbol

| symbol | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| COIN | 214 | $-4.94 | $-34.07 | $-59.37 to $-7.94 | loses beyond the market |
| NVDA | 192 | $-1.78 | $-17.20 | $-42.95 to $+3.23 | no evidence of edge |
| TSLA | 183 | $-16.39 | $-21.09 | $-34.08 to $-8.36 | loses beyond the market |
| AMD | 150 | $-16.20 | $-20.93 | $-36.17 to $-6.15 | loses beyond the market |
| MSTR | 143 | $+3.95 | $-30.67 | $-60.59 to $-0.24 | loses beyond the market |
| PLTR | 133 | $-21.04 | $-24.23 | $-41.50 to $-6.03 | loses beyond the market |
| CAT | 59 | $-25.29 | $-33.54 | $-50.32 to $-16.48 | loses beyond the market |
| UNH | 58 | $-0.53 | $-4.86 | $-30.26 to $+21.15 | no evidence of edge |
| AMZN | 57 | $-34.07 | $-22.93 | $-43.78 to $-0.89 | loses beyond the market |
| XOM | 55 | $+21.22 | $+23.12 | $+1.88 to $+45.06 | promising (needs more trades) |
| JPM | 53 | $+2.42 | $-5.32 | $-20.00 to $+10.20 | no evidence of edge |
| WMT | 53 | $+2.67 | $+2.70 | $-20.32 to $+25.84 | no evidence of edge |
| LLY | 52 | $+11.06 | $+11.29 | $-7.83 to $+31.73 | no evidence of edge |

## Backtest (60-day window), by strategy

| strategy | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| rsi2_reversion | 1139 | $-8.42 | $-11.70 | $-13.26 to $-10.20 | loses beyond the market |
| vwap_pullback | 709 | $-10.31 | $-14.74 | $-19.79 to $-9.47 | loses beyond the market |
| ar_forecast | 676 | $-11.95 | $-14.28 | $-17.53 to $-11.00 | loses beyond the market |
| ema_crossover | 652 | $-12.45 | $-15.09 | $-18.45 to $-11.53 | loses beyond the market |
| orb | 500 | $-15.15 | $-21.87 | $-31.87 to $-11.51 | loses beyond the market |
| squeeze_breakout | 440 | $-13.20 | $-15.85 | $-19.98 to $-11.60 | loses beyond the market |
| high_break_trail | 437 | $-17.62 | $-22.38 | $-29.79 to $-14.82 | loses beyond the market |
| news_momentum | 84 | $-22.68 | $-22.64 | $-35.19 to $-9.24 | loses beyond the market |
| gap_and_go | 4 | $+182.83 | $+128.69 | $+10.14 to $+215.23 | too few trades |

## Market-neutral ORB

ORB was the lab's best raw performer. Hedged against SPY, does anything remain?

| book | trades | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|
| ORB, paper | 341 | $-16.26 | $-35.52 to $+2.94 | no evidence of edge |
| ORB, backtest | 500 | $-21.87 | $-31.70 to $-11.94 | loses beyond the market |

## How to read this

- The 95% range is a bootstrap interval of the SPY-adjusted mean. A range that crosses zero means the data can't distinguish the strategy from luck.
- Variants (`_tuned`, `_regime`) are pooled into their base strategy; both were switched off on 2026-10-21 after losing more than the defaults.
- The traded universe widened from 6 high-beta tech/crypto names to 10 across sectors on 2026-10-21; the by-symbol table shows whether that helps.
