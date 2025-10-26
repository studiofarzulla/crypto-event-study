# TARCH-X Implementation Code

Custom Python implementation of TARCH-X models for cryptocurrency event study analysis.

## Core Modules

### TARCH-X Models
- **`tarch_x_manual.py`** - Main TARCH-X implementation with event indicators
- **`tarch_x_manual_optimized.py`** - Optimized version for faster estimation
- **`garch_models.py`** - Standard GARCH/EGARCH/TARCH specifications

### Analysis Pipeline
- **`data_preparation.py`** - Price data loading and preprocessing
- **`event_impact_analysis.py`** - Event impact estimation and hypothesis testing
- **`robustness_checks.py`** - Placebo tests, temporal stability, alternative windows
- **`bootstrap_inference.py`** - Bootstrap standard errors and confidence intervals

### Utilities
- **`config.py`** - Global configuration and parameters
- **`publication_outputs.py`** - Figure and table generation
- **`coingecko_fetcher.py`** - CoinGecko API price fetcher
- **`run_event_study_analysis.py`** - Main analysis orchestration script

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from code.tarch_x_manual import estimate_tarch_x
from code.robustness_checks import run_placebo_test

# See individual module docstrings for detailed usage
```

## Key Features

- Custom maximum likelihood TARCH-X estimator (~400 lines)
- Bootstrap inference (1,000 iterations)
- Robustness validation suite:
  - Placebo tests with 1,000 random event permutations
  - Temporal stability across market regimes
  - Alternative event window specifications (±1 to ±7 days)
- Publication-ready figure generation (300 DPI)

## License

CC-BY-4.0 - See LICENSE.txt in repository root
