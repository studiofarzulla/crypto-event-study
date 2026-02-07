# Infrastructure vs Regulatory Shocks: Asymmetric Volatility Response in Cryptocurrency Markets

**Event Study Evidence from Cryptocurrency Volatility**

[![DOI](https://img.shields.io/badge/DOI-10.21203%2Frs.3.rs--8323026%2Fv1-blue.svg)](https://doi.org/10.21203/rs.3.rs-8323026/v1)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Status](https://img.shields.io/badge/Status-Under_Review-yellow.svg)](https://doi.org/10.21203/rs.3.rs-8323026/v1)

**Working Paper DAI-2506** | [Dissensus AI](https://dissensus.ai)

Currently under review at **Digital Finance** (Springer).

## Abstract

Infrastructure failures generate 5.7x larger volatility shocks than regulatory announcements in cryptocurrency markets (2.385% vs 0.419%, p=0.0008, Cohen's d=2.753), challenging assumptions that "all bad news is equivalent" for portfolio risk management. This asymmetry is robust across six major cryptocurrencies (January 2019 -- August 2025), multiple statistical tests, and validation approaches including Bayesian inference (Bayes Factors >10 for 4/6 assets), machine learning clustering, network spillover analysis, and Markov regime-switching models.

We analyze 50 major events using GJR-GARCH-X models incorporating infrastructure disruptions (exchange outages, protocol exploits, network failures) and regulatory announcements (enforcement actions, policy changes) as exogenous variance drivers. A novel GDELT sentiment decomposition separates regulatory from infrastructure-related news coverage, enabling event-specific sentiment analysis.

Critically, even degraded sentiment proxies -- weekly aggregation creating 7-day temporal mismatch with daily volatility, 7% missing values, and systematic negative bias -- improve model fit for 83% of assets. This suggests sentiment's true information content is substantially underestimated in our results: cryptocurrency markets appear sufficiently sentiment-driven that any reasonable proxy captures tradeable signal, implying higher-frequency sentiment data would yield considerably stronger effects.

Network analysis reveals ETH, not BTC, serves as the primary systemic risk hub (eigenvector centrality 0.89 vs 0.71), challenging conventional assumptions about Bitcoin dominance. Regime-switching models detect 5x sensitivity amplification during crisis periods (F=45.23, p<0.001), with infrastructure sensitivity increasing from 2.3% to 11.2% during market stress -- implying traditional VaR models assuming linear risk scaling catastrophically underestimate tail risk.

## Key Findings

| Finding | Result |
|---------|--------|
| Infrastructure vs Regulatory volatility impact | 5.7x larger (2.385% vs 0.419%, p=0.0008) |
| Effect size | Cohen's d = 2.753 |
| Bayesian validation | BF > 10 for 4/6 assets |
| Sentiment model improvement | 83% of assets (5/6) |
| ETH systemic risk centrality | Eigenvector centrality 0.89 vs BTC 0.71 |
| Crisis amplification | 5x (2.3% to 11.2%, F=45.23, p<0.001) |

## Repository Structure

```
crypto-event-study/
├── preprint/                       # Extended preprint version
├── springer-submission/            # FROZEN -- Springer journal submission (DO NOT MODIFY)
├── code/                           # Analysis scripts
│   ├── config.py                   # Configuration
│   ├── data_collection.py          # CoinGecko & GDELT data
│   ├── tarch_x_estimation.py       # Manual MLE implementation
│   ├── hypothesis_tests.py         # Statistical tests
│   ├── robustness_checks.py        # Bayesian, clustering, spillover
│   └── figure_generation.py        # Publication figures
├── data/                           # Input data
│   ├── events.csv                  # 50 curated events (26 infra, 24 reg)
│   ├── crypto_prices/              # Daily OHLCV (6 assets)
│   └── gdelt_sentiment/            # Decomposed sentiment indices
├── publication_figures/            # Publication-ready figures
├── outputs/                        # Analysis results
└── docs/                           # Methodology documentation
```

**Note:** The `springer-submission/` directory contains the frozen journal submission and should not be modified.

## Replication

```bash
pip install -r requirements.txt

python code/data_collection.py
python code/tarch_x_estimation.py
python code/hypothesis_tests.py
python code/robustness_checks.py
python code/figure_generation.py
```

## Keywords

Cryptocurrency, Volatility, Event Study, GJR-GARCH-X, Infrastructure Risk, Regulatory Uncertainty

## Citation

```bibtex
@article{farzulla2025infrastructure,
  author  = {Farzulla, Murad},
  title   = {Infrastructure vs Regulatory Shocks: Asymmetric Volatility Response in Cryptocurrency Markets},
  year    = {2025},
  doi     = {10.21203/rs.3.rs-8323026/v1},
  url     = {https://doi.org/10.21203/rs.3.rs-8323026/v1},
  note    = {Under Review at Digital Finance (Springer)}
}
```

## Authors

- **Murad Farzulla** -- [Dissensus AI](https://dissensus.ai) & King's College London
  - ORCID: [0009-0002-7164-8704](https://orcid.org/0009-0002-7164-8704)
  - Email: murad@dissensus.ai

## License

Paper content: [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/)
Code: [MIT License](LICENSE)
