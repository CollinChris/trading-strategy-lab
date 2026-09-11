# Session checkpoint — 2026-09-11

Resume point for future working sessions (human or AI). Read this file, then
[PROGRESS.md](PROGRESS.md) for the full story, then `results/` for the data.

## Where the project stands

**v0.7 built (uncommitted at time of writing — check `git status`).** Since
v0.3: weekly tune workflow + tuning history (v0.4), tuned parameters traded as
live `<name>_tuned` A/B variants (v0.5), long **and** short on every strategy
(v0.6), **walk-forward regime filters** (v0.7, `trading-lab regime` →
`results/REGIME.md` + `regime_oos.png`; `src/trading_lab/regime.py`,
`tests/test_regime.py`; scikit-learn added), and the filter **trading live as
`<name>_regime` variants** (v0.8: `results/regime_model.joblib` loaded by
`paper.py`; `regime_ev` on every journal row; Saturday workflow now runs
tune → backtest → regime and commits all three). Everything below is live:

- **8 strategies** in `src/trading_lab/strategies/`: Gap & Go, ORB, VWAP
  Pullback, EMA 9/20, RSI(2) Reversion, News Momentum (Alpaca news API),
  Squeeze Breakout, High-Break ATR Trail (trailing stop).
- **Backtest engine** (`backtest.py`): no-lookahead (next-bar fills,
  stop-before-target, EOD flatten), slippage, trailing stops, and a
  market-condition snapshot on every trade (gap, VWAP dist, rel volume, SPY,
  hour, weekday).
- **Paper trading is LIVE on GitHub Actions** (first-ever session: Mon
  2026-08-24, 9:30pm SGT). Scans every 10 min 13–19 UTC weekdays; flatten
  19:55 & 20:55 UTC; nightly journal at 21:30 UTC commits real fills to
  `results/paper_journal.csv`. Verified green via workflow_dispatch.
- **Tuning harness** (`tune.py`): grid search on first 60% of sessions,
  validated on held-out 40%, objective = expectancy (never win rate).
- 55 tests; new code ruff + black clean (three pre-existing ruff nits remain in
  older test files); uv-managed.

## The scoreboard (do not re-litigate — it's measured)

- Full 60-day window: only News Momentum has PF > 1 (+$1.62/trade, n=30) —
  **but** its profit lives entirely in the train period; on the held-out final
  month it loses −$20.45/trade. Tuned version overfit worst of all
  (+$42 train → −$24 test).
- Every strategy is negative in the held-out month regardless of parameters →
  **regime problem, not parameter problem**.
- Win rate ranks strategies nearly opposite to profitability (RSI(2): best win
  rate, worst expectancy). Optimize expectancy/profit factor only.
- **Regime filters (v0.7):** best filter (gradient boosting on P&L) lifts OOS
  expectancy −$13.03 → −$4.82/trade, 92nd percentile vs same-size random
  selection — suggestive, still negative, gate still unmet. P(win) classifiers
  were *worse than random* (win-rate trap at the model level) — never filter on
  P(win) again; predict P&L. Filter mostly switches EMA/news/squeeze off.

## Credentials & operational facts

- Alpaca **paper** keys: local `.env` (gitignored) + GitHub Actions secrets
  `ALPACA_API_KEY` / `ALPACA_SECRET_KEY`. Never commit them; regenerating on
  the Alpaca dashboard kills old keys (then re-run `gh secret set …`).
- Owner is in Singapore: US market = 9:30pm–4am SGT. All code date-logic must
  use `market_today()` / `MARKET_TZ` (America/New_York), never `date.today()`.
- **November DST**: when the US switches to EST, shift scan + journal cron
  hours in `.github/workflows/*.yml` by +1 (flatten already has its backup run).
- yfinance caps 5m history at 60d; news fetch window is bars-window + 35d
  buffer. Data caches in `data/` (gitignored) are same-day only; safe to delete.
- "[already today]" in scan logs = stateless dedup working (deterministic
  `client_order_id` = `strategy--symbol--date`), not an error.

## Next steps (in order)

1. **Let the paper loop run 1–2 weeks.** Each morning (SGT): repo → Actions
   tab; journal rows accumulate in `results/paper_journal.csv`.
2. **Compare paper fills vs backtest assumptions** (slippage, stop behavior)
   once ~50 paper trades exist.
3. **Commit v0.7/v0.8** if not yet done (`git status`). The live `_regime` path
   has NOT yet been exercised in a real market session (built outside US hours;
   `--dry-run` only reached the entry-window guard). First trading night: check
   the scan logs for `regime filter: hgb_reg fitted …`, `[regime skip]` lines,
   and `_regime` submissions; next morning check `regime_ev` populated in the
   journal. Debug there before trusting the variant's book.
4. **Judge the regime book** once ~100 `_regime` fills exist: `_regime` vs base
   expectancy, and base rows split by `regime_ev` sign.
4b. **Learning curve says: more sessions.** Filter was noise at 10–30 training
   sessions, +$32/trade at 40 (fixed test set). Alpaca minute history (step 5)
   is now the highest-value data step; re-run `trading-lab regime` on it.
5. Longer history + true small-cap gappers via Alpaca historical minute data
   (Gap & Go is untestable on mega caps — 4 trades in 60d).
6. Candidate for deletion: Squeeze Breakout (PF 0.34; worst of the eight).

## Standing rules

- **Real money is gated**: paper is the data-collection lab; nothing goes live
  without sustained positive out-of-sample AND paper expectancy. (Owner's rule,
  2026-08-23.)
- Every claim in README/PROGRESS stays honest — negative results are findings.
- This is also a portfolio piece: keep README numbers current and PROGRESS.md
  narrated after each milestone.

## Resuming with Claude

Open a session in this repo and say: *"Read CHECKPOINT.md and PROGRESS.md,
check the latest Actions runs and results/paper_journal.csv, and pick up from
the next steps."* Useful first commands: `gh run list --limit 10`,
`uv run trading-lab paper --status`, `uv run pytest -q`.
