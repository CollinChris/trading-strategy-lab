# Lab review — is anything beating the market?

Generated 2026-11-04 · 1186 settled paper trades over 50 sessions (2026-08-24 → 2026-11-04) · 1186 SPY-adjusted.

**SPY-adjusted** = the trade's P&L plus an opposite, beta-weighted SPY position held for the same minutes, minus that hedge's slippage. It removes the market's intraday drift, which raw P&L can't tell apart from skill (in Sep–Oct 2026 SPY fell intraday on 27 of 43 days, so shorts looked profitable and longs looked broken).

## Decision gate

**Undecided — 47 days to the decision date.** No strategy beats the market yet.

Rule, set 2026-10-21: by **2026-12-21**, a strategy that has at least 100 SPY-adjusted paper trades and a 95% range entirely above zero keeps running. If none does, the study concludes.

## Paper trading, by strategy (variants pooled)

| strategy_base | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| orb | 294 | $+2.26 | $-4.69 | $-23.43 to $+14.08 | no evidence of edge |
| ar_forecast | 213 | $-3.75 | $-16.68 | $-30.04 to $-2.90 | loses beyond the market |
| high_break_trail | 203 | $-7.45 | $-16.36 | $-32.19 to $-1.56 | loses beyond the market |
| vwap_pullback | 198 | $-0.54 | $-11.89 | $-23.23 to $-0.41 | loses beyond the market |
| rsi2_reversion | 144 | $-8.70 | $-18.06 | $-31.90 to $-3.84 | loses beyond the market |
| ema_crossover | 64 | $-9.67 | $-16.13 | $-36.55 to $+4.38 | no evidence of edge |
| squeeze_breakout | 40 | $-4.82 | $-5.40 | $-28.29 to $+17.70 | no evidence of edge |
| news_momentum | 21 | $-37.49 | $-41.81 | $-90.63 to $-0.32 | too few trades |
| gap_and_go | 9 | $+103.19 | $+5.84 | $-55.34 to $+77.42 | too few trades |

## Paper trading, by side

| side | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| long | 621 | $-16.36 | $-22.81 | $-33.15 to $-12.53 | loses beyond the market |
| short | 565 | $+11.48 | $-1.98 | $-10.41 to $+6.80 | no evidence of edge |

## Paper trading, by symbol

| symbol | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| COIN | 188 | $+15.35 | $-10.31 | $-34.14 to $+15.38 | no evidence of edge |
| NVDA | 166 | $+13.08 | $+5.83 | $-2.33 to $+14.12 | no evidence of edge |
| TSLA | 159 | $-22.81 | $-24.04 | $-36.52 to $-11.54 | loses beyond the market |
| AMD | 150 | $-16.20 | $-20.93 | $-36.17 to $-6.15 | loses beyond the market |
| MSTR | 143 | $+3.95 | $-30.67 | $-60.59 to $-0.24 | loses beyond the market |
| PLTR | 133 | $-21.04 | $-24.23 | $-41.50 to $-6.03 | loses beyond the market |
| AMZN | 38 | $-31.98 | $-13.91 | $-37.62 to $+11.29 | no evidence of edge |
| XOM | 38 | $+15.44 | $+17.55 | $-5.62 to $+41.97 | no evidence of edge |
| UNH | 36 | $+12.13 | $+7.36 | $-29.66 to $+45.26 | no evidence of edge |
| CAT | 35 | $-28.10 | $-30.52 | $-49.05 to $-11.65 | loses beyond the market |
| WMT | 34 | $+19.52 | $+19.52 | $-5.42 to $+44.71 | no evidence of edge |
| JPM | 33 | $-7.57 | $-3.55 | $-19.90 to $+11.19 | no evidence of edge |
| LLY | 33 | $+9.64 | $+11.43 | $-8.96 to $+31.11 | no evidence of edge |

## Backtest (60-day window), by strategy

| strategy | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| rsi2_reversion | 1146 | $-9.09 | $-11.58 | $-13.06 to $-10.16 | loses beyond the market |
| vwap_pullback | 715 | $-10.74 | $-15.14 | $-20.10 to $-10.25 | loses beyond the market |
| ar_forecast | 653 | $-9.47 | $-11.63 | $-14.80 to $-8.55 | loses beyond the market |
| ema_crossover | 647 | $-12.94 | $-16.11 | $-19.42 to $-12.84 | loses beyond the market |
| orb | 499 | $-16.46 | $-18.70 | $-28.46 to $-8.78 | loses beyond the market |
| high_break_trail | 437 | $-17.51 | $-22.26 | $-29.15 to $-14.96 | loses beyond the market |
| squeeze_breakout | 435 | $-15.06 | $-17.06 | $-20.96 to $-12.97 | loses beyond the market |
| news_momentum | 85 | $-21.00 | $-21.02 | $-33.40 to $-8.28 | loses beyond the market |
| gap_and_go | 4 | $+182.83 | $+129.33 | $+10.56 to $+216.34 | too few trades |

## Market-neutral ORB

ORB was the lab's best raw performer. Hedged against SPY, does anything remain?

| book | trades | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|
| ORB, paper | 294 | $-4.69 | $-23.93 to $+15.14 | no evidence of edge |
| ORB, backtest | 499 | $-18.70 | $-28.53 to $-8.66 | loses beyond the market |

## How to read this

- The 95% range is a bootstrap interval of the SPY-adjusted mean. A range that crosses zero means the data can't distinguish the strategy from luck.
- Variants (`_tuned`, `_regime`) are pooled into their base strategy; both were switched off on 2026-10-21 after losing more than the defaults.
- The traded universe widened from 6 high-beta tech/crypto names to 10 across sectors on 2026-10-21; the by-symbol table shows whether that helps.
