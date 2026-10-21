# Lab review — is anything beating the market?

Generated 2026-10-20 · 821 settled paper trades over 39 sessions (2026-08-24 → 2026-10-20) · 821 SPY-adjusted.

**SPY-adjusted** = the trade's P&L plus an opposite, beta-weighted SPY position held for the same minutes, minus that hedge's slippage. It removes the market's intraday drift, which raw P&L can't tell apart from skill (in Sep–Oct 2026 SPY fell intraday on 27 of 43 days, so shorts looked profitable and longs looked broken).

## Decision gate

**Undecided — 62 days to the decision date.** No strategy beats the market yet.

Rule, set 2026-10-21: by **2026-12-21**, a strategy that has at least 100 SPY-adjusted paper trades and a 95% range entirely above zero keeps running. If none does, the study concludes.

## Paper trading, by strategy (variants pooled)

| strategy_base | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| orb | 204 | $+12.62 | $-1.94 | $-28.29 to $+25.24 | no evidence of edge |
| ar_forecast | 167 | $-1.98 | $-18.57 | $-34.44 to $-2.33 | loses beyond the market |
| high_break_trail | 132 | $-8.17 | $-20.08 | $-41.73 to $+2.49 | no evidence of edge |
| vwap_pullback | 125 | $-1.30 | $-17.90 | $-32.37 to $-3.04 | loses beyond the market |
| rsi2_reversion | 101 | $-15.89 | $-26.65 | $-44.46 to $-8.10 | loses beyond the market |
| ema_crossover | 49 | $-11.60 | $-18.53 | $-41.73 to $+5.59 | no evidence of edge |
| squeeze_breakout | 28 | $-7.83 | $-8.92 | $-39.37 to $+23.30 | too few trades |
| news_momentum | 11 | $-47.75 | $-77.64 | $-154.95 to $-2.19 | too few trades |
| gap_and_go | 4 | $+235.91 | $+69.82 | $-56.05 to $+187.00 | too few trades |

## Paper trading, by side

| side | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| long | 439 | $-15.16 | $-28.18 | $-41.62 to $-14.38 | loses beyond the market |
| short | 382 | $+14.88 | $-1.14 | $-12.56 to $+10.66 | no evidence of edge |

## Paper trading, by symbol

| symbol | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| AMD | 150 | $-16.20 | $-20.93 | $-35.24 to $-6.15 | loses beyond the market |
| COIN | 147 | $+31.98 | $+3.56 | $-26.93 to $+35.67 | no evidence of edge |
| MSTR | 143 | $+3.95 | $-30.67 | $-61.34 to $+1.09 | no evidence of edge |
| PLTR | 133 | $-21.04 | $-24.23 | $-40.86 to $-6.53 | loses beyond the market |
| NVDA | 126 | $+10.21 | $+2.98 | $-6.44 to $+12.16 | no evidence of edge |
| TSLA | 122 | $-18.84 | $-24.27 | $-39.19 to $-9.44 | loses beyond the market |

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
| ORB, paper | 204 | $-1.94 | $-27.16 to $+24.25 | no evidence of edge |
| ORB, backtest | 503 | $-15.57 | $-25.64 to $-4.89 | loses beyond the market |

## How to read this

- The 95% range is a bootstrap interval of the SPY-adjusted mean. A range that crosses zero means the data can't distinguish the strategy from luck.
- Variants (`_tuned`, `_regime`) are pooled into their base strategy; both were switched off on 2026-10-21 after losing more than the defaults.
- The traded universe widened from 6 high-beta tech/crypto names to 10 across sectors on 2026-10-21; the by-symbol table shows whether that helps.
