# Lab review — is anything beating the market?

Generated 2026-11-23 · 1640 settled paper trades over 63 sessions (2026-08-24 → 2026-11-23) · 1640 SPY-adjusted.

**SPY-adjusted** = the trade's P&L plus an opposite, beta-weighted SPY position held for the same minutes, minus that hedge's slippage. It removes the market's intraday drift, which raw P&L can't tell apart from skill (in Sep–Oct 2026 SPY fell intraday on 27 of 43 days, so shorts looked profitable and longs looked broken).

## Decision gate

**Undecided — 28 days to the decision date.** No strategy beats the market yet.

Rule, set 2026-10-21: by **2026-12-21**, a strategy that has at least 100 SPY-adjusted paper trades and a 95% range entirely above zero keeps running. If none does, the study concludes.

## Paper trading, by strategy (variants pooled)

| strategy_base | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| orb | 396 | $+3.61 | $-15.03 | $-32.75 to $+2.76 | no evidence of edge |
| high_break_trail | 289 | $-2.41 | $-22.39 | $-38.61 to $-7.11 | loses beyond the market |
| ar_forecast | 287 | $+0.81 | $-17.82 | $-29.76 to $-5.38 | loses beyond the market |
| vwap_pullback | 279 | $+2.84 | $-12.70 | $-22.91 to $-2.38 | loses beyond the market |
| rsi2_reversion | 203 | $-2.44 | $-15.41 | $-27.05 to $-2.96 | loses beyond the market |
| ema_crossover | 85 | $-6.30 | $-15.01 | $-30.75 to $+1.21 | no evidence of edge |
| squeeze_breakout | 56 | $-5.26 | $-4.92 | $-21.86 to $+12.70 | no evidence of edge |
| news_momentum | 33 | $-65.75 | $-69.04 | $-165.12 to $+4.45 | no evidence of edge |
| gap_and_go | 12 | $+75.59 | $-32.74 | $-95.16 to $+36.58 | too few trades |

## Paper trading, by side

| side | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| short | 826 | $+23.43 | $-6.02 | $-13.77 to $+1.69 | no evidence of edge |
| long | 814 | $-24.79 | $-28.81 | $-38.82 to $-18.87 | loses beyond the market |

## Paper trading, by symbol

| symbol | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| COIN | 236 | $-7.82 | $-42.02 | $-65.58 to $-18.54 | loses beyond the market |
| NVDA | 218 | $+14.66 | $-13.10 | $-37.41 to $+6.74 | no evidence of edge |
| TSLA | 205 | $-9.58 | $-23.45 | $-35.27 to $-11.05 | loses beyond the market |
| AMD | 150 | $-16.20 | $-20.93 | $-36.17 to $-6.15 | loses beyond the market |
| MSTR | 143 | $+3.95 | $-30.67 | $-60.59 to $-0.24 | loses beyond the market |
| PLTR | 133 | $-21.04 | $-24.23 | $-41.50 to $-6.03 | loses beyond the market |
| AMZN | 84 | $-11.42 | $-12.34 | $-28.87 to $+5.57 | no evidence of edge |
| CAT | 84 | $-2.57 | $-35.36 | $-49.13 to $-21.16 | loses beyond the market |
| JPM | 79 | $+17.59 | $-0.13 | $-12.16 to $+11.79 | no evidence of edge |
| LLY | 79 | $+11.46 | $+7.60 | $-7.48 to $+22.77 | no evidence of edge |
| UNH | 79 | $+19.31 | $+15.93 | $-15.47 to $+51.35 | no evidence of edge |
| WMT | 75 | $+1.45 | $+2.68 | $-15.16 to $+20.46 | no evidence of edge |
| XOM | 75 | $+22.54 | $+24.72 | $+8.55 to $+41.17 | promising (needs more trades) |

## Backtest (60-day window), by strategy

| strategy | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| rsi2_reversion | 1121 | $-7.06 | $-11.01 | $-12.50 to $-9.57 | loses beyond the market |
| ar_forecast | 731 | $-11.04 | $-13.50 | $-16.48 to $-10.50 | loses beyond the market |
| vwap_pullback | 689 | $-4.72 | $-12.34 | $-17.49 to $-7.07 | loses beyond the market |
| ema_crossover | 631 | $-12.54 | $-15.29 | $-18.80 to $-11.63 | loses beyond the market |
| orb | 500 | $-6.84 | $-17.53 | $-28.24 to $-6.44 | loses beyond the market |
| high_break_trail | 452 | $-8.79 | $-22.63 | $-30.52 to $-14.99 | loses beyond the market |
| squeeze_breakout | 417 | $-11.44 | $-15.45 | $-19.73 to $-10.95 | loses beyond the market |
| news_momentum | 39 | $+10.91 | $+15.47 | $-9.51 to $+43.79 | no evidence of edge |
| gap_and_go | 3 | $+141.47 | $+100.91 | $-55.67 to $+218.13 | too few trades |

## Market-neutral ORB

ORB was the lab's best raw performer. Hedged against SPY, does anything remain?

| book | trades | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|
| ORB, paper | 396 | $-15.03 | $-33.17 to $+2.20 | no evidence of edge |
| ORB, backtest | 500 | $-17.53 | $-28.28 to $-6.96 | loses beyond the market |

## How to read this

- The 95% range is a bootstrap interval of the SPY-adjusted mean. A range that crosses zero means the data can't distinguish the strategy from luck.
- Variants (`_tuned`, `_regime`) are pooled into their base strategy; both were switched off on 2026-10-21 after losing more than the defaults.
- The traded universe widened from 6 high-beta tech/crypto names to 10 across sectors on 2026-10-21; the by-symbol table shows whether that helps.
