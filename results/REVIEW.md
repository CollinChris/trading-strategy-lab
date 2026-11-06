# Lab review — is anything beating the market?

Generated 2026-11-06 · 1268 settled paper trades over 52 sessions (2026-08-24 → 2026-11-06) · 1268 SPY-adjusted.

**SPY-adjusted** = the trade's P&L plus an opposite, beta-weighted SPY position held for the same minutes, minus that hedge's slippage. It removes the market's intraday drift, which raw P&L can't tell apart from skill (in Sep–Oct 2026 SPY fell intraday on 27 of 43 days, so shorts looked profitable and longs looked broken).

## Decision gate

**Undecided — 45 days to the decision date.** No strategy beats the market yet.

Rule, set 2026-10-21: by **2026-12-21**, a strategy that has at least 100 SPY-adjusted paper trades and a 95% range entirely above zero keeps running. If none does, the study concludes.

## Paper trading, by strategy (variants pooled)

| strategy_base | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| orb | 312 | $+4.90 | $-9.41 | $-27.49 to $+8.91 | no evidence of edge |
| ar_forecast | 228 | $-5.61 | $-20.27 | $-33.92 to $-6.42 | loses beyond the market |
| high_break_trail | 218 | $-9.20 | $-20.50 | $-35.84 to $-5.18 | loses beyond the market |
| vwap_pullback | 208 | $-0.40 | $-13.57 | $-24.37 to $-2.37 | loses beyond the market |
| rsi2_reversion | 154 | $-9.44 | $-18.92 | $-32.58 to $-4.67 | loses beyond the market |
| ema_crossover | 70 | $-11.01 | $-16.29 | $-34.52 to $+2.75 | no evidence of edge |
| squeeze_breakout | 44 | $-3.89 | $-3.36 | $-23.57 to $+16.69 | no evidence of edge |
| news_momentum | 23 | $-36.07 | $-36.01 | $-83.41 to $+8.44 | too few trades |
| gap_and_go | 11 | $+89.10 | $-28.85 | $-95.33 to $+45.02 | too few trades |

## Paper trading, by side

| side | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| long | 659 | $-19.36 | $-24.76 | $-34.30 to $-15.00 | loses beyond the market |
| short | 609 | $+14.24 | $-6.37 | $-15.27 to $+2.24 | no evidence of edge |

## Paper trading, by symbol

| symbol | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| COIN | 198 | $+8.81 | $-21.69 | $-46.49 to $+4.36 | no evidence of edge |
| NVDA | 174 | $+17.59 | $+2.14 | $-6.67 to $+10.62 | no evidence of edge |
| TSLA | 166 | $-19.38 | $-24.51 | $-37.95 to $-11.71 | loses beyond the market |
| AMD | 150 | $-16.20 | $-20.93 | $-36.17 to $-6.15 | loses beyond the market |
| MSTR | 143 | $+3.95 | $-30.67 | $-60.59 to $-0.24 | loses beyond the market |
| PLTR | 133 | $-21.04 | $-24.23 | $-41.50 to $-6.03 | loses beyond the market |
| AMZN | 46 | $-37.73 | $-29.37 | $-50.92 to $-4.27 | loses beyond the market |
| XOM | 46 | $+10.41 | $+12.93 | $-9.45 to $+37.26 | no evidence of edge |
| UNH | 45 | $+4.06 | $-2.45 | $-33.93 to $+31.14 | no evidence of edge |
| CAT | 43 | $-23.04 | $-33.00 | $-52.42 to $-14.17 | loses beyond the market |
| WMT | 42 | $+17.09 | $+17.12 | $-6.39 to $+40.26 | no evidence of edge |
| JPM | 41 | $+1.97 | $-4.54 | $-23.13 to $+15.10 | no evidence of edge |
| LLY | 41 | $+6.27 | $+7.16 | $-15.66 to $+30.05 | no evidence of edge |

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
| ORB, paper | 312 | $-9.41 | $-28.23 to $+9.91 | no evidence of edge |
| ORB, backtest | 499 | $-18.70 | $-28.53 to $-8.66 | loses beyond the market |

## How to read this

- The 95% range is a bootstrap interval of the SPY-adjusted mean. A range that crosses zero means the data can't distinguish the strategy from luck.
- Variants (`_tuned`, `_regime`) are pooled into their base strategy; both were switched off on 2026-10-21 after losing more than the defaults.
- The traded universe widened from 6 high-beta tech/crypto names to 10 across sectors on 2026-10-21; the by-symbol table shows whether that helps.
