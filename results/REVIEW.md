# Lab review — is anything beating the market?

Generated 2026-11-06 · 1233 settled paper trades over 52 sessions (2026-08-24 → 2026-11-06) · 1233 SPY-adjusted.

**SPY-adjusted** = the trade's P&L plus an opposite, beta-weighted SPY position held for the same minutes, minus that hedge's slippage. It removes the market's intraday drift, which raw P&L can't tell apart from skill (in Sep–Oct 2026 SPY fell intraday on 27 of 43 days, so shorts looked profitable and longs looked broken).

## Decision gate

**Undecided — 45 days to the decision date.** No strategy beats the market yet.

Rule, set 2026-10-21: by **2026-12-21**, a strategy that has at least 100 SPY-adjusted paper trades and a 95% range entirely above zero keeps running. If none does, the study concludes.

## Paper trading, by strategy (variants pooled)

| strategy_base | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| orb | 304 | $+6.77 | $-8.48 | $-26.90 to $+11.44 | no evidence of edge |
| ar_forecast | 222 | $-4.28 | $-18.96 | $-32.22 to $-4.66 | loses beyond the market |
| high_break_trail | 213 | $-6.74 | $-18.31 | $-33.28 to $-2.83 | loses beyond the market |
| vwap_pullback | 205 | $+0.12 | $-13.21 | $-24.06 to $-1.85 | loses beyond the market |
| rsi2_reversion | 148 | $-7.70 | $-17.43 | $-30.66 to $-2.99 | loses beyond the market |
| ema_crossover | 65 | $-7.78 | $-14.13 | $-32.91 to $+6.16 | no evidence of edge |
| squeeze_breakout | 43 | $-3.16 | $-3.80 | $-24.05 to $+17.99 | no evidence of edge |
| news_momentum | 22 | $-43.04 | $-45.10 | $-91.08 to $-2.89 | too few trades |
| gap_and_go | 11 | $+89.10 | $-28.85 | $-95.33 to $+45.02 | too few trades |

## Paper trading, by side

| side | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| long | 631 | $-17.82 | $-24.14 | $-34.08 to $-14.07 | loses beyond the market |
| short | 602 | $+15.28 | $-5.21 | $-13.64 to $+3.26 | no evidence of edge |

## Paper trading, by symbol

| symbol | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| COIN | 192 | $+14.64 | $-16.61 | $-41.44 to $+10.04 | no evidence of edge |
| NVDA | 171 | $+17.00 | $+1.97 | $-7.21 to $+11.16 | no evidence of edge |
| TSLA | 163 | $-21.34 | $-27.37 | $-40.38 to $-15.07 | loses beyond the market |
| AMD | 150 | $-16.20 | $-20.93 | $-36.17 to $-6.15 | loses beyond the market |
| MSTR | 143 | $+3.95 | $-30.67 | $-60.59 to $-0.24 | loses beyond the market |
| PLTR | 133 | $-21.04 | $-24.23 | $-41.50 to $-6.03 | loses beyond the market |
| AMZN | 43 | $-31.77 | $-25.33 | $-48.64 to $+0.02 | no evidence of edge |
| XOM | 43 | $+12.35 | $+15.21 | $-9.67 to $+39.72 | no evidence of edge |
| CAT | 41 | $-25.20 | $-36.77 | $-55.97 to $-17.54 | loses beyond the market |
| UNH | 41 | $+10.11 | $+3.25 | $-30.90 to $+39.09 | no evidence of edge |
| WMT | 39 | $+21.67 | $+21.71 | $-2.43 to $+45.40 | no evidence of edge |
| JPM | 37 | $+13.22 | $+4.25 | $-14.33 to $+24.30 | no evidence of edge |
| LLY | 37 | $+13.33 | $+13.58 | $-10.68 to $+38.42 | no evidence of edge |

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
| ORB, paper | 304 | $-8.48 | $-27.74 to $+10.94 | no evidence of edge |
| ORB, backtest | 499 | $-18.70 | $-28.53 to $-8.66 | loses beyond the market |

## How to read this

- The 95% range is a bootstrap interval of the SPY-adjusted mean. A range that crosses zero means the data can't distinguish the strategy from luck.
- Variants (`_tuned`, `_regime`) are pooled into their base strategy; both were switched off on 2026-10-21 after losing more than the defaults.
- The traded universe widened from 6 high-beta tech/crypto names to 10 across sectors on 2026-10-21; the by-symbol table shows whether that helps.
