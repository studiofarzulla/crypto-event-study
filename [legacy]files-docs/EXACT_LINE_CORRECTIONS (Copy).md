# Exact Line-by-Line Corrections

**Purpose:** Show exactly what text to find and replace in dissertation files

---

## File 1: Farzulla_2025_Cryptocurrency_Heterogeneity.md

### Line 413 (Section 4.3.1 - Results)

**CURRENT (WRONG):**
```
Converting variance coefficients to volatility percentage changes (using pre-event baseline volatilities), infrastructure events increase conditional volatility by an average of 18.4% compared to 16.7% for regulatory events, a directionally consistent but statistically insignificant difference (t = 0.276, p = 0.795). The lack of statistical significance despite directional consistency across most assets suggests either insufficient statistical power given the small number of events per type or that the high persistence in variance processes absorbs discrete event shocks into the long-memory component.
```

**CORRECTED:**
```
Infrastructure events demonstrate mean variance coefficient impacts of 41.7% compared to 41.5% for regulatory events, a statistically insignificant difference (t = 0.006, p = 0.995). The lack of statistical significance despite directional consistency across five of six cryptocurrencies suggests either insufficient statistical power given the small number of event types or that the high persistence in variance processes absorbs discrete event shocks into the long-memory component.
```

**Changes made:**
- ❌ Removed: "Converting variance coefficients to volatility percentage changes (using pre-event baseline volatilities)"
- ✅ Changed: 18.4% → 41.7%
- ✅ Changed: 16.7% → 41.5%
- ✅ Changed: t = 0.276 → t = 0.006
- ✅ Changed: p = 0.795 → p = 0.995
- ✅ Clarified: "across most assets" → "across five of six cryptocurrencies"

---

### Line 535 (Section 5.1 - Discussion/Conclusion)

**CURRENT (WRONG):**
```
Our findings reveal a nuanced picture that challenges straightforward characterizations of cryptocurrency market dynamics. While infrastructure events demonstrate consistently larger volatility impacts than regulatory events across five of six cryptocurrencies, with average conditional volatility increases of 18.4% versus 16.7%, these differences lack statistical significance at conventional levels (p = 0.795). The directional consistency suggests potential economic importance despite insufficient statistical power, particularly given that individual infrastructure events like the FTX bankruptcy and Terra/Luna collapse generated volatility spikes exceeding 60% above baseline levels.
```

**CORRECTED:**
```
Our findings reveal a nuanced picture that challenges straightforward characterizations of cryptocurrency market dynamics. While infrastructure events demonstrate consistently larger volatility impacts than regulatory events across five of six cryptocurrencies, with average variance coefficient impacts of 41.7% versus 41.5%, these differences lack statistical significance at conventional levels (p = 0.995). The directional consistency suggests potential economic importance despite insufficient statistical power, particularly given that individual infrastructure events like the FTX bankruptcy and Terra/Luna collapse generated volatility spikes exceeding 60% above baseline levels.
```

**Changes made:**
- ✅ Changed: "conditional volatility increases of 18.4% versus 16.7%" → "variance coefficient impacts of 41.7% versus 41.5%"
- ✅ Changed: p = 0.795 → p = 0.995

---

## File 2: dissertation-integrated.md

### Line 514 (Section 4.3.1)

**Same as File 1, Line 413** - Apply identical correction

### Line 636 (Section 5.1)

**Same as File 1, Line 535** - Apply identical correction

---

## File 3: dissertation-original.md

### Line 106 (Abstract or Executive Summary)

**CURRENT (WRONG):**
```
Our findings reveal that while infrastructure events consistently show larger volatility impacts than regulatory events across five of six cryptocurrencies (average increases of 18.4% versus 16.7%), these differences lack statistical significance (p = 0.795) after appropriate multiple testing corrections.
```

**CORRECTED:**
```
Our findings reveal that while infrastructure events consistently show larger volatility impacts than regulatory events across five of six cryptocurrencies (average variance coefficient impacts of 41.7% versus 41.5%), these differences lack statistical significance (p = 0.995) after appropriate multiple testing corrections.
```

### Line 500 (Section 4.3.1)

**Same as File 1, Line 413** - Apply identical correction

### Line 579 (Section 5.1)

**Same as File 1, Line 535** - Apply identical correction

---

## File 4: Farzulla_2025_Cryptocurrency_Heterogeneity.html

### Lines 1712, 2013

**Note:** HTML file should be **regenerated from corrected markdown** rather than manually edited. After correcting the .md files, run:

```bash
pandoc Farzulla_2025_Cryptocurrency_Heterogeneity.md -o Farzulla_2025_Cryptocurrency_Heterogeneity.html
```

---

## Methodology Section Clarification (All Files)

### Section 3.4.4 - Event Coefficient Interpretation

**CURRENT:**
```
Event coefficients (δ_j) in the TARCH-X specification represent linear additions to conditional variance rather than multiplicative or log-variance effects. Specifically, during event periods, the conditional variance becomes σ²_t = baseline + δ_j where δ_j captures the absolute increase in variance (in squared percentage points). Economic interpretation of event effects therefore follows: a coefficient of δ_j = 0.5 indicates the event increases daily conditional variance by 0.5 squared percentage points. To express this as a relative increase, I calculate (δ_j / σ²_baseline) × 100, where σ²_baseline represents average pre-event conditional variance. This approach maintains consistency with the linear variance specification whilst providing economically meaningful effect magnitudes.
```

**RECOMMENDED CORRECTION:**
```
Event coefficients (δ_j) in the TARCH-X specification represent linear additions to conditional variance rather than multiplicative or log-variance effects. Specifically, during event periods, the conditional variance becomes σ²_t = baseline + δ_j where δ_j captures the absolute increase in variance. Economic interpretation of event effects therefore follows: a coefficient of δ_j = 0.5 indicates the event increases daily conditional variance by 0.5 squared percentage points. Reported percentages (e.g., 41.7%) represent the coefficient expressed as percentage points (δ_j × 100), maintaining consistency with the linear variance specification whilst providing economically meaningful effect magnitudes.
```

**Changes made:**
- ❌ Removed: "To express this as a relative increase, I calculate (δ_j / σ²_baseline) × 100, where σ²_baseline represents average pre-event conditional variance."
- ✅ Added: "Reported percentages (e.g., 41.7%) represent the coefficient expressed as percentage points (δ_j × 100)"

**Rationale:** The original text claims to normalize by baseline variance, but the code doesn't do this. The correction makes the text match what the code actually does.

---

## Quick Search Terms for Finding All Instances

### Use these search strings to find any remaining instances:

1. **Search for:** `18.4`
   - Should find: ~8 instances across dissertation files
   - Replace with: `41.7`

2. **Search for:** `16.7`
   - Should find: ~8 instances
   - Replace with: `41.5`

3. **Search for:** `0.795`
   - Should find: ~8 instances
   - Replace with: `0.995`

4. **Search for:** `0.276`
   - Should find: ~3 instances
   - Replace with: `0.006`

5. **Search for:** `baseline volatilities`
   - Should find: ~3 instances
   - Review context and remove claims about baseline normalization

---

## Verification Checklist

After making corrections:

- [ ] All instances of "18.4%" changed to "41.7%"
- [ ] All instances of "16.7%" changed to "41.5%"
- [ ] All instances of "p = 0.795" changed to "p = 0.995"
- [ ] All instances of "t = 0.276" changed to "t = 0.006"
- [ ] Methodology section no longer claims baseline normalization
- [ ] Abstract updated (if it contains these values)
- [ ] HTML file regenerated from corrected markdown
- [ ] DOCX file regenerated (if applicable)
- [ ] Visual check: No tables or figures show old values

---

## Files That Should NOT Be Changed

These files already have the CORRECT values:

- ✅ `PUBLICATION_ANALYTICS_FINAL.md`
- ✅ `event_study/outputs/analysis_results/hypothesis_test_results.csv`
- ✅ `event_study/outputs/publication/csv_exports/event_impacts_fdr.csv`
- ✅ `QUICK_REFERENCE_STATS.md`
- ✅ `publication_analysis_output.txt`

Leave these alone - they're already correct!

---

**Last Updated:** October 26, 2025
