"""Command-line entry point: `trading-lab backtest|tune|regime|paper|journal`."""

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

    rg = sub.add_parser(
        "regime",
        help="learn when each strategy wins from the trade journal, validated walk-forward",
    )
    rg.add_argument("--trades", default="results/trades.csv")
    rg.add_argument("--journal", default="results/paper_journal.csv")
    rg.add_argument(
        "--min-train", type=int, default=20, help="sessions before the first test block"
    )
    rg.add_argument("--block", type=int, default=5, help="sessions per walk-forward test block")
    rg.add_argument(
        "--model",
        nargs="*",
        default=["hgb_reg", "ridge", "hgb", "logit"],
        choices=["hgb_reg", "ridge", "hgb", "logit"],
        help="filters to evaluate (first is the primary in the report)",
    )

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

    elif args.command == "regime":
        from pathlib import Path

        from .regime import run_regime

        path = run_regime(
            trades_path=Path(args.trades),
            journal_path=Path(args.journal),
            min_train=args.min_train,
            block=args.block,
            kinds=tuple(args.model),
        )
        print(f"\nRegime report → {path}")

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
