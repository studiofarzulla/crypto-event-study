"""
C10b: DGP-robustness of the size study (referee pre-emption).
================================================================
The size study (c10) calibrates the t-copula bootstrap under the SAME multivariate-t
DGP it is then tested against, so its nominal size there is partly by construction.
A fair worry: did we pick a DGP that flatters the conclusion? This script re-runs the
size loop under PERTURBED DGPs to show that (a) the naive i.i.d. rule's over-rejection
is robust to the tail/copula choice, and (b) the t-copula bootstrap still controls size
even when the simulation DGP is MIS-SPECIFIED relative to its calibration.

Reuses c10's exact machinery (c7.build_design / fit_observed, run_reference_distributions,
_panel_estimate, _decisions); only the DGP nu vector / copula-nu is overridden.

Scenarios:
  S0 baseline            : nu = fitted (~3.1-4.6), matched           [sanity vs c10]
  S1 lighter tails       : nu = 8 all assets, matched
  S2 heavier tails       : nu = 2.5 all assets, matched
  S3 Gaussian dependence : nu_c -> 200 (~Gaussian copula), margins fitted
  S4 MIS-SPECIFIED       : simulate nu = 2.5, but calibrate t-crit at fitted nu
"""
import time, argparse
import numpy as np
import pandas as pd
from multiprocessing import Pool

import c7_ccc_garchx_bootstrap as c7
import c10_size_study as c10
from c10_size_study import (_G, run_reference_distributions, crit_from_draws,
                            _panel_estimate, _decisions, ASSETS)


def setup(seed):
    design, inf_d, reg_d, ret_df = c7.build_design()
    observed = c7.fit_observed(design, seed=seed)
    nu_null = np.array([observed[a]["params_null"][4] for a in ASSETS])
    R_return = ret_df.corr().values
    rho_return = c7.mean_off_diag(R_return)
    z_df = pd.DataFrame({a: pd.Series(observed[a]["z_resid"], index=design[a]["index"])
                         for a in ASSETS}).dropna()
    R_z = z_df.corr().values
    common_idx = z_df.index
    common_pos = {a: pd.Index(design[a]["index"]).get_indexer(common_idx) for a in ASSETS}
    R_z_pd = R_z.copy(); eps = 0.0
    while True:
        try:
            L_z = np.linalg.cholesky(R_z_pd); break
        except np.linalg.LinAlgError:
            eps = max(eps * 10, 1e-8); R_z_pd = R_z + eps * np.eye(len(ASSETS))
    _G.update(dict(design=design, observed=observed, R_z=R_z, L_z=L_z,
                   n_common=len(common_idx), common_pos=common_pos,
                   nu_null=nu_null, nu_c_null=float(np.median(nu_null)),
                   max_len=max(observed[a]["resid_unr"].shape[0] for a in ASSETS)))
    return rho_return, nu_null.copy()


def run_scenario(name, nu_sim, nu_c_sim, N, B_ref, n_jobs, seed, rho_return,
                 nu_cal=None, nu_c_cal=None):
    # calibrate t/gauss crit under the CALIBRATION dgp (defaults to sim = matched)
    nu_cal = nu_sim if nu_cal is None else nu_cal
    nu_c_cal = nu_c_sim if nu_c_cal is None else nu_c_cal
    _G["nu_null"] = np.asarray(nu_cal, float); _G["nu_c_null"] = float(nu_c_cal)
    c7._GLOBAL.update(_G)
    g_draws, t_draws, *_ = run_reference_distributions(B_ref, n_jobs, seed + 700_000)
    crit = {"gauss": crit_from_draws(g_draws), "t": crit_from_draws(t_draws)}
    # simulate under the SIM dgp (may differ -> mis-specification)
    _G["nu_null"] = np.asarray(nu_sim, float); _G["nu_c_null"] = float(nu_c_sim)
    c7._GLOBAL.update(_G)
    seeds = [seed + i for i in range(N)]
    with Pool(processes=n_jobs) as pool:
        panels = pool.map(_panel_estimate, seeds, chunksize=max(1, N // (n_jobs * 4)))
    panels = [p for p in panels if p is not None]
    n = len(panels)
    methods = ["naive_iid", "design_effect", "gaussian_copula_boot", "tcopula_boot"]
    cnt = {m: {0.05: 0, 0.10: 0} for m in methods}
    for (di, dr, sei, ser, d_bar, se_ok) in panels:
        dec = _decisions(di, dr, sei, ser, d_bar, se_ok, rho_return, crit)
        for m in methods:
            cnt[m][0.05] += int(dec[m][0.05]); cnt[m][0.10] += int(dec[m][0.10])
    print(f"\n[{name}]  N_used={n}")
    for m in methods:
        s5 = cnt[m][0.05] / n; s10 = cnt[m][0.10] / n
        se5 = (s5 * (1 - s5) / n) ** .5
        print(f"   {m:<22} size@5%={s5:5.3f}+/-{se5:.3f}   size@10%={s10:5.3f}")
    return {m: cnt[m][0.05] / n for m in methods}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--N", type=int, default=300)
    ap.add_argument("--B_ref", type=int, default=2000)
    ap.add_argument("--n_jobs", type=int, default=22)
    ap.add_argument("--seed", type=int, default=20260626)
    a = ap.parse_args()
    t0 = time.time()
    print("Setup (fit observed null DGP)...")
    rho_return, nu_fit = setup(a.seed)
    print(f"  fitted nu = {np.round(nu_fit,2)}  rho_return={rho_return:.3f}")
    nu8 = np.full(6, 8.0); nu25 = np.full(6, 2.5)
    run_scenario("S0 baseline (fitted nu, matched)", nu_fit, float(np.median(nu_fit)),
                 a.N, a.B_ref, a.n_jobs, a.seed, rho_return)
    run_scenario("S1 lighter tails nu=8 (matched)", nu8, 8.0,
                 a.N, a.B_ref, a.n_jobs, a.seed + 1, rho_return)
    run_scenario("S2 heavier tails nu=2.5 (matched)", nu25, 2.5,
                 a.N, a.B_ref, a.n_jobs, a.seed + 2, rho_return)
    run_scenario("S3 Gaussian dependence (nu_c=200, fitted margins)", nu_fit, 200.0,
                 a.N, a.B_ref, a.n_jobs, a.seed + 3, rho_return)
    run_scenario("S4 MIS-SPECIFIED (simulate nu=2.5, calibrate at fitted nu)",
                 nu25, 2.5, a.N, a.B_ref, a.n_jobs, a.seed + 4, rho_return,
                 nu_cal=nu_fit, nu_c_cal=float(np.median(nu_fit)))
    print(f"\nTotal {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
