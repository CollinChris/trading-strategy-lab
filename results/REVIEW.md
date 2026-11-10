# Lab review — is anything beating the market?

Generated 2026-11-10 · 1338 settled paper trades over 54 sessions (2026-08-24 → 2026-11-10) · 1338 SPY-adjusted.

**SPY-adjusted** = the trade's P&L plus an opposite, beta-weighted SPY position held for the same minutes, minus that hedge's slippage. It removes the market's intraday drift, which raw P&L can't tell apart from skill (in Sep–Oct 2026 SPY fell intraday on 27 of 43 days, so shorts looked profitable and longs looked broken).

## Decision gate

**Undecided — 41 days to the decision date.** No strategy beats the market yet.

Rule, set 2026-10-21: by **2026-12-21**, a strategy that has at least 100 SPY-adjusted paper trades and a 95% range entirely above zero keeps running. If none does, the study concludes.

## Paper trading, by strategy (variants pooled)

| strategy_base | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| orb | 327 | $+4.80 | $-10.51 | $-28.03 to $+8.31 | no evidence of edge |
| ar_forecast | 237 | $-6.79 | $-20.79 | $-34.20 to $-7.55 | loses beyond the market |
| high_break_trail | 232 | $-8.04 | $-19.39 | $-33.72 to $-4.64 | loses beyond the market |
| vwap_pullback | 219 | $-0.69 | $-13.64 | $-24.34 to $-2.65 | loses beyond the market |
| rsi2_reversion | 166 | $-7.59 | $-17.83 | $-30.23 to $-4.59 | loses beyond the market |
| ema_crossover | 74 | $-9.01 | $-14.50 | $-31.89 to $+4.09 | no evidence of edge |
| squeeze_breakout | 48 | $-6.02 | $-6.04 | $-25.25 to $+13.88 | no evidence of edge |
| news_momentum | 24 | $-29.02 | $-29.88 | $-77.53 to $+15.12 | too few trades |
| gap_and_go | 11 | $+89.10 | $-28.85 | $-95.33 to $+45.02 | too few trades |

## Paper trading, by side

| side | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| long | 709 | $-17.30 | $-24.58 | $-33.42 to $-15.21 | loses beyond the market |
| short | 629 | $+13.16 | $-6.01 | $-14.56 to $+2.71 | no evidence of edge |

## Paper trading, by symbol

| symbol | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| COIN | 207 | $+4.00 | $-26.30 | $-50.20 to $-0.22 | loses beyond the market |
| NVDA | 185 | $+17.29 | $+1.79 | $-7.56 to $+10.83 | no evidence of edge |
| TSLA | 173 | $-18.32 | $-25.35 | $-37.99 to $-13.36 | loses beyond the market |
| AMD | 150 | $-16.20 | $-20.93 | $-36.17 to $-6.15 | loses beyond the market |
| MSTR | 143 | $+3.95 | $-30.67 | $-60.59 to $-0.24 | loses beyond the market |
| PLTR | 133 | $-21.04 | $-24.23 | $-41.50 to $-6.03 | loses beyond the market |
| AMZN | 52 | $-30.01 | $-19.14 | $-40.59 to $+3.64 | no evidence of edge |
| UNH | 52 | $+5.73 | $-1.11 | $-29.09 to $+29.15 | no evidence of edge |
| CAT | 50 | $-18.26 | $-32.52 | $-48.79 to $-15.58 | loses beyond the market |
| XOM | 50 | $+11.86 | $+14.11 | $-8.02 to $+36.29 | no evidence of edge |
| JPM | 48 | $+4.31 | $-3.50 | $-19.98 to $+13.73 | no evidence of edge |
| WMT | 48 | $+12.71 | $+12.76 | $-8.65 to $+34.87 | no evidence of edge |
| LLY | 47 | $+12.40 | $+12.05 | $-8.51 to $+33.46 | no evidence of edge |

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
| ORB, paper | 327 | $-10.51 | $-28.78 to $+7.97 | no evidence of edge |
| ORB, backtest | 500 | $-21.87 | $-31.70 to $-11.94 | loses beyond the market |

## How to read this

- The 95% range is a bootstrap interval of the SPY-adjusted mean. A range that crosses zero means the data can't distinguish the strategy from luck.
- Variants (`_tuned`, `_regime`) are pooled into their base strategy; both were switched off on 2026-10-21 after losing more than the defaults.
- The traded universe widened from 6 high-beta tech/crypto names to 10 across sectors on 2026-10-21; the by-symbol table shows whether that helps.
