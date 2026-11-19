# News sentiment (pre-registered study C)

Generated 2026-11-19 from FNSPID's Benzinga headlines (Dong et al. 2024, CC BY-NC 4.0)
and Alpaca daily bars. Rules fixed in advance:
[PREREGISTRATION.md](../docs/research/PREREGISTRATION.md), section C as changed by
Amendment 1 (FNSPID's timestamps — see the data check below).

## Verdict: **FAIL**

mean daily return -9.2 bp, day-resampled 95% range -11.7 bp to -6.5 bp (not entirely above zero); annualised Sharpe -3.73 (needs ≥ 0.5).

Per the pre-registration, a failed idea is archived — not re-run with new settings.

## What was tested

- 13,057,514 FNSPID rows → 708,133 Benzinga rows from 2016 →
  151,862 headline-stock pairs after filters (141,492 unique
  headlines scored by FinBERT, 770 stocks, 2015-12-31 → 2020-06-11).
  Dropped: 326,397 round-up rows (same title on 3+ symbols that day),
  titles under 4 words, stocks outside the top-500 liquidity universe.
- Each session: mean FinBERT score of a stock's headlines dated since the previous session
  (Friday–Sunday for a Monday); with ≥ 10 stocks, long the top fifth and short the
  bottom fifth, open → close, each hedged with beta × SPY; 5 bp per side plus 1 bp on the hedge.
- 19,218 trades over 869 trading days
  (2016-12-29 → 2020-06-12).

## Headline numbers (primary)

| measure | value |
|---|---|
| mean daily portfolio return (market-adjusted, net) | -9.2 bp |
| 95% range, resampled by day | -11.7 bp to -6.5 bp |
| annualised Sharpe | -3.73 |
| mean per trade | -8.9 bp |

## Descriptive only (cannot rescue a failed primary)

All variants:

| variant | trades | days | daily mean | 95% range | Sharpe |
|---|---|---|---|---|---|
| FinBERT, headlines dated D → next session open → close (primary) | 19,218 | 869 | -9.2 bp | -11.7 bp to -6.5 bp | -3.73 |
| Loughran–McDonald, same rule | 19,218 | 869 | -10.7 bp | -13.3 bp to -8.1 bp | -4.38 |
| FinBERT, 16:00 → 09:25 ET window, timed rows only (+8 h) | 185 | 30 | +9.8 bp | -15.6 bp to +35.5 bp | +2.18 |
| Alpaca era (2026-04-29 on), FinBERT, date rule | 6,948 | 83 | -18.8 bp | -25.4 bp to -11.9 bp | -9.44 |
| Alpaca era, FinBERT, 16:00 → 09:25 ET window | 5,064 | 84 | -12.6 bp | -20.2 bp to -5.0 bp | -5.55 |

Primary, by leg:

| leg | trades | mean per trade | win rate | daily mean | 95% range (daily) | Sharpe |
|---|---|---|---|---|---|---|
| long (most positive) | 9,609 | -0.11% | 46% | -11.0 bp | -14.3 bp to -7.6 bp | -3.43 |
| short (most negative) | 9,609 | -0.07% | 46% | -7.4 bp | -11.5 bp to -2.9 bp | -1.82 |

Primary, by year:

| year | days with positions | daily mean | Sharpe | year total |
|---|---|---|---|---|
| 2016 | 2 | -39.9 bp | -14.68 | -0.80% |
| 2017 | 251 | -10.4 bp | -5.30 | -23.00% |
| 2018 | 251 | -8.2 bp | -3.66 | -18.78% |
| 2019 | 252 | -8.0 bp | -3.89 | -18.32% |
| 2020 | 113 | -10.7 bp | -2.56 | -11.61% |

## Data check — FNSPID timestamps

Only 2.3% of the kept rows carry a time of day; the rest are date-only,
which is why the primary rule trades the session after a headline's date. For timed rows,
the stamps labelled UTC run 8 hours behind UTC; Benzinga's fixed-schedule headlines should
land at their usual times once 8 hours are added:

| headline type | timed rows | usual time (ET) | median after +8 h (ET) |
|---|---|---|---|
| "Pre-Market Session" | 1,346 | 8.0h | 7.6h |
| "Mid-Day Market Update" | 396 | 12.0h | 12.2h |
| "Mid-Day Session" | 1,190 | 12.5h | 12.5h |
| "52-Week Highs On" | 2,309 | 10.5h | 10.6h |
| "Mid-Afternoon Market Update" | 454 | 14.5h | 14.6h |
| "After-Hours Session" | 59 | 17.0h | 17.3h |

Timed rows by hour of publication (ET, after the shift; hours with ≥ 1%):
05h 3% · 06h 6% · 07h 12% · 08h 18% · 09h 15% · 10h 10% · 11h 8% · 12h 6% · 13h 5% · 14h 4% · 15h 3% · 16h 7% · 17h 2%.
