# Lab review — is anything beating the market?

Generated 2026-11-02 · 1088 settled paper trades over 48 sessions (2026-08-24 → 2026-11-02) · 1088 SPY-adjusted.

**SPY-adjusted** = the trade's P&L plus an opposite, beta-weighted SPY position held for the same minutes, minus that hedge's slippage. It removes the market's intraday drift, which raw P&L can't tell apart from skill (in Sep–Oct 2026 SPY fell intraday on 27 of 43 days, so shorts looked profitable and longs looked broken).

## Decision gate

**Undecided — 49 days to the decision date.** No strategy beats the market yet.

Rule, set 2026-10-21: by **2026-12-21**, a strategy that has at least 100 SPY-adjusted paper trades and a 95% range entirely above zero keeps running. If none does, the study concludes.

## Paper trading, by strategy (variants pooled)

| strategy_base | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| orb | 271 | $-0.12 | $-7.49 | $-28.19 to $+13.34 | no evidence of edge |
| ar_forecast | 199 | $-3.16 | $-17.73 | $-31.78 to $-3.49 | loses beyond the market |
| high_break_trail | 181 | $-10.41 | $-19.03 | $-35.43 to $-2.73 | loses beyond the market |
| vwap_pullback | 180 | $-1.93 | $-14.20 | $-25.58 to $-2.78 | loses beyond the market |
| rsi2_reversion | 134 | $-15.58 | $-22.05 | $-36.50 to $-7.19 | loses beyond the market |
| ema_crossover | 58 | $-15.00 | $-22.67 | $-42.82 to $-0.75 | loses beyond the market |
| squeeze_breakout | 38 | $-5.82 | $-6.42 | $-29.38 to $+18.22 | no evidence of edge |
| news_momentum | 20 | $-42.75 | $-49.58 | $-95.74 to $-6.37 | too few trades |
| gap_and_go | 7 | $+153.36 | $+29.73 | $-42.20 to $+109.42 | too few trades |

## Paper trading, by side

| side | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| long | 572 | $-18.17 | $-26.50 | $-37.40 to $-15.30 | loses beyond the market |
| short | 516 | $+8.80 | $-3.29 | $-12.48 to $+6.23 | no evidence of edge |

## Paper trading, by symbol

| symbol | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| COIN | 179 | $+13.43 | $-8.95 | $-35.07 to $+17.00 | no evidence of edge |
| NVDA | 156 | $+12.69 | $+5.72 | $-2.78 to $+14.28 | no evidence of edge |
| AMD | 150 | $-16.20 | $-20.93 | $-35.79 to $-5.88 | loses beyond the market |
| TSLA | 149 | $-22.25 | $-24.18 | $-37.24 to $-11.00 | loses beyond the market |
| MSTR | 143 | $+3.95 | $-30.67 | $-60.59 to $-0.24 | loses beyond the market |
| PLTR | 133 | $-21.04 | $-24.23 | $-41.50 to $-6.03 | loses beyond the market |
| AMZN | 28 | $-16.46 | $-2.75 | $-29.63 to $+27.66 | too few trades |
| XOM | 28 | $-0.08 | $+0.86 | $-25.23 to $+26.77 | too few trades |
| CAT | 26 | $-46.15 | $-41.57 | $-64.50 to $-19.62 | too few trades |
| WMT | 26 | $-6.94 | $-6.88 | $-29.88 to $+15.82 | too few trades |
| UNH | 25 | $-4.82 | $-8.45 | $-38.13 to $+20.61 | too few trades |
| LLY | 23 | $-2.83 | $-4.35 | $-27.17 to $+17.75 | too few trades |
| JPM | 22 | $-10.48 | $-7.86 | $-21.82 to $+4.98 | too few trades |

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
| ORB, paper | 271 | $-7.49 | $-27.83 to $+13.50 | no evidence of edge |
| ORB, backtest | 499 | $-18.70 | $-28.53 to $-8.66 | loses beyond the market |

## How to read this

- The 95% range is a bootstrap interval of the SPY-adjusted mean. A range that crosses zero means the data can't distinguish the strategy from luck.
- Variants (`_tuned`, `_regime`) are pooled into their base strategy; both were switched off on 2026-10-21 after losing more than the defaults.
- The traded universe widened from 6 high-beta tech/crypto names to 10 across sectors on 2026-10-21; the by-symbol table shows whether that helps.
