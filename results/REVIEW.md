# Lab review — is anything beating the market?

Generated 2026-11-11 · 1349 settled paper trades over 55 sessions (2026-08-24 → 2026-11-11) · 1349 SPY-adjusted.

**SPY-adjusted** = the trade's P&L plus an opposite, beta-weighted SPY position held for the same minutes, minus that hedge's slippage. It removes the market's intraday drift, which raw P&L can't tell apart from skill (in Sep–Oct 2026 SPY fell intraday on 27 of 43 days, so shorts looked profitable and longs looked broken).

## Decision gate

**Undecided — 40 days to the decision date.** No strategy beats the market yet.

Rule, set 2026-10-21: by **2026-12-21**, a strategy that has at least 100 SPY-adjusted paper trades and a 95% range entirely above zero keeps running. If none does, the study concludes.

## Paper trading, by strategy (variants pooled)

| strategy_base | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| orb | 328 | $+4.21 | $-10.89 | $-28.95 to $+7.99 | no evidence of edge |
| ar_forecast | 239 | $-7.59 | $-21.32 | $-34.38 to $-8.25 | loses beyond the market |
| high_break_trail | 233 | $-8.50 | $-19.80 | $-34.34 to $-5.22 | loses beyond the market |
| vwap_pullback | 224 | $-2.22 | $-14.92 | $-25.32 to $-4.58 | loses beyond the market |
| rsi2_reversion | 167 | $-8.16 | $-18.34 | $-30.50 to $-5.44 | loses beyond the market |
| ema_crossover | 74 | $-9.01 | $-14.50 | $-31.89 to $+4.09 | no evidence of edge |
| squeeze_breakout | 48 | $-6.02 | $-6.04 | $-25.25 to $+13.88 | no evidence of edge |
| news_momentum | 25 | $-26.79 | $-27.34 | $-70.84 to $+14.31 | too few trades |
| gap_and_go | 11 | $+89.10 | $-28.85 | $-95.33 to $+45.02 | too few trades |

## Paper trading, by side

| side | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| long | 712 | $-17.36 | $-24.65 | $-33.51 to $-15.31 | loses beyond the market |
| short | 637 | $+11.68 | $-7.07 | $-15.20 to $+1.46 | no evidence of edge |

## Paper trading, by symbol

| symbol | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| COIN | 207 | $+4.00 | $-26.30 | $-50.20 to $-0.22 | loses beyond the market |
| NVDA | 186 | $+16.72 | $+1.26 | $-7.75 to $+10.16 | no evidence of edge |
| TSLA | 174 | $-18.58 | $-25.73 | $-38.48 to $-13.31 | loses beyond the market |
| AMD | 150 | $-16.20 | $-20.93 | $-36.17 to $-6.15 | loses beyond the market |
| MSTR | 143 | $+3.95 | $-30.67 | $-60.59 to $-0.24 | loses beyond the market |
| PLTR | 133 | $-21.04 | $-24.23 | $-41.50 to $-6.03 | loses beyond the market |
| UNH | 54 | $+2.21 | $-3.89 | $-30.25 to $+24.20 | no evidence of edge |
| AMZN | 52 | $-30.01 | $-19.14 | $-40.67 to $+3.67 | no evidence of edge |
| CAT | 52 | $-23.03 | $-35.30 | $-52.11 to $-18.30 | loses beyond the market |
| WMT | 50 | $+7.80 | $+7.84 | $-13.95 to $+29.92 | no evidence of edge |
| XOM | 50 | $+11.86 | $+14.11 | $-7.51 to $+36.56 | no evidence of edge |
| JPM | 49 | $+2.89 | $-4.35 | $-19.90 to $+13.06 | no evidence of edge |
| LLY | 49 | $+11.20 | $+10.92 | $-9.56 to $+32.40 | no evidence of edge |

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
| ORB, paper | 328 | $-10.89 | $-29.13 to $+7.58 | no evidence of edge |
| ORB, backtest | 500 | $-21.87 | $-31.70 to $-11.94 | loses beyond the market |

## How to read this

- The 95% range is a bootstrap interval of the SPY-adjusted mean. A range that crosses zero means the data can't distinguish the strategy from luck.
- Variants (`_tuned`, `_regime`) are pooled into their base strategy; both were switched off on 2026-10-21 after losing more than the defaults.
- The traded universe widened from 6 high-beta tech/crypto names to 10 across sectors on 2026-10-21; the by-symbol table shows whether that helps.
