# Pre-Submission Checklist
## Cryptocurrency Event Study Validation

**Last Updated:** October 24, 2025

---

## 🔴 CRITICAL - Must Complete Before Submission

### 1. Resolve Model Diagnostics Discrepancy
**Status:** ⚠️ **REQUIRES IMMEDIATE ATTENTION**

**Issue:**
- `model_diagnostics_thesis.csv` shows "Converged=No" for all models
- `model_diagnostics_final.csv` shows "Converged=Yes" with AIC/BIC values

**Action:**
```bash
# Check which file your thesis references
cd /home/kawaiikali/event-study/
cat model_diagnostics_thesis.csv
cat model_diagnostics_final.csv

# If thesis.csv is outdated from failed run:
mv model_diagnostics_thesis.csv model_diagnostics_OLD_DO_NOT_USE.csv

# Verify final.csv has your reported values
```

**Verification:**
- [ ] Thesis reports AIC/BIC from `model_diagnostics_final.csv`
- [ ] All convergence flags match between thesis and final.csv
- [ ] Outdated files renamed or deleted

---

### 2. Cross-Reference All Reported Values
**Status:** ⏳ **PENDING**

**Tables to Verify:**

#### Table: Model Comparison (Thesis Section 4.1)
- [ ] GARCH(1,1) AIC values match `outputs/publication/csv_exports/model_comparison.csv`
- [ ] TARCH(1,1) AIC values match
- [ ] TARCH-X shows improvement over TARCH
- [ ] Leverage parameters (γ) match individual parameter files

**Check Command:**
```bash
cat outputs/publication/csv_exports/btc_parameters.csv | grep gamma
cat outputs/publication/csv_exports/eth_parameters.csv | grep gamma
cat outputs/publication/csv_exports/model_comparison.csv
```

#### Table: Event Impact Results (Thesis Section 4.2)
- [ ] Infrastructure mean coefficient matches `outputs/analysis_results/hypothesis_test_results.csv`
- [ ] Regulatory mean coefficient matches
- [ ] t-test p-value matches
- [ ] FDR-corrected p-values match `outputs/publication/csv_exports/event_impacts_fdr.csv`

**Check Command:**
```bash
cat outputs/analysis_results/hypothesis_test_results.csv
cat outputs/publication/csv_exports/event_impacts_fdr.csv
```

#### Table: Major Events (Thesis Section 4.3)
- [ ] FTX bankruptcy volatility increase correct
- [ ] Terra/LUNA collapse volatility increase correct
- [ ] BTC ETF approval volatility increase correct

---

### 3. Verify Statistical Significance Reporting
**Status:** ⏳ **PENDING**

**Common Error:** Reporting raw p-values instead of FDR-corrected p-values

**Check:**
- [ ] All event coefficient p-values in thesis are FDR-corrected (from `event_impacts_fdr.csv`)
- [ ] Significance stars (*, **, ***) based on FDR-corrected p-values
- [ ] Footnote states: "P-values adjusted using Benjamini-Hochberg FDR correction at α=0.10"

**Verification Command:**
```bash
# Compare raw vs FDR-corrected for BNB Infrastructure (should be different)
grep "bnb,D_infrastructure" outputs/publication/csv_exports/event_impacts_fdr.csv
# Raw p=0.0216, FDR p=0.259 (not significant after correction)
```

---

## 🟡 IMPORTANT - Recommended Before Submission

### 4. Document Overlap Adjustment Methodology
**Status:** ⏳ **NEEDS TEXT IN METHODOLOGY**

**Issue:** 0.5 adjustment for EIP-1559/Poly Network overlap requires justification

**Add to Thesis (Section 3.2.3 - Overlap Treatment):**

> "For the EIP-1559 and Poly Network overlap (August 7-8, 2021), we apply a weighted adjustment where each event dummy is set to 0.5 on overlapping days. This approach attributes volatility equally to both events, preventing double-counting while preserving individual event identification. The total variance contribution on overlap days is 0.5×δ₁₇ + 0.5×δ₁₈, which maintains a unit contribution while allowing separate coefficient estimation. Alternative approaches (max pooling or full additive) were considered but rejected as they either lose information (max) or artificially inflate variance (additive)."

**Action:**
- [ ] Add justification paragraph to Section 3.2.3
- [ ] Reference implementation in code (data_preparation.py lines 257-280)
- [ ] Mention as robustness check limitation (could test max pooling)

---

### 5. Check Hessian Numerical Stability
**Status:** ⏳ **QUICK CHECK NEEDED**

**What to Look For:**
- NaN standard errors
- Standard errors > 10× coefficient
- Negative or zero standard errors

**Verification Command:**
```bash
# Check all TARCH-X standard errors
for crypto in btc eth xrp bnb ltc ada; do
    echo "=== $crypto TARCH-X ==="
    cat outputs/publication/csv_exports/${crypto}_parameters.csv | grep TARCH-X | grep -v "Const"
done
```

**If You Find Issues:**
- Standard errors look reasonable (0.1 to 2× coefficient) → ✅ OK
- Some standard errors > coefficient → ⚠️ Imprecise but valid (mention in limitations)
- NaN or unreasonable values → 🔴 Re-estimate with tighter tolerances

**Action:**
- [ ] All standard errors are finite (not NaN)
- [ ] All standard errors are reasonable (< 5× coefficient)
- [ ] If issues found, re-run with `options={'ftol': 1e-6}` in TARCH-X estimation

---

### 6. Inverse-Variance Weighted Results
**Status:** ✅ **ALREADY COMPUTED** - Just report it!

**Where to Find:**
```bash
cat outputs/analysis_results/inverse_variance_weighted.csv
```

**Why Important:**
- Accounts for different precision across cryptocurrencies
- Gives more weight to precisely estimated coefficients
- Often used in meta-analysis

**Action:**
- [ ] Report inverse-variance weighted average in results section
- [ ] Compare with simple mean (from hypothesis_test_results.csv)
- [ ] Discuss if results differ substantially

**Example Text:**
> "Using inverse-variance weighting to account for heterogeneous estimation precision across cryptocurrencies, the weighted average effect of Infrastructure events is 0.338 (SE=0.228), compared to 0.340 (SE=0.180) for Regulatory events (z=-0.004, p=0.997). This confirms the simple mean comparison and indicates no statistically significant difference in volatility impact."

---

## 🟢 OPTIONAL - Strengthen Analysis (If Time Permits)

### 7. Bootstrap Confidence Interval Coverage
**Status:** 💡 **OPTIONAL ENHANCEMENT**

**What It Tests:** Do 95% CIs actually contain the true parameter 95% of the time?

**How to Check:**
```python
# Run in Python environment
import pandas as pd

# Load bootstrap results (if saved)
# Count how many CIs contain the original estimate
# Should be ≈95% coverage

# If coverage is <90% or >98%, mention in limitations
```

**Action (if time):**
- [ ] Calculate empirical coverage rate
- [ ] Report in robustness section
- [ ] If coverage poor, mention bootstrap may underestimate uncertainty

---

### 8. Sensitivity Analysis: Max Pooling for Overlaps
**Status:** 💡 **OPTIONAL ROBUSTNESS CHECK**

**What It Tests:** Does overlap treatment affect conclusions?

**Quick Implementation:**
```python
# In data_preparation.py, try alternative:
# Instead of: dummies.loc[date, 'D_event_17'] = 0.5
# Use: dummies.loc[date, 'D_event_17'] = 1  # max pooling

# Re-run TARCH-X for BTC and ETH
# Compare event coefficients
```

**Action (if time):**
- [ ] Re-estimate with max pooling for overlaps
- [ ] Compare coefficients for events 17 and 18
- [ ] Report in robustness section: "Results robust to alternative overlap treatment"

---

### 9. Out-of-Sample Validation
**Status:** 💡 **PUBLICATION-LEVEL ENHANCEMENT**

**What It Tests:** Do models predict future volatility accurately?

**Implementation:**
```python
# Train on 2019-2023, test on 2024-2025
# Compare forecast RMSE: TARCH-X vs TARCH vs GARCH
# Lower RMSE confirms TARCH-X superiority empirically
```

**Action (if time and interest):**
- [ ] Split sample at 2024-01-01
- [ ] Generate out-of-sample forecasts
- [ ] Report forecast accuracy in Table
- [ ] Adds strong support for H3 (TARCH-X superiority)

---

## 📋 Final Pre-Submission Checklist Summary

### Must Do (Before Submission)
- [ ] Resolve model diagnostics discrepancy (thesis vs final file)
- [ ] Cross-reference all AIC/BIC values in thesis with final.csv
- [ ] Verify all p-values are FDR-corrected
- [ ] Check for NaN or unreasonable standard errors

### Should Do (Strengthen Results)
- [ ] Add overlap adjustment justification to methodology
- [ ] Report inverse-variance weighted results
- [ ] Verify bootstrap CIs look reasonable (no NaN bounds)

### Nice to Have (If Time)
- [ ] Sensitivity analysis with max pooling for overlaps
- [ ] Bootstrap coverage rate calculation
- [ ] Out-of-sample forecast evaluation

---

## 🎯 Estimated Time Requirements

| Task | Priority | Time Required |
|------|----------|---------------|
| Resolve diagnostics discrepancy | 🔴 Critical | 30 minutes |
| Cross-reference all tables | 🔴 Critical | 1 hour |
| Verify FDR-corrected p-values | 🔴 Critical | 30 minutes |
| Check Hessian stability | 🟡 Important | 15 minutes |
| Add overlap justification | 🟡 Important | 30 minutes |
| Report inverse-variance weights | 🟡 Important | 15 minutes |
| Sensitivity analysis | 🟢 Optional | 2 hours |
| Bootstrap coverage | 🟢 Optional | 1 hour |
| Out-of-sample validation | 🟢 Optional | 3 hours |

**Minimum time to submission-ready:** ~2.5 hours (critical + important items)
**Full robustness time:** ~9 hours (all items)

---

## 🚀 Quick Start Commands

### Verify Current State
```bash
cd /home/kawaiikali/event-study/

# 1. Check which diagnostic file is current
diff model_diagnostics_thesis.csv model_diagnostics_final.csv

# 2. Verify all output files exist
ls -lh outputs/analysis_results/
ls -lh outputs/publication/csv_exports/

# 3. Quick check for NaN in standard errors
grep -r "nan" outputs/publication/csv_exports/*.csv

# 4. View hypothesis test results
cat outputs/analysis_results/hypothesis_test_results.csv
```

### Generate Missing Files (If Needed)
```bash
cd /home/kawaiikali/event-study/event_study/code/

# Re-run full analysis (if files missing)
python run_event_study_analysis.py

# Re-run hypothesis testing only
python hypothesis_testing_results.py
```

---

## 📞 Questions to Verify with Thesis Supervisor

1. **Non-significant H1 result**: "My hypothesis that Infrastructure > Regulatory is not supported by the data. Should I frame this as 'exploratory' or 'no evidence of difference'?"

2. **Multiple testing correction**: "After FDR correction, most individual events are non-significant. Should I focus on aggregate effects or report individual events with correction?"

3. **Overlap adjustment**: "I used 0.5 weighting for overlapping events. Is this methodologically sound, or should I try max pooling?"

4. **Statistical power**: "With 50 events across 6 cryptocurrencies, power may be limited. Should I discuss this as a limitation?"

---

## ✅ Sign-Off

Once all critical items are complete:

- [ ] All reported values match output CSVs
- [ ] No convergence failures in reported models
- [ ] All p-values are FDR-corrected
- [ ] Standard errors are finite and reasonable
- [ ] Methodology section documents all special cases
- [ ] Limitations section mentions statistical power and overlap treatment

**Final verification:** Re-read thesis Results section while looking at output files side-by-side. Every number should match exactly.

---

**Ready to submit when all 🔴 CRITICAL items are checked ✓**

Good luck with your submission!
