# Progress log

A running record of what was built, what the data said, and what changed my
mind — kept honest for portfolio purposes.

## 2026-09-11 — v0.7/v0.8: regime filters, walk-forward, the win-rate trap again — then live

**Goal.** v0.2 ended with "regime problem, not parameter problem": every strategy
lost in the held-out month whatever its stops. The journal has recorded market
conditions at entry since v0.3, so the question was finally testable — can a
model learn *when* each strategy pays, and does that survive out of sample?

**Built.** `trading-lab regime`: a pooled model over the 3,092 backtest trades
(conditions + strategy + side; SPY move, trend slope, VWAP distance and
open→entry move are signed by trade direction so a short in a falling tape and
a long in a rising one read as the same regime). Four model kinds — two P(win)
classifiers converted to dollars with the training fold's average win/loss,
two P&L regressors. **Walk-forward validation** replaces the single split: 20
train-only sessions, then 5-session blocks each scored by a model trained only
on earlier sessions (8 folds, 40 OOS sessions). Every filter is scored against
2,000 random subsets of the same size — the honest baseline for "dropping
trades helped." Eleven tests, including a planted-regime dataset the filter
must find and a noise dataset it must not claim.

**Result: suggestive, not established.**

- The gradient-boosted P&L regressor keeps 295 of 2,063 OOS trades and lifts
  expectancy from **−$13.03 to −$4.82/trade** (PF 0.70 → 0.87), at the **92nd
  percentile** of same-size random selections. Its predicted-EV quintiles are
  monotonic out of sample (−$20.36 → −$3.52/trade; 34% → 46% win rate). Real
  signal — but the top quintile still loses, and 92nd is not 99th.
- **The win-rate trap came back wearing a model.** Both P(win) classifiers had
  OOS AUC ≈ 0.55 — mildly predictive — and the gradient-boosted one *underperformed
  random selection* (−$22.96/trade, 3rd percentile). The trades it rated most
  likely to win were those that won small and lost big, exactly v0.1's finding
  about RSI(2) at the strategy level. Regressing P&L directly fixed it. First
  run took an hour to build and ten minutes to disbelieve; the calibration table
  now lives in the report so the next model can't hide it.
- **What the filter actually does is switch strategies off.** Zero EMA, news, or
  squeeze trades survive out of sample; ORB's survivors turn +$17.32/trade (PF
  1.19, n=31); AR Forecast goes to breakeven. The most important features are
  direction-signed trend slope, overnight gap, and the open→entry move.
- **Paper fills point the same way, on 15 trades.** A filter fitted only on
  sessions before 2026-08-24 kept 15 of the 159 real paper fills since; they
  averaged +$118.91 vs −$25.86 for the whole book. Logged as a direction check.

**Is it data-starved? Measured, same day.** Holding the test set fixed to the
last 20 sessions and varying the training window: 10, 20, and 30 sessions of
history gave filters no better than random (31st, 17th, 49th percentile); 40
sessions gave **+$32.47/trade kept** at the 100th percentile. Trades within a
session share the tape (session-mean P&L varies ~60% more than independence
would allow), so the effective sample is ~60 sessions, not 3,092 trades. One
point on a steep curve — but it says the constraint is *sessions*, and the paper
loop at ~50 fills/week won't supply them; Alpaca's minute history can.

**Then live (v0.8, same day).** The filter is now a live A/B like the tuned
variants: `trading-lab regime` saves the primary model fitted on all sessions
(`results/regime_model.joblib`); the scanner scores every default strategy's
signal with it and places a second order tagged `<name>_regime` only when the
predicted EV is positive; the nightly journal stamps every row with
`regime_ev`; and the Saturday workflow refreshes the backtest, re-runs the
walk-forward report, and re-fits the model as the 60-day window rolls. Four
more tests (variant naming, single-signal scoring equals batch scoring, planted
regime ranks aligned signals higher, model save/load). The judgement comes
when ~100 `_regime` fills exist. Full tables: [results/REGIME.md](results/REGIME.md).

## 2026-08-23 — v0.3: news strategy goes live, automation, and the journal

**Built.** Three new strategies — **News Momentum** (fresh Alpaca-API headline
+ breakout confirmation), **Squeeze Breakout** (Bollinger contraction →
expansion), and **High-Break ATR Trail** (the roadmap's trailing-stop
experiment) — plus engine support for trailing stops. Every trade now records
a **market-condition snapshot at entry** (gap %, open→entry move, VWAP
distance, relative volume, SPY context, hour, weekday): the tuning dataset the
next phase will learn regime filters from. And the loop is now unattended:
GitHub Actions scan every 10 minutes of the US session, flatten at 15:55 ET,
and commit each day's actual paper fills to `results/paper_journal.csv`
overnight.

**First 8-strategy run (1,391 trades).**

- **News Momentum is the first strategy in the lab above water**: profit
  factor 1.04, expectancy **+$1.62/trade** (30 trades). Honesty required on
  two counts: 30 trades is a small sample, and this is the full window — the
  out-of-sample check comes from the tuner and, more importantly, from live
  paper fills accumulating in the journal.
- **The trailing stop beat most fixed targets**: High-Break ATR Trail's
  average win is 1.5× its average loss (PF 0.89) — better than three of the
  four original fixed-2R momentum setups. Exits matter more than entries here.
- **Squeeze Breakout flopped** (PF 0.34, −$35.5/trade): on liquid mega caps,
  intraday band squeezes appear to resolve as chop, not expansion. Candidate
  for deletion rather than tuning.
- A data lesson: the first news run silently covered only two-thirds of the
  price window, quietly starving the news strategy of a month of signals —
  found by cross-checking date ranges, fixed by widening the fetch window.

**The out-of-sample verdict (same day, worth its own paragraph).** The tuner's
train/test split killed the celebration: News Momentum's full-window profit
lives entirely in the first 36 sessions. On the held-out final month it loses
−$20.45/trade with default parameters, and its *tuned* parameters produced the
lab's worst overfit yet (+$42.15 train → −$23.89 test). High-Break ATR Trail
told the same story in miniature (+$17.22 → −$9.90). Eight strategies, ~93
parameter sets, one conclusion twice confirmed: on this universe and window,
parameter search finds memories, not edges — and every strategy bleeds in the
same held-out month, which is regime information, not strategy information.

**Next.** Let the paper loop and journal run for a couple of weeks to
accumulate genuinely unseen trades; then mine the journal's condition columns
for regime filters — the data now says *when* you trade matters more than
*what* you tweak.

## 2026-08-23 — v0.2: parameter tuning, and the overfitting lesson

**Goal.** v0.1's numbers were all negative, so before anything touches paper
trading I set a hard gate: *a configuration must show positive expectancy on
data it wasn't optimized on.* Built `trading-lab tune`: every strategy's stops,
targets, and entry thresholds parameterized (~75 combinations), grid-searched
by expectancy per trade on the first 36 sessions, winners re-run on the 24
held-out sessions alongside the untuned defaults.

**Result: the gate is unmet — and the failure mode is the education.**

- ORB's best training parameters earned **+$28.35/trade** in-sample and lost
  **−$18.78/trade** out-of-sample. That 47-dollar swing is what memorizing 36
  sessions looks like.
- In 3 of 4 tunable strategies the tuned parameters did *worse* on the test
  window than the defaults they were supposed to improve.
- All four test expectancies clustered between −$10 and −$19 no matter the
  parameters — the held-out month (Jul 21–Aug 21) was hostile to long-only
  intraday on this universe, full stop. You can't stop-loss your way out of
  the wrong regime.
- Gap & Go stayed untunable: even at a 1% gap threshold, mega caps produced
  too few qualifying days to evaluate honestly.

**What changes next.** One train/test split is itself a small sample, so the
next methodological step is walk-forward validation (rolling folds). After
that, the more promising lever is *when to trade* rather than *how to exit*:
regime filters (trend/volatility gates) attack the clustered losses directly,
where stop tweaking demonstrably didn't. Details: [results/TUNING.md](results/TUNING.md).

## 2026-08-23 — v0.1: five strategies, engine, first baseline

**Built.** Researched the most commonly taught day-trading setups (Warrior
Trading's Gap & Go / VWAP plays, plus the ORB, EMA-crossover, and RSI(2)
classics) and implemented all five from their textbook rules. Wrote an
event-driven backtest engine with a strict no-lookahead execution model
(signals on completed bars fill at the next open; stop-before-target when a
bar spans both; causal indicators verified by test), per-strategy metrics, a
results generator, and an Alpaca paper-trading executor with `--dry-run`,
`--status`, and `--flatten`. 15 tests across engine, indicators, and signals.

**First run.** 6 symbols × ~40 sessions × 5-minute bars → 1,065 trades.
Every strategy finished negative after 5 bps/side slippage. Best win rate:
RSI(2) Reversion at 52% — with the worst expectancy (−$10.87/trade), because
its average loss is twice its average win. Best profit factor: Opening Range
Breakout at 0.96, nearly breakeven. Full numbers in
[results/RESULTS.md](results/RESULTS.md).

**What I learned.**

- *Win rate was the wrong question.* I started this project asking "which
  strategy has the highest win rate?" — the very first run showed win rate and
  profitability ranking strategies in nearly opposite order. Expectancy and
  profit factor are the metrics I'll optimize against from here.
- *A filter that never fires is a finding.* Gap & Go took 4 trades in 40
  sessions: 2%+ overnight gaps barely exist on mega caps. The strategy's
  natural habitat (low-float small caps) needs paid/richer data — parked on the
  roadmap rather than faked.
- *Timezones are a correctness bug, not a style nit.* Running from Singapore,
  `date.today()` disagrees with the US market date for half the trading day;
  a lint rule (flagging naive datetimes) caught what would have made the paper
  scanner silently skip live sessions. All dates now flow through
  `market_today()` in America/New_York.

**Next.** Get Alpaca paper keys, cron the scanner + EOD flatten through a full
week, and compare paper fills against the backtest's assumptions before any
parameter tuning.
