# Lab review — is anything beating the market?

Generated 2026-10-21 · 832 settled paper trades over 40 sessions (2026-08-24 → 2026-10-21) · 832 SPY-adjusted.

**SPY-adjusted** = the trade's P&L plus an opposite, beta-weighted SPY position held for the same minutes, minus that hedge's slippage. It removes the market's intraday drift, which raw P&L can't tell apart from skill (in Sep–Oct 2026 SPY fell intraday on 27 of 43 days, so shorts looked profitable and longs looked broken).

## Decision gate

**Undecided — 61 days to the decision date.** No strategy beats the market yet.

Rule, set 2026-10-21: by **2026-12-21**, a strategy that has at least 100 SPY-adjusted paper trades and a 95% range entirely above zero keeps running. If none does, the study concludes.

## Paper trading, by strategy (variants pooled)

| strategy_base | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| orb | 206 | $+10.64 | $-3.36 | $-29.38 to $+23.41 | no evidence of edge |
| ar_forecast | 167 | $-1.98 | $-18.57 | $-34.44 to $-2.33 | loses beyond the market |
| high_break_trail | 133 | $-9.16 | $-20.79 | $-41.15 to $+0.41 | no evidence of edge |
| vwap_pullback | 130 | $-4.01 | $-18.76 | $-32.72 to $-3.97 | loses beyond the market |
| rsi2_reversion | 101 | $-15.89 | $-26.65 | $-44.46 to $-8.10 | loses beyond the market |
| ema_crossover | 50 | $-12.03 | $-18.85 | $-41.46 to $+4.97 | no evidence of edge |
| squeeze_breakout | 28 | $-7.83 | $-8.92 | $-39.37 to $+23.30 | too few trades |
| news_momentum | 13 | $-50.86 | $-69.62 | $-138.20 to $-5.43 | too few trades |
| gap_and_go | 4 | $+235.91 | $+69.82 | $-56.05 to $+187.00 | too few trades |

## Paper trading, by side

| side | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| long | 442 | $-15.87 | $-28.70 | $-42.38 to $-15.14 | loses beyond the market |
| short | 390 | $+12.80 | $-2.11 | $-13.17 to $+9.60 | no evidence of edge |

## Paper trading, by symbol

| symbol | trades | raw $/trade | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| AMD | 150 | $-16.20 | $-20.93 | $-35.24 to $-6.15 | loses beyond the market |
| COIN | 148 | $+30.05 | $+2.06 | $-27.94 to $+33.78 | no evidence of edge |
| MSTR | 143 | $+3.95 | $-30.67 | $-61.34 to $+1.09 | no evidence of edge |
| PLTR | 133 | $-21.04 | $-24.23 | $-40.86 to $-6.53 | loses beyond the market |
| NVDA | 128 | $+8.65 | $+2.76 | $-6.41 to $+11.69 | no evidence of edge |
| TSLA | 122 | $-18.84 | $-24.27 | $-39.19 to $-9.44 | loses beyond the market |
| AMZN | 3 | $-73.32 | $-51.12 | $-77.47 to $-33.85 | too few trades |
| CAT | 2 | $-117.00 | $-87.92 | $-114.45 to $-61.39 | too few trades |
| XOM | 2 | $-51.89 | $-47.01 | $-59.46 to $-34.56 | too few trades |
| LLY | 1 | $-58.73 | $-33.89 | — | no trades |

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
| ORB, paper | 206 | $-3.36 | $-29.91 to $+23.55 | no evidence of edge |
| ORB, backtest | 503 | $-15.57 | $-25.64 to $-4.89 | loses beyond the market |

## How to read this

- The 95% range is a bootstrap interval of the SPY-adjusted mean. A range that crosses zero means the data can't distinguish the strategy from luck.
- Variants (`_tuned`, `_regime`) are pooled into their base strategy; both were switched off on 2026-10-21 after losing more than the defaults.
- The traded universe widened from 6 high-beta tech/crypto names to 10 across sectors on 2026-10-21; the by-symbol table shows whether that helps.
