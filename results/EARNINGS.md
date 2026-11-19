# Earnings-reaction drift (pre-registered study B)

Generated 2026-11-19 from SEC 8-K item 2.02 filings and Alpaca daily bars. Rules
fixed in advance: [PREREGISTRATION.md](../docs/research/PREREGISTRATION.md), section B.

## Verdict: **FAIL**

mean daily return -3.4 bp, day-resampled 95% range -9.4 bp to +3.0 bp (not entirely above zero); annualised Sharpe -0.36 (needs ≥ 0.5).

Per the pre-registration, a failed idea is archived — not re-run with new settings.

## What was tested

- 53,913 earnings 8-Ks → 28,337 with a day-0 reaction in the top-1000
  universe → 5,801 trades (reaction in the top or bottom decile of the previous
  500 announcements; 2017-02-03 → 2026-11-18).
- Enter at the close of day +1, exit at the close of day +6, in the
  direction of the reaction; hedged with beta × SPY; 5 bp per side plus 1 bp on the hedge.
- Calendar-time portfolio over 2,462 trading days (2,258 with positions).

## Headline numbers

| measure | value |
|---|---|
| mean daily portfolio return (market-adjusted, net) | -3.4 bp |
| 95% range, resampled by day | -9.4 bp to +3.0 bp |
| annualised Sharpe | -0.36 |
| mean per trade (5 sessions) | -0.10% |

## Descriptive only (cannot rescue a failed primary)

By leg:

| leg | trades | mean per trade | win rate | daily mean | 95% range (daily) | Sharpe |
|---|---|---|---|---|---|---|
| long (top decile) | 2,890 | -0.28% | 48% | -0.1 bp | -7.4 bp to +7.3 bp | -0.01 |
| short (bottom decile) | 2,911 | +0.07% | 53% | -4.5 bp | -11.7 bp to +2.9 bp | -0.39 |

By liquidity tercile on day 0:

| liquidity rank | trades | mean per trade | win rate | daily mean | 95% range (daily) | Sharpe |
|---|---|---|---|---|---|---|
| 1–333 | 2,003 | -0.03% | 51% | -2.4 bp | -8.8 bp to +4.2 bp | -0.23 |
| 334–666 | 1,808 | +0.04% | 50% | +1.1 bp | -6.4 bp to +8.7 bp | +0.09 |
| 667–1000 | 1,990 | -0.30% | 50% | -7.5 bp | -14.4 bp to -0.7 bp | -0.68 |

By year (portfolio):

| year | days with positions | daily mean | Sharpe | year total |
|---|---|---|---|---|
| 2017 | 222 | +4.8 bp | +1.04 | +10.97% |
| 2018 | 231 | -13.8 bp | -2.61 | -29.94% |
| 2019 | 234 | +3.2 bp | +0.53 | +7.11% |
| 2020 | 241 | -3.2 bp | -0.28 | -11.46% |
| 2021 | 228 | -7.1 bp | -0.78 | -18.70% |
| 2022 | 238 | +3.7 bp | +0.36 | +6.03% |
| 2023 | 218 | +1.6 bp | +0.20 | +2.00% |
| 2024 | 228 | +8.7 bp | +0.88 | +20.80% |
| 2025 | 226 | -9.5 bp | -0.71 | -25.48% |
| 2026 | 192 | -24.0 bp | -1.90 | -43.94% |

Data check — acceptance times (read as US Eastern): 1% before 09:30, 53% at or
after 16:00, 46% during the session. Most US companies release before the
open or after the close, so a large "during the session" share would mean a time-zone error.

Accepted limitation (stated in advance): SEC's ticker map lists current companies only, so
announcements by since-delisted firms are missing.
