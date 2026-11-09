# Lab review — is anything beating the market?

Generated 2026-11-09 · 1300 settled paper trades over 53 sessions (2026-08-24 → 2026-11-09) · 1300 SPY-adjusted.

**SPY-adjusted** = the trade's P&L plus an opposite, beta-weighted SPY position held for the same minutes, minus that hedge's slippage. It removes the market's intraday drift, which raw P&L can't tell apart from skill (in Sep–Oct 2026 SPY fell intraday on 27 of 43 days, so shorts looked profitable and longs looked broken).

## Decision gate

**Undecided — 42 days to the decision date.** No strategy beats the market yet.

Rule, set 2026-10-21: by **2026-12-21**, a strategy that has at least 100 SPY-adjusted paper trades and a 95% range entirely above zero keeps running. If none does, the study concludes.

## Paper trading, by strategy (variants pooled)

| strategy_base | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| orb | 319 | $+6.79 | $-9.54 | $-27.47 to $+8.94 | no evidence of edge |
| ar_forecast | 230 | $-6.07 | $-20.60 | $-33.98 to $-7.07 | loses beyond the market |
| high_break_trail | 225 | $-8.07 | $-20.31 | $-35.26 to $-5.24 | loses beyond the market |
| vwap_pullback | 212 | $-1.23 | $-14.16 | $-24.58 to $-3.03 | loses beyond the market |
| rsi2_reversion | 162 | $-7.39 | $-18.22 | $-31.29 to $-4.70 | loses beyond the market |
| ema_crossover | 73 | $-10.45 | $-15.89 | $-33.91 to $+2.43 | no evidence of edge |
| squeeze_breakout | 45 | $-4.47 | $-3.98 | $-24.13 to $+15.58 | no evidence of edge |
| news_momentum | 23 | $-36.07 | $-36.01 | $-83.41 to $+8.44 | too few trades |
| gap_and_go | 11 | $+89.10 | $-28.85 | $-95.33 to $+45.02 | too few trades |

## Paper trading, by side

| side | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| long | 685 | $-17.38 | $-24.84 | $-34.58 to $-15.60 | loses beyond the market |
| short | 615 | $+13.97 | $-6.14 | $-14.75 to $+2.32 | no evidence of edge |

## Paper trading, by symbol

| symbol | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| COIN | 201 | $+8.63 | $-24.45 | $-49.31 to $+0.73 | no evidence of edge |
| NVDA | 179 | $+16.45 | $+0.04 | $-9.10 to $+8.78 | no evidence of edge |
| TSLA | 169 | $-18.45 | $-24.80 | $-37.92 to $-12.07 | loses beyond the market |
| AMD | 150 | $-16.20 | $-20.93 | $-36.17 to $-6.15 | loses beyond the market |
| MSTR | 143 | $+3.95 | $-30.67 | $-60.59 to $-0.24 | loses beyond the market |
| PLTR | 133 | $-21.04 | $-24.23 | $-41.50 to $-6.03 | loses beyond the market |
| AMZN | 49 | $-34.44 | $-22.61 | $-45.06 to $+1.56 | no evidence of edge |
| UNH | 48 | $+2.68 | $-3.93 | $-33.87 to $+27.59 | no evidence of edge |
| XOM | 47 | $+9.59 | $+11.85 | $-9.95 to $+36.13 | no evidence of edge |
| CAT | 46 | $-15.18 | $-30.44 | $-48.04 to $-12.64 | loses beyond the market |
| WMT | 46 | $+16.67 | $+16.70 | $-5.52 to $+38.78 | no evidence of edge |
| JPM | 45 | $+4.80 | $-3.64 | $-20.77 to $+15.04 | no evidence of edge |
| LLY | 44 | $+13.84 | $+13.42 | $-8.66 to $+35.44 | no evidence of edge |

## Backtest (60-day window), by strategy

| strategy | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| rsi2_reversion | 1139 | $-8.42 | $-11.70 | $-13.26 to $-10.20 | loses beyond the market |
| vwap_pullback | 709 | $-10.31 | $-14.74 | $-19.79 to $-9.47 | loses beyond the market |
| ar_forecast | 676 | $-11.95 | $-14.28 | $-17.53 to $-11.00 | loses beyond the market |
| ema_crossover | 652 | $-12.45 | $-15.09 | $-18.45 to $-11.53 | loses beyond the market |
| orb | 500 | $-15.15 | $-21.87 | $-31.87 to $-11.51 | loses beyond the market |
| squeeze_breakout | 440 | $-13.20 | $-15.85 | $-19.98 to $-11.60 | loses beyond the market |
| high_break_trail | 437 | $-17.62 | $-22.38 | $-29.79 to $-14.82 | loses beyond the market |
| news_momentum | 84 | $-22.68 | $-22.64 | $-35.19 to $-9.24 | loses beyond the market |
| gap_and_go | 4 | $+182.83 | $+128.69 | $+10.14 to $+215.23 | too few trades |

## Market-neutral ORB

ORB was the lab's best raw performer. Hedged against SPY, does anything remain?

| book | trades | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|
| ORB, paper | 319 | $-9.54 | $-27.74 to $+9.56 | no evidence of edge |
| ORB, backtest | 500 | $-21.87 | $-31.70 to $-11.94 | loses beyond the market |

## How to read this

- The 95% range is a bootstrap interval of the SPY-adjusted mean. A range that crosses zero means the data can't distinguish the strategy from luck.
- Variants (`_tuned`, `_regime`) are pooled into their base strategy; both were switched off on 2026-10-21 after losing more than the defaults.
- The traded universe widened from 6 high-beta tech/crypto names to 10 across sectors on 2026-10-21; the by-symbol table shows whether that helps.
