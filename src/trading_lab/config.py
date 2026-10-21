"""Run configuration."""

from dataclasses import dataclass, field

# Liquid, volatile large caps — a pragmatic stand-in for Warrior-Trading-style
# small-cap gappers, which free historical data can't screen for (see README).
# Ten names across sectors (2026-10-21). The original six (TSLA, NVDA, AMD,
# PLTR, COIN, MSTR) were all high-beta tech/crypto moving 1.8-2.9x SPY
# intraday, so every strategy was really the same market-direction bet.
DEFAULT_SYMBOLS = ["NVDA", "TSLA", "COIN", "AMZN", "JPM", "XOM", "UNH", "WMT", "CAT", "LLY"]


@dataclass(frozen=True)
class Config:
    symbols: list[str] = field(default_factory=lambda: list(DEFAULT_SYMBOLS))
    interval: str = "5m"
    period: str = "60d"  # yfinance caps 5m history at 60 calendar days
    notional_per_trade: float = 10_000.0  # dollars committed per trade
    slippage_bps: float = 5.0  # applied to entry and exit fills
    hedge_slippage_bps: float = 1.0  # SPY is far more liquid than the traded names
    max_trades_per_day: int = 3  # hard cap per strategy+symbol (strategies may use fewer)
    # Cap on total open notional per symbol in live paper trading. With ~25
    # strategy variants able to agree on one signal bar, a crowded name could
    # otherwise stack 10x notional in one symbol (PLTR, 2026-09-17). ~3 trades'
    # worth keeps a little agreement while bounding single-symbol exposure.
    max_symbol_notional: float = 30_000.0
    # Live variants and gates switched OFF on 2026-10-21 (code kept): the
    # SPY-adjusted review showed tuned variants (-$15.52/trade raw), regime
    # variants (-$31.63) and the long gate's apparent benefit were all either
    # losing or explained by intraday market direction. Re-enable to retest.
    trade_tuned_variants: bool = False
    trade_regime_variants: bool = False
    long_gate: str = "none"  # "regime": longs only when the regime filter's EV > 0
    long_gate_exempt: tuple[str, ...] = ("orb",)
    entry_cutoff: str = "15:30"  # no new entries at/after this bar (US/Eastern)
    eod_cutoff: str = "15:55"  # flatten everything at/after this bar (US/Eastern)
    # Volatility-scaled risk (opt-in experiment, off by default). When on:
    # percent-stops become ATR stops sized off the signal bar, and shares are
    # sized to a fixed dollar risk instead of a fixed notional. Structural
    # stops (absolute stop_price levels) are left where the strategy put them.
    vol_sizing: bool = False
    risk_per_trade: float = 100.0  # dollars at risk to the stop (= old 1% of $10k)
    stop_atr_mult: float = 1.5  # stop distance = mult x ATR(14) at the signal bar
