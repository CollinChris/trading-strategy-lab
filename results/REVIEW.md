# Lab review — is anything beating the market?

Generated 2026-10-26 · 920 settled paper trades over 43 sessions (2026-08-24 → 2026-10-26) · 920 SPY-adjusted.

**SPY-adjusted** = the trade's P&L plus an opposite, beta-weighted SPY position held for the same minutes, minus that hedge's slippage. It removes the market's intraday drift, which raw P&L can't tell apart from skill (in Sep–Oct 2026 SPY fell intraday on 27 of 43 days, so shorts looked profitable and longs looked broken).

## Decision gate

**Undecided — 56 days to the decision date.** No strategy beats the market yet.

Rule, set 2026-10-21: by **2026-12-21**, a strategy that has at least 100 SPY-adjusted paper trades and a 95% range entirely above zero keeps running. If none does, the study concludes.

## Paper trading, by strategy (variants pooled)

| strategy_base | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| orb | 229 | $+8.77 | $-2.30 | $-25.30 to $+22.03 | no evidence of edge |
| ar_forecast | 178 | $-0.76 | $-16.72 | $-32.13 to $-1.47 | loses beyond the market |
| high_break_trail | 152 | $-9.23 | $-20.17 | $-39.85 to $-1.01 | loses beyond the market |
| vwap_pullback | 144 | $-2.34 | $-16.64 | $-30.17 to $-3.08 | loses beyond the market |
| rsi2_reversion | 111 | $-16.88 | $-25.92 | $-41.87 to $-9.37 | loses beyond the market |
| ema_crossover | 51 | $-11.56 | $-18.07 | $-39.73 to $+6.16 | no evidence of edge |
| squeeze_breakout | 33 | $-7.58 | $-8.85 | $-35.60 to $+18.58 | no evidence of edge |
| news_momentum | 17 | $-46.52 | $-54.86 | $-109.30 to $-4.32 | too few trades |
| gap_and_go | 5 | $+179.80 | $+40.77 | $-59.93 to $+137.86 | too few trades |

## Paper trading, by side

| side | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| long | 489 | $-16.80 | $-27.52 | $-39.67 to $-15.13 | loses beyond the market |
| short | 431 | $+13.33 | $-0.76 | $-11.21 to $+10.07 | no evidence of edge |

## Paper trading, by symbol

| symbol | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| COIN | 159 | $+25.41 | $-0.38 | $-27.70 to $+29.06 | no evidence of edge |
| AMD | 150 | $-16.20 | $-20.93 | $-35.52 to $-5.40 | loses beyond the market |
| MSTR | 143 | $+3.95 | $-30.67 | $-61.34 to $+1.09 | no evidence of edge |
| NVDA | 136 | $+9.53 | $+2.75 | $-6.59 to $+11.54 | no evidence of edge |
| PLTR | 133 | $-21.04 | $-24.23 | $-41.42 to $-6.20 | loses beyond the market |
| TSLA | 130 | $-22.29 | $-25.90 | $-40.47 to $-11.42 | loses beyond the market |
| AMZN | 13 | $-10.14 | $-4.62 | $-31.44 to $+25.67 | too few trades |
| XOM | 11 | $-9.45 | $-8.48 | $-43.55 to $+27.67 | too few trades |
| UNH | 10 | $+10.83 | $+15.85 | $-17.04 to $+43.78 | too few trades |
| CAT | 9 | $-39.02 | $-46.88 | $-89.65 to $+1.73 | too few trades |
| JPM | 9 | $-14.12 | $+4.83 | $-13.19 to $+18.70 | too few trades |
| WMT | 9 | $+30.26 | $+30.43 | $-7.99 to $+68.49 | too few trades |
| LLY | 8 | $+10.70 | $+14.47 | $-18.31 to $+45.51 | too few trades |

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
| ORB, paper | 229 | $-2.30 | $-25.36 to $+21.27 | no evidence of edge |
| ORB, backtest | 498 | $-15.31 | $-25.62 to $-5.34 | loses beyond the market |

## How to read this

- The 95% range is a bootstrap interval of the SPY-adjusted mean. A range that crosses zero means the data can't distinguish the strategy from luck.
- Variants (`_tuned`, `_regime`) are pooled into their base strategy; both were switched off on 2026-10-21 after losing more than the defaults.
- The traded universe widened from 6 high-beta tech/crypto names to 10 across sectors on 2026-10-21; the by-symbol table shows whether that helps.
