# C7 -- CCC-GARCH-X Bootstrap: Definitive Cross-Asset-Robust Test

_Bootstrap B=2000; numba=False; runtime 13.8 min._

## The question

Is the infrastructure-vs-regulatory variance-coefficient asymmetry (d_bar = mean_a(delta_infra - delta_reg) over 6 assets) significant once cross-asset dependence is handled correctly -- i.e. via a model-based bootstrap of the ACTUAL GJR-GARCH-X estimator, with cross-asset dependence calibrated to the STANDARDISED-residual correlation rather than the raw-return correlation c6 used as a post-hoc proxy? c6 bracketed p ~ 0.067-0.078 and conjectured it had OVER-penalised (residual corr assumed << return corr). This test checks that conjecture directly.

## Per-asset coefficients (baseline S1, 50 events)

| asset | delta_infra | delta_reg | diff |
|---|---|---|---|
| btc | 1.0081 | 0.2984 | 0.7097 |
| eth | 2.2474 | 0.4881 | 1.7593 |
| xrp | 2.2374 | 1.2192 | 1.0181 |
| bnb | 1.2055 | 0.1814 | 1.0241 |
| ltc | 2.3797 | 0.1436 | 2.2360 |
| ada | 2.7915 | 0.0990 | 2.6925 |

## Headline numbers

- **d_bar_obs** = 1.5733
- **multiplier** (mean infra / mean reg) = 4.885x
- **rho_bar(returns)** = 0.6882
- **rho_bar(standardised residuals)** = 0.7048  <- the crux. The pre-test hypothesis was that GARCH strips common volatility, so rho_resid would be MUCH LOWER than rho_return and c6's raw-return penalty would be too harsh. That did NOT hold: rho_resid (0.705) is actually slightly HIGHER than rho_return (0.688). Standardising by sigma_t removes idiosyncratic fat-tailed spikes and concentrates the shared component, so the cross-asset dependence the bootstrap must respect is NOT lower than c6 assumed. c6 was therefore NOT over-penalising on the correlation axis -- which is why the proper test does not undercut c6's ~0.07.

## Significance

- **Parametric NULL-imposed (CCC MVN copula on R_z) -- INFERENCE OF RECORD: one-sided p = 0.0587**, two-sided p = 0.0592 (B used 1873, dropped 6.3%). This redraws the standardised innovations from a Student-t variance path with the fitted cross-asset correlation, refits unrestricted, and compares the observed d_bar to the null sampling distribution (correctly including the estimator's finite-sample bias).
- Cross-sectional WILD (Rademacher, shared eta_t): one-sided p = 0.0016, two-sided p = 0.0021 (B used 1898, dropped 5.1%). **DO NOT TRUST this p as significance evidence.** Sign-flipping residuals barely perturbs a VARIANCE-equation coefficient because eps^2 is sign-invariant; the wild d_bar distribution is near-degenerate (sd ~0.1), so the tiny p is an artifact of under-dispersion, not power. It is reported only for completeness; it is the wrong instrument for this estimand.
- Unrestricted parametric CI for d_bar (bias-corrected basic bootstrap; the estimator is upward-biased by median 0.447 in this sample): 90% [0.3858, 1.7637], 95% [0.1956, 1.8951]; fraction of (bias-corrected) draws <= 0 = 0.0106 (raw percentile 95% [1.2514, 2.9510]; B used 1884, dropped 5.8%)

## Where the truth lands vs c6 (p ~ 0.067-0.078)

The proper test (0.0587) **lands right on top of c6's ~0.07: still MARGINAL (significant at 10%, not at 5%).** It neither rescues the result to 5% nor undercuts it below 10%. The premise that c6 over-penalised by using the raw-return correlation does NOT hold here -- the standardised-residual correlation (0.705) is if anything slightly higher than the return correlation (0.688), so the correct cross-asset dependence is no weaker than c6 assumed, and the p-value stays in the same place. c6's post-hoc bracketing turns out to have been a good approximation.

## Verdict

Marginal: significant at 10% but NOT at 5% under the parametric null-imposed CCC bootstrap (p=0.0587). Same ballpark as c6.

## Caveats (honest)

- **The parametric null IS the inference of record.** It uses a Gaussian copula (MVN on R_z) for cross-asset dependence of standardised innovations; the per-asset variance path is the fitted Student-t GJR model, but the cross-asset copula itself is Gaussian (tail dependence not modelled). With nu~3 marginals this could mildly understate joint tail co-movement; the direction of any resulting bias on the p-value is not obvious, but the headline is robust to it being marginal either way.
- **The wild bootstrap is NOT a usable anchor here** (contrary to the usual model-free role): Rademacher sign-flips leave eps^2 -- and hence the variance-equation event coefficients -- almost unchanged, collapsing the wild d_bar distribution (sd ~0.1) and producing an artificially tiny p. We flag this rather than hide it.
- The unrestricted GARCH event-coefficient estimator is upward-biased in this small sample (bootstrap median bias ~0.45); the null-imposed test handles this automatically (its null distribution is centred at the biased-under-equality location, not at 0), and the reported CI is the bias-corrected basic-bootstrap interval.
- Bootstrap refits use a single default start (no multistart) for speed; the observed fits use multistart. Degenerate refits (SLSQP 'success' but |delta|>50, e.g. beta->0 / omega blown up) are rejected and counted as dropped.
- Convergence: dropped fractions above are the share of refits dropped; all are well under the 10% reliability threshold at the final B.

## Files

- `c7-ccc-bootstrap-results.csv` -- per-asset + summary
- `c7-bootstrap-draws.npz` -- raw d_bar draws (null/unr/wild)
- `code/c7_ccc_garchx_bootstrap.py`, `code/tarch_x_fast.py`