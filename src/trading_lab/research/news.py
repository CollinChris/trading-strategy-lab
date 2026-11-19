"""Study C — news sentiment (docs/research/PREREGISTRATION.md, section C).

Two headline sources, both Benzinga:
- FNSPID (Dong et al. 2024; CC BY-NC 4.0 — used non-commercially, never committed):
  the historical sample, 2016 → the dataset's end. Prepared once per run on Actions.
- Alpaca's news API, archived daily from 2026-04-29 on the `news-archive` branch as
  derived numbers only (id, time, symbols, word count, scores) — no headline text.

Pipeline: `prep_fnspid` filters headlines and splits unique titles into shards →
`score_shard` runs FinBERT + Loughran–McDonald per shard (parallel jobs) →
`run_study` turns sentiment into a daily long/short book and scores it.

FNSPID's quirks, found before the first run (PREREGISTRATION.md, Amendment 1): its
"UTC" stamps are 8 hours behind UTC, most Benzinga rows carry a date but no time,
and the file mixes in other publishers. Hence the primary rule trades headlines
dated D at the next session's open — safe however the stamps are read.
"""

from __future__ import annotations

import datetime as dt
import json
import math
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from ..data import market_today
from ..report import _md_table
from . import engine
from .prices import Panel, _headers, get_json
from .sentiment import FinBert, lm_lexicon, lm_scores, n_words

ET = ZoneInfo("America/New_York")
NEWS_URL = "https://data.alpaca.markets/v1beta1/news"
NEWS_DIR = Path("data/research/news")
ARCHIVE_START = dt.date(2026, 4, 29)  # first day Alpaca's news archive actually has
TOP_N = 500
MIN_WORDS = 4
ROUNDUP_SYMBOLS = 3
MIN_STOCKS = 10
SHARD_TITLES = 600_000  # unique titles per scoring job (~2 h at a cautious 80/s)
WINDOW = ("16:00", "09:25")  # original pre-open window, ET (descriptive since Amendment 1)
FNSPID_SHIFT = pd.Timedelta(hours=8)  # FNSPID "UTC" stamps run 8 h behind UTC
# Benzinga's fixed-schedule headlines and their usual ET hour: the timing check.
SCHEDULE = {
    "Pre-Market Session": 8.0,
    "Mid-Day Market Update": 12.0,
    "Mid-Day Session": 12.5,
    "52-Week Highs On": 10.5,
    "Mid-Afternoon Market Update": 14.5,
    "After-Hours Session": 17.0,
}


# --------------------------------------------------------------------------- timing


def assign_window(
    ts_utc: pd.Series, sessions: pd.DatetimeIndex, start: str = WINDOW[0], cut: str = WINDOW[1]
) -> np.ndarray:
    """Session position whose window [previous session + start, session + cut) (ET) holds
    each timestamp, or -1 (e.g. published during the trading day)."""
    days = sessions.as_unit("ns").normalize()

    def stamp(d: pd.DatetimeIndex, hhmm: str) -> np.ndarray:
        local = (d + pd.Timedelta(hhmm + ":00")).tz_localize(ET)
        return local.tz_convert("UTC").tz_localize(None).as_unit("ns").to_numpy()

    cuts = stamp(days, cut)
    prev = days.insert(0, days[0] - pd.Timedelta(days=1))[:-1]
    starts = stamp(prev, start)
    t = pd.to_datetime(ts_utc, utc=True).dt.tz_localize(None).dt.as_unit("ns").to_numpy()
    j = np.searchsorted(cuts, t, side="right")
    jj = np.minimum(j, len(days) - 1)
    return np.where((j < len(days)) & (t >= starts[jj]), j, -1)


def assign_dates(dates: pd.Series, sessions: pd.DatetimeIndex) -> np.ndarray:
    """First session strictly after each headline date (-1 if beyond the data)."""
    sess = sessions.as_unit("ns").normalize().to_numpy()
    d = pd.to_datetime(dates).dt.normalize().dt.as_unit("ns").to_numpy()
    j = np.searchsorted(sess, d, side="right")
    return np.where(j < len(sess), j, -1)


def book(
    heads: pd.DataFrame, sessions: pd.DatetimeIndex, rank: pd.DataFrame, timing: str
) -> pd.DataFrame:
    """Daily long/short picks, open → close. `heads` has symbol, score and either `date`
    (timing="date": dated D → the first session after D) or `ts` (timing="window": the
    16:00 → 09:25 ET window). Mean score per stock, top-`TOP_N` universe, ≥ MIN_STOCKS
    names → long the top ⌊n/5⌋, short the bottom ⌊n/5⌋ (ties by symbol)."""
    if timing == "date":
        j = assign_dates(heads["date"], sessions)
    else:
        j = assign_window(heads["ts"], sessions)
    h = heads.assign(session_i=j)
    h = h[h["session_i"] >= 0]
    s = h.groupby(["session_i", "symbol"], as_index=False)["score"].mean()
    s["rank"] = engine.lookup(rank, s["symbol"], s["session_i"])
    s = s[s["rank"] <= TOP_N].reset_index(drop=True)
    n = s.groupby("session_i")["symbol"].transform("size")
    k = n // 5
    by = ["session_i", "score", "symbol"]
    up = s.sort_values(by, ascending=[True, False, True]).groupby("session_i").cumcount()
    down = s.sort_values(by, ascending=[True, True, True]).groupby("session_i").cumcount()
    up, down = up.sort_index(), down.sort_index()
    enough = n >= MIN_STOCKS
    t = pd.concat(
        [
            s[enough & (up < k)].assign(direction=1),
            s[enough & (down < k)].assign(direction=-1),
        ]
    ).sort_values(["session_i", "direction", "symbol"])
    t["entry_i"] = t["exit_i"] = t["session_i"]
    t["entry_at"] = "open"
    return t.reset_index(drop=True)


# --------------------------------------------------------------------------- FNSPID


def _universe(panel: Panel, rank: pd.DataFrame) -> set[str]:
    start = panel.sessions.searchsorted(pd.Timestamp("2016-01-01"))
    return set(rank.columns[(rank.iloc[start:] <= TOP_N).any()])


def _hour_profile(ts_utc: pd.Series) -> dict[str, float]:
    hours = ts_utc.dt.tz_convert(ET).dt.hour.value_counts(normalize=True).sort_index()
    return {f"{h:02d}": round(float(v), 4) for h, v in hours.items()}


def _et_hours(ts_utc: pd.Series) -> np.ndarray:
    et = ts_utc.dt.tz_convert(ET)
    return (et.dt.hour + et.dt.minute / 60).to_numpy(dtype="float64")


def prep_fnspid(csv_path: Path, panel_dir: Path, out_dir: Path = NEWS_DIR) -> dict:
    """Filter FNSPID's external news to Benzinga headlines for universe stocks.

    Writes headlines.pkl (date, ts — true UTC, NaT when the row has no time — symbol,
    h), titles.pkl (h, title: the unique titles to score) and prep.json (counts, the
    timing check, shard count)."""
    panel = Panel.load(panel_dir)
    universe = _universe(panel, engine.universe_rank(panel))
    first = pd.Timestamp("2015-12-31")
    parts, titles = [], {}
    schedule: dict[str, list[np.ndarray]] = {k: [] for k in SCHEDULE}
    rows = benzinga = 0
    reader = pd.read_csv(
        csv_path,
        usecols=["Date", "Article_title", "Stock_symbol", "Url"],
        dtype=str,
        chunksize=500_000,
        on_bad_lines="skip",
    )
    for chunk in reader:
        rows += len(chunk)
        chunk = chunk[chunk["Url"].str.contains("benzinga.com", regex=False, na=False)]
        stamp = pd.to_datetime(
            chunk["Date"].str.replace("UTC", "", regex=False).str.strip(),
            errors="coerce",
            format="ISO8601",
        )
        ok = stamp.notna() & chunk["Article_title"].notna() & chunk["Stock_symbol"].notna()
        ok &= stamp >= first
        stamp = stamp[ok]
        timed = (stamp.dt.hour != 0) | (stamp.dt.minute != 0) | (stamp.dt.second != 0)
        c = pd.DataFrame(
            {
                "date": stamp.dt.normalize(),
                "ts": (stamp + FNSPID_SHIFT).dt.tz_localize("UTC").where(timed),
                "symbol": chunk.loc[ok, "Stock_symbol"]
                .str.strip()
                .str.upper()
                .str.replace("-", ".", regex=False),
                "title": chunk.loc[ok, "Article_title"].str.strip(),
            }
        )
        benzinga += len(c)
        on_clock = c[c["ts"].notna()]
        for pattern in SCHEDULE:
            hit = on_clock[on_clock["title"].str.contains(pattern, case=False, regex=False)]
            schedule[pattern].append(_et_hours(hit["ts"]))
        c["h"] = pd.util.hash_pandas_object(c["title"], index=False).to_numpy()
        mine = c[c["symbol"].isin(universe)].drop_duplicates("h")
        titles.update(zip(mine["h"], mine["title"], strict=True))
        parts.append(c[["date", "ts", "symbol", "h"]])
        print(f"fnspid: {rows:,} rows read, {benzinga:,} Benzinga 2016+", flush=True)
    heads = pd.concat(parts, ignore_index=True)
    stats: dict = {"rows": rows, "benzinga_2016_on": benzinga}
    tagged = heads.groupby(["h", "date"])["symbol"].transform("nunique")
    stats["roundup_dropped"] = int((tagged >= ROUNDUP_SYMBOLS).sum())
    heads = heads[(tagged < ROUNDUP_SYMBOLS) & heads["symbol"].isin(universe)]
    words = pd.Series({h: n_words(x) for h, x in titles.items()}, dtype="int64")
    heads = heads[heads["h"].map(words).fillna(0).to_numpy() >= MIN_WORDS]
    heads = heads.drop_duplicates().sort_values(["date", "ts"]).reset_index(drop=True)
    used = pd.unique(heads["h"])
    title_frame = pd.DataFrame({"h": used, "title": [titles[h] for h in used]})
    check = {}
    for pattern, expected in SCHEDULE.items():
        hours = np.concatenate(schedule[pattern]) if schedule[pattern] else np.array([])
        if len(hours):
            check[pattern] = {
                "n": len(hours),
                "median_et": round(float(np.median(hours)), 2),
                "expected_et": expected,
            }
    stats.update(
        headlines=len(heads),
        timed_share=round(float(heads["ts"].notna().mean()), 4),
        unique_titles=len(title_frame),
        symbols=int(heads["symbol"].nunique()),
        first=str(heads["date"].min().date()),
        last=str(heads["date"].max().date()),
        per_year={
            str(k): int(v) for k, v in heads["date"].dt.year.value_counts().sort_index().items()
        },
        hour_profile_et=_hour_profile(heads["ts"].dropna()),
        schedule_check=check,
        shards=max(1, math.ceil(len(title_frame) / SHARD_TITLES)),
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    heads.to_pickle(out_dir / "headlines.pkl")
    title_frame.to_pickle(out_dir / "titles.pkl")
    (out_dir / "prep.json").write_text(json.dumps(stats, indent=2))
    print(json.dumps(stats, indent=2))
    return stats


def score_shard(prep_dir: Path, shard: int, n_shards: int, out: Path) -> Path:
    titles = pd.read_pickle(prep_dir / "titles.pkl")
    sub = titles[titles["h"] % n_shards == shard]
    texts = sub["title"].tolist()
    print(f"scoring shard {shard}/{n_shards}: {len(texts):,} titles")
    fin = FinBert().score(texts)
    lm = lm_scores(texts, lm_lexicon())
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"h": sub["h"].to_numpy(), "finbert": fin, "lm": lm}).to_pickle(out)
    return out


# --------------------------------------------------------------------------- Alpaca archive

ARCHIVE_COLS = ["id", "created_at", "symbols", "n_symbols", "n_words", "finbert", "lm"]


def fetch_alpaca_news(start: dt.datetime, end: dt.datetime, headers: dict) -> list[dict]:
    params = {
        "start": start.astimezone(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "end": end.astimezone(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "limit": 50,
        "sort": "asc",
        "include_content": "false",
    }
    items: list[dict] = []
    while True:
        payload = get_json(NEWS_URL, params, headers)
        items.extend(payload.get("news", []))
        token = payload.get("next_page_token")
        if not token:
            return items
        params["page_token"] = token


def _month_starts(start: dt.datetime, end: dt.datetime):
    m = dt.datetime(start.year, start.month, 1, tzinfo=dt.UTC)
    while m < end:
        nxt = dt.datetime(m.year + m.month // 12, m.month % 12 + 1, 1, tzinfo=dt.UTC)
        yield max(m, start), min(nxt, end), m.strftime("%Y-%m")
        m = nxt


def archive(archive_dir: Path, since: dt.date = ARCHIVE_START, max_days: int = 30) -> int:
    """Append Alpaca headlines since the last archived one, scored, as monthly CSVs.
    At most `max_days` per run (~700 headlines an hour: a full backfill would outrun
    a 6-hour job), so a backlog catches up over consecutive daily runs."""
    archive_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(archive_dir.glob("*.csv"))
    start = dt.datetime.combine(since, dt.time(), tzinfo=ET).astimezone(dt.UTC)
    if files:
        last = pd.read_csv(files[-1], usecols=["created_at"])["created_at"].max()
        if isinstance(last, str):
            start = max(start, pd.Timestamp(last).to_pydatetime())
    end = min(dt.datetime.now(dt.UTC).replace(microsecond=0), start + dt.timedelta(days=max_days))
    headers, model, lexicon, added = _headers(), None, lm_lexicon(), 0
    for lo, hi, month in _month_starts(start, end):
        items = fetch_alpaca_news(lo, hi, headers)
        print(
            f"news archive {month}: {len(items):,} headlines from {lo:%Y-%m-%d %H:%M}", flush=True
        )
        if not items:
            continue
        heads = [str(i.get("headline") or "") for i in items]
        model = model or FinBert()
        new = pd.DataFrame(
            {
                "id": [i["id"] for i in items],
                "created_at": [i["created_at"] for i in items],
                "symbols": ["|".join(i.get("symbols") or []) for i in items],
                "n_symbols": [len(i.get("symbols") or []) for i in items],
                "n_words": [n_words(h) for h in heads],
                "finbert": np.round(model.score(heads), 5),
                "lm": np.round(lm_scores(heads, lexicon), 5),
            }
        )
        path = archive_dir / f"{month}.csv"
        if path.exists():
            new = pd.concat([pd.read_csv(path), new])
        new = new.drop_duplicates("id", keep="last").sort_values(["created_at", "id"])
        new[ARCHIVE_COLS].to_csv(path, index=False)
        added += len(items)
    return added


def load_archive(archive_dir: Path) -> pd.DataFrame:
    """Archive → one row per (headline, symbol), study filters applied; `date` is the
    headline's calendar date in New York."""
    files = sorted(archive_dir.glob("*.csv")) if archive_dir.exists() else []
    if not files:
        return pd.DataFrame(columns=["date", "ts", "symbol", "finbert", "lm"])
    a = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    a = a[(a["n_words"] >= MIN_WORDS) & (a["n_symbols"] < ROUNDUP_SYMBOLS) & (a["n_symbols"] > 0)]
    a = a.assign(symbol=a["symbols"].str.split("|")).explode("symbol")
    ts = pd.to_datetime(a["created_at"], utc=True, format="ISO8601")
    return pd.DataFrame(
        {
            "date": ts.dt.tz_convert(ET).dt.tz_localize(None).dt.normalize(),
            "ts": ts,
            "symbol": a["symbol"].str.upper(),
            "finbert": a["finbert"],
            "lm": a["lm"],
        }
    ).reset_index(drop=True)


# --------------------------------------------------------------------------- study

PRIMARY = "FinBERT, headlines dated D → next session open → close (primary)"


def _score(heads, scorer, timing, sessions, rank, panel, beta_cache):
    trades = book(heads.assign(score=heads[scorer]), sessions, rank, timing)
    missing = sorted((set(trades["symbol"]) - set(beta_cache.columns)) & set(panel.close.columns))
    if missing:
        extra = engine.rolling_beta(panel.close[missing], panel.close["SPY"])
        beta_cache = pd.concat([beta_cache, extra], axis=1)
    trades["beta"] = np.nan_to_num(
        engine.lookup(beta_cache, trades["symbol"], trades["entry_i"]), nan=1.0
    )
    results, daily = engine.simulate(trades, panel)
    return results, daily, beta_cache


def run_study(
    prep_dir: Path,
    score_files: list[Path],
    panel_dir: Path,
    archive_dir: Path | None,
    out: Path = Path("results/NEWS.md"),
) -> Path:
    panel = Panel.load(panel_dir)
    sessions = panel.sessions
    rank = engine.universe_rank(panel)
    heads = pd.read_pickle(prep_dir / "headlines.pkl")
    scores = pd.concat([pd.read_pickle(f) for f in score_files], ignore_index=True)
    heads = heads.merge(scores, on="h", how="inner")
    stats = json.loads((prep_dir / "prep.json").read_text())
    timed = heads[heads["ts"].notna()]
    variants = [
        (PRIMARY, heads, "finbert", "date"),
        ("Loughran–McDonald, same rule", heads, "lm", "date"),
        ("FinBERT, 16:00 → 09:25 ET window, timed rows only (+8 h)", timed, "finbert", "window"),
    ]
    forward = load_archive(archive_dir) if archive_dir else pd.DataFrame()
    if not forward.empty:
        variants += [
            ("Alpaca era (2026-04-29 on), FinBERT, date rule", forward, "finbert", "date"),
            ("Alpaca era, FinBERT, 16:00 → 09:25 ET window", forward, "finbert", "window"),
        ]
    beta = pd.DataFrame(index=sessions)
    runs = {}
    for name, frame, scorer, timing in variants:
        results, daily, beta = _score(frame, scorer, timing, sessions, rank, panel, beta)
        runs[name] = (results, daily)
    return write_report(runs, stats, sessions, out)


def _profile_line(profile: dict[str, float]) -> str:
    return " · ".join(f"{h}h {v:.0%}" for h, v in profile.items() if v >= 0.01)


def _schedule_table(check: dict) -> str:
    rows = [
        {
            "headline type": f'"{k}"',
            "timed rows": f"{v['n']:,}",
            "usual time (ET)": f"{v['expected_et']:.1f}h",
            "median after +8 h (ET)": f"{v['median_et']:.1f}h",
        }
        for k, v in check.items()
    ]
    return _md_table(pd.DataFrame(rows)) if rows else "_no fixed-schedule headlines found_"


def write_report(runs: dict, stats: dict, sessions: pd.DatetimeIndex, out: Path) -> Path:
    results, daily = runs[PRIMARY]
    done = results[results["adj_ret"].notna()].copy()
    if done.empty:
        out.write_text("# News sentiment\n\nNo trades — check the inputs.\n")
        return out
    port = engine.portfolio(daily, sessions)
    span = (int(daily["day_i"].min()), int(daily["day_i"].max()))
    s = engine.summarize(port)
    passed, reason = engine.decide(s, min_sharpe=0.5)
    done["leg"] = np.where(done["direction"] > 0, "long (most positive)", "short (most negative)")
    rows = []
    for name, (res, dly) in runs.items():
        x = engine.summarize(engine.portfolio(dly, sessions))
        rows.append(
            {
                "variant": name,
                "trades": f"{res['adj_ret'].notna().sum():,}",
                "days": f"{x['days']:,}",
                "daily mean": engine.bp(x["mean_daily"]),
                "95% range": f"{engine.bp(x['lo_daily'])} to {engine.bp(x['hi_daily'])}",
                "Sharpe": engine.num(x["sharpe"]),
            }
        )
    text = f"""# News sentiment (pre-registered study C)

Generated {market_today()} from FNSPID's Benzinga headlines (Dong et al. 2024, CC BY-NC 4.0)
and Alpaca daily bars. Rules fixed in advance:
[PREREGISTRATION.md](../docs/research/PREREGISTRATION.md), section C as changed by
Amendment 1 (FNSPID's timestamps — see the data check below).

## Verdict: {"**PASS**" if passed else "**FAIL**"}

{reason}.

{"Next step per the pre-registration: paper-trade it in a separate Alpaca paper account, judged on tracking this backtest." if passed else "Per the pre-registration, a failed idea is archived — not re-run with new settings."}

## What was tested

- {stats["rows"]:,} FNSPID rows → {stats["benzinga_2016_on"]:,} Benzinga rows from 2016 →
  {stats["headlines"]:,} headline-stock pairs after filters ({stats["unique_titles"]:,} unique
  headlines scored by FinBERT, {stats["symbols"]:,} stocks, {stats["first"]} → {stats["last"]}).
  Dropped: {stats["roundup_dropped"]:,} round-up rows (same title on 3+ symbols that day),
  titles under 4 words, stocks outside the top-{TOP_N} liquidity universe.
- Each session: mean FinBERT score of a stock's headlines dated since the previous session
  (Friday–Sunday for a Monday); with ≥ {MIN_STOCKS} stocks, long the top fifth and short the
  bottom fifth, open → close, each hedged with beta × SPY; 5 bp per side plus 1 bp on the hedge.
- {len(done):,} trades over {s["days"]:,} trading days
  ({sessions[span[0]].date()} → {sessions[span[1]].date()}).

## Headline numbers (primary)

| measure | value |
|---|---|
| mean daily portfolio return (market-adjusted, net) | {engine.bp(s["mean_daily"])} |
| 95% range, resampled by day | {engine.bp(s["lo_daily"])} to {engine.bp(s["hi_daily"])} |
| annualised Sharpe | {engine.num(s["sharpe"])} |
| mean per trade | {engine.bp(done["adj_ret"].mean())} |

## Descriptive only (cannot rescue a failed primary)

All variants:

{_md_table(pd.DataFrame(rows))}

Primary, by leg:

{engine.breakdown(done, daily, done["leg"], sessions, span, "leg")}

Primary, by year:

{engine.by_year(port)}

## Data check — FNSPID timestamps

Only {stats["timed_share"]:.1%} of the kept rows carry a time of day; the rest are date-only,
which is why the primary rule trades the session after a headline's date. For timed rows,
the stamps labelled UTC run 8 hours behind UTC; Benzinga's fixed-schedule headlines should
land at their usual times once 8 hours are added:

{_schedule_table(stats.get("schedule_check", {}))}

Timed rows by hour of publication (ET, after the shift; hours with ≥ 1%):
{_profile_line(stats["hour_profile_et"])}.
"""
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    return out
