# Analysis code — merged multi-moment event study

This directory holds the **`c1`–`c14` pipeline** behind the manuscript *Do Cryptocurrency
Markets Differentiate Infrastructure from Regulatory Shocks? A Multi-Moment Event Study
with Dependence-Robust Inference*. Every table/figure in the paper is produced here from
`../data/*.csv`. The script → paper-table map is in the **root `README.md`**.

> Tested on **Python 3.11–3.13**. Python 3.14 is not yet supported by the pinned
> `pandas==2.3.1` (its datetime C-extension segfaults there) — use 3.11–3.13.
> `python3.13 -m venv .venv && . .venv/bin/activate && pip install -r ../requirements.txt`

## Estimation engines
- **`tarch_x_fast.py`** — `FastTARCHX`: the GJR-GARCH-X (TARCH-X) maximum-likelihood
  estimator used throughout (Student-*t* innovations, event + sentiment exogenous
  regressors, multistart). This is the canonical estimator.
- **`tarch_x_manual.py`** — reference/manual TARCH-X implementation (cross-check).
- **`data_preparation.py`** — winsorisation helper (`DataPreparation.winsorize_returns`).
- **`descriptive_stats.py`** — Table 1 (raw + global-clip moments); fast sanity check.

## Pipeline (c-series)
| Script | Produces |
|---|---|
| `c1_build_candidate_pool.py` | reconstructed 135-event pool + drop-out census (§7.1) |
| `c2_relaxed_threshold_sensitivity.py` | scope-condition sweep (Table 10) |
| `c2b_two_asset_point.py` | like-for-like 2-asset screen, 1.61× (§7.1.2) |
| `c2c_corrected_figure.py` | corrected sweep figure |
| `c3_bai_perron.py` | structural breaks / sub-sample persistence (Table 13) |
| `c4_granger_causality.py` | weekly sentiment→volatility Granger (Table 14) |
| `c5_pseudoreplication_test.py` | ladder rungs 2–3 (event-level Welch / MW / cluster) |
| `c6_garchx_clustered.py` | design-effect correction (rung 4) |
| `c7_ccc_garchx_bootstrap.py` | Gaussian-copula CCC-GARCH-X bootstrap (rung 5) |
| `c8a`–`c8i` | control battery: break controls, anticipation sweep, rolling-winsor, constant/AR(1)/event-in-mean, persistence SEs, weekly-Granger FDR |
| `c9_tcopula_bootstrap.py` | **Student-*t*-copula bootstrap — inference of record (rung 6)** |
| `c10_size_study.py` | Monte-Carlo size study (Table 9) |
| `c11_returns_block_bootstrap.py` | first-moment returns null (rung 7) |
| `c12_granger_rigour.py` | Toda–Yamamoto / litigation / BTC-control Granger robustness |
| `c13_rung4_recompute.py` | corrected design-effect reference (t(df_eff), Table 9 sub-row) |
| `c14_garch_diagnostics.py` | per-asset parameter table (Table 4) + ARCH diagnostics |

The two heavy bootstraps (`c9`, `c10`) parallelise across cores (`--n_jobs`); on a single
core they run serially and are slow. Fixed seeds make all outputs deterministic.

## License
MIT (code) — see `LICENSE`. The paper is CC BY 4.0 (root `LICENSE`).
