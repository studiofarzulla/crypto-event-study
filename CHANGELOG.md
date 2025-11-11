# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-10

### Added
- Initial public release of cryptocurrency event study research
- Complete TARCH-X volatility analysis framework for 6 major cryptocurrencies (BTC, ETH, XRP, BNB, LTC, ADA)
- Event study methodology analyzing 18 infrastructure and regulatory events (2019-2025)
- Novel GDELT sentiment decomposition integrated into TARCH-X models
- Comprehensive statistical analysis including FDR correction and multiple hypothesis testing
- Four publication-ready figures (infrastructure vs regulatory comparison, cross-sectional heterogeneity, event coefficient heatmap, model performance comparison)
- Complete BibTeX bibliography with 74 academic references
- LaTeX source files for academic publication formatting
- Python analysis pipeline with reproducible random seed (42)
- CITATION.cff for proper academic attribution

### Key Findings
- **Infrastructure events dominate regulatory events**: 2.32% average volatility response vs 0.42% (p=0.0057, Cohen's d=2.88)
- **Cross-sectional heterogeneity**: ADA most sensitive (3.37%), BTC least sensitive (1.13%), 2.24pp spread
- **ETH infrastructure effect survives FDR correction**: Only significant result after multiple testing adjustment (FDR p=0.016)
- **TARCH-X model superiority**: 83% AIC preference rate over baseline GARCH/TARCH models
- **Sentiment decomposition significance**: GDELT variables significant in 50% of infrastructure events, 44% of regulatory events

### Technical Details
- Random seed: 42 (ensures reproducibility)
- Event windows: ±3 days around each event
- Statistical tests: Independent t-test, Mann-Whitney U, inverse-variance weighted Z-test
- FDR correction: Benjamini-Hochberg at α=0.10
- Model comparison: AIC and BIC for GARCH(1,1), TARCH(1,1), TARCH-X specifications

### Documentation
- Complete manuscript (50 pages, LaTeX + PDF)
- Section-by-section methodology documentation
- Comprehensive references and citations
- Reproducible code pipeline

### Research Context
- Submitted as Master's thesis, September 2025
- Revised for publication with corrected analysis pipeline (November 2025)
- Hypothesis testing outcomes: H1 (SUPPORTED), H2 (PARTIAL SUPPORT), H3 (SUPPORTED)

---

## Publication Information

**Title:** Differential Volatility Responses to Infrastructure and Regulatory Events in Cryptocurrency Markets: A TARCH-X Analysis

**Author:** Murad Farzulla

**DOI:** 10.5281/zenodo.17449736

**Repository:** https://github.com/studiofarzulla/cryptocurrency-event-study

**License:** See LICENSE file

**Citation:** See CITATION.cff for proper attribution format
