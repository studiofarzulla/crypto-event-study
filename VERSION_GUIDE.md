# Version Guide: Cryptocurrency Event Study

This repository contains multiple versions of the research paper. **Use v2.0.1 for citations and journal submissions.**

---

## Quick Reference

| Version | Status | Use Case | File |
|---------|--------|----------|------|
| **v2.0.1** | **Current (Nov 2025)** | **SSRN, journal submissions, citations** | `Farzulla_2025_Cryptocurrency_Event_Study_v2.0.1.pdf` |
| v2.0.0 | Published (Nov 2025) | Zenodo archive, independent research record | `Farzulla_2025_Cryptocurrency_Event_Study_v2.0.0.pdf` |

---

## Version Details

### v2.0.1 (November 2025) - CURRENT VERSION

**Purpose:** Journal submission variant with institutional affiliation

**DOI:** *Pending (SSRN Abstract ID: 5788082)*

**Key Changes from v2.0.0:**
- Added institutional affiliation: King's Business School, King's College London (primary) + Farzulla Research (secondary)
- Updated JEL codes: Added G41 (Behavioral Finance)
- Added funding statement acknowledging King's College London resources
- Updated computational infrastructure note (Resurrexi Lab: 8 nodes, 66 cores, 229GB RAM, 48GB VRAM)
- Fixed stationarity constraint formula (α + β + γ/2 < 1, corrected from previous formulation)
- Added TARCH/GJR-GARCH nomenclature clarification footnote
- Clarified return scaling (percentage returns ×100)
- Added note on custom MLE implementation (standard libraries don't support GARCH-X)
- Condensed Research Context section (4 paragraphs → 1 paragraph)
- Rewrote abstract to lead with main finding (5.7× infrastructure-regulatory asymmetry)

**Empirical Content:** Identical to v2.0.0 (all results, figures, tables, statistical tests unchanged)

**Target Audience:** Academic journals (Digital Finance, Finance Research Letters), SSRN repository

**Citation Format:**
```
Farzulla, M. (2025). Market Reaction Asymmetry: Infrastructure Disruption Dominance
Over Regulatory Uncertainty - Event Study Evidence from Cryptocurrency Volatility
(Version 2.0.1). SSRN. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5788082
```

---

### v2.0.0 (November 2025)

**Purpose:** Independent research record, Zenodo archival version

**DOI:** 10.5281/zenodo.17677682

**Key Features:**
- Farzulla Research preprint template
- Independent research organization affiliation
- Complete empirical findings (5.7× infrastructure-regulatory asymmetry)
- TARCH-X methodology with 6 cryptocurrencies, 50 events (2019-2025)
- Comprehensive robustness checks (Bayesian, regime-switching, network analysis)

**Target Audience:** Open access research community, Zenodo archive

**Citation Format:**
```
Farzulla, M. (2025). Market Reaction Asymmetry: Infrastructure Disruption Dominance
Over Regulatory Uncertainty (Version 2.0.0). Zenodo. https://doi.org/10.5281/zenodo.17677682
```

---

## Version History Summary

**v1.0.0 (November 2025):** Original Zenodo publication, statistical corrections from Master's thesis

**v2.0.0 (November 2025):** Adopted Farzulla Research template, maintained empirical content

**v2.0.1 (November 2025):** Added institutional affiliation metadata for journal submission, fixed technical issues flagged by peer review

---

## Which Version Should I Use?

### For Academic Citations
→ **Use v2.0.1** (most current, SSRN version)

### For Journal Submissions
→ **Use v2.0.1** (includes institutional affiliation, funding statement)

### For Open Access Archival Reference
→ **v2.0.0 is available** on Zenodo with DOI 10.5281/zenodo.17677682

### For Replication/Code
→ Both versions use identical data and code (available in `/code` directory)

---

## Data & Code Availability

All versions share the same underlying analysis:

- **Code Repository:** https://github.com/studiofarzulla/crypto-event-study
- **Code Archive (Zenodo):** https://doi.org/10.5281/zenodo.17679537
- **Interactive Dashboard:** https://farzulla.org/research/crypto-event-study/
- **Data Sources:** CoinGecko (price data), GDELT (sentiment analysis)

**License:**
- Paper: CC-BY-4.0
- Code: MIT

---

## Contact

**Author:** Murad Farzulla
**Email:** murad@farzulla.org
**ORCID:** 0009-0002-7164-8704
**Website:** https://farzulla.org

**Affiliations:**
1. King's Business School, King's College London
2. Farzulla Research

---

*Last Updated: November 22, 2025*
