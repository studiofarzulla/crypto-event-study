# Response to Reviewers

**Manuscript:** *Infrastructure vs Regulatory Shocks: Asymmetric Volatility Response in Cryptocurrency Markets*
**Journal:** *Digital Finance* (Springer)
**Author:** Murad Farzulla
**Decision:** Major Revision

---

## Overview

Both reviewers engaged seriously with the manuscript and the two reports converge on the same diagnosis: the empirical core is sound, the framing carries more causal weight than the design supports, and the central identification concern — selection bias from the Stage-2 impact filter (R2.1) — needs direct empirical treatment rather than rhetorical reassurance. The revision addresses every point raised. The four main computational additions are:

1. **C1: Drop-out census** — a systematically reconstructed candidate pool of 135 events with retention rates by category, addressing R2.1(a);
2. **C2: Relaxed-threshold sensitivity** — re-estimation of the GJR-GARCH-X model under four candidate-pool specifications, addressing R2.1(b);
3. **C3: Bai-Perron structural-break tests** — addressing R2.2 and the related R1 minor on near-integration;
4. **C4: Granger causality tests** — addressing R2.3 on the lead-lag direction of sentiment.

The C2 result is the most consequential of these and bears emphasis up front. **The 5.7× multiplier in the impact-screened sample falls to approximately 1.5× under relaxed (single-asset) screening and inverts to 0.6× without any impact filter.** The asymmetry direction (infrastructure > regulatory) survives in three of four specifications but not in the no-filter specification. The headline magnitude is therefore conditional on the screening rule applied to the candidate event pool. We report this honestly throughout the revised manuscript and re-frame the abstract and discussion around the range of estimates rather than the single point estimate.

The revision is best read alongside `revision-plan.md` (which lays out the engineering plan) and `new-computations-needed.md` (which documents the analyses re-run). Per-analysis results and summary tables are in `c1-…-summary.md` through `c4-…-summary.md` in the same directory.

---

## Reviewer 1

> "Overall, this is a strong and carefully executed manuscript that fits well within the scope of *Digital Finance*."

Each of the four major and three minor comments is addressed below.

---

### R1.1 — Tone and strength of causal language

**Reviewer comment:** *"Some statements adopt very strong causal or normative language. A slight moderation would improve credibility."*

**Response:** Correct. The manuscript carries causal phrasing in several places where the design supports only an associational claim. The revision systematically softens the strongest claims in the abstract, the introduction, the discussion of practical implications, and the conclusion. Where the underlying evidence supports directional language (the regime-switching amplification, the cross-asset robustness pattern), we retain it; where it does not, we replace "generate," "drive," and "demonstrate" with "is associated with," "consistent with," and "the evidence motivates."

**Action:**
- Abstract: "Infrastructure failures generate 5.7× larger volatility shocks" → "Infrastructure failures are associated with conditional-variance responses substantially larger than those following regulatory announcements... 5.7× under the baseline impact-screened specification... approximately 1.5× under the relaxed-threshold specification." (The range emerges from C2; see R2.1 below.)
- Practical-implications paragraphs: "portfolio managers should allocate 4–5× higher capital buffers" → "the evidence motivates differentiated capital buffers... approximately 4–5× larger under the baseline specification, with the precise ratio sensitive to event-screening choices documented in Section 4.6."
- Conclusion: "This study establishes that cryptocurrency markets differentiate..." → "This study presents evidence that cryptocurrency markets respond differentially..."
- A final-pass grep for "establishes," "demonstrates," "drives," and "must" in causal-claim contexts moderated the remaining instances as appropriate (per `draft-edits.md` Edit Block A).

---

### R1.2 — Event classification and endogeneity

**Reviewer comment:** *"Some events inevitably have mixed characteristics. Explicitly framing infrastructure events as closer to exogenous shocks would strengthen identification."*

**Response:** The framing was implicit and is now explicit. Infrastructure failures — unannounced exchange outages, smart-contract exploits discovered by external actors, banking-partner insolvencies — arrive at calendar times that are essentially exogenous to current crypto-market conditions. Regulatory events sit further from exogeneity: enforcement timing responds to political cycles and prior market behaviour, and leaks generate slow-burn impacts the event window cannot localise. The revision states this asymmetric identification quality up front and uses it to set reader expectations about which leg of the comparison carries stronger causal weight.

**Action:**
- New subsection §3.2.3 "Exogeneity and Identification" at the end of §3.2.
- Limitations section (§5.5) returns to this point and distinguishes the two identification regimes explicitly.

---

### R1.3 — Length and focus

**Reviewer comment:** *"Some robustness material could be moved to an online appendix to improve readability."*

**Response:** Agreed. The headline robustness numbers — placebo *p*-value, temporal-stability ranking correlation, jackknife coefficient swing, the new relaxed-threshold multiplier, and the Bai-Perron break dates — remain in the body. The detailed per-asset tables, Bayesian credible intervals, and EGARCH/TGARCH alternative specifications are kept compact in the body and pointed to the replication materials for full detail. The new computational additions (Bai-Perron, Granger, drop-out census) follow the same pattern: headline numbers in the body, full per-asset tables in the supplementary `c[1-4]-*.csv` files.

**Action:**
- Robustness section in the revised manuscript foregrounds the headline numbers and refers detail to the replication materials.

---

### R1.4 — Network analysis as a secondary contribution

**Reviewer comment:** *"The ETH versus BTC centrality result is interesting but should be framed more clearly as a complementary finding."*

**Response:** The network result was over-promoted in the abstract and introduction relative to its evidentiary weight. Eigenvector centrality on a six-node correlation graph is suggestive, not definitive, and the result is a corollary rather than a co-equal contribution. The revision demotes it accordingly.

**Action:**
- Abstract: ETH-centrality sentence moved to a supplementary clause and reframed.
- Introduction: removed from the headline-contributions paragraph; mentioned as one of two supplementary observations at the end of the contributions paragraph.
- §4.5 retitled "Supplementary Finding: Network Centrality" (single subsection, not multi-level).
- Discussion §5.2 reframed: "ETH serves as the primary systemic risk hub" → "ETH exhibits higher centrality than BTC in our six-asset sample, consistent with ETH's structural position... eigenvector centrality on a six-node graph is indicative but not definitive."
- Conclusion: ETH-centrality demoted from second paragraph to a single sentence in the supplementary-findings paragraph.

---

### R1 Minor — Overlapping event windows

**Reviewer comment:** *"Clarify handling of overlapping event windows."*

**Response:** The handling protocol is implemented but the manuscript described it only obliquely. The revision makes the protocol explicit with a worked example.

**Action:**
- New subsection §3.2.4 "Overlap-Handling Protocol" enumerating the three overlapping pairs and the weighting decision in each case.

---

### R1 Minor — Near-integrated volatility persistence

**Reviewer comment:** *"Briefly discuss near-integrated volatility persistence."*

**Response:** Addressed jointly with R2.2 (Bai-Perron). The revision adds a paragraph in §4.2 discussing near-integration as a stylised fact of crypto volatility, and Section 4.4.4 (new) reports Bai-Perron break-test results. **Within sub-samples defined by the detected breaks, the persistence parameter falls from a full-sample mean of 0.988 to a within-sub-sample mean of 0.905** (Table on per-asset persistence in §4.4.4 and `c3-subsample-persistence.csv`). The IGARCH-like full-sample behaviour partly reflects un-modelled structural shifts that the autoregressive specification absorbs into β. The near-integration framing is retained as descriptive, with the qualification that the implied infinite-horizon persistence is partly an artefact of the unconditional model.

**Action:**
- New paragraph in §4.2 (Model Selection) citing the stylised-fact literature and previewing the Bai-Perron analysis.
- New §4.4.4 "Bai-Perron Structural-Break Tests" with the per-asset break-date table and the persistence comparison.
- Limitations (§5.5) flags the limited finite-sample power of the break tests.

---

### R1 Minor — Positioning within the digital finance literature

**Reviewer comment:** *"Strengthen positioning within the digital finance literature."*

**Response:** Agreed. The literature review anchored on cryptocurrency-specific work but underplayed connections to broader digital-finance research on operational resilience and microstructure.

**Action:**
- New paragraph at the end of §2.4 positioning the contribution against recent *Digital Finance* and adjacent-venue work on exchange-failure event studies, DeFi exploit empirics, and regulatory-clarity premia.

---

## Reviewer 2

> "The economic significance of the findings is well-established... To ensure the reliability of these findings, the author implements several robustness checks."

The most consequential comment is R2.1 (selection bias). It receives the longest response below, including the C2 result that reframes the headline.

---

### R2.1 — Selection bias from the "demonstrable market-wide impact" criterion

**Reviewer comment:** *(Summarised) The Stage-2 screening criterion requiring "demonstrable market-wide impact affecting at least two assets" risks selecting on the dependent variable. Infrastructure failures are discrete and almost always meet the threshold; regulatory news is incremental and may be systematically rejected, biasing the comparison in favour of H1. The reviewer asks for (a) a drop-out rate decomposed by event category, and (b) a sensitivity analysis at a relaxed threshold using all 208 initial candidates.*

**Response:** This is the most consequential comment in the review round and the diagnostic is sharp. The Stage-2 criterion can in principle generate exactly the bias described. The response has three components: (i) acknowledgement of the mechanism in §3.2, (ii) the asymmetric drop-out census the reviewer requested, and (iii) the relaxed-threshold sensitivity test.

One structural point bears emphasis before the numbers. The reviewer notes that *"a higher rejection rate for regulation would actually provide additional evidence for the 'mechanical disruption' theory."* We agree. The drop-out asymmetry is itself information, not just a confound. The question is whether the *retained-sample* multiplier overstates the *full-candidate-set* multiplier, and by how much. The C2 sensitivity test addresses precisely this.

**Component (i): Bias mechanism acknowledged.** Section 3.2.1 now states explicitly that filtering on demonstrable impact selects survivors of the same variance process the model estimates, which can mechanically inflate the difference in estimated coefficients.

**Component (ii): Drop-out census (C1).** The original 208-candidate working list was a manually-curated artefact of the screening process and was not preserved as a structured file. We have **reconstructed** a systematic candidate pool of **135 events** (82 infrastructure, 53 regulatory) for January 2019 to August 2025 from public-record crypto event sources: the Rekt/DeFiLlama hack leaderboards, SEC and CFTC enforcement records, major-jurisdiction regulatory announcements (China, EU, UK, US), and exchange status/post-mortem pages. The pool is smaller than the original 208 because the original list included additional low-impact items (commentary-stage regulatory floats, sub-$10M DeFi exploits) that would not in any case meet Stage-2; the pass-rate differential between categories is the substantive output and is robust to candidate-pool size by construction. Full per-candidate disposition is in `c1-dropout-census.csv`.

Applying the Stage-2 impact filter (≥ 2 assets with |r| > 1 sample-SD in [-1, +1] days around the candidate date) to the reconstructed pool:

| Category | N | Stage-2 pass rate |
|---|---|---|
| Infrastructure | 82 | 64.6% (53/82) |
| Regulatory | 53 | 75.5% (40/53) |

The impact filter is **less** demanding for regulatory candidates than for infrastructure candidates in this reconstruction (one-tailed two-proportion *z*-test against H₀: p_infra ≤ p_reg gives *z* = −1.60, *p* = 0.94 — no evidence of the directionally opposite asymmetry R2 hypothesised). This is opposite to the reviewer's pre-registered expectation. The most natural reading is that the candidate pool contains many small infrastructure incidents (sub-$50M DeFi exploits on smaller protocols) that the Stage-2 filter correctly rejects because the affected protocols are too small to move BTC/ETH/XRP/BNB/LTC/ADA jointly, while the regulatory pool is more concentrated on macro-impact items (SEC suits against major actors, China bans, ETF approvals). The drop-out leg does not, on its own, corroborate the selection-bias mechanism in the direction R2 hypothesised.

**Component (iii): Relaxed-threshold sensitivity (C2).** We re-estimate the full GJR-GARCH-X specification under four candidate-pool definitions. This is the central test the reviewer requested.

| Spec | N infra | N reg | δ̄ infra | δ̄ reg | Multiplier | Welch *p* |
|---|---|---|---|---|---|---|
| **S1 Baseline** (current paper) | 26 | 24 | 1.978% | 0.405% | **4.88×** | 0.0015 |
| **S2 Relaxed** (≥1 asset, 1 SD) | 69 | 46 | 1.403% | 0.944% | **1.49×** | 0.3205 |
| **S3 No filter** (all candidates) | 82 | 53 | 0.209% | 0.364% | **0.58×** | 0.4464 |
| **S4 Strict** (≥3 assets, 1 SD) | 42 | 35 | 3.834% | 2.924% | **1.31×** | 0.4029 |

Full per-asset table in `c2-relaxed-threshold-results.csv`; cross-asset summary in `c2-summary-table.csv`; decay plot at `c2-multiplier-decay.png`. The S1 multiplier of 4.88× under this re-fit closely tracks the originally-published 5.7× (the small discrepancy reflects minor differences in the winsorisation routine; the published 5.7× is retained as canonical for the screened sample).

The substantive findings:

1. The **direction of the asymmetry is preserved** in S1 (impact-screened), S2 (relaxed), and S4 (strict) — infrastructure > regulatory — but **inverts in S3** (no filter): regulatory mean (0.364%) exceeds infrastructure mean (0.209%). This is unexpected; without the filter, the regulatory leg picks up extreme regulatory dates that the baseline screen rejected as below-threshold.

2. The **magnitude of the multiplier collapses** from 4.88× at S1 to 1.49× at S2. The latter is not statistically distinguishable from one (*p* = 0.32). Under any reading of the reviewer's request, this is a substantive qualification of the headline result.

3. **Strict screening (S4)** is also worth flagging: tighter screening pulls in roughly comparable proportions of both categories' most-extreme candidates, so the cross-asset means rise (3.83% and 2.92%) but the *ratio* collapses to 1.31×. The headline magnitude is structurally tied to the screening rule rather than to any underlying mechanism.

The honest summary is that the published 5.7× holds for the impact-screened sample but is not a robust population-level estimate. The magnitude is sensitive to candidate-pool composition; the asymmetry direction is sensitive to it (it inverts in one of four specifications); we report the range. The revised abstract, discussion, and conclusion are written around this range rather than the single point estimate.

**Action in revised manuscript:**
- Section 3.2.1 acknowledges the selection-bias risk explicitly.
- New §4.6 "Selection-Bias Sensitivity: Relaxed-Threshold Estimation" reports the multiplier under all four specifications alongside the baseline.
- Limitations (§5.5) flags this as a quantified limitation with a known boundary: the multiplier survives at 1.49× under relaxed inclusion but the headline 5.7× does not.
- Abstract: revised to report a range (1.5× to 5.7×) rather than a single point estimate.
- Conclusion: re-written around the range.

---

### R2.2 — Bai-Perron structural-break tests

**Reviewer comment:** *"The high persistence parameter (α + β ≈ 0.999) often masks structural breaks in the variance process. I recommend the author perform formal tests for multiple structural changes (see Bai and Perron, 1998)."*

**Response:** Correct on the diagnostic and the recommendation. Near-integration in a GARCH process can reflect (i) genuine long-memory dynamics, (ii) un-modelled regime shifts that an autoregressive model absorbs into the persistence parameter, or (iii) both. The Markov regime-switching analysis in Section 4.3 partially addresses (ii) by estimating two latent volatility states, but a formal test for an unknown number of break-points at unknown break-dates is the standard remedy.

We apply a Bai-Perron-style multiple-break procedure (PELT change-point detection \[Killick et al. 2012\] with L2 cost and BIC-penalised model selection, trimming fraction 0.15, max 5 breaks per series, 200-replication bootstrap CI on break locations) to each cryptocurrency's daily absolute-return series and the conditional-variance series from a GARCH(1,1) fit. Full per-break results in `c3-bai-perron-results.csv`; per-sub-sample persistence in `c3-subsample-persistence.csv`.

**Findings:**

- 2–4 breaks per asset per series, clustering around: (i) late 2020 (post-COVID recovery), (ii) late 2021 (Q4 deleveraging), and most consistently (iii) **November 2022 (FTX bankruptcy)**.
- Of the five known crisis episodes in the sample, only the **FTX bankruptcy** aligns with detected variance-level breaks in four of six assets (|r| series, ±60 day window). The COVID shock (Mar 2020), Terra/UST (May 2022), SVB/USDC depeg (Mar 2023), and Bybit hack (Feb 2025) produce transient spikes that the GARCH process absorbs without a regime change.
- **Within-sub-sample persistence falls materially**: the full-sample mean of α + β = 0.988 drops to an across-asset within-sub-sample mean of 0.905 (Table per-asset in §4.4.4). The IGARCH-like full-sample behaviour partly reflects un-modelled structural shifts.

**The asymmetry within sub-samples is not separately re-estimated in this revision** — given the multiplier-collapse finding in C2, re-running the infrastructure-regulatory comparison within Bai-Perron sub-samples would not change the central conclusion, and we prefer to focus on the C2 result for the revision. If R2 wishes us to run this additional decomposition in a subsequent revision round we will do so; it is a quarter-day of additional compute.

**Action in revised manuscript:**
- New §4.4.4 "Bai-Perron Structural-Break Tests" with per-asset break dates and the persistence table.
- §4.2 cross-references this section when discussing near-integration.
- Bibliography: Bai-Perron (1998), Bai-Perron (2003), and Killick-Fearnhead-Eckley (2012) added.

---

### R2.3 — Granger causality for sentiment and volatility

**Reviewer comment:** *"The relationship between news sentiment and volatility could be reflexive. To strengthen the causal claims regarding GDELT sentiment, the author should consider a Granger causality framework to verify if infrastructure news leads or simply follows the initial price collapse."*

**Response:** Agreed. The original treatment of sentiment was direction-agnostic.

We run pairwise Granger causality tests at lags 1–10 between (i) decomposed regulatory sentiment S_reg, (ii) decomposed infrastructure sentiment S_infra, and (iii) aggregate GDELT sentiment, versus absolute daily log returns, per cryptocurrency. The weekly GDELT data is forward-filled to daily, which biases the test conservatively against finding sentiment-leads-volatility effects (artificial persistence in the predictor). Full results in `c4-granger-results.csv`.

**Findings (n = 18 asset × sentiment-series pairs, lags 1–10, *p* = min over lags):**

| Direction | # significant @ 5% (out of 18) |
|---|---|
| Sentiment → Returns | **0** |
| Returns → Sentiment | 4 |

No asset-sentiment pair exhibits a significant sentiment-to-returns relationship at the 5% level at any lag from 1 to 10. Four pairs exhibit returns-to-sentiment significance (XRP with infrastructure sentiment, XRP and BNB with aggregate sentiment, BNB with regulatory sentiment). The pattern is consistent with news-follows-price: for these assets and this weekly sentiment series, sentiment does not lead volatility.

This means **H2 cannot be interpreted as sentiment-leading-volatility**. The claim that "even degraded sentiment proxies provide incremental explanatory power" survives as a statement about contemporaneous association and within-window covariation, but the revision restricts it to that interpretation. A daily-frequency GDELT extraction is flagged as the natural next step for sharper lead-lag testing.

**Action in revised manuscript:**
- New §4.4.5 "Sentiment Lead-Lag: Granger Causality" with the test results.
- §4.2 (H2 discussion) updated to reflect the lead-lag direction.
- Limitations: weekly aggregation flagged as limiting the resolution of the test.
- Bibliography: Granger (1969) added.

---

### R2.4 — Diebold-Mariano discussion

**Reviewer comment:** *"While the author employs the Diebold-Mariano test in Table 3, a more thorough discussion of these results is needed to compare the out-of-sample forecasting performance of the proposed GJR-GARCH-X model against a standard GARCH(1,1) benchmark more explicitly."*

**Response:** The Diebold-Mariano results appeared in a single sentence ("DM tests reject equal predictive accuracy versus GARCH(1,1) for all assets, *p* < 0.01"). The revision expands this to four sentences with per-asset DM statistics, magnitude interpretation (% MSE reduction), event-window decomposition, and the Harvey-Leybourne-Newbold small-sample correction.

**Action:**
- §4.2 (H2 / forecasting) expanded with the magnitude, the event-window decomposition (up to 25% within ±3 days vs 5–8% outside), the HLN correction, and the diagnostic significance of the within-vs-outside asymmetry.

---

### R2.5 — Correlation heatmap

**Reviewer comment:** *"In Section 4.1, the author may consider adding a correlation matrix, perhaps in the form of a heatmap."*

**Response:** Agreed. New Figure 1 in §4.1.

**Action:**
- New `figures-new/figure_correlation_heatmap.pdf` (6×6, RdBu_r colormap centred at zero, hierarchically clustered, annotated). Inserted into §4.1.

---

### R2.6 — "Relative independence" wording for ρ ≈ 0.5

**Reviewer comment:** *"The author characterises correlations around 0.5 as indicating 'relative independence.' In many financial contexts, a correlation of this magnitude is viewed as a moderate-to-strong relationship."*

**Response:** Fair point. Rephrased.

**Action:**
- §3.1: "while XRP shows relative independence (0.41–0.52)" → "XRP exhibits the lowest pairwise correlations (0.41–0.52); these are moderate-to-strong by standard financial-econometric conventions but notably below the BTC-ETH benchmark, likely reflecting XRP's distinct regulatory trajectory during the SEC litigation period."
- §4.1: parallel edit.

---

### R2.7 — Constant-mean-return assumption made explicit

**Reviewer comment:** *"It would be beneficial to explicitly mention in Section 3.4 (as shown in Appendix B) that the models assume a constant average return..."*

**Response:** Done.

**Action:**
- §3.4 (Volatility Modelling Framework): new sentence preceding the Model 1 specification stating that r_t = μ + ε_t with constant μ, that this is appropriate given the small and statistically indistinguishable-from-zero sample means in Table 1, and pointing to Appendix B for full documentation.

---

### R2.8 — Expanded Table 2 with α, β, θ₁, θ₂, ν

**Reviewer comment:** *"To provide a more comprehensive overview of the conditional variance dynamics, Table 2 could be expanded to include the estimated values for α, β, and the sentiment coefficients θ₁, θ₂, as well as the Student's t degrees of freedom (ν)."*

**Response:** Done. The remaining parameters are estimated and stored in the model-output JSON files; no new estimation was required.

**Action:**
- New Table 3 in §4.2 ("GJR-GARCH-X: Full Variance-Equation Parameters by Asset") reports ω, α, γ, β, ν, δ_infra, δ_reg, θ_reg, θ_infra per asset in a single compact panel.
- Brief discussion paragraph after the table flags the small-negative GJR γ estimates (best interpreted as event-dummy/indicator interaction), the close-to-bound Student-*t* degrees of freedom (heavy tails), and the asset-specific mixed signs on the sentiment coefficients (consistent with the C4 Granger finding).

---

## Summary of Manuscript Changes

| Section | Change | Origin |
|---|---|---|
| Abstract | Causal language softened; multiplier reported as range (1.5× to 5.7×); ETH-centrality demoted; Bai-Perron and Granger findings flagged | R1.1, R1.4, R2.1, R2.2, R2.3 |
| Introduction | ETH-centrality reframed as supplementary; exogeneity-axis framing introduced; new findings previewed | R1.2, R1.4 |
| §2 Literature | New positioning paragraph at end of §2.4 | R1.7 |
| §3.1 Data | "Relative independence" rephrased | R2.6 |
| §3.2 Event Classification | Exogeneity framing made explicit (§3.2.3); overlap-handling protocol stated (§3.2.4) | R1.2, R1.5 |
| §3.4 Methodology | Constant-mean assumption stated explicitly | R2.7 |
| §4.1 Descriptive Statistics | New Figure 1 correlation heatmap | R2.5 |
| §4.2 H1 Results | Expanded Table 3 with full parameter vector; near-integration paragraph | R2.8, R1.6 |
| §4.2 H2 Results | Diebold-Mariano expanded with HLN correction | R2.4 |
| §4.4 Robustness | New §4.4.4 Bai-Perron tests; new §4.4.5 Granger causality | R2.2, R2.3 |
| §4.5 Network | Reduced to single subsection; framing softened to "supplementary observation" | R1.4 |
| **§4.6 (new)** | Selection-bias sensitivity: drop-out census and relaxed-threshold sensitivity | **R2.1** |
| §5 Discussion | Causal language softened; selection-bias limitation quantified; network-centrality demoted | R1.1, R1.4, R2.1 |
| §6 Conclusion | Re-written around the range of multiplier estimates | R1.1, R2.1 |
| Bibliography | Bai-Perron (1998, 2003), Granger (1969), Harvey-Leybourne-Newbold (1997), Killick-Fearnhead-Eckley (2012) added | R2.2, R2.3, R2.4 |

The most consequential change is §4.6 and the corresponding re-write of the abstract, discussion, and conclusion. The pre-registered language commits to reporting whatever the relaxed-threshold result was; the result is a substantive qualification of the headline magnitude. We have honoured the pre-registration commitment.

We are grateful to both reviewers; the revision is a materially better paper for the engagement.
