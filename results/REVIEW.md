# Lab review — is anything beating the market?

Generated 2026-10-30 · 1064 settled paper trades over 47 sessions (2026-08-24 → 2026-10-30) · 1064 SPY-adjusted.

**SPY-adjusted** = the trade's P&L plus an opposite, beta-weighted SPY position held for the same minutes, minus that hedge's slippage. It removes the market's intraday drift, which raw P&L can't tell apart from skill (in Sep–Oct 2026 SPY fell intraday on 27 of 43 days, so shorts looked profitable and longs looked broken).

## Decision gate

**Undecided — 52 days to the decision date.** No strategy beats the market yet.

Rule, set 2026-10-21: by **2026-12-21**, a strategy that has at least 100 SPY-adjusted paper trades and a 95% range entirely above zero keeps running. If none does, the study concludes.

## Paper trading, by strategy (variants pooled)

| strategy_base | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| orb | 265 | $+0.68 | $-7.04 | $-27.47 to $+14.02 | no evidence of edge |
| ar_forecast | 195 | $-4.26 | $-18.41 | $-32.16 to $-4.05 | loses beyond the market |
| vwap_pullback | 177 | $-2.57 | $-15.23 | $-26.93 to $-3.75 | loses beyond the market |
| high_break_trail | 176 | $-10.42 | $-19.56 | $-36.84 to $-3.14 | loses beyond the market |
| rsi2_reversion | 130 | $-17.60 | $-24.88 | $-38.52 to $-9.74 | loses beyond the market |
| ema_crossover | 58 | $-15.00 | $-22.67 | $-42.82 to $-0.75 | loses beyond the market |
| squeeze_breakout | 37 | $-6.72 | $-7.51 | $-31.02 to $+17.34 | no evidence of edge |
| news_momentum | 20 | $-42.75 | $-49.58 | $-95.74 to $-6.37 | too few trades |
| gap_and_go | 6 | $+154.25 | $+28.54 | $-55.38 to $+125.92 | too few trades |

## Paper trading, by side

| side | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| long | 566 | $-18.85 | $-28.25 | $-39.12 to $-17.70 | loses beyond the market |
| short | 498 | $+8.82 | $-2.51 | $-11.70 to $+6.64 | no evidence of edge |

## Paper trading, by symbol

| symbol | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| COIN | 178 | $+14.26 | $-7.11 | $-32.64 to $+17.76 | no evidence of edge |
| NVDA | 153 | $+10.80 | $+5.66 | $-3.01 to $+14.64 | no evidence of edge |
| AMD | 150 | $-16.20 | $-20.93 | $-35.79 to $-5.88 | loses beyond the market |
| TSLA | 146 | $-21.09 | $-25.44 | $-38.05 to $-12.14 | loses beyond the market |
| MSTR | 143 | $+3.95 | $-30.67 | $-60.59 to $-0.24 | loses beyond the market |
| PLTR | 133 | $-21.04 | $-24.23 | $-41.50 to $-6.03 | loses beyond the market |
| AMZN | 25 | $-28.14 | $-23.69 | $-42.57 to $-3.26 | too few trades |
| CAT | 25 | $-46.49 | $-43.08 | $-66.29 to $-19.12 | too few trades |
| WMT | 25 | $-7.28 | $-7.21 | $-30.85 to $+18.34 | too few trades |
| XOM | 25 | $+7.02 | $+6.42 | $-20.93 to $+34.07 | too few trades |
| UNH | 22 | $-9.43 | $-10.09 | $-43.87 to $+24.37 | too few trades |
| LLY | 20 | $-12.98 | $-12.53 | $-36.02 to $+10.81 | too few trades |
| JPM | 19 | $-20.31 | $-11.73 | $-26.95 to $+2.40 | too few trades |

## Backtest (60-day window), by strategy

| strategy | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| rsi2_reversion | 1160 | $-9.39 | $-12.18 | $-13.68 to $-10.73 | loses beyond the market |
| vwap_pullback | 710 | $-12.56 | $-16.99 | $-22.02 to $-11.89 | loses beyond the market |
| ar_forecast | 659 | $-9.26 | $-11.24 | $-14.43 to $-8.09 | loses beyond the market |
| ema_crossover | 644 | $-12.69 | $-16.11 | $-19.44 to $-12.70 | loses beyond the market |
| orb | 498 | $-13.80 | $-15.31 | $-25.39 to $-5.01 | loses beyond the market |
| squeeze_breakout | 438 | $-16.13 | $-18.30 | $-22.52 to $-14.14 | loses beyond the market |
| high_break_trail | 429 | $-16.02 | $-22.05 | $-29.02 to $-14.96 | loses beyond the market |
| news_momentum | 78 | $-23.24 | $-25.89 | $-39.74 to $-11.53 | loses beyond the market |
| gap_and_go | 5 | $+112.86 | $+68.51 | $-72.90 to $+199.71 | too few trades |

## Market-neutral ORB

ORB was the lab's best raw performer. Hedged against SPY, does anything remain?

| book | trades | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|
| ORB, paper | 265 | $-7.04 | $-27.38 to $+14.43 | no evidence of edge |
| ORB, backtest | 498 | $-15.31 | $-25.62 to $-5.34 | loses beyond the market |

## How to read this

- The 95% range is a bootstrap interval of the SPY-adjusted mean. A range that crosses zero means the data can't distinguish the strategy from luck.
- Variants (`_tuned`, `_regime`) are pooled into their base strategy; both were switched off on 2026-10-21 after losing more than the defaults.
- The traded universe widened from 6 high-beta tech/crypto names to 10 across sectors on 2026-10-21; the by-symbol table shows whether that helps.
