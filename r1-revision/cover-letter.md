# Cover Letter — R1 Revision

**To:** *Digital Finance* Editorial Board
**Re:** Infrastructure vs Regulatory Shocks: Asymmetric Volatility Response in Cryptocurrency Markets (Manuscript ID DAFI-D-25-…)
**Author:** Murad Farzulla
**Date:** [pending submission]

---

Dear Editors,

Please find attached the revised manuscript responding to the Major Revision decision and the two referee reports. The revision is substantial and changes the headline framing of the paper in a way that warrants a brief preview here, ahead of the point-by-point response.

The single most consequential addition is the new Section 4.6, "Selection-Bias Sensitivity: Relaxed-Threshold Estimation," directly responding to Reviewer 2's central comment (R2.1). The reviewer asked whether the 5.7× infrastructure-regulatory multiplier survives when the Stage-2 "demonstrable market-wide impact" filter is relaxed across the original ~208 candidates. We have reconstructed a systematic candidate pool of 135 events from public-record sources (Rekt/DeFiLlama hack leaderboards, SEC/CFTC enforcement records, major-jurisdiction regulatory announcements, exchange status pages), and re-estimated the GJR-GARCH-X specification under four candidate-pool definitions: baseline (n=50, the impact-screened sample), relaxed (≥1 asset response, n=115), no-filter (n=135), and strict (≥3 assets, n=77). The multiplier under baseline is 4.88× (re-fit; the originally-published 5.7× reflects winsorisation differences and is retained as canonical for the screened sample), but **falls to 1.49× under relaxed inclusion and inverts to 0.58× without the impact filter**. The direction of the asymmetry survives in three of four specifications; the magnitude does not. The revised abstract, discussion, and conclusion are written around this range of estimates rather than around a single point estimate.

We have not papered over this finding. The honest characterisation is that the published 5.7× multiplier describes the sample of events large enough to produce multi-asset spikes, not a population-level claim about all infrastructure versus all regulatory events. Under the relaxed-threshold specification the asymmetry direction is preserved but the multiplier is not statistically distinguishable from one (Welch *p* = 0.32). This is a substantive qualification of the headline that the original submission did not articulate. The pre-registered text in our response letter committed to reporting whatever the relaxed-threshold result was; we have honoured that commitment.

The other major computational additions are (i) formal Bai-Perron-style structural-break tests on each cryptocurrency's variance process, which detect 2–4 breaks per asset clustering around the November 2022 FTX collapse and reveal that the unconditional α + β ≈ 0.998 falls to a within-regime mean of 0.905 once breaks are accommodated (R2.2 and R1's near-integration comment); and (ii) Granger causality tests at lags 1–10 between decomposed GDELT sentiment and absolute returns, which find no evidence that sentiment leads volatility, with the four significant directional pairs all running returns-leads-sentiment (R2.3). The H2 claim of "sentiment provides incremental explanatory power" survives as a contemporaneous-association statement but is no longer interpreted as evidence of sentiment leading volatility.

The presentation upgrades requested by Reviewer 2 — the correlation heatmap (R2.5), the expanded parameter table reporting ω, α, β, γ, θ₁, θ₂, and ν per asset (R2.8), the Diebold-Mariano discussion with HLN small-sample correction (R2.4), the rephrasing of "relative independence" (R2.6), and the explicit constant-mean-equation statement (R2.7) — are all incorporated. Reviewer 1's tone-moderation request (R1.1) has been applied across the abstract, introduction, discussion, and conclusion; the exogeneity-axis framing (R1.2) is now explicit in §3.2; the network-centrality result is reframed as a supplementary observation (R1.4); and the overlap-handling protocol is enumerated (R1.5).

A few items remain candidates for further iteration in a second round if the editors wish:

1. **Bai-Perron within-sub-sample re-estimation of the infrastructure-regulatory comparison.** Given the C2 multiplier collapse, this seemed lower-priority for this revision; we focused on reporting the C2 finding cleanly rather than running the further decomposition. A quarter-day of additional compute.

2. **Daily-frequency GDELT sentiment.** The Granger result is reported on weekly-aggregated forward-filled sentiment; daily extraction would offer sharper lead-lag resolution. This is flagged as future work in the Limitations section.

3. **A formal proportion test on the drop-out census under alternative candidate-pool reconstructions.** Our pool of 135 events is systematic but smaller than the original 208 list (which included some borderline / sub-impact items). The pass-rate differential is the substantive output and is robust to candidate-pool size by construction, but we are open to running a second pool from a different source compendium if that would strengthen the response.

We believe the revised manuscript is a more honest, better-calibrated paper than the original submission. The selection-bias finding does undercut the original headline, but it also clarifies what the impact-screened result actually says about cryptocurrency markets: there is a genuine asymmetry within the sample of events that produce multi-asset volatility spikes, even if the population-level magnitude is more modest than the original framing suggested. The Bai-Perron and Granger additions sharpen the model's interpretation in ways that improve credibility independent of the C2 outcome. We hope the revised paper merits publication in *Digital Finance*; we are open to further iteration if specific elements require additional treatment.

Sincerely,

Murad Farzulla
Farzulla Research / Dissensus AI
[murad@dissensus.ai]
ORCID: 0009-0002-7164-8704
