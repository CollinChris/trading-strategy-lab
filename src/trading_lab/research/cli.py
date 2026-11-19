"""`trading-lab research ...` — the pre-registered studies' commands (run on Actions)."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path

PANEL = "data/research/panel"


def add_parser(sub) -> None:
    rs = sub.add_parser("research", help="pre-registered event studies (GitHub Actions)")
    cmd = rs.add_subparsers(dest="research_command", required=True)

    b = cmd.add_parser("bars", help="daily price panel for every listed US stock")
    b.add_argument("--start", default="2015-01-01", help="2015 warms up the 2016 screens")
    b.add_argument("--end", default=None, help="default: yesterday (New York)")
    b.add_argument("--out", default=PANEL)

    for name, text in [
        ("insiders", "study A: insider cluster purchases → results/INSIDERS.md"),
        ("earnings", "study B: earnings-reaction drift → results/EARNINGS.md"),
    ]:
        p = cmd.add_parser(name, help=text)
        p.add_argument("--panel", default=PANEL)

    np_ = cmd.add_parser("news-prep", help="study C: filter FNSPID headlines, plan scoring shards")
    np_.add_argument("csv", help="FNSPID Stock_news/All_external.csv")
    np_.add_argument("--panel", default=PANEL)
    np_.add_argument("--out", default="data/research/news")

    ns = cmd.add_parser("news-score", help="study C: FinBERT + LM scores for one shard")
    ns.add_argument("--prep", default="data/research/news")
    ns.add_argument("--shard", type=int, required=True)
    ns.add_argument("--of", type=int, required=True)
    ns.add_argument("--out", required=True)

    st = cmd.add_parser("news-study", help="study C: score the book → results/NEWS.md")
    st.add_argument("scores", nargs="+", help="shard score pickles")
    st.add_argument("--prep", default="data/research/news")
    st.add_argument("--panel", default=PANEL)
    st.add_argument("--archive", default=None, help="news-archive checkout (forward sample)")

    na = cmd.add_parser("news-archive", help="append scored Alpaca headlines (no text kept)")
    na.add_argument("--dir", required=True)
    na.add_argument("--max-days", type=int, default=90, help="catch-up limit per run")


def dispatch(args: argparse.Namespace) -> None:
    c = args.research_command
    if c == "bars":
        from ..data import market_today
        from .prices import fetch_panel

        end = dt.date.fromisoformat(args.end) if args.end else market_today() - dt.timedelta(days=1)
        path = fetch_panel(dt.date.fromisoformat(args.start), end).save(Path(args.out))
        print(f"Panel → {path}")
    elif c == "insiders":
        from .insiders import run

        print(f"Insiders → {run(Path(args.panel))}")
    elif c == "earnings":
        from .earnings import run

        print(f"Earnings → {run(Path(args.panel))}")
    elif c == "news-prep":
        from .news import prep_fnspid

        stats = prep_fnspid(Path(args.csv), Path(args.panel), Path(args.out))
        if out := os.environ.get("GITHUB_OUTPUT"):
            with open(out, "a") as fh:
                fh.write(f"shards={json.dumps(list(range(stats['shards'])))}\n")
                fh.write(f"n_shards={stats['shards']}\n")
    elif c == "news-score":
        from .news import score_shard

        print(f"Scores → {score_shard(Path(args.prep), args.shard, args.of, Path(args.out))}")
    elif c == "news-study":
        from .news import run_study

        path = run_study(
            Path(args.prep),
            [Path(p) for p in args.scores],
            Path(args.panel),
            Path(args.archive) if args.archive else None,
        )
        print(f"News study → {path}")
    elif c == "news-archive":
        from .news import archive

        print(f"Archived {archive(Path(args.dir), max_days=args.max_days)} new headlines")
