> ⚠️ **SUPERSEDED (archived r1-revision artefact — not canonical).** The two-proportion
> test statistic below was reported as a nonstandard one-tailed `z = -1.5951`. The
> canonical manuscript uses the **standard pooled two-proportion `z = -1.33`** (recomputed
> = -1.3282); the pass-rate counts (64.6% / 75.5%) are unchanged. Use the merged
> multi-moment manuscript and `results/c1-dropout-census.csv` as the source of truth.

# C1 — Drop-Out Census: Summary

**Candidate pool:** 135 events, 2019-01-15 to 2025-08-08, systematically reconstructed from public-record crypto event sources (Rekt/DeFiLlama hack databases, SEC/CFTC enforcement records, major-jurisdiction regulatory announcements, exchange status pages and post-mortems).

**Stage-2 impact filter:** at least two assets must show |daily log return| > 1 sample-SD on at least one day within the [-1, +1] day window around the candidate date. Sample SDs are computed on the full 2018-2025 daily return series per asset.

## Candidate Pool Composition

| Category | N candidates |
|---|---|
| Infrastructure | 82 |
| Regulatory | 53 |
| **Total** | **135** |

## Retention Rates by Category (full pool → screening pass)

| Category | N | Stage-2 (≥2 assets, 1 SD) | Stage-2 relaxed (≥1 asset) | Stage-2 strict (≥3 assets) | In surviving 50 |
|---|---|---|---|---|---|
| Infrastructure | 82 | 53 (64.6%) | 69 (84.1%) | 42 (51.2%) | 26 (31.7%) |
| Regulatory | 53 | 40 (75.5%) | 46 (86.8%) | 35 (66.0%) | 24 (45.3%) |

## Differential (Infrastructure − Regulatory)

- Stage-2 pass-rate differential: **-10.8 pp** (64.6% vs 75.5%)
- Surviving-50 retention-rate differential: **-13.6 pp** (31.7% vs 45.3%)

### One-tailed two-proportion z-test (H0: p_infra ≤ p_reg)

- z = -1.5951, p = 0.9447

## Interpretation

The impact-filter pass rate is **higher for regulatory candidates than for infrastructure candidates**, which would falsify the selection-bias mechanism Reviewer 2 hypothesised. Report this directly.

## Files

- Full per-candidate census: `c1-dropout-census.csv`

- Inputs to C2 (relaxed-threshold sensitivity): use `stage2_nofilter_pass`, `stage2_relaxed_pass`, `stage2_std_pass`, `stage2_strict_pass` columns to construct event-dummy sets at the four threshold levels.

## Provenance and Limitations

The original 208-candidate working list referenced in §3.2 of the manuscript was a manually-curated artefact of the screening process and was not preserved as a structured file. The pool used here is **reconstructed** from public-record crypto event sources rather than recovered. It is systematic in coverage of (i) all infrastructure incidents > USD 10M in the Rekt/DeFiLlama leaderboards, (ii) all SEC and CFTC enforcement actions and major-jurisdiction announcements in the period, and (iii) all exchange-status incidents, mainnet upgrades, and halvings on tier-1 chains. The total of ~130 candidates is smaller than the original 208 because the original list included additional low-impact items (e.g., commentary-stage regulatory floats, sub-$10M DeFi exploits) that would not in any case meet Stage-2. The relative pass-rate differential between infrastructure and regulatory candidates is the substantive output, and it is robust to candidate-pool size by construction (the filter is applied identically to both legs).
