# Lab review — is anything beating the market?

Generated 2026-10-27 · 961 settled paper trades over 44 sessions (2026-08-24 → 2026-10-27) · 961 SPY-adjusted.

**SPY-adjusted** = the trade's P&L plus an opposite, beta-weighted SPY position held for the same minutes, minus that hedge's slippage. It removes the market's intraday drift, which raw P&L can't tell apart from skill (in Sep–Oct 2026 SPY fell intraday on 27 of 43 days, so shorts looked profitable and longs looked broken).

## Decision gate

**Undecided — 55 days to the decision date.** No strategy beats the market yet.

Rule, set 2026-10-21: by **2026-12-21**, a strategy that has at least 100 SPY-adjusted paper trades and a 95% range entirely above zero keeps running. If none does, the study concludes.

## Paper trading, by strategy (variants pooled)

| strategy_base | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| orb | 242 | $+6.21 | $-3.84 | $-25.52 to $+19.16 | no evidence of edge |
| ar_forecast | 181 | $+0.15 | $-15.59 | $-30.73 to $+0.34 | no evidence of edge |
| high_break_trail | 158 | $-9.30 | $-19.50 | $-37.72 to $-0.99 | loses beyond the market |
| vwap_pullback | 156 | $-1.96 | $-15.83 | $-28.72 to $-2.93 | loses beyond the market |
| rsi2_reversion | 114 | $-16.91 | $-26.09 | $-42.14 to $-9.76 | loses beyond the market |
| ema_crossover | 51 | $-11.56 | $-18.07 | $-39.73 to $+6.16 | no evidence of edge |
| squeeze_breakout | 35 | $-7.85 | $-8.64 | $-33.09 to $+16.73 | no evidence of edge |
| news_momentum | 18 | $-46.51 | $-54.64 | $-106.80 to $-8.52 | too few trades |
| gap_and_go | 6 | $+154.25 | $+28.54 | $-55.38 to $+125.92 | too few trades |

## Paper trading, by side

| side | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| long | 517 | $-17.07 | $-27.73 | $-39.13 to $-16.03 | loses beyond the market |
| short | 444 | $+13.23 | $+0.05 | $-10.22 to $+10.52 | no evidence of edge |

## Paper trading, by symbol

| symbol | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| COIN | 163 | $+23.60 | $-1.27 | $-27.77 to $+27.87 | no evidence of edge |
| AMD | 150 | $-16.20 | $-20.93 | $-35.52 to $-5.40 | loses beyond the market |
| MSTR | 143 | $+3.95 | $-30.67 | $-61.34 to $+1.09 | no evidence of edge |
| NVDA | 142 | $+8.99 | $+3.19 | $-5.54 to $+11.78 | no evidence of edge |
| TSLA | 134 | $-20.78 | $-25.62 | $-39.48 to $-11.50 | loses beyond the market |
| PLTR | 133 | $-21.04 | $-24.23 | $-41.50 to $-6.03 | loses beyond the market |
| AMZN | 17 | $-22.13 | $-17.88 | $-42.14 to $+8.62 | too few trades |
| UNH | 16 | $+14.41 | $+15.42 | $-22.53 to $+50.29 | too few trades |
| XOM | 15 | $+14.24 | $+14.40 | $-18.59 to $+49.21 | too few trades |
| CAT | 13 | $-36.70 | $-36.62 | $-68.97 to $-2.41 | too few trades |
| LLY | 12 | $+0.15 | $+2.20 | $-28.65 to $+31.97 | too few trades |
| WMT | 12 | $-0.44 | $-0.27 | $-44.16 to $+42.78 | too few trades |
| JPM | 11 | $-19.38 | $-7.73 | $-29.42 to $+10.83 | too few trades |

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
| ORB, paper | 242 | $-3.84 | $-26.75 to $+18.72 | no evidence of edge |
| ORB, backtest | 498 | $-15.31 | $-25.62 to $-5.34 | loses beyond the market |

## How to read this

- The 95% range is a bootstrap interval of the SPY-adjusted mean. A range that crosses zero means the data can't distinguish the strategy from luck.
- Variants (`_tuned`, `_regime`) are pooled into their base strategy; both were switched off on 2026-10-21 after losing more than the defaults.
- The traded universe widened from 6 high-beta tech/crypto names to 10 across sectors on 2026-10-21; the by-symbol table shows whether that helps.
