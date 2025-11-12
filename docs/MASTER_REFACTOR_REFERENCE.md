# MASTER REFACTOR REFERENCE
# Cryptocurrency Event Study - Complete Codebase Architecture

**Created:** October 28, 2025
**Purpose:** Guide upcoming refactor while preserving published research results
**Repository:** `/home/kawaiikali/Resurrexi/projects/planned-publish/event-study/`
**DOI:** 10.5281/zenodo.17449736

---

## TABLE OF CONTENTS

1. [Executive Summary](#executive-summary)
2. [Complete Data Flow Map](#complete-data-flow-map)
3. [Critical Implementation Details](#critical-implementation-details)
4. [Module Interdependency Map](#module-interdependency-map)
5. [File Organization Current State](#file-organization-current-state)
6. [Refactor Guidance](#refactor-guidance)
7. [Testing Strategy](#testing-strategy)
8. [DO NOT CHANGE](#do-not-change)

---

## EXECUTIVE SUMMARY

### High-Level Architecture

The cryptocurrency event study implements a **7-stage research pipeline** analyzing how Infrastructure vs Regulatory events affect cryptocurrency volatility across 6 cryptocurrencies (BTC, ETH, XRP, BNB, LTC, ADA) using 50 events from 2019-2025.

```
Raw CSVs → Data Prep → TARCH-X Models → Event Analysis → Hypothesis Tests → Robustness → Publication
   (8)        (1)          (3)               (1)              (1)            (3)         (5)
```

**Key Finding:** 97.4 percentage point spread in event sensitivity (BNB: 0.947% vs LTC: -0.027%)
**Null Result:** Infrastructure vs Regulatory events indistinguishable (p=0.997)
**Novel Method:** GDELT sentiment decomposition weighted by article type proportions

### Key Design Decisions

#### 1. Event Overlap Handling (CRITICAL - DO NOT CHANGE)

**Problem:** Multiple events on same dates double-count volatility effects

**Solutions:**
- **SEC Twin Suits (Events 31 & 32):** Composite dummy `D_SEC_enforcement_2023` covering June 2-9, 2023
- **EIP-1559 & Polygon Hack (Events 17 & 18):** Both dummies set to 0.5 on Aug 7-8, 2021 overlap
- **Bybit/SEC (Events 43 & 44):** Truncate windows to create 3-day gap (Feb 24-26)

**Rationale:** Prevents coefficient bias from double-counting simultaneous events

#### 2. GDELT Sentiment Decomposition (NOVEL METHODOLOGY)

**Three-stage process:**
1. Load weekly GDELT sentiment
2. Z-score normalize (52-week rolling window, 26-week min)
3. Decompose by article proportions:
   - `S_reg_decomposed = S_gdelt_normalized × reg_proportion`
   - `S_infra_decomposed = S_gdelt_normalized × infra_proportion`

**Why:** Separates sentiment signal into regulatory vs infrastructure components

#### 3. TARCH-X Model Specification

**Variance Equation:**
```
σ²_t = ω + α·ε²_{t-1} + γ·ε²_{t-1}·I(ε_{t-1}<0) + β·σ²_{t-1} + Σ(δⱼ × xⱼₜ)
```

Where:
- ω, α, β: GARCH parameters
- γ: Leverage (asymmetry) parameter
- δⱼ: Event/sentiment coefficients (variance-exogenous variables)
- xⱼₜ: Event dummies (D_infrastructure, D_regulatory) + decomposed sentiment

**Current Configuration (Oct 28, 2025):**
- Event dummies DISABLED in `garch_models.py:378-382` (testing sentiment-only)
- Parameters: 8 (6 base TARCH + 2 sentiment variables)
- Original: 10 parameters (6 base + 2 event dummies + 2 sentiment)

#### 4. Custom TARCH-X Implementation

**Why not use `arch` package?**
- Package doesn't properly support exogenous variables in variance equation
- Full control over MLE optimization
- Academic rigor for thesis requirements
- Transparent mathematical implementation

**Trade-off:** More code complexity, but methodological contribution

---

## COMPLETE DATA FLOW MAP

### Visual Pipeline

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           RAW INPUTS (data/)                              │
│  • btc.csv, eth.csv, xrp.csv, bnb.csv, ltc.csv, ada.csv                 │
│    (columns: snapped_at, price)                                          │
│  • events.csv (50 events: event_id, date, label, title, type)           │
│  • gdelt.csv (weekly: week_start, avg_tone, reg_prop, infra_prop)       │
└────────────────────────────┬─────────────────────────────────────────────┘
                             │
                             │ STAGE 1: DATA PREPARATION (data_preparation.py)
                             ↓
┌──────────────────────────────────────────────────────────────────────────┐
│ DataPreparation.prepare_crypto_data()                                    │
│ ├─ Load CSVs → UTC-aware timestamps                                     │
│ ├─ Calculate log returns: r_t = ln(P_t / P_{t-1}) × 100                │
│ ├─ Winsorize outliers: ±5σ from 30-day rolling mean                    │
│ ├─ Create event dummies: 7-day windows (±3 days) with special handling │
│ │   • SEC Twin Suits → D_SEC_enforcement_2023                          │
│ │   • EIP/Polygon overlap → 0.5 adjustment                             │
│ │   • Bybit/SEC → truncate windows                                     │
│ ├─ Aggregate by type: D_infrastructure, D_regulatory                    │
│ └─ Merge GDELT sentiment: 52-week z-score + theme decomposition        │
│                                                                           │
│ OUTPUT: 6 DataFrames (one per crypto) with columns:                     │
│   • price, returns, returns_winsorized                                  │
│   • D_event_1...D_event_50 (individual event dummies)                   │
│   • D_infrastructure, D_regulatory (aggregate dummies)                  │
│   • S_gdelt_normalized (overall sentiment z-score)                      │
│   • S_reg_decomposed, S_infra_decomposed (theme-specific sentiment)    │
└────────────────────────────┬─────────────────────────────────────────────┘
                             │
                             │ STAGE 2: MODEL ESTIMATION (garch_models.py)
                             ↓
┌──────────────────────────────────────────────────────────────────────────┐
│ GARCHModels.estimate_all_models()                                        │
│                                                                           │
│ For each cryptocurrency:                                                 │
│ ├─ GARCH(1,1): Baseline (5 params: μ, ω, α, β, ν)                      │
│ ├─ TARCH(1,1): Add leverage (6 params: +γ)                             │
│ └─ TARCH-X: Add events/sentiment (8-10 params: +δⱼ)                    │
│     Uses tarch_x_manual.py (custom MLE implementation)                  │
│                                                                           │
│ TARCH-X Implementation (tarch_x_manual.py):                             │
│ ├─ TARCHXEstimator class                                                │
│ ├─ _variance_recursion(): Compute σ²_t recursively                     │
│ ├─ _log_likelihood(): Student-t MLE objective                           │
│ ├─ _numerical_hessian(): Standard errors via central differences        │
│ └─ estimate(): SLSQP optimization with parameter bounds                 │
│                                                                           │
│ OUTPUT: model_results Dict[crypto, Dict[model_name, ModelResults]]      │
│   ModelResults attributes:                                               │
│   • parameters, std_errors, pvalues                                     │
│   • event_effects (variance-exogenous coefficients)                     │
│   • sentiment_effects                                                    │
│   • leverage_effect (γ parameter)                                       │
│   • volatility series, residuals                                        │
│   • aic, bic, log_likelihood, convergence flag                         │
└────────────────────────────┬─────────────────────────────────────────────┘
                             │
                             │ STAGE 3: EVENT ANALYSIS (event_impact_analysis.py)
                             ↓
┌──────────────────────────────────────────────────────────────────────────┐
│ EventImpactAnalysis(model_results)                                       │
│ ├─ Extract all event coefficients from TARCH-X models                   │
│ ├─ Classify by type: Infrastructure, Regulatory, Sentiment              │
│ ├─ Apply FDR correction (Benjamini-Hochberg at α=0.10)                 │
│ ├─ Calculate inverse-variance weighted averages                         │
│ ├─ Test Infrastructure vs Regulatory (paired t-test)                    │
│ └─ Calculate persistence measures (half-life)                           │
│                                                                           │
│ OUTPUT: analysis_results Dict                                            │
│   • event_coefficients: DataFrame (crypto, event_var, coef, p_val)     │
│   • fdr_corrected_pvalues: DataFrame with adjusted significance         │
│   • by_crypto: Summary stats per cryptocurrency                         │
│   • hypothesis_test: Infrastructure vs Regulatory t-test results        │
│   • inverse_variance_weighted: Precision-weighted meta-effect           │
└────────────────────────────┬─────────────────────────────────────────────┘
                             │
                             │ STAGE 4: HYPOTHESIS TESTING (hypothesis_testing_results.py)
                             ↓
┌──────────────────────────────────────────────────────────────────────────┐
│ HypothesisTestingResults.run_all_tests()                                 │
│                                                                           │
│ H1: Infrastructure > Regulatory                                          │
│ ├─ Coefficient comparison (paired t-test)                               │
│ ├─ Major events empirical analysis (FTX, Terra, ETF, etc.)             │
│ └─ Persistence analysis (half-life comparison)                          │
│                                                                           │
│ H2: Sentiment Leading Indicator                                          │
│ ├─ Cross-correlations (lags -4 to +4 weeks)                            │
│ ├─ Granger causality tests                                              │
│ └─ Optimal lag detection                                                 │
│                                                                           │
│ H3: TARCH-X Superiority                                                  │
│ ├─ AIC comparison (TARCH vs TARCH-X)                                   │
│ ├─ BIC comparison                                                        │
│ └─ Win rate calculation                                                  │
│                                                                           │
│ FTX Verification:                                                        │
│ └─ Ensure control window fix produces positive coefficients             │
│                                                                           │
│ OUTPUT: hypothesis_results Dict (H1/H2/H3 test statistics + FTX check) │
└────────────────────────────┬─────────────────────────────────────────────┘
                             │
                             │ STAGE 5: ROBUSTNESS CHECKS (robustness_*.py)
                             ↓
┌──────────────────────────────────────────────────────────────────────────┐
│ RobustnessChecks.run_all_robustness_checks()                            │
│                                                                           │
│ Check 1: OHLC Volatility (robustness_checks.py)                         │
│ └─ Garman-Klass estimator vs returns-based (ρ > 0.80 validates)        │
│                                                                           │
│ Check 2: Placebo Test (robustness_placebo_outlier.py)                   │
│ ├─ 1,000 random event dates (avoid real events ±6 days)                │
│ ├─ Shuffle coefficients across cryptos                                  │
│ └─ Observed > 95th percentile validates event-driven heterogeneity     │
│                                                                           │
│ Check 3: Winsorization Robustness (robustness_checks.py)                │
│ └─ Raw vs winsorized returns (winsorized has lower AIC)                │
│                                                                           │
│ Check 4: Event Window Sensitivity (robustness_alternative_windows.py)   │
│ ├─ Test windows: [-1,+1], [-3,+3], [-5,+5], [-7,+7]                   │
│ ├─ Sign stability: 94% (coefficients maintain same sign)               │
│ └─ Ranking stability: Spearman ρ > 0.95                                │
│                                                                           │
│ Check 5: Outlier Sensitivity (robustness_placebo_outlier.py)            │
│ └─ Winsorize at 90th percentile (Cohen's d: 5.19 → 3.5, still huge)   │
│                                                                           │
│ OUTPUT: robustness_results Dict (all check results + visualizations)    │
└────────────────────────────┬─────────────────────────────────────────────┘
                             │
                             │ STAGE 6: BOOTSTRAP INFERENCE (bootstrap_inference*.py)
                             ↓
┌──────────────────────────────────────────────────────────────────────────┐
│ BootstrapInference.residual_bootstrap_tarch()                           │
│ ├─ Resample standardized residuals (500 replications)                  │
│ ├─ Re-estimate TARCH models                                             │
│ ├─ Calculate percentile confidence intervals (2.5th, 97.5th)           │
│ └─ Track convergence rate (>80% acceptable)                            │
│                                                                           │
│ Optimized version (bootstrap_inference_optimized.py):                   │
│ └─ Parallelization with joblib (5-10x speedup)                         │
│                                                                           │
│ OUTPUT: bootstrap_results Dict (CIs, convergence rates, distributions) │
└────────────────────────────┬─────────────────────────────────────────────┘
                             │
                             │ STAGE 7: PUBLICATION OUTPUTS (publication_outputs.py, create_*.py)
                             ↓
┌──────────────────────────────────────────────────────────────────────────┐
│ PublicationOutputs.generate_all_outputs()                                │
│                                                                           │
│ LaTeX Tables (outputs/publication/latex/):                              │
│ ├─ model_comparison.tex (AIC/BIC across GARCH models)                  │
│ ├─ event_comparison.tex (Infrastructure vs Regulatory test)            │
│ ├─ leverage_parameters.tex (Asymmetric volatility effects)             │
│ └─ table1_heterogeneity.tex (Cross-sectional heterogeneity)           │
│                                                                           │
│ Figures (publication_figures/):                                          │
│ ├─ figure1_heterogeneity.pdf (THE MONEY SHOT: 97.4pp spread)          │
│ ├─ figure2_infrastructure_vs_regulatory.pdf (NULL RESULT: p=0.997)     │
│ ├─ figure3_event_coefficients_heatmap.pdf (Token-specific responses)   │
│ ├─ figure4_model_comparison.pdf (RMSE, MAE, AIC, BIC)                 │
│ └─ temporal_stability_analysis.png (Ranking stability ρ=1.00)         │
│                                                                           │
│ CSV Exports (outputs/publication/csv_exports/):                         │
│ ├─ {crypto}_parameters.csv (All parameter estimates)                   │
│ ├─ model_comparison.csv (AIC/BIC comparison)                           │
│ ├─ event_impacts_fdr.csv (Event coefficients with FDR correction)      │
│ └─ hypothesis_test.csv (t-test, Mann-Whitney, Cohen's d)              │
│                                                                           │
│ Diagnostic Plots:                                                        │
│ ├─ volatility_major_events.png (FTX, Terra, ETF timelines)            │
│ ├─ diagnostic_plots.png (ACF + Q-Q plots)                              │
│ └─ event_impact_comparison.png (Bar chart with CIs)                    │
└──────────────────────────────────────────────────────────────────────────┘
```

### Data Transformations

| Stage | Input | Transformation | Output |
|-------|-------|----------------|--------|
| **Stage 1** | `btc.csv` (price, date) | log returns, winsorize, merge events/sentiment | `prepared_df` (returns + dummies + sentiment) |
| **Stage 2** | `prepared_df` | TARCH-X MLE estimation | `ModelResults` (params, volatility, event_effects) |
| **Stage 3** | `model_results` | Extract coefficients, FDR correction | `analysis_results` (event impacts, hypothesis tests) |
| **Stage 4** | `analysis_results` | Statistical tests (t-test, Granger) | `hypothesis_results` (H1/H2/H3) |
| **Stage 5** | `prepared_df` + `model_results` | Robustness tests (placebo, OHLC, windows) | `robustness_results` (validation checks) |
| **Stage 6** | `returns` | Bootstrap resampling | `bootstrap_results` (confidence intervals) |
| **Stage 7** | All results | Format for publication | LaTeX tables, PDF figures, CSVs |

---

## CRITICAL IMPLEMENTATION DETAILS

### Event Dummy Logic (DO NOT CHANGE)

#### 1. Standard Event Windows
```python
# data_preparation.py, create_event_window()
window_before = 3  # days before event
window_after = 3   # days after event
total_window = 7   # days (±3 + event day)
```

#### 2. SEC Twin Suits Composite Dummy
```python
# events.csv: event_id 31 (Coinbase) and 32 (Binance)
# Filed on 2023-06-05 and 2023-06-06 (consecutive days)

if event_id in [31, 32]:
    if event_id == 31:  # Create composite dummy once
        dummy_name = 'D_SEC_enforcement_2023'
        window_start = pd.Timestamp('2023-06-02', tz='UTC')
        window_end = pd.Timestamp('2023-06-09', tz='UTC')
        dummies[dummy_name] = 0
        mask = (dummies.index >= window_start) & (dummies.index <= window_end)
        dummies.loc[mask, dummy_name] = 1
    # Skip event_id 32 (already captured in composite)
    continue
```

**Why:** Single coefficient captures joint enforcement action effect

#### 3. EIP-1559 & Polygon Hack Overlap Adjustment
```python
# events.csv: event_id 17 (EIP-1559) and 18 (Polygon Hack)
# EIP-1559: 2021-08-05, Polygon: 2021-08-07
# Overlapping days: Aug 7-8

if 'D_event_17' in dummies.columns and 'D_event_18' in dummies.columns:
    overlap_dates = [
        pd.Timestamp('2021-08-07', tz='UTC'),
        pd.Timestamp('2021-08-08', tz='UTC')
    ]
    adjustment = -0.5

    for date in overlap_dates:
        if date in dummies.index:
            if dummies.loc[date, 'D_event_17'] == 1 and dummies.loc[date, 'D_event_18'] == 1:
                dummies.loc[date, 'D_event_17'] = 0.5  # 1 + (-0.5)
                dummies.loc[date, 'D_event_18'] = 0.5
```

**Coefficient Interpretation:**
- Model coefficients represent effect when dummy = 1.0
- On overlap days (dummy = 0.5), actual effect = coefficient × 0.5
- Total volatility impact = 0.5×coef₁₇ + 0.5×coef₁₈

**Trade-off:** Prevents double-counting but may underestimate if effects are truly additive

#### 4. Bybit/SEC Window Truncation
```python
# events.csv: event_id 43 (Bybit hack, 2025-02-21) and 44 (SEC dismissal, 2025-02-27)

if event_id == 43:  # Bybit hack
    truncate_date = pd.Timestamp('2025-02-23', tz='UTC')
    for date in window:
        if date <= truncate_date and date in dummies.index:
            dummies.loc[date, 'D_event_43'] = 1

if event_id == 44:  # SEC dismissal
    start_date = pd.Timestamp('2025-02-27', tz='UTC')
    for date in window:
        if date >= start_date and date in dummies.index:
            dummies.loc[date, 'D_event_44'] = 1
```

**Result:** 3-day gap (Feb 24-26) prevents window overlap

### GDELT Sentiment Decomposition Methodology

#### Step 1: Load Weekly GDELT Data
```python
# gdelt.csv columns:
# - week_start: Monday date
# - S_gdelt_raw: Average tone (-10 to +10)
# - reg_proportion: Proportion of regulatory articles (0-1)
# - infra_proportion: Proportion of infrastructure articles (0-1)

df = pd.read_csv('data/gdelt.csv')
df['week_start'] = pd.to_datetime(df['week_start'], utc=True)
```

#### Step 2: Z-score Normalization (52-week rolling)
```python
window_size = 52  # 1 year of weekly data
min_periods = 26  # 6 months minimum for initialization

rolling_mean = df['S_gdelt_raw'].rolling(window=52, min_periods=26).mean()
rolling_std = df['S_gdelt_raw'].rolling(window=52, min_periods=26).std()

df['S_gdelt_normalized'] = (df['S_gdelt_raw'] - rolling_mean) / rolling_std

# Handle edge cases
df.loc[rolling_std < 0.001, 'S_gdelt_normalized'] = 0  # Avoid division by near-zero
df['S_gdelt_normalized'].fillna(0, inplace=True)  # Missing values before June 2019
```

**Why 52-week window?**
- Captures full yearly cycle (seasonal patterns, regulatory cycles)
- Handles market regime shifts (bull/bear) dynamically
- 26-week min ensures at least 6 months data before calculating z-score

#### Step 3: Theme Decomposition
```python
df['S_reg_decomposed'] = df['S_gdelt_normalized'] * df['reg_proportion']
df['S_infra_decomposed'] = df['S_gdelt_normalized'] * df['infra_proportion']
```

**Purpose:** Separates sentiment signal into regulatory vs infrastructure components

#### Step 4: Weekly → Daily Reindexing
```python
# Forward-fill weekly data to daily frequency
daily_index = pd.date_range(start=sentiment_subset.index.min(),
                           end=daily_data.index.max(),
                           freq='D', tz='UTC')
sentiment_daily = sentiment_subset.reindex(daily_index).ffill()

# Merge with returns data
result = daily_data.merge(sentiment_daily, left_index=True, right_index=True, how='left')
```

**Logic:** Sentiment from week starting Monday applies to all 7 days until next week's data

### TARCH-X Model Specification Details

#### Parameter Count
| Model | Base Params | Exog Params | Total | Parameters |
|-------|-------------|-------------|-------|------------|
| GARCH(1,1) | 5 | 0 | 5 | μ, ω, α, β, ν |
| TARCH(1,1) | 6 | 0 | 6 | + γ (leverage) |
| TARCH-X (full) | 6 | 4 | 10 | + δ_D_infra, δ_D_reg, δ_S_infra_decomp, δ_S_reg_decomp |
| TARCH-X (current) | 6 | 2 | 8 | + δ_S_infra_decomp, δ_S_reg_decomp (event dummies disabled Oct 28) |

#### Variance Recursion (Core Algorithm)
```python
# tarch_x_manual.py, _variance_recursion()
def _variance_recursion(self, params):
    omega, alpha, gamma, beta = params[0:4]
    nu = params[4]  # Student-t degrees of freedom

    variance = np.zeros(self.n_obs)
    residuals = (self.returns - self.returns.mean()).values

    # Initialize first variance
    variance[0] = np.var(self.returns)

    # Recursive computation
    for t in range(1, self.n_obs):
        # Previous squared residual
        eps_sq_prev = residuals[t-1] ** 2

        # Leverage term (GJR-GARCH)
        leverage_term = gamma * eps_sq_prev * (residuals[t-1] < 0)

        # Base TARCH terms
        variance[t] = omega + alpha * eps_sq_prev + leverage_term + beta * variance[t-1]

        # Add exogenous variables (event dummies + sentiment)
        if self.has_exog:
            for i, exog_name in enumerate(self.exog_names):
                delta = params[5 + i]  # Exogenous coefficient
                exog_value = self.exog_vars.iloc[t, i]
                variance[t] += delta * exog_value

        # Ensure variance is positive
        variance[t] = max(variance[t], 1e-8)

    return variance, residuals
```

**Why Recursive:** Variance at time t depends on variance at time t-1 (cannot fully vectorize)

#### Log-Likelihood Function (Student-t)
```python
def _log_likelihood(self, params):
    nu = params[4]
    variance, residuals = self._variance_recursion(params)
    std_residuals = residuals / np.sqrt(variance)

    log_lik = 0
    for t in range(self.n_obs):
        # Gamma function terms
        log_gamma_term = (np.log(gamma((nu + 1) / 2)) -
                         np.log(gamma(nu / 2)) -
                         0.5 * np.log(np.pi * (nu - 2)))

        # Variance term
        log_var_term = -0.5 * np.log(variance[t])

        # Density term
        density_term = -((nu + 1) / 2) * np.log(1 + std_residuals[t]**2 / (nu - 2))

        log_lik += log_gamma_term + log_var_term + density_term

    return -log_lik  # Return negative for minimization
```

**Why Student-t:** Captures fat tails in cryptocurrency returns (more robust than Normal)

#### Parameter Bounds & Constraints
```python
bounds = [
    (1e-8, None),      # omega > 0
    (1e-8, 0.3),       # 0 < alpha < 0.3
    (-0.5, 0.5),       # -0.5 < gamma < 0.5
    (1e-8, 0.999),     # 0 < beta < 1
    (2.1, 50),         # 2 < nu < 50 (finite variance)
    *[(-1.0, 1.0) for _ in range(self.n_exog)]  # Event/sentiment coefficients
]

# Stationarity constraint (not enforced in optimization, checked post-estimation)
persistence = alpha + beta + gamma/2
assert persistence < 1.0, "Non-stationary model"
```

### Event Impact Analysis Details

#### FDR Correction (Benjamini-Hochberg)
```python
# event_impact_analysis.py, apply_fdr_correction()
from statsmodels.stats.multitest import fdrcorrection

# 50 events × 6 cryptos = 300 statistical tests
# Expected false positives at α=0.05: 15

reject, pvals_corrected = fdrcorrection(df['p_value'], alpha=0.10, method='indep')
df['fdr_corrected_pvalue'] = pvals_corrected
df['fdr_significant'] = reject
```

**Why FDR vs Bonferroni:**
- Bonferroni too conservative (controls family-wise error rate)
- FDR controls expected proportion of false discoveries
- More appropriate for exploratory research

#### Inverse-Variance Weighting
```python
def calculate_inverse_variance_weighted_average(df):
    # Weight by precision (inverse of squared standard error)
    df['weight'] = 1 / (df['std_error'] ** 2)

    # Weighted average
    weighted_avg = (df['coefficient'] * df['weight']).sum() / df['weight'].sum()

    # Standard error of weighted average
    se_weighted = np.sqrt(1 / df['weight'].sum())

    # Z-test for significance
    z_statistic = weighted_avg / se_weighted
    p_value = 2 * (1 - norm.cdf(np.abs(z_statistic)))

    return {
        'weighted_avg': weighted_avg,
        'se': se_weighted,
        'z_statistic': z_statistic,
        'p_value': p_value,
        'ci_lower': weighted_avg - 1.96 * se_weighted,
        'ci_upper': weighted_avg + 1.96 * se_weighted
    }
```

**Why:** Gives more weight to precisely estimated coefficients (low standard error)

### Special Event Handling

#### Major Events for Volatility Analysis
```python
# hypothesis_testing_results.py, analyze_major_events_volatility()
major_events = [
    (1, '2022-11-11', 'FTX Bankruptcy', 'Infrastructure'),
    (2, '2022-05-09', 'Terra/Luna Collapse', 'Infrastructure'),
    (3, '2024-01-10', 'BTC ETF Approval', 'Regulatory'),
    (4, '2021-09-24', 'China Mining Ban', 'Regulatory'),
    (5, '2019-02-15', 'QuadrigaCX Collapse', 'Infrastructure'),
    (6, '2019-06-21', 'FATF Crypto Rules', 'Regulatory')
]

# For each event, calculate:
# - Pre-event volatility: 30 days before (excluding 5 days before event)
# - Event window volatility: ±2 days around event
# - Post-event volatility: 5-15 days after
# - Percentage increase: (event_vol - pre_vol) / pre_vol × 100
# - Persistence: days for shock to decay to 50%
```

**Purpose:** Empirical validation of H1 (Infrastructure > Regulatory)

---

## MODULE INTERDEPENDENCY MAP

### Critical Execution Order

```
config.py (loaded first by all modules)
    ↓
data_preparation.py (creates crypto_data)
    ↓
garch_models.py (requires crypto_data with returns)
    ↓
event_impact_analysis.py (requires model_results with TARCH-X parameters)
    ↓
hypothesis_testing_results.py (requires analysis_results)
    ↓
[Optional branches - can run in parallel]
    ├─→ robustness_checks.py (requires crypto_data + model_results)
    ├─→ bootstrap_inference.py (requires returns series)
    └─→ publication_outputs.py (requires all results)
```

### Import Graph

```
run_event_study_analysis.py (orchestrator)
├── config.py
├── data_preparation.py
│   └── config.py
├── garch_models.py
│   ├── data_preparation.py
│   └── tarch_x_manual.py
├── event_impact_analysis.py
│   ├── data_preparation.py
│   └── garch_models.py
├── hypothesis_testing_results.py
│   ├── data_preparation.py
│   ├── garch_models.py
│   └── event_impact_analysis.py
├── robustness_checks.py
│   ├── data_preparation.py
│   ├── garch_models.py
│   └── bootstrap_inference.py
├── bootstrap_inference.py
│   └── garch_models.py
└── publication_outputs.py
    └── config.py
```

### What Depends on What

| Module | Depends On | Provides To | Breaking Changes Impact |
|--------|------------|-------------|-------------------------|
| `config.py` | None | All modules | **CRITICAL** - Breaks everything |
| `data_preparation.py` | `config.py` | All analysis modules | **CRITICAL** - Breaks pipeline |
| `garch_models.py` | `data_preparation.py`, `tarch_x_manual.py` | Event analysis, hypothesis tests | **HIGH** - Invalidates results |
| `tarch_x_manual.py` | None | `garch_models.py` | **HIGH** - Changes model specification |
| `event_impact_analysis.py` | `garch_models.py` | Hypothesis tests, publication | **MEDIUM** - Changes statistical tests |
| `hypothesis_testing_results.py` | `event_impact_analysis.py` | Publication outputs | **MEDIUM** - Changes conclusions |
| `robustness_checks.py` | `data_preparation.py`, `garch_models.py` | Publication outputs | **LOW** - Supplementary validation |
| `bootstrap_inference.py` | `garch_models.py` | Publication outputs | **LOW** - Confidence intervals only |
| `publication_outputs.py` | All results | LaTeX/figures/CSVs | **VERY LOW** - Formatting only |

### Critical Dependencies

**DO NOT CHANGE WITHOUT VERIFICATION:**

1. **`data_preparation.py` → Event dummy creation logic**
   - Affects: All downstream analysis
   - Test: `tests/test_edge_cases.py`
   - Verify: Event window dates, overlap handling, dummy values

2. **`tarch_x_manual.py` → Variance recursion & MLE**
   - Affects: All coefficient estimates
   - Test: `tests/test_garch_models.py`
   - Verify: Parameter convergence, AIC/BIC values, residual diagnostics

3. **`garch_models.py` → Exogenous variable preparation**
   - Affects: Which variables enter variance equation
   - Test: `tests/test_tarch_x_integration.py`
   - Verify: Multicollinearity checks, variable alignment

4. **`event_impact_analysis.py` → FDR correction**
   - Affects: Statistical significance conclusions
   - Test: `tests/test_statistical_methods.py`
   - Verify: P-value adjustments, rejection flags

---

## FILE ORGANIZATION CURRENT STATE

### Core Analysis Modules (700-1000 lines each)

```
code/
├── data_preparation.py              # 700+ lines - ETL pipeline
│   ├── DataPreparation class
│   ├── create_event_dummies() - CRITICAL event overlap handling
│   ├── load_gdelt_sentiment() - 52-week z-score normalization
│   ├── winsorize_returns() - Outlier capping (±5σ)
│   └── prepare_crypto_data() - Main pipeline method
│
├── garch_models.py                  # 500+ lines - Model estimation interface
│   ├── GARCHModels class
│   ├── estimate_garch_11() - Uses arch package
│   ├── estimate_tarch_11() - Uses arch package
│   ├── estimate_tarch_x() - Calls tarch_x_manual.py
│   └── _prepare_exogenous_variables() - Lines 378-382 (event dummies disabled Oct 28)
│
├── tarch_x_manual.py                # 500+ lines - Custom TARCH-X implementation
│   ├── TARCHXEstimator class
│   ├── _variance_recursion() - Recursive σ²_t computation
│   ├── _log_likelihood() - Student-t MLE objective
│   ├── _numerical_hessian() - Standard errors via central differences
│   └── estimate() - SLSQP optimization with parameter bounds
│
├── event_impact_analysis.py        # 978 lines - Event coefficient extraction
│   ├── EventImpactAnalysis class
│   ├── _extract_all_event_coefficients()
│   ├── test_infrastructure_vs_regulatory() - Paired t-test
│   ├── apply_fdr_correction() - Benjamini-Hochberg at α=0.10
│   └── calculate_inverse_variance_weighted_average()
│
└── hypothesis_testing_results.py   # 442 lines - Statistical hypothesis tests
    ├── HypothesisTestingResults class
    ├── test_hypothesis_1() - Infrastructure > Regulatory
    ├── test_hypothesis_2() - Sentiment leading indicator
    ├── test_hypothesis_3() - TARCH-X superiority
    └── verify_ftx_event() - Control window fix validation
```

### Robustness & Validation (650-760 lines each)

```
code/
├── robustness_checks.py              # 759 lines - OHLC, placebo, winsorization
│   ├── check_ohlc_volatility() - Garman-Klass vs returns-based
│   ├── run_placebo_test() - 1,000 random event dates
│   ├── check_winsorization_robustness() - Raw vs winsorized
│   └── check_event_window_sensitivity() - Windows: [-2,+2], [-3,+3], [-5,+5]
│
├── robustness_alternative_windows.py # 667 lines - Window sensitivity analysis
│   ├── Test windows: [-1,+1], [-3,+3], [-5,+5], [-7,+7]
│   ├── Calculate heterogeneity ratio, Cohen's d, Kruskal-Wallis H
│   ├── Sign stability: 94% (coefficients maintain same sign)
│   └── Ranking stability: Spearman ρ > 0.95
│
└── robustness_placebo_outlier.py    # 759 lines - Publication-ready robustness
    ├── Placebo test: 1,000 iterations, shuffle coefficients
    ├── Outlier sensitivity: Winsorize at 90th percentile
    └── Metrics: Kruskal-Wallis H, range, Cohen's d, ratio
```

### Bootstrap Inference (370-490 lines)

```
code/
├── bootstrap_inference.py            # 368 lines - Standard residual bootstrap
│   ├── BootstrapInference class
│   ├── residual_bootstrap_tarch() - Resample standardized residuals (500 reps)
│   ├── Calculate percentile CIs (2.5th, 97.5th)
│   └── Track convergence rate (>80% acceptable)
│
└── bootstrap_inference_optimized.py # 489 lines - Parallelized version
    ├── Vectorized block bootstrap
    ├── Parallelization with joblib (5-10x speedup)
    └── Progress bars with tqdm
```

### Publication Pipeline (Varies)

```
code/
├── publication_outputs.py            # Main output generator
│   ├── PublicationOutputs class
│   ├── generate_latex_model_comparison_table()
│   ├── generate_latex_event_comparison_table()
│   ├── plot_volatility_around_events()
│   ├── plot_diagnostic_charts()
│   └── generate_all_outputs() - Master function
│
├── create_publication_figures.py    # 4 main figures (timeline, volatility, heatmap, models)
│   ├── create_event_timeline_figure()
│   ├── create_volatility_comparison_figure()
│   ├── create_impact_heatmap()
│   └── create_model_comparison_figure()
│
├── create_heterogeneity_figures.py  # KEY RESULTS (3 figures + table)
│   ├── figure1_heterogeneity.pdf - THE MONEY SHOT (97.4pp spread)
│   ├── figure2_infrastructure_vs_regulatory.pdf - NULL RESULT (p=0.997)
│   ├── figure3_event_coefficients_heatmap.pdf - Token-specific responses
│   └── table1_heterogeneity.tex - LaTeX table
│
├── create_temporal_stability_figure.py # Robustness visualization
│   └── temporal_stability_analysis.png - Perfect ranking stability (ρ=1.00)
│
└── generate_latex_tables.py         # Standalone table generator
    ├── table1_event_study_results.tex
    ├── table2_descriptive_statistics.tex
    ├── table3_volatility_models.tex
    └── table4_regression_results.tex
```

### Utility Scripts

```
code/
├── run_event_study_analysis.py      # Main orchestration script (7-stage pipeline)
├── config.py                         # Paths, seeds, parameters
├── validate_data.py                  # Data integrity checks
├── run_smoke_tests.py                # Quick validation
├── tarch_x_integration.py            # Integration guide
└── tarch_x_manual_optimized.py      # Vectorized TARCH-X (5x speedup)
```

### Legacy/Experimental (DO NOT USE)

```
code/
├── data_preparation_template.py      # Template, not used
├── extract_volatility_template.py    # Template, not used
├── extract_volatility.py             # Old extraction logic
├── fix_correlation_matrix.py         # One-time fix
├── ftx_anomaly_detection.py          # Exploratory analysis
├── ftx_time_series_forecast.py       # Exploratory analysis
├── temporal_stability_analysis.py    # Analysis script (results hardcoded in create_temporal_stability_figure.py)
├── quick_anomaly_scan.py             # Debugging tool
├── validate_fixes.py                 # One-time validation
└── sentiment_improvement_analysis.py # Exploratory analysis
```

### Tests

```
tests/
├── test_data_preparation_original.py # ETL pipeline validation
├── test_garch_models.py              # Model estimation verification
├── test_tarch_x_integration.py       # TARCH-X integration tests
├── test_statistical_methods.py       # Hypothesis test validation
├── test_edge_cases.py                # Event overlap handling
├── test_data_validation.py           # Data integrity checks
└── test_integration.py               # End-to-end pipeline test
```

### Redundancies Identified

| Original | Optimized | Status | Action |
|----------|-----------|--------|--------|
| `tarch_x_manual.py` | `tarch_x_manual_optimized.py` | Original in use | **Keep both** (original for clarity, optimized for performance) |
| `bootstrap_inference.py` | `bootstrap_inference_optimized.py` | Original in use | **Keep both** (same rationale) |
| `temporal_stability_analysis.py` | `create_temporal_stability_figure.py` | Superseded | **Remove temporal_stability_analysis.py** (hardcoded data) |
| `data_preparation_template.py` | None | Template | **Remove** (not used) |
| `extract_volatility_template.py` | None | Template | **Remove** (not used) |
| `extract_volatility.py` | Integrated into other modules | Old logic | **Remove** (superseded) |
| `fix_correlation_matrix.py` | None | One-time fix | **Move to /legacy/** |
| `validate_fixes.py` | None | One-time validation | **Move to /legacy/** |
| `ftx_anomaly_detection.py` | None | Exploratory | **Move to /exploratory/** |
| `ftx_time_series_forecast.py` | None | Exploratory | **Move to /exploratory/** |
| `quick_anomaly_scan.py` | None | Debugging | **Move to /utils/** |
| `sentiment_improvement_analysis.py` | None | Exploratory | **Move to /exploratory/** |
| `gdelt_bigquery_implementation.py` | None | Data collection script | **Move to /data_collection/** |

---

## REFACTOR GUIDANCE

### Goals

1. **Preserve Research Integrity:** Published results MUST NOT change
2. **Improve Maintainability:** Reduce code duplication, clarify dependencies
3. **Enhance Testability:** Modular design with clear interfaces
4. **Simplify Onboarding:** Clear separation of concerns, consistent naming

### Proposed Structure

```
event_study/
├── code/
│   ├── core/                        # CORE ANALYSIS (DO NOT CHANGE LOGIC)
│   │   ├── __init__.py
│   │   ├── config.py                # Configuration
│   │   ├── data_preparation.py      # ETL pipeline
│   │   ├── garch_models.py          # Model estimation interface
│   │   ├── tarch_x_manual.py        # Custom TARCH-X implementation
│   │   └── tarch_x_manual_optimized.py # Optimized version
│   │
│   ├── analysis/                    # STATISTICAL ANALYSIS
│   │   ├── __init__.py
│   │   ├── event_impact_analysis.py
│   │   └── hypothesis_testing_results.py
│   │
│   ├── robustness/                  # ROBUSTNESS CHECKS
│   │   ├── __init__.py
│   │   ├── robustness_checks.py
│   │   ├── robustness_alternative_windows.py
│   │   └── robustness_placebo_outlier.py
│   │
│   ├── inference/                   # BOOTSTRAP INFERENCE
│   │   ├── __init__.py
│   │   ├── bootstrap_inference.py
│   │   └── bootstrap_inference_optimized.py
│   │
│   ├── publication/                 # OUTPUT GENERATION
│   │   ├── __init__.py
│   │   ├── publication_outputs.py
│   │   ├── create_publication_figures.py
│   │   ├── create_heterogeneity_figures.py
│   │   ├── create_temporal_stability_figure.py
│   │   └── generate_latex_tables.py
│   │
│   ├── utils/                       # UTILITIES
│   │   ├── __init__.py
│   │   ├── validate_data.py
│   │   └── quick_anomaly_scan.py
│   │
│   ├── scripts/                     # ORCHESTRATION SCRIPTS
│   │   ├── run_event_study_analysis.py
│   │   └── run_smoke_tests.py
│   │
│   ├── exploratory/                 # EXPLORATORY ANALYSIS (NOT USED IN PUBLICATION)
│   │   ├── __init__.py
│   │   ├── ftx_anomaly_detection.py
│   │   ├── ftx_time_series_forecast.py
│   │   └── sentiment_improvement_analysis.py
│   │
│   └── legacy/                      # LEGACY CODE (DO NOT USE)
│       ├── __init__.py
│       ├── data_preparation_template.py
│       ├── extract_volatility_template.py
│       ├── extract_volatility.py
│       ├── fix_correlation_matrix.py
│       ├── validate_fixes.py
│       └── temporal_stability_analysis.py
│
├── data/                            # RAW DATA (DO NOT CHANGE)
│   ├── btc.csv
│   ├── eth.csv
│   ├── xrp.csv
│   ├── bnb.csv
│   ├── ltc.csv
│   ├── ada.csv
│   ├── events.csv
│   └── gdelt.csv
│
├── outputs/                         # OUTPUT DIRECTORY
│   ├── analysis_results/
│   ├── publication/
│   └── robustness/
│
├── tests/                           # TEST SUITE
│   ├── __init__.py
│   ├── test_data_preparation.py
│   ├── test_garch_models.py
│   ├── test_tarch_x_integration.py
│   ├── test_statistical_methods.py
│   ├── test_edge_cases.py
│   ├── test_data_validation.py
│   └── test_integration.py
│
├── docs/                            # DOCUMENTATION
│   ├── DOCS_DATA_PIPELINE.md
│   ├── DOCS_MODEL_ESTIMATION.md
│   ├── DOCS_MASTER_ORCHESTRATION.md
│   ├── DOCS_ANALYSIS_TESTING.md
│   ├── DOCS_PUBLICATION_PIPELINE.md
│   └── MASTER_REFACTOR_REFERENCE.md (this file)
│
├── publication_figures/             # PUBLICATION OUTPUTS
│   └── (generated figures)
│
├── publication_tables/              # PUBLICATION OUTPUTS
│   └── (generated LaTeX tables)
│
├── .env                             # ENVIRONMENT VARIABLES
├── requirements.txt                 # DEPENDENCIES
├── CLAUDE.md                        # CLAUDE CODE CONTEXT
└── README.md                        # PROJECT OVERVIEW
```

### What Should Be Consolidated

**Priority 1: Remove Clear Redundancies**
```bash
# Move to legacy/
mv code/data_preparation_template.py code/legacy/
mv code/extract_volatility_template.py code/legacy/
mv code/extract_volatility.py code/legacy/
mv code/temporal_stability_analysis.py code/legacy/

# Move to exploratory/
mv code/ftx_anomaly_detection.py code/exploratory/
mv code/ftx_time_series_forecast.py code/exploratory/
mv code/sentiment_improvement_analysis.py code/exploratory/

# Move to utils/
mv code/quick_anomaly_scan.py code/utils/

# Move to legacy/ (one-time fixes)
mv code/fix_correlation_matrix.py code/legacy/
mv code/validate_fixes.py code/legacy/
```

**Priority 2: Organize by Concern**
```bash
# Create subdirectories
mkdir code/core code/analysis code/robustness code/inference code/publication
mkdir code/utils code/scripts code/exploratory code/legacy

# Move core modules (DO NOT CHANGE LOGIC)
mv code/config.py code/core/
mv code/data_preparation.py code/core/
mv code/garch_models.py code/core/
mv code/tarch_x_manual.py code/core/
mv code/tarch_x_manual_optimized.py code/core/
mv code/tarch_x_integration.py code/core/

# Move analysis modules
mv code/event_impact_analysis.py code/analysis/
mv code/hypothesis_testing_results.py code/analysis/

# Move robustness modules
mv code/robustness_checks.py code/robustness/
mv code/robustness_alternative_windows.py code/robustness/
mv code/robustness_placebo_outlier.py code/robustness/

# Move inference modules
mv code/bootstrap_inference.py code/inference/
mv code/bootstrap_inference_optimized.py code/inference/

# Move publication modules
mv code/publication_outputs.py code/publication/
mv code/create_publication_figures.py code/publication/
mv code/create_heterogeneity_figures.py code/publication/
mv code/create_temporal_stability_figure.py code/publication/
mv code/generate_latex_tables.py code/publication/

# Move utilities
mv code/validate_data.py code/utils/
mv code/quick_anomaly_scan.py code/utils/

# Move scripts
mv code/run_event_study_analysis.py code/scripts/
mv code/run_smoke_tests.py code/scripts/
```

**Priority 3: Update Imports**
```python
# Before refactor:
from data_preparation import DataPreparation
from garch_models import GARCHModels

# After refactor:
from code.core.data_preparation import DataPreparation
from code.core.garch_models import GARCHModels
```

### What Should Be Separated

**1. Configuration Management**
- Current: Single `config.py` with all settings
- Proposed: Split into:
  - `code/core/config.py` - Core paths and parameters (DO NOT CHANGE)
  - `code/core/special_events.py` - Event overlap handling configs (DO NOT CHANGE)
  - `code/publication/figure_config.py` - Matplotlib settings (safe to modify)

**2. Event Dummy Creation**
- Current: Monolithic method in `data_preparation.py`
- Proposed: Extract to separate module:
  - `code/core/event_dummies.py` - Event overlap handling logic (DO NOT CHANGE)
  - Keep main `data_preparation.py` as orchestrator

**3. TARCH-X Estimation**
- Current: Single `tarch_x_manual.py` file
- Proposed: Split into:
  - `code/core/tarch_x_estimator.py` - Core estimation logic (DO NOT CHANGE)
  - `code/core/tarch_x_mle.py` - Log-likelihood and optimization
  - `code/core/tarch_x_inference.py` - Standard errors and confidence intervals

**4. Robustness Checks**
- Current: Multiple files with overlapping logic
- Proposed: Single `robustness_checks.py` with submodules:
  - `robustness/ohlc_volatility.py`
  - `robustness/placebo_test.py`
  - `robustness/window_sensitivity.py`
  - `robustness/outlier_sensitivity.py`

### What Needs to Stay for Research Reproducibility

**CRITICAL - DO NOT CHANGE:**

1. **Event Overlap Handling Logic** (`data_preparation.py`)
   - SEC Twin Suits composite dummy
   - EIP-1559 & Polygon Hack 0.5 adjustment
   - Bybit/SEC window truncation
   - **Reason:** Published results depend on exact event window definitions

2. **GDELT Sentiment Decomposition** (`data_preparation.py`)
   - 52-week z-score normalization
   - Theme decomposition by article proportions
   - Weekly → daily forward-fill
   - **Reason:** Novel methodology is core contribution

3. **TARCH-X Variance Recursion** (`tarch_x_manual.py`)
   - Recursive σ²_t computation
   - Parameter bounds and constraints
   - Student-t log-likelihood
   - **Reason:** Published coefficients depend on exact MLE implementation

4. **FDR Correction** (`event_impact_analysis.py`)
   - Benjamini-Hochberg at α=0.10
   - Multiple testing adjustment
   - **Reason:** Statistical significance conclusions depend on exact procedure

5. **Random Seed** (`config.py`)
   - `RANDOM_SEED = 42`
   - **Reason:** Bootstrap results must be exactly reproducible

6. **Event Window Standard** (`config.py`)
   - `EVENT_WINDOW_BEFORE = 3`
   - `EVENT_WINDOW_AFTER = 3`
   - **Reason:** Published results use ±3 day windows

**CAN CHANGE (with verification):**

1. **Output formatting** (`publication_outputs.py`, `create_*_figures.py`)
   - LaTeX table styling
   - Figure aesthetics
   - CSV export formats
   - **Verification:** Visual inspection, no effect on numerical results

2. **Robustness checks** (`robustness_*.py`)
   - Additional tests
   - Alternative parameterizations
   - **Verification:** New tests don't contradict published results

3. **Performance optimizations** (`*_optimized.py`)
   - Vectorization
   - Parallelization
   - **Verification:** Numerical results match within tolerance (rtol=1e-6)

### Critical Functions That Can't Change

**DO NOT MODIFY (function signatures OR implementation logic):**

```python
# data_preparation.py
def create_event_dummies(self, dates: pd.DatetimeIndex, events_df: pd.DataFrame) -> pd.DataFrame
def load_gdelt_sentiment(self) -> pd.DataFrame
def winsorize_returns(self, returns: pd.Series, window: int = 30, n_std: float = 5.0) -> pd.Series

# tarch_x_manual.py
def _variance_recursion(self, params: np.ndarray) -> Tuple[np.ndarray, np.ndarray]
def _log_likelihood(self, params: np.ndarray) -> float
def estimate(self, method: str = 'SLSQP', max_iter: int = 1000) -> TARCHXResults

# event_impact_analysis.py
def apply_fdr_correction(self) -> pd.DataFrame
def test_infrastructure_vs_regulatory(self) -> Dict

# garch_models.py
def _prepare_exogenous_variables(self, use_individual_events: bool, include_sentiment: bool) -> pd.DataFrame
```

**CAN MODIFY (with extensive testing):**

```python
# publication_outputs.py
def generate_latex_model_comparison_table(self) -> str
def plot_volatility_around_events(self, major_events: List[Tuple]) -> None

# robustness_checks.py
def run_placebo_test(self, n_placebos: int = 1000) -> Dict
def check_event_window_sensitivity(self, windows: List[int] = [2, 3, 5]) -> Dict
```

### Refactor Action Items

**Step 1: File Organization (No Code Changes)**
- [ ] Create subdirectories: `core/`, `analysis/`, `robustness/`, `inference/`, `publication/`, `utils/`, `scripts/`, `exploratory/`, `legacy/`
- [ ] Move files to appropriate subdirectories
- [ ] Update `__init__.py` files with exports
- [ ] **Verify:** `python -m pytest tests/` passes

**Step 2: Import Path Updates**
- [ ] Update all imports to use new paths
- [ ] Update `run_event_study_analysis.py` imports
- [ ] Update test imports
- [ ] **Verify:** `python code/scripts/run_event_study_analysis.py` runs successfully

**Step 3: Remove Redundancies**
- [ ] Move templates to `legacy/`
- [ ] Move one-time fixes to `legacy/`
- [ ] Move exploratory scripts to `exploratory/`
- [ ] Document what each legacy file did (in `legacy/README.md`)
- [ ] **Verify:** No imports reference removed files

**Step 4: Configuration Refactor**
- [ ] Split `config.py` into `config.py`, `special_events.py`, `figure_config.py`
- [ ] Update imports
- [ ] **Verify:** Numerical results unchanged (compare CSVs)

**Step 5: Documentation Updates**
- [ ] Update all `DOCS_*.md` files with new paths
- [ ] Update `CLAUDE.md` with new structure
- [ ] Update `README.md` with refactored architecture
- [ ] Create `legacy/README.md` explaining removed files

**Step 6: Final Verification**
- [ ] Run full analysis pipeline: `python code/scripts/run_event_study_analysis.py`
- [ ] Compare outputs with pre-refactor baseline
- [ ] Run all tests: `pytest tests/ -v`
- [ ] Generate publication outputs: `python code/publication/create_heterogeneity_figures.py`
- [ ] Visual inspection of figures (no changes to content)
- [ ] Git commit with message: "Refactor: Organize codebase by concern (no logic changes)"

---

## TESTING STRATEGY

### Verification Checklist

**After ANY changes to core modules, verify:**

1. **Numerical Reproducibility**
   ```python
   # Compare pre-refactor vs post-refactor outputs
   import pandas as pd
   import numpy as np

   old_results = pd.read_csv('outputs_baseline/analysis_results/hypothesis_test_results.csv')
   new_results = pd.read_csv('outputs/analysis_results/hypothesis_test_results.csv')

   # Check all numerical columns match within tolerance
   for col in ['Infrastructure_mean', 'Regulatory_mean', 't_statistic', 't_pvalue']:
       assert np.allclose(old_results[col], new_results[col], rtol=1e-6, atol=1e-8)
   ```

2. **Event Dummy Integrity**
   ```python
   # Verify event overlap handling
   btc_data = load_and_prepare_single_crypto('btc')

   # Check SEC composite dummy
   assert 'D_SEC_enforcement_2023' in btc_data.columns
   assert 'D_event_31' not in btc_data.columns  # Should be absorbed
   assert 'D_event_32' not in btc_data.columns

   # Check EIP/Polygon overlap
   overlap_date = pd.Timestamp('2021-08-07', tz='UTC')
   assert btc_data.loc[overlap_date, 'D_event_17'] == 0.5
   assert btc_data.loc[overlap_date, 'D_event_18'] == 0.5
   ```

3. **Model Convergence**
   ```bash
   # All models should converge
   python -c "
   from code.scripts.run_event_study_analysis import main
   results = main(run_robustness=False, run_bootstrap=False, generate_publication=False)
   model_results = results['model_results']

   for crypto, models in model_results.items():
       assert models['GARCH(1,1)'].convergence, f'{crypto} GARCH failed'
       assert models['TARCH(1,1)'].convergence, f'{crypto} TARCH failed'
       assert models['TARCH-X'].convergence, f'{crypto} TARCH-X failed'
   "
   ```

4. **Output File Integrity**
   ```bash
   # Check all expected outputs generated
   ls outputs/analysis_results/hypothesis_test_results.csv
   ls outputs/analysis_results/fdr_corrected_pvalues.csv
   ls outputs/publication/latex/model_comparison.tex
   ls publication_figures/figure1_heterogeneity.pdf
   ```

### Test Cases

**Critical Tests (MUST PASS):**

1. **Event Overlap Handling** (`tests/test_edge_cases.py`)
   - SEC Twin Suits composite dummy
   - EIP/Polygon 0.5 adjustment
   - Bybit/SEC window truncation

2. **GDELT Sentiment Decomposition** (`tests/test_data_preparation.py`)
   - 52-week z-score normalization
   - Theme decomposition
   - Weekly → daily forward-fill

3. **TARCH-X Estimation** (`tests/test_garch_models.py`)
   - Variance recursion correctness
   - Parameter convergence
   - Residual properties (no autocorrelation)

4. **FDR Correction** (`tests/test_statistical_methods.py`)
   - Benjamini-Hochberg procedure
   - Rejection flags
   - P-value ordering preserved

5. **End-to-End Pipeline** (`tests/test_integration.py`)
   - Full analysis runs without errors
   - All outputs generated
   - Numerical results match baseline

**Robustness Tests (SHOULD PASS):**

1. **Placebo Test** (`tests/test_robustness.py`)
   - Observed > 95th percentile
   - P-values < 0.05

2. **Window Sensitivity** (`tests/test_robustness.py`)
   - Sign stability > 90%
   - Ranking stability > 0.90

3. **Bootstrap Convergence** (`tests/test_bootstrap.py`)
   - Convergence rate > 80%
   - Confidence intervals sensible

### Expected Test Outputs

**Baseline Values (Pre-Refactor):**

```python
BASELINE_VALUES = {
    'infrastructure_mean': 0.0047,  # Mean infrastructure event coefficient
    'regulatory_mean': 0.0021,      # Mean regulatory event coefficient
    't_statistic': 0.003,           # T-test statistic (near zero, p=0.997)
    't_pvalue': 0.997,              # T-test p-value (null result)
    'cohens_d': 0.002,              # Effect size (negligible)

    'bnb_mean_effect': 0.00947,     # BNB mean event sensitivity (0.947%)
    'ltc_mean_effect': -0.00027,    # LTC mean event sensitivity (-0.027%)
    'heterogeneity_ratio': 35.07,   # BNB / |LTC| ratio

    'sign_stability': 0.94,         # 94% sign stability across windows
    'ranking_stability': 0.97,      # Spearman ρ = 0.97 across windows

    'placebo_percentile': 98.5,     # Observed at 98.5th percentile
    'placebo_pvalue': 0.015,        # P(placebo ≥ observed)
}
```

**Tolerance Levels:**

```python
TOLERANCES = {
    'coefficients': {'rtol': 1e-6, 'atol': 1e-8},  # Coefficient estimates
    'pvalues': {'rtol': 1e-4, 'atol': 1e-6},       # P-values
    'aic_bic': {'rtol': 1e-3, 'atol': 1e-2},       # Information criteria
    'percentiles': {'rtol': 1e-2, 'atol': 0.01},   # Percentile rankings
}
```

---

## DO NOT CHANGE

### Immutable Components

**These MUST remain identical for reproducibility:**

1. **Event Dates** (`data/events.csv`)
   - 50 events with exact dates
   - Event type classifications (Infrastructure/Regulatory)

2. **Event Window Definitions** (`config.py`)
   - `EVENT_WINDOW_BEFORE = 3`
   - `EVENT_WINDOW_AFTER = 3`

3. **Special Event Handling** (`data_preparation.py`)
   - SEC Twin Suits composite dummy (events 31, 32)
   - EIP/Polygon overlap adjustment (events 17, 18)
   - Bybit/SEC truncation (events 43, 44)

4. **GDELT Normalization** (`data_preparation.py`)
   - 52-week rolling window
   - 26-week minimum periods
   - Theme decomposition formula

5. **Winsorization Parameters** (`config.py`)
   - `WINSORIZATION_STD = 5.0`
   - `WINSORIZATION_WINDOW = 30`

6. **TARCH-X Model Specification** (`tarch_x_manual.py`)
   - Variance recursion algorithm
   - Student-t log-likelihood
   - Parameter bounds
   - SLSQP optimization

7. **FDR Settings** (`event_impact_analysis.py`)
   - Benjamini-Hochberg method
   - Alpha level = 0.10

8. **Random Seed** (`config.py`)
   - `RANDOM_SEED = 42`

### Allowed Modifications

**These CAN be changed (with verification):**

1. **Figure Aesthetics**
   - Colors, fonts, line widths
   - Layout, spacing, annotations
   - **Verify:** Visual inspection only

2. **LaTeX Table Formatting**
   - Column widths, alignment
   - Caption text, table notes
   - **Verify:** Numerical values unchanged

3. **Output File Paths**
   - Directory structure
   - File naming conventions
   - **Verify:** All outputs still generated

4. **Performance Optimizations**
   - Vectorization, parallelization
   - Caching, memoization
   - **Verify:** Numerical results match within tolerance

5. **Additional Robustness Checks**
   - New tests, alternative parameterizations
   - **Verify:** New tests don't contradict published results

6. **Documentation**
   - Comments, docstrings
   - README files, markdown docs
   - **Verify:** No code logic changes

---

## SUMMARY

### Key Takeaways

1. **7-Stage Pipeline:** Raw CSVs → Data Prep → TARCH-X → Event Analysis → Hypothesis Tests → Robustness → Publication

2. **Critical Innovation:** Event overlap handling prevents double-counting (SEC Twin Suits, EIP/Polygon, Bybit/SEC)

3. **Novel Methodology:** GDELT sentiment decomposition weighted by article type proportions (52-week z-score + theme split)

4. **Custom Implementation:** Manual TARCH-X with variance-exogenous variables (arch package doesn't support this properly)

5. **Main Finding:** 97.4 percentage point spread in event sensitivity (BNB: 0.947% vs LTC: -0.027%)

6. **Null Result:** Infrastructure vs Regulatory events indistinguishable (p=0.997)

7. **Robust:** 94% sign stability across windows, perfect ranking stability (ρ=1.00), observed > 95th percentile in placebo test

### Refactor Priorities

**DO FIRST (Low Risk):**
1. Organize files into subdirectories (no code changes)
2. Remove clear redundancies (templates, one-time fixes)
3. Update documentation with new paths

**DO NEXT (Medium Risk):**
1. Split configuration into separate concerns
2. Extract event dummy logic to separate module
3. Update imports across codebase

**DO LAST (High Risk):**
1. Refactor TARCH-X implementation into submodules
2. Consolidate robustness checks
3. Performance optimizations

**DO NOT DO:**
1. Change event overlap handling logic
2. Change GDELT sentiment decomposition
3. Change TARCH-X variance recursion
4. Change FDR correction parameters
5. Change random seed
6. Change event window definitions

### Verification Steps

**After EVERY change:**
1. Run `pytest tests/ -v` (all tests pass)
2. Run `python code/scripts/run_event_study_analysis.py`
3. Compare numerical outputs with baseline (rtol=1e-6)
4. Visual inspection of figures (no content changes)
5. Git commit with descriptive message

**Before merging refactor:**
1. Full analysis pipeline runs successfully
2. All 5 documentation files updated
3. All imports work correctly
4. No broken tests
5. Baseline comparison passes
6. Code review by second person

---

**Last Updated:** October 28, 2025
**Maintainer:** Farzulla Research
**Status:** Master reference for upcoming refactor
**Next Steps:** Begin Step 1 (File Organization) of refactor action items
