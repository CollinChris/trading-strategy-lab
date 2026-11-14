# Lab review — is anything beating the market?

Generated 2026-11-14 · 1431 settled paper trades over 57 sessions (2026-08-24 → 2026-11-13) · 1431 SPY-adjusted.

**SPY-adjusted** = the trade's P&L plus an opposite, beta-weighted SPY position held for the same minutes, minus that hedge's slippage. It removes the market's intraday drift, which raw P&L can't tell apart from skill (in Sep–Oct 2026 SPY fell intraday on 27 of 43 days, so shorts looked profitable and longs looked broken).

## Decision gate

**Undecided — 37 days to the decision date.** No strategy beats the market yet.

Rule, set 2026-10-21: by **2026-12-21**, a strategy that has at least 100 SPY-adjusted paper trades and a 95% range entirely above zero keeps running. If none does, the study concludes.

## Paper trading, by strategy (variants pooled)

| strategy_base | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| orb | 350 | $-3.18 | $-16.62 | $-35.47 to $+3.15 | no evidence of edge |
| ar_forecast | 248 | $-8.26 | $-20.41 | $-32.88 to $-7.64 | loses beyond the market |
| high_break_trail | 246 | $-16.13 | $-25.20 | $-42.99 to $-8.59 | loses beyond the market |
| vwap_pullback | 239 | $-2.72 | $-15.37 | $-27.06 to $-4.47 | loses beyond the market |
| rsi2_reversion | 181 | $-8.92 | $-17.04 | $-29.62 to $-4.62 | loses beyond the market |
| ema_crossover | 76 | $-10.20 | $-15.38 | $-33.02 to $+2.48 | no evidence of edge |
| squeeze_breakout | 51 | $-2.21 | $-2.29 | $-20.58 to $+17.55 | no evidence of edge |
| news_momentum | 29 | $-79.18 | $-85.06 | $-194.08 to $-4.14 | too few trades |
| gap_and_go | 11 | $+89.10 | $-28.85 | $-95.33 to $+45.02 | too few trades |

## Paper trading, by side

| side | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| long | 759 | $-22.53 | $-28.86 | $-39.32 to $-18.32 | loses beyond the market |
| short | 672 | $+8.19 | $-8.93 | $-16.93 to $-0.63 | loses beyond the market |

## Paper trading, by symbol

| symbol | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| COIN | 216 | $-6.83 | $-35.00 | $-59.40 to $-9.79 | loses beyond the market |
| NVDA | 196 | $-2.93 | $-18.00 | $-43.02 to $+2.24 | no evidence of edge |
| TSLA | 184 | $-16.71 | $-21.34 | $-33.87 to $-8.32 | loses beyond the market |
| AMD | 150 | $-16.20 | $-20.93 | $-36.17 to $-6.15 | loses beyond the market |
| MSTR | 143 | $+3.95 | $-30.67 | $-60.59 to $-0.24 | loses beyond the market |
| PLTR | 133 | $-21.04 | $-24.23 | $-41.50 to $-6.03 | loses beyond the market |
| CAT | 62 | $-24.22 | $-33.04 | $-49.37 to $-16.07 | loses beyond the market |
| AMZN | 61 | $-31.55 | $-19.48 | $-39.39 to $+1.55 | no evidence of edge |
| UNH | 61 | $-6.00 | $-9.83 | $-34.38 to $+16.64 | no evidence of edge |
| LLY | 57 | $+12.49 | $+12.17 | $-6.32 to $+30.90 | no evidence of edge |
| JPM | 56 | $+0.90 | $-5.75 | $-19.46 to $+9.36 | no evidence of edge |
| WMT | 56 | $+1.06 | $+1.10 | $-21.00 to $+23.50 | no evidence of edge |
| XOM | 56 | $+20.67 | $+22.44 | $+2.08 to $+43.04 | promising (needs more trades) |

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
| ORB, paper | 350 | $-16.62 | $-35.32 to $+1.91 | no evidence of edge |
| ORB, backtest | 495 | $-21.56 | $-31.65 to $-11.08 | loses beyond the market |

## How to read this

- The 95% range is a bootstrap interval of the SPY-adjusted mean. A range that crosses zero means the data can't distinguish the strategy from luck.
- Variants (`_tuned`, `_regime`) are pooled into their base strategy; both were switched off on 2026-10-21 after losing more than the defaults.
- The traded universe widened from 6 high-beta tech/crypto names to 10 across sectors on 2026-10-21; the by-symbol table shows whether that helps.
