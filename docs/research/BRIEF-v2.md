# Research brief v2 — strategies with a real chance of beating the market

You are doing a thorough, multi-hour literature and feasibility study for a small,
honest paper-trading research lab. **No code changes.** The deliverable is one report.
Take your time: depth and verified sources matter more than speed.

## Delivery — read this first

1. Write the report to `docs/research/2026-11-strategy-research-v2.md`.
2. Commit it on a new branch `research/strategy-ideas-v2` and open a pull request
   against `main` titled **"Research v2: strategies with a real chance of beating the market"**.
3. **Whatever happens with git, end the session by pasting the complete report as your
   final message.** If the push or the pull request failed, say so in the first line of
   that message and include the exact error. (A previous research session finished
   without leaving anything on GitHub; the transcript is the fallback.)

## What the lab has already established (do not re-propose)

Read `README.md`, `results/REVIEW.md`, `results/OPTIONS.md`, `results/HISTORY.md` (if
present), and `src/trading_lab/market.py` first.

- Nine textbook intraday technical rules (opening-range breakout, VWAP pullback, EMA
  crossover, RSI(2), Bollinger squeeze breakout, first-hour-high trail, gap-and-go, a
  headline-timing "news momentum" rule, an autoregressive return forecast) show no edge
  once each trade is scored against an opposite, beta-weighted SPY hedge ("SPY-adjusted").
  Over 1,500 paper trades most lose *beyond* the market, before slippage.
- Weekly parameter tuning fit noise: winning parameters changed most weeks, and even the
  best set lost money on its own training data.
- A machine-learning "regime filter" on entry conditions looked strong in one backtest
  window and failed live.
- Ten-year confirmation (`results/HISTORY.md`, 2016–2026, 196,462 backtest trades): no
  intraday rule beats the market in any of 11 years, long or short. The losses (about
  $12–17 per $10k trade) are roughly the size of the modelled costs (5 bps per side plus
  the hedge), so the entries have about **zero predictive value before costs**. Live paper
  results run about $10 per trade worse than the backtest (execution lag). Implication for
  this research: favour lower-turnover signals (daily/weekly horizons) with an economic
  mechanism, where the edge per trade can plausibly exceed costs.
- Cboe option-selling benchmarks (put-write, covered calls, iron condors, since 1986):
  no statistically significant alpha beyond their market exposure; weekly put-writing has
  significantly *negative* alpha over the last 10 years.

The lab's evidence standard, which every proposal must be testable against: returns
judged net of market exposure; out-of-sample / walk-forward validation; realistic costs;
confidence intervals resampled by trading day (or month for slower strategies); a
decision rule committed to before the data arrives.

## Constraints

- The user is in Singapore. Execution is **Alpaca paper trading** only, US equities/ETFs.
- Free data the lab can use: Alpaca 5-minute and daily bars (consolidated feed, 2016+),
  Alpaca's news API (headlines + summaries, roughly 2015+), SEC EDGAR (filings incl.
  Form 4 insider trades, 8-K, 10-K/Q text), FRED, Cboe index histories, yfinance.
  Assess whether each needed dataset is actually available free and at what depth.
- Compute: GitHub Actions (free, 4-core runners, 6-hour job limit, parallel jobs) —
  not the user's laptop. A small model such as FinBERT on CPU is in scope; say whether
  it is feasible at the needed scale.
- LLM access: a Claude Code subscription only (no API key). Scoring millions of headlines
  with an LLM is not realistic; say what volume would be.
- Your cloud VM may block finance websites; use your web search/fetch tools. If a source
  can't be reached, say so rather than citing from memory.

## Scope — evaluate all of these, plus anything you find with comparable evidence

1. **Sentiment and news:** news-sentiment return predictability (e.g. Tetlock 2007;
   Tetlock, Saar-Tsechansky & Macskassy 2008), LLM headline scoring (Lopez-Lira & Tang
   2023 and replications/critiques), dictionary methods (Loughran & McDonald), social-media
   sentiment, earnings-call tone, analyst forecast revisions, investor attention
   (Google Trends, Wikipedia views, abnormal news volume).
2. **Industry and sector trends:** industry momentum (Moskowitz & Grinblatt 1999), sector
   rotation, time-series momentum / trend following (Moskowitz, Ooi & Pedersen 2012),
   economic links and lead-lag (Cohen & Frazzini 2008), technology-linked firms.
3. **Event-driven:** post-earnings-announcement drift, the earnings-announcement premium,
   insider purchases from Form 4 (e.g. Lakonishok & Lee 2001; Cohen, Malloy & Pomorski
   2012), buyback announcements, index additions/deletions.
4. **Calendar and structural:** overnight vs intraday returns, pre-FOMC drift (Lucca &
   Moench 2015), turn-of-the-month.
5. **Cross-sectional anomalies at retail scale:** short-term reversal, 52-week-high
   momentum, low volatility, and what large replication studies say about decay —
   e.g. McLean & Pontiff (2016), Hou, Xue & Zhang (2020) "Replicating Anomalies",
   Jensen, Kelly & Pedersen (2023), and the free Chen & Zimmermann Open Source Asset
   Pricing dataset (check whether its monthly predictor returns let the lab test
   post-publication performance without building the signals itself).
6. **Statistical arbitrage:** pairs trading (Gatev, Goetzmann & Rouwenhorst 2006) and
   its documented decline.

## Method

For every candidate, record: the mechanism (why anyone would leave this money on the
table), the original evidence (sample, universe, holding period, effect size), the
evidence **after** publication and after costs, whether it works in large caps or only
small/illiquid stocks, and the data the lab would need. Prefer peer-reviewed papers and
large replication studies; label practitioner and vendor claims as such. Fetch and read
the sources you cite; do not cite from memory.

For the shortlist, also estimate **statistical power**: given a realistic edge and its
volatility, how many trades or months of out-of-sample data would the lab need to tell it
from zero? A test that needs 30 years of paper trading is not a test.

## Report structure

1. **Bottom line** (one paragraph): is there a realistic, retail-feasible edge worth
   testing, and which one.
2. **Ranked shortlist of 3–5 ideas.** For each: mechanism; evidence quality (strong /
   medium / weak, with citations); realistic edge after costs and market adjustment;
   data needed and whether it's free; a concrete test specification (signal definition,
   universe, rebalancing or holding period, costs, market adjustment, walk-forward split,
   power estimate, a pre-committed pass/fail rule); main failure mode.
3. **Sentiment and news in depth** — what actually works, at what horizon, and whether
   the lab's free data and compute can reach it.
4. **Promising-sounding but avoid** — with reasons.
5. **Appendix table** of every candidate evaluated: name, horizon, evidence grade,
   post-publication status, data feasibility, verdict.
6. **Sources** — full citations with links.

Length: as long as it needs to be, up to about 6,000 words plus the appendix.

## Before you deliver, check the report against this list

- [ ] Every factual claim about returns cites a source you actually opened.
- [ ] Each shortlisted idea has a power estimate and a pass/fail rule.
- [ ] Nothing re-proposes what the lab has already ruled out.
- [ ] Data availability was checked, not assumed.
- [ ] Vendor or course-seller claims are labelled as such.
- [ ] No code, workflow, or results files were modified.
- [ ] The full report is pasted in your final message.
