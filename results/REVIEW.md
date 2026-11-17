# Lab review — is anything beating the market?

Generated 2026-11-17 · 1464 settled paper trades over 58 sessions (2026-08-24 → 2026-11-16) · 1464 SPY-adjusted.

**SPY-adjusted** = the trade's P&L plus an opposite, beta-weighted SPY position held for the same minutes, minus that hedge's slippage. It removes the market's intraday drift, which raw P&L can't tell apart from skill (in Sep–Oct 2026 SPY fell intraday on 27 of 43 days, so shorts looked profitable and longs looked broken).

## Decision gate

**Undecided — 34 days to the decision date.** No strategy beats the market yet.

Rule, set 2026-10-21: by **2026-12-21**, a strategy that has at least 100 SPY-adjusted paper trades and a 95% range entirely above zero keeps running. If none does, the study concludes.

## Paper trading, by strategy (variants pooled)

| strategy_base | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| orb | 356 | $-1.86 | $-17.06 | $-35.77 to $+1.63 | no evidence of edge |
| ar_forecast | 252 | $-6.42 | $-19.81 | $-32.40 to $-7.12 | loses beyond the market |
| high_break_trail | 252 | $-14.35 | $-24.25 | $-41.72 to $-8.40 | loses beyond the market |
| vwap_pullback | 248 | $-1.08 | $-15.39 | $-26.10 to $-4.59 | loses beyond the market |
| rsi2_reversion | 185 | $-8.68 | $-17.90 | $-30.00 to $-4.74 | loses beyond the market |
| ema_crossover | 79 | $-5.06 | $-13.69 | $-30.45 to $+3.68 | no evidence of edge |
| squeeze_breakout | 52 | $-1.86 | $-1.97 | $-20.37 to $+17.14 | no evidence of edge |
| news_momentum | 29 | $-79.18 | $-85.06 | $-194.08 to $-4.14 | too few trades |
| gap_and_go | 11 | $+89.10 | $-28.85 | $-95.33 to $+45.02 | too few trades |

## Paper trading, by side

| side | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| long | 762 | $-22.67 | $-28.91 | $-39.57 to $-18.13 | loses beyond the market |
| short | 702 | $+10.95 | $-8.90 | $-16.94 to $-0.66 | loses beyond the market |

## Paper trading, by symbol

| symbol | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| COIN | 219 | $-8.38 | $-38.59 | $-62.46 to $-13.19 | loses beyond the market |
| NVDA | 201 | $+0.31 | $-16.98 | $-41.87 to $+2.94 | no evidence of edge |
| TSLA | 187 | $-14.61 | $-21.85 | $-34.31 to $-9.17 | loses beyond the market |
| AMD | 150 | $-16.20 | $-20.93 | $-36.17 to $-6.15 | loses beyond the market |
| MSTR | 143 | $+3.95 | $-30.67 | $-60.59 to $-0.24 | loses beyond the market |
| PLTR | 133 | $-21.04 | $-24.23 | $-41.50 to $-6.03 | loses beyond the market |
| AMZN | 65 | $-26.94 | $-20.23 | $-38.76 to $-0.64 | loses beyond the market |
| CAT | 65 | $-14.50 | $-28.94 | $-45.95 to $-13.04 | loses beyond the market |
| UNH | 63 | $-7.90 | $-10.94 | $-34.81 to $+16.32 | no evidence of edge |
| LLY | 61 | $+15.68 | $+14.41 | $-3.88 to $+32.32 | no evidence of edge |
| JPM | 59 | $+7.82 | $-1.06 | $-15.26 to $+14.45 | no evidence of edge |
| WMT | 59 | $+1.62 | $+1.74 | $-19.16 to $+22.07 | no evidence of edge |
| XOM | 59 | $+21.41 | $+23.54 | $+4.26 to $+42.84 | promising (needs more trades) |

## Backtest (60-day window), by strategy

| strategy | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| rsi2_reversion | 1140 | $-8.03 | $-11.34 | $-12.84 to $-9.85 | loses beyond the market |
| ar_forecast | 703 | $-11.60 | $-13.79 | $-16.91 to $-10.65 | loses beyond the market |
| vwap_pullback | 692 | $-8.95 | $-13.99 | $-19.20 to $-8.95 | loses beyond the market |
| ema_crossover | 644 | $-12.67 | $-15.40 | $-18.80 to $-11.94 | loses beyond the market |
| orb | 495 | $-14.81 | $-21.56 | $-31.69 to $-11.63 | loses beyond the market |
| high_break_trail | 438 | $-19.10 | $-24.52 | $-31.99 to $-17.18 | loses beyond the market |
| squeeze_breakout | 432 | $-13.02 | $-16.16 | $-20.39 to $-11.91 | loses beyond the market |
| news_momentum | 102 | $-17.16 | $-17.31 | $-29.56 to $-5.40 | loses beyond the market |
| gap_and_go | 4 | $+182.83 | $+129.59 | $+10.68 to $+216.96 | too few trades |

## Market-neutral ORB

ORB was the lab's best raw performer. Hedged against SPY, does anything remain?

| book | trades | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|
| ORB, paper | 356 | $-17.06 | $-35.41 to $+1.29 | no evidence of edge |
| ORB, backtest | 495 | $-21.56 | $-31.65 to $-11.08 | loses beyond the market |

## How to read this

- The 95% range is a bootstrap interval of the SPY-adjusted mean. A range that crosses zero means the data can't distinguish the strategy from luck.
- Variants (`_tuned`, `_regime`) are pooled into their base strategy; both were switched off on 2026-10-21 after losing more than the defaults.
- The traded universe widened from 6 high-beta tech/crypto names to 10 across sectors on 2026-10-21; the by-symbol table shows whether that helps.
