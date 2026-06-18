# C8h — Cross-Asset-Robust Significance of the Break-Controlled Multiplier

_Null-imposed CCC-GARCH-X parametric bootstrap, B=2000; runtime 15.5 min; same engine as c7 (regime dummies added to the variance-equation exog)._

## The gap this closes

c8a reported the break-controlled multipliers (full-regime 2.64x, crisis 3.97x) with NAIVE Welch p-values (0.0115, 0.0033) that treat the 6 per-asset event coefficients as independent — the exact pseudoreplication c7 corrected for the baseline (naive 0.0015 -> robust 0.059). This applies the cross-asset-robust inference to the controlled specs.

**c7 baseline (uncontrolled) for reference:** multiplier 4.88x, naive Welch p=0.0015, **cross-asset-robust CCC null-imposed p=0.059** (marginal — sig at 10%, not 5%).

## Result

| variant | multiplier | naive Welch p | **robust CCC p (1-sided)** | robust 2-sided | rho_resid | dropped |
|---|---|---|---|---|---|---|
| full regime | 2.64x | 0.0115 | **0.1091** | 0.1155 | 0.701 | 22.1% |
| crisis regime | 3.96x | 0.0033 | **0.0611** | 0.0622 | 0.703 | 6.0% |

- **full regime dummies** (multiplier 2.64x, d_bar_obs=1.517): NOT significant at 10% under CCC bootstrap (p=0.1091) — only directional. Naive Welch was 0.0115; the cross-asset-robust value is 0.1091.
- **crisis regime dummies** (multiplier 3.96x, d_bar_obs=1.431): MARGINAL: significant at 10% but NOT 5% under CCC bootstrap (p=0.0611) — same regime as the c7 baseline (0.059). Naive Welch was 0.0033; the cross-asset-robust value is 0.0611.

## Honest verdict

Under proper cross-asset-robust inference the break-controlled asymmetry is full-regime p=0.1091, crisis-dummy p=0.0611. Compare the controlled NAIVE p's (0.0115 / 0.0033) and the c7 baseline robust p (0.059). The naive controlled significance does NOT hold under the right inference — the controlled multiplier is best read as DIRECTIONAL (and, like the baseline, at best marginal). Whichever way it lands, 'still significant at 5%' from c8a's Welch p was on the wrong inference.

## Reliability caveat (read the crisis variant as the clean one)

- **Crisis-dummy variant is the trustworthy read: 6.0% of null refits dropped — under c7's 10% reliability bar.** Its p=0.0611 lands essentially on top of the c7 uncontrolled baseline (0.059): adding the single FTX-crisis control leaves the significance exactly where it was — marginal (10%, not 5%).
- **Full-regime variant is reliability-FLAGGED: 22.1% of null refits dropped — ABOVE the 10% bar.** With one combined event dummy plus 3–4 regime dummies all competing to explain the variance LEVEL, the null fits hit degenerate optima far more often (SLSQP boundary solutions), so a fifth of draws are rejected. Its p=0.1091 is directionally informative (the asymmetry weakens further once full regime structure is absorbed) but should NOT be quoted as a precise figure — the drop rate exceeds the reliability threshold. The honest statement is "≥10%, not significant," not "exactly 0.109".

**Bottom line for the manuscript:** the break-controlled infra>reg asymmetry, under the same cross-asset-robust inference used for the headline (c7), is **marginal at best** — crisis-control p=0.061 (clean, ≈ the 0.059 baseline), full-regime p≥0.10 (flagged, not significant). It is NOT "still significant at 5%". The controlled result is directional and, at most, weakly significant at the 10% level — consistent with the baseline never having cleared 5% under proper inference either.

## Files

- `c8h-break-ccc-bootstrap-results.csv`, `c8h-break-ccc-draws-{full,crisis}.npz`
- `code/c8h_break_controls_ccc_bootstrap.py` (reuses `c7_ccc_garchx_bootstrap.py` engine)