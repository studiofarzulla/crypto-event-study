# Methodology: Sentiment Without Structure

## Research Design

### Core Question
Why do regulatory events cause weak volatility responses in cryptocurrency markets compared to traditional markets?

### Hypothesis
Cryptocurrency markets exhibit **no microstructure response** to regulation because:
1. Decentralized architecture prevents regulatory enforcement at protocol level
2. Global orderbooks enable instant migration to unregulated jurisdictions
3. No central exchange means no enforceable structural rules

Result: Regulation affects only **sentiment** (narrative), not **structure** (market mechanics)

---

## Empirical Strategy

### Phase 1: Microstructure Event Study

**Design:** Difference-in-differences around regulatory events

**Treatment:** Cryptocurrency asset (BTC)
**Control:** Traditional asset (SPY)
**Event:** Regulatory announcement (N=20 events, 2019-2025)

**Metrics:**
- Bid-ask spread (percentage): `(ask - bid) / midpoint × 100`
- Order book depth: Sum of bid/ask sizes at top 10 levels
- Trading volume: Daily volume in USD
- Price impact: `|ΔPrice| / Volume^0.5` (Kyle's lambda)

**Test:**
```
H0_crypto: ΔSpread = 0 (no microstructure change)
H0_trad:   ΔSpread ≠ 0 (significant microstructure change)
H0_diff:   ΔSpread_trad - ΔSpread_crypto > 0
```

**Event Window:**
- Pre-event baseline: [t-30, t-1]
- Post-event impact: [t+1, t+30]
- Immediate impact: [t-3, t+3]

---

### Phase 2: Extended TARCH-X with Microstructure

**Model Specification:**

σ²_t = ω + α·ε²_{t-1} + γ·ε²_{t-1}·I(ε_{t-1}<0) + β·σ²_{t-1}
       + δ_reg·D_regulatory_t        (from Paper 1)
       + δ_sent·Sentiment_t           (from Paper 1)
       + θ_spread·Spread_t            (NEW)
       + θ_depth·Depth_t              (NEW)

**Key Parameters:**
- **δ_reg:** Direct regulatory event effect
- **δ_sent:** Sentiment channel effect
- **θ_spread:** Microstructure (spread) channel effect
- **θ_depth:** Microstructure (depth) channel effect

**Hypothesis:**
- Crypto: θ_spread ≈ 0, θ_depth ≈ 0 (no microstructure channel)
- Traditional: θ_spread > 0, θ_depth < 0 (significant channel)

---

### Phase 3: Variance Decomposition

**Decompose regulatory volatility impact:**

Total Impact = δ_reg

Sentiment Component = δ_sent × Avg(Sentiment | D_regulatory = 1)
Microstructure Component = θ_spread × Avg(ΔSpread | D_regulatory = 1)
                          + θ_depth × Avg(ΔDepth | D_regulatory = 1)
Direct Component = Total - Sentiment - Microstructure

**Calculate Shares:**
```
Sentiment Share = Sentiment Component / Total Impact
Microstructure Share = Microstructure Component / Total Impact
Direct Share = Direct Component / Total Impact
```

**Expected:**
- Crypto: 70-80% sentiment, 0-5% microstructure, 15-25% direct
- Traditional: 20-30% sentiment, 50-70% microstructure, 10-20% direct

---

### Phase 4: Volume Migration Analysis

**Test jurisdictional arbitrage:**

Regulated Share_t = (Volume_Coinbase + Volume_Kraken) / Volume_Global

**Hypothesis:** After regulatory event, `Regulated Share` declines as trading migrates to offshore venues

**Statistical Test:**
```
Pre-event:  Regulated Share = baseline
Post-event: Regulated Share < baseline (significant decline)
```

**Mechanism:**
1. US regulation announced
2. US exchanges face compliance costs → spreads widen
3. Traders migrate to Binance/OKX (offshore)
4. Global price unaffected (arbitrage equalizes)
5. **No structural change** at global level

---

## Data Requirements

### Crypto Microstructure

**Source:** Binance API (free), Kaiko (premium)

**Metrics:**
- 1-minute orderbook snapshots
- Top 10 price levels
- Bid/ask prices and sizes
- Trade volumes

**Assets:** BTC, ETH, XRP, BNB, LTC, ADA

**Period:** 2019-01-01 to 2025-01-31

**Frequency:** Daily aggregates for event study

### Traditional Microstructure

**Source:** WRDS TAQ (ideal), Yahoo Finance (proxy)

**Metrics:**
- Quoted spread (from TAQ)
- Effective spread (from trades)
- Depth at best bid/ask
- Volume

**Assets:** SPY, GLD, XLF, QQQ

**Period:** Matched to crypto (2019-2025)

**Note:** Yahoo Finance provides only OHLC, so we use `(high - low) / close` as spread proxy

### Event Database

**From Paper 1:** 50 curated events
**Filter:** 20 regulatory events (type = 'Regulatory')

**Additions:**
- SEC enforcement actions
- CFTC announcements
- International regulatory changes (EU MiCA, UK FCA)
- Exchange regulations (Binance bans, Coinbase restrictions)

### Exchange Volume Data

**Source:** CoinGecko API, Nomics

**Metrics:**
- Daily volume by exchange
- Separate regulated (Coinbase, Kraken, Gemini) vs unregulated (Binance, OKX, Bybit)

**Calculation:**
```python
regulated_share = (Volume_Coinbase + Volume_Kraken + Volume_Gemini) / Volume_Global
```

---

## Statistical Methods

### Event Study Tests

**T-test for microstructure changes:**
```python
pre_spread = spread[t-30:t-1]
post_spread = spread[t+1:t+30]
t_stat, p_value = ttest_ind(post_spread, pre_spread)
```

**Difference-in-differences:**
```python
DiD = (post_trad - pre_trad) - (post_crypto - pre_crypto)
```

### Extended TARCH-X Estimation

**Optimization:** SLSQP with constraints
- Stationarity: α + β + |γ|/2 < 0.999
- Positivity: ω, α, β > 0
- Student-t: 2 < ν < 50

**Standard Errors:** Numerical Hessian (as in Paper 1)

**Model Selection:** AIC, BIC comparison

### Multiple Testing Correction

**FDR Correction:** Benjamini-Hochberg procedure
- Alpha = 0.10 for event study (20 events × 4 metrics = 80 tests)
- Control false discovery rate

### Robustness Checks

1. **Alternative event windows:** ±7, ±14, ±30 days
2. **Different asset pairs:** ETH vs Gold, BNB vs Financials
3. **Subsample analysis:** Pre-2022 vs Post-2022
4. **Bootstrap confidence intervals:** 1000 replications

---

## Comparison to Paper 1

### Paper 1 (Infrastructure vs Regulatory)

**Question:** Do infrastructure events cause larger volatility than regulatory?
**Answer:** Yes, 5.7× larger (2.385% vs 0.419%)

**Method:** TARCH-X with event dummies and sentiment

**Finding:** Infrastructure > Regulatory (empirical fact)

### Paper 2 (Sentiment Without Structure)

**Question:** WHY are regulatory effects weak in crypto?
**Answer:** No microstructure channel (only sentiment)

**Method:** Extended TARCH-X + microstructure variables + comparative analysis

**Finding:** Mechanism identification (explains Paper 1)

### Connection

Paper 1 provides:
- Empirical motivation (weak regulatory effects)
- Methodology foundation (TARCH-X)
- Event classification
- GDELT sentiment data

Paper 2 extends:
- Adds microstructure variables to variance equation
- Compares crypto vs traditional markets
- Decomposes variance into channels
- Tests volume migration hypothesis

**Together:** Complete story of how crypto markets process regulatory information differently from traditional markets

---

## Expected Timeline

### Pilot Study (Complete)
- 5 events, BTC vs SPY
- Tests methodology
- Runtime: ~10 minutes

### Full Data Collection (2-3 months)
- 20 events × 6 cryptos × 4 traditional assets
- Orderbook data from exchanges
- Volume migration tracking

### Analysis & Estimation (1 month)
- Extended TARCH-X for all assets
- Variance decomposition
- Robustness checks

### Writing & Refinement (2 months)
- Draft manuscript
- Figures and tables
- Conference presentations

**Total:** ~5-6 months to submission

---

## Key Innovations

1. **First comparative microstructure study** (crypto vs traditional)
2. **Variance channel decomposition** (sentiment vs microstructure)
3. **Volume migration as regulatory circumvention** mechanism
4. **Sentiment as microstructure substitute** theoretical framework

---

## Potential Extensions

1. **ETF comparison:** BTC spot vs IBIT ETF (tests if regulation works when enforceable)
2. **Cross-country analysis:** US vs EU vs Asia regulatory divergence
3. **Time-varying effects:** Does microstructure channel emerge as crypto matures?
4. **DeFi protocols:** Truly unregulatable markets (Uniswap, Curve)

---

## References to Paper 1

All references to Paper 1 methods:
- TARCH-X specification: Paper 1, Section 3.2
- Event classification: Paper 1, Table 1
- GDELT methodology: Paper 1, Appendix A
- Stationarity constraints: Paper 1, Bug Fix Summary

This ensures consistency and builds credibly on established foundations.
