"""Event-study engine shared by the pre-registered studies.

Every rule here is fixed by docs/research/PREREGISTRATION.md ("Rules common to all
three"): the point-in-time liquidity universe, the 250-session beta, the SPY hedge,
costs, the calendar-time portfolio and the bootstrap ranges. Studies only decide
*which* trades to take; this module decides how they are scored.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..report import _md_table
from .prices import Panel

SLIPPAGE_BPS = 5.0  # per side, stock
HEDGE_BPS = 1.0  # per side, SPY hedge (scaled by beta)
BOOT_N = 4000
SEED = 0


def universe_rank(
    panel: Panel, min_price: float = 5.0, min_history: int = 250, window: int = 60
) -> pd.DataFrame:
    """Rank (1 = most liquid) by median dollar volume over the `window` sessions *before*
    each date; NaN where the stock fails the price or history screen. Unadjusted prices."""
    dv = (panel.close_raw * panel.volume_raw).astype("float64")
    # Median of the sessions the stock actually traded in the window; 2/3 required.
    med = dv.rolling(window, min_periods=window * 2 // 3).median().shift(1)
    seen = panel.close_raw.notna().cumsum().shift(1)
    ok = (panel.close_raw.shift(1) >= min_price) & (seen >= min_history)
    return med.where(ok).rank(axis=1, ascending=False, method="first")


def rolling_beta(
    close: pd.DataFrame,
    spy: pd.Series,
    window: int = 250,
    min_obs: int = 120,
    clip: tuple[float, float] = (0.0, 3.0),
) -> pd.DataFrame:
    """Slope of daily close-to-close returns on SPY's over the `window` sessions before
    each date (row t uses data through t-1); 1.0 where fewer than `min_obs` days."""
    close = close.astype("float64")
    r = close / close.shift(1) - 1
    m = spy.astype("float64") / spy.astype("float64").shift(1) - 1
    have = r.notna() & np.broadcast_to(m.notna().to_numpy()[:, None], r.shape)
    r = r.where(have)
    mm = have.astype("float64").mul(m, axis=0).where(have)

    def roll(x: pd.DataFrame) -> pd.DataFrame:
        return x.rolling(window, min_periods=min_obs).sum()

    n = roll(have.astype("float64"))
    s_r, s_m = roll(r), roll(mm)
    cov = roll(r * mm) - s_r * s_m / n
    var = roll(mm * mm) - s_m**2 / n
    beta = (cov / var).clip(*clip)
    return beta.shift(1).fillna(1.0)


def lookup(frame: pd.DataFrame, symbols, rows) -> np.ndarray:
    """frame.iloc[row, column-of-symbol] for many pairs at once; NaN for unknown symbols."""
    cols = frame.columns.get_indexer(pd.Index(symbols))
    rows = np.asarray(rows, dtype=int)
    vals = frame.to_numpy()[rows, np.where(cols < 0, 0, cols)].astype("float64")
    return np.where(cols < 0, np.nan, vals)


def _ffill(a: np.ndarray) -> np.ndarray:
    idx = np.where(np.isnan(a), 0, np.arange(len(a)))
    return a[np.maximum.accumulate(idx)]


def simulate(
    trades: pd.DataFrame,
    panel: Panel,
    slippage_bps: float = SLIPPAGE_BPS,
    hedge_bps: float = HEDGE_BPS,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Score trades against an opposite beta × notional SPY position.

    `trades` needs symbol, entry_i, exit_i (session positions), entry_at ("open" or
    "close"; exits are always at the close), direction (+1/-1) and beta. Returns the
    per-trade frame with stock_ret, spy_ret, adj_ret (net, market-adjusted), days and
    last_i — or NaN when there was no entry price — plus a long frame of daily
    market-adjusted returns (day_i, trade, ret) for the calendar-time portfolio.
    """
    O = panel.open.to_numpy()
    C = panel.close.to_numpy()
    cols = panel.close.columns.get_indexer(pd.Index(trades["symbol"]))
    spy_o = panel.open["SPY"].to_numpy(dtype="float64")
    spy_c = panel.close["SPY"].to_numpy(dtype="float64")
    s_cost, h_cost = slippage_bps / 1e4, hedge_bps / 1e4

    out = {k: np.full(len(trades), np.nan) for k in ("stock_ret", "spy_ret", "adj_ret", "days")}
    out["last_i"] = np.full(len(trades), -1)
    day_parts, trade_parts, ret_parts = [], [], []
    it = zip(
        cols,
        trades["entry_i"],
        trades["exit_i"],
        trades["entry_at"],
        trades["direction"],
        trades["beta"],
        strict=True,
    )
    for k, (j, e, x, at, d, b) in enumerate(it):
        if j < 0:
            continue
        closes = C[e : x + 1, j].astype("float64")
        valid = np.flatnonzero(~np.isnan(closes))
        if not len(valid) or valid[0] != 0:
            continue  # no close on the entry session — never entered
        last = int(valid[-1])  # bars stop mid-hold → exit at the last close
        px = _ffill(closes[: last + 1])
        if at == "open":
            if np.isnan(O[e, j]):
                continue
            path = np.concatenate([[float(O[e, j])], px])
            spath = np.concatenate([[spy_o[e]], spy_c[e : e + last + 1]])
            days = np.arange(e, e + last + 1)
        else:
            if last == 0:
                continue  # entered at the close and gone before the next one
            path, spath = px, spy_c[e : e + last + 1]
            days = np.arange(e + 1, e + last + 1)
        rs = path[1:] / path[:-1] - 1
        rm = spath[1:] / spath[:-1] - 1
        cost = s_cost + b * h_cost
        daily = d * (rs - b * rm)
        daily[0] -= cost
        daily[-1] -= cost
        stock_ret, spy_ret = path[-1] / path[0] - 1, spath[-1] / spath[0] - 1
        out["stock_ret"][k], out["spy_ret"][k] = stock_ret, spy_ret
        out["adj_ret"][k] = d * (stock_ret - b * spy_ret) - 2 * cost
        out["days"][k] = len(days)
        out["last_i"][k] = days[-1]
        day_parts.append(days)
        trade_parts.append(np.full(len(days), k))
        ret_parts.append(daily)

    result = trades.reset_index(drop=True).assign(**out)
    daily = pd.DataFrame(
        {
            "day_i": np.concatenate(day_parts) if day_parts else np.array([], dtype=int),
            "trade": np.concatenate(trade_parts) if trade_parts else np.array([], dtype=int),
            "ret": np.concatenate(ret_parts) if ret_parts else np.array([]),
        }
    )
    return result, daily


def portfolio(
    daily: pd.DataFrame, sessions: pd.DatetimeIndex, span: tuple[int, int] | None = None
) -> pd.Series:
    """Equal weight across positions open each day; 0 on days with none, over `span`
    (session positions, inclusive) or from the first to the last day with a position."""
    if span is None:
        if daily.empty:
            return pd.Series(dtype="float64")
        span = (int(daily["day_i"].min()), int(daily["day_i"].max()))
    mean = daily.groupby("day_i")["ret"].mean()
    s = mean.reindex(range(span[0], span[1] + 1), fill_value=0.0)
    return pd.Series(s.to_numpy(), index=sessions[s.index], name="ret")


def boot_ci(x: np.ndarray, n: int = BOOT_N, seed: int = SEED) -> tuple[float, float]:
    """95% bootstrap range of the mean (resampling the given units with replacement)."""
    x = np.asarray(x, dtype="float64")
    if len(x) < 2:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    means = np.empty(n)
    for s in range(0, n, 500):
        m = min(500, n - s)
        means[s : s + m] = x[rng.integers(0, len(x), (m, len(x)))].mean(axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def sharpe(x: pd.Series) -> float:
    sd = x.std(ddof=1)
    return float(x.mean() / sd * np.sqrt(252)) if sd > 0 else float("nan")


def monthly(daily_ret: pd.Series) -> pd.Series:
    return (1 + daily_ret).groupby(daily_ret.index.to_period("M")).prod() - 1


def summarize(port: pd.Series) -> dict:
    """Headline numbers for a daily portfolio series."""
    lo, hi = boot_ci(port.to_numpy())
    mon = monthly(port) if len(port) else pd.Series(dtype="float64")
    mlo, mhi = boot_ci(mon.to_numpy())
    return {
        "days": len(port),
        "active_days": int((port != 0).sum()),
        "mean_daily": float(port.mean()) if len(port) else float("nan"),
        "lo_daily": lo,
        "hi_daily": hi,
        "sharpe": sharpe(port) if len(port) > 1 else float("nan"),
        "months": len(mon),
        "mean_monthly": float(mon.mean()) if len(mon) else float("nan"),
        "lo_monthly": mlo,
        "hi_monthly": mhi,
    }


def bp(x: float) -> str:
    return "—" if pd.isna(x) else f"{x * 1e4:+.1f} bp"


def pct(x: float) -> str:
    return "—" if pd.isna(x) else f"{x * 100:+.2f}%"


def num(x: float, places: int = 2) -> str:
    return "—" if pd.isna(x) else f"{x:+.{places}f}"


def breakdown(
    results: pd.DataFrame,
    daily: pd.DataFrame,
    by: pd.Series,
    sessions: pd.DatetimeIndex,
    span: tuple[int, int],
    label: str,
) -> str:
    """Markdown table: for each group of trades, its own calendar-time portfolio."""
    rows = []
    for key, idx in results.groupby(by.to_numpy(), sort=True).groups.items():
        sub = results.loc[idx]
        port = portfolio(daily[daily["trade"].isin(idx)], sessions, span)
        s = summarize(port)
        rows.append(
            {
                label: str(key),
                "trades": f"{sub['adj_ret'].notna().sum():,}",
                "mean per trade": pct(sub["adj_ret"].mean()),
                "win rate": f"{(sub['adj_ret'] > 0).mean():.0%}",
                "daily mean": bp(s["mean_daily"]),
                "95% range (daily)": f"{bp(s['lo_daily'])} to {bp(s['hi_daily'])}",
                "Sharpe": num(s["sharpe"]),
            }
        )
    return _md_table(pd.DataFrame(rows)) if rows else "_no trades_"


def by_year(port: pd.Series) -> str:
    rows = [
        {
            "year": str(year),
            "days with positions": f"{int((p != 0).sum()):,}",
            "daily mean": bp(p.mean()),
            "Sharpe": num(sharpe(p)),
            "year total": pct(float((1 + p).prod() - 1)),
        }
        for year, p in port.groupby(port.index.year)
    ]
    return _md_table(pd.DataFrame(rows)) if rows else "_no data_"


def decide(s: dict, min_sharpe: float, monthly_rule: bool = False) -> tuple[bool, str]:
    """Apply a pre-registered pass rule; returns (passed, the reason in words)."""
    if monthly_rule:
        ci_ok = s["mean_monthly"] > 0 and s["lo_monthly"] > 0
        ci_text = (
            f"mean monthly return {pct(s['mean_monthly'])}, month-resampled 95% range "
            f"{pct(s['lo_monthly'])} to {pct(s['hi_monthly'])}"
        )
    else:
        ci_ok = s["lo_daily"] > 0
        ci_text = (
            f"mean daily return {bp(s['mean_daily'])}, day-resampled 95% range "
            f"{bp(s['lo_daily'])} to {bp(s['hi_daily'])}"
        )
    sr_ok = s["sharpe"] >= min_sharpe
    name = "IR" if monthly_rule else "Sharpe"
    passed = bool(ci_ok and sr_ok)
    reason = (
        f"{ci_text} ({'above zero' if ci_ok else 'not entirely above zero'}); "
        f"annualised {name} {num(s['sharpe'])} (needs ≥ {min_sharpe})"
    )
    return passed, reason
