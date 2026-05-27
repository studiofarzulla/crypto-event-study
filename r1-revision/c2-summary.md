# C2 — Relaxed-Threshold Sensitivity: Summary

**Headline question.** When the Stage-2 'demonstrable market-wide impact' filter is relaxed or removed, does the 5.7× infrastructure-vs-regulatory multiplier survive?

**Answer.** See the table below — the multiplier under each specification.

## Cross-Asset Multiplier by Specification

| Spec | N infra | N reg | δ̄ infra | δ̄ reg | Multiplier | Cohen's d | Welch t | p |
|---|---|---|---|---|---|---|---|---|
| S1_baseline | 26 | 24 | 1.9783 | 0.4051 | **4.883×** | 2.699 | 4.676 | 0.0015 |
| S2_relaxed | 69 | 46 | 1.4027 | 0.9437 | **1.486×** | 0.607 | 1.051 | 0.3205 |
| S3_nofilter | 82 | 53 | 0.2093 | 0.3637 | **0.575×** | -0.474 | -0.821 | 0.4464 |
| S4_strict | 42 | 35 | 3.8343 | 2.9239 | **1.311×** | 0.505 | 0.874 | 0.4029 |

## Decision-Tree Outcome (per `revision-plan.md`)

**MAJOR REFRAMING NEEDED.** Multiplier < 1.5× or p ≥ 0.10 under relaxed threshold. Flag for Murad: editor-conversation scope discussion.

- Relaxed-threshold multiplier: **1.486×** (p = 0.3205)
- No-filter multiplier:         **0.575×**
- Strict-threshold multiplier:  **1.311×**

## Files

- Per-asset model parameters: `c2-relaxed-threshold-results.csv`
- Cross-asset summary: `c2-summary-table.csv`
- Plot: `c2-multiplier-decay.png` / `.pdf`
