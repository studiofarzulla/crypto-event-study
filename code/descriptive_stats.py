"""
Table 1: Per-Asset Descriptive Statistics for Daily Returns
===========================================================

Reproduces the descriptive-statistics table (mean, SD, skewness, excess
kurtosis, annualised volatility) for daily log returns of the six assets over
the analysis window 2019-01-01 to 2025-08-31.

Winsorisation
-------------
Returns are winsorised with the project's CANONICAL rolling rule, identical to
``DataPreparation.winsorize_returns(window=30, n_std=5.0)`` from the pre-revision
pipeline (clip each observation to a 30-day rolling mean +/- 5 sigma band,
``min_periods=1``). That helper lives in the local-only pre-revision package and
is replicated inline here so Table 1 is reproducible from the public repo
(``data/*.csv`` only). The winsorisation roughly halves the raw skewness/kurtosis
(extreme tails are clipped), which is why the reported moments are much milder
than the raw-return moments.

Moments use pandas' bias-corrected estimators (``.skew()`` = G1,
``.kurtosis()`` = Fisher/excess G2, normal == 0), matching the original pipeline.
Annualised volatility uses the conventional sqrt(252) scaling (comparability
only), matching the Table 1 caption.

Outputs:
    results/table1-descriptive-stats.csv
    (also printed to stdout)
"""

from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent  # repo root (crypto-event-study/)
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "results"

ASSETS = ["btc", "eth", "xrp", "bnb", "ltc", "ada"]
START_DATE = "2019-01-01"
END_DATE = "2025-08-31"
ANN_FACTOR = np.sqrt(252)  # Table 1 caption: conventional sqrt(252), illustrative


def winsorize_returns(returns: pd.Series, window: int = 30, n_std: float = 5.0) -> pd.Series:
    """Canonical rolling winsoriser (== DataPreparation.winsorize_returns)."""
    rolling_mean = returns.rolling(window=window, min_periods=1).mean()
    rolling_std = returns.rolling(window=window, min_periods=1).std()
    upper = rolling_mean + n_std * rolling_std
    lower = rolling_mean - n_std * rolling_std
    return returns.clip(lower=lower, upper=upper)


def load_returns(asset: str) -> pd.Series:
    """Daily log returns (%) over the analysis window, matching the pipeline loaders."""
    df = pd.read_csv(DATA_DIR / f"{asset}.csv")
    df["date"] = pd.to_datetime(df["snapped_at"], utc=True).dt.tz_convert(None).dt.normalize()
    df = df.sort_values("date").drop_duplicates("date").set_index("date")
    df = df.loc[START_DATE:END_DATE]
    return (np.log(df["price"]).diff() * 100).dropna()


def describe(asset: str) -> dict:
    raw = load_returns(asset)
    win = winsorize_returns(raw).dropna()
    return {
        "asset": asset.upper(),
        "n_raw": int(raw.shape[0]),
        "n_winsor": int(win.shape[0]),
        "n_clipped": int((raw.reindex(win.index) != win).sum()),
        "mean": round(float(win.mean()), 4),
        "sd": round(float(win.std()), 4),
        "skewness": round(float(win.skew()), 4),
        "excess_kurtosis": round(float(win.kurtosis()), 4),
        "ann_vol_pct": round(float(win.std() * ANN_FACTOR), 2),
    }


def main():
    rows = [describe(a) for a in ASSETS]
    df = pd.DataFrame(rows)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = OUT_DIR / "table1-descriptive-stats.csv"
    df.to_csv(out_csv, index=False)

    print("Table 1 — Descriptive Statistics: Daily Returns (%), winsorised (rolling 30d, +/-5 sigma)")
    print(df.to_string(index=False))
    print(f"\nWrote {out_csv}")


if __name__ == "__main__":
    main()
