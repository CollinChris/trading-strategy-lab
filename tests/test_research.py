"""Pre-registered studies: the scoring engine and each study's signal timing, on
small synthetic data (the real runs happen on GitHub Actions)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from trading_lab.research import earnings, engine, insiders, news, sec, sentiment
from trading_lab.research.prices import Panel


def make_panel(n: int = 320, seed: int = 0) -> Panel:
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-01", periods=n)
    spy = 300 * np.cumprod(1 + rng.normal(0, 0.01, n))
    close = pd.DataFrame(
        {
            "SPY": spy,
            "AAA": 50 * np.cumprod(1 + rng.normal(0, 0.02, n)),
            "BBB": 20 * np.cumprod(1 + rng.normal(0, 0.02, n)),
            "LOW": np.full(n, 3.0),  # under $5 — never eligible
        },
        index=idx,
    )
    volume = pd.DataFrame(
        {"SPY": 1e8, "AAA": 1e6, "BBB": 1e5, "LOW": 1e9}, index=idx, dtype="float64"
    )
    return Panel(open=close.shift(1).bfill(), close=close, close_raw=close, volume_raw=volume)


# --------------------------------------------------------------------------- engine


def test_universe_rank_screens_and_uses_only_earlier_sessions():
    p = make_panel()
    rank = engine.universe_rank(p, min_history=250)
    assert rank.iloc[:250].isna().all().all()  # not enough history yet
    assert rank["LOW"].isna().all()  # price screen beats huge volume
    row = rank.iloc[300]
    assert (row["SPY"], row["AAA"], row["BBB"]) == (1, 2, 3)
    # A volume spike on day t can't change day t's rank (no look-ahead).
    p.volume_raw.iloc[300, p.volume_raw.columns.get_loc("BBB")] = 1e15
    assert engine.universe_rank(p, min_history=250).iloc[300]["BBB"] == 3


def test_universe_rank_uses_unadjusted_price():
    p = make_panel()
    p.close_raw["AAA"] = p.close["AAA"] * 10  # e.g. a later 10:1 split
    p.close["AAA"] = p.close["AAA"] / 20  # adjusted price under $5
    assert engine.universe_rank(p, min_history=250).iloc[300]["AAA"] == 2


def test_rolling_beta_recovers_slope_clips_and_lags():
    p = make_panel()
    m = p.close["SPY"] / p.close["SPY"].shift(1) - 1
    two = 10 * np.cumprod(1 + (1.5 * m).fillna(0))
    wild = 10 * np.cumprod(1 + (5 * m).fillna(0))
    close = pd.DataFrame({"TWO": two, "WILD": wild}, index=p.sessions)
    beta = engine.rolling_beta(close, p.close["SPY"], window=250, min_obs=120)
    assert (beta.iloc[:121] == 1.0).all().all()  # too few observations → 1.0
    assert beta["TWO"].iloc[200] == pytest.approx(1.5)
    assert beta["WILD"].iloc[200] == pytest.approx(3.0)  # clipped
    # Row t uses data through t-1: changing day t's price leaves row t alone.
    bumped = close.copy()
    bumped.iloc[200, 0] *= 1.5
    again = engine.rolling_beta(bumped, p.close["SPY"], window=250, min_obs=120)
    assert again["TWO"].iloc[200] == pytest.approx(1.5)


def _flat_panel(n: int = 10) -> Panel:
    idx = pd.bdate_range("2021-01-04", periods=n)
    close = pd.DataFrame({"SPY": 400.0, "XYZ": 100.0}, index=idx)
    return Panel(open=close.copy(), close=close.copy(), close_raw=close.copy(), volume_raw=close)


def test_simulate_one_day_open_to_close_hedged_with_costs():
    p = _flat_panel()
    p.close.loc[p.sessions[3], ["SPY", "XYZ"]] = [404.0, 102.0]
    trades = pd.DataFrame(
        {"symbol": ["XYZ", "XYZ"], "entry_i": 3, "exit_i": 3, "entry_at": "open"}
        | {"direction": [1, -1], "beta": 1.0}
    )
    res, daily = engine.simulate(trades, p)
    cost = 2 * (5e-4 + 1e-4)
    assert res["stock_ret"].tolist() == pytest.approx([0.02, 0.02])
    assert res["adj_ret"].tolist() == pytest.approx([0.01 - cost, -0.01 - cost])
    assert daily.groupby("trade")["ret"].sum().tolist() == pytest.approx(res["adj_ret"].tolist())


def test_simulate_close_entry_and_delisting_exit():
    p = _flat_panel()
    p.close.loc[p.sessions[2:], "XYZ"] = [
        100.0,
        110.0,
        121.0,
        np.nan,
        np.nan,
        np.nan,
        np.nan,
        np.nan,
    ]
    trades = pd.DataFrame(
        {"symbol": ["XYZ"], "entry_i": [2], "exit_i": [7], "entry_at": ["close"]}
        | {"direction": [1], "beta": [0.0]}
    )
    res, daily = engine.simulate(trades, p)
    # Entered at day 2's close; bars stop after day 4 → out at day 4's close.
    assert res.loc[0, "stock_ret"] == pytest.approx(0.21)
    assert res.loc[0, "days"] == 2 and res.loc[0, "last_i"] == 4
    assert daily["day_i"].tolist() == [3, 4]


def test_portfolio_equal_weight_zero_fill_and_bootstrap():
    sessions = pd.bdate_range("2021-01-04", periods=6)
    daily = pd.DataFrame({"day_i": [1, 1, 3], "trade": [0, 1, 2], "ret": [0.02, 0.0, -0.01]})
    port = engine.portfolio(daily, sessions)
    assert port.tolist() == pytest.approx([0.01, 0.0, -0.01])
    assert port.index[0] == sessions[1]
    lo, hi = engine.boot_ci(np.array([1.0, 2.0, 3.0, 4.0]))
    assert lo <= 2.5 <= hi
    assert engine.boot_ci(np.array([1.0, 2.0, 3.0, 4.0])) == (lo, hi)  # seeded


def test_decide_rules():
    good = {"mean_daily": 3e-4, "lo_daily": 1e-4, "hi_daily": 5e-4, "sharpe": 0.8}
    assert engine.decide(good, min_sharpe=0.5)[0]
    assert not engine.decide(good | {"sharpe": 0.4}, min_sharpe=0.5)[0]
    assert not engine.decide(good | {"lo_daily": -1e-5}, min_sharpe=0.5)[0]
    monthly = {"mean_monthly": 0.01, "lo_monthly": 0.002, "hi_monthly": 0.02, "sharpe": 0.5}
    assert engine.decide(monthly, min_sharpe=0.45, monthly_rule=True)[0]
    assert not engine.decide(monthly | {"lo_monthly": -0.001}, 0.45, monthly_rule=True)[0]


# --------------------------------------------------------------------------- SEC / insiders


def test_sec_needs_a_contact_email(monkeypatch):
    monkeypatch.setenv("SEC_USER_AGENT", "no contact")
    with pytest.raises(SystemExit):
        sec.user_agent()
    monkeypatch.setenv("SEC_USER_AGENT", "Lab research lab@example.com")
    assert sec.user_agent() == "Lab research lab@example.com"
    assert sec.to_alpaca("brk-b") == "BRK.B"


def test_qualifying_purchases_filter():
    sub = pd.DataFrame(
        {
            "ACCESSION_NUMBER": ["a1", "a2", "a3", "a4"],
            "FILING_DATE": ["31-MAR-2016", "31-MAR-2016", "01-APR-2016", "01-APR-2016"],
            "DOCUMENT_TYPE": ["4", "4/A", "4", "4"],
            "ISSUERCIK": "100",
            "ISSUERTRADINGSYMBOL": "xyz",
            "AFF10B5ONE": ["0", "0", "1", "0"],
        }
    )
    owners = pd.DataFrame(
        {
            "ACCESSION_NUMBER": ["a1", "a2", "a3", "a4"],
            "RPTOWNERCIK": ["1", "2", "3", "4"],
            "RPTOWNER_RELATIONSHIP": ["Director", "Officer", "Director", "TenPercentOwner"],
        }
    )
    trans = pd.DataFrame(
        {
            "ACCESSION_NUMBER": ["a1", "a1", "a2", "a3", "a4"],
            "TRANS_DATE": ["29-MAR-2016"] * 5,
            "TRANS_CODE": ["P", "S", "P", "P", "P"],
            "TRANS_PRICEPERSHARE": ["10.5", "10.5", "10", "10", "10"],
            "TRANS_ACQUIRED_DISP_CD": ["A", "D", "A", "A", "A"],
        }
    )
    q = insiders.qualifying(sub, owners, trans)
    # a1's purchase only: a2 is an amendment, a3 a 10b5-1 plan, a4 not an insider.
    assert len(q) == 1
    row = q.iloc[0]
    assert (row["owner_cik"], row["symbol"]) == (1, "XYZ")
    assert row["filing_date"] == pd.Timestamp("2016-03-31")


def _buys(rows):
    return pd.DataFrame(
        [
            {
                "issuer_cik": 1,
                "symbol": "XYZ",
                "owner_cik": o,
                "trans_date": pd.Timestamp(t),
                "filing_date": pd.Timestamp(f),
            }
            for o, t, f in rows
        ]
    )


def test_cluster_needs_two_insiders_within_a_week():
    same_person = _buys([(1, "2020-01-01", "2020-01-02"), (1, "2020-01-03", "2020-01-04")])
    assert insiders.find_clusters(same_person).empty
    too_far = _buys([(1, "2020-01-01", "2020-01-02"), (2, "2020-01-10", "2020-01-11")])
    assert insiders.find_clusters(too_far).empty
    pair = _buys([(1, "2020-01-01", "2020-01-02"), (2, "2020-01-06", "2020-01-08")])
    ev = insiders.find_clusters(pair)
    # Known only once the second insider's filing is in.
    assert ev["filing_date"].tolist() == [pd.Timestamp("2020-01-08")]
    assert ev["insiders"].tolist() == [2]


def test_cluster_cooldown():
    rows = [(1, "2020-01-01", "2020-01-02"), (2, "2020-01-02", "2020-01-03")]
    rows += [(3, "2020-02-01", "2020-02-02"), (4, "2020-02-02", "2020-02-03")]  # within 60 days
    rows += [(5, "2020-04-01", "2020-04-02"), (6, "2020-04-02", "2020-04-03")]  # after
    ev = insiders.find_clusters(_buys(rows))
    assert ev["filing_date"].dt.strftime("%m-%d").tolist() == ["01-03", "04-03"]


# --------------------------------------------------------------------------- earnings


def test_day_zero_timing():
    sessions = pd.bdate_range("2024-04-29", periods=10)  # Mon 29 Apr → Fri 10 May
    accepted = earnings.parse_accepted(
        pd.Series(
            [
                "2024-04-30T07:00:00.000Z",  # Tue before the open → Tue
                "2024-04-30T09:30:00.000Z",  # Tue at the open → Wed
                "2024-04-30T16:05:12.000Z",  # Tue after the close → Wed
                "2024-05-04T10:00:00.000Z",  # Saturday → Mon
            ]
        )
    )
    assert accepted.iloc[2] == pd.Timestamp("2024-04-30 16:05:12")  # wall clock kept
    got = sessions[earnings.day_zero(accepted, sessions)].strftime("%a %d").tolist()
    assert got == ["Tue 30", "Wed 01", "Wed 01", "Mon 06"]


def test_percentiles_use_only_earlier_days():
    day = np.array([0, 0, 1, 1, 2])
    reaction = np.array([1.0, 2.0, 3.0, 0.0, 1.5])
    pct = earnings.percentiles(day, reaction, lookback=3, min_history=2)
    assert np.isnan(pct[:2]).all()  # nothing earlier
    assert pct[2:4].tolist() == [1.0, 0.0]  # vs {1, 2}; same-day events excluded
    assert pct[4] == pytest.approx(1 / 3)  # vs the last 3, {2, 3, 0}: only 0 is below


# --------------------------------------------------------------------------- news


def test_assign_window():
    sessions = pd.bdate_range("2024-03-07", periods=5)  # Thu 7 → Wed 13 Mar (DST on 10th)
    ts = pd.Series(
        pd.to_datetime(
            [
                "2024-03-07 21:30",  # Thu 16:30 EST → Fri
                "2024-03-08 14:20",  # Fri 09:20 EST → Fri
                "2024-03-08 15:00",  # Fri 10:00 EST, intraday → none
                "2024-03-09 15:00",  # Saturday → Mon
                "2024-03-11 13:20",  # Mon 09:20 EDT → Mon
                "2024-03-11 13:30",  # Mon 09:30 EDT → none
            ],
            utc=True,
        )
    )
    j = news.assign_window(ts, sessions)
    labels = [sessions[i].strftime("%a") if i >= 0 else "-" for i in j]
    assert labels == ["Fri", "Fri", "-", "Mon", "Mon", "-"]


def test_assign_dates_trades_the_next_session():
    sessions = pd.bdate_range("2024-03-07", periods=5)  # Thu 7 → Wed 13 Mar
    dates = pd.Series(pd.to_datetime(["2024-03-07", "2024-03-08", "2024-03-09", "2024-03-10"]))
    got = [sessions[i].strftime("%a %d") for i in news.assign_dates(dates, sessions)]
    # A headline dated Thursday could be from Thursday afternoon → Friday's open at the earliest.
    assert got == ["Fri 08", "Mon 11", "Mon 11", "Mon 11"]
    assert news.assign_dates(pd.Series(pd.to_datetime(["2024-03-13"])), sessions).tolist() == [-1]


def test_book_picks_top_and_bottom_fifth():
    sessions = pd.bdate_range("2024-03-04", periods=3)
    syms = [f"S{i:02d}" for i in range(12)]
    rank = pd.DataFrame(1.0, index=sessions, columns=syms)
    rank["S11"] = np.nan  # outside the universe
    ts = pd.Timestamp("2024-03-05 12:00", tz="UTC")  # Tue 07:00 ET → Tue
    scores = [0.9, 0.8, 0.5, 0.5, 0.0, 0.0, 0.0, 0.0, -0.5, -0.9, -0.9, 1.0]
    heads = pd.DataFrame({"ts": ts, "symbol": syms, "score": scores})
    t = news.book(heads, sessions, rank, "window")
    # 11 eligible → k = 2 each side; S11's 1.0 is out; -0.9 tie broken by symbol.
    assert t[t["direction"] == 1]["symbol"].tolist() == ["S00", "S01"]
    assert sorted(t[t["direction"] == -1]["symbol"]) == ["S09", "S10"]
    assert (t["entry_i"] == 1).all() and (t["exit_i"] == 1).all()
    few = news.book(heads.iloc[:9], sessions, rank, "window")
    assert few.empty  # fewer than 10 stocks with news
    dated = heads.drop(columns="ts").assign(date=pd.Timestamp("2024-03-04"))
    assert (news.book(dated, sessions, rank, "date")["entry_i"] == 1).all()  # Mon → Tue


def test_lm_scores_and_lexicon(tmp_path):
    csv = tmp_path / "LM.csv"
    csv.write_text("Word,Negative,Positive\nLOSS,2009,0\nGAIN,0,2009\nOLD,-2012,0\n")
    lex = sentiment.lm_lexicon(csv)
    assert lex == (frozenset({"GAIN"}), frozenset({"LOSS"}))
    got = sentiment.lm_scores(["Big gain, small loss, old gain", "", "Nothing here"], lex)
    assert got.tolist() == pytest.approx([1 / 6, 0.0, 0.0])
    assert sentiment.n_words("Apple beats on Q3 EPS") == 5


def test_load_archive_filters(tmp_path):
    pd.DataFrame(
        {
            "id": [1, 2, 3, 4],
            "created_at": ["2026-05-01T12:00:00Z"] * 4,
            "symbols": ["AAPL", "AAPL|MSFT|NVDA", "TSLA", "AMD|INTC"],
            "n_symbols": [1, 3, 1, 2],
            "n_words": [6, 6, 3, 5],
            "finbert": [0.5, 0.1, 0.2, -0.3],
            "lm": [0.0, 0.0, 0.0, 0.1],
        }
    ).to_csv(tmp_path / "2026-05.csv", index=False)
    a = news.load_archive(tmp_path)
    assert a["symbol"].tolist() == ["AAPL", "AMD", "INTC"]  # round-up and 3-word dropped
    assert str(a["ts"].dt.tz) == "UTC"


# --------------------------------------------------------------------------- end to end


def market(n_days: int = 420, n_syms: int = 40, seed: int = 1) -> Panel:
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2019-01-01", periods=n_days)
    m = rng.normal(0, 0.01, n_days)
    cols = {"SPY": 300 * np.cumprod(1 + m)}
    for i in range(n_syms):
        cols[f"S{i:02d}"] = 30 * np.cumprod(
            1 + m * rng.uniform(0.5, 1.5) + rng.normal(0, 0.02, n_days)
        )
    close = pd.DataFrame(cols, index=idx)
    opens = close.shift(1).bfill() * (1 + rng.normal(0, 0.005, close.shape))
    volume = pd.DataFrame(rng.uniform(1e5, 1e7, close.shape), index=idx, columns=close.columns)
    return Panel(open=opens, close=close, close_raw=close, volume_raw=volume)


def test_insider_study_end_to_end(tmp_path):
    p = market()
    rng = np.random.default_rng(2)
    events = pd.DataFrame(
        {
            "issuer_cik": range(60),
            "symbol": [f"S{i:02d}" for i in rng.integers(0, 40, 60)],
            "filing_date": p.sessions[rng.integers(255, 370, 60)],
            "insiders": rng.integers(2, 5, 60),
        }
    )
    rank = engine.universe_rank(p)
    beta = engine.rolling_beta(p.close, p.close["SPY"])
    trades = insiders.build_trades(events, p, rank, beta)
    assert (trades["exit_i"] - trades["entry_i"] == insiders.HOLD - 1).all()
    assert (p.sessions[trades["entry_i"]] > trades["filing_date"]).all()
    res, daily = engine.simulate(trades, p)
    out = insiders.write_report(
        pd.DataFrame(index=range(500)), events, res, daily, p, tmp_path / "I.md"
    )
    text = out.read_text()
    assert "## Verdict: **" in text and "By cluster size" in text


def test_earnings_study_end_to_end(tmp_path):
    p = market()
    rng = np.random.default_rng(3)
    n = 900
    days = p.sessions[rng.integers(252, 400, n)]
    accepted = pd.Series(days) + pd.to_timedelta(rng.choice([7 * 60, 16 * 60 + 5], n), unit="min")
    events = pd.DataFrame(
        {"symbol": [f"S{i:02d}" for i in rng.integers(0, 40, n)], "accepted": accepted}
    )
    rank = engine.universe_rank(p)
    beta = engine.rolling_beta(p.close, p.close["SPY"])
    ev, trades = earnings.build_trades(events, p, rank, beta)
    assert ev["pct"].notna().sum() > 0 and len(trades) > 0
    assert set(trades["direction"]) <= {1, -1}
    assert (trades["exit_i"] - trades["day0_i"] == earnings.EXIT_LAG).all()
    res, daily = engine.simulate(trades, p)
    out = earnings.write_report(events, ev, res, daily, p, tmp_path / "E.md")
    assert "acceptance times" in out.read_text()


def test_news_study_end_to_end(tmp_path):
    p = market()
    p.save(tmp_path / "panel")
    rng = np.random.default_rng(4)
    n = 6000
    day = p.sessions[rng.integers(260, 410, n)]
    ts = (pd.Series(day).dt.tz_localize("America/New_York") + pd.Timedelta(hours=7)).dt.tz_convert(
        "UTC"
    )
    heads = pd.DataFrame(
        {
            "date": pd.Series(day).to_numpy(),
            "ts": ts.where(rng.uniform(size=n) < 0.3),
            "symbol": [f"S{i:02d}" for i in rng.integers(0, 40, n)],
            "h": rng.integers(0, 3000, n).astype("uint64"),
        }
    )
    prep = tmp_path / "prep"
    prep.mkdir()
    heads.to_pickle(prep / "headlines.pkl")
    stats = {
        "rows": n,
        "benzinga_2016_on": n,
        "headlines": n,
        "timed_share": 0.3,
        "unique_titles": 3000,
        "symbols": 40,
        "first": "2020-01-01",
        "last": "2020-08-01",
        "roundup_dropped": 0,
        "hour_profile_et": {"07": 1.0},
        "schedule_check": {
            "Mid-Day Market Update": {"n": 5, "median_et": 12.1, "expected_et": 12.0}
        },
    }
    (prep / "prep.json").write_text(__import__("json").dumps(stats))
    scores = pd.DataFrame(
        {
            "h": np.arange(3000, dtype="uint64"),
            "finbert": rng.uniform(-1, 1, 3000),
            "lm": rng.normal(0, 0.05, 3000),
        }
    )
    scores.to_pickle(tmp_path / "s0.pkl")
    out = news.run_study(prep, [tmp_path / "s0.pkl"], tmp_path / "panel", None, tmp_path / "N.md")
    text = out.read_text()
    assert "Loughran–McDonald" in text and "timed rows only" in text and "## Verdict: **" in text
    assert "Mid-Day Market Update" in text


def test_fnspid_prep_benzinga_only_shifted_and_filtered(tmp_path):
    p = market()
    p.save(tmp_path / "panel")
    bz = "https://www.benzinga.com/news/1"
    rows = [
        # Date, title, symbol, url
        ("2020-06-05 08:45:06 UTC", "S00 Stocks Moving In Friday's Mid-Day Session", "S00", bz),
        ("2020-06-05 00:00:00 UTC", "S01 raises full-year guidance on strong demand", "S01", bz),
        (
            "2020-06-05 00:00:00 UTC",
            "Reuters says S02 shares jump on takeover talk",
            "S02",
            "https://www.reuters.com/x",
        ),
        ("2020-06-05 00:00:00 UTC", "Too short", "S03", bz),
        ("2020-06-05 00:00:00 UTC", "Market round-up of the biggest movers today", "S04", bz),
        ("2020-06-05 00:00:00 UTC", "Market round-up of the biggest movers today", "S05", bz),
        ("2020-06-05 00:00:00 UTC", "Market round-up of the biggest movers today", "S06", bz),
        ("2015-06-05 00:00:00 UTC", "Old news from before the study window starts", "S07", bz),
        ("2020-06-05 00:00:00 UTC", "Unknown ticker gets a brand new headline", "ZZZZ", bz),
    ]
    frame = pd.DataFrame(rows, columns=["Date", "Article_title", "Stock_symbol", "Url"])
    frame.assign(Publisher="x", Article="body, with a comma").to_csv(
        tmp_path / "f.csv", index=False
    )
    stats = news.prep_fnspid(tmp_path / "f.csv", tmp_path / "panel", tmp_path / "out")
    heads = pd.read_pickle(tmp_path / "out" / "headlines.pkl")
    assert sorted(heads["symbol"]) == ["S00", "S01"]
    assert stats["roundup_dropped"] == 3 and stats["benzinga_2016_on"] == 7
    timed = heads.dropna(subset=["ts"]).iloc[0]
    assert timed["ts"] == pd.Timestamp("2020-06-05 16:45:06", tz="UTC")  # +8 h
    assert (heads["date"] == pd.Timestamp("2020-06-05")).all()
    assert stats["schedule_check"]["Mid-Day Session"]["median_et"] == pytest.approx(12.75)
    assert len(pd.read_pickle(tmp_path / "out" / "titles.pkl")) == 2
