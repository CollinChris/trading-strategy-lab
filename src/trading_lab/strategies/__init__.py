"""Strategy registry."""

from .ar_forecast import ArForecast
from .base import EntrySignal, Strategy
from .ema_crossover import EmaCrossover
from .gap_and_go import GapAndGo
from .high_break_trail import HighBreakTrail
from .news_momentum import NewsMomentum
from .orb import OpeningRangeBreakout
from .rsi_reversion import RsiReversion
from .squeeze_breakout import SqueezeBreakout
from .vwap_pullback import VwapPullback


def all_strategies(news_index=None) -> list[Strategy]:
    """Fresh instances of the nine strategies under test."""
    return [
        GapAndGo(),
        OpeningRangeBreakout(),
        VwapPullback(),
        EmaCrossover(),
        RsiReversion(),
        NewsMomentum(news_index=news_index),
        SqueezeBreakout(),
        HighBreakTrail(),
        ArForecast(),
    ]


__all__ = [
    "ArForecast",
    "EmaCrossover",
    "EntrySignal",
    "GapAndGo",
    "HighBreakTrail",
    "NewsMomentum",
    "OpeningRangeBreakout",
    "RsiReversion",
    "SqueezeBreakout",
    "Strategy",
    "VwapPullback",
    "all_strategies",
]
