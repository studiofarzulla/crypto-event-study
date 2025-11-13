# Code Failures, Market Panic: Why Infrastructure Events Hit Crypto Harder Than Regulations

**Author:** Murad Farzulla
**Date:** November 2025
**Status:** Working Paper

[![Paper DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17595207.svg)](https://doi.org/10.5281/zenodo.17595207)
[![Code DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17595251.svg)](https://doi.org/10.5281/zenodo.17595251)
**Interactive Dashboard:** [farzulla.org/research/crypto-event-study](https://farzulla.org/research/crypto-event-study/)

## Abstract

We document that infrastructure events cause 5.7× larger volatility impacts than regulatory events in cryptocurrency markets (2.385% vs 0.419%, p=0.0008, Cohen's d=2.753). Using TARCH-X models on 50 curated events (2019-2025) across 6 major cryptocurrencies, we find substantial cross-sectional heterogeneity with a 2.18 percentage point spread (ADA: 3.371% vs BTC: 1.191%). Novel GDELT sentiment decomposition by event type reveals asymmetric information processing. Findings are robust to Bayesian inference, machine learning pattern detection, network spillover analysis, and Markov regime-switching models.

## Key Findings

**Differential Volatility Response (5.7× multiplier):**
- Infrastructure events: 2.385% volatility impact
- Regulatory events: 0.419% volatility impact
- Statistical significance: t=4.768, p=0.0008, Cohen's d=2.753

**Cross-Sectional Heterogeneity (2.18pp spread):**
- ADA (Cardano): 3.371% | LTC (Litecoin): 3.013% | ETH (Ethereum): 2.385%
- XRP (Ripple): 2.242% | BNB (Binance): 1.737% | BTC (Bitcoin): 1.191%

**Novel Contributions:**
- First TARCH-X implementation with unbounded event coefficients
- GDELT sentiment decomposition by article type proportions
- Multi-method validation framework (frequentist + Bayesian + ML + network)
- Unexpected finding: ETH most central (0.89), not BTC (0.71)
- Crisis amplification: 5× larger effects during turbulent periods

## Repository Structure

```
.
├── Farzulla_2025_Cryptocurrency_Heterogeneity.pdf    # Final paper (53 pages)
├── Farzulla_2025_Cryptocurrency_Heterogeneity.tex    # LaTeX source
├── references.bib                                    # Bibliography
├── code/                                             # Analysis code (Python)
│   ├── tarch_x_manual.py                            # Custom TARCH-X implementation
│   ├── data_preparation.py                          # ETL pipeline
│   ├── garch_models.py                              # Model estimation
│   ├── event_impact_analysis.py                     # Event analysis
│   └── generate_publication_figures_enhanced.py     # Figure generator
├── data/                                             # Input data (8 CSVs, 1.7MB)
│   ├── btc.csv, eth.csv, xrp.csv, bnb.csv, ltc.csv, ada.csv
│   ├── events.csv                                   # 50 curated events
│   └── gdelt.csv                                    # Sentiment data
├── outputs/analysis_results/                         # Statistical results
│   ├── hypothesis_test_results.csv                  # Main findings
│   ├── fdr_corrected_pvalues.csv                    # FDR corrections
│   └── model_parameters/                            # 6 JSON files (per crypto)
├── publication_figures/                              # Figures used in paper
│   ├── figure1_enhanced_comparison.pdf              # Infrastructure vs Regulatory
│   ├── figure2_heterogeneity_enhanced.pdf           # Cross-sectional spread
│   ├── figure3_model_comparison.pdf                 # AIC/BIC model selection
│   ├── figure4_temporal_decomposition.pdf           # Temporal patterns
│   └── robustness_*.png                             # Robustness checks
├── docs/                                             # Technical documentation
│   ├── DOCS_DATA_PIPELINE.md                        # ETL internals
│   ├── DOCS_MODEL_ESTIMATION.md                     # TARCH-X details
│   └── BUG_FIX_SUMMARY.md                           # Critical bug history
└── tests/                                            # Test suite
```

## Reproducibility

**Full replication:**
```bash
# Install dependencies
pip install -r requirements.txt

# Run complete analysis (5-10 minutes)
python code/run_event_study_analysis.py

# Generate all figures
python code/generate_publication_figures_enhanced.py
```

**Requirements:**
- Python 3.9+
- NumPy, pandas, Matplotlib, SciPy
- arch (GARCH models)
- statsmodels (statistical tests)

All data, code, and results included for complete reproducibility.

## Citation

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

See `CITATION.cff` for complete citation metadata.

## Licenses

- **Paper:** CC BY 4.0 (root `LICENSE` file)
- **Code:** MIT License (`code/LICENSE` file)
- **Data:** CC BY 4.0

## Timeline

- **September 2025:** Master's thesis submission (null result, p=0.997)
- **October 2025:** Removed artificial constraints
- **November 10-12, 2025:** Fixed stationarity bugs (revealed significant findings)
- **November 12, 2025:** Final polish and publication

See `docs/BUG_FIX_SUMMARY.md` and Appendix D in the paper for complete methodological evolution.

## Contact

Murad Farzulla
[farzulla.org](https://farzulla.org)

**Interactive Dashboard:** Explore all results at [farzulla.org/research/crypto-event-study](https://farzulla.org/research/crypto-event-study/)
