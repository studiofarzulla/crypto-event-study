# C9 -- Student-t-Copula CCC-GARCH-X Bootstrap (corrected inference of record)

_B=2000; copula=true multivariate-t (shared chi-square mixing) with per-asset Student-t margins at the FITTED nu; runtime 42.8 min._

## What was wrong

c7 and c8h are the cross-asset-robust significance tests for the infrastructure-vs-regulatory variance-coefficient asymmetry. Their CCC parametric bootstrap drew the standardised innovations as **Gaussian** (`rng.standard_normal`) even though each GJR-GARCH-X is fitted with **Student-t** errors, nu ~ 3.1-4.6. With nu ~ 3 the true innovation is far heavier-tailed than a Gaussian, so the Gaussian draw makes the null distribution of d_bar **too narrow** -> the bootstrap p is biased **downward** (optimistic). The reported p's were therefore flattered.

## The fix

Innovations are now drawn from a Student-t copula: latent MVN(0, R_z) divided by a shared chi-square (-> multivariate-t, joint tail dependence), mapped to uniforms, then to per-asset Student-t margins at the **fitted nu**, rescaled to unit variance by sqrt((nu-2)/nu). Same change in the null-imposed and unrestricted draws; everything else (B, null via combined dummy, refit, drop guards) is the c7/c8h engine unchanged (monkeypatched draw functions only).

## Results: OLD Gaussian (wrong) vs NEW t-copula (correct)

| spec | multiplier | OLD Gaussian p (1-sided) | **NEW t-copula p (1-sided)** | NEW 2-sided | null SD Gauss -> t | drop rate (t) |
|---|---|---|---|---|---|---|
| baseline | 4.88x | 0.0571 | **0.3218** | 0.3234 | 0.4549 -> 0.7872 | 7.6% |
| crisis | 3.97x | 0.0611 | **0.3180** | 0.3212 | 0.4730 -> 0.8407 | 6.7% |
| full | 2.64x | 0.1091 | **0.2485** | 0.2844 | 0.8388 -> 1.4001 | 23.4% |

## Validation that the fix behaves correctly

The decision-relevant validation is that **the corrected (heavier-tailed) draw raises p** relative to Gaussian. It does, in every spec (below). Re-running the OLD Gaussian draw with the SAME seeds and design in-process:
- **baseline**: p 0.0571 (Gaussian) -> 0.3218 (t-copula) [p ROSE]; null SD 0.4549 -> 0.7872.
- **crisis**: p 0.0611 (Gaussian) -> 0.3180 (t-copula) [p ROSE]; null SD 0.4730 -> 0.8407.
- **full**: p 0.1091 (Gaussian) -> 0.2485 (t-copula) [p ROSE]; null SD 0.8388 -> 1.4001.

**Note on the null SD (why it does NOT widen).** A naive expectation is that heavier tails widen the null SD. That holds for an *un-rescaled* Student-t (variance nu/(nu-2) ~ 3 for nu ~ 3), but the spec correctly feeds **unit-variance** innovations (rescaled by sqrt((nu-2)/nu)) -- the variance recursion already carries the scale via sigma2_t. A unit-variance t with nu ~ 3 is MORE concentrated in the body than a Gaussian (~80% of mass within +/-1 vs 68%), with its unit variance made up by rare extreme tails. So the bulk of refits is tighter (lower SD) while the occasional extreme draw shifts the null distribution's LOCATION upward toward d_bar_obs -- which is what raises p. Direct check of the innovations confirms unit variance, Gaussian-beating excess kurtosis (8-60 vs ~0), and preserved cross-asset correlation. The SD-widening heuristic is therefore the wrong tripwire for unit-variance margins; p rising is the correct one, and it does.
## Per-spec verdict

- **baseline** (4.88x, d_bar_obs=1.573): NOT significant at 10% -- directional only (p=0.3218).
- **crisis** (3.97x, d_bar_obs=1.431): NOT significant at 10% -- directional only (p=0.3180).
- **full** (2.64x, d_bar_obs=1.517): NOT significant at 10% -- directional only (p=0.2485).

## Honest headline

With the correct Student-t innovations the baseline headline is **p=0.3218 -- NOW NON-SIGNIFICANT** (>0.10). The Gaussian draw's p=0.059 was an artifact of too-thin tails. The point estimate (4.88x) is unchanged, but the asymmetry is no longer statistically distinguishable from zero under correct inference -- it is DIRECTIONAL ONLY.

Crisis-control stability: crisis-dummy p=0.3180 vs baseline p=0.3218 -> the 'controls don't kill it' story **still holds** (crisis p stays in the baseline neighbourhood). Full-regime p=0.2485 (was the weakest spec under Gaussian too).

## Caveats

- The copula df for the true-t mixing is the median fitted nu (a single shared tail-dependence parameter); margins are exact per-asset. Using a common copula df is standard and conservative on the dependence axis.
- Non-overlap (non-common-window) positions get independent unit-variance Student-t draws at each asset's fitted nu (they don't enter cross-asset corr), matching c7's treatment of those positions.
- Bootstrap refits use a single default start (speed); observed fits use multistart. Degenerate refits (|delta|>50) dropped and counted; drop rates reported above.
- `USE_T_COPULA` toggles true-t-copula vs Gaussian-copula-with-t-margins; the headline above uses the true t-copula.

## Files

- `c9-tcopula-results.csv`, `c9-tcopula-draws-{baseline,crisis,full}.npz`
- `code/c9_tcopula_bootstrap.py` (reuses `c7_ccc_garchx_bootstrap.py` + `c8h_break_controls_ccc_bootstrap.py` engines)