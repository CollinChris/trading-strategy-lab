"""Option-selling strategies on 40 years of free Cboe benchmark history —
results/OPTIONS.md. A desk study, separate from the stock lab's data.

Cboe publishes daily levels for the classic premium-selling benchmarks: PUT
(monthly at-the-money put-write), BXM / BXMD (covered calls), CNDR (iron
condor), WPUT (weekly put-write), PPUT (protective put). Every one is judged
the way the stock strategies are: return beyond its market exposure (CAPM
alpha against the S&P 500 total return), not raw return — a put-writer earns
much of its return simply by being ~0.6x long stocks.

The timing test is walk-forward: in each month the put-write is held only if
last month's volatility risk premium (VIX minus SPX realised vol) was above
its own expanding median — computed from past months only.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import numpy as np
import pandas as pd

from .data import market_today
from .report import _md_table

CBOE_URL = "https://cdn.cboe.com/api/global/us_indices/daily_prices/{name}_History.csv"
CACHE = Path("data/cboe")
STRATEGIES = {
    "PUT": "Monthly ATM put-write",
    "WPUT": "Weekly ATM put-write",
    "BXM": "Covered call (ATM, monthly)",
    "BXMD": "Covered call (30-delta)",
    "CNDR": "Iron condor",
    "PPUT": "Protective put (5% OTM)",
}
EPISODES = {
    "2008 crisis": ("2007-10-01", "2009-03-31"),
    "Feb 2018 'Volmageddon'": ("2018-01-15", "2018-04-30"),
    "2020 COVID crash": ("2020-02-15", "2020-04-30"),
    "2022 bear market": ("2022-01-01", "2022-10-31"),
}


def load_cboe(name: str, max_age_days: int = 7) -> pd.Series:
    """Daily closing level of a Cboe index, cached under data/cboe/."""
    import requests

    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{name}.csv"
    stale = (
        not path.exists()
        or (dt.date.today() - dt.date.fromtimestamp(path.stat().st_mtime)).days > max_age_days
    )
    if stale:
        r = requests.get(
            CBOE_URL.format(name=name), timeout=60, headers={"User-Agent": "Mozilla/5.0"}
        )
        r.raise_for_status()
        if not r.text.startswith("DATE"):
            raise RuntimeError(f"Cboe {name}: unexpected response ({r.text[:60]!r})")
        path.write_text(r.text)
    df = pd.read_csv(path)
    col = "CLOSE" if "CLOSE" in df.columns else df.columns[1]
    s = pd.Series(
        df[col].astype(float).to_numpy(),
        index=pd.to_datetime(df["DATE"], format="%m/%d/%Y"),
        name=name,
    )
    s = s[s > 0].sort_index()
    # Keep only the stretch where the series is truly daily. PUT, for one, has
    # a handful of scattered points before 2007; forward-filling them makes
    # months of fake zero returns that fake a low beta and a high alpha.
    gaps = s.index.to_series().diff().dt.days
    big = gaps[gaps > 7]
    return s if big.empty else s[big.index[-1] :]


def load_market() -> tuple[pd.Series, pd.Series]:
    """S&P 500 total-return index and the 13-week T-bill yield (annual %)."""
    import yfinance as yf

    raw = yf.download(["^SP500TR", "^IRX"], start="1988-01-01", progress=False, auto_adjust=False)[
        "Close"
    ]
    raw.index = pd.to_datetime(raw.index).tz_localize(None)
    return raw["^SP500TR"].dropna().rename("SPXTR"), raw["^IRX"].dropna().rename("IRX")


def monthly(levels: pd.DataFrame) -> pd.DataFrame:
    return levels.sort_index().ffill().resample("ME").last()


def capm(excess: pd.Series, market_excess: pd.Series) -> dict:
    """OLS of monthly excess returns on the market's. Alpha annualised (x12)."""
    df = pd.concat([excess, market_excess], axis=1).dropna()
    if len(df) < 24:
        return {"months": len(df), "beta": np.nan, "alpha": np.nan, "t": np.nan}
    y, x = df.iloc[:, 0].to_numpy(), df.iloc[:, 1].to_numpy()
    X = np.column_stack([np.ones_like(x), x])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ coef
    se = np.sqrt(resid.var(ddof=2) * np.linalg.inv(X.T @ X)[0, 0])
    return {"months": len(df), "beta": coef[1], "alpha": coef[0] * 12, "t": coef[0] / se}


def stats(returns: pd.Series, rf: pd.Series) -> dict:
    r = returns.dropna()
    ex = (r - rf.reindex(r.index)).dropna()
    years = len(r) / 12
    wealth = (1 + r).cumprod()
    return {
        "cagr": wealth.iloc[-1] ** (1 / years) - 1 if years > 0 else np.nan,
        "sharpe": ex.mean() / ex.std(ddof=1) * np.sqrt(12) if len(ex) > 2 else np.nan,
        "max_dd": (wealth / wealth.cummax() - 1).min(),
    }


def vrp_signal(vix: pd.Series, spx: pd.Series) -> pd.Series:
    """Month-end VIX minus SPX's trailing 21-day realised vol (annualised %)."""
    rv = np.log(spx).diff().rolling(21).std() * np.sqrt(252) * 100
    return monthly(pd.concat([vix.rename("vix"), rv.rename("rv")], axis=1)).eval("vix - rv")


def timed_putwrite(
    put_ret: pd.Series, rf: pd.Series, signal: pd.Series, min_history: int = 60
) -> pd.Series:
    """Hold the put-write in month t only if the signal at the end of month
    t-1 was at or above the expanding median of all earlier signals (no
    lookahead); otherwise earn the T-bill rate."""
    sig = signal.reindex(put_ret.index)
    known = sig.shift(1)  # the signal as of the previous month-end
    threshold = sig.expanding(min_periods=min_history).median().shift(1)
    valid = known.notna() & threshold.notna()
    invest = valid & (known >= threshold)
    return put_ret.where(invest, rf.reindex(put_ret.index)).where(valid)


def _pct(x: float, digits: int = 1) -> str:
    return "—" if pd.isna(x) else f"{x * 100:+.{digits}f}%"


def build(out: Path = Path("results/OPTIONS.md")) -> Path:
    idx = {n: load_cboe(n) for n in [*STRATEGIES, "VIX", "SPX"]}
    spxtr, irx = load_market()
    m = monthly(pd.concat([*(idx[n] for n in STRATEGIES), spxtr], axis=1))
    rets = m.pct_change()
    rf = (monthly(irx.to_frame())["IRX"].shift(1) / 100 / 12).reindex(rets.index)
    mkt_ex = rets["SPXTR"] - rf

    periods = {"full history": "1988-01-01", "since 2007": "2007-01-01", "last 10 years": None}
    ten_years = (rets.index[-1] - pd.DateOffset(years=10)).strftime("%Y-%m-%d")
    rows = []
    for name, label in STRATEGIES.items():
        for period, start in periods.items():
            s = start or ten_years
            r = rets[name][s:].dropna()
            if len(r) < 24:
                continue
            reg, st = capm(r - rf.reindex(r.index), mkt_ex), stats(r, rf)
            rows.append(
                {
                    "strategy": f"{label} ({name})",
                    "period": period,
                    "from": f"{r.index[0]:%Y-%m}",
                    "months": reg["months"],
                    "CAGR": _pct(st["cagr"]),
                    "max drawdown": _pct(st["max_dd"], 0),
                    "beta": f"{reg['beta']:.2f}",
                    "alpha/yr": _pct(reg["alpha"]),
                    "alpha t-stat": f"{reg['t']:+.2f}",
                    "Sharpe": f"{st['sharpe']:.2f}",
                }
            )
    bench_rows = []
    for period, start in periods.items():
        st = stats(rets["SPXTR"][(start or ten_years) :].dropna(), rf)
        bench_rows.append(
            {
                "period": period,
                "S&P 500 TR CAGR": _pct(st["cagr"]),
                "max drawdown": _pct(st["max_dd"], 0),
                "Sharpe": f"{st['sharpe']:.2f}",
            }
        )

    daily = pd.concat([*(idx[n] for n in STRATEGIES), spxtr], axis=1).sort_index().ffill()
    ep_rows = []
    for ep, (a, b) in EPISODES.items():
        w = daily[a:b]
        ep_rows.append(
            {
                "episode": ep,
                **{n: _pct((w[n] / w[n].cummax() - 1).min(), 0) for n in [*STRATEGIES, "SPXTR"]},
            }
        )

    sig = vrp_signal(idx["VIX"], idx["SPX"])
    put = rets["PUT"].dropna()
    timed = timed_putwrite(put, rf, sig).dropna()
    always = put.reindex(timed.index)
    t_reg, a_reg = (
        capm(timed - rf.reindex(timed.index), mkt_ex),
        capm(always - rf.reindex(always.index), mkt_ex),
    )
    t_st, a_st = stats(timed, rf), stats(always, rf)
    held = (timed != rf.reindex(timed.index)).mean()
    timing = pd.DataFrame(
        [
            {
                "strategy": "Put-write, always (PUT)",
                "months": a_reg["months"],
                "CAGR": _pct(a_st["cagr"]),
                "max drawdown": _pct(a_st["max_dd"], 0),
                "beta": f"{a_reg['beta']:.2f}",
                "alpha/yr": _pct(a_reg["alpha"]),
                "alpha t-stat": f"{a_reg['t']:+.2f}",
                "Sharpe": f"{a_st['sharpe']:.2f}",
            },
            {
                "strategy": "Put-write only when VRP ≥ its past median",
                "months": t_reg["months"],
                "CAGR": _pct(t_st["cagr"]),
                "max drawdown": _pct(t_st["max_dd"], 0),
                "beta": f"{t_reg['beta']:.2f}",
                "alpha/yr": _pct(t_reg["alpha"]),
                "alpha t-stat": f"{t_reg['t']:+.2f}",
                "Sharpe": f"{t_st['sharpe']:.2f}",
            },
        ]
    )
    vrp_positive = (sig.dropna() > 0).mean()

    sig_alpha = [r for r in rows if abs(float(r["alpha t-stat"])) >= 2]
    if sig_alpha:
        found = "; ".join(
            f"{r['strategy']} {r['period']} ({r['alpha/yr']}, t={r['alpha t-stat']})"
            for r in sig_alpha
        )
        headline = f"**Statistically clear alphas (|t| ≥ 2): {found}.** Everything else is indistinguishable from its market exposure."
    else:
        headline = (
            "**No option-selling benchmark shows statistically clear alpha in any period** — "
            "their returns are explained by how much stock-market exposure they carry."
        )
    out.write_text(f"""# Option-selling strategies — 40 years of Cboe benchmarks

Generated {market_today().isoformat()} · daily index levels from Cboe (free, `data/cboe/`) ·
benchmark S&P 500 total return (`^SP500TR`), risk-free 13-week T-bill (`^IRX`) · monthly returns,
**gross of trading costs** (real implementations pay spreads these indexes don't).

{headline}

The premium these strategies harvest is real: VIX sat above SPX's trailing realised volatility
in {vrp_positive:.0%} of month-ends. The question is whether harvesting it beats simply owning
the equivalent amount of stock market — that is what **alpha** measures here.

## Each strategy against its market exposure

{_md_table(pd.DataFrame(rows))}

For comparison, the S&P 500 itself:

{_md_table(pd.DataFrame(bench_rows))}

**alpha/yr** = annual return beyond what the strategy's beta to the S&P 500 explains (CAPM on
monthly excess returns); |t| ≥ 2 is the usual bar for "not luck". A strategy with beta 0.6 and
zero alpha is just a cheaper way to own 60% of the market.

## Worst drawdowns in each crisis (peak to trough inside the window)

{_md_table(pd.DataFrame(ep_rows))}

## Timing test — sell puts only when the premium is rich?

Each month, the put-write is held only if the previous month-end's volatility risk premium
(VIX minus 21-day realised vol) was at or above the median of all earlier months; otherwise the
money sits in T-bills. The threshold uses past data only (5-year warm-up on PUT's daily
history, which starts in 2007), so this is an out-of-sample test from {timed.index[0]:%Y-%m}.
Invested {held:.0%} of months.

{_md_table(timing)}

## What this means for the lab

- Paper trading can check how a live implementation tracks these indexes and what it pays in
  spreads — it cannot establish an edge: a 1–2%/yr alpha needs decades of data to separate from
  luck, which only these index histories have.
- Ranking for a paper replication, if any: the monthly put-write (cleanest, matches `PUT`), then a
  delta-hedged covered call (Israelov & Nielsen 2015, which removes the unrewarded equity-timing
  piece). Avoid weekly put-writing, same-day (0DTE) premium selling, and selling into earnings.
""")
    return out
