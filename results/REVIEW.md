# Lab review — is anything beating the market?

Generated 2026-11-17 · 1504 settled paper trades over 59 sessions (2026-08-24 → 2026-11-17) · 1504 SPY-adjusted.

**SPY-adjusted** = the trade's P&L plus an opposite, beta-weighted SPY position held for the same minutes, minus that hedge's slippage. It removes the market's intraday drift, which raw P&L can't tell apart from skill (in Sep–Oct 2026 SPY fell intraday on 27 of 43 days, so shorts looked profitable and longs looked broken).

## Decision gate

**Undecided — 34 days to the decision date.** No strategy beats the market yet.

Rule, set 2026-10-21: by **2026-12-21**, a strategy that has at least 100 SPY-adjusted paper trades and a 95% range entirely above zero keeps running. If none does, the study concludes.

## Paper trading, by strategy (variants pooled)

| strategy_base | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| orb | 364 | $-2.47 | $-17.94 | $-36.71 to $-0.10 | loses beyond the market |
| high_break_trail | 262 | $-15.25 | $-24.99 | $-41.74 to $-9.66 | loses beyond the market |
| ar_forecast | 258 | $-7.48 | $-21.08 | $-33.38 to $-8.68 | loses beyond the market |
| vwap_pullback | 256 | $-1.12 | $-15.56 | $-26.16 to $-4.77 | loses beyond the market |
| rsi2_reversion | 189 | $-7.95 | $-17.73 | $-29.96 to $-5.19 | loses beyond the market |
| ema_crossover | 82 | $-6.05 | $-14.20 | $-30.13 to $+2.85 | no evidence of edge |
| squeeze_breakout | 53 | $-2.33 | $-2.52 | $-20.79 to $+16.47 | no evidence of edge |
| news_momentum | 29 | $-79.18 | $-85.06 | $-194.08 to $-4.14 | too few trades |
| gap_and_go | 11 | $+89.10 | $-28.85 | $-95.33 to $+45.02 | too few trades |

## Paper trading, by side

| side | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| long | 769 | $-23.16 | $-29.11 | $-40.10 to $-18.70 | loses beyond the market |
| short | 735 | $+9.87 | $-10.27 | $-17.97 to $-2.62 | loses beyond the market |

## Paper trading, by symbol

| symbol | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| COIN | 222 | $-7.77 | $-38.98 | $-62.74 to $-12.98 | loses beyond the market |
| NVDA | 206 | $-0.06 | $-18.72 | $-43.72 to $+1.18 | no evidence of edge |
| TSLA | 192 | $-16.76 | $-22.85 | $-35.14 to $-10.66 | loses beyond the market |
| AMD | 150 | $-16.20 | $-20.93 | $-36.17 to $-6.15 | loses beyond the market |
| MSTR | 143 | $+3.95 | $-30.67 | $-60.59 to $-0.24 | loses beyond the market |
| PLTR | 133 | $-21.04 | $-24.23 | $-41.50 to $-6.03 | loses beyond the market |
| AMZN | 70 | $-28.43 | $-21.03 | $-39.16 to $-2.81 | loses beyond the market |
| CAT | 68 | $-12.46 | $-30.95 | $-46.58 to $-15.00 | loses beyond the market |
| LLY | 65 | $+13.22 | $+12.22 | $-4.96 to $+29.87 | no evidence of edge |
| UNH | 65 | $-9.26 | $-12.07 | $-35.58 to $+12.47 | no evidence of edge |
| JPM | 64 | $+5.95 | $-1.85 | $-15.07 to $+11.97 | no evidence of edge |
| WMT | 63 | $+0.99 | $+1.10 | $-19.34 to $+20.73 | no evidence of edge |
| XOM | 63 | $+19.17 | $+21.05 | $+1.86 to $+40.35 | promising (needs more trades) |

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
| ORB, paper | 364 | $-17.94 | $-36.46 to $-0.15 | loses beyond the market |
| ORB, backtest | 495 | $-21.56 | $-31.65 to $-11.08 | loses beyond the market |

## How to read this

- The 95% range is a bootstrap interval of the SPY-adjusted mean. A range that crosses zero means the data can't distinguish the strategy from luck.
- Variants (`_tuned`, `_regime`) are pooled into their base strategy; both were switched off on 2026-10-21 after losing more than the defaults.
- The traded universe widened from 6 high-beta tech/crypto names to 10 across sectors on 2026-10-21; the by-symbol table shows whether that helps.
