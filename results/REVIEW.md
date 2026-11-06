# Lab review — is anything beating the market?

Generated 2026-11-06 · 1245 settled paper trades over 52 sessions (2026-08-24 → 2026-11-06) · 1245 SPY-adjusted.

**SPY-adjusted** = the trade's P&L plus an opposite, beta-weighted SPY position held for the same minutes, minus that hedge's slippage. It removes the market's intraday drift, which raw P&L can't tell apart from skill (in Sep–Oct 2026 SPY fell intraday on 27 of 43 days, so shorts looked profitable and longs looked broken).

## Decision gate

**Undecided — 45 days to the decision date.** No strategy beats the market yet.

Rule, set 2026-10-21: by **2026-12-21**, a strategy that has at least 100 SPY-adjusted paper trades and a 95% range entirely above zero keeps running. If none does, the study concludes.

## Paper trading, by strategy (variants pooled)

| strategy_base | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| orb | 305 | $+5.69 | $-9.38 | $-28.04 to $+10.21 | no evidence of edge |
| ar_forecast | 224 | $-5.41 | $-20.24 | $-33.81 to $-6.68 | loses beyond the market |
| high_break_trail | 215 | $-8.61 | $-20.19 | $-35.89 to $-4.24 | loses beyond the market |
| vwap_pullback | 206 | $-0.10 | $-13.39 | $-24.33 to $-2.41 | loses beyond the market |
| rsi2_reversion | 149 | $-8.44 | $-18.51 | $-32.07 to $-4.24 | loses beyond the market |
| ema_crossover | 69 | $-11.24 | $-17.05 | $-35.94 to $+2.24 | no evidence of edge |
| squeeze_breakout | 43 | $-3.16 | $-3.80 | $-24.05 to $+17.99 | no evidence of edge |
| news_momentum | 23 | $-36.07 | $-36.01 | $-83.41 to $+8.44 | too few trades |
| gap_and_go | 11 | $+89.10 | $-28.85 | $-95.33 to $+45.02 | too few trades |

## Paper trading, by side

| side | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| long | 639 | $-18.60 | $-24.76 | $-34.49 to $-14.67 | loses beyond the market |
| short | 606 | $+14.06 | $-6.46 | $-14.92 to $+2.45 | no evidence of edge |

## Paper trading, by symbol

| symbol | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| COIN | 197 | $+9.04 | $-21.88 | $-46.53 to $+3.54 | no evidence of edge |
| NVDA | 171 | $+17.00 | $+1.97 | $-7.21 to $+11.16 | no evidence of edge |
| TSLA | 164 | $-20.49 | $-26.21 | $-39.12 to $-13.58 | loses beyond the market |
| AMD | 150 | $-16.20 | $-20.93 | $-36.17 to $-6.15 | loses beyond the market |
| MSTR | 143 | $+3.95 | $-30.67 | $-60.59 to $-0.24 | loses beyond the market |
| PLTR | 133 | $-21.04 | $-24.23 | $-41.50 to $-6.03 | loses beyond the market |
| XOM | 44 | $+11.42 | $+14.30 | $-10.74 to $+38.98 | no evidence of edge |
| AMZN | 43 | $-31.77 | $-25.33 | $-48.14 to $+1.08 | no evidence of edge |
| UNH | 43 | $+6.29 | $-0.64 | $-34.10 to $+33.91 | no evidence of edge |
| CAT | 41 | $-25.20 | $-36.77 | $-56.12 to $-17.22 | loses beyond the market |
| LLY | 39 | $+9.61 | $+10.00 | $-12.96 to $+33.14 | no evidence of edge |
| WMT | 39 | $+21.67 | $+21.71 | $-2.43 to $+46.34 | no evidence of edge |
| JPM | 38 | $+9.84 | $+1.06 | $-17.62 to $+22.31 | no evidence of edge |

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
| ORB, paper | 305 | $-9.38 | $-28.60 to $+9.89 | no evidence of edge |
| ORB, backtest | 499 | $-18.70 | $-28.53 to $-8.66 | loses beyond the market |

## How to read this

- The 95% range is a bootstrap interval of the SPY-adjusted mean. A range that crosses zero means the data can't distinguish the strategy from luck.
- Variants (`_tuned`, `_regime`) are pooled into their base strategy; both were switched off on 2026-10-21 after losing more than the defaults.
- The traded universe widened from 6 high-beta tech/crypto names to 10 across sectors on 2026-10-21; the by-symbol table shows whether that helps.
