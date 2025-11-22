# TARCH-X Implementation Code

[![Code DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17595251.svg)](https://doi.org/10.5281/zenodo.17595251)

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
- **`robustness_overlapping_events.py`** - Robustness check for overlapping event treatment
- **`run_diagnostics.py`** - Model diagnostics (Ljung-Box, ARCH-LM, Jarque-Bera tests)
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

## Citation

If you use this code in your research, please cite:

```bibtex
@software{farzulla2025crypto_code,
  author = {Farzulla, Murad},
  title = {TARCH-X Implementation for Cryptocurrency Event Study Analysis},
  year = {2025},
  month = {November},
  publisher = {Zenodo},
  version = {v1.0.1},
  doi = {10.5281/zenodo.17595251},
  url = {https://doi.org/10.5281/zenodo.17595251}
}
```

For the research paper using this code, cite:

```bibtex
@techreport{farzulla2025infrastructure,
  author = {Farzulla, Murad},
  title = {Code Failures, Market Panic: Why Infrastructure Events Hit Crypto Harder Than Regulations},
  subtitle = {A TARCH-X Analysis of Differential Volatility Responses},
  year = {2025},
  month = {November},
  type = {Working Paper},
  doi = {10.5281/zenodo.17595207},
  url = {https://doi.org/10.5281/zenodo.17595207}
}
```

## License

MIT License - See `LICENSE` file in this directory

The research paper is licensed under CC BY 4.0 (see root `LICENSE` file).
