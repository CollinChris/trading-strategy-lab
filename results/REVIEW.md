# Lab review — is anything beating the market?

Generated 2026-10-23 · 897 settled paper trades over 42 sessions (2026-08-24 → 2026-10-23) · 897 SPY-adjusted.

**SPY-adjusted** = the trade's P&L plus an opposite, beta-weighted SPY position held for the same minutes, minus that hedge's slippage. It removes the market's intraday drift, which raw P&L can't tell apart from skill (in Sep–Oct 2026 SPY fell intraday on 27 of 43 days, so shorts looked profitable and longs looked broken).

## Decision gate

**Undecided — 59 days to the decision date.** No strategy beats the market yet.

Rule, set 2026-10-21: by **2026-12-21**, a strategy that has at least 100 SPY-adjusted paper trades and a 95% range entirely above zero keeps running. If none does, the study concludes.

## Paper trading, by strategy (variants pooled)

| strategy_base | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| orb | 222 | $+9.08 | $-2.77 | $-26.64 to $+22.63 | no evidence of edge |
| ar_forecast | 175 | $-1.59 | $-17.76 | $-32.92 to $-1.74 | loses beyond the market |
| high_break_trail | 147 | $-9.73 | $-20.87 | $-40.49 to $-0.70 | loses beyond the market |
| vwap_pullback | 144 | $-2.34 | $-16.64 | $-30.17 to $-3.08 | loses beyond the market |
| rsi2_reversion | 107 | $-18.00 | $-27.43 | $-43.97 to $-10.23 | loses beyond the market |
| ema_crossover | 51 | $-11.56 | $-18.07 | $-39.73 to $+6.16 | no evidence of edge |
| squeeze_breakout | 31 | $-7.30 | $-8.49 | $-37.00 to $+19.66 | no evidence of edge |
| news_momentum | 15 | $-57.60 | $-67.02 | $-126.32 to $-11.29 | too few trades |
| gap_and_go | 5 | $+179.80 | $+40.77 | $-59.93 to $+137.86 | too few trades |

## Paper trading, by side

| side | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| long | 478 | $-17.02 | $-28.13 | $-40.48 to $-16.11 | loses beyond the market |
| short | 419 | $+12.88 | $-1.58 | $-12.57 to $+9.07 | no evidence of edge |

## Paper trading, by symbol

| symbol | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| COIN | 157 | $+25.38 | $-0.82 | $-28.99 to $+28.47 | no evidence of edge |
| AMD | 150 | $-16.20 | $-20.93 | $-35.52 to $-5.40 | loses beyond the market |
| MSTR | 143 | $+3.95 | $-30.67 | $-61.34 to $+1.09 | no evidence of edge |
| NVDA | 134 | $+10.85 | $+3.87 | $-5.22 to $+13.14 | no evidence of edge |
| PLTR | 133 | $-21.04 | $-24.23 | $-41.42 to $-6.20 | loses beyond the market |
| TSLA | 128 | $-22.34 | $-26.44 | $-41.65 to $-12.00 | loses beyond the market |
| AMZN | 12 | $-8.13 | $-2.70 | $-31.47 to $+29.57 | too few trades |
| CAT | 8 | $-41.08 | $-49.10 | $-96.39 to $+6.81 | too few trades |
| XOM | 8 | $-33.59 | $-29.84 | $-62.48 to $+4.57 | too few trades |
| JPM | 7 | $-19.06 | $+2.35 | $-18.50 to $+19.29 | too few trades |
| UNH | 6 | $+15.83 | $+24.80 | $-0.16 to $+51.58 | too few trades |
| WMT | 6 | $+27.98 | $+27.95 | $-23.18 to $+76.33 | too few trades |
| LLY | 5 | $-17.96 | $-6.93 | $-39.05 to $+35.16 | too few trades |

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
| ORB, paper | 222 | $-2.77 | $-27.01 to $+22.13 | no evidence of edge |
| ORB, backtest | 503 | $-15.57 | $-25.64 to $-4.89 | loses beyond the market |

## How to read this

- The 95% range is a bootstrap interval of the SPY-adjusted mean. A range that crosses zero means the data can't distinguish the strategy from luck.
- Variants (`_tuned`, `_regime`) are pooled into their base strategy; both were switched off on 2026-10-21 after losing more than the defaults.
- The traded universe widened from 6 high-beta tech/crypto names to 10 across sectors on 2026-10-21; the by-symbol table shows whether that helps.
