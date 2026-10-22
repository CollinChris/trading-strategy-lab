# Lab review — is anything beating the market?

Generated 2026-10-22 · 861 settled paper trades over 41 sessions (2026-08-24 → 2026-10-22) · 861 SPY-adjusted.

**SPY-adjusted** = the trade's P&L plus an opposite, beta-weighted SPY position held for the same minutes, minus that hedge's slippage. It removes the market's intraday drift, which raw P&L can't tell apart from skill (in Sep–Oct 2026 SPY fell intraday on 27 of 43 days, so shorts looked profitable and longs looked broken).

## Decision gate

**Undecided — 60 days to the decision date.** No strategy beats the market yet.

Rule, set 2026-10-21: by **2026-12-21**, a strategy that has at least 100 SPY-adjusted paper trades and a 95% range entirely above zero keeps running. If none does, the study concludes.

## Paper trading, by strategy (variants pooled)

| strategy_base | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| orb | 214 | $+8.24 | $-4.16 | $-29.21 to $+21.15 | no evidence of edge |
| ar_forecast | 171 | $-2.32 | $-18.80 | $-34.19 to $-2.43 | loses beyond the market |
| high_break_trail | 138 | $-10.36 | $-21.97 | $-43.35 to $-0.98 | loses beyond the market |
| vwap_pullback | 136 | $-2.00 | $-16.88 | $-30.72 to $-3.16 | loses beyond the market |
| rsi2_reversion | 104 | $-17.88 | $-27.42 | $-44.74 to $-9.14 | loses beyond the market |
| ema_crossover | 50 | $-12.03 | $-18.85 | $-41.46 to $+4.97 | no evidence of edge |
| squeeze_breakout | 30 | $-6.85 | $-8.00 | $-37.32 to $+21.66 | no evidence of edge |
| news_momentum | 14 | $-49.55 | $-66.30 | $-131.02 to $-7.83 | too few trades |
| gap_and_go | 4 | $+235.91 | $+69.82 | $-56.05 to $+187.00 | too few trades |

## Paper trading, by side

| side | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| long | 459 | $-17.01 | $-29.24 | $-41.74 to $-16.07 | loses beyond the market |
| short | 402 | $+12.58 | $-1.72 | $-12.98 to $+9.51 | no evidence of edge |

## Paper trading, by symbol

| symbol | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| COIN | 153 | $+25.90 | $-0.74 | $-28.38 to $+29.14 | no evidence of edge |
| AMD | 150 | $-16.20 | $-20.93 | $-35.52 to $-5.40 | loses beyond the market |
| MSTR | 143 | $+3.95 | $-30.67 | $-61.34 to $+1.09 | no evidence of edge |
| PLTR | 133 | $-21.04 | $-24.23 | $-40.86 to $-6.53 | loses beyond the market |
| NVDA | 131 | $+10.35 | $+3.94 | $-4.86 to $+13.23 | no evidence of edge |
| TSLA | 125 | $-18.98 | $-24.74 | $-39.46 to $-10.06 | loses beyond the market |
| AMZN | 6 | $-58.34 | $-40.22 | $-56.36 to $-29.17 | too few trades |
| XOM | 6 | $-28.92 | $-27.80 | $-62.49 to $+8.52 | too few trades |
| CAT | 4 | $-43.07 | $-17.65 | $-88.59 to $+71.83 | too few trades |
| JPM | 3 | $-27.74 | $-0.39 | $-8.89 to $+4.76 | too few trades |
| WMT | 3 | $-40.88 | $-39.83 | $-47.37 to $-24.75 | too few trades |
| LLY | 2 | $-53.13 | $-41.22 | $-48.54 to $-33.89 | too few trades |
| UNH | 2 | $-13.66 | $+1.89 | $-4.35 to $+8.13 | too few trades |

## Backtest (60-day window), by strategy

| strategy | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| rsi2_reversion | 1173 | $-9.32 | $-11.95 | $-13.42 to $-10.53 | loses beyond the market |
| vwap_pullback | 714 | $-12.88 | $-17.00 | $-21.99 to $-11.93 | loses beyond the market |
| ar_forecast | 670 | $-8.28 | $-11.26 | $-14.40 to $-8.02 | loses beyond the market |
| ema_crossover | 650 | $-12.40 | $-15.68 | $-19.11 to $-12.25 | loses beyond the market |
| orb | 503 | $-11.95 | $-15.57 | $-25.42 to $-5.56 | loses beyond the market |
| high_break_trail | 437 | $-16.37 | $-21.47 | $-28.51 to $-14.14 | loses beyond the market |
| squeeze_breakout | 421 | $-15.82 | $-17.83 | $-21.80 to $-13.58 | loses beyond the market |
| news_momentum | 72 | $-17.75 | $-22.68 | $-36.08 to $-9.08 | loses beyond the market |
| gap_and_go | 5 | $+114.70 | $+59.81 | $-81.29 to $+199.23 | too few trades |

## Market-neutral ORB

ORB was the lab's best raw performer. Hedged against SPY, does anything remain?

| book | trades | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|
| ORB, paper | 214 | $-4.16 | $-29.07 to $+21.79 | no evidence of edge |
| ORB, backtest | 503 | $-15.57 | $-25.64 to $-4.89 | loses beyond the market |

## How to read this

- The 95% range is a bootstrap interval of the SPY-adjusted mean. A range that crosses zero means the data can't distinguish the strategy from luck.
- Variants (`_tuned`, `_regime`) are pooled into their base strategy; both were switched off on 2026-10-21 after losing more than the defaults.
- The traded universe widened from 6 high-beta tech/crypto names to 10 across sectors on 2026-10-21; the by-symbol table shows whether that helps.
