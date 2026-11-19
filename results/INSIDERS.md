# Insider cluster purchases (pre-registered study A)

Generated 2026-11-19 from SEC Form 4 data sets and Alpaca daily bars. Rules fixed
in advance: [PREREGISTRATION.md](../docs/research/PREREGISTRATION.md), section A.

## Verdict: **FAIL**

mean monthly return -0.36%, month-resampled 95% range -1.13% to +0.44% (not entirely above zero); annualised IR -0.27 (needs ≥ 0.45).

Per the pre-registration, a failed idea is archived — not re-run with new settings.

## What was tested

- 165,114 qualifying director/officer purchases → 15,804 cluster events
  (11,182 in stocks with Alpaca prices; insider
  buying is mostly a small-cap phenomenon) → 1,002 trades in the top-1000
  liquidity universe at entry
  (453 stocks, 2017-01-04 → 2026-05-27).
- Long at the next open after the filing date, out at the close of the 40th session;
  every trade hedged with beta × SPY; 5 bp per side on the stock and 1 bp on the hedge.
- Calendar-time portfolio: equal weight across open positions, 2,361 trading days
  (2,361 with positions), 113 months.

## Headline numbers

| measure | value |
|---|---|
| mean monthly return (market-adjusted, net) | -0.36% |
| 95% range, resampled by month | -1.13% to +0.44% |
| annualised IR (daily) | -0.27 |
| mean per trade (40 sessions) | -1.63% (95% range -2.46% to -0.80%, trades resampled independently — optimistic) |
| raw stock return per trade, before hedge and costs | +1.71% |

## Descriptive only (cannot rescue a failed primary)

By year (portfolio):

| year | days with positions | daily mean | Sharpe | year total |
|---|---|---|---|---|
| 2017 | 250 | -5.4 bp | -1.11 | -13.26% |
| 2018 | 251 | -5.1 bp | -1.30 | -12.54% |
| 2019 | 252 | -2.8 bp | -0.68 | -7.33% |
| 2020 | 253 | -4.6 bp | -0.43 | -14.08% |
| 2021 | 252 | +1.2 bp | +0.20 | +1.94% |
| 2022 | 251 | +3.9 bp | +0.67 | +9.08% |
| 2023 | 250 | -0.6 bp | -0.09 | -2.63% |
| 2024 | 252 | +0.7 bp | +0.11 | +0.39% |
| 2025 | 250 | +1.0 bp | +0.18 | +1.56% |
| 2026 | 100 | -10.4 bp | -1.58 | -10.39% |

By liquidity tercile at entry:

| liquidity rank | trades | mean per trade | win rate | daily mean | 95% range (daily) | Sharpe |
|---|---|---|---|---|---|---|
| 1–333 | 265 | -1.86% | 42% | -1.0 bp | -6.1 bp to +4.2 bp | -0.12 |
| 334–666 | 375 | -1.32% | 46% | -2.4 bp | -6.9 bp to +2.2 bp | -0.33 |
| 667–1000 | 362 | -1.78% | 46% | -2.0 bp | -7.9 bp to +4.2 bp | -0.21 |

By cluster size:

| cluster | trades | mean per trade | win rate | daily mean | 95% range (daily) | Sharpe |
|---|---|---|---|---|---|---|
| 2 insiders | 718 | -1.95% | 44% | -3.9 bp | -8.6 bp to +1.0 bp | -0.52 |
| 3+ insiders | 284 | -0.81% | 47% | +1.2 bp | -4.2 bp to +6.3 bp | +0.15 |

Accepted limitations (stated in advance): the Rule 10b5-1 flag exists only from 2023;
SEC's ticker map lists current companies, so some delisted issuers can't be priced. Alpaca's
price history starts in January 2016 and the screens need 250 sessions of it, so trades start
in 2017.
