# STEP-BY-STEP INTEGRATION INSTRUCTIONS
**Dissertation:** Cross-Sectional Heterogeneity in Cryptocurrency Volatility
**Date:** October 26, 2025
**Estimated Time:** 90-120 minutes

---

## BEFORE YOU START

### Prerequisites:
- [ ] Microsoft Word installed
- [ ] Original dissertation open: `MURAD_FARZULLA_AG44473.docx`
- [ ] This file open: `INTEGRATION_INSTRUCTIONS.md`
- [ ] Ready-to-paste sections open: `ROBUSTNESS_SECTIONS_READY.md`
- [ ] Updated abstract open: `UPDATED_ABSTRACT.md`

### Backup:
```bash
# Create backup before making changes
cp MURAD_FARZULLA_AG44473.docx MURAD_FARZULLA_AG44473_BACKUP.docx
```

---

## STEP 1: SAVE AS NEW FILE (5 minutes)

1. Open `MURAD_FARZULLA_AG44473.docx` in Microsoft Word
2. **File → Save As**
3. **New filename:** `FARZULLA_2025_CRYPTO_HETEROGENEITY.docx`
4. **Location:** `/home/kawaiikali/event-study/`
5. Click **Save**

✅ **Checkpoint:** New file created, original unchanged

---

## STEP 2: UPDATE TITLE PAGE (5 minutes)

### Current Title Section:
```
AG44473
(Candidate Number)
```

### New Title Section:
```
Cross-Sectional Heterogeneity in Cryptocurrency Volatility Event Responses:
Evidence from TARCH-X Analysis

Murad Farzulla
Farzulla Research

October 2025
```

**Action:**
1. Navigate to title page (first page after coversheet)
2. Replace candidate number with academic title
3. Add author name and affiliation
4. Update date to October 2025

✅ **Checkpoint:** Title page professional and publication-ready

---

## STEP 3: REPLACE ABSTRACT (10 minutes)

### Location: Section 0 (Abstract)

**Action:**
1. Navigate to "0. Abstract" section
2. Select entire abstract paragraph (NOT the heading)
3. Open `UPDATED_ABSTRACT.md`
4. Copy the full abstract text
5. Paste to replace existing abstract

**Verify new abstract includes:**
- [ ] "35-fold variation" mentioned
- [ ] "placebo test p<0.001" mentioned
- [ ] "Spearman ρ = 1.00" mentioned
- [ ] "45% variance reduction" mentioned
- [ ] "93% of response variation" mentioned

✅ **Checkpoint:** Abstract updated with robustness mentions

---

## STEP 4: ENHANCE SECTION 4.6.2 PLACEBO TEST (15 minutes)

### Location: Section 4.6.2 (Placebo Test)

**Current content:** Basic placebo test description

**Action:**
1. Navigate to end of Section 4.6.2
2. Add a new paragraph AFTER existing content
3. Open `ROBUSTNESS_SECTIONS_READY.md`
4. Copy section "4.6.2 Enhanced Placebo Test"
5. Paste at end of 4.6.2

**New content should include:**
- [ ] "1,000 randomly assigned event dates"
- [ ] "Kruskal-Wallis H-statistic (10.31) exceeds 95th percentile"
- [ ] "p<0.001"
- [ ] "2.1× higher heterogeneity"

✅ **Checkpoint:** Placebo test enhanced with 1,000-permutation details

---

## STEP 5: ADD SECTION 4.6.4 ALTERNATIVE WINDOWS (15 minutes)

### Location: AFTER Section 4.6.3 (Winsorization Impact)

**Action:**
1. Navigate to end of Section 4.6.3
2. Insert new heading: "4.6.4 Alternative Event Window Specifications"
3. Use Heading 3 style (match 4.6.1, 4.6.2, 4.6.3)
4. Open `ROBUSTNESS_SECTIONS_READY.md`
5. Copy section "4.6.4 Alternative Event Windows"
6. Paste under new heading

**New section should include:**
- [ ] Four window specifications (±1, ±3, ±5, ±7 days)
- [ ] Cohen's d ranges (1.68 to 2.43)
- [ ] Spearman ρ > 0.85
- [ ] Sign stability 88.9%

**Optional figure reference:**
Add after last paragraph:
```
Figure X shows robustness of token rankings across alternative event window
specifications. (See FIGURE_INSERTION_GUIDE.md for figure placement)
```

✅ **Checkpoint:** New subsection 4.6.4 added

---

## STEP 6: ADD SECTION 4.6.5 TEMPORAL STABILITY (15 minutes)

### Location: AFTER Section 4.6.4

**Action:**
1. Navigate to end of Section 4.6.4
2. Insert new heading: "4.6.5 Temporal Stability Across Market Regimes"
3. Use Heading 3 style
4. Open `ROBUSTNESS_SECTIONS_READY.md`
5. Copy section "4.6.5 Temporal Stability"
6. Paste under new heading

**New section should include:**
- [ ] Two periods: Early (2019-2021) vs Late (2022-2025)
- [ ] "Spearman rank correlation: ρ = 1.00 (p<0.001)"
- [ ] "Zero ranking changes"
- [ ] "Perfect ranking stability"
- [ ] Cohen's d comparison (2.51 vs 2.50)

**Optional figure reference:**
Add after last paragraph:
```
Table X presents cross-sectional rankings by period, demonstrating perfect
stability. (See FIGURE_INSERTION_GUIDE.md for table placement)
```

✅ **Checkpoint:** New subsection 4.6.5 added

---

## STEP 7: VERIFY/UPDATE CORRELATION MATRIX (20 minutes)

### Location: Section 4.7 (Economic Significance)

**Critical Check:**
Does your dissertation have a correlation matrix? If yes, check the values.

**⚠️ IF CORRELATION MATRIX HAS PERFECT ±1.0 VALUES:**
This is wrong. Replace with corrected matrix from `ROBUSTNESS_SECTIONS_READY.md`.

**Steps:**
1. Navigate to Section 4.7 (or wherever portfolio implications are)
2. Find correlation matrix table
3. **Check diagonal values:**
   - If all diagonal = 1.000 AND all off-diagonal = ±1.000 or ±0.999 → WRONG
   - If off-diagonal range 0.3 to 0.7 → CORRECT, skip to Step 8

**If matrix is WRONG:**
1. Select entire correlation matrix table
2. Delete it
3. Open `ROBUSTNESS_SECTIONS_READY.md`
4. Copy "Corrected Correlation Matrix"
5. Paste to replace

**Also update portfolio metrics if wrong:**
- Variance reduction: Change from ~2% to **45.18%**
- BNB-LTC correlation: Change from ~1.0 to **0.387**
- Diversification ratio: Change from ~2.0 to **1.3567**

**Add note under correlation matrix:**
```
Note: Correlations calculated from daily conditional volatility time-series
(N=2,800 observations), not aggregated event means. This correction ensures
realistic portfolio diversification metrics.
```

✅ **Checkpoint:** Correlation matrix verified/corrected

---

## STEP 8: UPDATE CONCLUSION (10 minutes)

### Location: Section 5.1 (Summary)

**Action:**
1. Navigate to Section 5.1
2. Find last paragraph of summary
3. Add new paragraph AFTER existing summary
4. Open `ROBUSTNESS_SECTIONS_READY.md`
5. Copy "Conclusion Addition"
6. Paste as new paragraph

**New paragraph should include:**
- [ ] "placebo tests... p<0.001"
- [ ] "perfectly stable... ρ = 1.00"
- [ ] "alternative event window specifications"
- [ ] "sign stability 88.9%"
- [ ] "structural token characteristics"

✅ **Checkpoint:** Conclusion emphasizes robustness

---

## STEP 9: ADD REPRODUCIBILITY STATEMENT (15 minutes)

### Location: NEW section after 5.4 or before Section 6

**Action:**
1. Navigate to end of Section 5.4 (Future Research)
2. Insert new heading: "5.5 Code and Data Availability"
3. Use Heading 2 style (match 5.1, 5.2, 5.3, 5.4)
4. Open `ROBUSTNESS_SECTIONS_READY.md`
5. Copy section "5.5 Reproducibility Statement"
6. Paste under new heading

**New section should include:**
- [ ] Data sources (CoinGecko, GDELT)
- [ ] Zenodo DOI placeholder
- [ ] List of 6 repository components
- [ ] Note about bug fixes

**⚠️ IMPORTANT:**
Replace `[INSERT DOI]` with actual Zenodo DOI when available.
For now, leave as placeholder or use: `[DOI to be assigned upon publication]`

✅ **Checkpoint:** Reproducibility section added

---

## STEP 10: INSERT FIGURES (15 minutes)

### Optional but Recommended

**See:** `FIGURE_INSERTION_GUIDE.md` for detailed instructions

**Quick summary:**
1. **Figure 4 (Placebo Test):** After Section 4.6.2
2. **Figure 5 (Alternative Windows):** After Section 4.6.4
3. **Figure 6 (Temporal Stability):** After Section 4.6.5

**Process:**
1. Navigate to insertion point
2. **Insert → Picture → From File**
3. Select figure from `publication_figures/` directory
4. **Right-click → Wrap Text → Top and Bottom**
5. Add caption: **References → Insert Caption**
6. Update figure numbering throughout document

✅ **Checkpoint:** Figures inserted (optional)

---

## STEP 11: UPDATE REFERENCES (10 minutes)

### Verify all new citations

**Check if these appear in References section:**
- [ ] Benjamini & Hochberg (1995) - FDR correction
- [ ] Storey (2002) - q-values
- [ ] Any new robustness test references

**If missing, add to Section 7 (References):**

See `ROBUSTNESS_SECTIONS_READY.md` → "Additional References" for BibTeX entries.

✅ **Checkpoint:** References complete

---

## STEP 12: FINAL VERIFICATION (15 minutes)

### Use INTEGRATION_CHECKLIST.md

**Critical checks:**
- [ ] Title changed from candidate number to academic title
- [ ] Abstract mentions robustness (p<0.001, ρ=1.00, 88.9%)
- [ ] Section 4.6 has 5 subsections (added 4.6.4 and 4.6.5)
- [ ] Correlation matrix has realistic values (0.3-0.7 range) OR was correct
- [ ] Reproducibility statement added (Section 5.5)
- [ ] Conclusion emphasizes robustness validation
- [ ] All new text reads smoothly (no copy-paste artifacts)
- [ ] Figure numbers updated if figures inserted
- [ ] No "TODO" or placeholder text remaining (except Zenodo DOI if not ready)

**Word count check:**
- Original: ~15,000-20,000 words
- New: Should be ~15,500-20,600 words (+500-600)

**Proofread new sections:**
1. Read aloud all new paragraphs
2. Check for:
   - Typos
   - Missing periods
   - Formatting consistency
   - Proper citation style

✅ **Checkpoint:** All verifications complete

---

## STEP 13: SAVE AND EXPORT (5 minutes)

### Save final version

1. **File → Save** (save as .docx)
2. **File → Save As → PDF**
   - Filename: `FARZULLA_2025_CRYPTO_HETEROGENEITY.pdf`
   - Purpose: For easy distribution and Zenodo upload

### Create backup

```bash
# Copy final version to safe location
cp FARZULLA_2025_CRYPTO_HETEROGENEITY.docx ~/Documents/Resurrexi/publications/
cp FARZULLA_2025_CRYPTO_HETEROGENEITY.pdf ~/Documents/Resurrexi/publications/
```

✅ **Checkpoint:** Files saved and backed up

---

## COMPLETION CHECKLIST

### Verify integration success:

- [ ] **Step 1:** New file created with academic title
- [ ] **Step 2:** Title page updated
- [ ] **Step 3:** Abstract replaced with robustness mentions
- [ ] **Step 4:** Section 4.6.2 enhanced (1,000 permutations)
- [ ] **Step 5:** Section 4.6.4 added (alternative windows)
- [ ] **Step 6:** Section 4.6.5 added (temporal stability)
- [ ] **Step 7:** Correlation matrix verified/corrected
- [ ] **Step 8:** Conclusion updated
- [ ] **Step 9:** Reproducibility section added (5.5)
- [ ] **Step 10:** Figures inserted (optional)
- [ ] **Step 11:** References verified
- [ ] **Step 12:** Final verification complete
- [ ] **Step 13:** Files saved and backed up

### Word count increase:
- [ ] Added ~500-600 words to dissertation

### Key robustness statistics mentioned:
- [ ] Placebo test: p<0.001
- [ ] Temporal stability: ρ = 1.00
- [ ] Alternative windows: 88.9% sign stability
- [ ] Cross-sectional heterogeneity: 35-fold, 93%

---

## TROUBLESHOOTING

### Problem: Can't find Section 4.6
**Solution:** Use Ctrl+F (Find) to search for "4.6" or "Robustness"

### Problem: Formatting breaks when pasting
**Solution:**
1. Paste as plain text first (Ctrl+Shift+V)
2. Then reformat using existing paragraph styles

### Problem: Figure numbers don't update
**Solution:**
1. Select all (Ctrl+A)
2. Right-click → Update Field (F9)

### Problem: Abstract too long
**Solution:**
- Use concise version from UPDATED_ABSTRACT.md
- Journal abstracts typically 200-250 words

### Problem: Not sure if correlation matrix is wrong
**Solution:**
- If ANY off-diagonal value is ±1.000 or ±0.999 → WRONG
- If range is 0.3 to 0.7 → CORRECT

---

## NEXT STEPS AFTER INTEGRATION

### Prepare for publication:
1. [ ] Get Zenodo DOI for code/data
2. [ ] Replace `[INSERT DOI]` placeholder
3. [ ] Final proofread (consider professional editing)
4. [ ] Share with co-authors/advisors for review
5. [ ] Prepare journal submission package
6. [ ] Upload to Zenodo with manuscript

### Timeline:
- **Today:** Complete integration (2 hours)
- **This week:** Proofread and refine
- **Next week:** Get Zenodo DOI
- **Week 3:** Submit to journal

---

## SUPPORT

If you encounter issues:
1. Check `TROUBLESHOOTING` section above
2. Review `INTEGRATION_CHECKLIST.md` for verification steps
3. Consult `ROBUSTNESS_SECTIONS_READY.md` for original text

**All integration materials complete. Ready to proceed with manual integration.**

---

**Document:** INTEGRATION_INSTRUCTIONS.md
**Created:** October 26, 2025
**Purpose:** Step-by-step guide for dissertation integration
**Status:** Complete and ready to use
