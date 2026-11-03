# Lab review — is anything beating the market?

Generated 2026-11-03 · 1152 settled paper trades over 49 sessions (2026-08-24 → 2026-11-03) · 1152 SPY-adjusted.

**SPY-adjusted** = the trade's P&L plus an opposite, beta-weighted SPY position held for the same minutes, minus that hedge's slippage. It removes the market's intraday drift, which raw P&L can't tell apart from skill (in Sep–Oct 2026 SPY fell intraday on 27 of 43 days, so shorts looked profitable and longs looked broken).

## Decision gate

**Undecided — 48 days to the decision date.** No strategy beats the market yet.

Rule, set 2026-10-21: by **2026-12-21**, a strategy that has at least 100 SPY-adjusted paper trades and a 95% range entirely above zero keeps running. If none does, the study concludes.

## Paper trading, by strategy (variants pooled)

| strategy_base | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| orb | 286 | $+0.43 | $-6.54 | $-25.70 to $+13.49 | no evidence of edge |
| ar_forecast | 206 | $-6.07 | $-19.15 | $-32.65 to $-5.19 | loses beyond the market |
| high_break_trail | 197 | $-8.71 | $-17.88 | $-33.24 to $-2.11 | loses beyond the market |
| vwap_pullback | 192 | $-1.71 | $-13.27 | $-24.44 to $-1.63 | loses beyond the market |
| rsi2_reversion | 141 | $-8.52 | $-18.18 | $-31.99 to $-3.87 | loses beyond the market |
| ema_crossover | 62 | $-10.98 | $-17.55 | $-37.67 to $+4.02 | no evidence of edge |
| squeeze_breakout | 40 | $-4.82 | $-5.40 | $-28.29 to $+17.70 | no evidence of edge |
| news_momentum | 20 | $-42.75 | $-49.58 | $-95.74 to $-6.37 | too few trades |
| gap_and_go | 8 | $+126.95 | $+18.26 | $-46.66 to $+91.61 | too few trades |

## Paper trading, by side

| side | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| long | 603 | $-18.76 | $-25.22 | $-35.50 to $-14.85 | loses beyond the market |
| short | 549 | $+11.35 | $-2.54 | $-11.21 to $+6.39 | no evidence of edge |

## Paper trading, by symbol

| symbol | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| COIN | 186 | $+14.31 | $-11.28 | $-35.60 to $+14.50 | no evidence of edge |
| NVDA | 162 | $+13.03 | $+5.17 | $-3.15 to $+13.35 | no evidence of edge |
| TSLA | 155 | $-21.46 | $-22.93 | $-35.75 to $-9.98 | loses beyond the market |
| AMD | 150 | $-16.20 | $-20.93 | $-36.17 to $-6.15 | loses beyond the market |
| MSTR | 143 | $+3.95 | $-30.67 | $-60.59 to $-0.24 | loses beyond the market |
| PLTR | 133 | $-21.04 | $-24.23 | $-41.50 to $-6.03 | loses beyond the market |
| AMZN | 35 | $-30.81 | $-10.04 | $-34.59 to $+17.37 | no evidence of edge |
| XOM | 34 | $+5.99 | $+8.82 | $-13.93 to $+31.67 | no evidence of edge |
| CAT | 32 | $-32.88 | $-34.95 | $-54.30 to $-15.41 | loses beyond the market |
| UNH | 32 | $-16.97 | $-22.18 | $-49.66 to $+3.97 | no evidence of edge |
| WMT | 32 | $+11.16 | $+11.15 | $-12.45 to $+34.34 | no evidence of edge |
| LLY | 30 | $+11.77 | $+13.75 | $-7.38 to $+36.02 | no evidence of edge |
| JPM | 28 | $-3.81 | $+2.50 | $-11.09 to $+16.24 | too few trades |

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
| ORB, paper | 286 | $-6.54 | $-26.05 to $+13.29 | no evidence of edge |
| ORB, backtest | 499 | $-18.70 | $-28.53 to $-8.66 | loses beyond the market |

## How to read this

- The 95% range is a bootstrap interval of the SPY-adjusted mean. A range that crosses zero means the data can't distinguish the strategy from luck.
- Variants (`_tuned`, `_regime`) are pooled into their base strategy; both were switched off on 2026-10-21 after losing more than the defaults.
- The traded universe widened from 6 high-beta tech/crypto names to 10 across sectors on 2026-10-21; the by-symbol table shows whether that helps.
