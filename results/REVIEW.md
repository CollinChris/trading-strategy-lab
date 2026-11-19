# Lab review — is anything beating the market?

Generated 2026-11-19 · 1535 settled paper trades over 61 sessions (2026-08-24 → 2026-11-19) · 1535 SPY-adjusted.

**SPY-adjusted** = the trade's P&L plus an opposite, beta-weighted SPY position held for the same minutes, minus that hedge's slippage. It removes the market's intraday drift, which raw P&L can't tell apart from skill (in Sep–Oct 2026 SPY fell intraday on 27 of 43 days, so shorts looked profitable and longs looked broken).

## Decision gate

**Undecided — 32 days to the decision date.** No strategy beats the market yet.

Rule, set 2026-10-21: by **2026-12-21**, a strategy that has at least 100 SPY-adjusted paper trades and a 95% range entirely above zero keeps running. If none does, the study concludes.

## Paper trading, by strategy (variants pooled)

| strategy_base | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| orb | 372 | $+0.24 | $-14.66 | $-33.65 to $+3.16 | no evidence of edge |
| high_break_trail | 268 | $-12.61 | $-21.77 | $-39.04 to $-4.94 | loses beyond the market |
| ar_forecast | 265 | $-5.48 | $-18.75 | $-31.47 to $-5.68 | loses beyond the market |
| vwap_pullback | 262 | $-0.64 | $-14.99 | $-25.53 to $-4.38 | loses beyond the market |
| rsi2_reversion | 192 | $-8.05 | $-17.56 | $-29.35 to $-5.42 | loses beyond the market |
| ema_crossover | 82 | $-6.05 | $-14.20 | $-30.13 to $+2.85 | no evidence of edge |
| squeeze_breakout | 53 | $-2.33 | $-2.52 | $-20.79 to $+16.47 | no evidence of edge |
| news_momentum | 30 | $-74.61 | $-80.33 | $-187.07 to $-2.75 | loses beyond the market |
| gap_and_go | 11 | $+89.10 | $-28.85 | $-95.33 to $+45.02 | too few trades |

## Paper trading, by side

| side | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| long | 777 | $-23.10 | $-28.90 | $-39.49 to $-18.70 | loses beyond the market |
| short | 758 | $+12.68 | $-6.76 | $-14.74 to $+1.38 | no evidence of edge |

## Paper trading, by symbol

| symbol | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| COIN | 225 | $-9.38 | $-39.41 | $-63.63 to $-14.51 | loses beyond the market |
| NVDA | 209 | $+1.65 | $-16.93 | $-40.54 to $+2.59 | no evidence of edge |
| TSLA | 194 | $-16.73 | $-22.97 | $-35.33 to $-10.46 | loses beyond the market |
| AMD | 150 | $-16.20 | $-20.93 | $-36.17 to $-6.15 | loses beyond the market |
| MSTR | 143 | $+3.95 | $-30.67 | $-60.59 to $-0.24 | loses beyond the market |
| PLTR | 133 | $-21.04 | $-24.23 | $-41.50 to $-6.03 | loses beyond the market |
| AMZN | 74 | $-23.66 | $-17.04 | $-34.53 to $+0.17 | no evidence of edge |
| CAT | 71 | $-16.35 | $-33.40 | $-48.90 to $-17.88 | loses beyond the market |
| UNH | 69 | $+19.12 | $+16.54 | $-18.38 to $+57.51 | no evidence of edge |
| JPM | 68 | $+6.79 | $-0.07 | $-13.16 to $+13.96 | no evidence of edge |
| LLY | 68 | $+16.21 | $+15.19 | $-1.31 to $+31.98 | no evidence of edge |
| XOM | 66 | $+20.94 | $+22.68 | $+4.94 to $+41.05 | promising (needs more trades) |
| WMT | 65 | $-0.21 | $-0.11 | $-19.08 to $+18.34 | no evidence of edge |

## Backtest (60-day window), by strategy

| strategy | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| rsi2_reversion | 1140 | $-8.03 | $-11.34 | $-12.84 to $-9.85 | loses beyond the market |
| ar_forecast | 703 | $-11.60 | $-13.79 | $-16.91 to $-10.65 | loses beyond the market |
| vwap_pullback | 692 | $-8.95 | $-13.99 | $-19.20 to $-8.95 | loses beyond the market |
| ema_crossover | 644 | $-12.67 | $-15.40 | $-18.80 to $-11.94 | loses beyond the market |
| orb | 495 | $-14.81 | $-21.56 | $-31.69 to $-11.63 | loses beyond the market |
| high_break_trail | 438 | $-19.10 | $-24.52 | $-31.99 to $-17.18 | loses beyond the market |
| squeeze_breakout | 432 | $-13.02 | $-16.16 | $-20.39 to $-11.91 | loses beyond the market |
| news_momentum | 102 | $-17.16 | $-17.31 | $-29.56 to $-5.40 | loses beyond the market |
| gap_and_go | 4 | $+182.83 | $+129.59 | $+10.68 to $+216.96 | too few trades |

## Market-neutral ORB

ORB was the lab's best raw performer. Hedged against SPY, does anything remain?

| book | trades | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|
| ORB, paper | 372 | $-14.66 | $-32.73 to $+3.98 | no evidence of edge |
| ORB, backtest | 495 | $-21.56 | $-31.65 to $-11.08 | loses beyond the market |

## How to read this

- The 95% range is a bootstrap interval of the SPY-adjusted mean. A range that crosses zero means the data can't distinguish the strategy from luck.
- Variants (`_tuned`, `_regime`) are pooled into their base strategy; both were switched off on 2026-10-21 after losing more than the defaults.
- The traded universe widened from 6 high-beta tech/crypto names to 10 across sectors on 2026-10-21; the by-symbol table shows whether that helps.
