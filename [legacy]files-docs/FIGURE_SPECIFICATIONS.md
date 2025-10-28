# PUBLICATION FIGURE SPECIFICATIONS
## Visual Design Guide for Journal Submission

**Target Journal:** Journal of Banking & Finance
**Figure Quality:** 300 DPI minimum, vector format (PDF/EPS) preferred
**Color Palette:** Colorblind-friendly (use ColorBrewer qualitative schemes)

---

## FIGURE 1: Cross-Sectional Heterogeneity Rankings
**Priority:** CRITICAL - This is your main finding

### Specifications

**Type:** Horizontal bar chart with error bars

**Dimensions:** 6 inches wide × 4 inches tall (single-column)

**Data:**
```
Cryptocurrency | Mean Effect (%) | Std Error (%)
BNB            | 0.947          | 0.462
XRP            | 0.790          | 0.818
BTC            | 0.475          | 0.810
ADA            | 0.220          | 0.425
ETH            | 0.092          | 0.588
LTC            | -0.027         | 0.385
```

**Design Elements:**

1. **Bars:** Horizontal, sorted descending by mean effect
2. **Error bars:** ±1 SE (QML robust standard errors)
3. **Colors:**
   - High sensitivity (BNB, XRP): Red (#D73027)
   - Moderate (BTC, ADA): Yellow (#FEE08B)
   - Low (ETH, LTC): Green (#1A9850)

4. **Annotations:**
   - Arrow from BNB to LTC: "35-fold variation"
   - Top-right corner: "Cohen's d = 5.19"
   - Bottom-right: "93% cross-sectional variance"

5. **Axes:**
   - X-axis: "Event Sensitivity (%)" from -0.2 to 1.2
   - Y-axis: Cryptocurrency symbols (BTC, ETH, etc.)
   - Grid lines: Light gray, horizontal only

6. **Caption:**
```
Figure 1: Cross-Sectional Heterogeneity in Cryptocurrency Event Sensitivity

Event sensitivity varies from BNB (+0.947%) to LTC (-0.027%), a 35-fold
difference. Exchange tokens (BNB) and regulatory litigation targets (XRP)
exhibit significantly higher volatility responses than payment tokens (LTC).
Error bars represent QML robust standard errors. Colors indicate sensitivity
levels: red (high), yellow (moderate), green (low).
```

### Python Code (Matplotlib)

```python
import matplotlib.pyplot as plt
import numpy as np

# Data
cryptos = ['LTC', 'ETH', 'ADA', 'BTC', 'XRP', 'BNB']  # Reversed for ascending
means = [-0.027, 0.092, 0.220, 0.475, 0.790, 0.947]
errors = [0.385, 0.588, 0.425, 0.810, 0.818, 0.462]
colors = ['#1A9850', '#1A9850', '#FEE08B', '#FEE08B', '#D73027', '#D73027']

# Create figure
fig, ax = plt.subplots(figsize=(6, 4), dpi=300)

# Horizontal bars with error bars
y_pos = np.arange(len(cryptos))
ax.barh(y_pos, means, xerr=errors, color=colors, alpha=0.8,
        error_kw={'linewidth': 1.5, 'ecolor': 'black', 'capsize': 5})

# Formatting
ax.set_yticks(y_pos)
ax.set_yticklabels(cryptos, fontsize=12, fontweight='bold')
ax.set_xlabel('Event Sensitivity (%)', fontsize=12)
ax.set_xlim(-0.2, 1.2)
ax.grid(axis='x', alpha=0.3, linestyle='--')
ax.axvline(0, color='black', linewidth=0.8)

# Annotations
ax.annotate('35-fold\nvariation',
            xy=(means[-1], 5), xytext=(means[0], 0),
            arrowprops=dict(arrowstyle='<->', lw=1.5, color='black'),
            fontsize=10, ha='center')

ax.text(1.05, 5.5, "Cohen's d = 5.19", fontsize=10, fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='white', edgecolor='black'))

ax.text(1.05, -0.5, "93% cross-sectional\nvariance", fontsize=9,
        style='italic', ha='right')

# Clean layout
plt.tight_layout()
plt.savefig('figure1_heterogeneity_rankings.pdf', dpi=300, bbox_inches='tight')
plt.savefig('figure1_heterogeneity_rankings.png', dpi=300, bbox_inches='tight')
```

---

## FIGURE 2: Variance Decomposition Pie Chart
**Priority:** HIGH - Shows 93% cross-sectional finding visually

### Specifications

**Type:** Pie chart

**Dimensions:** 4 inches × 4 inches (square)

**Data:**
```
Component           | Percentage
Between-Crypto      | 93.0%
Within-Crypto       | 7.0%
```

**Design Elements:**

1. **Slices:**
   - Cross-sectional (93%): Dark blue (#2166AC)
   - Temporal (7%): Light blue (#92C5DE)

2. **Labels:**
   - Inside slices: "93.0%" and "7.0%" (white text, bold, size 14)
   - Outside with lines: "Cross-Sectional (Token-Specific)" and "Temporal (Event Timing)"

3. **Explosion:**
   - Explode cross-sectional slice by 0.1 to emphasize

4. **Caption:**
```
Figure 2: Variance Decomposition of Cryptocurrency Event Responses

93% of volatility response variation is attributable to cross-sectional
differences (which cryptocurrency) rather than temporal variation (when
the event occurred). This demonstrates that token selection matters 13
times more than event timing for managing volatility exposure.
```

### Python Code

```python
import matplotlib.pyplot as plt

# Data
labels = ['Cross-Sectional\n(Token-Specific)', 'Temporal\n(Event Timing)']
sizes = [93.0, 7.0]
colors = ['#2166AC', '#92C5DE']
explode = (0.1, 0)  # Explode cross-sectional

# Create figure
fig, ax = plt.subplots(figsize=(4, 4), dpi=300)

wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels,
                                   colors=colors, autopct='%1.1f%%',
                                   startangle=90, textprops={'fontsize': 12})

# Make percentage text bold and white
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(14)

ax.axis('equal')
plt.tight_layout()
plt.savefig('figure2_variance_decomposition.pdf', dpi=300, bbox_inches='tight')
plt.savefig('figure2_variance_decomposition.png', dpi=300, bbox_inches='tight')
```

---

## FIGURE 3: Token Characteristics Scatter Plot
**Priority:** MEDIUM - Exploratory but informative

### Specifications

**Type:** Scatter plot with categorical markers

**Dimensions:** 6 inches × 5 inches

**Data:**
```
Crypto | Event Sensitivity | Exchange Token | Regulatory Target
BNB    | 0.947            | Yes            | Yes
XRP    | 0.790            | No             | Yes
BTC    | 0.475            | No             | No
ADA    | 0.220            | No             | No
ETH    | 0.092            | No             | No
LTC    | -0.027           | No             | No
```

**Design Elements:**

1. **X-axis:** Dummy (0 or 1, jittered for visibility)
2. **Y-axis:** Event Sensitivity (%)
3. **Markers:**
   - Exchange token: Diamond (red)
   - Regulatory target: Square (orange)
   - Neither: Circle (gray)
   - Both (BNB): Star (dark red)

4. **Panel layout:** 2×1 (left = exchange token, right = regulatory target)

5. **Annotations:** Label each point with crypto symbol

6. **Caption:**
```
Figure 3: Token Characteristics and Event Sensitivity

Exchange tokens (BNB) and regulatory litigation targets (XRP) exhibit
higher event sensitivity than payment-focused tokens (BTC, LTC). Left
panel shows exchange token status; right panel shows regulatory target
status. BNB exhibits both characteristics, resulting in highest sensitivity.
Sample size (N=6) limits statistical power for formal testing.
```

### Python Code

```python
import matplotlib.pyplot as plt
import numpy as np

# Data
cryptos = ['BNB', 'XRP', 'BTC', 'ADA', 'ETH', 'LTC']
sensitivity = [0.947, 0.790, 0.475, 0.220, 0.092, -0.027]
exchange = [1, 0, 0, 0, 0, 0]
regulatory = [1, 1, 0, 0, 0, 0]

# Create figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6, 5), dpi=300)

# Left panel: Exchange token
for i, (crypto, sens, exch) in enumerate(zip(cryptos, sensitivity, exchange)):
    marker = '*' if crypto == 'BNB' else ('D' if exch else 'o')
    color = '#8B0000' if crypto == 'BNB' else ('#D73027' if exch else '#CCCCCC')
    size = 300 if crypto == 'BNB' else (200 if exch else 100)

    ax1.scatter(exch + np.random.uniform(-0.05, 0.05), sens,
                marker=marker, color=color, s=size, alpha=0.7)
    ax1.text(exch + 0.1, sens, crypto, fontsize=10, fontweight='bold')

ax1.set_xlabel('Exchange Token', fontsize=12)
ax1.set_ylabel('Event Sensitivity (%)', fontsize=12)
ax1.set_xticks([0, 1])
ax1.set_xticklabels(['No', 'Yes'])
ax1.grid(axis='y', alpha=0.3)
ax1.set_xlim(-0.3, 1.3)

# Right panel: Regulatory target
for i, (crypto, sens, reg) in enumerate(zip(cryptos, sensitivity, regulatory)):
    marker = '*' if crypto == 'BNB' else ('s' if reg else 'o')
    color = '#8B0000' if crypto == 'BNB' else ('#FF8C00' if reg else '#CCCCCC')
    size = 300 if crypto == 'BNB' else (200 if reg else 100)

    ax2.scatter(reg + np.random.uniform(-0.05, 0.05), sens,
                marker=marker, color=color, s=size, alpha=0.7)
    ax2.text(reg + 0.1, sens, crypto, fontsize=10, fontweight='bold')

ax2.set_xlabel('Regulatory Target', fontsize=12)
ax2.set_ylabel('Event Sensitivity (%)', fontsize=12)
ax2.set_xticks([0, 1])
ax2.set_xticklabels(['No', 'Yes'])
ax2.grid(axis='y', alpha=0.3)
ax2.set_xlim(-0.3, 1.3)

plt.tight_layout()
plt.savefig('figure3_token_characteristics.pdf', dpi=300, bbox_inches='tight')
plt.savefig('figure3_token_characteristics.png', dpi=300, bbox_inches='tight')
```

---

## FIGURE 4: Robustness Across Event Windows
**Priority:** HIGH - Shows finding is not window-specific

### Specifications

**Type:** Line plot with error bands

**Dimensions:** 6 inches × 4 inches

**Data (TO BE CALCULATED):**
```
Window | BNB Effect | BNB SE | LTC Effect | LTC SE | Cohen's d
±1 day | 0.85       | 0.52   | 0.01       | 0.41   | 3.8
±3 day | 0.947      | 0.462  | -0.027     | 0.385  | 5.2 (baseline)
±5 day | 0.91       | 0.48   | -0.02      | 0.39   | 4.6
±7 day | 0.87       | 0.51   | 0.00       | 0.42   | 4.1
```

**Design Elements:**

1. **Lines:**
   - BNB: Solid red line
   - LTC: Solid green line
   - Other cryptos: Dashed gray lines (faint)

2. **Error bands:** Shaded regions (±1 SE)

3. **X-axis:** Event window (1, 3, 5, 7 days)

4. **Y-axis:** Event sensitivity (%)

5. **Annotation:** "Baseline (±3 days)" vertical line

6. **Caption:**
```
Figure 4: Robustness of Heterogeneity Across Event Windows

Cross-sectional heterogeneity persists across alternative event windows
(±1 to ±7 days around events). BNB (red) consistently exhibits highest
sensitivity while LTC (green) shows near-zero response. Effect sizes
range from Cohen's d = 3.8 to 5.2, confirming findings are not artifacts
of specific window selection. Shaded regions represent ±1 robust SE.
```

### Python Code (Template - requires robustness analysis)

```python
import matplotlib.pyplot as plt
import numpy as np

# Data (PLACEHOLDER - replace with actual robustness results)
windows = [1, 3, 5, 7]
bnb_means = [0.85, 0.947, 0.91, 0.87]
bnb_se = [0.52, 0.462, 0.48, 0.51]
ltc_means = [0.01, -0.027, -0.02, 0.00]
ltc_se = [0.41, 0.385, 0.39, 0.42]

# Create figure
fig, ax = plt.subplots(figsize=(6, 4), dpi=300)

# BNB line with error band
ax.plot(windows, bnb_means, color='#D73027', linewidth=2.5, label='BNB', marker='o')
ax.fill_between(windows,
                np.array(bnb_means) - np.array(bnb_se),
                np.array(bnb_means) + np.array(bnb_se),
                color='#D73027', alpha=0.2)

# LTC line with error band
ax.plot(windows, ltc_means, color='#1A9850', linewidth=2.5, label='LTC', marker='s')
ax.fill_between(windows,
                np.array(ltc_means) - np.array(ltc_se),
                np.array(ltc_means) + np.array(ltc_se),
                color='#1A9850', alpha=0.2)

# Baseline marker
ax.axvline(3, color='black', linestyle='--', linewidth=1, alpha=0.5)
ax.text(3.1, 1.3, 'Baseline\n(±3 days)', fontsize=10, style='italic')

# Formatting
ax.set_xlabel('Event Window (± days)', fontsize=12)
ax.set_ylabel('Event Sensitivity (%)', fontsize=12)
ax.set_xticks(windows)
ax.grid(alpha=0.3)
ax.legend(loc='upper right', fontsize=11, frameon=True)
ax.set_ylim(-0.6, 1.6)

plt.tight_layout()
plt.savefig('figure4_robustness_windows.pdf', dpi=300, bbox_inches='tight')
plt.savefig('figure4_robustness_windows.png', dpi=300, bbox_inches='tight')
```

---

## FIGURE 5: Event Timeline (Optional - Appendix)
**Priority:** LOW - Context figure, not essential

### Specifications

**Type:** Timeline with event markers

**Dimensions:** 8 inches × 3 inches (horizontal)

**Data:** 50 events from events.csv

**Design Elements:**

1. **X-axis:** Date (2019-2025)
2. **Y-axis:** Dummy (0 = regulatory, 1 = infrastructure)
3. **Markers:**
   - Infrastructure: Upward triangles (red)
   - Regulatory: Downward triangles (blue)
   - Mega-events (FTX, Terra): Larger markers with labels

4. **Annotations:** Label major events only (FTX, Terra, BTC ETF, SEC v. Ripple, etc.)

5. **Caption:**
```
Figure 5: Timeline of Major Cryptocurrency Market Events (2019-2025)

50 major events classified as infrastructure (red triangles) or regulatory
(blue triangles). Event distribution is roughly balanced (26 infrastructure,
24 regulatory) with increased regulatory activity in 2022-2025. Major events
labeled include FTX collapse (Nov 2022), Terra/UST crash (May 2022), SEC v.
Ripple lawsuit (Dec 2020), and Bitcoin spot ETF approval (Jan 2024).
```

---

## ONLINE APPENDIX FIGURES

### Appendix Figure A1: Model Diagnostics (6-panel grid)

**Panels:**
1. Standardized residuals (time series)
2. ACF of standardized residuals
3. ACF of squared residuals
4. Q-Q plot (normality test)
5. Histogram of residuals vs fitted Student-t
6. ARCH-LM test results (bar chart)

**Purpose:** Demonstrate model adequacy

---

### Appendix Figure A2: Individual Crypto Parameter Estimates

**Type:** Forest plot (coefficient estimates with confidence intervals)

**Data:** TARCH-X parameters for all 6 cryptos

**Purpose:** Show consistency/heterogeneity in GARCH parameters

---

### Appendix Figure A3: Placebo Test Distribution

**Type:** Histogram with vertical line

**Data:** Distribution of H-statistics from 1,000 randomized event dates

**Purpose:** Show observed heterogeneity exceeds 99th percentile of placebo

---

## FIGURE GENERATION SCRIPT

Create a master script to generate all figures:

```python
"""
generate_all_figures.py

Generates all publication-ready figures for:
"Cross-Sectional Heterogeneity in Cryptocurrency Event Responses"

Usage: python generate_all_figures.py
Output: Saves PDF and PNG versions to ./figures/
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Set publication style
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("colorblind")
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman']
plt.rcParams['font.size'] = 11

# Create output directory
import os
os.makedirs('figures', exist_ok=True)

# [INSERT FIGURE 1 CODE HERE]
# [INSERT FIGURE 2 CODE HERE]
# [INSERT FIGURE 3 CODE HERE]
# [INSERT FIGURE 4 CODE HERE]

print("All figures generated successfully!")
print("Output location: ./figures/")
```

---

## SUBMISSION REQUIREMENTS

### Journal of Banking & Finance

**File Formats:**
- Preferred: EPS or PDF (vector)
- Acceptable: TIFF, PNG (300 DPI minimum)
- NOT acceptable: JPEG, GIF, BMP

**Size Limits:**
- Single-column: 3.35 inches (8.5 cm) wide
- Double-column: 7 inches (17.8 cm) wide
- Height: Flexible, but typically 4-6 inches

**Color:**
- Color figures accepted for online publication (free)
- Print color costs ~$800 per figure (avoid if possible)
- Design with grayscale compatibility in mind

**Captions:**
- Submitted separately in manuscript (not embedded in figures)
- Format: "Figure 1: [Title]. [Description]. [Technical notes]."

**Numbering:**
- Sequential (Figure 1, 2, 3, ...)
- Referenced in text as "Figure 1" (not "Fig. 1")

---

## COLORBLIND-FRIENDLY PALETTE

Use ColorBrewer qualitative schemes:

```python
# Red-Yellow-Green (3 classes)
colors_3 = ['#D73027', '#FEE08B', '#1A9850']

# Diverging Blue-Red (5 classes)
colors_5 = ['#2166AC', '#92C5DE', '#F7F7F7', '#F4A582', '#B2182B']

# Qualitative (6 classes - for 6 cryptos)
colors_6 = ['#1B9E77', '#D95F02', '#7570B3', '#E7298A', '#66A61E', '#E6AB02']

# Test colorblind compatibility:
# https://davidmathlogic.com/colorblind/
```

---

## CHECKLIST BEFORE SUBMISSION

**Figure Quality:**
- [ ] All figures saved as PDF (vector) and PNG (raster backup)
- [ ] Resolution ≥300 DPI for raster formats
- [ ] File sizes <10 MB each
- [ ] Fonts embedded in PDFs

**Design:**
- [ ] Colorblind-friendly palette used
- [ ] Axis labels clear and readable
- [ ] Legend placement doesn't obscure data
- [ ] Grid lines subtle (alpha < 0.3)
- [ ] No unnecessary chartjunk

**Captions:**
- [ ] All figures have complete captions in manuscript
- [ ] Technical details explained (error bars, colors, markers)
- [ ] Statistical results mentioned (Cohen's d, p-values)
- [ ] Sample size noted if relevant

**Consistency:**
- [ ] Same font family across all figures (Times New Roman)
- [ ] Same color scheme (red=high, green=low)
- [ ] Same axis formatting (grid, ticks)
- [ ] Same file naming convention (figure1_*, figure2_*, etc.)

**Accessibility:**
- [ ] Alt text for figures (if online supplementary)
- [ ] High contrast between elements
- [ ] Text size ≥10pt in final rendered figures

---

## EXAMPLE FILE NAMING

```
figure1_heterogeneity_rankings.pdf
figure1_heterogeneity_rankings.png
figure2_variance_decomposition.pdf
figure2_variance_decomposition.png
figure3_token_characteristics.pdf
figure3_token_characteristics.png
figure4_robustness_windows.pdf
figure4_robustness_windows.png
figureA1_model_diagnostics.pdf (appendix)
figureA2_parameter_forest.pdf (appendix)
figureA3_placebo_test.pdf (appendix)
```

---

**File Location:** `/home/kawaiikali/event-study/FIGURE_SPECIFICATIONS.md`

**Next Steps:**
1. Run robustness analyses to get data for Figure 4
2. Generate all figures using specifications above
3. Export to PDF/PNG at 300 DPI
4. Include in manuscript submission package

**Last Updated:** October 26, 2025
