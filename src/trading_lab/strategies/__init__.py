"""Strategy registry."""

import inspect

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


def all_strategies(news_index=None, tuned: dict[str, dict] | None = None) -> list[Strategy]:
    """Fresh instances of the nine strategies under test.

    `tuned` maps a strategy name to a parameter dict (the weekly tune's
    results/tuned_params.json). Each entry adds a SECOND instance named
    `<name>_tuned` trading alongside the default — a live A/B of whether the
    weekly re-tune helps. Entries whose params equal the class defaults are
    skipped: they would just duplicate the base instance's orders.
    """
    base = [
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
    for name, params in (tuned or {}).items():
        cls = next((type(s) for s in base if s.name == name), None)
        if cls is None:
            continue
        defaults = {
            k: p.default
            for k, p in inspect.signature(cls.__init__).parameters.items()
            if p.default is not inspect.Parameter.empty
        }
        if all(defaults.get(k) == v for k, v in params.items()):
            continue
        kwargs = dict(params)
        if name == "news_momentum":
            kwargs["news_index"] = news_index
        variant = cls(**kwargs)
        variant.name = f"{name}_tuned"
        base.append(variant)
    return base


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
