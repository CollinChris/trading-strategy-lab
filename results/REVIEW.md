# Lab review — is anything beating the market?

Generated 2026-10-27 · 980 settled paper trades over 44 sessions (2026-08-24 → 2026-10-27) · 980 SPY-adjusted.

**SPY-adjusted** = the trade's P&L plus an opposite, beta-weighted SPY position held for the same minutes, minus that hedge's slippage. It removes the market's intraday drift, which raw P&L can't tell apart from skill (in Sep–Oct 2026 SPY fell intraday on 27 of 43 days, so shorts looked profitable and longs looked broken).

## Decision gate

**Undecided — 55 days to the decision date.** No strategy beats the market yet.

Rule, set 2026-10-21: by **2026-12-21**, a strategy that has at least 100 SPY-adjusted paper trades and a 95% range entirely above zero keeps running. If none does, the study concludes.

## Paper trading, by strategy (variants pooled)

| strategy_base | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| orb | 247 | $+5.53 | $-4.07 | $-25.62 to $+18.70 | no evidence of edge |
| ar_forecast | 182 | $-0.13 | $-15.57 | $-30.33 to $+0.18 | no evidence of edge |
| high_break_trail | 163 | $-7.31 | $-17.94 | $-34.76 to $-0.04 | loses beyond the market |
| vwap_pullback | 160 | $-0.32 | $-14.43 | $-27.09 to $-1.82 | loses beyond the market |
| rsi2_reversion | 118 | $-15.54 | $-24.81 | $-39.76 to $-9.43 | loses beyond the market |
| ema_crossover | 51 | $-11.56 | $-18.07 | $-39.73 to $+6.16 | no evidence of edge |
| squeeze_breakout | 35 | $-7.85 | $-8.64 | $-33.09 to $+16.73 | no evidence of edge |
| news_momentum | 18 | $-46.51 | $-54.64 | $-106.80 to $-8.52 | too few trades |
| gap_and_go | 6 | $+154.25 | $+28.54 | $-55.38 to $+125.92 | too few trades |

## Paper trading, by side

| side | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| long | 527 | $-15.90 | $-27.16 | $-38.33 to $-15.74 | loses beyond the market |
| short | 453 | $+12.95 | $+0.61 | $-9.49 to $+11.20 | no evidence of edge |

## Paper trading, by symbol

| symbol | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| COIN | 165 | $+21.92 | $-1.57 | $-28.11 to $+26.83 | no evidence of edge |
| AMD | 150 | $-16.20 | $-20.93 | $-35.52 to $-5.40 | loses beyond the market |
| MSTR | 143 | $+3.95 | $-30.67 | $-61.34 to $+1.09 | no evidence of edge |
| NVDA | 143 | $+8.71 | $+3.58 | $-5.15 to $+12.31 | no evidence of edge |
| TSLA | 137 | $-18.83 | $-24.69 | $-38.17 to $-10.87 | loses beyond the market |
| PLTR | 133 | $-21.04 | $-24.23 | $-41.50 to $-6.03 | loses beyond the market |
| AMZN | 19 | $-12.92 | $-12.93 | $-34.99 to $+11.93 | too few trades |
| UNH | 17 | $+11.01 | $+11.78 | $-23.46 to $+46.73 | too few trades |
| XOM | 17 | $+25.20 | $+23.97 | $-10.14 to $+56.96 | too few trades |
| CAT | 16 | $-12.72 | $-24.42 | $-54.59 to $+7.01 | too few trades |
| WMT | 15 | $+4.24 | $+4.38 | $-31.10 to $+39.85 | too few trades |
| LLY | 13 | $-8.94 | $-7.53 | $-41.89 to $+25.28 | too few trades |
| JPM | 12 | $-20.26 | $-8.29 | $-27.07 to $+9.72 | too few trades |

## Backtest (60-day window), by strategy

| strategy | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| rsi2_reversion | 1160 | $-9.39 | $-12.18 | $-13.68 to $-10.73 | loses beyond the market |
| vwap_pullback | 710 | $-12.56 | $-16.99 | $-22.02 to $-11.89 | loses beyond the market |
| ar_forecast | 659 | $-9.26 | $-11.24 | $-14.43 to $-8.09 | loses beyond the market |
| ema_crossover | 644 | $-12.69 | $-16.11 | $-19.44 to $-12.70 | loses beyond the market |
| orb | 498 | $-13.80 | $-15.31 | $-25.39 to $-5.01 | loses beyond the market |
| squeeze_breakout | 438 | $-16.13 | $-18.30 | $-22.52 to $-14.14 | loses beyond the market |
| high_break_trail | 429 | $-16.02 | $-22.05 | $-29.02 to $-14.96 | loses beyond the market |
| news_momentum | 78 | $-23.24 | $-25.89 | $-39.74 to $-11.53 | loses beyond the market |
| gap_and_go | 5 | $+112.86 | $+68.51 | $-72.90 to $+199.71 | too few trades |

## Market-neutral ORB

ORB was the lab's best raw performer. Hedged against SPY, does anything remain?

| book | trades | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|
| ORB, paper | 247 | $-4.07 | $-27.09 to $+17.80 | no evidence of edge |
| ORB, backtest | 498 | $-15.31 | $-25.62 to $-5.34 | loses beyond the market |

## How to read this

- The 95% range is a bootstrap interval of the SPY-adjusted mean. A range that crosses zero means the data can't distinguish the strategy from luck.
- Variants (`_tuned`, `_regime`) are pooled into their base strategy; both were switched off on 2026-10-21 after losing more than the defaults.
- The traded universe widened from 6 high-beta tech/crypto names to 10 across sectors on 2026-10-21; the by-symbol table shows whether that helps.
