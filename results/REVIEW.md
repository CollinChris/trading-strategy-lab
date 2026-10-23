# Lab review — is anything beating the market?

Generated 2026-10-23 · 888 settled paper trades over 42 sessions (2026-08-24 → 2026-10-23) · 888 SPY-adjusted.

**SPY-adjusted** = the trade's P&L plus an opposite, beta-weighted SPY position held for the same minutes, minus that hedge's slippage. It removes the market's intraday drift, which raw P&L can't tell apart from skill (in Sep–Oct 2026 SPY fell intraday on 27 of 43 days, so shorts looked profitable and longs looked broken).

## Decision gate

**Undecided — 59 days to the decision date.** No strategy beats the market yet.

Rule, set 2026-10-21: by **2026-12-21**, a strategy that has at least 100 SPY-adjusted paper trades and a 95% range entirely above zero keeps running. If none does, the study concludes.

## Paper trading, by strategy (variants pooled)

| strategy_base | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| orb | 222 | $+9.08 | $-2.77 | $-26.64 to $+22.63 | no evidence of edge |
| ar_forecast | 174 | $-1.05 | $-17.65 | $-33.03 to $-1.28 | loses beyond the market |
| high_break_trail | 145 | $-8.59 | $-20.15 | $-39.82 to $+0.26 | no evidence of edge |
| vwap_pullback | 139 | $-0.84 | $-15.45 | $-29.61 to $-1.49 | loses beyond the market |
| rsi2_reversion | 107 | $-18.00 | $-27.43 | $-43.97 to $-10.23 | loses beyond the market |
| ema_crossover | 51 | $-11.56 | $-18.07 | $-39.73 to $+6.16 | no evidence of edge |
| squeeze_breakout | 30 | $-6.85 | $-8.00 | $-37.32 to $+21.66 | no evidence of edge |
| news_momentum | 15 | $-57.60 | $-67.02 | $-126.32 to $-11.29 | too few trades |
| gap_and_go | 5 | $+179.80 | $+40.77 | $-59.93 to $+137.86 | too few trades |

## Paper trading, by side

| side | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| long | 473 | $-16.44 | $-27.68 | $-40.10 to $-14.79 | loses beyond the market |
| short | 415 | $+13.40 | $-1.36 | $-12.31 to $+9.63 | no evidence of edge |

## Paper trading, by symbol

| symbol | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| COIN | 156 | $+26.16 | $-0.59 | $-30.07 to $+28.82 | no evidence of edge |
| AMD | 150 | $-16.20 | $-20.93 | $-35.52 to $-5.40 | loses beyond the market |
| MSTR | 143 | $+3.95 | $-30.67 | $-61.34 to $+1.09 | no evidence of edge |
| NVDA | 133 | $+11.54 | $+4.88 | $-3.97 to $+13.76 | no evidence of edge |
| PLTR | 133 | $-21.04 | $-24.23 | $-41.42 to $-6.20 | loses beyond the market |
| TSLA | 127 | $-21.39 | $-25.59 | $-40.03 to $-11.04 | loses beyond the market |
| AMZN | 9 | $+0.32 | $+1.86 | $-36.51 to $+44.36 | too few trades |
| XOM | 8 | $-33.59 | $-29.84 | $-64.12 to $+3.97 | too few trades |
| CAT | 7 | $-32.12 | $-40.28 | $-91.43 to $+19.69 | too few trades |
| JPM | 6 | $-10.36 | $+11.80 | $+0.65 to $+22.45 | too few trades |
| WMT | 6 | $+27.98 | $+27.95 | $-23.18 to $+76.33 | too few trades |
| LLY | 5 | $-17.96 | $-6.93 | $-39.05 to $+35.16 | too few trades |
| UNH | 5 | $+4.06 | $+16.98 | $-4.89 to $+46.57 | too few trades |

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
| ORB, paper | 222 | $-2.77 | $-27.01 to $+22.13 | no evidence of edge |
| ORB, backtest | 503 | $-15.57 | $-25.64 to $-4.89 | loses beyond the market |

## How to read this

- The 95% range is a bootstrap interval of the SPY-adjusted mean. A range that crosses zero means the data can't distinguish the strategy from luck.
- Variants (`_tuned`, `_regime`) are pooled into their base strategy; both were switched off on 2026-10-21 after losing more than the defaults.
- The traded universe widened from 6 high-beta tech/crypto names to 10 across sectors on 2026-10-21; the by-symbol table shows whether that helps.
