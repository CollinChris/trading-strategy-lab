# Ten-year history — does anything beat the market?

Generated 2026-11-18 · **2016-01-04 → 2026-11-17** · 10 symbols
(NVDA, TSLA, COIN, AMZN, JPM, XOM, UNH, WMT, CAT, LLY) · Alpaca 5-minute bars, consolidated feed, split/dividend-adjusted ·
196,462 default-parameter trades over 2,735 trading days. Same engine,
costs and SPY adjustment as the live lab (`results/REVIEW.md`).

**No strategy beats the market over 11 years.** Once SPY's intraday move is removed, none of these rules has an edge after costs on these symbols.

## Every strategy at its default parameters

| strategy | trades | trading days | raw $/trade | SPY-adjusted $/trade | 95% range (day-resampled) | verdict |
|---|---|---|---|---|---|---|
| RSI(2) Reversion | 48863 | 2735 | $-8.70 | $-12.18 | $-12.42 to $-11.95 | loses beyond the market |
| VWAP Pullback | 32147 | 2735 | $-7.65 | $-13.31 | $-14.11 to $-12.50 | loses beyond the market |
| AR Forecast | 26827 | 2721 | $-10.42 | $-14.29 | $-14.87 to $-13.73 | loses beyond the market |
| EMA 9/20 Crossover | 26827 | 2734 | $-8.40 | $-13.29 | $-13.99 to $-12.59 | loses beyond the market |
| Opening Range Breakout | 22799 | 2735 | $-7.73 | $-13.01 | $-14.78 to $-11.33 | loses beyond the market |
| High-Break ATR Trail | 20903 | 2735 | $-9.00 | $-17.38 | $-18.54 to $-16.20 | loses beyond the market |
| Squeeze Breakout | 17852 | 2734 | $-9.20 | $-14.58 | $-15.32 to $-13.79 | loses beyond the market |
| Gap & Go | 244 | 220 | $+7.90 | $-3.54 | $-34.76 to $+29.50 | no evidence of edge |

The 95% range resamples **whole trading days**, not individual trades — trades on the same day
share one market, so per-trade resampling would overstate the precision.

## Year by year (SPY-adjusted $/trade, default parameters)

| strategy | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| AR Forecast | -12.3 | -13.2 | -14.0 | -13.0 | -15.7 | -14.4 | -16.2 | -14.6 | -13.5 | -15.2 | -12.7 |
| EMA 9/20 Crossover | -12.6 | -12.2 | -11.2 | -13.2 | -13.7 | -12.1 | -17.9 | -11.6 | -13.3 | -12.6 | -15.4 |
| Gap & Go | +10.4 | +53.5 | -15.9 | -24.0 | -36.6 | +51.0 | +15.7 | -63.4 | +11.0 | +43.0 | -23.6 |
| High-Break ATR Trail | -17.4 | -11.5 | -17.0 | -13.9 | -18.1 | -15.2 | -23.2 | -16.9 | -16.3 | -21.2 | -19.5 |
| Opening Range Breakout | -15.9 | -7.7 | -12.5 | -11.5 | -9.5 | -11.1 | -16.1 | -15.4 | -11.0 | -19.8 | -11.6 |
| RSI(2) Reversion | -12.1 | -11.2 | -11.7 | -11.1 | -12.6 | -11.0 | -13.6 | -12.5 | -12.2 | -13.1 | -12.7 |
| Squeeze Breakout | -14.0 | -12.5 | -12.9 | -12.9 | -15.8 | -14.2 | -20.5 | -12.8 | -11.8 | -14.8 | -17.5 |
| VWAP Pullback | -14.5 | -11.7 | -12.5 | -14.5 | -10.5 | -11.5 | -20.0 | -14.7 | -9.2 | -13.9 | -12.6 |

Years with a positive SPY-adjusted mean, per strategy: AR Forecast 0/11, EMA 9/20 Crossover 0/11, Gap & Go 6/11, High-Break ATR Trail 0/11, Opening Range Breakout 0/11, RSI(2) Reversion 0/11, Squeeze Breakout 0/11, VWAP Pullback 0/11.
A strategy that works only in some kinds of market shows up here as a run of positive years.

## Long and short separately

| strategy | side | trades | SPY-adjusted $/trade | 95% range | verdict |
|---|---|---|---|---|---|
| AR Forecast | long | 13485 | $-14.34 | $-15.11 to $-13.52 | loses beyond the market |
| AR Forecast | short | 13342 | $-14.24 | $-15.06 to $-13.43 | loses beyond the market |
| EMA 9/20 Crossover | long | 13622 | $-13.74 | $-14.75 to $-12.76 | loses beyond the market |
| EMA 9/20 Crossover | short | 13205 | $-12.82 | $-13.72 to $-11.85 | loses beyond the market |
| Gap & Go | long | 131 | $+12.20 | $-29.47 to $+54.82 | no evidence of edge |
| Gap & Go | short | 113 | $-21.78 | $-66.65 to $+26.29 | no evidence of edge |
| High-Break ATR Trail | long | 10637 | $-17.03 | $-18.54 to $-15.46 | loses beyond the market |
| High-Break ATR Trail | short | 10266 | $-17.74 | $-19.32 to $-16.15 | loses beyond the market |
| Opening Range Breakout | long | 11436 | $-13.72 | $-15.96 to $-11.37 | loses beyond the market |
| Opening Range Breakout | short | 11363 | $-12.28 | $-14.58 to $-9.98 | loses beyond the market |
| RSI(2) Reversion | long | 24905 | $-12.09 | $-12.42 to $-11.75 | loses beyond the market |
| RSI(2) Reversion | short | 23958 | $-12.27 | $-12.64 to $-11.92 | loses beyond the market |
| Squeeze Breakout | long | 8972 | $-14.63 | $-15.72 to $-13.58 | loses beyond the market |
| Squeeze Breakout | short | 8880 | $-14.53 | $-15.63 to $-13.38 | loses beyond the market |
| VWAP Pullback | long | 16099 | $-13.71 | $-14.81 to $-12.65 | loses beyond the market |
| VWAP Pullback | short | 16048 | $-12.90 | $-14.03 to $-11.80 | loses beyond the market |

## Walk-forward tuning — does picking parameters on the past help the future?

Each year, every parameter set in the tuning grid is scored on the previous 2 years
(SPY-adjusted, at least 50 trades), the best one is kept, and it is then scored on
the year itself — which it has never seen — next to the untuned defaults.

| strategy | test years | tuned, out of sample | defaults, same years | years tuned beat defaults | distinct parameter picks |
|---|---|---|---|---|---|
| AR Forecast | 9 | $-14.50 | $-14.50 | 0/9 | 1 |
| EMA 9/20 Crossover | 9 | $-12.82 | $-13.48 | 7/9 | 5 |
| Gap & Go | 9 | $-9.26 | $-5.77 | 3/9 | 5 |
| High-Break ATR Trail | 9 | $-15.54 | $-17.99 | 9/9 | 3 |
| Opening Range Breakout | 9 | $-12.94 | $-13.26 | 6/9 | 3 |
| RSI(2) Reversion | 9 | $-11.34 | $-12.28 | 9/9 | 5 |
| Squeeze Breakout | 9 | $-14.25 | $-14.86 | 8/9 | 2 |
| VWAP Pullback | 9 | $-12.37 | $-13.34 | 8/9 | 5 |

"Distinct parameter picks" counts how often the winner changed. A tuned set that keeps changing
and doesn't beat the defaults is fitting noise.

## Notes

- News Momentum: excluded — needs a 10-year headline archive the lab doesn't have.
- AR Forecast: defaults only, no walk-forward tuning (compute; `--full-grid` adds it).
- The ten symbols were chosen in 2026 — survivors with hindsight. Losses here are, if anything,
  understated; apparent edges deserve suspicion.
- COIN listed in April 2021; its history starts there.
- Raw per-trade results: `data/history/trades.pkl` (gitignored, regenerable).
