"""Command-line entry point: `trading-lab backtest` and `trading-lab paper`."""

from __future__ import annotations

import argparse

from .config import DEFAULT_SYMBOLS, Config


def main() -> None:
    parser = argparse.ArgumentParser(prog="trading-lab")
    sub = parser.add_subparsers(dest="command", required=True)

    bt = sub.add_parser("backtest", help="run all five strategies and write results/")
    bt.add_argument("--symbols", nargs="*", default=DEFAULT_SYMBOLS)
    bt.add_argument("--interval", default="5m")
    bt.add_argument("--period", default="60d")
    bt.add_argument(
        "--vol-sizing", action="store_true", help="ATR stops + fixed dollar risk per trade"
    )

    tn = sub.add_parser("tune", help="grid-search parameters on a train split, validate held-out")
    tn.add_argument("--symbols", nargs="*", default=DEFAULT_SYMBOLS)
    tn.add_argument("--train-frac", type=float, default=0.6)

    pp = sub.add_parser("paper", help="scan latest bars and place Alpaca paper orders")
    pp.add_argument("--dry-run", action="store_true", help="print orders instead of submitting")
    pp.add_argument(
        "--vol-sizing", action="store_true", help="ATR stops + fixed dollar risk per trade"
    )
    pp.add_argument("--flatten", action="store_true", help="close all paper positions/orders")
    pp.add_argument("--status", action="store_true", help="show paper positions and open orders")

    sub.add_parser(
        "journal", help="append today's filled paper trades to results/paper_journal.csv"
    )

    args = parser.parse_args()

    if args.command == "backtest":
        from .backtest import run_backtest
        from .metrics import summarize
        from .report import write_report

        cfg = Config(
            symbols=args.symbols,
            interval=args.interval,
            period=args.period,
            vol_sizing=args.vol_sizing,
        )
        trades = run_backtest(cfg)
        if trades.empty:
            print("No trades generated — check symbols/period.")
            return
        summary = summarize(trades)
        path = write_report(trades, summary, cfg)
        print(summary.to_string(index=False))
        print(f"\n{len(trades)} trades → {path}")

    elif args.command == "tune":
        from .tune import tune

        path = tune(Config(symbols=args.symbols), train_frac=args.train_frac)
        print(f"\nTuning report → {path}")

    elif args.command == "paper":
        from . import paper

        if args.flatten:
            paper.flatten()
        elif args.status:
            paper.status()
        else:
            paper.scan_and_trade(Config(vol_sizing=args.vol_sizing), dry_run=args.dry_run)

    elif args.command == "journal":
        from . import paper

        paper.journal(Config())


if __name__ == "__main__":
    main()
