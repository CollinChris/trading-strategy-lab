# Lab review — is anything beating the market?

Generated 2026-11-23 · 1613 settled paper trades over 63 sessions (2026-08-24 → 2026-11-23) · 1613 SPY-adjusted.

**SPY-adjusted** = the trade's P&L plus an opposite, beta-weighted SPY position held for the same minutes, minus that hedge's slippage. It removes the market's intraday drift, which raw P&L can't tell apart from skill (in Sep–Oct 2026 SPY fell intraday on 27 of 43 days, so shorts looked profitable and longs looked broken).

## Decision gate

**Undecided — 28 days to the decision date.** No strategy beats the market yet.

Rule, set 2026-10-21: by **2026-12-21**, a strategy that has at least 100 SPY-adjusted paper trades and a 95% range entirely above zero keeps running. If none does, the study concludes.

## Paper trading, by strategy (variants pooled)

| strategy_base | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| orb | 391 | $+4.03 | $-14.49 | $-31.57 to $+3.20 | no evidence of edge |
| high_break_trail | 287 | $-2.24 | $-22.48 | $-39.49 to $-7.03 | loses beyond the market |
| ar_forecast | 279 | $+0.77 | $-18.48 | $-30.93 to $-5.75 | loses beyond the market |
| vwap_pullback | 274 | $+2.61 | $-13.50 | $-24.01 to $-3.26 | loses beyond the market |
| rsi2_reversion | 200 | $-4.16 | $-17.28 | $-29.24 to $-5.14 | loses beyond the market |
| ema_crossover | 83 | $-5.24 | $-14.93 | $-31.20 to $+1.79 | no evidence of edge |
| squeeze_breakout | 55 | $-4.33 | $-3.86 | $-21.53 to $+14.89 | no evidence of edge |
| news_momentum | 33 | $-65.75 | $-69.04 | $-165.12 to $+4.45 | no evidence of edge |
| gap_and_go | 11 | $+89.10 | $-28.85 | $-95.33 to $+45.02 | too few trades |

## Paper trading, by side

| side | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| short | 816 | $+23.45 | $-6.36 | $-14.13 to $+1.53 | no evidence of edge |
| long | 797 | $-25.05 | $-29.22 | $-39.35 to $-19.28 | loses beyond the market |

## Paper trading, by symbol

| symbol | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| COIN | 235 | $-8.60 | $-42.56 | $-66.90 to $-19.14 | loses beyond the market |
| NVDA | 216 | $+15.76 | $-12.25 | $-36.51 to $+6.50 | no evidence of edge |
| TSLA | 202 | $-8.51 | $-22.75 | $-34.57 to $-10.94 | loses beyond the market |
| AMD | 150 | $-16.20 | $-20.93 | $-36.17 to $-6.15 | loses beyond the market |
| MSTR | 143 | $+3.95 | $-30.67 | $-60.59 to $-0.24 | loses beyond the market |
| PLTR | 133 | $-21.04 | $-24.23 | $-41.50 to $-6.03 | loses beyond the market |
| AMZN | 82 | $-11.28 | $-12.33 | $-29.41 to $+5.72 | no evidence of edge |
| CAT | 80 | $-0.56 | $-36.08 | $-50.34 to $-21.38 | loses beyond the market |
| JPM | 77 | $+18.17 | $-0.02 | $-12.00 to $+12.52 | no evidence of edge |
| LLY | 76 | $+14.78 | $+10.64 | $-5.05 to $+25.94 | no evidence of edge |
| UNH | 75 | $+16.96 | $+13.54 | $-19.81 to $+52.34 | no evidence of edge |
| WMT | 72 | $-1.82 | $-0.59 | $-18.05 to $+17.34 | no evidence of edge |
| XOM | 72 | $+20.41 | $+22.66 | $+5.66 to $+39.84 | promising (needs more trades) |

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
| ORB, paper | 391 | $-14.49 | $-32.84 to $+2.88 | no evidence of edge |
| ORB, backtest | 500 | $-17.53 | $-28.28 to $-6.96 | loses beyond the market |

## How to read this

- The 95% range is a bootstrap interval of the SPY-adjusted mean. A range that crosses zero means the data can't distinguish the strategy from luck.
- Variants (`_tuned`, `_regime`) are pooled into their base strategy; both were switched off on 2026-10-21 after losing more than the defaults.
- The traded universe widened from 6 high-beta tech/crypto names to 10 across sectors on 2026-10-21; the by-symbol table shows whether that helps.
