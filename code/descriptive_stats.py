"""
Table 1: Per-Asset Descriptive Statistics for Daily Returns
===========================================================

Reproduces the descriptive-statistics table (N, mean, SD, skewness, excess
kurtosis, annualised volatility) for daily log returns of the six assets over
the analysis window 2019-01-01 to 2025-08-31, directly from ``data/*.csv``.

Raw vs winsorised
-----------------
Table 1 reports moments on the RAW daily log returns. This is deliberate: the
heavy tails (large excess kurtosis) are exactly what motivate the Student-t
innovations in the variance models, and winsorising before reporting would hide
them. The returns are winsorised only for the GARCH-X ESTIMATION, using the
headline global-clip rule (0.5 / 99.5 percent), identical to the winsorisation
in ``c2_relaxed_threshold_sensitivity.py``. For transparency this script also
prints the global-clip moments, which are much milder (the tails are capped).

Moments use pandas' bias-corrected estimators (``.skew()`` = G1,
``.kurtosis()`` = Fisher/excess G2, normal == 0). Annualised volatility uses the
conventional sqrt(252) scaling (comparability only), matching the Table 1
caption. BNB lists later than the other assets, giving a shorter series.

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


def load_returns(asset: str) -> pd.Series:
    """Daily log returns (%) over the analysis window, matching the pipeline loaders."""
    df = pd.read_csv(DATA_DIR / f"{asset}.csv")
    df["date"] = pd.to_datetime(df["snapped_at"], utc=True).dt.tz_convert(None).dt.normalize()
    df = df.sort_values("date").drop_duplicates("date").set_index("date")
    df = df.loc[START_DATE:END_DATE]
    return (np.log(df["price"]).diff() * 100).dropna()


def global_clip(returns: pd.Series, lo: float = 0.005, hi: float = 0.995) -> pd.Series:
    """Headline estimation winsoriser: clip to the 0.5 / 99.5 percent global quantiles."""
    qlo, qhi = returns.quantile([lo, hi])
    return returns.clip(qlo, qhi)


def moments(s: pd.Series) -> dict:
    return {
        "n": int(s.shape[0]),
        "mean": round(float(s.mean()), 4),
        "sd": round(float(s.std()), 4),
        "skewness": round(float(s.skew()), 4),
        "excess_kurtosis": round(float(s.kurtosis()), 4),
        "ann_vol_pct": round(float(s.std() * ANN_FACTOR), 2),
    }


def describe(asset: str) -> dict:
    raw = load_returns(asset)
    row = {"asset": asset.upper(), **moments(raw)}
    # transparency: global-clip (estimation) moments alongside the raw Table 1 moments
    gc = moments(global_clip(raw))
    row["gclip_skew"] = gc["skewness"]
    row["gclip_exkurt"] = gc["excess_kurtosis"]
    return row


def main():
    df = pd.DataFrame([describe(a) for a in ASSETS])

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = OUT_DIR / "table1-descriptive-stats.csv"
    df.to_csv(out_csv, index=False)

    print("Table 1 -- Descriptive Statistics: Daily Returns (%), RAW (moments as reported)")
    print(df.to_string(index=False))
    print(
        "\nNote: Table 1 moments are RAW; the 'gclip_*' columns show the milder "
        "global-clip (0.5/99.5%) moments used for estimation only."
    )
    print(f"Wrote {out_csv}")


if __name__ == "__main__":
    main()
