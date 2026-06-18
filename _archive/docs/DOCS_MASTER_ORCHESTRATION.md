# Master Orchestration Documentation

**Module:** Complete Execution Pipeline
**Files:**
- `code/run_event_study_analysis.py` - Main execution script
- `code/config.py` - Configuration settings
- `code/__init__.py` - Package initialization

**Last Updated:** 2025-10-28

---

## Overview

The cryptocurrency event study implements a **7-stage pipeline** that transforms raw price data through econometric models into publication-ready academic outputs. The `run_event_study_analysis.py` script orchestrates all modules in the correct dependency order.

### Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      RAW INPUTS (data/)                          │
│  • btc.csv, eth.csv, xrp.csv, bnb.csv, ltc.csv, ada.csv         │
│  • events.csv (infrastructure/regulatory categorization)         │
│  • gdelt.csv (sentiment signals)                                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ STAGE 1: DATA PREPARATION
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│              DataPreparation.prepare_crypto_data()               │
│  • Align all data to UTC timestamps                             │
│  • Calculate log returns                                         │
│  • Winsorize outliers (5σ, 30-day rolling window)              │
│  • Create 7-day event windows with special case handling        │
│  • Merge sentiment controls (GDeltToneDelta)                    │
│  Outputs: 6 DataFrames with returns + D_infra/D_reg + sentiment │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ STAGE 2: MODEL ESTIMATION
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│          estimate_models_for_all_cryptos(crypto_data)            │
│  For each cryptocurrency, estimate 3 models:                     │
│  1. GARCH(1,1) - Baseline volatility model                      │
│  2. TARCH(1,1) - Adds leverage effect (γ parameter)            │
│  3. TARCH-X - Adds event dummies to variance equation           │
│                                                                  │
│  Model Specification (TARCH-X):                                 │
│    r_t = μ + ε_t                                                │
│    σ²_t = ω + αε²_{t-1} + γI_{t-1}ε²_{t-1} + βσ²_{t-1}        │
│           + δ_infra·D_infra_t + δ_reg·D_reg_t                  │
│           + δ_sent·GDeltToneDelta_t                             │
│                                                                  │
│  Outputs: ModelResults objects with:                            │
│  • Parameters (ω, α, β, γ, δ_infra, δ_reg, δ_sent)            │
│  • Standard errors & p-values                                   │
│  • AIC/BIC for model comparison                                 │
│  • Convergence status & fitted volatility series                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ STAGE 3: HYPOTHESIS TESTING
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│          run_complete_analysis(model_results)                    │
│                                                                  │
│  PRIMARY HYPOTHESIS TEST:                                       │
│  H₀: δ_infra = δ_reg (equal volatility impact)                 │
│  H₁: δ_infra > δ_reg (infrastructure has larger impact)        │
│                                                                  │
│  Statistical Methods:                                           │
│  1. Paired t-test (infrastructure vs regulatory effects)        │
│  2. Inverse-variance weighting (precision-weighted meta-effect) │
│  3. FDR correction (Benjamini-Hochberg at α=0.10)              │
│  4. By-cryptocurrency heterogeneity analysis                    │
│                                                                  │
│  Outputs: Dictionary containing:                                │
│  • hypothesis_test: {infrastructure, regulatory, t_test}        │
│  • fdr_correction: DataFrame with adjusted p-values             │
│  • inverse_variance_weighted: precision-weighted effects        │
│  • by_crypto: Per-cryptocurrency analysis                       │
│  • publication_table: LaTeX-ready summary table                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ STAGE 4: RESULTS EXPORT
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│              save_results_to_csv(results, output_dir)            │
│  Exports to outputs/analysis_results/:                          │
│  • hypothesis_test_results.csv                                  │
│  • fdr_corrected_pvalues.csv                                    │
│  • inverse_variance_weighted.csv                                │
│  • analysis_by_crypto.csv                                       │
│  • publication_table.csv                                        │
│  • model_parameters/{crypto}_parameters.json                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ STAGE 5: ROBUSTNESS CHECKS (Optional)
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│         run_robustness_checks(cryptos, run_bootstrap)            │
│  Tests sensitivity to methodological choices:                    │
│  • Placebo test (random event dates, expect null effects)       │
│  • Alternative winsorization thresholds (3σ, 5σ, 7σ)          │
│  • Event window sensitivity (3-day vs 7-day windows)           │
│  • Outlier exclusion (compare with/without extreme events)      │
│  • Bootstrap inference (if run_bootstrap=True)                  │
│                                                                  │
│  Outputs to outputs/analysis_results/robustness/:               │
│  • placebo_test.csv                                             │
│  • winsorization_comparison.csv                                 │
│  • event_window_sensitivity.csv (from robustness modules)       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ STAGE 6: BOOTSTRAP INFERENCE (Optional)
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│    run_bootstrap_analysis(returns, model_type, n_bootstrap)     │
│  Nonparametric inference via residual resampling:               │
│  • Generate 500+ bootstrap samples                              │
│  • Re-estimate TARCH-X on each sample                           │
│  • Construct 90% confidence intervals for δ_infra, δ_reg       │
│  • Validate asymptotic standard errors                          │
│                                                                  │
│  Outputs: bootstrap_confidence_intervals.csv                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ STAGE 7: PUBLICATION OUTPUTS (Optional)
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│    generate_publication_outputs(models, analysis, data)          │
│  Creates academic journal-ready materials:                       │
│                                                                  │
│  LaTeX Tables (outputs/tables/):                                │
│  • Table 1: Descriptive statistics                              │
│  • Table 2: GARCH model comparison (AIC/BIC)                    │
│  • Table 3: TARCH-X event coefficients with significance        │
│  • Table 4: Hypothesis test results                             │
│  • Table 5: Robustness checks summary                           │
│                                                                  │
│  Figures (outputs/figures/):                                    │
│  • Figure 1: Price & volatility time series                     │
│  • Figure 2: Event impacts bar chart (infrastructure vs reg)    │
│  • Figure 3: Residual diagnostics (QQ plots, ACF)              │
│  • Figure 4: Heterogeneity across cryptocurrencies              │
│                                                                  │
│  CSV Exports (outputs/publication/):                            │
│  • All tables in CSV format for data availability               │
│  • Replication data files                                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Execution Modes

### 1. Standard Analysis (Fastest)

```python
python code/run_event_study_analysis.py
```

**Default settings:**
- `run_robustness=False` - Skip robustness checks
- `run_bootstrap=False` - Skip bootstrap inference
- `generate_publication=True` - Generate tables/figures

**Execution time:** ~5-10 minutes
**Outputs:** Core results + publication materials

### 2. Full Analysis (Complete)

```python
# Edit run_event_study_analysis.py, line 333-337:
results = main(
    run_robustness=True,
    run_bootstrap=True,
    generate_publication=True
)
```

**Execution time:** ~30-60 minutes
**Outputs:** All results + robustness + bootstrap + publication

### 3. Quick Hypothesis Test Only

```python
# Edit run_event_study_analysis.py, line 333-337:
results = main(
    run_robustness=False,
    run_bootstrap=False,
    generate_publication=False
)
```

**Execution time:** ~3-5 minutes
**Outputs:** Hypothesis test results only

---

## Configuration System

### Environment Variables (.env file)

The `config.py` module supports customization via `.env`:

```bash
# Data locations
DATA_DIR=/path/to/data
OUTPUTS_DIR=/path/to/outputs

# API settings
COINGECKO_API_KEY=your_api_key_here
COINGECKO_RATE_LIMIT=1.2

# Analysis parameters
EVENT_WINDOW_BEFORE=3
EVENT_WINDOW_AFTER=3
WINSORIZATION_STD=5
WINSORIZATION_WINDOW=30

# Model parameters
GARCH_P=1
GARCH_Q=1
BOOTSTRAP_N_SIMULATIONS=1000

# Reproducibility (CRITICAL for journal submission)
RANDOM_SEED=42

# Date range
ANALYSIS_START_DATE=2019-01-01
ANALYSIS_END_DATE=2025-08-31

# Logging
LOG_LEVEL=INFO
LOG_FILE=/path/to/event_study.log
```

### Default Configuration

If no `.env` file exists, defaults from `config.py`:

```python
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
OUTPUTS_DIR = BASE_DIR / 'outputs'
RANDOM_SEED = 42
CRYPTOCURRENCIES = ['btc', 'eth', 'xrp', 'bnb', 'ltc', 'ada']
```

### Special Event Configurations

The `config.py` defines edge cases requiring custom handling:

**1. SEC Twin Suits (2023-06-05 and 2023-06-06):**
- Events 31 (Coinbase) and 32 (Binance) filed on consecutive days
- Combined into single composite dummy `D_SEC_enforcement_2023`
- Window: 2023-06-02 to 2023-06-09 (7 days)

**2. EIP-1559/Polygon Overlap (2021-08-05 and 2021-08-07):**
- Events 17 (EIP-1559) and 18 (Polygon) have overlapping windows
- Adjustment factor: 0.5 for overlapping dates
- Prevents double-counting in event window

**3. Bybit/SEC Truncation (2025-02-23 and 2025-02-27):**
- Event 43 (Bybit) ends 2025-02-23
- Event 44 (SEC) starts 2025-02-27
- 3-day gap prevents window collision

---

## Module Dependencies

### Execution Order (Critical)

The pipeline **must** execute in this order due to data dependencies:

```
config.py (loaded first by all modules)
    ↓
data_preparation.py (creates crypto_data)
    ↓
garch_models.py (requires crypto_data with returns)
    ↓
event_impact_analysis.py (requires model_results with TARCH-X parameters)
    ↓
[Optional branches - can run in parallel]
    ├─→ robustness_checks.py (requires crypto_data + model_results)
    ├─→ bootstrap_inference.py (requires returns series)
    └─→ publication_outputs.py (requires model_results + analysis_results)
```

### Import Graph

```
run_event_study_analysis.py
├── config.py (global settings)
├── data_preparation.py
│   └── config.py
├── garch_models.py
│   ├── data_preparation.py
│   └── tarch_x_manual.py (MLE optimizer)
├── event_impact_analysis.py
│   ├── data_preparation.py
│   └── garch_models.py
├── publication_outputs.py
│   └── config.py
├── robustness_checks.py
│   ├── data_preparation.py
│   ├── garch_models.py
│   └── bootstrap_inference.py
└── bootstrap_inference.py
    └── garch_models.py
```

### External Dependencies

**Required packages:**
- `pandas` - Data manipulation
- `numpy` - Numerical computations
- `scipy` - Statistical tests (t-test, FDR correction)
- `statsmodels` - FDR correction (`fdrcorrection`)
- `matplotlib` - Publication figures
- `seaborn` - Statistical visualization
- `python-dotenv` - Environment variable loading (optional)

**Optional packages:**
- `arch` - Baseline GARCH/TARCH models (if not using manual implementation)
- `pytest` - Testing framework

---

## Output Directory Structure

```
outputs/
├── analysis_results/         [STAGE 4: Main Results]
│   ├── hypothesis_test_results.csv
│   ├── fdr_corrected_pvalues.csv
│   ├── inverse_variance_weighted.csv
│   ├── analysis_by_crypto.csv
│   ├── publication_table.csv
│   ├── model_parameters/
│   │   ├── btc_parameters.json
│   │   ├── eth_parameters.json
│   │   └── ... (one per crypto)
│   └── robustness/          [STAGE 5: Robustness]
│       ├── placebo_test.csv
│       ├── winsorization_comparison.csv
│       └── event_window_sensitivity.csv
│
├── publication/             [STAGE 7: Publication Outputs]
│   ├── tables/
│   │   ├── table1_descriptive_stats.tex
│   │   ├── table2_model_comparison.tex
│   │   ├── table3_event_coefficients.tex
│   │   ├── table4_hypothesis_tests.tex
│   │   └── table5_robustness.tex
│   ├── figures/
│   │   ├── figure1_price_volatility.pdf
│   │   ├── figure2_event_impacts.pdf
│   │   ├── figure3_diagnostics.pdf
│   │   └── figure4_heterogeneity.pdf
│   └── csv_exports/
│       └── (all tables in CSV format)
│
├── figures/                 [General figures directory]
└── tables/                  [General tables directory]
```

---

## Key Execution Features

### 1. Reproducibility Controls

**Critical for journal submission:** All stochastic operations use fixed random seeds.

```python
# Line 67-71 in run_event_study_analysis.py
import random
np.random.seed(config.RANDOM_SEED)  # Default: 42
random.seed(config.RANDOM_SEED)
print(f"[REPRODUCIBILITY] Random seed set to: {config.RANDOM_SEED}")
```

**Ensures exact replication of:**
- Bootstrap resampling
- Initial parameter values in GARCH estimation
- Any Monte Carlo simulations in robustness checks

### 2. Data Validation

**Pre-flight checks before analysis starts:**

```python
# Lines 76-90
required_files = ['btc.csv', 'eth.csv', 'events.csv', 'gdelt.csv']
for file in required_files:
    if not (data_path / file).exists():
        missing_files.append(file)
        print(f"ERROR: Required file {file} not found")
```

**Prevents cascade failures** by validating inputs before expensive computations.

### 3. Graceful Degradation

**If one cryptocurrency fails, continue with others:**

```python
# Lines 107-120
for crypto in all_cryptos:
    try:
        crypto_data[crypto] = data_prep.prepare_crypto_data(...)
        print(f"[OK] Shape: {crypto_data[crypto].shape}")
    except Exception as e:
        print(f"[FAIL] Error: {str(e)}")
        # Continue with other cryptos
```

**Robustness principle:** Partial results are better than total failure.

### 4. Convergence Monitoring

**Real-time feedback on model estimation quality:**

```python
# Lines 143-153
print("Model Convergence Summary:")
for crypto in model_results:
    garch_ok = model_results[crypto]['GARCH(1,1)'].convergence
    tarch_ok = model_results[crypto]['TARCH(1,1)'].convergence
    tarchx_ok = model_results[crypto]['TARCH-X'].convergence

    print(f"{crypto.upper()} - GARCH: {'[OK]' if garch_ok else '[FAIL]'} | "
          f"TARCH: {'[OK]' if tarch_ok else '[FAIL]'} | "
          f"TARCH-X: {'[OK]' if tarchx_ok else '[FAIL]'}")
```

**Example output:**
```
BTC   - GARCH: [OK] | TARCH: [OK] | TARCH-X: [OK]
ETH   - GARCH: [OK] | TARCH: [OK] | TARCH-X: [OK]
XRP   - GARCH: [OK] | TARCH: [OK] | TARCH-X: [FAIL]
```

### 5. Structured Results Summary

**Key findings printed to console for immediate review:**

```python
# Lines 162-216
print("KEY FINDINGS SUMMARY")

# 1. Hypothesis test results
infra_mean = hyp_test['infrastructure']['mean']
reg_mean = hyp_test['regulatory']['mean']
p_val = hyp_test['t_test']['p_value']
print(f"Infrastructure mean effect: {infra_mean:.6f}")
print(f"Regulatory mean effect:     {reg_mean:.6f}")
print(f"T-test p-value: {p_val:.4f}")

# 2. Inverse-variance weighted analysis
diff = ivw['difference']
print(f"Weighted difference: {diff['value']:.6f}")
print(f"Z-statistic: {diff['z_statistic']:.4f}")

# 3. FDR correction summary
n_sig_raw = (fdr_df['p_value'] < 0.10).sum()
n_sig_fdr = fdr_df['fdr_significant'].sum()
print(f"Significant before FDR: {n_sig_raw}")
print(f"Significant after FDR:  {n_sig_fdr}")
```

---

## CLI Usage Patterns

### Standard Workflow

```bash
# 1. Ensure data files are present
ls data/
# Should show: btc.csv, eth.csv, xrp.csv, bnb.csv, ltc.csv, ada.csv, events.csv, gdelt.csv

# 2. (Optional) Configure via .env
nano .env
# Add: RANDOM_SEED=42, DATA_DIR=/path/to/data, etc.

# 3. Run main analysis
python code/run_event_study_analysis.py

# 4. Review console output for key findings
# Look for: "Infrastructure > Regulatory (significant)" message

# 5. Check outputs
ls outputs/analysis_results/
cat outputs/analysis_results/hypothesis_test_results.csv
```

### Development/Testing Workflow

```bash
# Run with different configurations
python -c "
from code.run_event_study_analysis import main
results = main(
    run_robustness=True,
    run_bootstrap=False,
    generate_publication=False
)
"

# Or modify the script directly (lines 333-337)
nano code/run_event_study_analysis.py
# Change: run_robustness=True, run_bootstrap=True
python code/run_event_study_analysis.py
```

### Minimal Test Run (Development)

```bash
# Quick validation run (3-5 minutes)
python code/run_event_study_analysis.py --quick
# Note: Requires adding argparse support to script
```

---

## Performance Characteristics

### Execution Time by Stage

**On typical hardware (4-core CPU, 16GB RAM):**

| Stage | Operation | Time | Bottleneck |
|-------|-----------|------|------------|
| 1 | Data Preparation | ~30s | CSV I/O + merging |
| 2 | GARCH Estimation | ~3-5min | BFGS optimization (TARCH-X) |
| 3 | Hypothesis Testing | ~10s | t-test + FDR correction |
| 4 | Results Export | ~5s | JSON serialization |
| 5 | Robustness Checks | ~10-15min | Multiple re-estimations |
| 6 | Bootstrap Inference | ~15-20min | 500+ bootstrap iterations |
| 7 | Publication Outputs | ~1-2min | LaTeX table generation |

**Total time:**
- **Standard run:** 5-10 minutes
- **Full analysis:** 30-60 minutes
- **With bootstrap:** 45-90 minutes

### Memory Requirements

**Peak memory usage:**
- Data preparation: ~500MB (all 6 cryptocurrencies loaded)
- Model estimation: ~1GB (storing residuals + volatility series)
- Bootstrap: ~2GB (resampling + parallel estimation)

**Recommendation:** Minimum 4GB RAM, 8GB for comfortable execution.

### Parallelization Opportunities

**Current implementation is sequential.** Potential speedups:

1. **Per-cryptocurrency parallelization:**
   - Lines 107-120: `for crypto in all_cryptos` → `multiprocessing.Pool`
   - Expected speedup: 3-5x on 6-core CPU

2. **Bootstrap parallelization:**
   - `bootstrap_inference.py` can run bootstrap iterations in parallel
   - Expected speedup: 4-8x on 8-core CPU

3. **Robustness checks parallelization:**
   - Different robustness tests are independent
   - Can run placebo/winsorization/event windows in parallel

---

## Error Handling & Debugging

### Common Errors

**1. Missing data files:**
```
ERROR: Required file btc.csv not found in /path/to/data
```
**Solution:** Ensure all 8 CSV files exist in `data/` directory.

**2. TARCH-X convergence failure:**
```
XRP - GARCH: [OK] | TARCH: [OK] | TARCH-X: [FAIL]
```
**Solution:** Check XRP data for:
- Insufficient observations (need >200 days)
- Collinearity between event dummies
- Extreme outliers causing numerical instability

**3. Empty analysis results:**
```
ERROR: No cryptocurrency data could be loaded
```
**Solution:** Check data file formats (CSV with proper columns).

### Debug Mode

Enable verbose logging by modifying `config.py`:

```python
LOG_LEVEL = 'DEBUG'
```

Or add debug prints in `run_event_study_analysis.py`:

```python
# After line 133
print(f"DEBUG: model_results keys: {model_results.keys()}")
for crypto, models in model_results.items():
    print(f"DEBUG: {crypto} models: {models.keys()}")
    if 'TARCH-X' in models:
        print(f"DEBUG: TARCH-X parameters: {models['TARCH-X'].parameters}")
```

---

## Integration with Testing Framework

### Unit Tests

Individual modules have dedicated test files:

```bash
pytest tests/test_data_preparation.py      # Test Stage 1
pytest tests/test_garch_models.py          # Test Stage 2
pytest tests/test_statistical_methods.py   # Test Stage 3
```

### Integration Test

Full pipeline validation:

```bash
pytest tests/test_integration.py
```

**What it tests:**
- End-to-end execution with synthetic data
- All modules integrate correctly
- Output files are generated
- Results pass sanity checks

### Edge Case Tests

Validate special event handling:

```bash
pytest tests/test_edge_cases.py
```

**What it tests:**
- SEC twin suits composite dummy
- EIP/Polygon overlap adjustment
- Bybit/SEC window truncation
- Missing data handling
- Convergence failure recovery

---

## Relationship to Other Documentation Layers

### How This Connects Everything

```
DOCS_MASTER_ORCHESTRATION.md (You Are Here)
│
├─→ Controls execution order of:
│   ├── DOCS_DATA_PIPELINE.md (Stage 1)
│   ├── DOCS_MODEL_ESTIMATION.md (Stage 2)
│   ├── DOCS_ANALYSIS_METHODS.md (Stage 3)
│   └── DOCS_PUBLICATION_OUTPUTS.md (Stage 7)
│
├─→ Uses settings from:
│   └── config.py
│
├─→ Generates outputs consumed by:
│   └── LaTeX manuscript (external)
│
└─→ Validated by:
    └── tests/test_integration.py
```

---

## Academic Workflow Integration

### From Raw Data to Journal Submission

**Step 1: Data Collection**
```bash
# Collect price data via CoinGecko API
python code/coingecko_fetcher.py
# Manual: Create events.csv with Infrastructure/Regulatory labels
# Manual: Download GDELT sentiment data
```

**Step 2: Run Complete Analysis**
```bash
# Full analysis with all robustness checks
python code/run_event_study_analysis.py
# Runtime: ~30-60 minutes
```

**Step 3: Review Results**
```bash
# Check hypothesis test outcome
cat outputs/analysis_results/hypothesis_test_results.csv

# Inspect model parameters
cat outputs/analysis_results/model_parameters/btc_parameters.json

# Review robustness checks
cat outputs/analysis_results/robustness/placebo_test.csv
```

**Step 4: Generate Publication Materials**
```bash
# LaTeX tables automatically created in outputs/publication/tables/
# Copy to manuscript directory:
cp outputs/publication/tables/*.tex manuscript/tables/

# Figures automatically created in outputs/publication/figures/
cp outputs/publication/figures/*.pdf manuscript/figures/
```

**Step 5: Write Manuscript**
```latex
% In manuscript/main.tex
\input{tables/table3_event_coefficients.tex}
\begin{figure}
  \includegraphics{figures/figure2_event_impacts.pdf}
  \caption{Infrastructure vs Regulatory Event Impacts}
\end{figure}
```

**Step 6: Replication Package**
```bash
# Create replication archive
zip -r replication_package.zip \
    code/ \
    data/ \
    outputs/analysis_results/ \
    README.md \
    requirements.txt

# Upload to journal's data repository
```

---

## Package Initialization

### The `__init__.py` File

**Purpose:** Expose main API for external scripts.

```python
# code/__init__.py
__version__ = "1.0.0"

# Public API
from .data_preparation import DataPreparation
from .garch_models import estimate_models_for_all_cryptos
from .event_impact_analysis import run_complete_analysis
from .publication_outputs import generate_publication_outputs
from .robustness_checks import run_robustness_checks
from .bootstrap_inference import run_bootstrap_analysis

__all__ = [
    'DataPreparation',
    'estimate_models_for_all_cryptos',
    'run_complete_analysis',
    'generate_publication_outputs',
    'run_robustness_checks',
    'run_bootstrap_analysis',
]
```

**Usage in external scripts:**

```python
# Option 1: Import from package
from event_study import DataPreparation, run_complete_analysis

# Option 2: Import full package
import event_study
results = event_study.run_complete_analysis(model_results)
```

---

## Reproducibility Checklist

**Before running the analysis:**

- [ ] Set fixed random seed in `config.py` or `.env` (`RANDOM_SEED=42`)
- [ ] Document software versions (`pip freeze > requirements.txt`)
- [ ] Timestamp data collection dates (record in `data/README.md`)
- [ ] Version control configuration files (`git add config.py .env.example`)

**During execution:**

- [ ] Save console output (`python run_event_study_analysis.py | tee analysis_log.txt`)
- [ ] Record execution time and environment (CPU, RAM, OS)
- [ ] Check convergence status for all models

**After execution:**

- [ ] Archive outputs directory (`tar -czf outputs_YYYYMMDD.tar.gz outputs/`)
- [ ] Save model parameters (`model_parameters/*.json`)
- [ ] Document any convergence failures or warnings
- [ ] Create replication instructions (see Academic Workflow above)

---

## Frequently Asked Questions

**Q: How do I add a new cryptocurrency?**

A: Edit three files:
1. `config.py`: Add to `CRYPTOCURRENCIES` list
2. `data/`: Add `{crypto}.csv` with columns: `date`, `price`, `volume`
3. Re-run `run_event_study_analysis.py`

**Q: How do I change the event window size?**

A: Modify `.env` or `config.py`:
```python
EVENT_WINDOW_BEFORE=5  # Change from default 3
EVENT_WINDOW_AFTER=5
```
This will use [-5, +5] days around event dates.

**Q: What if a GARCH model doesn't converge?**

A: The analysis continues with other cryptocurrencies. To debug:
1. Check data quality for that crypto (missing values, outliers)
2. Inspect event dummy collinearity
3. Try different initial parameter values in `tarch_x_manual.py`

**Q: Can I run only the hypothesis test without GARCH estimation?**

A: No, hypothesis testing requires TARCH-X parameters (δ_infra, δ_reg) which come from GARCH estimation. However, you can **load cached model results** if available:

```python
# Save results after first run
import pickle
with open('model_results.pkl', 'wb') as f:
    pickle.dump(model_results, f)

# Load in subsequent runs
with open('model_results.pkl', 'rb') as f:
    model_results = pickle.load(f)
analysis_results = run_complete_analysis(model_results)
```

**Q: How do I cite this code in my paper?**

A: Include software citation in references:

```bibtex
@software{farzulla2025eventStudy,
  author = {Farzulla, Murad},
  title = {Cryptocurrency Event Study Analysis: Infrastructure vs Regulatory Events},
  year = {2025},
  version = {1.0.0},
  url = {https://github.com/yourusername/crypto-event-study},
  doi = {10.5281/zenodo.XXXXXXX}
}
```

---

## Future Enhancements

**Potential improvements to the orchestration layer:**

1. **Command-line interface:**
   ```bash
   python run_event_study_analysis.py \
       --cryptos btc,eth \
       --robustness \
       --bootstrap 1000 \
       --output-dir custom_outputs/
   ```

2. **Parallel execution:**
   - Use `multiprocessing.Pool` for per-crypto GARCH estimation
   - Expected speedup: 3-5x

3. **Caching intermediate results:**
   - Save model results to disk after Stage 2
   - Skip re-estimation if data unchanged

4. **Progress bars:**
   - Use `tqdm` for long-running operations
   - Example: `for crypto in tqdm(all_cryptos, desc="Estimating GARCH models")`

5. **Logging framework:**
   - Replace `print()` with proper logging
   - Rotate log files, separate ERROR/INFO levels

6. **Configuration validation:**
   - Check `.env` values are in valid ranges
   - Warn about non-standard settings

---

## Contact & Support

**For questions about this documentation:**
- Author: Murad Farzulla
- Email: murad@farzulla.org
- GitHub: [Link to repository]

**For issues with execution:**
- Check console output for error messages
- Review convergence summary for model failures
- Enable DEBUG logging in `config.py`

**For methodology questions:**
- See `DOCS_MODEL_ESTIMATION.md` for GARCH details
- See `DOCS_ANALYSIS_METHODS.md` for hypothesis testing
- Consult academic references in manuscript

---

**End of Master Orchestration Documentation**

*This documentation describes version 1.0.0 of the cryptocurrency event study codebase.*
*Last updated: 2025-10-28*
