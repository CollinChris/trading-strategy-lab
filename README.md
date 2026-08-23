# Trading Strategy Lab

Five popular day-trading strategies, implemented from their textbook rules and
raced against each other on identical data, identical costs, and identical
risk sizing — then paper-traded via the Alpaca API. The point is to measure,
not to believe: which of the setups people actually teach survives contact
with out-of-sample data?

## Current verdict (60 days, 5-minute bars, v0.1 untuned rules)

| Strategy | Trades | Win rate | Profit factor | Expectancy/trade | Total P&L |
|---|---|---|---|---|---|
| RSI(2) Reversion | 396 | **52.0%** | 0.53 | −$10.87 | −$4,304 |
| Gap & Go | 4 | 50.0% | 0.87 | −$22.14 | −$89 |
| Opening Range Breakout | 179 | 46.9% | **0.96** | −$3.47 | −$621 |
| VWAP Pullback | 246 | 34.6% | 0.75 | −$14.33 | −$3,524 |
| EMA 9/20 Crossover | 240 | 27.5% | 0.62 | −$15.14 | −$3,633 |

![Cumulative P&L by strategy](results/equity_curves.png)

**The honest headline: every strategy lost money in this window.** That is the
expected result for untuned textbook rules on liquid large caps after slippage —
and it's the whole reason to test before trading. Two early lessons the data
already teaches:

1. **Win rate is not profitability.** The "best" strategy by win rate (RSI(2),
   52%) has the *worst* expectancy — its average loss is twice its average win.
   Ranking by profit factor instead puts Opening Range Breakout on top (0.96,
   nearly breakeven).
2. **Sample size gates every conclusion.** Gap & Go looks harmless at −$89, but
   four trades is noise, not evidence — its 2% gap filter almost never fires on
   mega caps, which is itself a finding: the strategy's edge (if any) lives in
   the low-float small caps it was designed for.

Full metrics, exit-reason breakdown, and the trade-by-trade log:
[results/RESULTS.md](results/RESULTS.md).

## Tuning (v0.2): can stops and targets fix it?

Short answer so far: **no — and the way it fails is the lesson.** A grid search
over each strategy's stop placement, profit targets, and entry thresholds
(~75 parameter sets), optimized by expectancy on the first 36 sessions and
validated on 24 held-out sessions:

![Train vs test expectancy](results/tuning_shrinkage.png)

- The star of the training window (ORB at **+$28/trade**) lost **−$19/trade**
  on data it hadn't seen — the grid search memorized the past, it didn't find
  an edge.
- In 3 of 4 tunable strategies, the "optimal" parameters did *worse* out-of-
  sample than the untuned defaults.
- Every test-window expectancy landed between −$10 and −$19 regardless of
  parameters: the held-out month was simply hostile to long-only intraday on
  this universe, which is a regime problem no stop-loss setting can tune away.
- Gap & Go couldn't be tuned at all — even at a 1% gap threshold it produced
  too few trades on mega caps to evaluate honestly.

Full table: [results/TUNING.md](results/TUNING.md).

**Project rule:** nothing goes to live paper trading until a configuration
shows **positive out-of-sample expectancy**. That gate is currently unmet.

## The five strategies

| Strategy | Style | Rule sketch |
|---|---|---|
| **Gap & Go** | Momentum (Ross Cameron's signature) | Day gaps up ≥2%; buy break of opening-bar high on volume; stop = opening low; 2R target |
| **Opening Range Breakout** | Momentum | Buy first close above the 15-minute opening range; stop = range low; 2R target |
| **VWAP Pullback** | Momentum continuation (Warrior-Trading style) | Green day tags session VWAP and holds; buy the bounce confirmation; stop under VWAP; 2R target |
| **EMA 9/20 Crossover** | Trend following | Buy 9-EMA crossing above 20-EMA while above VWAP; exit on cross-down; stop = 5-bar low |
| **RSI(2) Reversion** | Mean reversion (Connors-style, intraday) | Buy RSI(2) < 10 dips while above VWAP; exit RSI(2) > 60; 1% stop |
| **News Momentum** | Catalyst momentum | Fresh headline (≤45 min, via Alpaca's news API) + breakout of prior bar high on 1.5× volume above VWAP; stop = 3-bar low; 2R target |
| **Squeeze Breakout** | Volatility expansion | Bollinger bandwidth at its tightest of the last hour, then first close above the upper band; stop = middle band; 2R target |
| **High-Break ATR Trail** | Momentum, trailing exit | Break of the first-hour high above VWAP; no fixed target — stop trails the high by 2×ATR so winners run |

All long-only, max 1–3 trades per symbol per day, everything flat by 15:55 ET.

## How it works

```
yfinance 5m bars + Alpaca news ──▶ strategies (signals on completed bars)
                                      │
                                      ▼
             event-driven backtest engine ──▶ metrics ──▶ results/RESULTS.md + chart
                                      │            └──▶ per-trade journal w/ market conditions
                                      ▼ (same Strategy classes, live bars)
             Alpaca paper executor (bracket orders, GitHub Actions cron)
                                      │
                                      ▼ nightly
             results/paper_journal.csv — real fills + conditions, committed back
```

The engine is deliberately paranoid about **lookahead bias**:

- signals are evaluated on *completed* bars and fill at the *next* bar's open;
- stops/targets are monitored intra-bar; when one bar spans both, the **stop is
  assumed to hit first** (conservative);
- indicators are causal (value at bar *i* uses only bars ≤ *i*), verified by test;
- 5 bps slippage is charged on every fill, both sides.

## Usage

```bash
uv sync
uv run trading-lab backtest                    # writes results/ (table, chart, trade log)
uv run trading-lab backtest --symbols TSLA AMD # custom universe
uv run trading-lab tune                        # grid-search params on a train split,
                                               #   validate held-out → results/TUNING.md
uv run pytest                                  # 15 tests: engine, indicators, signals
```

### Paper trading (stage 2)

Create a free account at [alpaca.markets](https://alpaca.markets), generate
**paper** keys, and `cp .env.example .env`:

```bash
uv run trading-lab paper --dry-run   # show what would be ordered, submit nothing
uv run trading-lab paper             # submit bracket orders to the paper account
uv run trading-lab paper --status    # open positions
uv run trading-lab paper --flatten   # EOD discipline: close everything (~15:55 ET)
uv run trading-lab journal           # append today's fills to results/paper_journal.csv
```

The scanner runs once and exits (cron it during US market hours). One paper
trade per strategy+symbol per day; dynamic-exit strategies run stop-only
brackets and rely on `--flatten` for the end-of-day exit.

## User guide — the automated loop

Once the repo has `ALPACA_API_KEY` / `ALPACA_SECRET_KEY` as Actions secrets,
three GitHub Actions workflows run the whole loop unattended. No machine needs
to be on.

### What runs, and when

| Workflow | Cron (UTC) | US market time | Singapore time | What it does |
|---|---|---|---|---|
| `paper-scan` | every 10 min, 13:00–19:59 Mon–Fri | 9:00am–3:59pm ET | 9:00pm–3:59am | Checks the latest completed 5-min bar for all 8 strategies × 6 symbols; fires bracket orders (entry + stop + target) at the paper account. Scans outside the 09:35–15:30 ET entry window exit immediately without trading. |
| `paper-flatten` | 19:55 & 20:55 Mon–Fri | 3:55pm ET (+ EST-season backup) | 3:55am / 4:55am | Closes every open paper position and cancels open orders — day-trading discipline, nothing held overnight. |
| `paper-journal` | 21:30 Mon–Fri | 5:30pm ET | 5:30am | Pulls the day's actual fills from Alpaca, computes the market conditions at each entry, appends rows to `results/paper_journal.csv`, and **commits the file back to the repo**. |

So each weekday: up to ~42 scans, one flatten, one journal commit. GitHub's
cron is UTC and ignores US daylight saving — **in November, shift the scan and
journal hours in `.github/workflows/*.yml` by +1** (the flatten workflow
already has its EST backup run built in).

### What updates automatically vs manually

**Automatic (no action needed):**
- `results/paper_journal.csv` — grows by one commit per trading day (only when
  there were fills; zero-trade days commit nothing).
- **Run logs** — every workflow run (each scan included) keeps its full console
  log in the repo's **Actions tab** for ~90 days: which signals fired, which
  orders were submitted, "[already today]" dedup notices, errors.
- Positions, orders, and P&L — live on the
  [Alpaca paper dashboard](https://app.alpaca.markets) at any moment.

**Manual (run when you want fresh analysis):**
- `uv run trading-lab backtest` — regenerates `results/RESULTS.md`, the equity
  chart, and `results/trades.csv`. Not on a schedule; run it after changing
  strategies or when you want the window refreshed, then commit.
- `uv run trading-lab tune` — regenerates `results/TUNING.md`. Same deal.

### Watching it work

- **Browser:** repo → **Actions** tab → pick a workflow → open any run.
- **Terminal:** `gh run list --limit 10` for recent runs,
  `gh run watch` to follow one live,
  `gh workflow run paper-scan.yml` to trigger a scan manually right now.
- First thing tomorrow (SGT): check the Actions tab over breakfast — the
  overnight session's scans, the 3:55am flatten, and the 5:30am journal commit
  will all be there.

### Pausing, resuming, changing things

- **Pause everything:** `gh workflow disable paper-scan.yml` (repeat for
  `paper-flatten.yml` / `paper-journal.yml`), or the "…" menu on the workflow
  page. `enable` to resume. Disable the scanner but keep flatten enabled if
  positions might still be open.
- **Change the universe:** edit `DEFAULT_SYMBOLS` in `src/trading_lab/config.py`.
- **Change sizing/slippage/cutoffs:** same file (`Config`).
- **Change scan frequency:** the cron line in `paper-scan.yml` (don't go below
  every 5 min — that's the bar size).
- **Rotate keys:** regenerate on the Alpaca dashboard, then
  `gh secret set ALPACA_API_KEY` / `ALPACA_SECRET_KEY` and update local `.env`.

### Safety & troubleshooting

- Duplicate protection is stateless: the deterministic `client_order_id`
  (`strategy--symbol--date`) means Alpaca itself rejects a same-day
  resubmission — "[already today]" in scan logs is normal, not an error.
- Every order is a **paper** order: `paper=True` is hard-coded and these keys
  only work against the paper API. Real money would require live keys, which
  this project deliberately never uses (see the roadmap gate).
- A scan that logs "outside the entry window" or "market closed? skipping" did
  its job — those are the guards working.
- If a workflow suddenly fails on every run: check whether the Alpaca keys were
  regenerated (old secrets die the moment new keys are made).

### The trade journal (the tuning dataset)

Every trade — backtest (`results/trades.csv`) and paper
(`results/paper_journal.csv`) — records the market conditions at entry:

`mkt_gap_pct` (overnight gap) · `mkt_change_open_pct` (session open→entry) ·
`mkt_dist_vwap_pct` (entry vs VWAP) · `mkt_rel_volume` (signal-bar volume vs
day average) · `mkt_spy_change_pct` (what the index was doing) · `hour_et` ·
`weekday`

That's the raw material for the next phase: instead of asking "which stop is
best?", ask "under which conditions does this strategy win at all?" — regime
filters learned from the journal.

## Methodology & limitations (read before believing any number)

- **60-day sample, one market regime.** yfinance caps 5-minute history at 60
  calendar days (~40 sessions). Nothing here is statistically settled.
- **Universe mismatch, by necessity.** Warrior-Trading-style trading lives on
  low-float small-cap gappers with news catalysts; free historical data can't
  screen those, so the lab runs on liquid large caps (TSLA, NVDA, AMD, PLTR,
  COIN, MSTR). Gap & Go in particular is handicapped by this.
- **v0.1 is intentionally untuned.** These are the textbook rules as commonly
  taught, not optimized parameters — the next milestone is honest tuning with
  in-sample/out-of-sample splits, so the baseline had to be recorded first.
- Long-only; no commissions (slippage only); intra-bar fills approximated from
  bar ranges; every position force-closed by 15:55 ET.

## Roadmap

- [x] v0.1 — five strategies, no-lookahead engine, first 60-day baseline
- [x] v0.2 — parameter sweeps with train/test split → nothing survives out-of-sample yet
- [x] v0.3 — three new strategies (news momentum, squeeze breakout, ATR-trail exits),
      per-trade market-condition journal, GitHub Actions paper trading + nightly journal
- [ ] Walk-forward validation (multiple train/test folds instead of one split)
- [ ] Regime filters learned from the journal (trade only where the conditions data says the strategy wins)
- [ ] Longer history + true gappers via Alpaca's historical minute data
- [ ] Short side for the momentum setups
- [ ] **Gate:** paper trading is the data-collection lab; nothing touches real money
      without sustained positive out-of-sample **and** paper expectancy

Progress log: [PROGRESS.md](PROGRESS.md).

## Disclaimer

Educational project. Paper trading only. Nothing here is financial advice, and
backtest/paper results do not predict live results.
