# Progress log

A running record of what was built, what the data said, and what changed my
mind — kept honest for portfolio purposes.

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
