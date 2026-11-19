# Research v2 — strategies with a real chance of beating the market

*Prepared 2026-11-18 for the Trading Strategy Lab. Literature and feasibility study only; no code,
workflow, or results files were changed.*

**How sources were read.** This session's cloud container blocks direct outbound fetches
(arxiv.org, ssrn.com, sec.gov, columbia.edu and every other host tested returned
`connect_rejected` from the egress proxy), so every source below was read through the web-search
tool, which retrieves and excerpts pages server-side. Where only an abstract or a secondary
summary was reachable, the citation says so; where a number comes from a practitioner or vendor
source (Alpha Architect, Quantpedia, blogs), it is labelled as such. Nothing is cited from memory
alone.

---

## 1. Bottom line

Yes — but only one family of ideas fits all three of the lab's hard constraints (free data, a
market-adjusted evidence standard, and enough statistical power to reach a verdict within about a
year), and it is **daily-horizon news-sentiment trading built on the Alpaca/Benzinga news archive
(2015→) scored with a small local model (FinBERT + the Loughran–McDonald dictionary)**. It has
peer-reviewed support at exactly the lab's horizon (Tetlock 2007, 2008; Lopez-Lira & Tang 2023),
ten years of free in-house data for a walk-forward backtest with real power (a net Sharpe of
~0.6–0.9 is detectable; anything weaker is honestly untestable and the pre-committed rule below
says to stop), and a cost structure the lab can model exactly because it already measures
SPY-adjusted P&L with slippage. Two slower event-driven ideas — **Form 4 insider cluster
purchases** and an **OSAP-guided price-only factor composite** — are worth running in parallel as
low-maintenance "slow lane" experiments, with the explicit understanding that paper trading can
validate their implementation but only their long historical backtests can establish an edge.
Everything else examined (pre-FOMC drift, index effects, PEAD in large caps, pairs trading,
social-media sentiment, Google-Trends attention, turn-of-the-month, overnight-vs-intraday, buyback
drift, customer-supplier momentum) fails on post-publication evidence, on costs, on free-data
availability, or on statistical power — details in §4 and the appendix. The realistic expectation,
stated plainly: the best-supported idea here has perhaps a 20–30% chance of showing a tradeable,
market-adjusted edge after costs; the literature's base rate for published anomalies surviving
publication, costs, and large-cap implementation is poor (McLean & Pontiff 2016; Hou, Xue & Zhang
2020; Chen & Zimmermann 2023).

---

## 2. Ranked shortlist

### Idea 1 — Overnight news-sentiment long-short (daily horizon) — **rank 1**

**Mechanism.** Prices underreact to firm-specific news for hours-to-days, most strongly to
negative news and to stories about fundamentals; the money is left on the table because the
marginal readers of low-salience headlines are slow, and arbitrage capital does not fully chase
small, short-lived, stock-specific mispricings (limits-to-arbitrage). This is the one mechanism in
this report with peer-reviewed evidence at exactly the daily horizon the lab can trade.

**Evidence — medium-to-strong, with a big caveat on magnitude.**
- Tetlock (2007, *Journal of Finance* 62(3)): a one-standard-deviation rise in WSJ-column
  pessimism predicts a next-day Dow drop of ~8.1bp (alt. spec. 6.2bp), with later reversion —
  market-level, small, but the first clean demonstration that text moves next-day prices
  ([paper](https://www.columbia.edu/~pt2238/papers/Tetlock_Media_Sentiment_JF.pdf), read via
  search extracts).
- Tetlock, Saar-Tsechansky & Macskassy (2008, *JF* 63(3), "More Than Words"): the fraction of
  negative words in firm-specific news forecasts low earnings and returns; prices briefly
  underreact; predictability is largest for fundamentals-focused stories. Crucially, their own
  cost table shows the trading profits "easily vanish" once round-trip costs exceed ~10bp
  ([paper](https://business.columbia.edu/sites/default/files-efs/pubfiles/3096/More_Than_Words_tetlock.pdf)).
- Lopez-Lira & Tang (2023–24, "Can ChatGPT Forecast Stock Price Movements?"): GPT-scored headlines
  (159,137 firm-headline-date observations, 4,123 US firms, Oct 2021 onward — chosen to post-date
  the model's training) predict next-day returns; the long-short earns ~38bp/day with a gross
  annualized Sharpe of 3.28, but the short leg carries most of it (short-leg Sharpe 2.12 vs 0.90
  long), predictability concentrates in smaller stocks and negative news, and the authors
  themselves attribute it to limits to arbitrage
  ([arXiv 2304.07619](https://arxiv.org/pdf/2304.07619), read via search extracts). Alpha
  Architect's summary (practitioner source) reports the strategy stays profitable at 5–10bp
  round-trip costs and dies at ~20bp
  ([alphaarchitect.com](https://alphaarchitect.com/chatgpt-forecast-stock-price/)).
- The critique literature matters: Glasserman & Lin (2023; *J. Financial Data Science* 2024) show
  look-ahead/memorization effects in LLM-scored headlines (anonymizing company names *improved*
  in-sample signals), and Lopez-Lira, Tang & Zhu (2025) and Gao, Jiang & Yan (2025) document LLM
  memorization of historical prices directly
  ([lookahead-bias test](https://arxiv.org/html/2512.23847v1)). This is an argument **for** a
  small frozen model: FinBERT's weights predate the test data and cannot memorize 2020s returns.
- FinBERT vs dictionary: a 2024 *Finance Research Letters* study finds the Loughran–McDonald
  dictionary has the least predictive power among tested models for news-based direction
  forecasting, with transformer models ahead ([via search](https://arxiv.org/pdf/2412.19245));
  evidence on 10-K (not headline) tone is a clean null (non-peer-reviewed replication,
  [github](https://github.com/ZacharyChai/finbert-10k-sentiment)). Run both scorers; the
  dictionary is the free robustness check.

**Realistic edge after costs and SPY adjustment.** The honest estimate is far below Lopez-Lira &
Tang's gross Sharpe 3.28: the lab trades liquid large/mid caps (where the paper's effect is
weakest), hedges beta, and pays its modelled 5bp per side. A net, market-adjusted Sharpe in the
0.5–1.0 range *if the effect exists at all in this universe* is the right planning number; there
is a real chance the large-cap edge is zero.

**Data needed and cost — all free, with one verification step.**
- Alpaca News API: Benzinga-sourced, historical from 2015, averaging 130+ articles/day
  ([docs](https://docs.alpaca.markets/us/docs/historical-news-data)); a community forum reports a
  possible gap Feb 2015–Oct 2016 — verify with a coverage census before relying on early years
  ([forum](https://forum.alpaca.markets/t/historical-news-data-missing-for-2016/13576)).
- Alpaca bars: historical since 2016 on the free Basic plan (recent-15-minute restriction is
  irrelevant for a next-day strategy) ([docs](https://docs.alpaca.markets/us/docs/about-market-data-api)).
- FinBERT on GitHub Actions: no published headline-throughput benchmark exists (searched); on a
  4-core runner, a BERT-base model on ~30-token headlines should score on the order of 10–50
  headlines/sec with batching (estimate, to be benchmarked first). The full archive is roughly
  130/day × ~4,000 days ≈ 500–700k headlines → single-digit hours across a few parallel jobs,
  well inside the 6-hour limit. One-off cost; daily incremental scoring is trivial.

**Concrete test specification.**
- *Signal:* for each symbol each day, aggregate all headlines+summaries time-stamped between the
  prior 16:00 ET close and 09:25 ET using FinBERT (P(pos)−P(neg), story-weighted), with the
  Loughran–McDonald net-negativity score computed in parallel as a robustness line. Stocks with no
  fresh news are excluded (no stale-signal carry).
- *Universe:* top ~300 US common stocks by 60-day median dollar volume, price > $5 (buildable from
  Alpaca daily bars; survivorship-safe because membership is recomputed point-in-time from bars).
- *Portfolio:* long the top sentiment decile of news-stocks, short the bottom decile, equal
  weight, enter at next open, exit at same-day close (variant: next open), each position carrying
  the lab's standard opposite beta-weighted SPY hedge; report `pnl_vs_spy` exactly as the paper
  book does.
- *Costs:* 5bp per side (lab standard) plus a sensitivity table at 10 and 20bp round-trip — the
  Tetlock-2008 and Lopez-Lira cost cliffs sit in that range, so the sensitivity table is the
  honesty check.
- *Walk-forward:* train/choose all design knobs on 2016–2021 only; one validation pass on
  2022–2024; a final untouched holdout 2025→today scored once. Day-resampled bootstrap CIs
  (the lab's standard).
- *Power:* a daily strategy observed over 10 years detects a true annualized Sharpe ≥ 0.63 at
  t ≥ 2 (t = SR·√years); over the ~5-year validation+holdout window alone the detectable Sharpe is
  ≥ 0.89. A live paper year by itself only detects SR ≥ 2 — which is why the verdict must come
  from the historical walk-forward, with paper trading as the implementation check.
- *Pre-committed pass/fail:* **pass** = holdout (2025→) SPY-adjusted, cost-charged mean daily
  return positive with the day-resampled 95% CI above zero **and** validation-window net Sharpe
  ≥ 0.5; then 3 months of paper trading whose realized expectancy must stay inside the backtest's
  CI. **Fail** on any leg → archive the idea; no re-tuning and re-trying (that is the v0.2 lesson).
- *Main failure mode:* the edge lives in the short leg of small caps (exactly what Lopez-Lira &
  Tang found) and evaporates in a liquid large-cap, beta-hedged, cost-charged book; secondarily,
  Benzinga's coverage/mix changed over the decade, making early-sample signals unrepresentative.

### Idea 2 — Form 4 insider cluster purchases (20–60 day horizon) — **rank 2**

**Mechanism.** Officers and directors legally trade on superior information about their own firm;
*purchases* (unlike sales) have one dominant motive. The signal is strongest when it is
"opportunistic" (not routine, not a 10b5-1 plan) and when several insiders buy within days of each
other. Reasons the money stays on the table: the information diffuses slowly, the stocks involved
skew smaller, and institutional mandates rarely chase 2-day-old Form 4s.

**Evidence — strong original, genuinely uncertain post-publication.**
- Lakonishok & Lee (2001, *RFS* 14(1), 1975–1995, all NYSE/AMEX/Nasdaq): insider *purchases*
  predict returns, selling does not; the effect concentrates in smaller firms
  ([paper](https://www.lsvasset.com/pdf/research-papers/Insider-Trades-Informative.pdf), read via
  search extracts). A third-party summary puts small-cap purchase abnormal returns ~7.4% over 12
  months (not verified against the paper's tables).
- Cohen, Malloy & Pomorski (2012, *JF* 67(3), "Decoding Inside Information", 1986–2007):
  classifying trades as routine vs opportunistic, opportunistic trades earn value-weighted
  abnormal returns of **82bp/month** (equal-weighted 180bp), routine trades ≈ zero; opportunistic
  trades also predict future firm news
  ([SSRN 1692517](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1692517), read via search
  extracts).
- Post-publication: no clean replication found. A UK FTSE-350 study finds the anomaly survives
  only partly once small firms are excluded; one study narrows the edge to directors with
  interlocking board seats; the samples above end in 2007. Honest grade: **medium** — mechanism
  durable (it is legal informed trading), magnitude post-2012 unknown.

**Realistic edge.** If the published 82bp/month VW alpha decayed by the literature's typical
~50–60% post-publication (McLean & Pontiff 2016), expect ~30–40bp/month on a mid/large-cap book
before the lab's costs — a calendar-time information ratio somewhere around 0.4–0.8 annualized.
Small enough that only a long backtest can see it.

**Data — free and confirmed.** SEC "Insider Transactions Data Sets": structured quarterly files
of all Forms 3/4/5, **2006 Q1 → present**, free from DERA
([sec.gov](https://www.sec.gov/data-research/sec-markets-data/insider-transactions-data-sets));
live signals from the EDGAR daily index (filings due within 2 business days of the trade). Daily
prices for a 2006→ backtest: yfinance daily bars (free; survivorship caveat — delisted names are
missing, mitigated but not removed by a mid/large-cap universe), with Alpaca daily bars confirming
2016→.

**Concrete test specification.**
- *Signal:* open-market purchases (transaction code P) by officers/directors; **cluster** = ≥2
  distinct insiders buying within 5 trading days; exclude filings marked as 10b5-1-plan trades
  (checkbox in the XML since 2023; before that, a footnote-text heuristic, imperfect — say so in
  the results); a simpler "non-routine" filter (buyer has no same-calendar-month purchase in the
  prior 3 years, per Cohen et al.) as a variant.
- *Universe:* top ~1,000 by market cap at signal time (avoids the microcap liquidity trap while
  keeping the mid-caps where the effect lives).
- *Portfolio:* calendar-time, equal-weighted, hold 40 trading days from the *filing* date (never
  the trade date — that is lookahead), overlapping positions, beta-weighted SPY hedge, 5bp/side.
- *Walk-forward:* design on 2006–2017, validate 2018–2022, holdout 2023→. Month-resampled CIs
  (slow strategy — the lab's standard for slower books).
- *Power:* per-event framing: detecting a true per-event abnormal return of μ over 2 months
  against a cross-event SD of σ ≈ 15% needs N ≈ (2σ/μ)²: μ = 2% → ~225 events; μ = 1% → ~900.
  The 20-year backtest contains thousands of qualifying clusters, so the backtest has power;
  live, a mid/large-cap universe plausibly yields ~10–30 clusters/month, so paper trading alone
  would need 1–3 years even for the optimistic case. Calendar-time framing: 20 backtest years
  detect IR ≥ 0.45 at t ≥ 2.
- *Pre-committed pass/fail:* **pass** = holdout (2023→) SPY-adjusted net mean monthly return
  positive with month-resampled 95% CI above zero and full-sample IR ≥ 0.45; then paper-trade 6
  months purely as an execution check (fills near open after filing-day, hedge tracking), judged
  by tracking error vs backtest, not by its own significance. **Fail** → archive.
- *Main failure mode:* the anomaly was always mostly a small-cap effect and the post-2012,
  mid/large-cap, post-publication residue is zero; secondarily, pre-2023 10b5-1 misclassification
  adds noise that buries a thin signal.

### Idea 3 — OSAP-guided price-only factor composite (monthly, "slow lane") — **rank 3**

**Mechanism & why it is on the list.** The brief asked specifically whether the Chen & Zimmermann
Open Source Asset Pricing dataset lets the lab test post-publication anomaly performance without
building signals — it does. OSAP publishes monthly long-short returns for **212 published
predictors** (CSV/Stata, CC BY 4.0, portfolios through end-2023 in the August-2024 release, via
website, Hugging Face, or the `openassetpricing` Python package)
([openassetpricing.com](https://www.openassetpricing.com/),
[PyPI](https://pypi.org/project/openassetpricing/),
[GitHub](https://github.com/OpenSourceAP/CrossSection)). Step 1 is pure analysis at zero data
cost: measure each predictor's post-publication, recent-15-year mean return directly from OSAP.
Step 2 implements only the survivors that need **prices alone** (momentum 12-2, 52-week-high
proximity, short-term reversal as a *trade-timing overlay* rather than a standalone strategy,
seasonality, low-beta) as one value-weighted composite on the lab's top-300 universe, monthly
rebalance, SPY-hedged.

**Evidence — strong that *most* anomalies are dead; weak that the composite beats.** McLean &
Pontiff (2016, *JF* 71(1), 97 predictors): −26% out-of-sample, −58% post-publication
([paper](https://gwern.net/doc/economics/2016-mclean.pdf)); Jacobs & Müller (2020, *JFE*): US
post-publication decline −62%, and notably *no reliable decline in 38 non-US markets*; Chen &
Zimmermann's own follow-up work: decay ~50% gross, ~72% excluding stale data, and roughly **93%
after trading costs** — "even the strongest anomalies have tiny expected returns" after costs and
decay ([publication-bias paper](https://arxiv.org/pdf/2209.13623),
["Zeroing In"](https://www.cambridge.org/core/services/aop-cambridge-core/content/view/945133D5A3ECEEAF466AEE91551FD225/S0022109022000874a.pdf/zeroing-in-on-the-expected-returns-of-anomalies.pdf),
read via search extracts). Hou, Xue & Zhang (2020, *RFS*): with microcaps de-emphasized, 65% of
452 anomalies fail |t| ≥ 1.96 (82% at 2.78); microcaps are 3.2% of market cap but 60.7% of stock
count ([paper](https://theinvestmentcapm.com/uploads/1/2/2/6/122679606/houxuezhang2019rfs.pdf)).
Jensen, Kelly & Pedersen (2023, *JF*) is the optimistic counterweight — most factors replicate
across 93 countries — but replication ≠ net-of-cost retail profit.

**Power — stated honestly, this is the idea's defining limit.** A monthly long-short with a
realistic post-publication net Sharpe of ~0.3–0.5 needs **16–44 years** of live data for t ≥ 2.
No paper-trading program can validate it. The only legitimate claims the lab can make are: (a) the
OSAP-measured post-publication record of the chosen predictors (free, instant, decades of data);
(b) a 2006→ price-only backtest of the composite (detects SR ≥ 0.45); (c) live paper tracking of
the backtest. That is still worth doing because it is nearly free to run and it anchors the lab's
expectations about *everything else* in this report.

- *Pre-committed pass/fail:* **pass to implementation** only if ≥3 price-only predictors show
  positive OSAP post-publication mean with t ≥ 1 over their last 15 data years; **pass to paper**
  only if the lab's own 2006→ composite backtest has month-resampled 95% CI above zero after
  costs and SPY adjustment. Paper trading is judged on tracking error vs the backtest (within the
  backtest CI over 6 months), explicitly **not** on live significance.
- *Main failure mode:* the composite is statistically alive only because of pre-2010 data, and
  the lab ends up trading a museum piece; the OSAP step is designed to catch exactly this before
  any order is placed.

### Idea 4 — News co-mention lead-lag (2–5 day horizon) — **rank 4, exploratory**

**Mechanism.** Investors underreact to news about economically linked firms: Cohen & Frazzini
(2008, *JF*, "Economic Links and Predictable Returns") showed supplier stocks lag shocks to their
disclosed customers, with a monthly long-short alpha of 1.3% (t = 4.93) over 1981–2004
([paper](https://pages.stern.nyu.edu/~afrazzin/pdf/Economic%20Links%20and%20Predictable%20Returns%20-%20Cohen%20and%20Frazzini.pdf)).
Post-publication, that specific signal decayed hard: an independent replication finds the sign
survives but not significance out-of-sample; a 2023 study finds value-weighted customer-momentum
portfolios insignificant and *negative* over 2005–2018 ([arXiv](https://arxiv.org/pdf/2301.11394));
the official customer-link data (Compustat segments / FactSet Revere) is not free anyway. **But**
the decay evidence has an interesting shape: text-based industry links (Hoberg–Phillips TNIC)
kept working after SIC-based industry momentum faded (Text-Based Industry Momentum, *JFQA* 2019,
[paper](https://www.cambridge.org/core/services/aop-cambridge-core/content/view/6E04891A7AD30C24C21CBDE37EC06BF4/S0022109018000479a.pdf/text-based-industry-momentum.pdf)),
suggesting finer, less-crowded link graphs decay slower. The lab owns a free link graph nobody
arbitrages directly: **co-mentions in Benzinga articles** (Alpaca news items carry multi-symbol
tags). Signal: when stock A has a large idiosyncratic news-day move, trade linked stock B (high
trailing co-mention weight, no own news, no move yet) over the next 1–5 days.

**Evidence grade: medium-weak** — the mechanism is peer-reviewed, this exact implementation is
not. Treat it as research, not a promise. It shares Idea 1's pipeline (same news archive, same
universe, same cost model), so the marginal build cost is small, which is the only reason it makes
the shortlist over better-documented but untestable ideas.

- *Test spec:* same universe/costs/market adjustment as Idea 1; link graph from trailing-12-month
  co-mention counts (point-in-time); design 2016–2021, validate 2022–2024, holdout 2025→;
  day-resampled CIs. Power: identical to Idea 1 (daily book, 10 years → detectable SR ≥ 0.63).
- *Pre-committed pass/fail:* same two-stage rule as Idea 1. **Fail** → archive without re-tuning.
- *Main failure mode:* co-mentions mostly encode same-sector pairs, so the "lead-lag" collapses
  into (decayed) industry momentum plus noise; the test must therefore include an
  industry-momentum control.

---

## 3. Sentiment and news, in depth

**What actually works, per the strongest evidence, and at what horizon:**

1. **Firm-specific textual tone → days.** The core, replicated result (Tetlock 2008; the LLM
   recut in Lopez-Lira & Tang 2023): negative firm news is underreacted to for roughly one to a
   few trading days; fundamentals-focused stories carry the most signal; negative beats positive;
   small caps beat large. Every careful cost treatment puts the survival threshold at a ~10–20bp
   round trip — tight but not hopeless for a liquid-large-cap, at-the-open implementation
   paying something like the lab's modelled 10bp round trip.
2. **Market-level media sentiment → next day, tiny.** Tetlock 2007's 6–8bp next-day effect with
   reversal is real but an order of magnitude too small to trade net of costs as a timing signal,
   and it is a *market-exposure* bet, which the lab's SPY-adjustment framework correctly scores
   as ~zero. Not pursuable.
3. **Earnings-call tone → weeks.** Price, Doran, Peterson & Bliss (2012, *J. Banking & Finance*):
   call tone predicts 60-day drift better than the earnings surprise itself
   ([ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0378426611002901),
   abstract read). But newer work disagrees on sign and scope (a 2023 study finds *negative*
   post-call tone-return relations; a 2026 preprint finds continuation only in microcaps), and —
   decisive for the lab — free, bulk, point-in-time call transcripts do not exist among the lab's
   data sources (EDGAR has press releases, not transcripts). Watch, don't build.
4. **Attention spikes → short pop, then reversal.** Da, Engelberg & Gao (2011, *JF*, "In Search
   of Attention"): abnormal Google search volume predicts a ~2-week price increase then reversal,
   Russell 3000 2004–2008 ([paper](https://academicweb.nd.edu/~zda/Google.pdf), read via search
   extracts). Infeasible for the lab: pytrends is archived (April 2025) and rate-limited, the
   official Trends API is a closed alpha, and the index is relative, not absolute. Abnormal *news
   volume* from the Alpaca archive is the free cousin and can ride along as a feature in Idea 1's
   dataset at zero extra cost — but as a conditioning variable, not a standalone strategy,
   because its documented pattern (pop-then-reversal) is exactly the kind of two-sided effect
   that died in the lab's intraday book before.
5. **Analyst revisions → months.** A real, replicated predictor family, but it needs a
   point-in-time estimates feed (IBES); no free source exists; yfinance's current-snapshot
   estimates are not point-in-time and would manufacture lookahead. Skip.
6. **Social media → unclear and unavailable.** The academic record is split (a 2024 *JFE* paper
   finds next-day predictability from StockTwits common-factor sentiment; several studies find
   none), and the decisive point is that free, licensed, historical Twitter/StockTwits firehoses
   do not exist in 2026. Untestable at this lab. Skip.

**Can the lab's compute reach it?** Yes, with a small model. FinBERT (BERT-base, ~110M params,
trained on pre-2015 financial text — which also makes it immune to the LLM memorization critique)
has no published headline-throughput benchmark (searched; closest figures are long-document
latencies from unverified blogs), so the first task in Idea 1's plan is a 15-minute benchmark on a
runner. A defensible planning estimate for 4-core CPU inference on ~30-token headlines with
batching is tens of headlines per second; even at a pessimistic 10/sec the full ~600k-headline
archive is ~17 CPU-hours — a weekend of parallel GitHub Actions jobs, once, and seconds per day
thereafter.

**What volume could Claude score?** A Claude Code subscription (no API key) is interactive-session
capacity: realistically thousands of headlines per day, not millions. The right division of
labor: use Claude to **label a stratified validation set (~2,000 headlines)** against which
FinBERT and the Loughran–McDonald scorer are graded, and to audit the worst disagreements.
Production scoring belongs to the small local model. (This also sidesteps the
lookahead/memorization problem that the LLM-forecasting literature is currently fighting about —
Glasserman & Lin 2023; Gao, Jiang & Yan 2025.)

---

## 4. Promising-sounding but avoid

- **Pre-FOMC announcement drift** (Lucca & Moench 2015, *JF*): since 1994, >80% of the US equity
  premium accrued in the 24h before scheduled FOMC announcements (~3.9%/yr vs ~0.9%/yr on all
  other days) ([Liberty Street](https://libertystreeteconomics.newyorkfed.org/2012/07/the-puzzling-pre-fomc-announcement-drift)).
  Avoid for **power**: 8 events/year with a per-event effect of ~20–50bp against ~100bp daily
  vol needs on the order of (2·1.0/0.3)² ≈ 45–100 events ≈ 6–13 years for t ≥ 2, the post-2015
  record is weaker and concentrated in press-conference meetings (NY Fed follow-up), and
  Cieslak–Morse–Vissing-Jørgensen attribute much of it to leakage that cannot be predicted from
  the calendar alone. Also it is pure market exposure, which the lab's own standard nets out.
- **S&P index additions/deletions**: Greenwood & Sammon ("The Disappearing Index Effect", *JF*
  2025): addition pops fell from 7.4% (1990s) to <1% in the last decade; deletions from −16.1% to
  −0.6% (2010–2020), statistically zero
  ([paper](https://marcosammon.com/images/greenwood_sammon.pdf)). The effect is gone, and
  professionals front-run reconstitution dates anyway.
- **PEAD in the lab's universe**: Martineau ("Rest in Peace Post-Earnings Announcement Drift",
  *Critical Finance Review* 2022): drift is dead in all but microcaps, roughly zero for large
  stocks since ~2006 ([OSF](https://osf.io/kyqae/), read via search extracts and secondary
  summaries). The lab trades exactly the universe where it no longer exists.
- **Earnings-announcement premium**: real historically (Frazzini & Lamont 2007: 7–18%/yr;
  global confirmation in Barber et al.), but recent US work finds it has disappeared, plausibly
  via 2004's 8-K reform ("The Disappearing Earnings Announcement Premium",
  [Rotman paper](https://www-2.rotman.utoronto.ca/userfiles/seminars/files/G_%20Narayanamoorthy%20paper.pdf)),
  and the Barber paper itself flags ~100%/month turnover and very high arbitrage costs.
- **Pairs trading**: GGR (2006, *RFS*): ~11%/yr excess, 1962–2002; Do & Faff (2010, 2012):
  top-20-pairs returns fell ~0.86% → ~0.24%/month (secondary figure) and the baseline scheme is
  **unprofitable after costs** in the modern sample
  ([GGR](http://stat.wharton.upenn.edu/~steele/Courses/434/434Context/PairsTrading/PairsTradingGGR.pdf),
  [Do & Faff via abstracts](https://www.researchgate.net/publication/228259167_Are_Pairs_Trading_Profits_Robust_to_Trading_Costs)).
  Also high-turnover mean reversion is adjacent to what the lab already falsified intraday.
- **Short-term reversal as a standalone**: Avramov, Chordia & Goyal (2006, *JF*): profits sit in
  high-turnover, illiquid names and are smaller than realistic costs. Low-turnover variants may
  survive institutionally, but it is a liquidity-provision business, not a retail paper-lab edge.
  Useful only as an *entry-timing overlay* inside Ideas 2–3.
- **Time-series momentum / trend following on the lab's horizon**: Huang, Li, Wang & Zhou (2020,
  *JFE* 135(3)): MOP's pooled t = 4.34 fails bootstrap critical values; asset-level regressions
  show little TSM ([paper](https://ink.library.smu.edu.sg/context/lkcsb_research/article/7520/viewcontent/Time_series_momentum_JFE_sv.pdf)).
  Even taking the practitioner view, a one-asset (SPY) trend overlay is a market-timing bet the
  lab's SPY-adjustment nets to ~zero, and multi-asset futures are outside Alpaca equities.
- **Sector/industry momentum (SIC/ETF version)**: original effect (Moskowitz & Grinblatt 1999)
  challenged by Grundy & Martin (2001) and documented as weaker post-publication; monthly horizon
  → power needs decades; French-library industry data is free
  ([data library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html)) so
  it can be *studied* offline, but it does not merit live slots.
- **Overnight-vs-intraday harvesting**: the overnight premium is real in data but Lachance
  (*Review of Financial Economics* 2023, "Night trading") finds overnight holding is "generally a
  losing proposition" after costs outside narrow subsets; breakeven needs abnormal returns of
  4–8%/yr against 1.5–3.1bp daily round trips
  ([Wiley](https://onlinelibrary.wiley.com/doi/full/10.1002/rfe.1180), read via search extracts;
  cost figures echoed by Alpha Architect, practitioner). Daily-compounded cost on a
  hold-every-night book is exactly the regime where 5bp/side kills everything.
- **Turn-of-the-month**: evidence genuinely mixed (an SSRN/IRFA 2026 paper finds an 8-day-window
  effect persisting; a practitioner study finds the classic window gone in the last decade; a
  replication finds modern rolling estimates indistinguishable from zero). Small, market-exposure
  flavored, ~12 events/year → underpowered. Skip.
- **Buyback-announcement drift**: Ikenberry-era long-run returns have not survived: Fu & Huang
  (2015) and others find post-2001 long-horizon abnormal returns much lower or gone in the US.
- **Customer–supplier (official-links) momentum**: decayed post-publication (see Idea 4) *and*
  the link data is paywalled. The co-mention variant in Idea 4 is the only free salvage.
- **Live LLM scoring of the full news stream with Claude**: volume-infeasible (see §3) and the
  academic contamination fight makes LLM-scored *backtests* hard to defend right now.
- **Weekly/0DTE option selling, intraday TA variants, more parameter tuning, ML regime filters on
  the existing entries**: already ruled out by the lab's own results (`results/OPTIONS.md`,
  `results/REVIEW.md`, README v0.2–v0.10); listed here only for completeness.

---

## 5. Appendix — every candidate evaluated

Evidence grade: S = strong (top-journal + replications), M = medium, W = weak. Post-pub = what
happened after publication/sample end. Feasible = lab can get the data free and run it on Actions.

| Candidate | Horizon | Evidence | Post-publication status | Data feasibility | Verdict |
|---|---|---|---|---|---|
| Firm-news sentiment L/S (FinBERT/LM on Benzinga) | 1 day | S (Tetlock 07/08; Lopez-Lira & Tang 23) | Alive in recent samples; magnitude post-2023 unknown; cost cliff 10–20bp | Yes — news 2015→, bars 2016→ | **Shortlist #1** |
| Form 4 insider cluster purchases | 1–3 mo | S original (LL01; CMP12) | Uncertain; likely halved; mid/large-cap residue unproven | Yes — SEC DERA 2006→ free | **Shortlist #2** |
| OSAP survivor composite (price-only factors) | monthly | S (OSAP, MP16, HXZ20, JKP23) | Average anomaly ≈ dead after costs+decay; survivors identifiable from OSAP directly | Yes — OSAP CSV free; prices free | **Shortlist #3 (slow lane)** |
| News co-mention lead-lag | 2–5 days | M (CF08 mechanism; TNIC persistence) | Official-link version decayed to ~0 | Yes — same pipeline as #1 | **Shortlist #4 (exploratory)** |
| Market-level media sentiment timing | 1 day | S (Tetlock 07) | 6–8bp/day, reverses; is market exposure | Yes | Avoid — too small, netted out by SPY adjustment |
| Earnings-call tone drift | 60 days | M (Price et al. 12; newer work conflicting) | Sign disputes; microcap-only in 2026 preprint | No — no free transcript archive | Avoid (data) |
| Analyst forecast revisions | 1–6 mo | S historical | Decayed like other anomalies | No — IBES not free, lookahead risk | Avoid (data) |
| Social-media sentiment | 1 day | M, split literature | Untested OOS at scale | No — no free historical firehose | Avoid (data) |
| Google Trends / Wikipedia attention | 1–2 wk | M (DEG11) | Pop-then-reversal; crowded | No — pytrends archived, API closed alpha | Avoid (data); news-volume cousin folded into #1 |
| Abnormal news volume (attention) | days | M | Two-sided (pop+reversal) | Yes | Feature in #1, not standalone |
| PEAD | 1–3 mo | S original | Dead outside microcaps since ~2006 (Martineau) | Partly | Avoid (dead in lab's universe) |
| Earnings-announcement premium | 1 mo | S original (FL07; Barber et al.) | US: disappeared post-2004 reform; turnover ~100%/mo | Partly (8-K dates free) | Avoid |
| Buyback-announcement drift | 6–48 mo | S original (Ikenberry) | Post-2001 much weaker/gone (Fu & Huang 15) | Partly (8-K/10-Q) | Avoid |
| Index additions/deletions | days–wks | S | Gone: <1% adds, −0.6% deletes (Greenwood & Sammon) | Yes | Avoid (dead) |
| Pre-FOMC drift | 24 h ×8/yr | S (LM15) | Weaker post-2015; press-conf. meetings; leakage story | Yes | Avoid (power: ≥6–13 yrs) |
| Turn-of-the-month | 8 days/mo | M, contested | Classic window faded; shifted window claimed alive | Yes | Avoid (small, underpowered, mkt exposure) |
| Overnight-vs-intraday | nightly | S descriptive | Net of costs ≈ losing (Lachance 23) | Yes | Avoid (costs) |
| Short-term reversal standalone | 1–5 days | S original (ACG06 critique) | Below costs except low-turnover institutional variants | Yes | Avoid standalone; timing overlay only |
| 52-week-high momentum | monthly | M (GH04; subsumption disputed) | In OSAP; test via Idea 3, not standalone | Yes | Fold into #3 |
| Low-volatility | monthly | M–S | Crowding debated; decades to verify live | Yes | Fold into #3 |
| Industry/sector momentum (SIC/ETF) | monthly | M (MG99; GM01 critique) | Weaker post-publication; TNIC variant persisted | Yes (French library) | Avoid live; offline study only |
| Time-series momentum (SPY overlay) | weeks–mo | Contested (MOP12 vs Huang et al. 20) | Pooled-t artifact per critique | Yes | Avoid |
| Customer–supplier momentum (official links) | monthly | S original (CF08) | VW ≈ 0 and negative 2005–2018 | No (links paywalled) | Avoid; co-mention salvage = #4 |
| Pairs trading (GGR distance) | days–wks | S original | Declined (DF10); unprofitable after costs (DF12) | Yes | Avoid |
| Option-premium selling | monthly | Lab's own study | WPUT negative alpha; rest ≈ 0 | — | Already ruled out (`results/OPTIONS.md`) |
| LLM live headline scoring (Claude, full stream) | 1 day | M + contamination fight | n/a | No — volume ~10³/day vs needed ~10⁵ | Avoid; use for validation labels only |

---

## 6. Sources

Peer-reviewed / working papers (all read via the search tool's server-side page extracts, as noted
in the header; items marked *abstract/secondary* could not be read in full):

1. Tetlock, P. (2007). "Giving Content to Investor Sentiment: The Role of Media in the Stock Market." *Journal of Finance* 62(3), 1139–1168. https://www.columbia.edu/~pt2238/papers/Tetlock_Media_Sentiment_JF.pdf
2. Tetlock, P., Saar-Tsechansky, M., & Macskassy, S. (2008). "More Than Words: Quantifying Language to Measure Firms' Fundamentals." *Journal of Finance* 63(3), 1437–1467. https://business.columbia.edu/sites/default/files-efs/pubfiles/3096/More_Than_Words_tetlock.pdf
3. Lopez-Lira, A., & Tang, Y. (2023–24). "Can ChatGPT Forecast Stock Price Movements? Return Predictability and Large Language Models." arXiv:2304.07619. https://arxiv.org/pdf/2304.07619
4. Glasserman, P., & Lin, C. (2023/2024). "Assessing Look-Ahead Bias in Stock Return Predictions Generated by GPT Sentiment Analysis." *Journal of Financial Data Science* 6(1). *(abstract/secondary)* https://www.pm-research.com/content/iijjfds/6/1/25
5. Gao, Z., Jiang, W., & Yan, Y. (2025). "Detecting Lookahead Bias in LLM Forecasts." arXiv:2512.23847. https://arxiv.org/html/2512.23847
6. Chen, Q. et al. (2024). LLM vs dictionary sentiment for return direction. *Finance Research Letters* 62, 105227. *(abstract/secondary)* https://arxiv.org/pdf/2412.19245
7. Price, S.M., Doran, J., Peterson, D., & Bliss, B. (2012). "Earnings Conference Calls and Stock Returns: The Incremental Informativeness of Textual Tone." *Journal of Banking & Finance.* *(abstract)* https://www.sciencedirect.com/science/article/abs/pii/S0378426611002901
8. Da, Z., Engelberg, J., & Gao, P. (2011). "In Search of Attention." *Journal of Finance* 66(5). https://academicweb.nd.edu/~zda/Google.pdf
9. Moskowitz, T., & Grinblatt, M. (1999). "Do Industries Explain Momentum?" *Journal of Finance* 54(4). *(abstract/secondary)* https://onlinelibrary.wiley.com/doi/abs/10.1111/0022-1082.00146
10. "Text-Based Industry Momentum." *JFQA* (2019). https://www.cambridge.org/core/services/aop-cambridge-core/content/view/6E04891A7AD30C24C21CBDE37EC06BF4/S0022109018000479a.pdf/text-based-industry-momentum.pdf
11. Moskowitz, T., Ooi, Y.H., & Pedersen, L.H. (2012). "Time Series Momentum." *JFE* 104(2). *(secondary)*
12. Huang, D., Li, J., Wang, L., & Zhou, G. (2020). "Time Series Momentum: Is It There?" *JFE* 135(3). https://ink.library.smu.edu.sg/context/lkcsb_research/article/7520/viewcontent/Time_series_momentum_JFE_sv.pdf
13. Cohen, L., & Frazzini, A. (2008). "Economic Links and Predictable Returns." *Journal of Finance* 63(4). https://pages.stern.nyu.edu/~afrazzin/pdf/Economic%20Links%20and%20Predictable%20Returns%20-%20Cohen%20and%20Frazzini.pdf
14. "Customer Momentum" (2023). arXiv:2301.11394 (post-publication customer-momentum evidence). https://arxiv.org/pdf/2301.11394
15. Martineau, C. (2022). "Rest in Peace Post-Earnings Announcement Drift." *Critical Finance Review.* *(OSF/secondary)* https://osf.io/kyqae/
16. Frazzini, A., & Lamont, O. (2007). "The Earnings Announcement Premium and Trading Volume." NBER w13090. https://www.nber.org/system/files/working_papers/w13090/w13090.pdf
17. Barber, B. et al. "The Earnings Announcement Premium Around the Globe." https://webuser.bus.umich.edu/rlehavy/BDLT.pdf
18. "The Disappearing Earnings Announcement Premium" (Rotman seminar paper). https://www-2.rotman.utoronto.ca/userfiles/seminars/files/G_%20Narayanamoorthy%20paper.pdf
19. Lakonishok, J., & Lee, I. (2001). "Are Insider Trades Informative?" *RFS* 14(1). https://www.lsvasset.com/pdf/research-papers/Insider-Trades-Informative.pdf
20. Cohen, L., Malloy, C., & Pomorski, L. (2012). "Decoding Inside Information." *Journal of Finance* 67(3). https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1692517
21. Greenwood, R., & Sammon, M. (2025). "The Disappearing Index Effect." *Journal of Finance.* https://marcosammon.com/images/greenwood_sammon.pdf
22. Lucca, D., & Moench, E. (2015). "The Pre-FOMC Announcement Drift." *Journal of Finance* 70(1); NY Fed Staff Report 512 and Liberty Street posts. https://libertystreeteconomics.newyorkfed.org/2012/07/the-puzzling-pre-fomc-announcement-drift
23. Lachance, M.-E. (2023). "Night Trading: Lower Risk but Higher Returns?" *Review of Financial Economics.* https://onlinelibrary.wiley.com/doi/full/10.1002/rfe.1180
24. Lou, D., Polk, C., & Skouras, S. "A Tug of War: Overnight Versus Intraday Expected Returns." http://www.econ.yale.edu/~shiller/behfin/2015-04-11/lou_polk_skouras.pdf
25. Kayaçetin, N.V. (2026). "Infrequent Rebalancing, Risk Deferral, and Equity Returns at the Turn of the Month." *(SSRN/ScienceDirect abstract)* https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7201062
26. Avramov, D., Chordia, T., & Goyal, A. (2006). "Liquidity and Autocorrelations in Individual Stock Returns." *Journal of Finance* 61(5). https://papers.ssrn.com/sol3/papers.cfm?abstract_id=555968
27. George, T., & Hwang, C.-Y. (2004). 52-week-high momentum. *(secondary, via citing papers)*
28. McLean, R.D., & Pontiff, J. (2016). "Does Academic Research Destroy Stock Return Predictability?" *Journal of Finance* 71(1). https://gwern.net/doc/economics/2016-mclean.pdf
29. Jacobs, H., & Müller, S. (2020). "Anomalies Across the Globe: Once Public, No Longer Existent?" *JFE.* *(abstract)* https://www.sciencedirect.com/science/article/abs/pii/S0304405X19301618
30. Hou, K., Xue, C., & Zhang, L. (2020). "Replicating Anomalies." *RFS* 33(5). https://theinvestmentcapm.com/uploads/1/2/2/6/122679606/houxuezhang2019rfs.pdf
31. Jensen, T., Kelly, B., & Pedersen, L.H. (2023). "Is There a Replication Crisis in Finance?" *Journal of Finance.* *(secondary summaries)*
32. Chen, A., & Zimmermann, T. "Open Source Cross-Sectional Asset Pricing" + "Publication Bias in Asset Pricing Research." https://www.openassetpricing.com/ · https://arxiv.org/pdf/2209.13623
33. Chen, A., & Velikov, M. (2022). "Zeroing In on the Expected Returns of Anomalies." *JFQA.* https://www.cambridge.org/core/services/aop-cambridge-core/content/view/945133D5A3ECEEAF466AEE91551FD225/S0022109022000874a.pdf/zeroing-in-on-the-expected-returns-of-anomalies.pdf
34. Gatev, E., Goetzmann, W., & Rouwenhorst, K.G. (2006). "Pairs Trading: Performance of a Relative-Value Arbitrage Rule." *RFS* 19(3). http://stat.wharton.upenn.edu/~steele/Courses/434/434Context/PairsTrading/PairsTradingGGR.pdf
35. Do, B., & Faff, R. (2010, 2012). "Does Simple Pairs Trading Still Work?" / "Are Pairs Trading Profits Robust to Trading Costs?" *(abstracts/secondary)* https://www.researchgate.net/publication/228259167_Are_Pairs_Trading_Profits_Robust_to_Trading_Costs

Data/tooling documentation:

36. Alpaca Market Data docs (Basic plan, history since 2016): https://docs.alpaca.markets/us/docs/about-market-data-api
37. Alpaca Historical News docs (Benzinga, 2015→, 130+/day): https://docs.alpaca.markets/us/docs/historical-news-data · gap report: https://forum.alpaca.markets/t/historical-news-data-missing-for-2016/13576
38. SEC Insider Transactions Data Sets (2006 Q1→, quarterly, free): https://www.sec.gov/data-research/sec-markets-data/insider-transactions-data-sets
39. Open Source Asset Pricing downloads: https://www.openassetpricing.com/ · https://pypi.org/project/openassetpricing/ · https://github.com/OpenSourceAP/CrossSection
40. Kenneth French Data Library (daily industry portfolios, free): https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html
41. Google Trends access status (pytrends archived 2025; official API alpha): https://apiserpent.com/blog/pytrends-dead-google-trends-data-2026 *(practitioner)*

Practitioner/vendor sources (labelled as such wherever used): Alpha Architect summaries of
Lopez-Lira & Tang and of overnight-return costs (https://alphaarchitect.com/chatgpt-forecast-stock-price/,
https://alphaarchitect.com/trading-costs-wipe-out-the-overnight-return-anomaly/), QuantSeeker
turn-of-month note, Quantpedia strategy pages, assorted blogs identified inline.
