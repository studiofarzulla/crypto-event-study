# C14 -- GARCH Squared-Residual Diagnostics (baseline GJR-GARCH-X)

_Baseline S1 spec (26 infra + 24 reg curated events); FastTARCHX multistart fit (same model as c6/c7); numba=False; runtime 12.2s._

## The question

Reviewer #C2 asks whether the GJR-GARCH-X variance equation fully absorbs conditional heteroskedasticity *before* the event coefficients are interpreted. If standardised residuals still carry ARCH, then unmodelled volatility clustering -- which is concentrated in the 2022-23 window where the infrastructure events (Terra/Luna, FTX, etc.) cluster -- could be absorbed by the D_infra dummy and mechanically inflate delta_infra and the ~4.88x curated multiplier. The test: Ljung-Box Q on z_t^2 at lags 5/10/20 plus Engle ARCH-LM, per asset.

## Fitted variance parameters (baseline)

| asset | n | omega | alpha | gamma | beta | nu | persist. | dInfra | dReg |
|---|---|---|---|---|---|---|---|---|---|
| btc | 2434 | 0.1148 | 0.0741 | -0.0000 | 0.9249 | 3.13 | 0.9990 | 1.0079 | 0.2984 |
| eth | 2434 | 0.1271 | 0.0704 | -0.0081 | 0.9246 | 3.76 | 0.9990 | 2.2474 | 0.4881 |
| xrp | 2434 | 1.3256 | 0.2134 | -0.0273 | 0.7719 | 3.14 | 0.9990 | 2.2373 | 1.2191 |
| bnb | 2191 | 0.2863 | 0.1390 | -0.0109 | 0.8545 | 4.21 | 0.9990 | 1.2055 | 0.1814 |
| ltc | 2434 | 0.7105 | 0.0983 | -0.0337 | 0.8838 | 3.93 | 0.9990 | 2.3796 | 0.1436 |
| ada | 2434 | 1.4038 | 0.1587 | -0.0250 | 0.8006 | 4.58 | 0.9718 | 2.7915 | 0.0990 |

_persist. = alpha + beta + |gamma|/2 (stationarity < 1)._

## Standardised-residual moments (whitening sanity)

| asset | mean(z) | mean(z^2) | excess kurt(z) |
|---|---|---|---|
| btc | 0.002 | 0.837 | 3.53 |
| eth | 0.003 | 0.922 | 2.71 |
| xrp | -0.008 | 0.890 | 5.86 |
| bnb | -0.016 | 0.958 | 2.73 |
| ltc | 0.001 | 0.947 | 2.33 |
| ada | -0.012 | 0.966 | 2.32 |

_mean(z)~0 and mean(z^2)~1 indicate the variance level is captured; residual excess kurtosis is expected (Student-t marginals) and is not an ARCH symptom._

## Ljung-Box Q on z_t^2 (residual-ARCH portmanteau)

| asset | Q(5) | p5 adj | Q(10) | p10 adj | Q(20) | p20 adj |
|---|---|---|---|---|---|---|
| btc | 6.60 | 0.0857 | 11.67 | 0.1665 | 23.53 | 0.1712 |
| eth | 1.28 | 0.7337 | 7.70 | 0.4632 | 15.57 | 0.6227 |
| xrp | 2.46 | 0.4832 | 5.12 | 0.7446 | 10.60 | 0.9107 |
| bnb | 3.53 | 0.3170 | 9.91 | 0.2717 | 19.03 | 0.3900 |
| ltc | 3.63 | 0.3037 | 7.02 | 0.5347 | 14.13 | 0.7207 |
| ada | 3.87 | 0.2753 | 9.07 | 0.3366 | 17.37 | 0.4979 |

_p..adj is the Li-Mak (1994) adjustment, df = lag - 2 (subtracting the ARCH+GARCH lag orders p+q=2; gamma is a within-lag asymmetry term, not an extra lag order), the honest df for a fitted GARCH(1,1). Naive-df p-values (df = lag) are in the CSV; they tell the same story._

## Engle ARCH-LM on z_t (T*R^2 of z^2 on its lags)

| asset | LM(5) | p(5) | LM(10) | p(10) |
|---|---|---|---|---|
| btc | 6.67 | 0.2466 | 11.74 | 0.3030 |
| eth | 1.24 | 0.9405 | 9.12 | 0.5207 |
| xrp | 2.48 | 0.7802 | 5.25 | 0.8741 |
| bnb | 3.47 | 0.6279 | 9.62 | 0.4748 |
| ltc | 3.59 | 0.6101 | 7.08 | 0.7178 |
| ada | 3.94 | 0.5581 | 9.39 | 0.4953 |

## Significant residual-ARCH flags (p < 0.05)

- Ljung-Box(z^2), adjusted df: lag5 = 0/6, lag10 = 0/6, lag20 = 0/6 assets.
- Ljung-Box(z^2), naive df (for reference): lag5 = 0/6, lag10 = 0/6, lag20 = 0/6 assets.
- ARCH-LM: lag5 = 0/6, lag10 = 0/6 assets.
- Assets flagged by ANY adjusted test: none.

## Verdict

ADEQUATE. No asset shows significant residual ARCH at the 5% level on either the adjusted Ljung-Box(z^2) portmanteau (lags 5/10/20) or the Engle ARCH-LM test (lags 5/10). The GJR-GARCH-X variance equation fully absorbs the conditional heteroskedasticity, so the event coefficients delta_infra/delta_reg are estimated on properly whitened squared residuals. The curated ~4.88x multiplier is NOT an artifact of unmodelled volatility clustering being soaked up by the 2022-23 infrastructure-event dummies.

## Caveats (honest)

- The portmanteau on squared standardised residuals is the standard McLeod-Li check for *remaining* ARCH after a GARCH fit; it does not test the level fit (mean(z^2)~1 covers that separately above).
- df adjustment: Li-Mak (1994), df = lag - (p+q) = lag - 2, subtracting the one ARCH lag (alpha) and one GARCH lag (beta). gamma (leverage) is a within-lag asymmetry term, and omega / the 5 exog deltas are level terms, so none of those is subtracted. The naive-df column is also reported and yields the same conclusion. (Counting gamma as a third 'lag' term, df = lag - 3, would push only one borderline statistic -- btc lag-5 -- to p=0.037; that is a df-convention artifact, not residual ARCH: btc's ARCH-LM(5) p=0.247 and its naive LB(5) p=0.252 are both far from significant.)
- A clean portmanteau means no *linear* ARCH remains in z^2; it does not rule out higher-order nonlinearity or regime structure (those are handled separately by the Bai-Perron / persistence-break analyses in c3/c8).
- This diagnostic conditions on the fitted point estimates (multistart MLE); it is descriptive of model adequacy, not an inference test on the deltas (that is c7's CCC bootstrap).

## Files

- `c14-garch-diagnostics-per-asset.csv` -- full per-asset table
- `code/c14_garch_diagnostics.py`, `code/tarch_x_fast.py`, `code/c2_relaxed_threshold_sensitivity.py`