# Code Failures, Market Panic: Why Infrastructure Events Hit Crypto Harder Than Regulations

**Author:** Murad Farzulla
**Affiliation:** Farzulla Research
**Status:** Preprint v2.0.0
**Date:** November 2025
**DOI:** [10.5281/zenodo.17677682](https://doi.org/10.5281/zenodo.17677682)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17677682.svg)](https://doi.org/10.5281/zenodo.17677682)

## Abstract

Cryptocurrency markets exhibit asymmetric volatility responses to different event types. Using TARCH-X models with decomposed GDELT sentiment indices across 50 events (2019-2025) and 6 cryptocurrencies, we document that **infrastructure events generate 5.7× larger volatility impacts than regulatory events** (2.385% vs 0.419%, p=0.0008, Cohen's d=2.75).

This finding contradicts traditional financial market patterns where regulatory uncertainty dominates infrastructure concerns. The mechanism appears rooted in cryptocurrency's foundational architecture: decentralized protocols resist regulatory enforcement (jurisdictional arbitrage nullifies structural interventions), while infrastructure failures directly compromise operational integrity with no escape route.

**Key Findings:**
- Infrastructure events: 2.385% mean volatility increase (highly significant across all tests)
- Regulatory events: 0.419% mean volatility increase (5.7× smaller)
- Robustness: Multiple hypothesis tests, Bayesian validation (BF > 10 for 4/6 assets), network spillover analysis, regime-switching models
- Heterogeneity: ETH most sensitive (4.09% infrastructure response), BTC most stable (1.19%)
- Network topology: ETH emerges as central systemic risk factor (eigenvector centrality 0.89 vs BTC 0.71)

**Implications:**
- Risk management: Infrastructure events require 4-5× higher capital buffers than regulatory events
- Policy focus: Operational resilience standards matter more than compliance frameworks
- Market architecture: Crypto's decentralization makes regulation narratively powerful but mechanically weak

## Repository Contents

```
.
├── README.md                           # This file
├── CITATION.cff                        # Citation metadata
├── LICENSE                             # MIT for code, CC-BY-4.0 for paper
├── Farzulla_2025_Cryptocurrency_Event_Study.tex    # LaTeX source
├── Farzulla_2025_Cryptocurrency_Event_Study.pdf    # Compiled paper
├── references.bib                      # Bibliography
├── code/                               # Analysis scripts
│   ├── config.py                       # Configuration
│   ├── data_collection.py              # CoinGecko & GDELT data
│   ├── tarch_x_estimation.py           # Manual MLE implementation
│   ├── hypothesis_tests.py             # Statistical tests
│   ├── robustness_checks.py            # Bayesian, clustering, spillover
│   └── figure_generation.py            # Publication figures
├── data/                               # Input data
│   ├── events.csv                      # 50 curated events (26 infra, 24 reg)
│   ├── crypto_prices/                  # Daily OHLCV (6 assets)
│   └── gdelt_sentiment/                # Decomposed sentiment indices
├── publication_figures/                # Publication-ready figures
│   ├── figure1_enhanced_comparison.pdf
│   ├── figure2_heterogeneity_enhanced.pdf
│   └── figure4_temporal_decomposition.pdf
├── outputs/                            # Analysis results
│   ├── model_results/                  # TARCH-X estimates
│   ├── hypothesis_tests/               # Test statistics
│   └── robustness/                     # Validation outputs
├── docs/                               # Documentation
│   ├── METHODOLOGY.md                  # Detailed methodology
│   ├── DATA_SOURCES.md                 # Data provenance
│   └── REPLICATION.md                  # Reproducibility guide
└── tests/                              # Unit tests
```

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/studiofarzulla/cryptocurrency-event-study.git
cd cryptocurrency-event-study

# Install dependencies (Python 3.9+)
pip install -r requirements.txt
```

### Run Analysis

```bash
# Full pipeline (data collection → estimation → results)
python code/run_full_analysis.py

# Or step-by-step:
python code/data_collection.py          # Download crypto prices & GDELT
python code/tarch_x_estimation.py       # Estimate models (6 assets × 3 specs)
python code/hypothesis_tests.py         # H1, H2, H3 tests
python code/robustness_checks.py        # Bayesian, spillover, regime
python code/figure_generation.py        # Generate publication figures
```

**Expected runtime:** ~45 minutes on standard hardware (M1/M2 Mac, Ryzen 9)

### View Results

All outputs saved to `outputs/`:
- `model_results/tarch_x_estimates.csv` - Parameter estimates with robust SEs
- `hypothesis_tests/h1_infrastructure_regulatory.csv` - Main finding (5.7× multiplier)
- `figures/` - Publication-ready figures (PDF)

## Key Methodology

### TARCH-X Models

Three nested specifications estimated via quasi-maximum likelihood (QML):

**Model 1: GARCH(1,1)**
```
σ²_t = ω + α·ε²_{t-1} + β·σ²_{t-1}
```

**Model 2: TARCH(1,1)** (adds leverage effects)
```
σ²_t = ω + α·ε²_{t-1} + γ·ε²_{t-1}·I(ε<0) + β·σ²_{t-1}
```

**Model 3: TARCH-X** (adds events + sentiment)
```
σ²_t = ω + α·ε²_{t-1} + γ·ε²_{t-1}·I(ε<0) + β·σ²_{t-1}
       + Σ δ_j·D_{j,t} + θ₁·S^REG_t + θ₂·S^INFRA_t
```

Where:
- `D_{j,t}` = Dummy for event j on day t
- `S^REG_t` = GDELT regulatory sentiment (decomposed)
- `S^INFRA_t` = GDELT infrastructure sentiment (decomposed)

**Innovation:** Unbounded event coefficients (no positivity constraints), allowing negative volatility effects. Manual MLE implementation provides full control over optimization and robust standard errors via numerical Hessian.

### Event Classification

**Infrastructure Events (n=26):**
- Exchange hacks/outages (Mt. Gox, Binance, Coinbase)
- Network congestion/forks (Bitcoin halving, Ethereum Merge)
- Protocol upgrades (Taproot activation, EIP-1559)
- Technical failures affecting operational capacity

**Regulatory Events (n=24):**
- Government announcements (China ban, SEC enforcement)
- Exchange regulations (Binance settlement, FTX collapse)
- Institutional adoption (Bitcoin ETF approval)
- Policy frameworks affecting legal/compliance environment

**Data Quality:** All events verified via multiple sources (CoinDesk, Bloomberg, official announcements). See `data/events.csv` for full list with sources.

### Statistical Validation

**Primary Tests:**
- Independent t-test (parametric)
- Mann-Whitney U (non-parametric)
- Cohen's d (effect size)
- Inverse-variance weighted meta-analysis

**Robustness Checks:**
- Bayesian hypothesis testing (Bayes Factors)
- Machine learning clustering (k-means, silhouette validation)
- Network spillover analysis (VAR-based connectedness)
- Markov regime-switching models
- Bootstrap resampling (10,000 iterations)

**Multiple Testing:** Benjamini-Hochberg FDR correction applied (controlled at q=0.10)

## Main Results

### Hypothesis 1: Infrastructure > Regulatory (SUPPORTED ✓)

| Metric | Infrastructure | Regulatory | Ratio | p-value |
|--------|---------------|------------|-------|---------|
| Mean volatility impact | 2.385% | 0.419% | 5.7× | 0.0008*** |
| Cohen's d | - | - | 2.75 | - |
| Mann-Whitney U | - | - | - | 0.0010*** |
| Inverse-variance Z | - | - | - | 0.0003*** |
| Bayes Factor (BTC) | - | - | 15.2 | - |

**Interpretation:** Infrastructure events generate statistically and economically significant larger volatility responses. Effect robust across parametric/non-parametric tests and Bayesian validation.

### Cross-Sectional Heterogeneity

**Infrastructure Sensitivity Ranking:**
1. ADA: 3.371%
2. XRP: 2.848%
3. ETH: 2.627%
4. BNB: 2.310%
5. LTC: 1.894%
6. BTC: 1.191%

**Network Centrality (Unexpected):**
- ETH eigenvector centrality: 0.89 (highest systemic risk)
- BTC eigenvector centrality: 0.71 (lower than expected)
- Network density: 0.667 (substantial interconnectedness)

**Finding:** Ethereum, not Bitcoin, emerges as primary systemic risk factor in cryptocurrency markets—challenges conventional assumptions.

### Hypothesis 2: Sentiment Leading Indicator (PARTIAL SUPPORT)

GDELT sentiment showed limited predictive power due to:
- 100% negative sentiment bias (structural data quality issue)
- 7% missing values (25/345 weeks)
- Weekly aggregation temporal mismatch with daily volatility
- Limited cryptocurrency-specific coverage (2019-2021 period)

**However:** Sentiment coefficients significant within TARCH-X specifications, confirming conceptual validity despite implementation constraints.

**Recommendation:** Daily GDELT via Google BigQuery (addresses temporal mismatch, ~$0-5/month cost).

### Hypothesis 3: TARCH-X Model Superiority (SUPPORTED ✓)

| Asset | GARCH AIC | TARCH AIC | TARCH-X AIC | Winner |
|-------|-----------|-----------|-------------|--------|
| BTC | 6420.3 | 6391.2 | **6358.7** | TARCH-X |
| ETH | 7832.1 | 7801.4 | **7768.9** | TARCH-X |
| XRP | 6912.5 | 6889.3 | **6861.2** | TARCH-X |
| BNB | 7234.8 | 7210.1 | **7182.6** | TARCH-X |
| LTC | 6543.2 | 6521.7 | **6495.3** | TARCH-X |
| ADA | 7401.6 | 7389.4 | 7391.8 | TARCH |

**AIC Preference:** 83% (5/6 assets prefer TARCH-X)
**BIC Trade-off:** BIC penalizes TARCH-X by 30-44 points (parsimony vs fit trade-off)

**Interpretation:** Event-specific modeling provides significant informational value for volatility forecasting despite added complexity.

## Crisis Amplification

Infrastructure effects amplify **5× during crisis periods** (COVID-19 crash, FTX collapse):
- Crisis infrastructure impact: 11.93% (March 2020)
- Non-crisis infrastructure impact: 2.32%
- Amplification ratio: 5.14×

**Crisis periods explain 67% of extreme volatility events** despite representing only 18% of sample period.

## Practical Implications

### For Risk Managers

**Differentiated Capital Requirements:**
- Infrastructure events: $2-5M VaR increase per $100M portfolio
- Regulatory events: $0.5-1M VaR increase per $100M portfolio
- Required buffer ratio: 4-5×

**Hedging Strategies:**
- Infrastructure risk: Requires operational insurance, cross-exchange redundancy
- Regulatory risk: Addressable via sentiment monitoring, compliance tracking

### For Regulators

**Policy Priorities:**
1. **Operational resilience standards** (5.7× larger market impact than compliance)
2. Real-time infrastructure monitoring frameworks
3. Circuit breakers for technical failures (not just price movements)
4. Cross-exchange coordination protocols

**Regulatory Effectiveness:**
- Crypto markets process regulatory information through **sentiment only** (no microstructure enforcement)
- Decentralization enables jurisdictional arbitrage → regulatory interventions remain geographically/institutionally constrained
- Implication: Regulators retain narrative power but lack mechanical power

### For Investors

**Event-Based Trading:**
- Infrastructure failures offer predictable volatility spikes (entry/exit timing)
- Regulatory announcements show muted, heterogeneous responses (BTC defensive, altcoins sensitive)

**Portfolio Diversification:**
- ETH concentration = systemic risk (high network centrality despite Ethereum narrative)
- BTC serves defensive role (lowest infrastructure sensitivity)

## Version History

### v2.0.0 (November 2025) - Current
- Reformatted to Farzulla Research preprint template
- Strengthened key findings: ETH network centrality, crisis amplification, Paper 2 teaser
- Fixed numerical inconsistencies throughout (standardized to analysis outputs)
- Synced Appendix A with events.csv (50 events: 26 infrastructure, 24 regulatory)
- Fixed bibliography errors (Chen volume, Saggu authorship, Bonaparte journal, Saiedi study)
- Removed Appendix D revision notes (kept hypothesis changes table)
- Updated contact email to murad@farzulla.org
- DOI: 10.5281/zenodo.17677682

### v1.0.0 (November 2025)
- Initial public release
- Master's thesis revision with expanded robustness checks
- Custom TARCH-X MLE implementation (400+ lines, unbounded coefficients)
- 50 curated events, GDELT sentiment decomposition, 6 cryptocurrencies
- DOI: 10.5281/zenodo.17595207

### Master's Thesis (September 2025)
- Original submission version
- Different findings due to implementation bugs (infrastructure/regulatory indistinguishable)
- Fixed in v1.0.0 via stationarity corrections and constraint removal

## Citation

### Paper Citation

```bibtex
@techreport{farzulla2025infrastructure,
  author = {Farzulla, Murad},
  title = {Code Failures, Market Panic: Why Infrastructure Events Hit Crypto Harder Than Regulations},
  institution = {Farzulla Research},
  year = {2025},
  month = {November},
  type = {Preprint},
  version = {2.0.0},
  doi = {10.5281/zenodo.17677682},
  url = {https://farzulla.org/research/crypto-event-study/}
}
```

### Repository Citation

See `CITATION.cff` for structured citation metadata (Zenodo/GitHub compatible).

## Interactive Dashboard

Explore results interactively at: [farzulla.org/research/crypto-event-study/](https://farzulla.org/research/crypto-event-study/)

Features:
- Asset-specific volatility responses
- Event timeline with classification filters
- Network spillover visualizations
- Model comparison diagnostics

## Data Availability

All data, code, and documentation publicly available:
- **GitHub:** [github.com/studiofarzulla/cryptocurrency-event-study](https://github.com/studiofarzulla/cryptocurrency-event-study)
- **Zenodo:** [10.5281/zenodo.17677682](https://doi.org/10.5281/zenodo.17677682)
- **Dashboard:** [farzulla.org/research/crypto-event-study/](https://farzulla.org/research/crypto-event-study/)

**Data Sources:**
- Crypto prices: CoinGecko API (public, free)
- GDELT sentiment: Google BigQuery public dataset
- Event classification: Manual curation from news sources (documented in `data/events.csv`)

**Reproducibility:** Python 3.9+, standard hardware (no GPU required), ~45min runtime.

## Contact

**Murad Farzulla**
Farzulla Research
📧 murad@farzulla.org
🌐 [farzulla.org](https://farzulla.org)
🔬 [orcid.org/0009-0002-7164-8704](https://orcid.org/0009-0002-7164-8704)

## License

- **Code:** MIT License (see `LICENSE`)
- **Paper:** Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Data:** See individual data source licenses (CoinGecko, GDELT)

## Acknowledgments

This research benefited from:
- **Perplexity AI:** Exceptional research discovery capabilities for literature review and data source identification
- **Anthropic Claude:** Invaluable assistance with analytical framework development, custom TARCH-X MLE implementation, methodological critique, and technical writing—substantially accelerated research velocity and enabled expanded scope of analysis

Computational resources: Personal workstation (AMD Ryzen 9 9900X, 128GB RAM)—no institutional compute infrastructure required.

---

**Note:** This is an independent research project (no institutional affiliation). All analysis conducted on standard consumer hardware, demonstrating accessibility of cryptocurrency market research.
