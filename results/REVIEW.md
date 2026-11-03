# Lab review — is anything beating the market?

Generated 2026-11-03 · 1127 settled paper trades over 49 sessions (2026-08-24 → 2026-11-03) · 1127 SPY-adjusted.

**SPY-adjusted** = the trade's P&L plus an opposite, beta-weighted SPY position held for the same minutes, minus that hedge's slippage. It removes the market's intraday drift, which raw P&L can't tell apart from skill (in Sep–Oct 2026 SPY fell intraday on 27 of 43 days, so shorts looked profitable and longs looked broken).

## Decision gate

**Undecided — 48 days to the decision date.** No strategy beats the market yet.

Rule, set 2026-10-21: by **2026-12-21**, a strategy that has at least 100 SPY-adjusted paper trades and a 95% range entirely above zero keeps running. If none does, the study concludes.

## Paper trading, by strategy (variants pooled)

| strategy_base | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| orb | 280 | $-0.86 | $-7.79 | $-27.74 to $+12.44 | no evidence of edge |
| ar_forecast | 205 | $-6.14 | $-19.31 | $-32.66 to $-5.02 | loses beyond the market |
| high_break_trail | 190 | $-8.82 | $-18.45 | $-34.90 to $-2.58 | loses beyond the market |
| vwap_pullback | 188 | $-2.14 | $-14.08 | $-25.38 to $-2.26 | loses beyond the market |
| rsi2_reversion | 138 | $-9.63 | $-19.07 | $-33.39 to $-4.55 | loses beyond the market |
| ema_crossover | 60 | $-13.83 | $-20.49 | $-40.77 to $+0.78 | no evidence of edge |
| squeeze_breakout | 39 | $-4.92 | $-5.75 | $-28.56 to $+17.94 | no evidence of edge |
| news_momentum | 20 | $-42.75 | $-49.58 | $-95.74 to $-6.37 | too few trades |
| gap_and_go | 7 | $+153.36 | $+29.73 | $-42.20 to $+109.42 | too few trades |

## Paper trading, by side

| side | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| long | 592 | $-18.83 | $-25.57 | $-35.90 to $-15.21 | loses beyond the market |
| short | 535 | $+10.16 | $-3.78 | $-12.44 to $+5.19 | no evidence of edge |

## Paper trading, by symbol

| symbol | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| COIN | 184 | $+14.66 | $-11.18 | $-36.07 to $+14.53 | no evidence of edge |
| NVDA | 161 | $+13.47 | $+5.59 | $-2.61 to $+13.91 | no evidence of edge |
| TSLA | 152 | $-23.24 | $-23.85 | $-37.66 to $-10.90 | loses beyond the market |
| AMD | 150 | $-16.20 | $-20.93 | $-36.17 to $-6.15 | loses beyond the market |
| MSTR | 143 | $+3.95 | $-30.67 | $-60.59 to $-0.24 | loses beyond the market |
| PLTR | 133 | $-21.04 | $-24.23 | $-41.50 to $-6.03 | loses beyond the market |
| AMZN | 33 | $-33.97 | $-13.31 | $-37.87 to $+15.47 | no evidence of edge |
| XOM | 31 | $+5.49 | $+8.27 | $-16.40 to $+33.20 | no evidence of edge |
| CAT | 29 | $-34.27 | $-38.27 | $-59.26 to $-16.88 | too few trades |
| UNH | 29 | $-16.79 | $-22.89 | $-52.65 to $+5.34 | too few trades |
| WMT | 29 | $+5.50 | $+5.48 | $-19.84 to $+31.32 | too few trades |
| LLY | 28 | $+5.74 | $+8.33 | $-14.61 to $+31.17 | too few trades |
| JPM | 25 | $-10.80 | $-2.75 | $-16.74 to $+10.79 | too few trades |

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
| ORB, paper | 280 | $-7.79 | $-28.42 to $+12.52 | no evidence of edge |
| ORB, backtest | 499 | $-18.70 | $-28.53 to $-8.66 | loses beyond the market |

## How to read this

- The 95% range is a bootstrap interval of the SPY-adjusted mean. A range that crosses zero means the data can't distinguish the strategy from luck.
- Variants (`_tuned`, `_regime`) are pooled into their base strategy; both were switched off on 2026-10-21 after losing more than the defaults.
- The traded universe widened from 6 high-beta tech/crypto names to 10 across sectors on 2026-10-21; the by-symbol table shows whether that helps.
