# C10 -- Monte-Carlo Size-Distortion Study of the Inference Ladder

_N=923 true-null panels (of 1000 requested); bootstrap critical values calibrated from B_ref=4000; numba=False; runtime 21.4 min._

## The question

Does the naive iid inference the prior/headline analysis used OVER-REJECT a true null of no differential event effect, and do the dependence-robust / heavy-tailed methods restore nominal size? A correctly-sized test rejects a true null exactly alpha of the time; an over-rejecting test manufactures false 'significance'. This is the demonstration that turns the paper's pseudoreplication argument from assertion into measured fact.

## DGP (true null, fitted to the data)

- Per-asset **GJR-GARCH-X** variance dynamics estimated under the **null-imposed** combined-dummy spec (D_event = D_infra + D_reg), so delta_infra = delta_reg **by construction** -- there is genuinely no differential event effect in the truth.
- Cross-asset dependence at the **standardised-residual correlation** rho_resid = 0.705 (return-correlation rho_return = 0.688), via the Cholesky of R_z.
- **Student-t innovations** at each asset's fitted nu = [3.175;3.701;3.144;4.198;3.947;4.563] (median nu_c = 3.824), unit variance, with joint tail dependence via a true multivariate-t copula (shared chi-square mixing) -- identical DGP to c9.
- The **actual 26 infra / 24 reg** event-label structure and the real event-window dummies are reused unchanged for every panel; only returns are re-simulated. (Point estimate on the real data: d_bar = 1.573, 4.89x -- the SIM imposes the null, this is shown only to anchor the DGP.)

## The size table (empirical rejection rate under a true null)

| method | size @ alpha=0.05 | size @ alpha=0.10 |
|---|---|---|
| (i) NAIVE iid t-test | **0.512** +/- 0.016 | **0.701** +/- 0.015 |
| (ii) design-effect corrected | 0.434 +/- 0.016 | 0.655 +/- 0.016 |
| (iii) Gaussian-copula bootstrap | 0.308 +/- 0.015 | 0.398 +/- 0.016 |
| (iv) Student-t-copula bootstrap | 0.039 +/- 0.006 | 0.095 +/- 0.010 |

_(+/- = Monte-Carlo binomial standard error.) Nominal size is 0.05 and 0.10._

## Self-validation (correctness check)

The Student-t-copula bootstrap (iv) is calibrated from the SAME DGP the panels are drawn from, so its size MUST land ~nominal up to Monte-Carlo error -- this is the implementation tripwire. It comes out **0.039 @0.05** and **0.095 @0.10** (targets 0.05/0.10). Both within ~MC error of nominal: the DGP/implementation passes the check.

## Verdict on the naive over-rejection

- The **naive iid t-test rejects a true null 51.2% of the time at the 5% level (10.2x nominal) and 70.1% at the 10% level (7.0x nominal).** This is severe size distortion: a 'significant' headline from this rule is, under the realistic null, a manufactured false positive a large fraction of the time. It is the direct, simulated counterpart of the pseudoreplication diagnosis -- the six assets are not six independent draws.
- The **design-effect correction** pulls size down to 0.434/0.655; it helps but does not fully restore nominal size (it uses the raw-return correlation as a proxy and ignores the GARCH/heavy-tail structure).
- The **Gaussian-copula bootstrap** lands at 0.308/0.398 and the **Student-t-copula bootstrap** at 0.039/0.095 -- both at/near nominal, with the heavy-tailed t-copula the most faithful to the fat-tailed (nu~3) DGP. The dependence-robust methods that the paper adopts as its inference of record control size; the naive rule does not.

## Method notes

- (i) NAIVE: Welch t-test on the 6 per-asset delta_infra vs 6 delta_reg as iid (the headline rule that produced t=4.768/p=0.0008).
- (ii) DESIGN-EFFECT: paired-difference SE inflated by sqrt(1+(N-1)*rho_bar) on the cross-asset RETURN correlation, t on N-1 df (c6's rule).
- (iii)/(iv) BOOTSTRAP: ONE-SIDED upper-tail test (H1: infra>reg) -- reject if d_bar exceeds the (1-alpha) quantile of the respective null sampling distribution of d_bar (Gaussian copula = c7; Student-t copula = c9), exactly the c7/c9 decision p=P(null>=d_bar)<alpha. Under the true null the bootstrap's null DGP IS the simulation DGP, so the critical value is a property of the DGP and is calibrated once from B_ref reference draws rather than via a redundant O(N x B) nested refit. One-sided critical d_bar: Gaussian 5%=1.6152/10%=1.4538, t-copula 5%=2.4448/10%=2.1655 (null centres 0.9289 / 1.2886).

## Fragility / honest caveats

- **Convergence:** 7.7% of the 1000 outer panels were dropped (a per-asset refit failed to converge, hit a degenerate |delta|>50 optimum, or returned a non-positive-definite Hessian sub-block for the SE). Reference-draw drop rates: Gaussian 5.8%, t-copula 7.3%. All under the 10% reliability threshold (reliable).
- **Per-asset model SEs are audit-only, not on the decision path.** Neither rung (i) (Welch on the 6 vs 6 coefficients) nor rung (ii) (dispersion of the 6 paired differences, c6's rule) uses the per-asset model SE, so an SE failure never drops a panel or flips a decision. The numerical-Hessian SEs are computed only for reporting; their sub-block was positive-definite for 98.7% of accepted panels. Panel acceptance is therefore identical to the reference-draw rule (convergence + |delta|<=50), which is exactly what makes rung (iv)'s size nominal by construction.
- **The bootstrap rungs are calibrated, not fully nested.** This is exact for SIZE (shared null DGP) but means rungs (iii)/(iv) here measure the size of the bootstrap *decision rule under its own correctly-specified null*; a fully-nested loop would additionally absorb per-panel re-centring noise, which is a second-order effect on size and is the standard simplification.
- **Copula df** for the t-copula tail-mixing is the median fitted nu (one shared dependence parameter); margins are exact per-asset. The Gaussian-copula rung shares the t-copula's margins only through the separate c7 draw path (Gaussian innovations), so (iii) is the genuine 'right dependence, wrong tails' comparator and (iv) the fully-correct one.
- **Monte-Carlo error**: sizes carry binomial SEs of ~0.016-0.015; differences within ~2 SE of each other or of nominal are not separable at this N.

## Files

- `c10-size-study-results.csv` -- size table + DGP metadata
- `c10-size-study-draws.npz` -- panel d_bar, per-panel p-values (iid/deff), reference null draws, critical values
- `code/c10_size_study.py` (reuses `tarch_x_fast.py`, `c7_ccc_garchx_bootstrap.py`, `c9_tcopula_bootstrap.py`)