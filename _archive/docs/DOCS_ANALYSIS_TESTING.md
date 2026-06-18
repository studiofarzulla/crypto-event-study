# ANALYSIS & TESTING LAYER DOCUMENTATION
## Cryptocurrency Event Study - Statistical Validation Framework

**Repository:** `/home/kawaiikali/event-study/`
**Date:** October 28, 2025
**Target Journal:** Journal of Banking & Finance

---

## TABLE OF CONTENTS

1. [Overview](#overview)
2. [Module Summary](#module-summary)
3. [Event Impact Analysis](#event-impact-analysis)
4. [Hypothesis Testing](#hypothesis-testing)
5. [Robustness Checks](#robustness-checks)
6. [Bootstrap Inference](#bootstrap-inference)
7. [Analysis Pipeline Flow](#analysis-pipeline-flow)
8. [Output Formats](#output-formats)
9. [Critical Metrics](#critical-metrics)

---

## OVERVIEW

The analysis and testing layer implements comprehensive statistical validation for cryptocurrency event study results. This layer transforms TARCH-X model outputs into publication-ready findings through hypothesis testing, robustness checks, and bootstrap inference.

**Core Purpose:** Validate that Infrastructure events have greater volatility impact than Regulatory events, with statistical rigor sufficient for peer review.

**Key Innovation:** Custom variance-exogenous coefficient extraction for event dummies in TARCH models, with FDR correction for multiple testing.

---

## MODULE SUMMARY

| Module | Purpose | Key Outputs | Lines of Code |
|--------|---------|-------------|---------------|
| `event_impact_analysis.py` | Event coefficient extraction, FDR correction, hypothesis testing | Event coefficients, p-values, publication tables | 978 |
| `hypothesis_testing_results.py` | Comprehensive H1/H2/H3 testing framework | Hypothesis test results, verification diagnostics | 442 |
| `robustness_checks.py` | Four robustness validations (OHLC, placebo, winsorization, windows) | Robustness validation results, visualizations | 759 |
| `robustness_alternative_windows.py` | Event window sensitivity analysis (±1, ±3, ±5, ±7 days) | Window comparison results, ranking stability | 667 |
| `robustness_placebo_outlier.py` | Placebo test (1,000 random dates), outlier sensitivity | Placebo distributions, outlier-robust estimates | 759 |
| `bootstrap_inference.py` | Residual-based bootstrap for TARCH models | 95% confidence intervals, convergence rates | 368 |
| `bootstrap_inference_optimized.py` | Parallelized bootstrap with joblib | Optimized CI estimation, 5-10x speedup | 489 |

**Total:** 4,462 lines of statistical validation code

---

## EVENT IMPACT ANALYSIS

**File:** `code/event_impact_analysis.py`

### Purpose

Extracts event coefficients from TARCH-X variance equations and performs statistical tests for Infrastructure vs Regulatory hypothesis.

### Core Class: `EventImpactAnalysis`

```python
EventImpactAnalysis(model_results: Dict[str, Dict[str, ModelResults]])
```

**Initialization:**
- Takes nested dictionary: `{crypto: {model_name: ModelResults}}`
- Automatically extracts all event coefficients from TARCH-X models
- Classifies event types: Infrastructure, Regulatory, Sentiment

### Key Methods

#### 1. Event Coefficient Extraction

```python
_extract_all_event_coefficients() -> pd.DataFrame
```

**What it does:**
- Iterates through all TARCH-X models
- Extracts variance-exogenous coefficients (`event_effects` attribute)
- Maps event variables to types:
  - `D_infrastructure` → Infrastructure
  - `D_regulatory` → Regulatory
  - `S_*`, `*_normalized`, `*_decomposed` → Sentiment
- Retrieves standard errors and p-values from specialized attributes

**Output columns:**
- `crypto`: Cryptocurrency symbol
- `event_variable`: Event dummy name (e.g., `D_infrastructure`)
- `coefficient`: Variance impact coefficient
- `std_error`: Standard error
- `p_value`: Statistical significance
- `event_type`: Infrastructure, Regulatory, or Sentiment

#### 2. Infrastructure vs Regulatory Test

```python
test_infrastructure_vs_regulatory() -> Dict
```

**Hypothesis:**
- **H0:** Infrastructure = Regulatory (no difference)
- **H1:** Infrastructure > Regulatory (Infrastructure has larger impact)

**Statistical Tests:**
1. **Paired t-test** - Tests difference in means across same cryptocurrencies
2. **Mann-Whitney U test** - Non-parametric test for distributions
3. **Cohen's d** - Effect size measure (pooled standard deviation)

**Effect Size Interpretation:**
- d < 0.2: Negligible
- 0.2 ≤ d < 0.5: Small
- 0.5 ≤ d < 0.8: Medium
- d ≥ 0.8: Large

**Returns:**
```python
{
    'infrastructure': {'n': int, 'mean': float, 'median': float, 'std': float},
    'regulatory': {'n': int, 'mean': float, 'median': float, 'std': float},
    't_test': {'statistic': float, 'p_value': float, 'test_type': str},
    'mann_whitney': {'statistic': float, 'p_value': float},
    'effect_size': float  # Cohen's d
}
```

#### 3. FDR Correction

```python
apply_fdr_correction() -> pd.DataFrame
```

**Purpose:** Control False Discovery Rate in multiple testing (50 events × 6 cryptos = 300 tests)

**Method:** Benjamini-Hochberg procedure at α = 0.10

**What it does:**
- Takes all event p-values
- Applies FDR correction
- Flags significant results after correction
- Reports how many false discoveries were controlled

**Output:** Original DataFrame plus:
- `fdr_corrected_pvalue`: Adjusted p-value
- `fdr_significant`: Boolean flag

#### 4. Inverse-Variance Weighted Averages

```python
calculate_inverse_variance_weighted_average() -> Dict
```

**Why:** Gives more weight to precisely estimated coefficients (low standard error)

**Formula:**
```
weight_i = 1 / SE_i²
weighted_avg = Σ(coef_i × weight_i) / Σ(weight_i)
SE_weighted = sqrt(1 / Σ(weight_i))
```

**Returns:**
- Weighted average effect for Infrastructure events
- Weighted average effect for Regulatory events
- Z-test for difference
- 95% confidence intervals

#### 5. Persistence Measures

```python
calculate_persistence_measures() -> Dict
```

**Volatility persistence:** How long shocks persist

**Formula:**
- GARCH: `α + β`
- TARCH: `α + β + γ/2`

**Half-life:** Days for shock to decay to 50%
```
half_life = -log(0.5) / log(persistence)
```

**Interpretation:**
- persistence < 1: Stationary (mean-reverting)
- persistence ≥ 1: Non-stationary (shocks persist indefinitely)

#### 6. Major Events Volatility Analysis

```python
analyze_major_events_volatility(crypto_data: Dict, events_df: pd.DataFrame) -> Dict
```

**Analyzes 6 major events:**
1. FTX Bankruptcy (2022-11-11) - Infrastructure
2. Terra/UST Collapse (2022-05-09) - Infrastructure
3. BTC ETF Approval (2024-01-10) - Regulatory
4. China Ban (2021-09-24) - Regulatory
5. QuadrigaCX Collapse (2019-02-15) - Infrastructure
6. FATF Crypto Rules (2019-06-21) - Regulatory

**For each event, calculates:**
- Pre-event volatility (30 days before, excluding 5 days before event)
- Event window volatility (±2 days around event)
- Post-event volatility (5-15 days after)
- Percentage increase
- Persistence metric

**Aggregates by event type** to test H1 empirically

---

## HYPOTHESIS TESTING

**File:** `code/hypothesis_testing_results.py`

### Purpose

Comprehensive testing framework for three main hypotheses:
- **H1:** Infrastructure > Regulatory volatility impact
- **H2:** Sentiment as leading indicator (different patterns by event type)
- **H3:** TARCH-X outperforms GARCH/TARCH

### Core Class: `HypothesisTestingResults`

```python
HypothesisTestingResults()
```

**What it does:**
- Loads all cryptocurrency data
- Estimates GARCH(1,1), TARCH(1,1), TARCH-X for each crypto
- Runs all hypothesis tests
- Verifies fixes with FTX diagnostic

### Test Flow

```
load_all_crypto_data()
    ↓
estimate_all_models()
    ↓
┌───────────────┼───────────────┐
│               │               │
test_hypothesis_1()  test_hypothesis_2()  test_hypothesis_3()
    ↓               ↓               ↓
Infrastructure   Sentiment     Model
vs Regulatory    Leading       Superiority
                 Indicator     (AIC/BIC)
    ↓               ↓               ↓
verify_ftx_event()
```

### Hypothesis 1: Infrastructure > Regulatory

**Three-pronged approach:**

1. **Coefficient Comparison**
   - Extract Infrastructure and Regulatory coefficients from TARCH-X
   - Convert to percentage volatility impact (multiply by 100)
   - Paired t-test for mean difference

2. **Major Events Empirical Analysis**
   - Calculate actual volatility increases for 6 major events
   - Compare Infrastructure vs Regulatory event averages
   - Show concrete examples (FTX: +150%, ETF: +50%)

3. **Persistence Analysis**
   - Calculate half-life separately for Infrastructure vs Regulatory events
   - Test if Infrastructure events have longer-lasting impacts

**Expected Result:**
- Infrastructure mean > Regulatory mean
- Positive Cohen's d
- Significant t-test (p < 0.05)

### Hypothesis 2: Sentiment Leading Indicator

**Tests whether:**
- Infrastructure events: Contemporaneous (lag = 0)
- Regulatory events: Sentiment leads volatility (lag < 0)

**Method:**
- Cross-correlations at lags -4 to +4 weeks
- Granger causality tests (up to 4 lags)
- Find optimal lag by maximum absolute correlation

**Support criteria:**
- Infrastructure: |optimal_lag| ≤ 1 (contemporaneous)
- Regulatory: optimal_lag < 0 (sentiment leads)

### Hypothesis 3: TARCH-X Superiority

**Comparison:**
- GARCH(1,1): Baseline
- TARCH(1,1): Leverage effect
- TARCH-X: Leverage + event dummies

**Metrics:**
- AIC (Akaike Information Criterion) - lower is better
- BIC (Bayesian Information Criterion) - lower is better
- AIC improvement = TARCH(1,1) AIC - TARCH-X AIC

**Win rate:** Percentage of cryptos where TARCH-X beats TARCH

### FTX Verification

**Purpose:** Verify control window fix produces positive coefficients

**Method:**
- Get FTX event date (2022-11-11)
- Calculate baseline volatility (60-30 days before)
- Calculate event volatility (±2 days)
- Check: event_vol > baseline_vol → positive coefficient

**Success criteria:** All cryptos show positive coefficients

---

## ROBUSTNESS CHECKS

### 1. Main Robustness Framework

**File:** `code/robustness_checks.py`

Implements four robustness validations:

#### Check 1: OHLC Volatility

```python
check_ohlc_volatility(cryptos: List[str]) -> Dict
```

**Purpose:** Compare close-to-close returns with OHLC-based volatility

**Method:**
- Fetch OHLC data from CoinGecko API
- Calculate Garman-Klass volatility estimator:
  ```
  GK = sqrt(0.5*(log(H/L))² - (2*log(2)-1)*(log(C/O))²)
  ```
- Correlate with traditional volatility from returns

**Expected:** High correlation (ρ > 0.80) validates returns-based approach

#### Check 2: Placebo Test

```python
run_placebo_test(n_placebos: int = 1000) -> Dict
```

**Purpose:** Show heterogeneity is event-driven, not spurious

**Method:**
1. Generate 1,000 random event dates (avoiding real events ±6 days)
2. Create event dummies for each placebo date
3. Run TARCH-X with placebo events
4. Extract placebo coefficients
5. Calculate 95th percentile of placebo distribution
6. Test if real coefficients exceed placebo threshold

**Expected:** Real event coefficients >> 95th percentile of placebo

**Implementation details:**
- Uses 5-day event window (±2 days, matching real events)
- Block bootstrap with 10-day blocks
- 20 placebo tests (limited for speed, full analysis: 1,000)

#### Check 3: Winsorization Robustness

```python
check_winsorization_robustness(cryptos: List[str]) -> Dict
```

**Purpose:** Compare raw vs winsorized returns

**Method:**
- Estimate GARCH with raw returns
- Estimate GARCH with winsorized returns (99th/1st percentile)
- Compare AIC, BIC, parameter stability

**Expected:** Winsorized models have lower AIC (better fit)

**Why winsorization:**
- Cryptocurrency returns have extreme outliers
- Student-t distribution helps but may not be sufficient
- Winsorization = cap extreme values at 99th/1st percentile

#### Check 4: Event Window Sensitivity

```python
check_event_window_sensitivity(windows: List[int] = [2, 3, 5]) -> Dict
```

**Purpose:** Test robustness to event window length

**Windows:**
- Narrow: [-2, +2] (5 days)
- Base: [-3, +3] (7 days, current choice)
- Wide: [-5, +5] (11 days)

**For each window:**
- Calculate Average Abnormal Returns (AAR)
- Calculate Cumulative AAR (CAAR)
- Test statistical significance (t-test at each day)
- Compare consistency across windows

**Expected:** Results stable across windows (94% sign stability)

### 2. Alternative Windows Analysis

**File:** `code/robustness_alternative_windows.py`

**Purpose:** Comprehensive sensitivity analysis for event windows

**Windows tested:**
- Narrow: [-1, +1] (3 days)
- Base: [-3, +3] (7 days)
- Moderate: [-5, +5] (11 days)
- Wide: [-7, +7] (15 days)

**Metrics calculated:**
1. **Heterogeneity Ratio:** BNB effect / LTC effect
2. **Cohen's d:** Effect size between BNB and LTC
3. **Kruskal-Wallis H:** Non-parametric heterogeneity test
4. **Rankings:** Crypto ordering by mean effect

**Stability measures:**
- Sign stability: % of coefficients maintaining same sign
- Ranking stability: Spearman rank correlation vs base window
- Effect size consistency: Cohen's d range across windows

**Expected from research:**
- 94% sign stability across windows
- Spearman ρ > 0.95 for rankings
- Cohen's d remains "huge" (d > 1.2) in all windows

**Visualizations:**
1. Heterogeneity ratio across windows (line plot)
2. Cohen's d across windows (line plot with thresholds)
3. Rankings heatmap (all windows)
4. Effect sizes with 95% CI (4-panel, one per window)

### 3. Placebo Test & Outlier Sensitivity

**File:** `code/robustness_placebo_outlier.py`

**Purpose:** Publication-ready robustness for peer review

#### Part 1: Placebo Test (1,000 iterations)

**Method:**
1. Generate 1,000 sets of random dates (same n as real events)
2. For each placebo sample:
   - Randomly shuffle observed coefficients across cryptos
   - Calculate Kruskal-Wallis H, Cohen's d, range, ratio
3. Compare observed statistics to placebo distribution

**Metrics tested:**
- **Kruskal-Wallis H:** Overall heterogeneity test
- **Range:** max_effect - min_effect
- **Cohen's d:** (mean_high - mean_low) / pooled_std
- **Ratio:** max_effect / |min_effect|

**For each metric:**
- Percentile of observed in placebo distribution
- P-value: P(placebo ≥ observed)
- Fold difference: observed / placebo_mean

**Expected:**
- All metrics exceed 95th percentile
- P-values < 0.05
- Real events produce 5-10x higher heterogeneity

#### Part 2: Outlier Sensitivity

**Purpose:** Show heterogeneity persists without extreme events

**Method:**
- Winsorize coefficients at 90th percentile (cap extreme values)
- Recalculate all heterogeneity metrics
- Compare baseline vs robust estimates

**Expected:**
- Cohen's d drops from ~5.19 to ~3.5-4.0
- Still in "huge" effect size range (d > 1.2)
- Rankings remain stable (BNB #1, LTC #6)

**Interpretation:**
- Magnitude decreases but pattern persists
- Not driven solely by FTX/Terra outliers
- Core finding is robust

---

## BOOTSTRAP INFERENCE

### 1. Standard Bootstrap

**File:** `code/bootstrap_inference.py`

**Purpose:** Residual-based bootstrap for TARCH confidence intervals

**Method:** Following Pascual et al. (2006)

**Algorithm:**
1. Estimate original TARCH model
2. Extract standardized residuals and conditional volatility
3. For each bootstrap replication:
   - Resample standardized residuals with replacement
   - Generate bootstrap returns: `bootstrap_returns = residuals × volatility`
   - Re-estimate TARCH model
   - Store parameters if converged
4. Calculate percentile confidence intervals (2.5th, 97.5th)

**Key Parameters:**
- `n_bootstrap`: Number of replications (default: 500)
- `seed`: Random seed for reproducibility (default: 42)
- `model_type`: 'GARCH' or 'TARCH'

**Returns:**
```python
{
    'original_params': Dict[str, float],
    'bootstrap_params': List[Dict[str, float]],
    'confidence_intervals': Dict[str, Dict],
    'bootstrap_stats': Dict[str, Dict],
    'convergence_rate': float
}
```

**Confidence intervals include:**
- `ci_lower`: 2.5th percentile
- `ci_upper`: 97.5th percentile
- `ci_width`: Upper - Lower
- `bootstrap_mean`: Mean across replications
- `bootstrap_std`: Standard deviation

**Additional statistics:**
- Persistence: α + β + γ/2 (for TARCH)
- Skewness and kurtosis of parameter distributions
- Min/max parameter values across replications

### 2. Optimized Bootstrap

**File:** `code/bootstrap_inference_optimized.py`

**Performance improvements:**
1. **Parallelization:** Uses `joblib` for parallel execution
2. **Vectorization:** Block bootstrap with NumPy operations
3. **Memory efficiency:** Stores only converged results
4. **Type hints:** Full type safety for better optimization

**Speedup:** 5-10x faster than standard version (500 replications in ~2 minutes)

**Additional features:**
- `n_jobs`: Number of parallel workers (-1 = all cores)
- Progress bars with `tqdm`
- Logging with standard `logging` module
- Thread-local random seeds for reproducibility

**Usage:**
```python
bootstrap = BootstrapInference(returns, n_bootstrap=500, n_jobs=-1)
results = bootstrap.residual_bootstrap_tarch(model_type='TARCH')
table = bootstrap.create_bootstrap_table(results)
```

### Event Coefficient Bootstrap

**Method:** Block bootstrap preserving event structure

```python
bootstrap_event_coefficients_optimized(
    data_with_events: pd.DataFrame,
    event_columns: List[str],
    n_bootstrap: int = 100,
    block_size: int = 10
) -> Dict
```

**Algorithm:**
1. Fit baseline TARCH-X model
2. For each bootstrap replication:
   - Create block bootstrap sample (10-day blocks)
   - Preserve event dummy structure
   - Re-estimate TARCH-X
   - Extract event coefficients
3. Calculate 95% CI for each event coefficient

**Why block bootstrap:**
- Preserves temporal dependence
- Maintains event window structure
- More conservative than iid resampling

**Returns:** Confidence intervals for D_infrastructure, D_regulatory

---

## ANALYSIS PIPELINE FLOW

```
┌─────────────────────────────────────────────────────────────┐
│                     DATA LAYER                              │
│  • Price data (BTC, ETH, XRP, BNB, LTC, ADA)               │
│  • Event data (50 events, Infrastructure/Regulatory)        │
│  • Sentiment data (GDELT weekly aggregates)                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   MODELING LAYER                            │
│  • GARCH(1,1): Baseline model                              │
│  • TARCH(1,1): Leverage effect                             │
│  • TARCH-X: Leverage + event dummies                       │
│                                                             │
│  Output: ModelResults objects with:                        │
│    - parameters, std_errors, pvalues                       │
│    - event_effects (variance-exogenous coefficients)       │
│    - volatility series, AIC, BIC                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              EVENT IMPACT ANALYSIS                          │
│  EventImpactAnalysis(model_results)                         │
│                                                             │
│  1. Extract event coefficients from all TARCH-X models      │
│  2. Classify by type: Infrastructure, Regulatory, Sentiment │
│  3. Apply FDR correction for multiple testing               │
│  4. Calculate inverse-variance weighted averages            │
│                                                             │
│  Output:                                                    │
│    • event_coefficients: DataFrame with all coefficients    │
│    • fdr_corrected_pvalues: Adjusted significance           │
│    • by_crypto: Summary statistics per cryptocurrency       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              HYPOTHESIS TESTING                             │
│  HypothesisTestingResults.run_all_tests()                   │
│                                                             │
│  H1: Infrastructure > Regulatory                            │
│    • Paired t-test (same cryptos)                          │
│    • Mann-Whitney U (distributions)                        │
│    • Cohen's d (effect size)                               │
│    • Major events analysis (empirical validation)          │
│    • Persistence comparison (half-life)                    │
│                                                             │
│  H2: Sentiment Leading Indicator                            │
│    • Cross-correlations (-4 to +4 weeks)                   │
│    • Granger causality tests                               │
│    • Optimal lag detection                                 │
│                                                             │
│  H3: TARCH-X Superiority                                    │
│    • AIC comparison (TARCH vs TARCH-X)                     │
│    • BIC comparison                                        │
│    • Win rate calculation                                  │
│                                                             │
│  FTX Verification:                                          │
│    • Baseline vs event volatility                          │
│    • Coefficient sign check                                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              ROBUSTNESS CHECKS                              │
│  RobustnessChecks.run_all_robustness_checks()               │
│                                                             │
│  Check 1: OHLC Volatility                                   │
│    • Fetch OHLC from CoinGecko                             │
│    • Calculate Garman-Klass estimator                      │
│    • Correlate with returns-based volatility               │
│                                                             │
│  Check 2: Placebo Test                                      │
│    • Generate 1,000 random event dates                     │
│    • Run TARCH-X with placebo events                       │
│    • Compare real vs placebo distributions                 │
│    • Calculate percentiles and p-values                    │
│                                                             │
│  Check 3: Winsorization                                     │
│    • Estimate with raw returns                             │
│    • Estimate with winsorized returns                      │
│    • Compare AIC, parameter stability                      │
│                                                             │
│  Check 4: Event Window Sensitivity                          │
│    • Test windows: [-1,+1], [-3,+3], [-5,+5], [-7,+7]     │
│    • Calculate AAR, CAAR for each window                   │
│    • Test sign stability (expected: 94%)                   │
│    • Calculate ranking stability (Spearman ρ)              │
│                                                             │
│  Outlier Sensitivity:                                       │
│    • Winsorize at 90th percentile                          │
│    • Recalculate heterogeneity metrics                     │
│    • Compare baseline vs robust                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              BOOTSTRAP INFERENCE                            │
│  BootstrapInference(returns, n_bootstrap=500)               │
│                                                             │
│  Standard Bootstrap:                                        │
│    • Resample standardized residuals                       │
│    • Re-estimate TARCH models                              │
│    • Calculate percentile confidence intervals             │
│    • Convergence rate tracking                             │
│                                                             │
│  Optimized Bootstrap:                                       │
│    • Parallel execution (joblib)                           │
│    • Vectorized block bootstrap                            │
│    • 5-10x speedup over standard                           │
│                                                             │
│  Event Coefficient Bootstrap:                               │
│    • Block bootstrap (10-day blocks)                       │
│    • Preserve event structure                              │
│    • 95% CI for event coefficients                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              OUTPUT & VISUALIZATION                         │
│                                                             │
│  Publication Tables:                                        │
│    • event_impacts_fdr.csv - Event coefficients with FDR   │
│    • hypothesis_test_results.csv - H1/H2/H3 statistics     │
│    • robustness_summary.csv - All robustness checks        │
│    • bootstrap_confidence_intervals.csv - CI estimates     │
│                                                             │
│  Figures:                                                   │
│    • placebo_test_robustness.png - 4-panel placebo         │
│    • window_sensitivity.png - AAR/CAAR by window           │
│    • heterogeneity_by_window.png - Stability across windows│
│    • bootstrap_distributions.png - Parameter distributions │
│                                                             │
│  Markdown Reports:                                          │
│    • ROBUSTNESS_PLACEBO_OUTLIER.md                         │
│    • ROBUSTNESS_ALTERNATIVE_WINDOWS.md                     │
│    • HYPOTHESIS_TESTING_SUMMARY.md                         │
└─────────────────────────────────────────────────────────────┘
```

---

## OUTPUT FORMATS

### Event Coefficients DataFrame

**File:** Event impact analysis output

**Columns:**
```python
{
    'crypto': str,                    # Cryptocurrency symbol (btc, eth, etc.)
    'event_variable': str,            # Event dummy name (D_infrastructure, D_regulatory)
    'coefficient': float,             # Variance impact coefficient
    'std_error': float,               # Standard error
    'p_value': float,                 # Raw p-value
    'event_type': str,                # Infrastructure, Regulatory, Sentiment
    'fdr_corrected_pvalue': float,    # FDR-adjusted p-value
    'fdr_significant': bool           # Significant after FDR correction
}
```

**Example rows:**
```
crypto  event_variable      coefficient  std_error  p_value   event_type      fdr_significant
btc     D_infrastructure    0.004753     0.001234   0.0001    Infrastructure  True
btc     D_regulatory        0.002104     0.000987   0.0330    Regulatory      False
eth     D_infrastructure    0.000920     0.000456   0.0440    Infrastructure  False
```

### Hypothesis Test Results

**Format:** Dictionary

```python
{
    'h1_results': {
        'coefficient_comparison': {
            'infrastructure_mean': float,      # Mean Infrastructure effect (%)
            'regulatory_mean': float,          # Mean Regulatory effect (%)
            'p_value': float                   # T-test p-value
        },
        'major_events': {
            'major_events': Dict[int, Dict],   # Event-specific analysis
            'infrastructure_stats': Dict,      # Aggregate Infrastructure stats
            'regulatory_stats': Dict,          # Aggregate Regulatory stats
            'h1_evidence': Dict                # H1 support metrics
        },
        'persistence': {
            'persistence_by_type': Dict,       # Half-life by event type
            'h1_test_results': List[Dict],     # Per-crypto H1 tests
            'h1_support_rate': float           # % of cryptos supporting H1
        }
    },
    'h2_results': Dict,                        # Sentiment leading indicator tests
    'h3_results': {
        'model_comparison': List[Dict],        # AIC/BIC comparison
        'win_rate': float,                     # TARCH-X win rate
        'mean_aic_improvement': float          # Average AIC improvement
    },
    'ftx_verification': Dict[str, Dict]        # FTX diagnostic results
}
```

### Robustness Check Results

**Format:** Nested dictionary

```python
{
    'ohlc_volatility': {
        'btc': {
            'gk_volatility_mean': float,
            'returns_volatility_mean': float,
            'correlation': float
        },
        # ... other cryptos
    },
    'placebo_test': {
        'n_placebos': int,
        'placebo_mean': float,
        'placebo_95th_percentile': float,
        'infrastructure_exceeds_95pct': bool,
        'regulatory_exceeds_95pct': bool
    },
    'winsorization': {
        'btc': {
            'aic_raw': float,
            'aic_winsorized': float,
            'aic_improvement': float
        },
        # ... other cryptos
    },
    'event_window': {
        'regulatory': {
            2: {'results_df': DataFrame, 'n_events': int},  # [-2,+2] window
            3: {'results_df': DataFrame, 'n_events': int},  # [-3,+3] window
            5: {'results_df': DataFrame, 'n_events': int}   # [-5,+5] window
        },
        'infrastructure': {...}
    }
}
```

### Bootstrap Results

**Format:** Dictionary

```python
{
    'original_params': {
        'omega': float,
        'alpha[1]': float,
        'beta[1]': float,
        'gamma[1]': float,    # TARCH asymmetry
        'nu': float           # Student-t degrees of freedom
    },
    'bootstrap_params': List[Dict],  # List of parameter dictionaries
    'confidence_intervals': {
        'omega': {
            'original': float,
            'ci_lower': float,
            'ci_upper': float,
            'ci_width': float,
            'bootstrap_mean': float,
            'bootstrap_std': float
        },
        # ... other parameters
    },
    'bootstrap_stats': {
        'persistence': {
            'mean': float,
            'median': float,
            'ci_lower': float,
            'ci_upper': float
        }
    },
    'convergence_rate': float  # Fraction of successful replications
}
```

---

## CRITICAL METRICS

### Primary Hypothesis Testing Metrics

| Metric | Purpose | Threshold | Interpretation |
|--------|---------|-----------|----------------|
| **Cohen's d** | Effect size (BNB vs LTC) | d > 0.8 = "Large" | Quantifies heterogeneity magnitude |
| **Kruskal-Wallis H** | Non-parametric heterogeneity test | p < 0.05 | Tests if all cryptos respond identically |
| **Paired t-test** | Infrastructure vs Regulatory | p < 0.05 | Tests mean difference |
| **Mann-Whitney U** | Distribution difference | p < 0.05 | Non-parametric test |
| **FDR q-value** | Multiple testing correction | q < 0.10 | Controls false discovery rate |

### Robustness Metrics

| Check | Metric | Pass Criteria | What It Validates |
|-------|--------|---------------|-------------------|
| **OHLC Volatility** | Correlation | ρ > 0.80 | Returns-based volatility is accurate |
| **Placebo Test** | Percentile of observed | > 95th | Heterogeneity is event-driven |
| **Winsorization** | AIC improvement | Negative = better | Outliers don't drive results |
| **Window Sensitivity** | Sign stability | > 90% | Robust to window choice |
| **Window Sensitivity** | Spearman ρ | > 0.90 | Rankings stable across windows |

### Bootstrap Metrics

| Metric | Purpose | Acceptable Range |
|--------|---------|------------------|
| **Convergence Rate** | Bootstrap reliability | > 80% |
| **CI Width** | Precision of estimate | Narrower = more precise |
| **Persistence CI** | Stationarity check | Upper bound < 1.0 for stationarity |

### Model Comparison Metrics

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| **AIC** | -2*log(L) + 2*k | Lower is better; penalizes parameters |
| **BIC** | -2*log(L) + k*log(n) | Lower is better; stronger penalty |
| **Win Rate** | % cryptos where TARCH-X wins | > 50% = TARCH-X superior |
| **AIC Improvement** | AIC_TARCH - AIC_TARCHX | > 0 = TARCH-X better |

### Event Impact Metrics

| Metric | Definition | Typical Range |
|--------|------------|---------------|
| **Variance Coefficient** | Linear impact on σ² | 0.0001 to 0.01 |
| **Percentage Impact** | Coefficient × 100% | 0.01% to 1.00% |
| **Half-life (days)** | -log(0.5) / log(persistence) | 1 to 30 days |
| **Heterogeneity Ratio** | max_effect / |min_effect| | 10x to 50x |

---

## KEY INSIGHTS

### 1. FDR Correction is Critical

**Why:** 50 events × 6 cryptos = 300 statistical tests

**Without correction:** ~15 false positives expected at α = 0.05

**With Benjamini-Hochberg FDR at α = 0.10:**
- Controls expected proportion of false discoveries
- More appropriate than Bonferroni (too conservative)
- Balances Type I and Type II errors

### 2. Inverse-Variance Weighting Matters

**Problem:** Some coefficients estimated with high precision, others with high uncertainty

**Solution:** Weight by inverse of variance (1/SE²)

**Effect:**
- Precise estimates get more weight
- Noisy estimates downweighted
- Overall estimate more reliable

### 3. Bootstrap Convergence Challenges

**Issue:** TARCH models sometimes fail to converge in bootstrap samples

**Typical convergence rate:** 70-90%

**Solutions:**
- Increase max iterations (default: 500)
- Use good starting values from original model
- Parallel execution to run more replications
- Accept 80%+ convergence as sufficient

### 4. Event Window Choice

**Trade-offs:**

**Narrow (±1 day):**
- Pros: Reduces noise, isolates event
- Cons: May miss delayed reactions

**Wide (±7 days):**
- Pros: Captures full impact, including delayed responses
- Cons: Higher risk of confounding events

**Optimal:** Base window (±3 days) balances both concerns

**Validation:** Test multiple windows and show sign stability > 90%

### 5. Placebo Test Design

**Key decision:** How to generate placebo dates?

**Approach:**
1. Use study date range (2019-2025)
2. Exclude ±6 days around real events (avoid contamination)
3. Sample uniformly from remaining dates
4. Match sample size (50 events)

**Why shuffle coefficients:**
- Preserves marginal distributions
- Breaks event-crypto relationship
- Tests null hypothesis of "no event-specific effect"

---

## USAGE EXAMPLES

### Example 1: Complete Analysis

```python
from hypothesis_testing_results import HypothesisTestingResults

# Initialize and run all tests
tester = HypothesisTestingResults()
results = tester.run_all_tests()

# Access specific results
h1 = results['h1_results']
print(f"Infrastructure mean: {h1['coefficient_comparison']['infrastructure_mean']:.4f}")
print(f"Regulatory mean: {h1['coefficient_comparison']['regulatory_mean']:.4f}")
print(f"P-value: {h1['coefficient_comparison']['p_value']:.4f}")
```

### Example 2: Event Impact Analysis Only

```python
from event_impact_analysis import EventImpactAnalysis

# Assuming you have model_results from GARCH estimation
analyzer = EventImpactAnalysis(model_results)

# Test Infrastructure vs Regulatory
h1_test = analyzer.test_infrastructure_vs_regulatory()

# Apply FDR correction
fdr_results = analyzer.apply_fdr_correction()

# Get publication table
pub_table = analyzer.generate_publication_table()
```

### Example 3: Robustness Checks

```python
from robustness_checks import RobustnessChecks

checker = RobustnessChecks(data_path='event_study/data')

# Run specific check
placebo_results = checker.run_placebo_test(n_placebos=1000)

# Or run all checks
all_robust = checker.run_all_robustness_checks(
    cryptos=['btc', 'eth'],
    run_ohlc=True,
    run_placebo=True,
    run_winsorization=True,
    run_event_window=True
)
```

### Example 4: Bootstrap Confidence Intervals

```python
from bootstrap_inference_optimized import BootstrapInference

# Standard usage
bootstrap = BootstrapInference(returns, n_bootstrap=500, n_jobs=-1)
results = bootstrap.residual_bootstrap_tarch(model_type='TARCH')

# View confidence intervals
for param, ci in results['confidence_intervals'].items():
    print(f"{param}: [{ci['ci_lower']:.6f}, {ci['ci_upper']:.6f}]")
```

---

## DEPENDENCIES

**Core:**
- `pandas >= 1.3.0`
- `numpy >= 1.21.0`
- `scipy >= 1.7.0`

**Statistics:**
- `statsmodels >= 0.13.0` (Granger causality, time series)
- `arch >= 5.0.0` (GARCH models, optional for baseline)

**Visualization:**
- `matplotlib >= 3.4.0`
- `seaborn >= 0.11.0`

**Performance:**
- `joblib >= 1.0.0` (parallel bootstrap)
- `tqdm >= 4.62.0` (progress bars)

**Optional:**
- `coingecko_fetcher` (OHLC data for robustness check)

---

## VALIDATION CHECKLIST

**Before publishing results, verify:**

- [ ] All event coefficients extracted correctly from TARCH-X models
- [ ] FDR correction applied at α = 0.10
- [ ] Cohen's d > 0.8 (large effect size)
- [ ] Paired t-test p < 0.05 for Infrastructure vs Regulatory
- [ ] Placebo test: observed > 95th percentile
- [ ] Sign stability > 90% across event windows
- [ ] Ranking stability: Spearman ρ > 0.90
- [ ] Bootstrap convergence rate > 80%
- [ ] OHLC correlation > 0.80 with returns volatility
- [ ] Outlier sensitivity: Cohen's d still "huge" after winsorization
- [ ] FTX verification: all cryptos show positive coefficients

---

## PUBLICATION READINESS

**This analysis layer provides:**

1. **Statistical Rigor:** Multiple hypothesis tests with appropriate corrections
2. **Robustness:** Four independent robustness checks validate core findings
3. **Transparency:** Bootstrap confidence intervals quantify uncertainty
4. **Reproducibility:** Seeded random number generation ensures replicability

**Output suitable for:**
- Top-tier finance journals (JF, JFE, RFS, JBF)
- Peer review with rigorous statistical standards
- Replication by independent researchers

**Next steps for manuscript:**
1. Incorporate hypothesis test results into Results section
2. Add robustness checks as separate subsection or appendix
3. Include bootstrap confidence intervals in tables
4. Reference placebo test to address spurious correlation concerns

---

**Last Updated:** October 28, 2025
**Maintainer:** Research Team
**Related Documentation:**
- `DOCS_PUBLICATION_PIPELINE.md` - Full publication workflow
- `DOCS_DATA_PREPARATION.md` - Data preparation layer
- `DOCS_MODELING.md` - GARCH/TARCH modeling layer
