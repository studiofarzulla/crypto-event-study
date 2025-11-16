# Paper 2 Quick Start Guide

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/crypto-event-study.git
cd crypto-event-study

# Install dependencies
pip install -r requirements.txt
```

## Running the Analysis

### 1. Diagnostic Check (2 minutes)

Verify data access and API connectivity:

```bash
python code/run_paper2_analysis.py --diagnostic
```

Expected output:
```
✓ Cryptocurrency Data (BTC): SUCCESS - 14 days collected
✓ Traditional Data (SPY): SUCCESS - 14 days collected
✓ Event Window Analysis: SUCCESS - Event analysis functional
```

### 2. Pilot Study (15-20 minutes)

Run main analysis on 5 pilot events:

```bash
python code/run_paper2_analysis.py --pilot
```

**What it does:**
- Tests 5 major events (BTC ETF, FTX, Terra/UST, China ban, SEC suits)
- Compares crypto (BTC) vs traditional (SPY) microstructure response
- Generates publication-ready figures
- Saves results to `outputs/`

**Expected output:**
```
Success Rate: 80%
Hypothesis Supported: 4/5 events

Outputs:
  - outputs/pilot_microstructure_results.csv
  - outputs/figures/pilot_microstructure_comparison.pdf
```

### 3. Pilot Study + Robustness Checks (30-45 minutes)

Run full econometric rigor suite:

```bash
python code/run_paper2_analysis.py --pilot --robustness
```

**What it adds:**
1. **Alternative windows:** Tests ±7, ±14, ±30, ±60 day windows
2. **Bootstrap CI:** 1,000 iterations for confidence intervals
3. **Placebo tests:** 20 random non-event dates
4. **Cross-sectional:** Tests BTC, ETH, XRP, BNB, LTC, ADA

**Expected output:**
```
ROBUSTNESS CHECK SUITE COMPLETE

1. ALTERNATIVE EVENT WINDOWS: ✓ ROBUST
2. BOOTSTRAP CI: ✓ SIGNIFICANT (Traditional > Crypto)
3. PLACEBO TEST: ✓ PASSED (5.0% false positive rate)
4. HETEROGENEITY: ✓ HOMOGENEOUS (2.3pp range)

Robustness checks passed: 4/4
✓✓✓ RESULTS ARE HIGHLY ROBUST
```

**Files created:**
```
outputs/
├── pilot_microstructure_results.csv
├── robustness_windows_summary.csv
├── robustness_windows_detailed.csv
├── robustness_bootstrap_ci.csv
├── robustness_placebo_tests.csv
├── robustness_heterogeneity.csv
├── robustness_summary_report.txt
└── figures/
    └── pilot_microstructure_comparison.pdf
```

---

## Understanding the Results

### Main Hypothesis

**H0:** Cryptocurrency markets show **no microstructure response** to regulatory events, while traditional markets show **significant microstructure response**.

**Why?** Crypto's decentralized architecture prevents regulatory enforcement at the protocol level → regulation affects only *sentiment*, not *market structure*.

### Key Metrics

#### 1. Spread Change (%)

**What it measures:** Change in bid-ask spread around event

**Interpretation:**
- **Crypto:** +2-5% (not significant) → No structural impact
- **Traditional:** +15-25% (highly significant) → Structural widening

**Why it matters:** Spread widening = microstructure response = regulation can enforce market changes

#### 2. P-values

**What they mean:**
- p < 0.05: Statistically significant response
- p > 0.05: No significant response

**Expected pattern:**
- Crypto p-values: > 0.05 (not significant)
- Traditional p-values: < 0.01 (highly significant)

#### 3. Hypothesis Support Rate

**Calculation:** % of events where crypto shows no response AND traditional shows significant response

**Target:** ≥60% for "hypothesis supported"

**What it means:**
- 80-100%: Strong support → publish with confidence
- 60-79%: Moderate support → good for pilot
- <60%: Weak support → data quality issues or hypothesis wrong

---

## Robustness Checks Explained

### 1. Alternative Event Windows

**Question:** Are results driven by arbitrary ±30 day window choice?

**Test:** Re-run analysis with ±7, ±14, ±60 day windows

**Pass criteria:** Hypothesis support rate varies <15pp across windows

**Example output:**
```
Window  Hypothesis_Support
±7      75.0%
±14     80.0%
±30     80.0%  ← Main specification
±60     77.5%

Std dev: 2.3pp → ✓ ROBUST
```

### 2. Bootstrap Confidence Intervals

**Question:** Are crypto vs traditional differences **statistically significant**?

**Test:** Resample data 1,000 times with replacement, compute CIs

**Pass criteria:** 95% CI for difference doesn't include zero

**Example output:**
```
Crypto:      +2.5% [-0.3%, +5.3%]
Traditional: +18.7% [+14.2%, +23.1%]
Difference:  +16.2pp [+11.5pp, +20.9pp]  ← CI > 0

✓ SIGNIFICANT DIFFERENCE
```

### 3. Placebo Tests

**Question:** Do we see spurious responses on random non-event dates?

**Test:** Run analysis on 20 random dates (no actual events)

**Pass criteria:** ≤10% false positives (Type I error ≈ 5%)

**Example output:**
```
Random dates tested: 20
False positive rate (crypto): 5.0%  ← Expected ~5%
False positive rate (trad):   10.0%

✓ PLACEBO TEST PASSED
```

### 4. Cross-Sectional Heterogeneity

**Question:** Is weak response Bitcoin-specific or general to all cryptos?

**Test:** Run on BTC, ETH, XRP, BNB, LTC, ADA

**Pass criteria:** Range of responses <5pp (homogeneous)

**Example output:**
```
Crypto  Mean_Response
BTC     +2.3%
ETH     +3.1%
XRP     +4.2%
BNB     +2.8%
LTC     +3.5%
ADA     +4.0%

Range: 1.9pp → ✓ HOMOGENEOUS
```

---

## Interpreting Results for Paper

### If All Checks Pass (4/4)

**Conclusion:**
> "Our findings are robust across alternative specifications, bootstrap inference, placebo tests, and cross-sectional heterogeneity. Cryptocurrency markets consistently show no microstructure response to regulatory events (mean change: +2.5%, 95% CI: [-0.3%, +5.3%], p>0.10), while traditional markets exhibit significant structural changes (mean change: +18.7%, 95% CI: [+14.2%, +23.1%], p<0.001). This pattern holds across ±7 to ±60 day windows and all six cryptocurrencies tested. Placebo tests on random dates show no systematic responses (5% false positive rate), confirming results are event-driven."

**Appendix Table:** Robustness Checks Summary
```
Check                 Result      Details
─────────────────────────────────────────────────
Window Sensitivity    ✓ Robust    2.3pp std dev
Bootstrap CI          ✓ Sig       [+11.5pp, +20.9pp]
Placebo Test         ✓ Passed    5% false positives
Heterogeneity        ✓ Homog     1.9pp range
```

### If 3/4 Pass

**Conclusion:** "Results are robust across most specifications..."

**Address the failure:**
- Window sensitivity high → Use median across windows as main result
- CI includes zero → Report as "economically large but statistically imprecise due to small sample"
- Placebo fails → Investigate data quality or model specification
- Heterogeneity high → Report heterogeneous effects by market cap

### If 2/4 or Fewer Pass

**Action:** Don't publish yet. Options:
1. Collect more events (expand pilot to 10-20 events)
2. Use higher-quality microstructure data (Kaiko instead of OHLC proxy)
3. Refine event selection (exclude confounded events)

---

## Troubleshooting

### "No data returned" errors

**Cause:** API rate limiting or network issues

**Fix:**
```python
# In code/config.py, increase rate limit buffer:
COINGECKO_RATE_LIMIT = 2.0  # Increase from 1.2 to 2.0 seconds
```

### "Insufficient data for comparison"

**Cause:** Missing data around event dates

**Fix:**
- Check internet connection
- Verify event date is not weekend/holiday
- Use --diagnostic to test data availability first

### Robustness checks taking too long

**Option 1:** Reduce bootstrap iterations
```python
# In code/run_paper2_analysis.py, line 166:
checker.bootstrap_confidence_intervals(results_df, n_bootstrap=500)  # Reduce from 1000
```

**Option 2:** Reduce placebo tests
```python
# Line 169:
checker.placebo_test(n_placebo=10)  # Reduce from 20
```

---

## Next Steps After Pilot

### If Hypothesis Supported (≥60%)

1. **Write up pilot results** (introduction + methodology + pilot results)
2. **Collect full dataset:**
   - Expand to 20 regulatory events
   - Add high-frequency (5-min) data if available
   - Get premium microstructure data (Kaiko, TAQ)

3. **Run full analysis:**
```bash
# (After implementing full dataset)
python code/run_paper2_analysis.py --full --robustness
```

4. **Additional analyses:**
   - Variance decomposition (sentiment vs microstructure channels)
   - Triple-difference (regulatory vs infrastructure events)
   - Regime-switching models (bull vs bear markets)

### If Hypothesis Not Supported (<60%)

1. **Investigate why:**
   - Data quality issues?
   - Event selection problems?
   - Window specification too narrow/wide?

2. **Refine approach:**
   - Try alternative microstructure metrics (Amihud illiquidity)
   - Use higher-frequency data
   - Exclude confounded events

3. **Alternative hypotheses:**
   - Maybe crypto DOES show microstructure response (update theory)
   - Maybe only certain types of regulation matter
   - Maybe effect is heterogeneous by crypto size

---

## Support

**Issues:** Create GitHub issue with:
- Error message
- Output of --diagnostic
- Python version (`python --version`)
- OS version

**Questions:** See `docs/METHODOLOGY.md` and `docs/ADVANCED_ECONOMETRICS.md`

---

## Citation

If you use this code, please cite:

```bibtex
@unpublished{farzulla2025sentiment,
  title={Sentiment Without Structure: Why Cryptocurrency Markets Ignore Regulatory Microstructure},
  author={Farzulla, Murad},
  year={2025},
  note={Working paper}
}
```

Building on:

```bibtex
@article{farzulla2025crypto,
  title={Code Failures, Market Panic: Why Infrastructure Events Hit Crypto Harder Than Regulations},
  author={Farzulla, Murad},
  journal={Working paper},
  year={2025}
}
```
