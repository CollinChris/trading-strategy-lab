# Lab review — is anything beating the market?

Generated 2026-11-27 · 1728 settled paper trades over 66 sessions (2026-08-24 → 2026-11-27) · 1728 SPY-adjusted.

**SPY-adjusted** = the trade's P&L plus an opposite, beta-weighted SPY position held for the same minutes, minus that hedge's slippage. It removes the market's intraday drift, which raw P&L can't tell apart from skill (in Sep–Oct 2026 SPY fell intraday on 27 of 43 days, so shorts looked profitable and longs looked broken).

## Decision gate

**Undecided — 24 days to the decision date.** No strategy beats the market yet.

Rule, set 2026-10-21: by **2026-12-21**, a strategy that has at least 100 SPY-adjusted paper trades and a 95% range entirely above zero keeps running. If none does, the study concludes.

## Paper trading, by strategy (variants pooled)

| strategy_base | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| orb | 420 | $+2.49 | $-15.68 | $-32.60 to $+1.09 | no evidence of edge |
| high_break_trail | 307 | $-1.48 | $-21.52 | $-36.99 to $-6.92 | loses beyond the market |
| ar_forecast | 302 | $-1.01 | $-18.14 | $-29.68 to $-6.53 | loses beyond the market |
| vwap_pullback | 296 | $+2.92 | $-12.74 | $-22.45 to $-3.34 | loses beyond the market |
| rsi2_reversion | 209 | $-3.40 | $-16.23 | $-27.92 to $-4.23 | loses beyond the market |
| ema_crossover | 90 | $-3.10 | $-13.77 | $-28.92 to $+1.69 | no evidence of edge |
| squeeze_breakout | 57 | $-5.98 | $-4.49 | $-21.20 to $+13.27 | no evidence of edge |
| news_momentum | 34 | $-52.02 | $-61.79 | $-154.73 to $+10.49 | no evidence of edge |
| gap_and_go | 13 | $+80.43 | $-24.67 | $-84.46 to $+38.86 | too few trades |

## Paper trading, by side

| side | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| long | 867 | $-20.75 | $-27.00 | $-36.55 to $-17.73 | loses beyond the market |
| short | 861 | $+19.84 | $-7.36 | $-14.90 to $+0.34 | no evidence of edge |

## Paper trading, by symbol

| symbol | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| COIN | 245 | $-7.15 | $-40.85 | $-63.52 to $-18.28 | loses beyond the market |
| NVDA | 225 | $+16.66 | $-12.54 | $-35.75 to $+6.58 | no evidence of edge |
| TSLA | 214 | $-7.46 | $-22.35 | $-33.68 to $-10.64 | loses beyond the market |
| AMD | 150 | $-16.20 | $-20.93 | $-36.17 to $-6.15 | loses beyond the market |
| MSTR | 143 | $+3.95 | $-30.67 | $-60.59 to $-0.24 | loses beyond the market |
| PLTR | 133 | $-21.04 | $-24.23 | $-41.50 to $-6.03 | loses beyond the market |
| AMZN | 94 | $-14.01 | $-13.85 | $-29.82 to $+2.39 | no evidence of edge |
| CAT | 94 | $-3.32 | $-36.40 | $-50.11 to $-22.93 | loses beyond the market |
| LLY | 89 | $+5.07 | $+4.68 | $-9.27 to $+18.68 | no evidence of edge |
| JPM | 88 | $+12.12 | $-2.76 | $-13.46 to $+8.59 | no evidence of edge |
| UNH | 85 | $+21.35 | $+14.80 | $-16.29 to $+49.94 | no evidence of edge |
| WMT | 85 | $+0.68 | $+2.35 | $-14.18 to $+17.96 | no evidence of edge |
| XOM | 83 | $+19.25 | $+20.51 | $+5.30 to $+35.81 | promising (needs more trades) |

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
| ORB, paper | 420 | $-15.68 | $-32.27 to $+0.79 | no evidence of edge |
| ORB, backtest | 500 | $-17.53 | $-28.28 to $-6.96 | loses beyond the market |

## How to read this

- The 95% range is a bootstrap interval of the SPY-adjusted mean. A range that crosses zero means the data can't distinguish the strategy from luck.
- Variants (`_tuned`, `_regime`) are pooled into their base strategy; both were switched off on 2026-10-21 after losing more than the defaults.
- The traded universe widened from 6 high-beta tech/crypto names to 10 across sectors on 2026-10-21; the by-symbol table shows whether that helps.
