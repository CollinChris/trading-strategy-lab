# Lab review — is anything beating the market?

Generated 2026-11-12 · 1371 settled paper trades over 56 sessions (2026-08-24 → 2026-11-12) · 1371 SPY-adjusted.

**SPY-adjusted** = the trade's P&L plus an opposite, beta-weighted SPY position held for the same minutes, minus that hedge's slippage. It removes the market's intraday drift, which raw P&L can't tell apart from skill (in Sep–Oct 2026 SPY fell intraday on 27 of 43 days, so shorts looked profitable and longs looked broken).

## Decision gate

**Undecided — 39 days to the decision date.** No strategy beats the market yet.

Rule, set 2026-10-21: by **2026-12-21**, a strategy that has at least 100 SPY-adjusted paper trades and a 95% range entirely above zero keeps running. If none does, the study concludes.

## Paper trading, by strategy (variants pooled)

| strategy_base | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| orb | 335 | $-2.02 | $-16.91 | $-37.10 to $+1.96 | no evidence of edge |
| ar_forecast | 241 | $-7.86 | $-21.18 | $-34.02 to $-8.19 | loses beyond the market |
| high_break_trail | 238 | $-14.04 | $-24.98 | $-42.75 to $-8.20 | loses beyond the market |
| vwap_pullback | 227 | $-4.01 | $-16.98 | $-28.78 to $-5.43 | loses beyond the market |
| rsi2_reversion | 170 | $-8.62 | $-18.76 | $-31.79 to $-5.34 | loses beyond the market |
| ema_crossover | 74 | $-9.01 | $-14.50 | $-31.89 to $+4.09 | no evidence of edge |
| squeeze_breakout | 48 | $-6.02 | $-6.04 | $-25.25 to $+13.88 | no evidence of edge |
| news_momentum | 27 | $-85.95 | $-93.02 | $-206.44 to $-6.44 | too few trades |
| gap_and_go | 11 | $+89.10 | $-28.85 | $-95.33 to $+45.02 | too few trades |

## Paper trading, by side

| side | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| long | 728 | $-23.89 | $-31.45 | $-42.92 to $-20.77 | loses beyond the market |
| short | 643 | $+10.58 | $-7.86 | $-16.33 to $+0.70 | no evidence of edge |

## Paper trading, by symbol

| symbol | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| COIN | 210 | $-3.00 | $-34.29 | $-59.67 to $-7.20 | loses beyond the market |
| NVDA | 189 | $-2.47 | $-18.43 | $-44.18 to $+3.58 | no evidence of edge |
| TSLA | 177 | $-19.10 | $-25.42 | $-37.96 to $-13.53 | loses beyond the market |
| AMD | 150 | $-16.20 | $-20.93 | $-36.17 to $-6.15 | loses beyond the market |
| MSTR | 143 | $+3.95 | $-30.67 | $-60.59 to $-0.24 | loses beyond the market |
| PLTR | 133 | $-21.04 | $-24.23 | $-41.50 to $-6.03 | loses beyond the market |
| AMZN | 55 | $-30.82 | $-19.41 | $-39.75 to $+2.25 | no evidence of edge |
| UNH | 55 | $-0.95 | $-6.62 | $-33.03 to $+22.33 | no evidence of edge |
| CAT | 54 | $-27.72 | $-39.82 | $-56.77 to $-22.36 | loses beyond the market |
| XOM | 53 | $+17.94 | $+20.25 | $-0.25 to $+42.35 | no evidence of edge |
| LLY | 51 | $+12.58 | $+12.45 | $-8.40 to $+32.35 | no evidence of edge |
| WMT | 51 | $+2.37 | $+2.39 | $-22.76 to $+25.78 | no evidence of edge |
| JPM | 50 | $+1.64 | $-5.37 | $-20.61 to $+11.26 | no evidence of edge |

## Backtest (60-day window), by strategy

| strategy | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| rsi2_reversion | 1139 | $-8.42 | $-11.70 | $-13.26 to $-10.20 | loses beyond the market |
| vwap_pullback | 709 | $-10.31 | $-14.74 | $-19.79 to $-9.47 | loses beyond the market |
| ar_forecast | 676 | $-11.95 | $-14.28 | $-17.53 to $-11.00 | loses beyond the market |
| ema_crossover | 652 | $-12.45 | $-15.09 | $-18.45 to $-11.53 | loses beyond the market |
| orb | 500 | $-15.15 | $-21.87 | $-31.87 to $-11.51 | loses beyond the market |
| squeeze_breakout | 440 | $-13.20 | $-15.85 | $-19.98 to $-11.60 | loses beyond the market |
| high_break_trail | 437 | $-17.62 | $-22.38 | $-29.79 to $-14.82 | loses beyond the market |
| news_momentum | 84 | $-22.68 | $-22.64 | $-35.19 to $-9.24 | loses beyond the market |
| gap_and_go | 4 | $+182.83 | $+128.69 | $+10.14 to $+215.23 | too few trades |

## Market-neutral ORB

ORB was the lab's best raw performer. Hedged against SPY, does anything remain?

| book | trades | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|
| ORB, paper | 335 | $-16.91 | $-36.24 to $+2.39 | no evidence of edge |
| ORB, backtest | 500 | $-21.87 | $-31.70 to $-11.94 | loses beyond the market |

## How to read this

- The 95% range is a bootstrap interval of the SPY-adjusted mean. A range that crosses zero means the data can't distinguish the strategy from luck.
- Variants (`_tuned`, `_regime`) are pooled into their base strategy; both were switched off on 2026-10-21 after losing more than the defaults.
- The traded universe widened from 6 high-beta tech/crypto names to 10 across sectors on 2026-10-21; the by-symbol table shows whether that helps.
