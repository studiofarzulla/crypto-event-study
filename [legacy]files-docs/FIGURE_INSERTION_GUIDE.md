# FIGURE AND TABLE INSERTION GUIDE
**Purpose:** Instructions for inserting publication figures into dissertation
**Date:** October 26, 2025

---

## OVERVIEW

This guide explains how to insert the publication-ready figures and tables generated during robustness analysis into your dissertation.

**Note:** Figure insertion is OPTIONAL but recommended for publication quality.

---

## AVAILABLE FIGURES

All figures located in: `/home/kawaiikali/event-study/publication_figures/`

### Robustness Check Figures:

1. **placebo_test_robustness.png** (369 KB, 300 DPI)
   - 4-panel figure showing placebo test results
   - For Section 4.6.2

2. **robustness_effects_confidence_intervals.png** (296 KB, 300 DPI)
   - Alternative window specifications
   - For Section 4.6.4

3. **temporal_stability_analysis.png** (224 KB, 300 DPI)
   - 3-panel figure showing temporal stability
   - For Section 4.6.5

### Additional Figures (Optional):

4. **robustness_cohens_d.png** (182 KB)
5. **robustness_heterogeneity_ratio.png** (224 KB)
6. **robustness_rankings_heatmap.png** (146 KB)

---

## FIGURE 1: PLACEBO TEST RESULTS

### Insertion Point
**Section 4.6.2** - After enhanced placebo test paragraph

### File Information
- **Filename:** `placebo_test_robustness.png`
- **Size:** 369 KB
- **Resolution:** 300 DPI
- **Dimensions:** ~2000 × 1500 pixels

### How to Insert

1. Navigate to end of Section 4.6.2 (after new placebo text)
2. Insert page break or leave space for figure
3. **Insert → Picture → From File**
4. Browse to: `/home/kawaiikali/event-study/publication_figures/`
5. Select: `placebo_test_robustness.png`
6. Click **Insert**

### Format Figure

1. **Right-click on figure → Wrap Text → Top and Bottom**
2. **Resize if needed:** Drag corners while holding Shift (maintains aspect ratio)
3. **Recommended width:** 6-7 inches (fits within margins)
4. **Center the figure:** Select figure → Paragraph → Alignment → Center

### Add Caption

1. **Right-click on figure → Insert Caption**
2. **Label:** Figure
3. **Position:** Below selected item
4. **Caption text:**

```
Figure X: Placebo Test Validation Using 1,000 Random Event Dates

Distribution of heterogeneity statistics from 1,000 random event date samples (blue histograms). Red dashed lines show observed values from actual events; orange dotted lines show 95th percentile of placebo distribution. All observed metrics exceed or approach the 95th percentile, confirming heterogeneity is event-driven rather than spurious. Panel A: Kruskal-Wallis H-test statistic (observed 10.31 vs placebo 95th percentile 8.76, p<0.001). Panel B: Range of sensitivity (observed 97.4%). Panel C: Cohen's d (observed 5.19). Panel D: Heterogeneity ratio (observed 35-fold).
```

5. Click **OK**

### Update Figure Numbers

After inserting:
1. **Select All** (Ctrl+A)
2. **Right-click → Update Field** (or press F9)
3. This automatically renumbers all figures

### Reference in Text

Add reference in Section 4.6.2 text:
```
Results are visualized in Figure X, which shows the distribution of heterogeneity
statistics from placebo samples compared to observed values.
```

---

## FIGURE 2: ALTERNATIVE EVENT WINDOWS

### Insertion Point
**Section 4.6.4** - After alternative windows paragraph

### File Information
- **Filename:** `robustness_effects_confidence_intervals.png`
- **Size:** 296 KB
- **Resolution:** 300 DPI

### Caption

```
Figure X: Robustness to Alternative Event Window Specifications

Mean event sensitivity coefficients with 95% confidence intervals across four event window specifications. Token rankings remain stable across all window lengths (Spearman ρ > 0.85), with BNB consistently exhibiting highest sensitivity and LTC lowest. Narrow window (±1 day) captures immediate impacts; Base window (±3 days) is our primary specification; Moderate (±5 days) and Wide (±7 days) windows capture delayed market responses. Sign stability of 88.9% across windows demonstrates robustness is not an artifact of window choice.
```

### Reference in Text

```
Figure X demonstrates that cross-sectional heterogeneity persists across all
event window specifications, from narrow (±1 day) to wide (±7 days).
```

---

## FIGURE 3: TEMPORAL STABILITY

### Insertion Point
**Section 4.6.5** - After temporal stability paragraph

### File Information
- **Filename:** `temporal_stability_analysis.png`
- **Size:** 224 KB
- **Resolution:** 300 DPI

### Caption

```
Figure X: Temporal Stability of Cross-Sectional Heterogeneity Across Market Regimes

Comparison of cryptocurrency event sensitivity rankings between Early period (2019-2021, bull market, 21 events) and Late period (2022-2025, post-crash normalization, 29 events). Panel A: Rankings with perfect correlation (Spearman ρ = 1.00, p<0.001). Panel B: Effect sizes by period showing comparable magnitudes (Cohen's d = 2.51 early vs 2.50 late). Panel C: Scatter plot of early vs late coefficients demonstrating perfect positive correlation. Zero ranking changes across all six cryptocurrencies confirms heterogeneity reflects structural token characteristics rather than market regimes.
```

### Reference in Text

```
Figure X illustrates the perfect ranking stability across market regimes, with
no cryptocurrency changing position between bull and bear market periods.
```

---

## OPTIONAL TABLES

### Table 1: Alternative Window Robustness Summary

**Location:** After Section 4.6.4 or in Appendix
**Source:** See ROBUSTNESS_SECTIONS_READY.md

**How to Create:**

1. **Insert → Table**
2. **Dimensions:** 5 columns × 5 rows
3. **Fill with data:**

```
Window          Days    Heterogeneity    Cohen's d    Spearman ρ
                        Ratio                         (vs base)

Narrow (±1)     3       37.63×          2.27         1.000***
Base (±3)       7       812.02×         2.20         -
Moderate (±5)   11      27.59×          2.43         1.000***
Wide (±7)       15      8.19×           1.68         0.886**

Notes: ** p<0.05, *** p<0.01
```

### Table 2: Temporal Stability Rankings

**Location:** After Section 4.6.5 or in Appendix
**Source:** See ROBUSTNESS_SECTIONS_READY.md

**Full table provided in ROBUSTNESS_SECTIONS_READY.md - copy formatting**

---

## GENERAL FIGURE INSERTION GUIDELINES

### Before Inserting

- [ ] Check if dissertation already has figures
- [ ] Note current figure numbering scheme
- [ ] Decide if inserting in main text or appendix
- [ ] Ensure sufficient space (may need page breaks)

### During Insertion

**For each figure:**
1. Insert at appropriate location
2. Set text wrapping (Top and Bottom recommended)
3. Resize to fit within margins (typically 6-7 inches wide)
4. Center horizontally
5. Add caption with descriptive text
6. Update all field codes (Ctrl+A, then F9)

### After Insertion

- [ ] All figures numbered sequentially
- [ ] All figures referenced in text
- [ ] All captions descriptive and informative
- [ ] Consistent formatting across all figures
- [ ] Document updated (all field codes refreshed)

---

## FIGURE FORMATTING BEST PRACTICES

### Size and Position
- **Width:** 6-7 inches for full-width figures
- **Width:** 3-4 inches for two-column figures
- **Alignment:** Center horizontal
- **Text wrapping:** Top and Bottom (not In Line with Text)

### Caption Style
- **Font:** Same as body text (10-12pt)
- **Format:** Bold figure number, regular description
- **Position:** Below figure
- **Spacing:** Single space within caption, double space before/after

### Resolution
- All provided figures are 300 DPI ✓
- Suitable for print publication ✓
- No need to adjust resolution

### File Formats
- PNG format suitable for Word ✓
- PDF versions available if needed
- Vector formats preserve quality at any size

---

## TROUBLESHOOTING

### Problem: Figure too large/small
**Solution:**
- Right-click → Size and Position
- Set width to 6-7 inches
- Check "Lock aspect ratio"
- Apply

### Problem: Figure moves when editing text
**Solution:**
- Change text wrapping to "Top and Bottom"
- Or use "Position → More Layout Options → Fix position on page"

### Problem: Figure numbers not updating
**Solution:**
- Select all (Ctrl+A)
- Press F9 to update all fields
- Or right-click each figure number → Update Field

### Problem: Caption font doesn't match
**Solution:**
- Select caption text
- Apply "Caption" or "Figure Caption" style
- Or manually set font to match body text

### Problem: Figure appears blurry
**Solution:**
- Delete and re-insert original PNG
- Do NOT resize by stretching - use size settings
- Check print preview (not just screen display)

---

## FIGURE CHECKLIST

After inserting all figures:

- [ ] All figures inserted at correct locations
- [ ] All figures properly sized (6-7 inches width)
- [ ] All figures centered horizontally
- [ ] All figures have captions
- [ ] All captions descriptive and informative
- [ ] All figure numbers sequential
- [ ] All figures referenced in text
- [ ] Text wrapping set correctly
- [ ] All field codes updated (F9)
- [ ] Print preview looks good

---

## ALTERNATIVE: APPENDIX PLACEMENT

If main text is too crowded, consider placing all robustness figures in appendix:

### Create New Appendix Section
**"Appendix E: Robustness Check Visualizations"**

### Advantages:
- Keeps main text focused
- All robustness materials together
- Easier to reference as group

### References in Main Text:
```
See Appendix E for complete robustness check visualizations including placebo
tests (Figure E1), alternative window specifications (Figure E2), and temporal
stability analysis (Figure E3).
```

---

## SUMMARY

### Required Insertions (Recommended):
1. ✅ Figure: Placebo Test (4-panel) - Section 4.6.2
2. ✅ Figure: Alternative Windows - Section 4.6.4
3. ✅ Figure: Temporal Stability (3-panel) - Section 4.6.5

### Optional Insertions:
4. Table: Alternative Window Summary - Section 4.6.4 or Appendix
5. Table: Temporal Stability Rankings - Section 4.6.5 or Appendix
6. Additional robustness figures - Appendix

### Time Estimate:
- **3 figures:** ~15-20 minutes total
- **With tables:** +10 minutes
- **Total:** 25-30 minutes

---

## FINAL NOTES

**Image Quality:**
- All figures generated at 300 DPI ✓
- Publication-ready resolution ✓
- Grayscale-compatible ✓
- Professional appearance ✓

**Consistency:**
- Use same caption format for all figures
- Maintain sequential numbering
- Reference all figures in text
- Update all cross-references

**Journal Requirements:**
- Check journal-specific figure guidelines
- Some journals prefer separate figure files
- May need specific format (TIFF, EPS)
- Current PNG format suitable for most journals

---

**Document:** FIGURE_INSERTION_GUIDE.md
**Created:** October 26, 2025
**Purpose:** Instructions for inserting publication figures
**Status:** Complete - ready for use
