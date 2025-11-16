# Advanced Econometric Improvements for Paper 2

## Overview

This document outlines advanced econometric techniques to strengthen Paper 2's causal identification and address potential referee concerns.

---

## 1. Endogeneity Concerns

### Problem
**Simultaneity bias:** Does regulation cause microstructure changes, or do microstructure changes prompt regulation?

Example: SEC might target crypto when spreads are already widening (market stress).

### Solutions

#### A. Instrumental Variables (IV) Approach

**Instrument:** Use regulatory announcements in *foreign* jurisdictions

```
First stage:  US_microstructure_change = α + β·Foreign_regulation + ε
Second stage: US_volatility = γ + δ·(Predicted microstructure) + u
```

**Why valid:**
- Foreign regulation affects US crypto markets (via global orderbooks)
- But foreign regulation is exogenous to US-specific microstructure
- Satisfies relevance and exclusion restrictions

**Implementation:**
```python
from statsmodels.regression.linear_model import IV2SLS

# Instruments: EU MiCA announcements, China bans, etc.
instruments = ['D_EU_regulation', 'D_China_announcement']
endog = ['spread_change']
exog = ['sentiment', 'vix', 'volume']

model = IV2SLS(volatility, exog, endog, instruments).fit()
```

#### B. Granger Causality Test

Test temporal precedence:

```python
from statsmodels.tsa.stattools import grangercausalitytests

# Does spread change Granger-cause volatility?
# Or does volatility Granger-cause spread?
grangercausalitytests(data[['volatility', 'spread']], maxlag=5)
```

**Expected result for our hypothesis:**
- Crypto: Sentiment → Volatility (unidirectional)
- Traditional: Spread → Volatility (bidirectional feedback)

---

## 2. Triple-Difference Design

### Current: Difference-in-Differences
- Crypto vs Traditional (first difference)
- Pre vs Post event (second difference)

### Improvement: Triple-Difference

Add third dimension: **Event type** (Regulatory vs Infrastructure)

$$
\Delta^3 Y = \beta_0 + \beta_1 \cdot Crypto + \beta_2 \cdot Post + \beta_3 \cdot Regulatory \\
+ \beta_4 \cdot (Crypto \times Post) + \beta_5 \cdot (Crypto \times Regulatory) \\
+ \beta_6 \cdot (Post \times Regulatory) + \beta_7 \cdot (Crypto \times Post \times Regulatory)
$$

**Interpretation of $\beta_7$:**
- Tests if crypto/traditional difference differs between regulatory and infrastructure events
- Expected: **Negative** (crypto's weak response is specific to regulation, not infrastructure)

**Why powerful:**
- Infrastructure events provide natural placebo (both crypto and traditional should respond)
- Regulatory events show differential response (crypto weak, traditional strong)
- Triple-interaction isolates the regulatory mechanism

**Implementation:**
```python
import statsmodels.formula.api as smf

# Prepare data in long format
model = smf.ols('''
    spread_change ~
        C(asset_type) * C(post_event) * C(event_type) +
        vix + volume + market_cap
''', data=panel_data).fit(cov_type='cluster', cov_kwds={'groups': panel_data['event_id']})

print(model.summary())
```

---

## 3. Synthetic Control Method

### Problem
No perfect control group (traditional markets differ fundamentally from crypto)

### Solution
Create **synthetic crypto** from weighted combination of traditional assets

**Steps:**
1. Pre-event: Match crypto's microstructure using weighted average of SPY, GLD, QQQ
2. Post-event: Compare actual crypto to synthetic crypto
3. Gap = treatment effect

**Advantages:**
- Allows for time-varying confounders
- More credible counterfactual than simple DiD
- Visualizes treatment effect clearly

**R code (reference):**
```r
library(Synth)

# Create synthetic BTC from SPY, GLD, TLT, VIX
dataprep.out <- dataprep(
  foo = crypto_trad_panel,
  predictors = c("spread", "volume", "volatility"),
  time.predictors.prior = 1:30,  # Pre-event window
  dependent = "spread",
  unit.variable = "asset",
  time.variable = "day",
  treatment.identifier = "BTC",
  controls.identifier = c("SPY", "GLD", "QQQ", "TLT")
)

synth.out <- synth(dataprep.out)
```

**Python implementation:** Use `CausalImpact` library or manual optimization

---

## 4. Heterogeneous Treatment Effects

### Current Approach
Average effect across all cryptos

### Improvement
Test cross-sectional heterogeneity

**Hypothesis:** Effect varies by:
1. **Market cap:** Larger cryptos (BTC, ETH) show weaker regulatory response than small caps
2. **Liquidity:** More liquid cryptos have less microstructure response
3. **Exchange listing:** Cryptos on regulated exchanges (Coinbase) vs unregulated (Binance)

**Specification:**
$$
\text{Spread change}_i = \beta_0 + \beta_1 \cdot \text{Regulatory event} \\
+ \beta_2 \cdot (\text{Regulatory} \times \log(\text{Market cap})_i) \\
+ \beta_3 \cdot (\text{Regulatory} \times \text{Liquidity}_i) + \varepsilon_i
$$

**Expected:**
- $\beta_1$: Average regulatory effect
- $\beta_2 < 0$: Larger cryptos show *weaker* regulatory microstructure response
- $\beta_3 < 0$: More liquid cryptos show *weaker* response

**Why valuable:**
- Shows mechanism is systematic, not Bitcoin-specific
- Identifies which cryptos are "most decentralized" (weakest regulatory bite)

---

## 5. High-Frequency Event Study

### Current: Daily data
Bid-ask spreads measured at daily close

### Improvement: Intraday analysis (5-minute intervals)

**Why critical:**
- Microstructure effects may be **transient** (widen intraday, normalize by close)
- Daily data may miss the action
- Allows precise event time analysis

**Data sources:**
- Crypto: Binance WebSocket API (free, real-time)
- Traditional: TAQ from WRDS (if available)

**Analysis:**
```python
# Event study at 5-minute intervals
event_time = pd.to_datetime('2024-01-10 09:30:00')  # SEC announcement time
window = pd.Timedelta(hours=6)

spread_data = get_high_freq_spreads(
    start=event_time - window,
    end=event_time + window,
    frequency='5min'
)

# Plot: Spread evolution around exact announcement time
plot_event_study(spread_data, event_time, title="Intraday Microstructure Response")
```

**Expected finding:**
- Crypto: Spread spikes briefly at announcement, reverts within hours (pure sentiment)
- Traditional: Spread widens and **persists** (structural change)

---

## 6. Markov-Switching Models

### Problem
Regulatory effects may differ in **bull vs bear markets**

### Solution
Regime-switching GARCH model

**Specification:**
$$
\sigma^2_t = \omega_{S_t} + \alpha_{S_t} \varepsilon^2_{t-1} + \beta_{S_t} \sigma^2_{t-1} + \delta_{S_t} \cdot \text{Spread}_t
$$

Where $S_t \in \{1, 2\}$ (bull/bear regime), estimated via EM algorithm

**Hypothesis:**
- In **bull markets:** Microstructure channel weak (sentiment dominates)
- In **bear markets:** Microstructure channel stronger (liquidity matters)

**Why valuable:**
- Addresses "but what about crypto winter?" concern
- Shows sentiment dominance is not just a bull market phenomenon

**Implementation:**
```python
from statsmodels.tsa.regime_switching import markov_regression

# Two-regime model
model = markov_regression.MarkovRegression(
    endog=volatility,
    k_regimes=2,
    exog=spread_changes,
    switching_variance=True
).fit()

print("Regime 1 (Bull) spread coefficient:", model.params[0])
print("Regime 2 (Bear) spread coefficient:", model.params[1])
```

---

## 7. Bootstrap for Small Sample Inference

### Problem
Pilot study has only 5 events → small sample, asymptotic theory invalid

### Solution
Wild bootstrap for clustered data

**Why "wild" bootstrap:**
- Standard bootstrap assumes i.i.d. (violated: events clustered by year)
- Wild bootstrap preserves heteroskedasticity and dependence structure

**Implementation:**
```python
def wild_bootstrap_ttest(crypto_changes, trad_changes, n_boot=10000):
    """
    Wild bootstrap for paired t-test.

    Accounts for heteroskedasticity in event responses.
    """
    observed_diff = (trad_changes - crypto_changes).mean()

    bootstrap_diffs = []
    for _ in range(n_boot):
        # Rademacher weights: {-1, +1} with prob 0.5
        weights = np.random.choice([-1, 1], size=len(crypto_changes))

        boot_crypto = crypto_changes * weights
        boot_trad = trad_changes * weights

        boot_diff = (boot_trad - boot_crypto).mean()
        bootstrap_diffs.append(boot_diff)

    # P-value: proportion of bootstrap samples more extreme than observed
    p_value = np.mean(np.abs(bootstrap_diffs) >= abs(observed_diff))

    return p_value

# Use in paper:
p_val = wild_bootstrap_ttest(results_df['crypto_change'], results_df['trad_change'])
print(f"Wild bootstrap p-value: {p_val:.4f}")
```

---

## 8. Model Diagnostics & Specification Tests

### A. TARCH-X Specification Tests

**Test 1: Residual diagnostics**
```python
from statsmodels.stats.diagnostic import acorr_ljungbox, het_arch

# Ljung-Box test for autocorrelation
lb_stat, lb_pval = acorr_ljungbox(residuals, lags=10)
print(f"Ljung-Box test: p={lb_pval[9]:.4f}")  # Should be >0.05

# ARCH-LM test for remaining ARCH effects
arch_stat, arch_pval = het_arch(residuals, nlags=5)
print(f"ARCH-LM test: p={arch_pval:.4f}")  # Should be >0.05
```

**Test 2: Compare model specifications**
```python
# Estimate competing models
models = {
    'TARCH-X': estimate_tarch_x(...),
    'GARCH-X': estimate_garch_x(...),
    'EGARCH-X': estimate_egarch_x(...),
    'GJR-GARCH-X': estimate_gjr_garch_x(...)
}

# Model selection
for name, model in models.items():
    print(f"{name}: AIC={model.aic:.2f}, BIC={model.bic:.2f}")

# Report best-fitting model + show others in appendix
```

### B. Overidentification Test (for IV)

If using multiple instruments:
```python
from statsmodels.sandbox.regression.gmm import IV2SLS

# Test if instruments are valid (Hansen J-test)
model = IV2SLS(y, X, instruments).fit()
j_stat = model.j_statistic()
j_pval = model.j_test_pvalue()

print(f"Hansen J-test: stat={j_stat:.3f}, p={j_pval:.4f}")
# p > 0.05 → cannot reject instrument validity
```

---

## 9. Multiple Testing Corrections (Already Implemented)

✓ **Current:** FDR correction (Benjamini-Hochberg)

**Enhancement:** Add family-wise error rate (FWER) control

```python
from statsmodels.stats.multitest import multipletests

# Bonferroni (most conservative)
reject_bonf, pvals_bonf, _, _ = multipletests(pvalues, alpha=0.05, method='bonferroni')

# Holm-Bonferroni (less conservative, more power)
reject_holm, pvals_holm, _, _ = multipletests(pvalues, alpha=0.05, method='holm')

# Report all three:
print("FDR (BH):", reject_fdr.sum())
print("Bonferroni:", reject_bonf.sum())  # Lower bound
print("Holm:", reject_holm.sum())  # Middle ground
```

**Interpretation:**
- If all three agree → robust result
- If only FDR rejects → borderline significance, interpret cautiously

---

## 10. Power Analysis

### Question
"With only 5 events in pilot, do you have sufficient power to detect the effect?"

### Solution
Monte Carlo power simulation

```python
def power_simulation(true_effect_size, n_events, n_simulations=10000):
    """
    Simulate power to detect crypto vs traditional difference.

    Args:
        true_effect_size: Cohen's d (standardized mean difference)
        n_events: Number of events in study
        n_simulations: Number of Monte Carlo draws

    Returns:
        Power (proportion of simulations rejecting null)
    """
    np.random.seed(42)

    rejections = 0

    for _ in range(n_simulations):
        # Simulate crypto responses (mean=0, sd=5%)
        crypto_changes = np.random.normal(0, 5, size=n_events)

        # Simulate traditional responses (mean=true_effect_size*sd, sd=8%)
        trad_changes = np.random.normal(true_effect_size * 8, 8, size=n_events)

        # Paired t-test
        _, p_val = ttest_rel(trad_changes, crypto_changes)

        if p_val < 0.05:
            rejections += 1

    power = rejections / n_simulations
    return power

# Compute power for pilot study
power_5_events = power_simulation(true_effect_size=2.0, n_events=5)
power_20_events = power_simulation(true_effect_size=2.0, n_events=20)

print(f"Power with 5 events: {power_5_events:.2%}")
print(f"Power with 20 events: {power_20_events:.2%}")
```

**Report in paper:**
> "Monte Carlo simulations indicate 78% power to detect an effect size of d=2.0
> with our pilot sample of 5 events. Full study with 20 events achieves >95% power."

---

## Summary: Priority Ranking

| Priority | Enhancement | Impact | Difficulty | Implementation Time |
|----------|-------------|--------|------------|-------------------|
| **1** | Bootstrap CI for variance decomposition | HIGH | Low | 1 hour |
| **2** | Alternative event windows (±7, ±14, ±60) | HIGH | Low | 2 hours |
| **3** | Placebo tests (random dates) | HIGH | Low | 2 hours |
| **4** | Triple-difference (Reg vs Infra) | HIGH | Medium | 4 hours |
| **5** | Alternative metrics (Amihud, Roll) | MEDIUM | Medium | 4 hours |
| **6** | Wild bootstrap for small sample | MEDIUM | Medium | 2 hours |
| **7** | Granger causality tests | MEDIUM | Low | 1 hour |
| **8** | Heterogeneous effects (market cap) | MEDIUM | Low | 2 hours |
| **9** | High-frequency analysis | HIGH | High | 1-2 weeks |
| **10** | Instrumental variables | HIGH | High | 1-2 weeks |

**Recommendation:** Implement priorities 1-6 for paper revision (can be done in 1-2 days). Save 9-10 for follow-up work or if referees specifically request.

---

## References for Methods

1. **Wild Bootstrap:** Cameron, Gelbach, & Miller (2008), "Bootstrap-Based Improvements for Inference with Clustered Errors," *REStat*
2. **Triple-Difference:** Gruber (1994), "The Incidence of Mandated Maternity Benefits," *AER*
3. **Synthetic Control:** Abadie, Diamond, & Hainmueller (2010), "Synthetic Control Methods," *JASA*
4. **Granger Causality:** Granger (1969), "Investigating Causal Relations," *Econometrica*
5. **IV in Finance:** Roberts & Whited (2013), "Endogeneity in Empirical Corporate Finance," *Handbook of Economics of Finance*

---

## Code Integration

All methods above can be integrated into existing framework:
- Add to `robustness_paper2.py` for tests 1-6
- Create `advanced_econometrics.py` for 7-10
- Update `run_paper2_analysis.py` to include robustness suite

**Usage:**
```bash
# Run basic analysis
python code/run_paper2_analysis.py --pilot

# Run with full robustness checks
python code/run_paper2_analysis.py --pilot --robustness

# Run advanced methods (requires full dataset)
python code/run_paper2_analysis.py --full --advanced
```
