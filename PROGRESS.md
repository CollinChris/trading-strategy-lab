# Progress log

A running record of what was built, what the data said, and what changed my
mind — kept honest for portfolio purposes.

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
