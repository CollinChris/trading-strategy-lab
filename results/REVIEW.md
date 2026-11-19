# Lab review — is anything beating the market?

Generated 2026-11-19 · 1574 settled paper trades over 61 sessions (2026-08-24 → 2026-11-19) · 1574 SPY-adjusted.

**SPY-adjusted** = the trade's P&L plus an opposite, beta-weighted SPY position held for the same minutes, minus that hedge's slippage. It removes the market's intraday drift, which raw P&L can't tell apart from skill (in Sep–Oct 2026 SPY fell intraday on 27 of 43 days, so shorts looked profitable and longs looked broken).

## Decision gate

**Undecided — 32 days to the decision date.** No strategy beats the market yet.

Rule, set 2026-10-21: by **2026-12-21**, a strategy that has at least 100 SPY-adjusted paper trades and a 95% range entirely above zero keeps running. If none does, the study concludes.

## Paper trading, by strategy (variants pooled)

| strategy_base | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| orb | 381 | $+5.75 | $-14.16 | $-32.68 to $+3.70 | no evidence of edge |
| high_break_trail | 278 | $-8.97 | $-22.10 | $-38.95 to $-6.87 | loses beyond the market |
| ar_forecast | 273 | $-2.89 | $-18.66 | $-30.97 to $-5.67 | loses beyond the market |
| vwap_pullback | 267 | $+1.35 | $-14.30 | $-24.73 to $-3.82 | loses beyond the market |
| rsi2_reversion | 197 | $-5.16 | $-17.78 | $-29.37 to $-5.48 | loses beyond the market |
| ema_crossover | 82 | $-6.05 | $-14.20 | $-30.13 to $+2.85 | no evidence of edge |
| squeeze_breakout | 54 | $-2.44 | $-3.15 | $-21.17 to $+14.69 | no evidence of edge |
| news_momentum | 31 | $-64.53 | $-72.76 | $-175.22 to $+5.55 | no evidence of edge |
| gap_and_go | 11 | $+89.10 | $-28.85 | $-95.33 to $+45.02 | too few trades |

## Paper trading, by side

| side | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| short | 793 | $+18.14 | $-7.07 | $-14.78 to $+0.64 | no evidence of edge |
| long | 781 | $-22.77 | $-28.50 | $-38.66 to $-18.29 | loses beyond the market |

## Paper trading, by symbol

| symbol | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| COIN | 230 | $-7.16 | $-40.82 | $-64.41 to $-16.18 | loses beyond the market |
| NVDA | 213 | $+6.38 | $-15.76 | $-39.23 to $+2.90 | no evidence of edge |
| TSLA | 198 | $-12.14 | $-23.48 | $-35.42 to $-11.35 | loses beyond the market |
| AMD | 150 | $-16.20 | $-20.93 | $-36.17 to $-6.15 | loses beyond the market |
| MSTR | 143 | $+3.95 | $-30.67 | $-60.59 to $-0.24 | loses beyond the market |
| PLTR | 133 | $-21.04 | $-24.23 | $-41.50 to $-6.03 | loses beyond the market |
| AMZN | 78 | $-8.68 | $-10.73 | $-28.55 to $+7.89 | no evidence of edge |
| CAT | 75 | $-6.06 | $-33.96 | $-48.32 to $-18.35 | loses beyond the market |
| UNH | 73 | $+20.83 | $+14.55 | $-19.39 to $+53.23 | no evidence of edge |
| JPM | 72 | $+10.11 | $-2.13 | $-15.11 to $+11.12 | no evidence of edge |
| LLY | 71 | $+16.12 | $+12.82 | $-2.53 to $+28.83 | no evidence of edge |
| WMT | 69 | $+2.16 | $+2.77 | $-15.81 to $+20.75 | no evidence of edge |
| XOM | 69 | $+22.34 | $+23.95 | $+6.04 to $+42.16 | promising (needs more trades) |

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
| ORB, paper | 381 | $-14.16 | $-32.28 to $+3.43 | no evidence of edge |
| ORB, backtest | 495 | $-21.56 | $-31.65 to $-11.08 | loses beyond the market |

## How to read this

- The 95% range is a bootstrap interval of the SPY-adjusted mean. A range that crosses zero means the data can't distinguish the strategy from luck.
- Variants (`_tuned`, `_regime`) are pooled into their base strategy; both were switched off on 2026-10-21 after losing more than the defaults.
- The traded universe widened from 6 high-beta tech/crypto names to 10 across sectors on 2026-10-21; the by-symbol table shows whether that helps.
