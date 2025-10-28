# Publication-Quality Visualization System

**Event Study: Infrastructure vs Regulatory Events in Cryptocurrency Markets**

## Overview

This visualization system generates publication-ready figures for top-tier finance journals (JoF, JFE, RFS). All figures meet strict academic publishing standards:

- **Vector graphics** (PDF/SVG, not raster PNG)
- **Grayscale-friendly** (uses patterns and shapes, not just colors)
- **LaTeX-compatible fonts** (Times New Roman/serif)
- **High resolution** (300 DPI)
- **Clear statistical notation** (significance markers, confidence intervals)
- **Professional layout** (consistent spacing, proper legends)

## File Structure

```
/home/kawaiikali/event-study/
├── create_publication_figures.py      # Main visualization generator
├── data_preparation_template.py       # Template for formatting your data
├── data/                              # Input data (you create these)
│   ├── events.csv
│   ├── volatility_results.csv
│   ├── impact_matrix.csv
│   └── model_results.csv
└── publication_figures/               # Output directory (auto-created)
    ├── figure1_event_timeline.pdf
    ├── figure1_event_timeline.svg
    ├── figure2_volatility_comparison.pdf
    ├── figure2_volatility_comparison.svg
    ├── figure3_impact_heatmap.pdf
    ├── figure3_impact_heatmap.svg
    ├── figure4_model_comparison.pdf
    └── figure4_model_comparison.svg
```

## Quick Start

### Option 1: Run with Example Data (Demo)

```bash
cd /home/kawaiikali/event-study
python create_publication_figures.py
```

This generates all four figures using synthetic example data to demonstrate the output format.

### Option 2: Use Your Actual Data

1. **Prepare your data files** (see Data Format Requirements below)
2. **Save to** `/home/kawaiikali/event-study/data/`
3. **Run the generator:**

```bash
python create_publication_figures.py
```

## Data Format Requirements

### 1. events.csv

Event-level data with impact magnitudes and significance.

**Columns:**
- `date` (str): Event date in YYYY-MM-DD format
- `event_name` (str): Short descriptive name (e.g., "FTX Collapse")
- `event_type` (str): Either "infrastructure" or "regulatory"
- `impact_magnitude` (float): Cumulative abnormal return (decimal, e.g., 0.05 = 5%)
- `p_value` (float): Statistical significance from event study test

**Example:**
```csv
date,event_name,event_type,impact_magnitude,p_value
2022-11-08,FTX Collapse,infrastructure,-0.087,0.001
2022-09-15,Ethereum Merge,infrastructure,0.042,0.023
2023-06-13,SEC vs Ripple Ruling,regulatory,0.065,0.008
```

### 2. volatility_results.csv

Volatility dynamics across event periods.

**Columns:**
- `period` (str): One of:
  - `"Pre-Event\n(-10 to -1)"`
  - `"Event\n(0 to +5)"`
  - `"Post-Event\n(+6 to +20)"`
- `event_type` (str): "infrastructure" or "regulatory"
- `mean_volatility` (float): Average realized volatility in % per day
- `ci_lower` (float): Lower 95% confidence interval bound
- `ci_upper` (float): Upper 95% confidence interval bound

**Example:**
```csv
period,event_type,mean_volatility,ci_lower,ci_upper
"Pre-Event\n(-10 to -1)",infrastructure,2.45,2.15,2.75
"Event\n(0 to +5)",infrastructure,4.12,3.78,4.46
"Post-Event\n(+6 to +20)",infrastructure,3.05,2.71,3.39
```

### 3. impact_matrix.csv

Cross-sectional event impacts (Event × Cryptocurrency matrix).

**Format:**
- **Index:** Event names (matching events.csv)
- **Columns:** Cryptocurrency tickers (BTC, ETH, etc.)
- **Values:** Cumulative abnormal returns (%)

**Example:**
```csv
,BTC,ETH,BNB,SOL,ADA,XRP
FTX Collapse,-0.052,-0.089,-0.067,-0.145,-0.078,-0.034
Ethereum Merge,0.023,0.087,0.034,0.045,0.067,0.012
SEC vs Ripple,0.015,0.008,0.011,-0.003,0.009,0.156
```

### 4. model_results.csv

Model comparison statistics.

**Columns:**
- `model_name` (str): Name of the model (e.g., "GARCH(1,1)", "Market Model")
- `rmse` (float): Root mean squared error from out-of-sample forecasts
- `mae` (float): Mean absolute error
- `aic` (float): Akaike Information Criterion
- `bic` (float): Bayesian Information Criterion

**Example:**
```csv
model_name,rmse,mae,aic,bic
Market Model,3.452,2.763,4521.34,4536.78
GARCH(1,1),2.871,2.314,4398.67,4429.54
EGARCH,2.923,2.356,4405.23,4436.01
```

## Figure Descriptions

### Figure 1: Event Timeline Visualization

**Purpose:** Shows chronological sequence of all 18 events with impact magnitudes

**Features:**
- Timeline with dates on x-axis
- Impact magnitude (CAR) on y-axis
- Different markers for infrastructure (circles) vs regulatory (squares)
- Statistical significance markers (*, **, ***)
- Grayscale colors with distinct shapes

**Use in paper:** Introduction or descriptive statistics section

### Figure 2: Volatility Response Comparison

**Purpose:** Compares volatility dynamics before/during/after events

**Features:**
- Side-by-side panels (infrastructure vs regulatory)
- Three periods: Pre-Event, Event Window, Post-Event
- 95% confidence intervals (error bars)
- Hatching patterns for grayscale distinction

**Use in paper:** Main results section, tests H2 on volatility persistence

### Figure 3: Cross-Sectional Impact Heatmap

**Purpose:** Shows which events affected which cryptocurrencies most

**Features:**
- Matrix visualization (events × cryptocurrencies)
- Red-gray diverging colormap (works in grayscale)
- Values printed in cells
- Grid lines for clarity

**Use in paper:** Cross-sectional analysis, robustness checks

### Figure 4: Model Performance Comparison

**Purpose:** Evaluates forecast accuracy and model selection

**Features:**
- Four-panel layout (RMSE, MAE, AIC, BIC)
- Best-performing model highlighted with different pattern
- All bars with professional hatching

**Use in paper:** Methodology validation, out-of-sample tests

## Customization Options

### Modify Visual Style

Edit the configuration section in `create_publication_figures.py`:

```python
# Change font size
plt.rcParams['font.size'] = 11  # Default: 10

# Enable LaTeX rendering (requires LaTeX installation)
plt.rcParams['text.usetex'] = True

# Change figure dimensions
fig, ax = plt.subplots(figsize=(14, 6))  # Width, height in inches
```

### Add More Cryptocurrencies

Simply add columns to `impact_matrix.csv`. The heatmap will auto-adjust.

### Change Event Windows

Modify the period labels in `volatility_results.csv`:
```python
'period': ['Pre-Event\n(-20 to -1)', 'Event\n(0 to +10)', 'Post-Event\n(+11 to +30)']
```

### Add More Models

Add rows to `model_results.csv`. The bar charts will auto-scale.

## Statistical Significance Convention

The figures use standard econometrics notation:

- `*` p < 0.10 (10% significance)
- `**` p < 0.05 (5% significance)
- `***` p < 0.01 (1% significance)

These markers appear automatically based on p-values in your data.

## Publication Checklist

Before submitting to journal:

- [ ] All figures generated as vector graphics (PDF/SVG)
- [ ] Figures print clearly in grayscale
- [ ] All axes labeled with units
- [ ] Font sizes readable at reduced size (75% of original)
- [ ] Statistical significance properly marked
- [ ] Legends placed inside plot area (not outside)
- [ ] Consistent style across all figures
- [ ] Figure captions prepared (see example below)

## Example Figure Captions

**Figure 1:** Event Timeline and Impact Magnitudes. This figure shows the chronological sequence of 18 major events affecting cryptocurrency markets from 2022-2024. Infrastructure events (circles) include technological upgrades and platform incidents. Regulatory events (squares) include policy announcements and legal decisions. The y-axis shows cumulative abnormal returns (CAR) over the event window [0, +5]. Statistical significance: * p < 0.10, ** p < 0.05, *** p < 0.01.

**Figure 2:** Volatility Dynamics Around Infrastructure and Regulatory Events. This figure compares realized volatility (% per day) across three periods: pre-event window [-10, -1], event window [0, +5], and post-event window [+6, +20]. Panel A shows infrastructure events; Panel B shows regulatory events. Error bars represent 95% confidence intervals estimated using robust standard errors.

**Figure 3:** Cross-Sectional Event Impact Matrix. This heatmap displays cumulative abnormal returns (CAR) for each cryptocurrency (columns) during each event (rows). Darker shades indicate larger absolute impacts. Values are expressed as percentages. The matrix reveals heterogeneous responses across cryptocurrencies and event types.

**Figure 4:** Model Performance Comparison. This figure evaluates competing volatility models using out-of-sample forecasts. Panel (a) shows root mean squared error (RMSE), panel (b) shows mean absolute error (MAE), panel (c) shows Akaike Information Criterion (AIC), and panel (d) shows Bayesian Information Criterion (BIC). Lighter bars with cross-hatching indicate best performance within each metric.

## Technical Dependencies

Required Python packages:
```bash
pip install numpy pandas matplotlib seaborn
```

Optional (for LaTeX rendering):
```bash
# On Arch Linux:
sudo pacman -S texlive-core texlive-latexextra

# Then enable in script:
plt.rcParams['text.usetex'] = True
```

## Troubleshooting

### "FileNotFoundError: data/events.csv"

**Solution:** Create the data files first. Run `data_preparation_template.py` to see the expected format.

### Figures look pixelated

**Solution:** You're viewing the PNG preview. Open the PDF/SVG files for vector graphics.

### LaTeX errors

**Solution:** Set `plt.rcParams['text.usetex'] = False` in the script. LaTeX rendering is optional.

### Fonts not found

**Solution:** Install Times New Roman fonts or use default serif fonts (already configured as fallback).

### Colors not grayscale-friendly

**Solution:** The script already uses hatching patterns. Print a test page to verify.

## Advanced: Integrating with Your Analysis Pipeline

If you have an existing event study script, you can call the visualization functions directly:

```python
# In your main analysis script
from create_publication_figures import (
    create_event_timeline,
    create_volatility_comparison,
    create_impact_heatmap,
    create_model_comparison
)

# After calculating results:
create_event_timeline(events_df)
create_volatility_comparison(volatility_df)
# ... etc
```

## Contact & Support

This visualization system was designed for rigorous academic research. If you need to adapt it for a different context:

1. Read the inline documentation in `create_publication_figures.py`
2. Check the data preparation template for format examples
3. Test with example data first before using real data

## Citation

If you use this visualization system in published research, consider acknowledging it in your methodology section:

> "Figures were generated using custom Python scripts designed for publication-quality academic visualizations, following standards recommended by the Journal of Finance style guide."

## License

These scripts are provided as research tools. Modify freely for your academic work.

---

**Version:** 1.0
**Last Updated:** October 2025
**Compatibility:** Python 3.8+, matplotlib 3.3+
