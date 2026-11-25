# Lab review — is anything beating the market?

Generated 2026-11-25 · 1669 settled paper trades over 64 sessions (2026-08-24 → 2026-11-24) · 1669 SPY-adjusted.

**SPY-adjusted** = the trade's P&L plus an opposite, beta-weighted SPY position held for the same minutes, minus that hedge's slippage. It removes the market's intraday drift, which raw P&L can't tell apart from skill (in Sep–Oct 2026 SPY fell intraday on 27 of 43 days, so shorts looked profitable and longs looked broken).

## Decision gate

**Undecided — 26 days to the decision date.** No strategy beats the market yet.

Rule, set 2026-10-21: by **2026-12-21**, a strategy that has at least 100 SPY-adjusted paper trades and a 95% range entirely above zero keeps running. If none does, the study concludes.

## Paper trading, by strategy (variants pooled)

| strategy_base | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| orb | 406 | $+3.58 | $-14.75 | $-31.73 to $+2.54 | no evidence of edge |
| high_break_trail | 295 | $-3.49 | $-22.13 | $-37.98 to $-6.90 | loses beyond the market |
| ar_forecast | 291 | $+0.71 | $-17.54 | $-29.60 to $-5.02 | loses beyond the market |
| vwap_pullback | 286 | $+3.43 | $-12.63 | $-22.50 to $-2.64 | loses beyond the market |
| rsi2_reversion | 204 | $-2.62 | $-15.46 | $-27.12 to $-3.08 | loses beyond the market |
| ema_crossover | 86 | $-6.50 | $-15.08 | $-30.62 to $+0.87 | no evidence of edge |
| squeeze_breakout | 56 | $-5.26 | $-4.92 | $-21.86 to $+12.70 | no evidence of edge |
| news_momentum | 33 | $-65.75 | $-69.04 | $-165.12 to $+4.45 | no evidence of edge |
| gap_and_go | 12 | $+75.59 | $-32.74 | $-95.16 to $+36.58 | too few trades |

## Paper trading, by side

| side | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| short | 839 | $+23.22 | $-5.93 | $-13.56 to $+1.56 | no evidence of edge |
| long | 830 | $-24.73 | $-28.50 | $-38.42 to $-18.93 | loses beyond the market |

## Paper trading, by symbol

| symbol | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| COIN | 239 | $-5.44 | $-39.59 | $-63.64 to $-15.60 | loses beyond the market |
| NVDA | 221 | $+15.84 | $-12.25 | $-35.77 to $+6.46 | no evidence of edge |
| TSLA | 208 | $-10.96 | $-23.89 | $-35.44 to $-12.00 | loses beyond the market |
| AMD | 150 | $-16.20 | $-20.93 | $-36.17 to $-6.15 | loses beyond the market |
| MSTR | 143 | $+3.95 | $-30.67 | $-60.59 to $-0.24 | loses beyond the market |
| PLTR | 133 | $-21.04 | $-24.23 | $-41.50 to $-6.03 | loses beyond the market |
| CAT | 88 | $-6.96 | $-38.73 | $-52.79 to $-24.40 | loses beyond the market |
| AMZN | 85 | $-13.00 | $-13.58 | $-31.22 to $+3.92 | no evidence of edge |
| JPM | 82 | $+15.46 | $-1.01 | $-12.55 to $+10.74 | no evidence of edge |
| LLY | 82 | $+11.23 | $+7.93 | $-6.43 to $+22.78 | no evidence of edge |
| UNH | 82 | $+20.18 | $+17.30 | $-14.29 to $+52.82 | no evidence of edge |
| WMT | 78 | $-0.17 | $+0.97 | $-15.93 to $+18.00 | no evidence of edge |
| XOM | 78 | $+20.42 | $+22.55 | $+6.45 to $+38.47 | promising (needs more trades) |

## Backtest (60-day window), by strategy

| strategy | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| rsi2_reversion | 1121 | $-7.06 | $-11.01 | $-12.50 to $-9.57 | loses beyond the market |
| ar_forecast | 731 | $-11.04 | $-13.50 | $-16.48 to $-10.50 | loses beyond the market |
| vwap_pullback | 689 | $-4.72 | $-12.34 | $-17.49 to $-7.07 | loses beyond the market |
| ema_crossover | 631 | $-12.54 | $-15.29 | $-18.80 to $-11.63 | loses beyond the market |
| orb | 500 | $-6.84 | $-17.53 | $-28.24 to $-6.44 | loses beyond the market |
| high_break_trail | 452 | $-8.79 | $-22.63 | $-30.52 to $-14.99 | loses beyond the market |
| squeeze_breakout | 417 | $-11.44 | $-15.45 | $-19.73 to $-10.95 | loses beyond the market |
| news_momentum | 39 | $+10.91 | $+15.47 | $-9.51 to $+43.79 | no evidence of edge |
| gap_and_go | 3 | $+141.47 | $+100.91 | $-55.67 to $+218.13 | too few trades |

## Market-neutral ORB

ORB was the lab's best raw performer. Hedged against SPY, does anything remain?

| book | trades | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|
| ORB, paper | 406 | $-14.75 | $-32.06 to $+2.51 | no evidence of edge |
| ORB, backtest | 500 | $-17.53 | $-28.28 to $-6.96 | loses beyond the market |

## How to read this

- The 95% range is a bootstrap interval of the SPY-adjusted mean. A range that crosses zero means the data can't distinguish the strategy from luck.
- Variants (`_tuned`, `_regime`) are pooled into their base strategy; both were switched off on 2026-10-21 after losing more than the defaults.
- The traded universe widened from 6 high-beta tech/crypto names to 10 across sectors on 2026-10-21; the by-symbol table shows whether that helps.
