"""Strategy registry."""

from .base import EntrySignal, Strategy
from .ema_crossover import EmaCrossover
from .gap_and_go import GapAndGo
from .orb import OpeningRangeBreakout
from .rsi_reversion import RsiReversion
from .vwap_pullback import VwapPullback


def all_strategies() -> list[Strategy]:
    """Fresh instances of the five strategies under test."""
    return [
        GapAndGo(),
        OpeningRangeBreakout(),
        VwapPullback(),
        EmaCrossover(),
        RsiReversion(),
    ]


__all__ = [
    "EmaCrossover",
    "EntrySignal",
    "GapAndGo",
    "OpeningRangeBreakout",
    "RsiReversion",
    "Strategy",
    "VwapPullback",
    "all_strategies",
]
