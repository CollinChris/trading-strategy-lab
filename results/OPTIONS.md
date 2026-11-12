# Option-selling strategies — 40 years of Cboe benchmarks

Generated 2026-10-21 · daily index levels from Cboe (free, `data/cboe/`) ·
benchmark S&P 500 total return (`^SP500TR`), risk-free 13-week T-bill (`^IRX`) · monthly returns,
**gross of trading costs** (real implementations pay spreads these indexes don't).

**Statistically clear alphas (|t| ≥ 2): Weekly ATM put-write (WPUT) last 10 years (-5.1%, t=-3.04).** Everything else is indistinguishable from its market exposure.

The premium these strategies harvest is real: VIX sat above SPX's trailing realised volatility
in 87% of month-ends. The question is whether harvesting it beats simply owning
the equivalent amount of stock market — that is what **alpha** measures here.

## Each strategy against its market exposure

| strategy | period | from | months | CAGR | max drawdown | beta | alpha/yr | alpha t-stat | Sharpe |
|---|---|---|---|---|---|---|---|---|---|
| Monthly ATM put-write (PUT) | full history | 2007-02 | 237 | +7.2% | -33% | 0.60 | -0.1% | -0.04 | 0.56 |
| Monthly ATM put-write (PUT) | since 2007 | 2007-02 | 237 | +7.2% | -33% | 0.60 | -0.1% | -0.04 | 0.56 |
| Monthly ATM put-write (PUT) | last 10 years | 2016-10 | 121 | +8.6% | -21% | 0.55 | -0.9% | -0.59 | 0.65 |
| Weekly ATM put-write (WPUT) | full history | 2006-02 | 249 | +4.8% | -24% | 0.53 | -1.8% | -1.51 | 0.36 |
| Weekly ATM put-write (WPUT) | since 2007 | 2007-01 | 238 | +4.4% | -24% | 0.53 | -2.1% | -1.63 | 0.33 |
| Weekly ATM put-write (WPUT) | last 10 years | 2016-10 | 121 | +3.9% | -19% | 0.53 | -5.1% | -3.04 | 0.19 |
| Covered call (ATM, monthly) (BXM) | full history | 2002-04 | 295 | +6.2% | -36% | 0.63 | -0.8% | -0.77 | 0.46 |
| Covered call (ATM, monthly) (BXM) | since 2007 | 2007-01 | 238 | +6.1% | -36% | 0.62 | -1.4% | -1.14 | 0.45 |
| Covered call (ATM, monthly) (BXM) | last 10 years | 2016-10 | 121 | +8.0% | -22% | 0.59 | -1.8% | -1.09 | 0.56 |
| Covered call (30-delta) (BXMD) | full history | 1988-01 | 465 | +11.0% | -43% | 0.80 | +1.0% | +1.56 | 0.67 |
| Covered call (30-delta) (BXMD) | since 2007 | 2007-01 | 238 | +8.5% | -43% | 0.80 | -0.6% | -0.64 | 0.58 |
| Covered call (30-delta) (BXMD) | last 10 years | 2016-10 | 121 | +10.8% | -22% | 0.76 | -1.3% | -1.01 | 0.71 |
| Iron condor (CNDR) | full history | 1988-01 | 465 | +5.7% | -19% | 0.11 | +1.7% | +1.64 | 0.41 |
| Iron condor (CNDR) | since 2007 | 2007-01 | 238 | +1.0% | -19% | 0.10 | -1.3% | -0.85 | -0.05 |
| Iron condor (CNDR) | last 10 years | 2016-10 | 121 | +1.0% | -19% | 0.04 | -1.8% | -0.90 | -0.20 |
| Protective put (5% OTM) (PPUT) | full history | 1988-01 | 465 | +8.0% | -39% | 0.75 | -1.3% | -1.65 | 0.46 |
| Protective put (5% OTM) (PPUT) | since 2007 | 2007-01 | 238 | +8.2% | -39% | 0.70 | -0.1% | -0.06 | 0.58 |
| Protective put (5% OTM) (PPUT) | last 10 years | 2016-10 | 121 | +12.3% | -21% | 0.74 | +0.3% | +0.21 | 0.81 |

For comparison, the S&P 500 itself:

| period | S&P 500 TR CAGR | max drawdown | Sharpe |
|---|---|---|---|
| full history | +11.5% | -51% | 0.62 |
| since 2007 | +11.0% | -51% | 0.66 |
| last 10 years | +15.3% | -24% | 0.85 |

**alpha/yr** = annual return beyond what the strategy's beta to the S&P 500 explains (CAPM on
monthly excess returns); |t| ≥ 2 is the usual bar for "not luck". A strategy with beta 0.6 and
zero alpha is just a cheaper way to own 60% of the market.

## Worst drawdowns in each crisis (peak to trough inside the window)

| episode | PUT | WPUT | BXM | BXMD | CNDR | PPUT | SPXTR |
|---|---|---|---|---|---|---|---|
| 2008 crisis | -37% | -29% | -40% | -47% | -11% | -42% | -55% |
| Feb 2018 'Volmageddon' | -8% | -13% | -8% | -9% | -6% | -9% | -10% |
| 2020 COVID crash | -29% | -25% | -30% | -32% | -11% | -12% | -34% |
| 2022 bear market | -16% | -20% | -18% | -22% | -10% | -22% | -24% |

## Timing test — sell puts only when the premium is rich?

Each month, the put-write is held only if the previous month-end's volatility risk premium
(VIX minus 21-day realised vol) was at or above the median of all earlier months; otherwise the
money sits in T-bills. The threshold uses past data only (5-year warm-up on PUT's daily
history, which starts in 2007), so this is an out-of-sample test from 2012-02.
Invested 46% of months.

| strategy | months | CAGR | max drawdown | beta | alpha/yr | alpha t-stat | Sharpe |
|---|---|---|---|---|---|---|---|
| Put-write, always (PUT) | 177 | +8.3% | -21% | 0.54 | -0.5% | -0.38 | 0.77 |
| Put-write only when VRP ≥ its past median | 177 | +4.9% | -21% | 0.31 | -0.7% | -0.45 | 0.48 |

## What this means for the lab

- Paper trading can check how a live implementation tracks these indexes and what it pays in
  spreads — it cannot establish an edge: a 1–2%/yr alpha needs decades of data to separate from
  luck, which only these index histories have.
- Ranking for a paper replication, if any: the monthly put-write (cleanest, matches `PUT`), then a
  delta-hedged covered call (Israelov & Nielsen 2015, which removes the unrewarded equity-timing
  piece). Avoid weekly put-writing, same-day (0DTE) premium selling, and selling into earnings.
