# Earnings-reaction drift (pre-registered study B)

Generated 2026-11-19 from SEC 8-K item 2.02 filings and Alpaca daily bars. Rules
fixed in advance: [PREREGISTRATION.md](../docs/research/PREREGISTRATION.md), section B.

## Verdict: **FAIL**

mean daily return -8.7 bp, day-resampled 95% range -14.5 bp to -3.1 bp (not entirely above zero); annualised Sharpe -0.99 (needs ≥ 0.5).

Per the pre-registration, a failed idea is archived — not re-run with new settings.

## What was tested

- 53,832 earnings 8-Ks → 28,303 with a day-0 reaction in the top-1000
  universe → 5,766 trades (reaction in the top or bottom decile of the previous
  500 announcements; 2017-02-03 → 2026-11-18).
- Enter at the close of day +1, exit at the close of day +6, in the
  direction of the reaction; hedged with beta × SPY; 5 bp per side plus 1 bp on the hedge.
- Calendar-time portfolio over 2,462 trading days (2,302 with positions).

## Headline numbers

| measure | value |
|---|---|
| mean daily portfolio return (market-adjusted, net) | -8.7 bp |
| 95% range, resampled by day | -14.5 bp to -3.1 bp |
| annualised Sharpe | -0.99 |
| mean per trade (5 sessions) | -0.11% |

## Descriptive only (cannot rescue a failed primary)

By leg:

| leg | trades | mean per trade | win rate | daily mean | 95% range (daily) | Sharpe |
|---|---|---|---|---|---|---|
| long (top decile) | 2,887 | -0.37% | 48% | -6.5 bp | -14.1 bp to +1.1 bp | -0.53 |
| short (bottom decile) | 2,879 | +0.14% | 53% | -3.6 bp | -10.6 bp to +3.3 bp | -0.33 |

By liquidity tercile on day 0:

| liquidity rank | trades | mean per trade | win rate | daily mean | 95% range (daily) | Sharpe |
|---|---|---|---|---|---|---|
| 1–333 | 1,805 | -0.12% | 51% | -3.7 bp | -10.9 bp to +3.5 bp | -0.32 |
| 334–666 | 1,880 | +0.03% | 51% | -1.6 bp | -8.5 bp to +5.5 bp | -0.15 |
| 667–1000 | 2,081 | -0.23% | 50% | -10.9 bp | -17.8 bp to -3.8 bp | -0.97 |

By year (portfolio):

| year | days with positions | daily mean | Sharpe | year total |
|---|---|---|---|---|
| 2017 | 222 | +1.6 bp | +0.33 | +3.04% |
| 2018 | 240 | -13.8 bp | -2.40 | -30.04% |
| 2019 | 238 | +6.5 bp | +1.12 | +16.53% |
| 2020 | 245 | -9.0 bp | -0.75 | -23.93% |
| 2021 | 237 | -2.9 bp | -0.26 | -10.54% |
| 2022 | 233 | -12.3 bp | -1.23 | -28.89% |
| 2023 | 231 | -10.3 bp | -1.40 | -23.99% |
| 2024 | 237 | -2.1 bp | -0.28 | -6.83% |
| 2025 | 229 | -20.7 bp | -1.93 | -42.57% |
| 2026 | 190 | -25.6 bp | -2.55 | -44.99% |

Data check — acceptance times (UTC stamps converted to US Eastern): 44% before 09:30,
52% at or after 16:00, 4% during the session. Most US companies release before
the open or after the close; the study refuses to run if more than 20% fall in the session.

Run history: the first run (commit 4393248) read these stamps as Eastern without
converting, which put every pre-market announcement's day 0 one session late; its own data
check showed 46% "during the session". That run is void (it read FAIL, Sharpe −0.36); this
report is the corrected run, rules unchanged. See PREREGISTRATION.md, "Corrections".

Accepted limitation (stated in advance): SEC's ticker map lists current companies only, so
announcements by since-delisted firms are missing.
