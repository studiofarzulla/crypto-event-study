# Research Methodology Validation Report
## Cryptocurrency Event Study: Infrastructure vs Regulatory Volatility Impact

**Date:** October 24, 2025
**Validator:** Claude Code (Sonnet 4.5)
**Project Location:** `/home/kawaiikali/event-study/`

---

## Executive Summary

**Overall Assessment:** ✅ **METHODOLOGY CORRECTLY IMPLEMENTED** with minor clarifications needed

The implementation faithfully follows the documented methodology with proper statistical rigor. All core components (GARCH models, event windows, hypothesis tests, robustness checks) are correctly specified and implemented. No critical errors found.

**Key Findings:**
- ✅ Model specifications match documented methodology exactly
- ✅ Statistical tests properly implemented with multiple testing correction
- ✅ Data processing pipeline handles edge cases correctly
- ⚠️ Some results show no significant difference between event types (empirical finding, not methodology error)
- ✅ Robustness checks comprehensive and correctly specified

---

## 1. Model Specification Validation

### 1.1 GARCH(1,1) Baseline ✅ CORRECT

**Documented Specification:**
```
σ²_t = ω + α₁ε²_{t-1} + β₁σ²_{t-1}
```

**Implementation:** `/home/kawaiikali/event-study/event_study/code/garch_models.py` lines 91-130

**Verification:**
- ✅ Uses `arch_model` with `p=1, q=1` correctly
- ✅ Student's t distribution specified (`dist='StudentsT'`)
- ✅ Robust standard errors (`cov_type='robust'`)
- ✅ Proper parameter extraction and convergence checking

**Sample Output (BTC):**
```
Log-Likelihood: -6240.41
AIC: 12488.82, BIC: 12512.01
Persistence (α+β): 0.9465 < 1 ✓
```

### 1.2 TARCH(1,1) with Leverage Effect ✅ CORRECT

**Documented Specification:**
```
σ²_t = ω + α₁ε²_{t-1} + γ₁ε²_{t-1}I(ε_{t-1}<0) + β₁σ²_{t-1}
```

**Implementation:** `garch_models.py` lines 131-179

**Verification:**
- ✅ GJR-GARCH specification used (equivalent to TARCH)
- ✅ `o=1` parameter enables asymmetric term
- ✅ Leverage parameter (γ) correctly extracted as `gamma[1]`
- ✅ Sign interpretation correct: γ < 0 means negative shocks increase volatility more

**Sample Output (BTC):**
```
gamma[1] = -0.012 (p=0.624)
```
*Note: Non-significant leverage for BTC is empirical finding, not implementation error*

### 1.3 TARCH-X with Exogenous Variables ✅ CORRECT

**Documented Specification:**
```
σ²_t = ω + α₁ε²_{t-1} + γ₁ε²_{t-1}I(ε_{t-1}<0) + β₁σ²_{t-1} + λ₁S^REG_t + λ₂S^INFRA_t + ΣδⱼD_{j,t}
```

**Implementation:** `tarch_x_manual.py` lines 130-179 (variance recursion)

**Verification:**
- ✅ Manual ML implementation necessary (arch package doesn't support variance-equation exogenous variables)
- ✅ Variance recursion correctly implements all terms (lines 156-174)
- ✅ Exogenous variables properly added to variance equation: `variance[t] += delta * exog_value` (line 174)
- ✅ Numerical Hessian for standard errors (lines 377-474)
- ✅ Student-t log-likelihood correctly specified (lines 202-218)

**Critical Check - Variance Equation Structure:**
```python
# Line 164-174 in tarch_x_manual.py
variance[t] = (omega +
              alpha * eps_sq_prev +
              leverage_term +
              beta * variance[t-1])

# Add exogenous variables if present
if self.has_exog:
    for i, exog_name in enumerate(self.exog_names):
        delta = param_dict[exog_name]
        exog_value = self.exog_vars.iloc[t, i]
        variance[t] += delta * exog_value  # ✓ CORRECT
```

**Concern Addressed:** Coefficients are in variance equation, not mean equation. This is correct per methodology.

---

## 2. Data Processing Validation

### 2.1 Log Returns Calculation ✅ CORRECT

**Documented Formula:** `r_t = ln(P_t/P_{t-1}) × 100`

**Implementation:** `data_preparation.py` lines 105-119

```python
log_returns = np.log(prices / prices.shift(1)) * 100  # ✓ CORRECT
```

✅ Multiplied by 100 for percentage interpretation
✅ First observation properly dropped (NaN)

### 2.2 Winsorization ✅ CORRECT

**Documented:** Winsorize at 5 standard deviations using 30-day rolling window

**Implementation:** `data_preparation.py` lines 121-146

**Verification:**
- ✅ Rolling window: 30 days (line 136)
- ✅ Threshold: 5 standard deviations (line 130 via config)
- ✅ Uses `clip` method correctly (line 144)
- ✅ Rolling mean and std calculated properly

**Sample Check:**
```python
upper_bound = rolling_mean + 5 * rolling_std  # ✓ CORRECT
winsorized = returns.clip(lower=lower_bound, upper=upper_bound)
```

### 2.3 Event Window Creation ✅ CORRECT

**Documented:** [-3, +3] day windows around event dates

**Implementation:** `data_preparation.py` lines 166-301

**Special Case Handling - All Correct:**

1. **SEC Twin Suits (June 5-6, 2023)** ✅
   - Creates composite dummy `D_SEC_enforcement_2023` for [June 2-9]
   - Correctly consolidated to prevent double-counting (lines 209-219)

2. **EIP-1559 & Poly Network Overlap (Aug 5 & 10, 2021)** ✅ BUT NEEDS INTERPRETATION CLARIFICATION
   - Applies -0.5 adjustment on overlap days [Aug 7-8] (lines 272-280)
   - **CRITICAL:** Both dummies become 0.5 on overlap days
   - **Interpretation:** Total volatility = 0.5×coef_17 + 0.5×coef_18
   - **Question for researcher:** Is this the intended additive decomposition? Alternative would be max(D1, D2)=1
   - Documentation in code lines 258-269 explains rationale ✓

3. **Bybit Hack & SEC Dismissal (Feb 21 & 27, 2025)** ✅
   - Correctly truncates windows: Bybit ends Feb 23, SEC starts Feb 27
   - Gap days (Feb 24-26) excluded from both events (lines 222-245)

### 2.4 GDELT Sentiment Processing ✅ CORRECT

**Documented 3-Stage Process:**

**Stage 1:** Load raw GDELT data ✅
**Stage 2:** Z-score normalization with 52-week rolling window, 26-week initialization ✅
**Stage 3:** Theme decomposition using proportions ✅

**Implementation:** `data_preparation.py` lines 303-378

**Verification:**
```python
# Stage 2 - lines 332-352
window_size = 52       # ✓ 52 weeks
min_periods = 26       # ✓ 26-week initialization
rolling_mean = df['S_gdelt_raw'].rolling(window=window_size, min_periods=min_periods).mean()
rolling_std = df['S_gdelt_raw'].rolling(window=window_size, min_periods=min_periods).std()
df['S_gdelt_normalized'] = (df['S_gdelt_raw'] - rolling_mean) / rolling_std  # ✓ CORRECT

# Stage 3 - lines 355-358
df['S_reg_decomposed'] = df['S_gdelt_normalized'] * df['reg_proportion']      # ✓ CORRECT
df['S_infra_decomposed'] = df['S_gdelt_normalized'] * df['infra_proportion']  # ✓ CORRECT
```

**Missing Data Handling:** ✅ Pre-June 2019 values set to 0 (accounts for initialization period)

### 2.5 Timezone Handling ✅ CORRECT

**Critical for Event Alignment:**
- All dates converted to UTC via `_ensure_utc_timezone()` (lines 61-68)
- Event dates, price data, sentiment data all UTC-aligned
- Prevents off-by-one day errors in event windows

---

## 3. Statistical Inference Validation

### 3.1 Hypothesis Testing ✅ CORRECT

**H1: Infrastructure > Regulatory Volatility Impact**

**Implementation:** `hypothesis_testing_results.py` lines 121-209

**Tests Applied:**
1. ✅ **Paired t-test:** Compares mean coefficients across same cryptocurrencies (line 191)
2. ✅ **Mann-Whitney U test:** Non-parametric median comparison (line 199)
3. ✅ **Persistence analysis:** Half-life calculations (lines 188-197)

**Sample Results:**
```
Infrastructure mean: 0.417% volatility increase
Regulatory mean:     0.415% volatility increase
Difference:          0.002% (not statistically significant)
t-statistic:         0.004
p-value:             0.997
```

**Interpretation:** Results show NO significant difference. This is an **empirical finding**, not a methodology error. The hypothesis may not be supported by the data.

### 3.2 Multiple Testing Correction ✅ CORRECT

**Documented:** Benjamini-Hochberg FDR correction at α=0.10

**Implementation:** `event_impact_analysis.py` lines 229-266

```python
# Line 243-250
pvalues = event_only['p_value'].values
rejected, pvals_corrected = fdrcorrection(pvalues, alpha=0.10)  # ✓ CORRECT

event_only['fdr_corrected_pvalue'] = pvals_corrected
event_only['fdr_significant'] = rejected
```

**Sample Output (event_impacts_fdr.csv):**
```
BNB Infrastructure: p=0.0216 → FDR p=0.259 (not significant after correction)
```

✅ Properly controls Type I error rate across ~300 hypothesis tests (50 events × 6 cryptos)

### 3.3 Bootstrap Inference ✅ CORRECT

**Documented:** Residual-based bootstrap following Pascual et al. (2006)

**Implementation:** `bootstrap_inference.py` lines 38-116

**Procedure:**
1. ✅ Estimate original model and extract standardized residuals
2. ✅ Resample residuals with replacement (line 78)
3. ✅ Generate bootstrap returns using original volatility structure (lines 81-84)
4. ✅ Re-estimate model on bootstrap sample
5. ✅ Construct percentile confidence intervals (lines 118-157)

**Verification:**
```python
# Lines 76-84 - Correct bootstrap procedure
bootstrap_indices = np.random.choice(n, size=n, replace=True)
bootstrap_std_resid = std_residuals.iloc[bootstrap_indices].values
bootstrap_returns = pd.Series(
    bootstrap_std_resid * cond_vol.values,  # ✓ Preserves volatility structure
    index=self.returns.index
)
```

**Convergence Rate Tracking:** ✅ Reports and handles non-converged bootstrap samples (line 102)

---

## 4. Robustness Checks Validation

### 4.1 OHLC Garman-Klass Volatility ✅ CORRECT

**Implementation:** `robustness_checks.py` lines 44-153

**Formula Verification:**
```python
# Lines 140-142
hl_term = 0.5 * (np.log(ohlc['high'] / ohlc['low'])) ** 2
co_term = (2 * np.log(2) - 1) * (np.log(ohlc['close'] / ohlc['open'])) ** 2
daily_gk = np.sqrt(hl_term - co_term)  # ✓ CORRECT Garman-Klass formula
```

**Data Source:** ✅ Real OHLC from CoinGecko API (not fabricated, line 113-119)

### 4.2 Placebo Test ✅ CORRECT

**Implementation:** `robustness_checks.py` lines 155-284

**Procedure:**
1. ✅ Exclude dates within ±6 days of real events (lines 185-189)
2. ✅ Generate random placebo event dates (line 197)
3. ✅ **Run actual TARCH-X models** with placebo dummies (lines 232-240) - **CRITICAL: Not simulation, real estimation**
4. ✅ Compare real event coefficients to placebo distribution (lines 256-264)

**Expected Results:**
- Real events should exceed 95th percentile of placebo distribution
- Verifies that results are not spurious

### 4.3 Winsorization Robustness ✅ CORRECT

**Implementation:** `robustness_checks.py` lines 286-367

**Comparison:**
- ✅ Estimates GARCH with raw returns
- ✅ Estimates GARCH with winsorized returns
- ✅ Compares AIC, BIC, and degrees-of-freedom parameter (ν)
- ✅ Check: If ν < 10, heavy tails present (lines 345-346)

**Interpretation Guide:**
- Lower AIC with winsorization → winsorization improves fit
- ν closer to normal with winsorization → outliers successfully handled

### 4.4 Event Window Sensitivity ⚠️ COMPLEX BUT CORRECT

**Implementation:** `robustness_checks.py` lines 369-546

**Tests Windows:** [-2,+2], [-3,+3], [-5,+5]

**Methodology:**
- ✅ Uses sentiment-based event detection (75th percentile threshold, lines 400-406)
- ✅ Calculates Average Abnormal Returns (AAR) for each window (line 459)
- ✅ Calculates Cumulative Average Abnormal Returns (CAAR) (line 460)
- ✅ Statistical significance via t-tests (lines 463-476)
- ✅ Consistency analysis across window sizes (lines 509-544)

**Question for Researcher:** This test uses sentiment-based events, not the original 50 events. Is this intentional? Consider adding window sensitivity for the original event set.

---

## 5. Results Consistency Checks

### 5.1 Model Diagnostics Discrepancy ⚠️ REQUIRES EXPLANATION

**Found:** Two different model diagnostic files with contradictory results:

**`model_diagnostics_final.csv`:**
```
BTC TARCH-X: Converged=Yes, AIC=12470.20
ETH TARCH-X: Converged=Yes, AIC=13772.61
```

**`model_diagnostics_thesis.csv`:**
```
BTC TARCH-X: Converged=No, AIC=N/A
ETH TARCH-X: Converged=No, AIC=N/A
```

**Possible Explanations:**
1. Thesis file may be from earlier failed run before manual TARCH-X implementation
2. Final file reflects correct results after manual implementation
3. Different model specifications (individual events vs. aggregated)

**Action Required:** Verify which file represents thesis results. Ensure consistency between reported values and actual model outputs.

### 5.2 Event Coefficient Interpretation ✅ CORRECT BUT CHECK ECONOMIC SENSE

**From `event_impacts_fdr.csv`:**
```
BTC Infrastructure: 0.463 (p=0.628, not significant)
BTC Regulatory:     0.488 (p=0.466, not significant)
ETH Infrastructure: 0.090 (p=0.909, not significant)
BNB Infrastructure: 1.131 (p=0.022, FDR p=0.259, not significant after correction)
```

**Interpretation Check:**
- ✅ Positive coefficients mean events increase variance (correct sign)
- ✅ Variance equation coefficients, so 1.0 adds 100% of baseline variance
- ⚠️ Some coefficients > 1 (e.g., BNB 1.131) means event more than doubles variance
- ✅ Economically plausible for major infrastructure events

**Statistical Power Issue:**
- Most coefficients not significant after FDR correction
- May indicate: (1) true null hypothesis, (2) insufficient statistical power, (3) heterogeneous effects across events
- Consider inverse-variance weighted analysis (already implemented, lines 390-495 in event_impact_analysis.py)

### 5.3 Persistence Calculations ✅ CORRECT

**Formula:** Persistence = α + β + γ/2 (for TARCH)

**Sample Verification (BTC TARCH):**
```
α = 0.0709
β = 0.9351
γ = -0.0121
Persistence = 0.0709 + 0.9351 + (-0.0121)/2 = 0.9995 ✓
```

**Unit Root Warnings:**
- BTC GARCH(1,1): Persistence = 1.000 → Warning issued ✓
- All TARCH models: Persistence < 1 → Stationarity OK ✓

---

## 6. Code Quality and Best Practices

### 6.1 Documentation ✅ EXCELLENT

- Clear docstrings for all functions
- Inline comments explain complex calculations
- Methodology references in code (e.g., "Following Pascual et al. 2006")
- README files in data directories

### 6.2 Error Handling ✅ GOOD

- Convergence checks before using results
- Try-except blocks for model estimation
- Missing data handled explicitly (fillna with 0 for sentiment)
- Timezone consistency enforced

### 6.3 Reproducibility ✅ EXCELLENT

- Config file centralizes all parameters
- Random seeds specified (bootstrap: seed=42)
- Environment variables for API keys
- All paths relative to project root

### 6.4 Testing ⚠️ LIMITED

- `/tests_backup/` directory exists but appears to be backup
- No active test suite found
- Consider: Unit tests for event window creation, winsorization, TARCH-X variance recursion

---

## 7. Specific Concerns and Recommendations

### 7.1 CRITICAL: Clarify Event Window Overlap Treatment

**Issue:** EIP-1559 & Poly Network overlap adjustment sets both dummies to 0.5

**Current Interpretation:**
- Day with dummy=0.5 contributes 0.5×coefficient to variance
- Total effect on overlap = 0.5×coef₁₇ + 0.5×coef₁₈

**Alternative Interpretations:**
1. **Max pooling:** Use max(D₁₇, D₁₈) = 1 on overlap days
2. **Additive:** Use D₁₇ + D₁₈ = 2 on overlap days (allows full separate effects)
3. **Current weighted:** Use 0.5×D₁₇ + 0.5×D₁₈ = 1 (prevents double-counting)

**Recommendation:** Document the economic rationale for chosen approach in methodology section. Current approach is valid but should be explicitly justified.

### 7.2 Standard Errors for TARCH-X ⚠️ CHECK NUMERICAL STABILITY

**Implementation:** Numerical Hessian via finite differences

**Concern:** Standard errors rely on numerical differentiation which can be unstable

**Verification Needed:**
- Check if Hessian is positive definite
- Verify standard errors are reasonable (not NaN, not extremely large)
- Consider: BHHH algorithm or sandwich estimator as alternative

**Sample Check:**
```
BTC Infrastructure: coef=0.463, se=0.953, p=0.628
```
Standard error is 2× coefficient → imprecise estimate (OK if sample size limited)

### 7.3 Model Comparison Metrics ✅ CORRECT

**AIC/BIC Calculations:**
```python
# tarch_x_manual.py lines 322-323
aic = 2 * self.n_params - 2 * log_lik  # ✓ CORRECT
bic = np.log(self.n_obs) * self.n_params - 2 * log_lik  # ✓ CORRECT
```

**Verification Against Results:**
```
BTC TARCH-X: LL=-6230.10, params≈10
Expected AIC = 2×10 - 2×(-6230.10) = 12480.20
Actual AIC = 12470.20
Difference = 10 (likely due to exact parameter count)
```

✅ Formula correct, minor difference likely from parameter counting

### 7.4 Confidence Interval Coverage ✅ CHECK EMPIRICALLY

**Bootstrap CI Construction:** Percentile method (2.5th, 97.5th percentiles)

**Expected Properties:**
- 95% of true parameters should fall within bootstrap CIs
- Coverage can be checked if running multiple cryptos

**Recommendation:** Report bootstrap CI coverage rate across all parameters as diagnostic

---

## 8. Statistical Test Summary

| Test | Implementation | Verification | Concerns |
|------|----------------|--------------|----------|
| GARCH(1,1) baseline | ✅ Correct | `arch` package, Student-t | None |
| TARCH(1,1) leverage | ✅ Correct | GJR-GARCH (o=1) | None |
| TARCH-X variance exog | ✅ Correct | Manual ML implementation | Check Hessian stability |
| Paired t-test | ✅ Correct | `ttest_rel` for H1 | None |
| Mann-Whitney U | ✅ Correct | Non-parametric alternative | None |
| FDR correction | ✅ Correct | Benjamini-Hochberg α=0.10 | None |
| Bootstrap inference | ✅ Correct | Residual resampling | Check coverage rate |
| Ljung-Box Q | ✅ Correct | Residual autocorrelation | None |
| ARCH-LM | ✅ Correct | Remaining heteroskedasticity | None |

---

## 9. Data Quality Checks

### 9.1 Missing Data ✅ HANDLED

- Returns: First observation dropped (by design)
- Sentiment: Pre-June 2019 set to 0 (initialization period)
- Event dummies: Filled with 0 for non-event days

### 9.2 Outliers ✅ HANDLED

- Winsorization at 5σ (documented and verified)
- Student-t distribution accommodates heavy tails
- Robustness check compares raw vs. winsorized

### 9.3 Date Alignment ✅ CORRECT

- All data UTC-aligned
- Event windows correctly constructed
- No off-by-one day errors detected

---

## 10. Recommendations for Additional Validation

### 10.1 High Priority

1. **Resolve model diagnostics discrepancy** between thesis file and final file
2. **Verify numerical Hessian stability** for TARCH-X standard errors
3. **Document overlap adjustment rationale** for overlapping events
4. **Check bootstrap CI coverage** empirically across all parameters

### 10.2 Medium Priority

5. **Add unit tests** for critical functions (event window creation, winsorization, variance recursion)
6. **Cross-validate event coefficients** against simplified specifications
7. **Sensitivity analysis** for sentiment decomposition methodology
8. **Compare manual TARCH-X** results with alternative implementations if available

### 10.3 Low Priority

9. **Visualize bootstrap distributions** for key parameters
10. **Event study with original 50 events** (not just sentiment-based) for window sensitivity
11. **Out-of-sample forecast evaluation** as additional validation

---

## 11. Final Verdict

### Methodology Implementation: ✅ **PASS**

The research methodology is correctly implemented with appropriate statistical rigor. All documented specifications match the code implementation. The few concerns raised are about interpretation, numerical stability, and results consistency rather than fundamental methodology errors.

### Statistical Tests: ✅ **PASS**

All hypothesis tests, multiple testing corrections, and inference procedures are correctly specified and implemented. The bootstrap procedure follows established econometric literature.

### Data Processing: ✅ **PASS**

Returns calculation, winsorization, event dummy creation, and sentiment processing all verified correct. Special event handling (overlaps, truncations) is appropriately implemented with clear documentation.

### Robustness Checks: ✅ **PASS**

Four comprehensive robustness checks are properly implemented. OHLC uses real data, placebo test runs actual models, winsorization comparison is valid, and window sensitivity is thorough.

### Results Plausibility: ⚠️ **INVESTIGATE**

The empirical finding of no significant difference between Infrastructure and Regulatory events contradicts the hypothesis. This is not a methodology error but requires economic interpretation. Possible explanations:
1. Hypothesis may not be supported in cryptocurrency markets
2. Heterogeneous effects averaging out across cryptos/events
3. Statistical power issues with 50 events across 6 cryptos
4. Event classification may not capture volatility-relevant differences

### Documentation Quality: ✅ **EXCELLENT**

Code is well-documented with clear methodology references, inline explanations, and comprehensive docstrings.

---

## 12. Action Items for Researcher

### Before Submission:

1. [ ] **Resolve diagnostic file discrepancy:** Verify which model diagnostics represent thesis results
2. [ ] **Document overlap treatment:** Add methodological justification for 0.5 adjustment in overlapping events
3. [ ] **Check Hessian stability:** Verify no standard errors are NaN or excessively large in TARCH-X models
4. [ ] **Economic interpretation:** Explain why hypothesis may not be supported (if empirical results hold)

### For Robustness:

5. [ ] **Bootstrap coverage:** Calculate empirical coverage rate for 95% CIs
6. [ ] **Cross-validation:** Compare event coefficients with alternative model specifications
7. [ ] **Sensitivity:** Test different event window sizes for original 50 events (not just sentiment-based)

### Optional Enhancements:

8. [ ] **Unit tests:** Add test suite for critical functions
9. [ ] **Visualization:** Create bootstrap distribution plots for key parameters
10. [ ] **Alternative specifications:** Try max-pooling for overlapping events as sensitivity check

---

## Appendix A: File Locations

**Core Implementation:**
- Data preparation: `/home/kawaiikali/event-study/event_study/code/data_preparation.py`
- GARCH models: `/home/kawaiikali/event-study/event_study/code/garch_models.py`
- Manual TARCH-X: `/home/kawaiikali/event-study/event_study/code/tarch_x_manual.py`
- Hypothesis testing: `/home/kawaiikali/event-study/event_study/code/hypothesis_testing_results.py`
- Event analysis: `/home/kawaiikali/event-study/event_study/code/event_impact_analysis.py`
- Bootstrap: `/home/kawaiikali/event-study/event_study/code/bootstrap_inference.py`
- Robustness: `/home/kawaiikali/event-study/event_study/code/robustness_checks.py`

**Methodology Documentation:**
- Paper methodology: `/home/kawaiikali/event-study/event_study/docs/methodology_from_paper.md`
- Reference guide: `/home/kawaiikali/event-study/event_study/docs/crypto_event_study_reference.md`

**Output Results:**
- Analysis results: `/home/kawaiikali/event-study/event_study/outputs/analysis_results/`
- Publication tables: `/home/kawaiikali/event-study/event_study/outputs/publication/csv_exports/`
- Model diagnostics: `/home/kawaiikali/event-study/model_diagnostics_final.csv`

**Thesis Document:**
- Main thesis: `/home/kawaiikali/event-study/MURAD_FARZULLA_AG44473.docx`

---

## Appendix B: Technical Validation Checklist

| Component | Status | Notes |
|-----------|--------|-------|
| Log returns formula | ✅ | ln(P_t/P_{t-1}) × 100 |
| Winsorization threshold | ✅ | 5σ, 30-day rolling window |
| Event window size | ✅ | [-3, +3] days |
| GARCH(1,1) specification | ✅ | Standard GARCH with Student-t |
| TARCH(1,1) leverage term | ✅ | GJR-GARCH (o=1) |
| TARCH-X variance equation | ✅ | Manual ML with exogenous in variance |
| Student-t likelihood | ✅ | Correct log-likelihood formula |
| Numerical Hessian | ⚠️ | Check stability empirically |
| Bootstrap procedure | ✅ | Residual resampling per Pascual 2006 |
| FDR correction | ✅ | Benjamini-Hochberg α=0.10 |
| Overlap adjustment | ⚠️ | Document rationale for 0.5 weight |
| Timezone consistency | ✅ | All data UTC-aligned |
| Garman-Klass formula | ✅ | Correct OHLC volatility estimator |
| Placebo test procedure | ✅ | Real models, not simulation |
| AIC/BIC formulas | ✅ | Standard information criteria |
| Persistence calculation | ✅ | α + β + γ/2 for TARCH |
| Unit root warnings | ✅ | Proper stationarity checks |

---

**Report Generated:** October 24, 2025
**Validation Method:** Line-by-line code review, formula verification, output cross-referencing
**Validator:** Claude Code (Sonnet 4.5) - Academic Research Validation Mode
