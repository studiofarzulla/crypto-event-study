# Do Cryptocurrency Markets Differentiate Infrastructure from Regulatory Shocks?
### A Multi-Moment Event Study with Dependence-Robust Inference

Replication materials for the merged multi-moment paper (supersedes the earlier
single-moment "Infrastructure vs Regulatory Shocks" and the companion "Same Returns,
Different Risks").

**Finding.** Cryptocurrency markets do **not** statistically differentiate infrastructure
from regulatory shocks at *either* moment — returns (block-bootstrap *p* ≈ 0.28) or
conditional variance (Student-*t*-copula bootstrap *p* = 0.322) — once inference accounts
for cross-event/cross-asset dependence and heavy tails. The apparent volatility asymmetry
reported in the earlier version was an **inference artefact**. The lead contribution is a
methodological cautionary tale: an *inference ladder* and a *Monte-Carlo size study* showing
how naive event-study inference manufactures significance that correct inference dissolves.

## Repository structure
- `paper/` — merged manuscript (`main.tex`, `main.pdf`) + response/cover letters
- `code/` — verified analysis pipeline (`c1`–`c11`, `tarch_x_manual.py`, `tarch_x_fast.py`)
- `data/` — shared sample: 6 assets (BTC, ETH, XRP, BNB, LTC, ADA), 50 events, GDELT sentiment
- `results/` — committed outputs (CSVs + per-analysis FINDING docs)
- `_archive/` — superseded prior-version materials; **do not cite**
- `springer-submission/` — frozen original single-moment submission, retained as record (superseded)

## Script → paper map
| script | produces |
|---|---|
| `c1_build_candidate_pool` | candidate-event pool + drop-out census |
| `c2_relaxed_threshold` / `c2b_two_asset_point` | scope-condition multiverse (curated vs mechanical) |
| `c3_bai_perron` | structural breaks (descriptive) |
| `c5_pseudoreplication_test` | inference-ladder rungs 2–3 (event-level / cluster) |
| `c6_garchx_clustered` | design-effect / correlation-weighted (rung 4) |
| `c7_ccc_garchx_bootstrap` | Gaussian-copula bootstrap (rung 5) |
| `c9_tcopula_bootstrap` | **Student-*t*-copula bootstrap — inference of record (rung 6)** |
| `c8a` / `c8h_break_controls` | structural-break regime controls |
| `c8b`/`c8c`/`c8d`/`c8e` | anticipation / winsorisation / constant-mean / persistence |
| `c8f_weekly_granger_fdr` | weekly sentiment-leads-volatility (+ BH-FDR) |
| `c10_size_study` | **Monte-Carlo size-distortion study** |
| `c11_returns_block_bootstrap` | first-moment returns null (rung 7) |

## Reproduce
Tested on **Python 3.11–3.13**. (Python 3.14 is not yet supported by the pinned `pandas==2.3.1`, whose datetime C-extension segfaults there — use 3.11–3.13.)
```
python3.13 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python code/descriptive_stats.py       # Table 1 (fast sanity check)
python code/c9_tcopula_bootstrap.py    # inference of record (variance)
python code/c11_returns_block_bootstrap.py   # first moment (returns)
python code/c10_size_study.py          # Monte-Carlo size study
```

## Note on the prior version
This repository previously hosted the single-moment "5.7×, *p* = 0.0008" result. That
estimate did not survive dependence-robust inference; the point estimate is unchanged but it
is no longer statistically distinguishable from zero. This paper reports the corrected dual
null and the inference lesson openly, as self-correction. Superseded materials are in
`_archive/` and `springer-submission/`.

## Citation
See `CITATION.cff`.
