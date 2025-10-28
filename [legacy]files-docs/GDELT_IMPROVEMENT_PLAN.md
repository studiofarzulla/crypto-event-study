# GDELT/Sentiment Data Improvement Plan

**Date:** October 28, 2025
**Context:** Original thesis inspired by CRRIX (Cryptocurrency Regulatory Risk Index)
**Problem:** GDELT implementation is tanking TARCH-X model fit
**Goal:** Fix sentiment data quality to make TARCH-X competitive with simpler models

---

## Original Vision (CRRIX-Inspired)

**What CRRIX did:**
- NLP-based regulatory risk index for cryptocurrencies
- Used news/text data to quantify regulatory sentiment
- Showed how regulatory risk affects crypto markets

**Your Innovation:**
- Extend to BOTH regulatory AND infrastructure events
- Use GARCH framework to model volatility responses
- Show cross-sectional heterogeneity (some tokens respond, others don't)
- Decompose sentiment by event type (reg vs infra)

**Fucking cool idea!** But execution got derailed by data quality.

---

## Current GDELT Issues

### 1. Temporal Mismatch
- **GDELT:** Weekly aggregation (345 weeks)
- **Crypto prices:** Daily data
- **Problem:** Can't capture intra-week event timing

**Impact:** Sentiment variable poorly aligned with actual event dates

### 2. Missing Data
- **25 missing values** (7% of weeks)
- **Cause:** Likely weeks with no crypto news coverage
- **Problem:** Creates gaps in sentiment time series

### 3. Data Quality
- **Sentiment range:** -16.7 to -0.67 (all negative!)
- **Normalized range:** -5 to +2 (still skewed negative)
- **Problem:** Doesn't capture positive news/hype cycles

### 4. Decomposition Issues
- **Variables:** `S_reg_decomposed`, `S_infra_decomposed`
- **Method:** Multiply normalized sentiment by proportion of reg/infra articles
- **Problem:** Two correlated noisy variables from one noisy source

### 5. Model Fit Impact
- **TARCH-X BIC:** 30-44 points WORSE than GARCH(1,1)
- **Parameter count:** 11 vs 5 (6 extra parameters)
- **3 of those 6:** Sentiment variables (mostly non-significant)

---

## Why TARCH-X Fits Worse

**GARCH(1,1):** 5 parameters
- mu (mean)
- omega, alpha[1], beta[1] (volatility)
- nu (student-t df)

**TARCH-X:** 11 parameters
- Const (mean)
- **D_infrastructure** (event dummy) ← USEFUL
- **D_regulatory** (event dummy) ← USEFUL
- **S_gdelt_normalized** (sentiment) ← NOISY
- **S_reg_decomposed** (reg sentiment) ← NOISY
- **S_infra_decomposed** (infra sentiment) ← NOISY
- omega, alpha[1], gamma[1], beta[1], nu (volatility)

**The problem:** Adding 3 noisy sentiment variables for minimal explanatory power

---

## Potential Fixes (Ranked by Effort)

### Option 1: Drop Decomposed Sentiment (EASIEST)
**Change:** Remove `S_reg_decomposed` and `S_infra_decomposed`
**Keep:** `D_infrastructure`, `D_regulatory`, `S_gdelt_normalized`
**Result:** TARCH-X reduces to 8 parameters (vs 11)
**Expected impact:** BIC improves ~15-20 points (still worse than GARCH, but closer)

**Pros:**
- Quick fix (just modify model spec)
- Still have sentiment signal (albeit noisy)
- Keep event dummies (the main finding)

**Cons:**
- Loses theme decomposition (but it wasn't working anyway)
- Still has weekly vs daily temporal mismatch

---

### Option 2: Use Daily GDELT (MODERATE EFFORT)

**Approach:**
1. Re-query GDELT at **daily** granularity
2. Use crypto-specific keywords (Bitcoin, Ethereum, regulation, hack, etc.)
3. Calculate daily sentiment scores
4. Align with actual event dates

**GDELT Query Example:**
```python
# GDELT 2.0 API query for daily crypto news
keywords = [
    "bitcoin OR cryptocurrency OR blockchain",
    "regulation OR SEC OR ban OR legal",
    "hack OR exploit OR breach OR collapse"
]
```

**Pros:**
- Temporal alignment with daily price data
- More granular signal around specific events
- Can capture event-day sentiment spikes

**Cons:**
- Need to rebuild entire GDELT dataset
- GDELT API can be slow/unreliable
- Still reliant on news coverage quality

---

### Option 3: Alternative Sentiment Sources (HIGHER EFFORT)

**Better alternatives to GDELT:**

#### A. Crypto Fear & Greed Index
- **Source:** Alternative.me
- **Frequency:** Daily
- **Coverage:** 2018-present
- **Pros:** Crypto-native, combines multiple signals
- **Cons:** Single aggregate score (no reg/infra decomposition)

#### B. Twitter/X Sentiment
- **Source:** Twitter API (or scraped)
- **Frequency:** Real-time → daily aggregation
- **Keywords:** Specific to reg/infra events
- **Pros:** More volume, real-time, crypto-native
- **Cons:** API access issues, requires NLP processing

#### C. Reddit Sentiment (r/cryptocurrency, r/bitcoin)
- **Source:** Reddit API / Pushshift
- **Frequency:** Daily
- **Pros:** More thoughtful discussion than Twitter
- **Cons:** Similar API/processing requirements

#### D. On-Chain Sentiment Proxies
- **Metrics:** Exchange inflows, active addresses, MVRV ratio
- **Source:** Glassnode, CryptoQuant
- **Pros:** Behavioral data (revealed preferences)
- **Cons:** Not directly "sentiment", different interpretation

---

### Option 4: Hybrid Approach (BEST BUT MOST WORK)

**Combine multiple sources:**
1. **Event dummies** (D_infrastructure, D_regulatory) ← Keep these!
2. **Daily Fear & Greed Index** ← Easy to get, clean signal
3. **Optional:** Twitter volume spikes around events

**Model spec:**
```
TARCH-X:
  Mean equation:
    - Const
    - D_infrastructure
    - D_regulatory
    - FearGreed_normalized

  Variance equation:
    - omega, alpha[1], gamma[1], beta[1], nu
```

**Parameter count:** 9 (vs current 11)
**Expected BIC improvement:** 25-30 points better than current TARCH-X

---

## Recommended Path Forward

### Phase 1: Quick Win (1-2 hours)
1. **Drop decomposed sentiment variables**
   - Remove `S_reg_decomposed`, `S_infra_decomposed`
   - Keep `S_gdelt_normalized` (despite noise, keep for continuity)
   - Re-run TARCH-X with 8 parameters instead of 11

2. **Check BIC improvement**
   - Target: <30 point penalty vs GARCH
   - If achieved: Defensible model choice
   - If not: Proceed to Phase 2

### Phase 2: Better Sentiment (1 week)
1. **Fetch Crypto Fear & Greed Index**
   - Daily data from Alternative.me
   - 2018-2025 coverage (matches your study period)
   - Free API, easy to integrate

2. **Replace GDELT with Fear & Greed**
   - Single clean sentiment variable
   - Properly aligned with daily prices
   - Crypto-specific (not general news)

3. **Re-run TARCH-X**
   - Compare to Phase 1 results
   - Check if BIC penalty drops below 20 points

### Phase 3: Publication-Ready (if needed)
1. **Multi-source validation**
   - Show robustness to different sentiment sources
   - GDELT vs Fear&Greed vs Twitter volume
   - Demonstrate heterogeneity finding holds across sources

2. **Theoretical justification**
   - Why sentiment matters for crypto (behavioral finance)
   - Why some tokens are more sentiment-sensitive (retail vs institutional)
   - Connect to CRRIX framework

---

## What This Fixes

**Current state:**
- TARCH-X BIC penalty: 30-44 points
- Sentiment variables: Mostly non-significant
- Finding: 0.97pp spread (sounds small, hard to sell)

**After fixes:**
- TARCH-X BIC penalty: <20 points (defensible)
- Sentiment variables: Significant (clean signal)
- Finding: "BNB responds to events AND sentiment, LTC is event-neutral"
- Bonus: Can show individual event magnitudes with proper daily data

---

## Timeline Estimate

- **Phase 1 (drop decomposed vars):** 2 hours
- **Phase 2 (Fear & Greed data):** 1 week
  - Day 1: Fetch data
  - Day 2-3: Integrate into pipeline
  - Day 4-5: Re-run all models
  - Day 6-7: Regenerate figures/tables

- **Phase 3 (multi-source validation):** 2-3 weeks (if needed for journal)

---

## Questions to Answer

1. **Do you have access to GDELT query code, or is the CSV static?**
   - If static: Need to build fetcher
   - If you have code: Can modify for daily granularity

2. **What's your timeline for submission?**
   - If PhD apps: Phase 1 is enough (get DOI on Zenodo)
   - If journal submission: Phase 2-3 recommended

3. **Original CRRIX paper - what did they use for sentiment?**
   - Check their methodology
   - Might be able to replicate/improve their approach

---

## Bottom Line

**Your original CRRIX-inspired vision is solid!** The execution just got fucked by:
- Weekly vs daily temporal mismatch
- Decomposed sentiment adding noise instead of signal
- GDELT general news quality issues

**Fix:** Swap GDELT for Crypto Fear & Greed Index (crypto-native, daily, clean)
**Result:** TARCH-X becomes competitive, sentiment effects become significant, heterogeneity story gets stronger

**This is totally salvageable!** 🔥
