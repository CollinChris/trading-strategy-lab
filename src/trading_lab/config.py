"""Run configuration."""

from dataclasses import dataclass, field

# Liquid, volatile large caps — a pragmatic stand-in for Warrior-Trading-style
# small-cap gappers, which free historical data can't screen for (see README).
DEFAULT_SYMBOLS = ["TSLA", "NVDA", "AMD", "PLTR", "COIN", "MSTR"]


@dataclass(frozen=True)
class Config:
    symbols: list[str] = field(default_factory=lambda: list(DEFAULT_SYMBOLS))
    interval: str = "5m"
    period: str = "60d"  # yfinance caps 5m history at 60 calendar days
    notional_per_trade: float = 10_000.0  # dollars committed per trade
    slippage_bps: float = 5.0  # applied to entry and exit fills
    max_trades_per_day: int = 3  # hard cap per strategy+symbol (strategies may use fewer)
    entry_cutoff: str = "15:30"  # no new entries at/after this bar (US/Eastern)
    eod_cutoff: str = "15:55"  # flatten everything at/after this bar (US/Eastern)
    # Volatility-scaled risk (opt-in experiment, off by default). When on:
    # percent-stops become ATR stops sized off the signal bar, and shares are
    # sized to a fixed dollar risk instead of a fixed notional. Structural
    # stops (absolute stop_price levels) are left where the strategy put them.
    vol_sizing: bool = False
    risk_per_trade: float = 100.0  # dollars at risk to the stop (= old 1% of $10k)
    stop_atr_mult: float = 1.5  # stop distance = mult x ATR(14) at the signal bar
