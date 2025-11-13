# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Cryptocurrency Event Study Research Code**
Academic research codebase analyzing cross-sectional heterogeneity in cryptocurrency event sensitivity using TARCH-X volatility models. Published as working paper (DOI: 10.5281/zenodo.17449736).

## Core Commands

### Run Complete Analysis
```bash
# Full analysis pipeline (5-10 minutes)
python code/run_event_study_analysis.py

# With robustness checks and bootstrap (30-60 minutes)
python code/run_event_study_analysis.py --robustness --bootstrap
```

### Generate Publication Outputs
```bash
# Figures only (heterogeneity results - THE MONEY SHOT)
python code/create_heterogeneity_figures.py

# All publication figures
python code/create_publication_figures.py

# LaTeX tables
python code/generate_latex_tables.py
```

### Testing
```bash
# Run all tests with coverage
pytest

# Quick smoke tests
python code/run_smoke_tests.py

# Validate data integrity
python code/validate_data.py
```

### Development Workflow
```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt

# Run specific module
python -m code.data_preparation
python -m code.garch_models
```

## Architecture

### Pipeline Flow
```
Raw Data → Data Preparation → TARCH-X Models → Event Analysis → Publication Outputs
```

**Critical Path:**
1. `code/data_preparation.py` - ETL pipeline (prices → returns, events → dummies, GDELT → decomposed sentiment)
2. `code/garch_models.py` - Model estimation interface (GARCH/TARCH/TARCH-X)
3. `code/tarch_x_manual.py` - Custom TARCH-X with exogenous variance variables
4. `code/event_impact_analysis.py` - Extract event coefficients, FDR correction
5. `code/hypothesis_testing_results.py` - Statistical tests (infrastructure vs regulatory)
6. `code/publication_outputs.py` - Generate figures/tables

### Key Design Decisions

**Event Overlap Handling (CRITICAL):**
- SEC Twin Suits (events 31/32): Composite dummy prevents double-counting
- EIP-1559 & Polygon Hack (events 17/18): Both dummies set to 0.5 for correct coefficient interpretation
- Event windows: ±3 days standard (truncated to prevent overlap when needed)

**GDELT Sentiment Decomposition (NOVEL METHODOLOGY):**
```python
# Three-stage process:
# 1. Load weekly GDELT sentiment
# 2. Z-score normalize (52-week rolling window)
# 3. Decompose by article proportions:
S_reg_decomposed = S_gdelt_normalized × reg_proportion
S_infra_decomposed = S_gdelt_normalized × infra_proportion
```

**TARCH-X Model Specification:**
```
Mean Equation:
  r_t = μ + Σ(δ_j × D_j,t) + Σ(θ_k × S_k,t) + ε_t

Variance Equation:
  σ²_t = ω + α·ε²_{t-1} + γ·ε²_{t-1}·I(ε_{t-1}<0) + β·σ²_{t-1} + Σ(λ_j × x_j,t)
```

Where:
- `D_j,t` = Event dummy variables (D_infrastructure, D_regulatory)
- `S_k,t` = Sentiment variables (S_gdelt_normalized, S_reg_decomposed, S_infra_decomposed)
- `x_j,t` = Exogenous variables in variance equation

**Recent Modification (Oct 28, 2025):**
Event dummies temporarily disabled in `garch_models.py:378-382` to test sentiment-only approach. Reduces parameters from 11 → 9. Uncomment to restore original specification.

### File Organization

**Core Analysis Modules:**
- `data_preparation.py` - ETL pipeline (700+ lines)
- `garch_models.py` - Model estimation interface (500+ lines)
- `tarch_x_manual.py` - Custom TARCH-X implementation (500+ lines)
- `event_impact_analysis.py` - Event coefficient extraction (978 lines)
- `hypothesis_testing_results.py` - Statistical hypothesis tests (442 lines)

**Robustness & Validation:**
- `robustness_checks.py` - OHLC volatility, placebo tests (759 lines)
- `robustness_alternative_windows.py` - Window sensitivity analysis (667 lines)
- `robustness_placebo_outlier.py` - Publication-ready robustness (759 lines)
- `bootstrap_inference.py` - Confidence intervals (368 lines)

**Publication Pipeline:**
- `create_heterogeneity_figures.py` - KEY RESULTS (Figure 1-3, 97.4pp spread)
- `create_publication_figures.py` - Additional figures
- `generate_latex_tables.py` - LaTeX table generation
- `publication_outputs.py` - Unified output generator

**Utility Scripts:**
- `run_event_study_analysis.py` - Main orchestration script
- `config.py` - Paths, seeds, parameters
- `validate_data.py` - Data integrity checks
- `run_smoke_tests.py` - Quick validation

**Legacy/Experimental:**
- `tarch_x_manual_optimized.py` - Vectorized version (5x speedup)
- `tarch_x_integration.py` - Integration guide
- `bootstrap_inference_optimized.py` - Parallelized bootstrap
- `[legacy]files-docs/` - Old structure before refactor

### Data Dependencies

**Required CSVs in `data/`:**
- `btc.csv`, `eth.csv`, `xrp.csv`, `bnb.csv`, `ltc.csv`, `ada.csv` - Daily prices (snapped_at, price)
- `events.csv` - 50 events (event_id, date, label, title, type)
- `gdelt.csv` - Weekly sentiment (week_start, avg_tone, reg_proportion, infra_proportion)

**Outputs in `outputs/`:**
- `analysis_results/` - CSVs (model parameters, hypothesis tests, FDR corrections)
- `publication/figures/` - Publication-ready PDFs
- `publication/latex/` - LaTeX tables

## Critical Implementation Notes

### Reproducibility (JOURNAL PUBLICATION)
```python
# Set in run_event_study_analysis.py:69-71
np.random.seed(config.RANDOM_SEED)  # 42
random.seed(config.RANDOM_SEED)
```
**NEVER change** `RANDOM_SEED` after generating published results.

### Event Dummy Variables
- **Mutually exclusive**: D_infrastructure OR D_regulatory (not both)
- **Time-varying**: Activated only during event windows (±3 days)
- **Special values**: 0.5 for overlapping events of same type

### TARCH-X Parameter Count
- GARCH(1,1): 5 parameters (ω, α, β, μ, ν)
- TARCH(1,1): 6 parameters (adds γ for leverage)
- TARCH-X (full): 11 parameters (adds 2 event dummies + 3 sentiment variables)
- TARCH-X (sentiment-only): 9 parameters (current test configuration)

### Model Estimation Flow
```python
# 1. Prepare data
prep = DataPreparation(crypto='btc')
data = prep.prepare()

# 2. Estimate models
from garch_models import GARCHModels
estimator = GARCHModels(data, crypto='btc')
results = estimator.estimate_all_models()

# 3. Extract results
tarchx = results['TARCH-X']
print(f"AIC: {tarchx.aic}, BIC: {tarchx.bic}")
```

### Common Issues

**Convergence Failures:**
- TARCH-X may fail on sparse event windows
- Fallback: Uses GARCH(1,1) baseline
- Check `convergence` flag in results

**Event Overlap Detection:**
- Automatic composite dummy creation
- Manual 0.5 adjustment for same-type overlaps
- See `data_preparation.py:create_composite_dummy()` and `_create_event_dummies()`

**GDELT Missing Data:**
- 7% missing values (25/345 weeks)
- Forward-fill strategy from weekly to daily
- Z-score normalization handles outliers

## Testing Strategy

**Test Categories (pytest markers):**
- `@pytest.mark.unit` - Individual function tests
- `@pytest.mark.integration` - Multi-component tests
- `@pytest.mark.statistical` - Model validation tests
- `@pytest.mark.reproducibility` - Fixed-seed verification
- `@pytest.mark.slow` - Bootstrap/robustness tests

**Coverage Target:** 80%+ for publication

**Key Test Files:**
- `tests/test_data_preparation.py` - ETL pipeline validation
- `tests/test_garch_models.py` - Model estimation verification
- `tests/test_event_impact.py` - Event coefficient extraction
- `tests/test_robustness.py` - Statistical validation

## Documentation

**Comprehensive module docs in `docs/`:**
- `DOCS_DATA_PIPELINE.md` - Data preparation internals
- `DOCS_MODEL_ESTIMATION.md` - TARCH-X implementation details
- `DOCS_ANALYSIS_TESTING.md` - Statistical tests and robustness
- `DOCS_PUBLICATION_PIPELINE.md` - Figure/table generation
- `DOCS_MASTER_ORCHESTRATION.md` - Complete pipeline flow

**Read these before:**
- Modifying data preparation logic
- Changing model specifications
- Adding new robustness checks
- Generating publication outputs

## Research Context

**Key Finding:** 97.4 percentage point spread in event sensitivity (BNB: 0.947% vs LTC: -0.027%)

**Null Result:** Infrastructure vs Regulatory events indistinguishable (p=0.997)

**Novel Contribution:** GDELT sentiment decomposition methodology weighted by article type proportions

**Status:** Working paper submitted to Zenodo (October 2025), revision of Master's thesis

## Modification Guidelines

**Safe to modify:**
- Figure aesthetics in `create_*_figures.py`
- LaTeX table formatting in `generate_latex_tables.py`
- Additional robustness checks in `robustness_*.py`

**Requires caution:**
- Event window sizes (breaks published results)
- TARCH-X model specification (changes parameter count)
- Event overlap handling (affects coefficient interpretation)

**NEVER modify:**
- Random seed values
- Core data preparation logic (without extensive testing)
- Event dummy 0.5 adjustment logic
- Published figure/table outputs
