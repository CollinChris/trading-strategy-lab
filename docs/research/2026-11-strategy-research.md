# Strategy research: beyond intraday TA — sentiment, news, sector trends (2026-11)

**Scope.** Desk research only, no code. Question: given that nine intraday technical rules, an ML regime filter, and option-selling benchmarks all failed the lab's standard (SPY-adjusted, walk-forward, costs, day-resampled CIs, pre-committed stops), which strategy families have *published, primary-source* evidence strong enough to justify the next test?

**The decay baseline every claim below is discounted by.** McLean & Pontiff (2016, *JF*) tracked 97 published anomalies: returns fall ~26% out-of-sample and ~58% post-publication on average, with faster decay in liquid, easily-arbitraged names. Jensen, Kelly & Pedersen (2023, *JF*) find most factors replicate but shrink. So the realistic prior for any 1990s–2000s paper result, traded today in liquid US equities, is **less than half the published gross return, before costs**. Everything below applies that haircut.

---

## 1. Evidence map

### Sentiment and news

- **Firm-level news tone → next-day(s) returns.** Tetlock (2007, *JF*) showed aggregate media pessimism pressures the Dow with reversal; the tradable version is Tetlock, Saar-Tsechansky & Macskassy (2008, *JF*): the fraction of negative words in firm-specific news predicts returns over the next 1–10 days, concentrated in **negative** news and resolved mostly by the next earnings announcement — underreaction, not noise. Ke, Kelly & Xiu (2019, Chicago Booth WP) built a purpose-trained text model (SESTM) on Dow Jones Newswires: strong day-ahead predictability, but profits are earned almost entirely on **day +1**, halve with one day of delay, and are reported before costs. Lopez-Lira & Tang (2023, [arXiv:2304.07619](https://arxiv.org/abs/2304.07619)) scored headlines with ChatGPT: gross long-short Sharpe >3 in 2021–2023, **strongest in small caps and negative news** — but their own v6 (Oct 2025) documents the edge **declining as LLM adoption spreads**, and a cited decomposition has the Sharpe falling from ~6.5 (late 2021) to ~1.2 (early 2024). Verdict: the best-evidenced short-horizon signal family left, with documented, ongoing decay; the surviving slice is daily-horizon, negative-news, smaller-cap.
- **Social-media sentiment.** Bollen, Mao & Zeng (2011) — Twitter mood predicting the Dow — failed replication (Lachanski & Pav 2017, *Econ Journal Watch*); StockTwits/Twitter signals mostly proxy for retail attention and reverse. Twitter/X data is no longer free. Weak evidence, no data. Avoid.
- **Earnings-call tone.** Real effects (Loughran & McDonald 2011, *JF*; Mayew & Venkatachalam 2012, *JF*, on vocal affect), but mostly subsumed by the earnings surprise itself, and transcripts are **not free** (not on EDGAR). Avoid for this lab.
- **Analyst forecast revisions.** Gleason & Lee (2003, *TAR*): revision drift over 1–6 months, one of the stronger accounting anomalies — but it needs I/B/E/S, which is **not free**, and McLean-Pontiff decay applies. Avoid on data grounds.
- **Attention proxies (Google Trends SVI, Wikipedia views).** Da, Engelberg & Gao (2011, *JF*): attention spikes → short-term price pressure then **reversal within the year**, concentrated in small caps and IPOs. Google Trends data is resampled and inconsistent between downloads, which has broken replications. Weak, fragile. Avoid.

### Industry and sector trends

- **Industry momentum.** Moskowitz & Grinblatt (1999, *JF*): most individual-stock momentum is industry momentum; ~0.4%/mo gross at 6-month horizons. Post-publication the effect decayed with the rest of the momentum family and suffered momentum crashes (Daniel & Moskowitz 2016, *JFE*).
- **Time-series momentum.** Moskowitz, Ooi & Pedersen (2012, *JFE*): 12-month own-return sign predicts the next month across 58 futures. Huang, Li, Wang & Zhou (2020, *JFE*) show the pooled result is largely driven by the cross-asset mean and in-sample fit; per-asset evidence is weak. Applied to US sector ETFs only, expect a small, slow edge at best — but turnover is tiny, so it is one of the few families where costs don't dominate.
- **Customer–supplier lead-lag.** Cohen & Frazzini (2008, *JF*): suppliers drift after customers' news, ~1.5%/mo gross 1981–2004. Economically real (limited attention), but the linkage table requires parsing principal-customer disclosures out of 10-Ks, the effect lives in smaller suppliers, and post-publication studies show steep decay. High effort, low residual edge. Avoid for now.

### Event anomalies that fit a small daily-horizon lab

- **PEAD.** Bernard & Thomas (1989, *JAR*) is the classic; but Martineau (2022, *Critical Finance Review*, "Rest in Peace Post-Earnings Announcement Drift") shows prices now absorb earnings surprises **at the announcement** — drift has essentially vanished outside microcaps. SUE-based PEAD in a tradable universe is a dead letter; the residual, if any, is in sorting on the **announcement-day price reaction** in mid-caps.
- **Earnings-announcement premium.** Frazzini & Lamont (2007, NBER WP 13090): stocks earn abnormal returns in their announcement month/window; Barber, De George, Lehavy & Trueman (2013, *JFE*) confirm it in 46 countries — rare genuine out-of-sample evidence. Savor & Wilson (2016, *JF*) argue it is compensation for announcement risk, which means it is **earned, not free** — a crucial honesty point: a long-only announcement strategy is partly just concentrated event beta.
- **Short-term reversal.** Jegadeesh (1990, *JF*); real gross, but Avramov, Chordia & Goyal (2006, *JF*) show it lives in illiquid names and dies after costs. Avoid.
- **Overnight vs intraday decomposition.** Lou, Polk & Skouras (2019, *JFE*): strategy returns split systematically — momentum profits accrue overnight, reversal intraday. **Directly relevant diagnosis for this lab**: the lab's own v0.10 finding (longs lose intraday beyond the market) is the documented pattern, because the lab trades *only* intraday and flattens at 15:55. The equity risk premium is substantially an overnight phenomenon; an intraday-only long book is structurally fighting it. As a *harvesting* strategy (buy close/sell open daily) the two trades per day eat the edge; as a *design constraint* — let event trades hold overnight — it is free.
- **52-week-high momentum.** George & Hwang (2004, *JF*); overlaps standard momentum, monthly horizon, decayed post-publication. Nothing here the sector test doesn't cover more cheaply.
- **Pairs / stat-arb.** Gatev, Goetzmann & Rouwenhorst (2006, *RFS*): ~11%/yr 1962–2002; Do & Faff (2010 *FAJ*; 2012 *JFR*) show profits declining for decades and **roughly zero after realistic costs** post-2002. The surviving versions are high-frequency and infrastructure-heavy. Avoid.

### LLM feasibility (constraint from the brief)

Scoring the historical backlog with Claude is **not feasible**: no API key, and a 2016–2025 backfill for even 50 symbols is hundreds of thousands of Alpaca headlines. What is feasible:

1. **Backfill scoring with a free local model** — Loughran-McDonald word lists (free) and/or FinBERT — on GitHub Actions. FinBERT on a 4-core CPU runs ~20–50 headlines/s; ~500k headlines ≈ 3–7 core-hours, trivially sharded across workflow jobs.
2. **Claude as calibrator, not scorer**: label ~2–3k sampled headlines interactively in Claude Code sessions to build a validation set; measure FinBERT/lexicon agreement against it and against LLT's published prompt. If the cheap scorer agrees ≥80% on direction, use it everywhere.
3. **Live scoring** is tens of headlines/day for a 30–50 name universe — the local model handles it inside the existing scan workflow.

---

## 2. Ranked shortlist — three testable ideas

### #1 — Overnight news-drift: daily-horizon headline-tone long/short

**Mechanism.** Investors underreact to firm-specific news, especially negative news; prices drift for 1–3 days (Tetlock et al. 2008; Ke-Kelly-Xiu 2019; Lopez-Lira & Tang 2023). This is also the honest successor to the lab's failed "news momentum" rule, which used headline *timing* but never *content*.

**Evidence quality.** The strongest of any family in scope: three independent methodologies (word counts, supervised text model, LLM) across different corpora and decades agree on sign, horizon, and the negative-news asymmetry. Decay is documented and accelerating (LLT v6, 2025); Ke-Kelly-Xiu show the profit is gone if you trade a day late.

**Realistic market-adjusted edge after costs.** Published gross figures (Sharpe 3+) are small-cap-heavy and cost-free. For a liquid, shortable mid/large-cap universe at next-day horizon, with 5 bps slippage each way plus the SPY hedge's costs: **0–5 bps/day on traded capital, concentrated in the short/avoid side of negative news**. It is entirely plausible the lab measures zero; that is a publishable finding for the lab either way.

**Data.** All free: Alpaca news (2015+, timestamped), Alpaca daily and 5-min bars (SIP, 2016+), scoring per the LLM-feasibility plan above.

**Test design.** Universe: top ~50 liquid Alpaca-shortable names (price > $10). Signal: net headline tone over the prior 24 h ending 15:45 ET; enter at 15:50 close (long top tone, short bottom tone, skip no-news), exit next day 15:50 — so the position holds **overnight**, where Lou-Polk-Skouras say drift lives. Score every position SPY-adjusted with the existing `market.py` hedge over the same window. Backtest 2016–2025 walk-forward: any threshold/calibration chosen only on years before the year being scored. Costs: 5 bps per side plus hedge slippage, as now. **Pre-committed rule:** proceed to paper only if the walk-forward SPY-adjusted mean is positive with a day-resampled 95% CI above zero over 2021–2025 (the LLM-era, post-decay subsample — earlier years flatter the signal); in paper, the existing gate (≥100 adjusted trades, CI > 0, by a fixed date two quarters out).

**Main failure mode.** Staleness: Benzinga-feed timestamps can lag the primary source, so the measured "drift" may be pre-priced by the time the headline arrives — this exact failure killed Ke-Kelly-Xiu's delayed portfolios. Second: short-side alpha that Alpaca paper fills grant but real borrow would not. Mitigation: log signal-to-entry lag; report long and short books separately.

### #2 — Earnings-event suite: announcement premium + reaction-sorted drift

**Mechanism.** Two distinct effects on one free calendar. (a) Stocks earn a premium through their own announcement window — compensation for bearing announcement risk (Frazzini & Lamont 2007; Barber et al. 2013; Savor & Wilson 2016). (b) What drift remains post-Martineau is captured by the **announcement-day market-adjusted return**, not by SUE: buy (short) names that jumped (fell) on announcement day, hold 5–10 days.

**Evidence quality.** Announcement premium: strong, with genuine international out-of-sample confirmation; but partly risk, not mispricing, so expect it to look like beta the SPY hedge removes — which is exactly what the lab should want to measure. Reaction-sorted drift: moderate; Martineau's evidence says the SUE version is dead in large caps, so this is a test of the residual in mid-caps.

**Realistic edge after costs.** Announcement premium: 10–40 bps per event gross historically; after the beta-hedge, plausibly near zero — Savor-Wilson predicts most of it is hedged away. Reaction drift: 20–60 bps per event gross in mid-caps, fading toward zero in the largest names. Honest expectation: **one of the two survives adjustment, weakly, or neither**.

**Data.** Free: earnings timestamps from SEC EDGAR 8-K Item 2.02 acceptance times (classifies before-open vs after-close precisely); daily bars from Alpaca; no transcripts or I/B/E/S needed.

**Test design.** All US names in the Alpaca universe above $5 with EDGAR-dated announcements, ~4,000 events/quarter — sample size is this idea's great virtue. (a) Long each announcer from close T−1 to close T+1, SPY-hedged (hedge held overnight; paper supports it). (b) Sort events by day-0 SPY-adjusted return; long top decile / short bottom decile from close T+1 to close T+6. Walk-forward by year 2016–2025; day-resampled CIs; verdicts split by market-cap tercile. **Pre-committed rule:** each leg needs a 2021–2025 walk-forward adjusted CI above zero to graduate to paper; the lab's standing 100-trade paper gate thereafter.

**Main failure mode.** (a) is risk premium in disguise: a positive raw mean that vanishes under the hedge — report it, don't rationalize it. (b) earnings gaps are discontinuous: stops don't protect across the gap, and single-event tails are fat; cap per-event risk and resample by *event date*, not just trading day.

### #3 — Sector time-series momentum on ETFs (monthly, beta-hedged)

**Mechanism.** Slow-moving sector trends from gradual information diffusion and flows (Moskowitz & Grinblatt 1999; Moskowitz, Ooi & Pedersen 2012): hold sector ETFs whose trailing 12-1 month return is positive / above the cross-sector median, hedge the book's beta with SPY.

**Evidence quality.** Long histories, many asset classes — but Huang et al. (2020) undercut the per-asset statistics, momentum decayed post-publication, and crashes (Daniel & Moskowitz 2016) are documented. Ranked third because the *residual* market-adjusted edge is likely ≤2%/yr — real evidence, modest expectation.

**Realistic edge after costs.** Gross TSMOM-on-equity-sectors ≈ 2–4%/yr historically; after decay haircut and beta-hedging, **0–2%/yr**. Costs are negligible (monthly turnover on penny-spread ETFs), which is why a small edge can still survive here when it can't intraday.

**Data.** Free: SPDR sector ETFs (XLE, XLF, XLK, …) daily since 1998 via yfinance; Cboe/FRED for regime context; Alpaca trades them.

**Test design.** This idea **cannot be validated by paper trading** on any reasonable clock — a monthly strategy yields ~12 observations/year, so the lab's CI gate would take decades. Test it entirely in the history-study backtest: 1998–2025, expanding-window walk-forward for any parameter (lookback, cutoff), 5 bps costs, SPY-beta-hedged monthly returns, bootstrap by month. **Pre-committed rule:** require hedged alpha t ≥ 2 over the full sample *and* positive hedged mean in 2013–2025 standalone; otherwise record the negative and stop. Paper trading it is then only an execution check, not evidence.

**Main failure mode.** Statistical power and crowding: with ~330 monthly observations, a true 1.5%/yr alpha may be undetectable (t < 2) — pre-commit to treating "underpowered" as "not proven", not as license to keep tweaking. And TSMOM's worst drawdowns come exactly at market turns, when the beta-hedge is least accurate.

---

## 3. Promising-sounding but avoid

- **Social-media sentiment** — foundational paper failed replication (Lachanski & Pav 2017); free data no longer exists.
- **Google Trends / Wikipedia attention** — price-pressure-then-reversal in small caps (Da et al. 2011); Trends resampling makes results irreproducible.
- **Earnings-call tone / analyst revisions** — real literature, but transcripts and I/B/E/S aren't free; revisions decayed per McLean-Pontiff.
- **SUE-based PEAD in large caps** — Martineau (2022): the drift is gone where the lab can trade.
- **Pairs / stat-arb** — profits ≈ zero after costs since the 2000s (Do & Faff 2012); surviving versions need infrastructure the lab doesn't have.
- **Short-term reversal, weekly** — turnover eats it outside illiquid names (Avramov et al. 2006).
- **Overnight-drift harvesting (buy close / sell open daily)** — two trades/day on a few-bps effect; the right use is holding event trades overnight, as in #1 and #2.
- **Customer–supplier lead-lag** — genuine mechanism, but 10-K linkage parsing is a project in itself for a post-decay edge in small caps.
- **52-week-high momentum** — subsumed by the sector/momentum test at lower cost.
- **LLM-scores-everything** — infeasible without an API key, and the published LLM edge is already decaying as adoption spreads (LLT v6).

## 4. Bottom line

Honest answer: **the realistic probability that this lab finds a durable, SPY-adjusted, after-cost edge is low — well under 50% — but it is not zero, and the three tests above are where the remaining probability mass sits.** The published record says short-horizon alpha in liquid US equities is the most heavily arbitraged territory in finance, post-publication decay averages ~58%, and the one family with recent headline-grabbing results (LLM news scoring) is visibly decaying in its own authors' updates. What distinguishes the shortlist is not that the edges are large but that (i) each has multi-paper, multi-method evidence rather than one backtest, (ii) each is measurable with the lab's free data at sample sizes the lab's CI standard can actually resolve (thousands of events for #1–#2), and (iii) each moves off the intraday battleground — toward overnight and multi-day horizons — where the lab's own v0.10 result and Lou-Polk-Skouras agree returns actually accrue. The most valuable likely outcome remains a clean, market-adjusted *null* measured to tight confidence intervals; the lab should size its expectations, and its pre-committed stop rules, accordingly.

---

### Key references

Tetlock (2007) *JF*; Tetlock, Saar-Tsechansky & Macskassy (2008) *JF*; Ke, Kelly & Xiu (2019) Chicago Booth WP; Lopez-Lira & Tang (2023–25) [arXiv:2304.07619](https://arxiv.org/abs/2304.07619); Lachanski & Pav (2017) *Econ Journal Watch*; Da, Engelberg & Gao (2011) *JF*; Loughran & McDonald (2011) *JF*; Gleason & Lee (2003) *TAR*; Moskowitz & Grinblatt (1999) *JF*; Moskowitz, Ooi & Pedersen (2012) *JFE*; Huang, Li, Wang & Zhou (2020) *JFE*; Daniel & Moskowitz (2016) *JFE*; Cohen & Frazzini (2008) *JF*; Bernard & Thomas (1989) *JAR*; Martineau (2022) *Critical Finance Review*; Frazzini & Lamont (2007) NBER WP 13090; Barber, De George, Lehavy & Trueman (2013) *JFE*; Savor & Wilson (2016) *JF*; Jegadeesh (1990) *JF*; Avramov, Chordia & Goyal (2006) *JF*; [Lou, Polk & Skouras (2019) *JFE*](https://personal.lse.ac.uk/polk/research/TugOfWar.pdf); George & Hwang (2004) *JF*; Gatev, Goetzmann & Rouwenhorst (2006) *RFS*; Do & Faff (2010 *FAJ*, 2012 *JFR*); McLean & Pontiff (2016) *JF*; Jensen, Kelly & Pedersen (2023) *JF*.
