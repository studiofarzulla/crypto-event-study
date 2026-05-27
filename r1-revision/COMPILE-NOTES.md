# Compile Notes — R1 Revision

## Status

**Final compile:** clean. 30 pages. 0 errors, 0 LaTeX warnings, 0 undefined citations, 0 undefined references.

## Compile sequence

```bash
cd r1-revision/
pdflatex -interaction=nonstopmode -halt-on-error main-r1.tex
bibtex main-r1
pdflatex -interaction=nonstopmode -halt-on-error main-r1.tex
pdflatex -interaction=nonstopmode -halt-on-error main-r1.tex
```

The bibliography file is `references.bib` (a copy of `references-r1.bib` — the canonical file `main-r1.tex` references the basename `references` per `\bibliography{references}`).

## Files used

- Class: `sn-jnl.cls` (Springer Nature article class, copied from `digital-finance-canon/`)
- Bib style: `sn-mathphys-num.bst` (copied)
- Bibliography: `references.bib` (= `references-r1.bib` with renamed copy for compile)
- Figures: `figures-new/figure_correlation_heatmap.pdf` (referenced from §4.1)

## Headline outcome (CRITICAL — flag for Murad)

**The C2 relaxed-threshold sensitivity analysis returned a multiplier of 1.49× under relaxed inclusion (Welch p = 0.32) and 0.58× under no-filter inclusion.** Per the original `revision-plan.md` decision tree, this falls in the **"MAJOR REFRAMING NEEDED"** band (multiplier < 1.5× or p ≥ 0.10 under relaxed threshold).

The revision has been written as the planning documents specified, with the abstract, discussion, and conclusion re-cast around the range of multiplier estimates rather than a single point estimate. The 5.7× headline is retained as the impact-screened (baseline) number and the relaxed-threshold result is reported alongside it.

**Decision point for Murad before submission:**
1. The current revision honestly reports both numbers and treats the asymmetry as conditional on candidate-pool screening. This is the most defensible posture given the data.
2. An alternative posture would be to flag this in a brief editor-only note before submission, asking whether the editor wants to see the revision as written or whether a different framing is preferred. The reviewer-2 comment was sharp enough that the C2 finding is exactly what they asked for; reporting it honestly is consistent with what they requested.
3. The cover letter (in `cover-letter.md`) leads with this finding and frames it as a substantive qualification rather than a defeat. The framing is technical and direct.

## Per-section status (post-edits)

| Section | Edits applied | Status |
|---|---|---|
| Abstract | Multiplier range; ETH demoted; Bai-Perron and Granger flagged | Done |
| §1 Introduction | ETH demoted; range reported; near-integration previewed | Done |
| §2.4 Literature | New positioning paragraph at end | Done |
| §3.1 Data | "Relative independence" rephrased | Done |
| §3.2 Event Classification | Exogeneity (§3.2.3) and overlap-handling (§3.2.4) subsections added | Done |
| §3.4 Methodology | Constant-mean equation note added | Done |
| §4.1 Descriptive | Heatmap figure added | Done |
| §4.2 H1 Results | Table 3 (expanded params) added | Done |
| §4.2 H2 Results | Diebold-Mariano paragraph expanded; HLN noted | Done |
| §4.4 Robustness | §4.4.4 Bai-Perron and §4.4.5 Granger added | Done |
| §4.5 Network | Demoted to "Supplementary Finding"; single subsection | Done |
| **§4.6 (NEW)** | Selection-bias sensitivity: drop-out + relaxed-threshold | Done |
| §5 Discussion | Causal language softened; selection-bias caveat | Done |
| §5.5 Limitations | Selection-bias as quantified limitation; Granger flagged | Done |
| §6 Conclusion | Re-written around range | Done |
| References | Bai-Perron, Granger, HLN, Killick added | Done |

## Items intentionally NOT done

These were considered but not pursued in this revision round:

1. **Bai-Perron within-sub-sample re-estimation of the infrastructure-regulatory asymmetry.** Given the C2 multiplier collapse, re-running the comparison within Bai-Perron sub-samples would not change the central conclusion. The cover letter mentions this as a candidate for a possible second round.

2. **Daily-frequency GDELT extraction.** Out-of-scope for the revision; flagged as future work in Limitations.

3. **Standard-error reporting in Table 3.** The full GJR-GARCH-X SE computation was numerically unstable in the existing pipeline (`tarch_x_manual.py::_compute_standard_errors` emitted `RuntimeWarning: invalid value in sqrt` for several assets — the inverse Hessian had small negative diagonal entries on a couple of asset/spec combinations). The point estimates are reported in Table 3; full per-asset diagnostics including the SE issues are in `c2-relaxed-threshold-results.csv` and `c3-subsample-persistence.csv` for transparency.

4. **Per-asset DM statistics table.** The Diebold-Mariano discussion was expanded in prose (§4.2) but a per-asset table was not assembled. The existing pipeline does not export the DM statistics in a directly tabulatable form; assembling that table requires re-running the rolling-window forecasts. The prose expansion addresses the reviewer's underlying request (more thorough discussion); the per-asset table is a natural follow-up if requested.

## Replication

Code for all four computations is in `code/`:

| File | Output |
|---|---|
| `code/c1_build_candidate_pool.py` | `c1-dropout-census.csv`, `c1-dropout-summary.md` |
| `code/c2_relaxed_threshold_sensitivity.py` | `c2-relaxed-threshold-results.csv`, `c2-summary-table.csv`, `c2-summary.md`, `c2-multiplier-decay.{png,pdf}` |
| `code/c3_bai_perron.py` | `c3-bai-perron-results.csv`, `c3-subsample-persistence.csv`, `c3-break-summary.md` |
| `code/c4_granger_causality.py` | `c4-granger-results.csv`, `c4-granger-summary.md` |
| `code/figure_correlation_heatmap.py` | `figures-new/figure_correlation_heatmap.{pdf,png}` |

Each script is self-contained and re-uses the existing `../code/tarch_x_manual.py` estimator. Run order: C1 → C2 (depends on C1's census); C3 and C4 independent.

Python venv was created at the event-study project level (`event-study/.venv-r1/`) — NOT inside `r1-revision/` (per the constraint to keep the paper folder clean). To replicate:

```bash
cd event-study/
python3 -m venv .venv-r1
.venv-r1/bin/pip install numpy pandas scipy statsmodels matplotlib seaborn ruptures
.venv-r1/bin/python r1-revision/code/c1_build_candidate_pool.py
.venv-r1/bin/python r1-revision/code/c2_relaxed_threshold_sensitivity.py
.venv-r1/bin/python r1-revision/code/c3_bai_perron.py
.venv-r1/bin/python r1-revision/code/c4_granger_causality.py
.venv-r1/bin/python r1-revision/code/figure_correlation_heatmap.py
```
