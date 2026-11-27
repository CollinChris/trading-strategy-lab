# Lab review — is anything beating the market?

Generated 2026-11-27 · 1703 settled paper trades over 65 sessions (2026-08-24 → 2026-11-25) · 1703 SPY-adjusted.

**SPY-adjusted** = the trade's P&L plus an opposite, beta-weighted SPY position held for the same minutes, minus that hedge's slippage. It removes the market's intraday drift, which raw P&L can't tell apart from skill (in Sep–Oct 2026 SPY fell intraday on 27 of 43 days, so shorts looked profitable and longs looked broken).

## Decision gate

**Undecided — 24 days to the decision date.** No strategy beats the market yet.

Rule, set 2026-10-21: by **2026-12-21**, a strategy that has at least 100 SPY-adjusted paper trades and a 95% range entirely above zero keeps running. If none does, the study concludes.

## Paper trading, by strategy (variants pooled)

| strategy_base | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| orb | 413 | $+3.98 | $-14.96 | $-32.12 to $+2.23 | no evidence of edge |
| high_break_trail | 303 | $-1.22 | $-21.47 | $-36.70 to $-6.94 | loses beyond the market |
| ar_forecast | 297 | $-0.37 | $-17.66 | $-29.15 to $-5.49 | loses beyond the market |
| vwap_pullback | 292 | $+2.23 | $-13.23 | $-23.18 to $-2.84 | loses beyond the market |
| rsi2_reversion | 208 | $-2.94 | $-15.82 | $-27.18 to $-3.71 | loses beyond the market |
| ema_crossover | 87 | $-3.78 | $-14.81 | $-30.15 to $+0.99 | no evidence of edge |
| squeeze_breakout | 57 | $-5.98 | $-4.49 | $-21.20 to $+13.27 | no evidence of edge |
| news_momentum | 34 | $-52.02 | $-61.79 | $-154.73 to $+10.49 | no evidence of edge |
| gap_and_go | 12 | $+75.59 | $-32.74 | $-95.16 to $+36.58 | too few trades |

## Paper trading, by side

| side | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| short | 855 | $+20.99 | $-6.85 | $-14.52 to $+0.83 | no evidence of edge |
| long | 848 | $-21.54 | $-27.43 | $-37.39 to $-18.01 | loses beyond the market |

## Paper trading, by symbol

| symbol | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| COIN | 242 | $-4.90 | $-39.44 | $-63.09 to $-15.51 | loses beyond the market |
| NVDA | 223 | $+17.49 | $-12.71 | $-35.30 to $+5.63 | no evidence of edge |
| TSLA | 211 | $-7.24 | $-21.81 | $-34.12 to $-9.87 | loses beyond the market |
| AMD | 150 | $-16.20 | $-20.93 | $-36.17 to $-6.15 | loses beyond the market |
| MSTR | 143 | $+3.95 | $-30.67 | $-60.59 to $-0.24 | loses beyond the market |
| PLTR | 133 | $-21.04 | $-24.23 | $-41.50 to $-6.03 | loses beyond the market |
| AMZN | 91 | $-19.22 | $-16.09 | $-31.91 to $+0.52 | no evidence of edge |
| CAT | 91 | $-0.23 | $-35.18 | $-48.90 to $-21.19 | loses beyond the market |
| LLY | 86 | $+5.12 | $+4.71 | $-9.32 to $+18.55 | no evidence of edge |
| JPM | 85 | $+13.47 | $-2.04 | $-13.68 to $+9.67 | no evidence of edge |
| UNH | 85 | $+21.35 | $+14.80 | $-16.29 to $+49.94 | no evidence of edge |
| WMT | 82 | $-1.44 | $+0.37 | $-15.49 to $+16.70 | no evidence of edge |
| XOM | 81 | $+20.26 | $+21.63 | $+6.46 to $+37.59 | promising (needs more trades) |

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
| ORB, paper | 413 | $-14.96 | $-31.72 to $+2.00 | no evidence of edge |
| ORB, backtest | 500 | $-17.53 | $-28.28 to $-6.96 | loses beyond the market |

## How to read this

- The 95% range is a bootstrap interval of the SPY-adjusted mean. A range that crosses zero means the data can't distinguish the strategy from luck.
- Variants (`_tuned`, `_regime`) are pooled into their base strategy; both were switched off on 2026-10-21 after losing more than the defaults.
- The traded universe widened from 6 high-beta tech/crypto names to 10 across sectors on 2026-10-21; the by-symbol table shows whether that helps.
