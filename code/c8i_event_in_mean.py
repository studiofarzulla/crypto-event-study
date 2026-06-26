"""
C8i: Event-in-MEAN robustness control for the GJR-GARCH-X conditional-variance
multiplier (curated 6-asset panel, global-clip winsorisation).
==============================================================================

Reviewer concern (correct): the canonical mean equation is constant-only -- it
demeans returns by the sample mean and puts NO event dummies in the first moment.
If event days carry large first-moment shocks (e.g. an FTX-day crash), that
unmodelled mean shock inflates the residual eps_t, which then (a) feeds
alpha*eps^2_{t-1} into next-day variance and (b) competes with the contemporaneous
variance-side dummy delta*D_t to explain elevated window variance. The existing
"constant-mean robustness" (c8d) only tests AR(1) serial correlation and does NOT
address this.

This control augments the MEAN equation with the SAME event dummies
[D_infra, D_reg] over the SAME [-3,+3] window used for the variance dummies,
demeans returns by OLS on [const, D_infra, D_reg], and feeds those residuals into
the IDENTICAL GJR-GARCH-X variance recursion with the SAME variance-side event
dummies. Events therefore appear in BOTH moments.

Baseline (constant-mean, global-clip, FastTARCHX): dbar_infra=1.9783,
dbar_reg=0.40497, multiplier=4.885 (matches the canonical 4.88x).

Throwaway computation -- runs entirely from scratchpad, edits nothing canonical.
"""
import sys
from pathlib import Path
import warnings
import numpy as np
import pandas as pd
from scipy import stats

warnings.simplefilter("ignore")

REPO = Path(__file__).resolve().parent.parent
CODE_DIR = REPO / "code"
DATA_DIR = REPO / "data"
sys.path.insert(0, str(CODE_DIR))
from tarch_x_fast import FastTARCHX  # noqa: E402

ASSETS = ["btc", "eth", "xrp", "bnb", "ltc", "ada"]
START_DATE = "2019-01-01"
END_DATE = "2025-08-31"
WIN_BEFORE = 3
WIN_AFTER = 3
SENTIMENT_CUTOFF = pd.Timestamp("2019-06-01")


# ---------------------------------------------------------------------------
# Data loaders -- copied verbatim from c2_relaxed_threshold_sensitivity.py so
# the residuals/dummies are byte-for-byte identical to the published pipeline.
# ---------------------------------------------------------------------------
def load_returns_panel():
    panel = {}
    for a in ASSETS:
        df = pd.read_csv(DATA_DIR / f"{a}.csv")
        df["date"] = pd.to_datetime(df["snapped_at"], utc=True).dt.tz_convert(None).dt.normalize()
        df = df.sort_values("date").drop_duplicates("date").set_index("date")
        df = df.loc[START_DATE:END_DATE]
        logret = np.log(df["price"]).diff() * 100
        lo, hi = logret.quantile([0.005, 0.995])
        ret_w = logret.clip(lo, hi)
        panel[a] = ret_w.dropna()
    return panel


def load_sentiment_daily(date_index):
    df = pd.read_csv(DATA_DIR / "gdelt.csv")
    df["week_start"] = pd.to_datetime(df["week_start"], utc=True).dt.tz_convert(None).dt.normalize()
    df = df.set_index("week_start").sort_index()
    win, mp = 52, 26
    rmean = df["S_gdelt_raw"].rolling(win, min_periods=mp).mean()
    rstd = df["S_gdelt_raw"].rolling(win, min_periods=mp).std()
    df["S_gdelt_normalized"] = (df["S_gdelt_raw"] - rmean) / rstd
    if "S_reg_decomposed" not in df.columns or df["S_reg_decomposed"].isna().any():
        df["S_reg_decomposed"] = df["S_gdelt_normalized"] * df["reg_proportion"]
    if "S_infra_decomposed" not in df.columns or df["S_infra_decomposed"].isna().any():
        df["S_infra_decomposed"] = df["S_gdelt_normalized"] * df["infra_proportion"]
    cols = ["S_gdelt_normalized", "S_reg_decomposed", "S_infra_decomposed"]
    daily = df[cols].reindex(pd.date_range(df.index.min(), date_index.max(), freq="D")).ffill()
    daily.loc[daily.index < SENTIMENT_CUTOFF] = 0
    out = pd.DataFrame(index=date_index).join(daily, how="left").fillna(0)
    return out


def build_event_dummies(date_index, dates_infra, dates_reg, wb=3, wa=3):
    idx = pd.DatetimeIndex(date_index)
    d_inf = pd.Series(0.0, index=idx, name="D_infrastructure")
    d_reg = pd.Series(0.0, index=idx, name="D_regulatory")
    for dt in dates_infra:
        dt = pd.to_datetime(dt).normalize()
        mask = (idx >= dt - pd.Timedelta(days=wb)) & (idx <= dt + pd.Timedelta(days=wa))
        d_inf.loc[mask] = 1.0
    for dt in dates_reg:
        dt = pd.to_datetime(dt).normalize()
        mask = (idx >= dt - pd.Timedelta(days=wb)) & (idx <= dt + pd.Timedelta(days=wa))
        d_reg.loc[mask] = 1.0
    return pd.DataFrame({"D_infrastructure": d_inf, "D_regulatory": d_reg})


# ---------------------------------------------------------------------------
# Event-in-mean estimator: identical GJR-GARCH-X, but residuals come from an OLS
# of returns on [const, D_infra, D_reg] instead of the sample mean.
# ---------------------------------------------------------------------------
class FastTARCHXMeanX(FastTARCHX):
    def __init__(self, returns, var_exog, mean_exog):
        super().__init__(returns, var_exog)
        Xm = np.column_stack([np.ones(self.n_obs), np.asarray(mean_exog, dtype=float)])
        beta, *_ = np.linalg.lstsq(Xm, self.returns, rcond=None)
        self.mean_beta = beta            # [const, b_infra, b_reg]
        self.resid = self.returns - Xm @ beta
        # var0 left at parent's np.var(returns) so the ONLY change vs baseline is
        # the residual definition (the t=0 init washes out over ~2.4k obs anyway).


def fit_asset(returns, var_exog, mean_exog, seed=0):
    est = FastTARCHXMeanX(returns.values, var_exog.values, mean_exog.values)
    p, f, ok = est.fit_multistart(n_starts=5, seed=seed)
    d = est.deltas(p)
    return {
        "dInfra": d[0], "dReg": d[1], "converged": ok,
        "b_const": est.mean_beta[0], "b_infra": est.mean_beta[1], "b_reg": est.mean_beta[2],
        "omega": p[0], "alpha": p[1], "gamma": p[2], "beta": p[3], "nu": p[4],
    }


def fit_asset_baseline(returns, var_exog, seed=0):
    """Constant-mean baseline through the identical FastTARCHX, for an internal
    apples-to-apples sanity check against the published 4.88x."""
    est = FastTARCHX(returns.values, var_exog.values)
    p, f, ok = est.fit_multistart(n_starts=5, seed=seed)
    d = est.deltas(p)
    return d[0], d[1], ok


def main():
    print("Loading panel / sentiment / events ...")
    panel = load_returns_panel()
    common = pd.DatetimeIndex(sorted(set.intersection(*[set(s.index) for s in panel.values()])))
    sent = load_sentiment_daily(common)
    events = pd.read_csv(DATA_DIR / "events.csv")
    events["date"] = pd.to_datetime(events["date"])
    inf_d = events.loc[events["type"] == "Infrastructure", "date"].tolist()
    reg_d = events.loc[events["type"] == "Regulatory", "date"].tolist()
    print(f"curated events: {len(inf_d)} infra, {len(reg_d)} reg")

    base_rows, mean_rows = [], []
    for a in ASSETS:
        r = panel[a].loc[panel[a].index >= pd.Timestamp(START_DATE)]
        dum = build_event_dummies(r.index, inf_d, reg_d, WIN_BEFORE, WIN_AFTER)
        s = sent.reindex(r.index).fillna(0)
        var_exog = pd.concat(
            [dum[["D_infrastructure", "D_regulatory"]],
             s[["S_gdelt_normalized", "S_reg_decomposed", "S_infra_decomposed"]]],
            axis=1).fillna(0)
        mean_exog = dum[["D_infrastructure", "D_regulatory"]]

        bi, br, bok = fit_asset_baseline(r, var_exog, seed=0)
        base_rows.append({"asset": a, "dInfra": bi, "dReg": br, "converged": bok})

        m = fit_asset(r, var_exog, mean_exog, seed=0)
        m["asset"] = a
        mean_rows.append(m)
        print(f"  {a}: baseline dI={bi:.3f} dR={br:.3f} | "
              f"event-in-mean dI={m['dInfra']:.3f} dR={m['dReg']:.3f} "
              f"meanI={m['b_infra']:.3f} meanR={m['b_reg']:.3f} ok={m['converged']}")

    base = pd.DataFrame(base_rows)
    mean = pd.DataFrame(mean_rows)

    def summarise(df, label):
        infra = df["dInfra"].to_numpy(float)
        reg = df["dReg"].to_numpy(float)
        mi, mr = np.nanmean(infra), np.nanmean(reg)
        mult = mi / mr if mr != 0 else np.nan
        t, p = stats.ttest_ind(infra, reg, equal_var=False, nan_policy="omit")
        print(f"\n[{label}]  dbar_infra={mi:.4f}  dbar_reg={mr:.4f}  "
              f"multiplier={mult:.3f}x  Welch t={t:.3f} p={p:.4f}")
        return mi, mr, mult, t, p

    print("\n" + "=" * 70)
    summarise(base, "BASELINE constant-mean (FastTARCHX, global clip)")
    mi, mr, mult, t, p = summarise(mean, "EVENT-IN-MEAN (OLS demean on const,D_infra,D_reg)")

    print("\n--- Mean-equation event coefficients (return %, cross-asset mean) ---")
    print(f"  b_infra (mean): {mean['b_infra'].mean():.4f}  "
          f"[range {mean['b_infra'].min():.3f}..{mean['b_infra'].max():.3f}]")
    print(f"  b_reg   (mean): {mean['b_reg'].mean():.4f}  "
          f"[range {mean['b_reg'].min():.3f}..{mean['b_reg'].max():.3f}]")

    outdir = REPO / "results"
    base.to_csv(outdir / "c8i-baseline-per-asset.csv", index=False)
    mean.to_csv(outdir / "c8i-event-in-mean-per-asset.csv", index=False)
    summ = pd.DataFrame([
        {"spec": "baseline_const_mean", "dbar_infra": np.nanmean(base["dInfra"]),
         "dbar_reg": np.nanmean(base["dReg"]),
         "multiplier": np.nanmean(base["dInfra"]) / np.nanmean(base["dReg"])},
        {"spec": "event_in_mean", "dbar_infra": mi, "dbar_reg": mr,
         "multiplier": mult, "welch_t": t, "welch_p": p,
         "mean_b_infra": mean["b_infra"].mean(), "mean_b_reg": mean["b_reg"].mean()},
    ])
    summ.to_csv(outdir / "c8i-summary.csv", index=False)
    print(f"\nSaved: {outdir/'c8i-summary.csv'}, c8i-event-in-mean-per-asset.csv, c8i-baseline-per-asset.csv")


if __name__ == "__main__":
    main()
