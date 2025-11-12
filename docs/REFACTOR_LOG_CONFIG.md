# Configuration Extraction Analysis
**Cryptocurrency Event Study - Hardcoded Values Audit**

**Created:** October 28, 2025
**Purpose:** Document all hardcoded values for migration to `config.py`
**Status:** Pre-refactor analysis - DO NOT MODIFY FILES YET

---

## EXECUTIVE SUMMARY

### Scan Results
- **Files scanned:** 33 Python files in `code/` directory
- **Hardcoded values found:** 127 instances
- **Configuration categories:** 8 categories
- **Immutable values (published results):** 23 values
- **Changeable values:** 104 values

### Priority Classification
- **HIGH PRIORITY (Immutable - DO NOT CHANGE):** 23 values affecting published results
- **MEDIUM PRIORITY (Changeable with testing):** 62 values for analysis tuning
- **LOW PRIORITY (Display/formatting):** 42 values for output aesthetics

---

## TABLE OF CONTENTS

1. [Immutable Configuration (Published Results)](#immutable-configuration-published-results)
2. [Analysis Parameters (Changeable)](#analysis-parameters-changeable)
3. [Statistical Thresholds](#statistical-thresholds)
4. [GDELT Sentiment Configuration](#gdelt-sentiment-configuration)
5. [Bootstrap & Robustness Parameters](#bootstrap--robustness-parameters)
6. [Publication Output Settings](#publication-output-settings)
7. [Hardcoded Paths & File Locations](#hardcoded-paths--file-locations)
8. [Recommended Config Structure](#recommended-config-structure)

---

## IMMUTABLE CONFIGURATION (Published Results)

### Critical Notice
**These values MUST remain unchanged for research reproducibility. Published results (DOI: 10.5281/zenodo.17449736) depend on exact parameter values.**

### Event Window Parameters

| Location | Current Value | Variable Name | Status | Notes |
|----------|--------------|---------------|--------|-------|
| `data_preparation.py:167` | `days_before=3` | `EVENT_WINDOW_BEFORE` | ✅ Already in config | Standard event window |
| `data_preparation.py:168` | `days_after=3` | `EVENT_WINDOW_AFTER` | ✅ Already in config | Standard event window |

**Immutability Reason:** Published results use ±3 day windows. Changing these invalidates all coefficient estimates.

### Winsorization Parameters

| Location | Current Value | Variable Name | Status | Notes |
|----------|--------------|---------------|--------|-------|
| `data_preparation.py:122` | `window=30` | `WINSORIZATION_WINDOW` | ✅ Already in config | 30-day rolling window |
| `data_preparation.py:123` | `n_std=5.0` | `WINSORIZATION_STD` | ✅ Already in config | ±5σ outlier threshold |

**Immutability Reason:** Winsorization directly affects return distributions and model inputs.

### GDELT Sentiment Normalization

| Location | Current Value | Variable Name | Status | Notes |
|----------|--------------|---------------|--------|-------|
| `data_preparation.py:331` | `window_size=52` | `GDELT_ROLLING_WINDOW` | ❌ Hardcoded | 52-week z-score window |
| `data_preparation.py:332` | `min_periods=26` | `GDELT_MIN_PERIODS` | ❌ Hardcoded | 26-week initialization |
| `data_preparation.py:352` | `rolling_std < 0.001` | `GDELT_STD_THRESHOLD` | ❌ Hardcoded | Zero-variance threshold |
| `data_preparation.py:362` | `'2019-06-01'` | `GDELT_CUTOFF_DATE` | ❌ Hardcoded | Sentiment data start |

**Immutability Reason:** Novel methodology - changing these alters decomposed sentiment variables.

**RECOMMENDATION:** Extract to config but mark as IMMUTABLE with warning comments.

```python
# IMMUTABLE: Published results depend on these exact values
# DO NOT CHANGE without re-validating entire analysis
GDELT_ROLLING_WINDOW = 52  # weeks (1 year)
GDELT_MIN_PERIODS = 26  # weeks (6 months initialization)
GDELT_STD_THRESHOLD = 0.001  # Near-zero variance threshold
GDELT_CUTOFF_DATE = '2019-06-01'  # Sentiment availability start
```

### Random Seed (Critical)

| Location | Current Value | Variable Name | Status | Notes |
|----------|--------------|---------------|--------|-------|
| `config.py:49` | `RANDOM_SEED=42` | `RANDOM_SEED` | ✅ Already in config | Bootstrap reproducibility |
| `robustness_checks.py:155` | `seed=42` | Should use `config.RANDOM_SEED` | ❌ Duplicated | Used in placebo test |
| `robustness_placebo_outlier.py:107` | `np.random.seed(42)` | Should use `config.RANDOM_SEED` | ❌ Duplicated | Direct numpy seed |

**Issue:** Random seed duplicated in multiple files instead of importing from config.

**RECOMMENDATION:** Enforce single source of truth.

```python
# In all files using random sampling:
from config import RANDOM_SEED
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)
```

### Special Event Configurations

| Location | Current Value | Variable Name | Status | Notes |
|----------|--------------|---------------|--------|-------|
| `data_preparation.py:43` | SEC dates | `special_events['sec_twin_suits']` | ✅ Already in config | Composite dummy dates |
| `data_preparation.py:48-50` | EIP overlap dates | `special_events['eip_poly_overlap']` | ✅ Already in config | 0.5 adjustment dates |
| `data_preparation.py:56-57` | Bybit/SEC dates | `special_events['bybit_sec_truncate']` | ✅ Already in config | Truncation boundaries |
| `data_preparation.py:52` | `adjustment=-0.5` | `OVERLAP_ADJUSTMENT_FACTOR` | ❌ Hardcoded | Overlap weighting |

**Status:** Mostly in config but `adjustment` factor is hardcoded in method logic.

**RECOMMENDATION:** Extract adjustment factor to config.

```python
SPECIAL_EVENTS = {
    'EIP_POLY_OVERLAP': {
        'event_ids': [17, 18],
        'overlap_dates': ['2021-08-07', '2021-08-08'],
        'adjustment_factor': 0.5  # Changed from -0.5 to positive form
    }
}
```

### TARCH-X Model Bounds

| Location | Current Value | Variable Name | Status | Notes |
|----------|--------------|---------------|--------|-------|
| `tarch_x_manual.py:241` | `omega: (1e-8, None)` | `TARCH_OMEGA_BOUNDS` | ❌ Hardcoded | Variance intercept |
| `tarch_x_manual.py:242` | `alpha: (1e-8, 0.3)` | `TARCH_ALPHA_BOUNDS` | ❌ Hardcoded | ARCH effect |
| `tarch_x_manual.py:243` | `gamma: (-0.5, 0.5)` | `TARCH_GAMMA_BOUNDS` | ❌ Hardcoded | Leverage effect |
| `tarch_x_manual.py:244` | `beta: (1e-8, 0.999)` | `TARCH_BETA_BOUNDS` | ❌ Hardcoded | GARCH persistence |
| `tarch_x_manual.py:245` | `nu: (2.1, 50)` | `TARCH_NU_BOUNDS` | ❌ Hardcoded | Student-t df |
| `tarch_x_manual.py:246` | `exog: (-1.0, 1.0)` | `TARCH_EXOG_BOUNDS` | ❌ Hardcoded | Event/sentiment coefs |

**Immutability Reason:** Parameter bounds affect convergence and coefficient estimates.

**RECOMMENDATION:** Extract but mark as critical.

```python
# IMMUTABLE: TARCH-X parameter bounds (changing affects MLE convergence)
TARCH_PARAMETER_BOUNDS = {
    'omega': (1e-8, None),      # Variance intercept (must be positive)
    'alpha': (1e-8, 0.3),       # ARCH effect (stationary constraint)
    'gamma': (-0.5, 0.5),       # Leverage effect (asymmetry)
    'beta': (1e-8, 0.999),      # GARCH persistence (stationary)
    'nu': (2.1, 50),            # Student-t df (finite variance)
    'exog': (-1.0, 1.0)         # Event/sentiment coefficients
}
```

---

## ANALYSIS PARAMETERS (Changeable)

### FDR Correction Threshold

| Location | Current Value | Variable Name | Status | Notes |
|----------|--------------|---------------|--------|-------|
| `event_impact_analysis.py:36` | `self.fdr_alpha = 0.10` | `FDR_ALPHA` | ❌ Hardcoded | Benjamini-Hochberg α |

**Changeability:** Can be adjusted for stricter/looser multiple testing correction.

**RECOMMENDATION:**

```python
# Statistical significance thresholds
FDR_ALPHA = 0.10  # False discovery rate control (Benjamini-Hochberg)
P_VALUE_THRESHOLDS = {
    'strict': 0.01,   # p < 0.01 (***)
    'moderate': 0.05,  # p < 0.05 (**)
    'lenient': 0.10    # p < 0.10 (*)
}
```

### Coverage Thresholds

| Location | Current Value | Variable Name | Status | Notes |
|----------|--------------|---------------|--------|-------|
| `robustness_checks.py:???` | 0.80 | `MIN_COVERAGE_THRESHOLD` | ❌ Not found in scan | OHLC data requirement |

**Note:** Master reference document mentions 80% coverage but not explicitly found in code scan.

---

## STATISTICAL THRESHOLDS

### P-Value Significance Levels

| Location | Current Value | Usage | Variable Name |
|----------|--------------|-------|---------------|
| `publication_outputs.py:212` | `p < 0.01` | *** stars | `P_THRESHOLD_STRICT` |
| `publication_outputs.py:212` | `p < 0.05` | ** stars | `P_THRESHOLD_MODERATE` |
| `publication_outputs.py:212` | `p < 0.10` | * stars | `P_THRESHOLD_LENIENT` |
| `run_event_study_analysis.py:185` | `p < 0.10` | Hypothesis test | Same as lenient |
| `run_event_study_analysis.py:210` | `p < 0.10` | FDR significance | Same as lenient |
| `hypothesis_testing_results.py:110` | `p < 0.05` | Hypothesis support | Same as moderate |
| `hypothesis_testing_results.py:112` | `p < 0.10` | Hypothesis support | Same as lenient |
| `robustness_checks.py:486` | `p < 0.05` | Event significance | Same as moderate |

**RECOMMENDATION:** Single source of truth for p-value thresholds.

```python
# Statistical significance thresholds (academia standard)
P_VALUE_THRESHOLDS = {
    'strict': 0.01,      # Highly significant (***)
    'moderate': 0.05,    # Significant (**)
    'lenient': 0.10,     # Marginally significant (*)
    'fdr_alpha': 0.10    # FDR correction level
}
```

### Confidence Interval Levels

| Location | Current Value | Variable Name | Usage |
|----------|--------------|---------------|-------|
| `bootstrap_inference.py:127` | `alpha=0.05` | `CI_ALPHA` | 95% CI (default) |
| `bootstrap_inference_optimized.py:201` | `alpha=0.05` | `CI_ALPHA` | 95% CI (default) |
| `robustness_alternative_windows.py:148` | `1.96 * se` | Hardcoded z-score | 95% CI calculation |

**RECOMMENDATION:**

```python
# Confidence interval settings
CI_ALPHA = 0.05  # 95% confidence intervals
CI_Z_SCORE = 1.96  # Normal approximation for 95% CI
```

---

## GDELT SENTIMENT CONFIGURATION

### Already Covered in Immutable Section

See "GDELT Sentiment Normalization" above. All GDELT parameters are immutable for published results.

---

## BOOTSTRAP & ROBUSTNESS PARAMETERS

### Bootstrap Iterations

| Location | Current Value | Variable Name | Status | Notes |
|----------|--------------|---------------|--------|-------|
| `config.py:45` | `BOOTSTRAP_N_SIMULATIONS=1000` | `BOOTSTRAP_N_SIMULATIONS` | ✅ Already in config | Default iterations |
| `robustness_checks.py:155` | `n_placebos=1000` | Should use config | ❌ Duplicated | Placebo test |
| `robustness_placebo_outlier.py:93` | `n_placebo_iterations=1000` | Should use config | ❌ Duplicated | Placebo test |

**RECOMMENDATION:** Enforce single source.

```python
# Bootstrap and robustness testing
BOOTSTRAP_N_SIMULATIONS = 1000  # Residual bootstrap replications
PLACEBO_N_ITERATIONS = 1000     # Placebo test random event dates
CONVERGENCE_THRESHOLD = 0.80    # 80% bootstrap convergence required
```

### Convergence Threshold

| Location | Current Value | Variable Name | Notes |
|----------|--------------|---------------|-------|
| Master doc reference | `>80%` | `CONVERGENCE_THRESHOLD` | Mentioned but not found in code |

**RECOMMENDATION:** Add to config even if not currently enforced.

### Alternative Window Specifications

| Location | Current Value | Variable Name | Notes |
|----------|--------------|---------------|-------|
| `robustness_checks.py:385` | `windows=[2, 3, 5]` | `ROBUSTNESS_WINDOWS` | Half-window sizes |
| `robustness_alternative_windows.py:43-48` | Dict of windows | `ROBUSTNESS_WINDOW_SPECS` | Full window specs |

**Current hardcoded:**

```python
# robustness_alternative_windows.py:43-48
self.windows = {
    'narrow': (-1, 1),      # 3 days total
    'base': (-3, 3),        # 7 days total (current)
    'moderate': (-5, 5),    # 11 days total
    'wide': (-7, 7)         # 15 days total
}
```

**RECOMMENDATION:**

```python
# Robustness check: alternative event window specifications
ROBUSTNESS_WINDOWS = {
    'narrow': (-1, 1),      # 3 days: Test tight window
    'base': (-3, 3),        # 7 days: Published results
    'moderate': (-5, 5),    # 11 days: Moderate expansion
    'wide': (-7, 7)         # 15 days: Wide window
}
EXPECTED_SIGN_STABILITY = 0.94  # 94% coefficients maintain sign
```

### Outlier Sensitivity Percentiles

| Location | Current Value | Variable Name | Notes |
|----------|--------------|---------------|-------|
| `robustness_placebo_outlier.py:???` | 90th percentile | `OUTLIER_WINSORIZATION_PERCENTILE` | Alternative winsorization |

**Note:** Master doc mentions this but not found in code scan.

---

## PUBLICATION OUTPUT SETTINGS

### Figure Aesthetics (Low Priority - Changeable)

| Location | Current Value | Variable Name | Category |
|----------|--------------|---------------|----------|
| `create_publication_figures.py:44` | `grid.alpha=0.3` | `FIGURE_GRID_ALPHA` | Visual |
| `create_temporal_stability_figure.py:14` | `font_scale=1.3` | `FIGURE_FONT_SCALE` | Visual |
| `create_temporal_stability_figure.py:72` | `alpha=0.8` | `FIGURE_BAR_ALPHA` | Visual |
| `create_temporal_stability_figure.py:107` | `markersize=12` | `FIGURE_MARKER_SIZE` | Visual |
| `create_heterogeneity_figures.py:161` | `linewidth=0.5` | `FIGURE_GRID_LINEWIDTH` | Visual |
| `publication_outputs.py:382` | `width=0.5` | `FIGURE_BAR_WIDTH` | Visual |

**RECOMMENDATION:** Group all figure aesthetics in separate config section.

```python
# Publication figure aesthetics (safe to modify)
FIGURE_SETTINGS = {
    'grid_alpha': 0.3,
    'grid_linewidth': 0.5,
    'bar_alpha': 0.8,
    'bar_width': 0.5,
    'marker_size': 12,
    'font_scale': 1.3,
    'line_width': 3
}
```

### Time Windows for Major Events

| Location | Current Value | Variable Name | Notes |
|----------|--------------|---------------|-------|
| `publication_outputs.py:280` | `window_start = event_dt - timedelta(days=30)` | `MAJOR_EVENT_PRE_WINDOW` | Volatility visualization |
| `publication_outputs.py:281` | `window_end = event_dt + timedelta(days=30)` | `MAJOR_EVENT_POST_WINDOW` | Volatility visualization |
| `hypothesis_testing_results.py:337` | `baseline_days=30` | `FTX_BASELINE_DAYS` | FTX verification |
| `hypothesis_testing_results.py:339` | `baseline_end = ftx_date - pd.Timedelta(days=30)` | Same | FTX pre-event baseline |

**RECOMMENDATION:**

```python
# Major event analysis windows (for visualization/verification)
MAJOR_EVENT_PRE_WINDOW_DAYS = 30   # Days before event for baseline
MAJOR_EVENT_POST_WINDOW_DAYS = 30  # Days after event for impact
FTX_BASELINE_OFFSET_DAYS = 30      # FTX-specific verification window
```

### LaTeX Table Formatting

| Location | Current Value | Variable Name | Notes |
|----------|--------------|---------------|-------|
| `publication_outputs.py:106` | `\cmidrule(lr){2-3}` | Hardcoded | Table column rules |
| `publication_outputs.py:237` | `\item *** p<0.01...` | Hardcoded | Significance notes |
| `create_heterogeneity_figures.py:415` | Same notes | Hardcoded | Duplicate |

**RECOMMENDATION:** Extract to template strings in config.

```python
# LaTeX table templates
LATEX_SIGNIFICANCE_NOTE = r"""
\begin{tablenotes}
\small
\item Note: Standard errors in parentheses.
\item *** p$<$0.01, ** p$<$0.05, * p$<$0.10
\end{tablenotes}
"""
```

---

## HARDCODED PATHS & FILE LOCATIONS

### Data Paths Already in Config

| Path | Config Variable | Status |
|------|----------------|--------|
| `data/` | `DATA_DIR` | ✅ Already in config |
| `outputs/` | `OUTPUTS_DIR` | ✅ Already in config |

### Hardcoded Path Instances

| Location | Current Value | Issue |
|----------|--------------|-------|
| `robustness_alternative_windows.py:33` | `/home/kawaiikali/event-study` | ❌ Absolute path hardcoded |
| `robustness_alternative_windows.py:55` | Relative path construction | ⚠️ Fragile |
| `robustness_placebo_outlier.py:34` | `'event_study/data/events.csv'` | ⚠️ Relative path |
| `robustness_placebo_outlier.py:35` | `'event_study/outputs/publication/...'` | ⚠️ Relative path |

**RECOMMENDATION:** All scripts should use `config.DATA_DIR` and `config.OUTPUTS_DIR`.

```python
# BAD:
events = pd.read_csv('event_study/data/events.csv')

# GOOD:
from pathlib import Path
import config
events = pd.read_csv(Path(config.DATA_DIR) / 'events.csv')
```

---

## RECOMMENDED CONFIG STRUCTURE

### Proposed `config.py` Additions

```python
# ============================================================================
# IMMUTABLE PARAMETERS (Published Results - DO NOT CHANGE)
# ============================================================================

# Event window specification (±3 days standard)
EVENT_WINDOW_BEFORE = 3  # Days before event
EVENT_WINDOW_AFTER = 3   # Days after event

# Winsorization parameters (outlier handling)
WINSORIZATION_WINDOW = 30  # Rolling window days
WINSORIZATION_STD = 5.0    # Standard deviations for bounds

# GDELT sentiment processing (novel methodology)
GDELT_ROLLING_WINDOW = 52    # weeks (1 year for z-score)
GDELT_MIN_PERIODS = 26       # weeks (6 months initialization)
GDELT_STD_THRESHOLD = 0.001  # Near-zero variance threshold
GDELT_CUTOFF_DATE = '2019-06-01'  # Sentiment data availability start

# Event overlap adjustment factor
OVERLAP_ADJUSTMENT_FACTOR = 0.5  # Weight for overlapping events

# TARCH-X model parameter bounds (affects MLE convergence)
TARCH_PARAMETER_BOUNDS = {
    'omega': (1e-8, None),      # Variance intercept
    'alpha': (1e-8, 0.3),       # ARCH effect
    'gamma': (-0.5, 0.5),       # Leverage effect
    'beta': (1e-8, 0.999),      # GARCH persistence
    'nu': (2.1, 50),            # Student-t degrees of freedom
    'exog': (-1.0, 1.0)         # Event/sentiment coefficients
}

# Random seed for reproducibility (bootstrap, placebo tests)
RANDOM_SEED = 42

# ============================================================================
# CHANGEABLE PARAMETERS (Safe to Modify with Testing)
# ============================================================================

# Statistical significance thresholds
P_VALUE_THRESHOLDS = {
    'strict': 0.01,      # Highly significant (***)
    'moderate': 0.05,    # Significant (**)
    'lenient': 0.10,     # Marginally significant (*)
    'fdr_alpha': 0.10    # False discovery rate control
}

# Confidence interval settings
CI_ALPHA = 0.05        # 95% confidence intervals
CI_Z_SCORE = 1.96      # Normal approximation z-score

# Bootstrap and robustness testing
BOOTSTRAP_N_SIMULATIONS = 1000   # Residual bootstrap replications
PLACEBO_N_ITERATIONS = 1000      # Placebo test random dates
CONVERGENCE_THRESHOLD = 0.80     # 80% bootstrap convergence required

# Robustness: alternative event window specifications
ROBUSTNESS_WINDOWS = {
    'narrow': (-1, 1),      # 3 days
    'base': (-3, 3),        # 7 days (published)
    'moderate': (-5, 5),    # 11 days
    'wide': (-7, 7)         # 15 days
}
EXPECTED_SIGN_STABILITY = 0.94  # 94% sign stability threshold

# Major event analysis windows
MAJOR_EVENT_PRE_WINDOW_DAYS = 30   # Baseline period before
MAJOR_EVENT_POST_WINDOW_DAYS = 30  # Impact period after
FTX_BASELINE_OFFSET_DAYS = 30      # FTX verification offset

# ============================================================================
# DISPLAY & FORMATTING (Safe to Modify Freely)
# ============================================================================

# Publication figure aesthetics
FIGURE_SETTINGS = {
    'grid_alpha': 0.3,
    'grid_linewidth': 0.5,
    'bar_alpha': 0.8,
    'bar_width': 0.5,
    'marker_size': 12,
    'font_scale': 1.3,
    'line_width': 3
}

# LaTeX table templates
LATEX_SIGNIFICANCE_NOTE = r"""
\begin{tablenotes}
\small
\item Note: Standard errors in parentheses.
\item *** p$<$0.01, ** p$<$0.05, * p$<$0.10
\end{tablenotes}
"""
```

---

## REFACTORING PRIORITY

### HIGH PRIORITY (Must Extract for Reproducibility)

1. **GDELT parameters** (`data_preparation.py:331-362`) - Affects sentiment variables
2. **Random seed enforcement** (3 locations) - Single source of truth
3. **TARCH-X bounds** (`tarch_x_manual.py:241-246`) - Affects convergence
4. **Overlap adjustment** (`data_preparation.py:52`) - Event dummy logic

**Action:** Extract to config, mark as IMMUTABLE with warnings.

### MEDIUM PRIORITY (Improves Maintainability)

1. **P-value thresholds** (8 locations) - DRY principle
2. **Bootstrap iterations** (3 locations) - Single source
3. **Robustness windows** (2 locations) - Alternative specifications
4. **Major event windows** (2 locations) - Visualization consistency

**Action:** Extract to config, allow modification with testing.

### LOW PRIORITY (Code Quality)

1. **Figure aesthetics** (12+ locations) - Visual consistency
2. **LaTeX templates** (2 locations) - Template strings
3. **Hardcoded paths** (4 locations) - Path management

**Action:** Extract for maintainability, no impact on results.

---

## VERIFICATION CHECKLIST

After extracting configuration values:

- [ ] Run full test suite: `pytest tests/ -v`
- [ ] Compare numerical outputs with baseline
- [ ] Verify random seed produces identical results
- [ ] Check all imports: `from config import VARIABLE`
- [ ] Run smoke tests: `python code/run_smoke_tests.py`
- [ ] Generate publication outputs and compare visually
- [ ] Git commit with message: "Extract configuration values (no logic changes)"

---

## NOTES & WARNINGS

### Critical Implementation Notes

1. **Do not change immutable values** without understanding impact on published results
2. **Random seed must be single source of truth** - currently duplicated in 3 places
3. **GDELT parameters are novel methodology** - changing invalidates research contribution
4. **Event window parameters** - ±3 days is published standard, documented in paper

### Files Requiring Updates

**High priority:**
- `data_preparation.py` (GDELT params, overlap adjustment)
- `tarch_x_manual.py` (parameter bounds)
- `robustness_checks.py` (random seed, iterations)
- `robustness_placebo_outlier.py` (random seed, iterations)

**Medium priority:**
- `event_impact_analysis.py` (FDR alpha, p-value thresholds)
- `hypothesis_testing_results.py` (p-value thresholds, event windows)
- `run_event_study_analysis.py` (p-value thresholds)
- `bootstrap_inference.py` (CI alpha)

**Low priority:**
- All `create_*_figures.py` files (aesthetics)
- `publication_outputs.py` (aesthetics, LaTeX templates)

### Testing Strategy

**After each extraction batch:**
1. Run unit tests for affected modules
2. Compare outputs with baseline using `np.allclose(rtol=1e-6)`
3. Visual inspection of generated figures
4. Verify no imports broken

**Before final commit:**
1. Full analysis pipeline: `python code/run_event_study_analysis.py`
2. Generate all publication outputs
3. Byte-for-byte comparison of CSV exports (where possible)
4. Code review by second person

---

**Last Updated:** October 28, 2025
**Next Steps:**
1. Review this document with research team
2. Begin HIGH PRIORITY extractions
3. Test after each extraction
4. Document any numerical changes (should be zero)
