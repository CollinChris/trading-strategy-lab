import numpy as np
import pandas as pd
import pytest


def make_day(opens, highs, lows, closes, volumes=None, date="2026-08-17"):
    """Build a synthetic 5-minute session starting 09:30 America/New_York."""
    n = len(opens)
    index = pd.date_range(f"{date} 09:30", periods=n, freq="5min", tz="America/New_York")
    return pd.DataFrame(
        {
            "open": np.asarray(opens, dtype=float),
            "high": np.asarray(highs, dtype=float),
            "low": np.asarray(lows, dtype=float),
            "close": np.asarray(closes, dtype=float),
            "volume": np.asarray(volumes if volumes is not None else [1000] * n, dtype=float),
        },
        index=index,
    )


@pytest.fixture
def flat_day():
    """A do-nothing session: price pinned at 100 for 20 bars."""
    n = 20
    return make_day([100] * n, [100.5] * n, [99.5] * n, [100] * n)
