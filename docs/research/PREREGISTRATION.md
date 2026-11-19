# Pre-registration — three slower strategies (2026-11-19)

Written and committed **before** any of these strategies has been run on any data. The git
commit that adds this file is its timestamp. Ideas come from the two research reports in this
folder (`2026-11-strategy-research.md`, `2026-11-strategy-research-v2.md`); the specifications
below fix every free choice now, so the lab cannot tune its way to a result.

## Rules common to all three

- **No tuning.** Every parameter below is fixed. Because nothing is fitted to the data, the whole
  sample is out-of-sample with respect to this specification; there is no train/test split to
  game. The source papers' samples end before 2016 (Insiders, Earnings) or are a different
  method on a different universe (News — Lopez-Lira & Tang score with an LLM; this uses FinBERT).
- **One primary test per idea decides.** Variants listed as *descriptive* are reported for
  understanding only and can never replace a failed primary.
- **Fail means archive.** A failed idea is recorded in the README and not re-run with new
  settings (the lab's v0.2 lesson: re-tuning after a failure fits noise).
- **Pass means paper-trade, not money.** A passing idea moves to paper trading in a separate
  Alpaca paper account, judged on tracking its backtest, not on its own short live record.

**Prices.** Alpaca daily bars (consolidated SIP feed, split- and dividend-adjusted), from 2016-01-01
(earlier sessions used only to warm up the filters below) to the last completed session before
the run.

**Universe (point-in-time).** On each date, a stock is eligible if its previous unadjusted close
is at least $5, it has at least 250 earlier sessions of bars, and its rank by median daily dollar
volume (unadjusted close × volume) over the 60 sessions *before* that date is within the idea's
cut-off: top 1,000 for Insiders and Earnings, top 500 for News. Ranking is among every symbol
Alpaca lists on a major US exchange (active or delisted) for which bars exist, ETFs included.
(Unadjusted, because split-adjusted history would wrongly put e.g. NVDA's 2016 price under $5.)

**Costs.** 5 basis points per side on the stock (the lab's standard), plus 1 basis point per side
on the hedge, scaled by beta.

**Market adjustment.** Every position carries an opposite SPY position of beta × its notional.
Beta is the slope of the stock's daily close-to-close returns on SPY's over the 250 sessions
before entry (at least 120 required, else 1.0), clipped to [0, 3]. The hedge is measured over
exactly the same window and price points as the position.

**Portfolio and statistics.** Calendar-time, equal-weight across all positions open on a day; the
portfolio's daily return is the mean market-adjusted net return of those positions (0 on days with
none). Annualised Sharpe/IR = mean ÷ standard deviation × √252 over every trading day in the
sample. 95% ranges are bootstrap intervals with 4,000 resamples (seed 0) — by trading day for the
daily strategies, by calendar month for Insiders. A position's entry costs are booked on its first
day of exposure and its exit costs on its last. If a stock's bars stop mid-hold (delisting,
merger), the position exits at its last available close.

## A. Insider cluster purchases

- **Data:** SEC Insider Transactions Data Sets (Forms 3/4/5), 2016 Q1 → latest quarter published.
- **Qualifying trade:** an original Form 4 (amendments excluded) reporting a non-derivative
  purchase (transaction code P — "open market or private purchase" — acquired) at a positive
  price, by a reporting owner whose relationship includes Director or Officer. Excluded when the
  filing's Rule 10b5-1 flag (`AFF10B5ONE`) is set; SEC added that field to the 2023+ data sets, so
  earlier purchases cannot be screened — accepted limitation.
- **Ticker:** the issuer's CIK mapped to its current ticker (SEC `company_tickers.json`, matching
  how Alpaca keys history), falling back to the symbol reported on the filing.
- **Event:** for an issuer, the first filing date on which at least 2 distinct qualifying insiders
  have transaction dates within 7 calendar days of each other. At most one event per issuer per 60
  calendar days.
- **Trade:** long; enter at the open of the first session after the filing date; exit at the close
  of the 40th session (the entry session counts as the first). Universe filter applied as of the
  entry date (top 1,000).
- **PASS** if both: the mean monthly portfolio return is above zero with its month-resampled 95%
  range entirely above zero, and the annualised IR is at least 0.45.
- *Descriptive:* per-event mean market-adjusted return; by year; by liquidity tercile; clusters of
  3 or more insiders.

## B. Earnings-reaction drift

- **Data:** SEC EDGAR submissions; 8-K filings whose items include 2.02 (Results of Operations and
  Financial Condition). Announcement time = the filing's acceptance timestamp (US Eastern).
- **Day 0:** the announcement session if accepted before 09:30 ET on a trading day, otherwise the
  next session. One event per company per day 0 (the first filing).
- **Reaction:** day-0 close-to-close return minus beta × SPY's, beta as of the session before.
- **Signal:** the universe filter (top 1,000 as of day 0) is applied first. Each event's percentile
  is the share of the previous 500 eligible events' reactions (events with an earlier day 0) that
  are below its own; the first 200 events only build history. Long if the percentile is at least
  0.9; short if at most 0.1.
- **Trade:** enter at the close of day +1; exit at the close of day +6.
- **PASS** if both: the mean daily portfolio return's day-resampled 95% range is entirely above
  zero, and the annualised net Sharpe is at least 0.5.
- *Descriptive:* long and short legs separately; by liquidity tercile; by year.
- *Accepted limitation:* SEC's ticker map lists current companies only, so delisted firms'
  announcements are missing (survivorship).

## C. News sentiment (daily)

- **Historical data:** FNSPID (Benzinga headlines; Dong et al. 2024; CC BY-NC 4.0, used here
  non-commercially and never redistributed), 2016-01-01 → the dataset's last date.
- **Forward data:** Alpaca's news API (also Benzinga) from 2026-04-29, archived daily from now on.
  Reported as a confirmatory sample; with months rather than years of data it is descriptive.
- **Headline filter:** drop titles under 4 words, and drop a title that appears tagged to 3 or more
  symbols on the same day (market round-ups). FNSPID timestamps are read as UTC; rows stamped
  exactly midnight are treated as date-only and dropped (their time can't be placed in a window).
  The report shows the headlines' hour-of-day profile in Eastern time as a check on both.
- **Score:** FinBERT (`ProsusAI/finbert`), P(positive) − P(negative), on the headline text.
  A stock's sentiment for a session = the mean score of its headlines published from 16:00 ET on the
  previous session to 09:25 ET on the session.
- **Trade:** among universe stocks (top 500) with at least one such headline, if there are n ≥ 10:
  long the k = ⌊n/5⌋ highest by sentiment, short the k lowest (ties broken by symbol); enter at the
  open, exit at the close of the same session.
- **PASS** if both, on the historical sample: the mean daily portfolio return's day-resampled 95%
  range is entirely above zero, and the annualised net Sharpe is at least 0.5.
- *Descriptive:* Loughran–McDonald dictionary scorer (positive − negative word count over word
  count) with the same rule; an overnight-hold variant (headlines from 15:50 ET on the previous
  session to 15:50 ET on the session, enter at that session's close, exit at the next session's
  close); long and short legs; by year; the Alpaca-era forward sample (archived as derived scores
  only — no headline text is stored).

## Power, stated in advance

With about 8–10 years of daily data, a true annualised Sharpe of roughly 0.65–0.75 is the smallest
that reaches t ≥ 2; the pass rules sit at or below that, so a pass requires a real effect, not
luck at the threshold. A realistic post-publication edge may be smaller than what this design can
detect; in that case the honest result is "not shown", not "keep looking".
