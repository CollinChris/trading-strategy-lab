# Lab review — is anything beating the market?

Generated 2026-10-29 · 1014 settled paper trades over 45 sessions (2026-08-24 → 2026-10-28) · 1014 SPY-adjusted.

**SPY-adjusted** = the trade's P&L plus an opposite, beta-weighted SPY position held for the same minutes, minus that hedge's slippage. It removes the market's intraday drift, which raw P&L can't tell apart from skill (in Sep–Oct 2026 SPY fell intraday on 27 of 43 days, so shorts looked profitable and longs looked broken).

## Decision gate

**Undecided — 53 days to the decision date.** No strategy beats the market yet.

Rule, set 2026-10-21: by **2026-12-21**, a strategy that has at least 100 SPY-adjusted paper trades and a 95% range entirely above zero keeps running. If none does, the study concludes.

## Paper trading, by strategy (variants pooled)

| strategy_base | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| orb | 256 | $+4.61 | $-4.48 | $-26.66 to $+17.10 | no evidence of edge |
| ar_forecast | 185 | $-0.86 | $-15.95 | $-31.20 to $-1.41 | loses beyond the market |
| high_break_trail | 168 | $-7.69 | $-17.84 | $-35.40 to $+0.15 | no evidence of edge |
| vwap_pullback | 167 | $-1.40 | $-14.77 | $-26.89 to $-2.28 | loses beyond the market |
| rsi2_reversion | 123 | $-16.14 | $-24.92 | $-39.43 to $-9.20 | loses beyond the market |
| ema_crossover | 54 | $-12.82 | $-19.05 | $-40.04 to $+3.42 | no evidence of edge |
| squeeze_breakout | 36 | $-6.37 | $-7.31 | $-32.13 to $+18.33 | no evidence of edge |
| news_momentum | 19 | $-42.37 | $-50.35 | $-99.66 to $-4.97 | too few trades |
| gap_and_go | 6 | $+154.25 | $+28.54 | $-55.38 to $+125.92 | too few trades |

## Paper trading, by side

| side | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| long | 542 | $-15.79 | $-26.78 | $-37.90 to $-15.32 | loses beyond the market |
| short | 472 | $+11.16 | $-0.40 | $-10.29 to $+9.20 | no evidence of edge |

## Paper trading, by symbol

| symbol | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| COIN | 169 | $+20.66 | $-2.08 | $-28.61 to $+25.99 | no evidence of edge |
| AMD | 150 | $-16.20 | $-20.93 | $-35.52 to $-5.40 | loses beyond the market |
| NVDA | 148 | $+10.37 | $+5.63 | $-2.90 to $+14.59 | no evidence of edge |
| MSTR | 143 | $+3.95 | $-30.67 | $-60.68 to $+0.54 | no evidence of edge |
| TSLA | 142 | $-19.61 | $-25.30 | $-39.53 to $-12.39 | loses beyond the market |
| PLTR | 133 | $-21.04 | $-24.23 | $-41.50 to $-6.03 | loses beyond the market |
| AMZN | 22 | $-22.12 | $-20.01 | $-40.93 to $+3.10 | too few trades |
| XOM | 20 | $+23.59 | $+22.34 | $-6.01 to $+52.87 | too few trades |
| CAT | 19 | $-23.79 | $-32.05 | $-57.56 to $-3.81 | too few trades |
| UNH | 19 | $-3.34 | $-2.91 | $-42.27 to $+33.25 | too few trades |
| WMT | 18 | $-0.45 | $-0.34 | $-30.19 to $+28.58 | too few trades |
| LLY | 16 | $-7.47 | $-6.65 | $-34.98 to $+19.38 | too few trades |
| JPM | 15 | $-14.12 | $-5.15 | $-21.35 to $+9.91 | too few trades |

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
| ORB, paper | 256 | $-4.48 | $-25.84 to $+17.82 | no evidence of edge |
| ORB, backtest | 498 | $-15.31 | $-25.62 to $-5.34 | loses beyond the market |

## How to read this

- The 95% range is a bootstrap interval of the SPY-adjusted mean. A range that crosses zero means the data can't distinguish the strategy from luck.
- Variants (`_tuned`, `_regime`) are pooled into their base strategy; both were switched off on 2026-10-21 after losing more than the defaults.
- The traded universe widened from 6 high-beta tech/crypto names to 10 across sectors on 2026-10-21; the by-symbol table shows whether that helps.
