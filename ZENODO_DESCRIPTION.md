# Zenodo Description - Cryptocurrency Event Study v2.0.0

## Why infrastructure failures crash crypto markets 5.7× harder than regulatory crackdowns

Conventional wisdom says regulatory uncertainty drives cryptocurrency volatility. We prove the opposite: **infrastructure events generate 5.7× larger market impacts than regulatory events** (2.385% vs 0.419%, p=0.0008, Cohen's d=2.75). This contradicts traditional financial markets where policy matters more than pipes.

**The mechanism is architectural:** Decentralized protocols resist regulatory enforcement through jurisdictional arbitrage (regulatory interventions remain geographically constrained), while infrastructure failures directly compromise operational integrity with no escape route. Code failures cascade globally—regulations don't.

## Key Contributions

1. **Novel event decomposition methodology:** TARCH-X models with GDELT sentiment indices decomposed into regulatory vs infrastructure channels across 50 curated events (2019-2025) and 6 cryptocurrencies (BTC, ETH, XRP, BNB, LTC, ADA)

2. **Robust statistical validation:** Primary finding survives independent t-test, Mann-Whitney U, inverse-variance meta-analysis, Bayesian hypothesis testing (BF>10 for 4/6 assets), machine learning clustering, network spillover analysis, and Markov regime-switching models

3. **Unexpected network topology:** Ethereum emerges as central systemic risk factor (eigenvector centrality 0.89) over Bitcoin (0.71)—challenges conventional assumptions about market leadership

4. **Crisis amplification:** Infrastructure effects amplify **5× during crisis periods** (COVID-19 crash, FTX collapse), explaining 67% of extreme volatility events despite representing only 18% of sample

5. **Practical risk management:** Actionable capital buffer recommendations (4-5× higher VaR allocation for infrastructure vs regulatory risk)

## Why This Matters

**For portfolio managers:** Infrastructure events require $2-5M VaR increase per $100M portfolio vs $0.5-1M for regulatory events—traditional risk models underweight operational risk by 5×

**For regulators:** Policy focus should shift from compliance frameworks to operational resilience standards—narrative power without mechanical enforcement in decentralized systems

**For market structure:** Demonstrates how decentralization fundamentally inverts regulatory effectiveness relative to traditional finance

## Methodological Innovation

Custom quasi-maximum likelihood TARCH-X implementation with **unbounded event coefficients** (allows negative volatility effects), numerical Hessian robust standard errors, and full model comparison via AIC/BIC (TARCH-X wins 5/6 assets). Manual MLE implementation provides complete control over optimization and constraint relaxation impossible in standard econometric packages.

## Reproducibility

Full replication package: Python 3.9+, ~45min runtime on standard hardware, no proprietary data. All code, raw data (CoinGecko, GDELT), event classifications, and analysis outputs publicly archived. Repository: [10.5281/zenodo.17679537](https://doi.org/10.5281/zenodo.17679537)

**Research conducted independently with no institutional affiliation—demonstrates accessibility of cryptocurrency market research on consumer hardware.**

---

**Publication Status:** Preprint v2.0.0 (November 2025) | Farzulla Research
**Contact:** murad@farzulla.org | [ORCID 0009-0002-7164-8704](https://orcid.org/0009-0002-7164-8704)
**License:** CC-BY-4.0 (paper) | MIT (code)
