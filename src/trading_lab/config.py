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
