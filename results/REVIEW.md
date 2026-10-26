# Lab review — is anything beating the market?

Generated 2026-10-26 · 952 settled paper trades over 43 sessions (2026-08-24 → 2026-10-26) · 952 SPY-adjusted.

**SPY-adjusted** = the trade's P&L plus an opposite, beta-weighted SPY position held for the same minutes, minus that hedge's slippage. It removes the market's intraday drift, which raw P&L can't tell apart from skill (in Sep–Oct 2026 SPY fell intraday on 27 of 43 days, so shorts looked profitable and longs looked broken).

## Decision gate

**Undecided — 56 days to the decision date.** No strategy beats the market yet.

Rule, set 2026-10-21: by **2026-12-21**, a strategy that has at least 100 SPY-adjusted paper trades and a 95% range entirely above zero keeps running. If none does, the study concludes.

## Paper trading, by strategy (variants pooled)

| strategy_base | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| orb | 238 | $+6.80 | $-3.75 | $-26.75 to $+19.47 | no evidence of edge |
| ar_forecast | 181 | $+0.15 | $-15.59 | $-30.73 to $+0.34 | no evidence of edge |
| high_break_trail | 157 | $-8.71 | $-18.89 | $-37.23 to $-0.06 | loses beyond the market |
| vwap_pullback | 152 | $-1.44 | $-15.54 | $-28.79 to $-2.80 | loses beyond the market |
| rsi2_reversion | 114 | $-16.91 | $-26.09 | $-42.14 to $-9.76 | loses beyond the market |
| ema_crossover | 51 | $-11.56 | $-18.07 | $-39.73 to $+6.16 | no evidence of edge |
| squeeze_breakout | 35 | $-7.85 | $-8.64 | $-33.09 to $+16.73 | no evidence of edge |
| news_momentum | 18 | $-46.51 | $-54.64 | $-106.80 to $-8.52 | too few trades |
| gap_and_go | 6 | $+154.25 | $+28.54 | $-55.38 to $+125.92 | too few trades |

## Paper trading, by side

| side | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| long | 513 | $-16.81 | $-27.36 | $-38.79 to $-16.00 | loses beyond the market |
| short | 439 | $+13.62 | $-0.04 | $-10.51 to $+10.79 | no evidence of edge |

## Paper trading, by symbol

| symbol | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| COIN | 162 | $+24.16 | $-1.02 | $-28.00 to $+27.76 | no evidence of edge |
| AMD | 150 | $-16.20 | $-20.93 | $-35.52 to $-5.40 | loses beyond the market |
| MSTR | 143 | $+3.95 | $-30.67 | $-61.34 to $+1.09 | no evidence of edge |
| NVDA | 140 | $+10.12 | $+3.41 | $-5.56 to $+12.17 | no evidence of edge |
| PLTR | 133 | $-21.04 | $-24.23 | $-41.42 to $-6.20 | loses beyond the market |
| TSLA | 133 | $-21.91 | $-26.28 | $-40.39 to $-12.24 | loses beyond the market |
| AMZN | 16 | $-19.10 | $-15.54 | $-40.50 to $+12.61 | too few trades |
| UNH | 14 | $+31.98 | $+34.96 | $+3.63 to $+63.50 | too few trades |
| XOM | 14 | $+3.03 | $+4.01 | $-27.42 to $+34.44 | too few trades |
| CAT | 13 | $-36.70 | $-36.62 | $-68.97 to $-2.41 | too few trades |
| WMT | 12 | $-0.44 | $-0.27 | $-42.40 to $+40.96 | too few trades |
| JPM | 11 | $-19.38 | $-7.73 | $-28.83 to $+11.52 | too few trades |
| LLY | 11 | $+10.28 | $+13.06 | $-12.26 to $+37.69 | too few trades |

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
| ORB, paper | 238 | $-3.75 | $-26.80 to $+19.36 | no evidence of edge |
| ORB, backtest | 498 | $-15.31 | $-25.62 to $-5.34 | loses beyond the market |

## How to read this

- The 95% range is a bootstrap interval of the SPY-adjusted mean. A range that crosses zero means the data can't distinguish the strategy from luck.
- Variants (`_tuned`, `_regime`) are pooled into their base strategy; both were switched off on 2026-10-21 after losing more than the defaults.
- The traded universe widened from 6 high-beta tech/crypto names to 10 across sectors on 2026-10-21; the by-symbol table shows whether that helps.
