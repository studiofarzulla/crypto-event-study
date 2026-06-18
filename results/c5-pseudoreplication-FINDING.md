# C5 — Pseudoreplication re-test: the headline significance does NOT survive (BLOCKING)

**Date:** 17 Jun 2026. **Trigger:** external triage tool flagged the headline test (t=4.768, p=0.0008)
as pseudoreplication — it treats the 6 per-asset GJR-GARCH-X event coefficients as N=6 independent
observations, but all 6 assets see the same 50 events and correlate 0.54–0.83.

## Re-test (model-free abnormal-variance proxy; `code/c5_pseudoreplication_test.py`)
Abnormal variance = mean squared daily log-return (%²) in the [-3,+3] event window minus the asset's
full-sample mean squared return.

| Test | infra vs reg | statistic | p |
|---|---|---|---|
| Headline (N=6 per-asset coefficients) | 5.7× (GARCH-X) | t=4.768 | **0.0008** |
| Event-level, N=50 (events as unit), Welch | 24.3 vs 11.6 (2.1×) | t=0.65 | **0.52** |
| Event-level, Mann-Whitney | — | U=344 | **0.54** |
| Cluster-robust panel (295 obs, SE clustered by 50 events) | coef 13.4 (SE 19.8) | t=0.68 | **0.50** |

## UPDATE — definitive GARCH-X-based test (`code/c6_garchx_clustered.py`)
The event-level test above uses a *model-free* realized-variance proxy with low power. The fair test —
the reviewer's "panel GARCH + clustered SE" on the **actual GJR-GARCH-X estimator** — re-fits per asset
and applies cross-asset-correlation-robust inference (mean cross-asset ρ̄ = 0.69):

| Test | t | p |
|---|---|---|
| Headline (iid, reproduces paper) | 4.68 | 0.0015 |
| Design-effect corrected (effective N≈1.4) | 2.33 | **0.067** |
| Correlation-weighted (per-asset model SEs) | 1.76 | **0.078** |

**Definitive conclusion: the asymmetry is MARGINALLY significant (p ≈ 0.07), not "highly significant"
(p<0.001) and not a clean null.** The uncorrected p=0.0008 overstates precision because the 6 assets
(ρ̄≈0.69) are not independent; the model-free p≈0.5 understates it (low-power proxy). The truth is in
between: significant at 10%, not at 5%. Point estimate (~4.9–5.7×) and direction unchanged.

## (Superseded) earlier conclusion from the model-free proxy
**The infrastructure-vs-regulatory asymmetry is directional (point estimate ~2–6× depending on
estimator) but NOT statistically significant once cross-asset correlation is properly handled.**
The headline p=0.0008 is spurious precision from pseudoreplication: the 6 per-asset coefficients are
tightly clustered because they average the *same* correlated events, not because the effect is
precisely estimated. The correct event-level/clustered standard error is an order of magnitude larger,
and the difference falls to p≈0.5.

This is the most serious issue in the paper. It is NOT a wording fix — it removes the central
significance claim ("infrastructure events generate a *significantly* larger response, p=0.0008").
The scope-conditioned framing (5.7× curated, attenuating under mechanical screening) already softened
the magnitude; this removes the significance of even the curated-sample asymmetry under proper inference.

## Caveat / definitive test
This uses a model-free realized-variance proxy, not the GJR-GARCH-X estimator. The definitive test is a
**panel GJR-GARCH-X estimated jointly across assets with event-clustered standard errors**. But two
independent model-free methods both give p≈0.5, and proper clustering necessarily inflates the SE far
above the N=6 value, so the headline significance is very likely an artifact regardless. The panel
GARCH-X would confirm, not overturn, the direction of this finding.

## Implication (MF decision)
The paper's empirical core needs a fundamental rethink, not a patch:
- (a) Run the panel GJR-GARCH-X + clustered SE to confirm definitively.
- (b) Reframe honestly around a *directional but non-significant* asymmetry + the scope condition — a
  much weaker claim, likely below Digital Finance's bar as a "significant asymmetry" paper.
- (c) Reconsider the contribution/venue: the honest result is "infra appears larger but we cannot
  reject equality of infra vs reg event impacts under proper inference" — which is closer to the
  no-structure companion's null than to the original headline.
Regime-switching (H3) and out-of-sample DM were NOT run pending this decision — they are moot until
the headline is resolved.
