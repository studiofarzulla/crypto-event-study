# Publication Pipeline Documentation

**Cryptocurrency Event Study - Output Generation Layer**
**Last Updated:** October 28, 2025
**Repository:** `/home/kawaiikali/event-study/`

---

## Overview

The publication pipeline transforms statistical analysis results into publication-ready outputs for academic journals (Journal of Finance, Journal of Banking & Finance, RFS). This layer handles:

1. **LaTeX table generation** - Formatted tables with statistical significance markers
2. **Publication-quality figures** - Vector graphics (PDF/SVG) with grayscale-friendly styling
3. **CSV data exports** - Raw results for appendices and robustness checks
4. **Diagnostic visualizations** - Model validation and quality checks

---

## Architecture

```
Analysis Results → Publication Formatting → Output Artifacts
     ↓                      ↓                       ↓
┌─────────────┐    ┌──────────────┐    ┌──────────────────┐
│ Model       │    │ LaTeX        │    │ Tables (.tex)    │
│ Results     │───▶│ Generation   │───▶│ Figures (.pdf)   │
│ (Dict)      │    │              │    │ CSV (.csv)       │
└─────────────┘    └──────────────┘    └──────────────────┘
       │                   │
       ▼                   ▼
┌─────────────┐    ┌──────────────┐
│ Analysis    │    │ Figure       │
│ Results     │───▶│ Generation   │
│ (Dict)      │    │ (matplotlib) │
└─────────────┘    └──────────────┘
```

---

## Core Publication Scripts

### 1. `publication_outputs.py` - Main Output Generator

**Class:** `PublicationOutputs`

**Purpose:** Unified interface for generating all publication artifacts from model results.

**Input Requirements:**
```python
PublicationOutputs(
    model_results: Dict,      # GARCH model results by crypto
    analysis_results: Dict,   # Hypothesis tests, event impacts, etc.
    crypto_data: Dict         # Prepared cryptocurrency data
)
```

**Generated Outputs:**

| Output Type | Filename | Format | Purpose |
|------------|----------|--------|---------|
| Model Comparison Table | `model_comparison.tex` | LaTeX | AIC/BIC statistics across GARCH models |
| Event Comparison Table | `event_comparison.tex` | LaTeX | Infrastructure vs Regulatory hypothesis test |
| Leverage Parameters Table | `leverage_parameters.tex` | LaTeX | Asymmetric volatility effects |
| Volatility Timeline Plot | `volatility_major_events.png` | PNG | Volatility around major events (FTX, Terra/Luna, BTC ETF) |
| Diagnostic Plots | `diagnostic_plots.png` | PNG | ACF of squared residuals + Q-Q plots |
| Event Impact Comparison | `event_impact_comparison.png` | PNG | Bar chart with confidence intervals |
| Model Parameters CSV | `{crypto}_parameters.csv` | CSV | Parameter estimates with std errors |
| Model Comparison CSV | `model_comparison.csv` | CSV | AIC/BIC/log-likelihood comparison |
| Event Impacts CSV | `event_impacts_fdr.csv` | CSV | Event coefficients with FDR correction |
| Hypothesis Test CSV | `hypothesis_test.csv` | CSV | t-test and Mann-Whitney results |

**Key Methods:**

```python
# LaTeX table generation
generate_latex_model_comparison_table() → str
generate_latex_event_comparison_table() → str
generate_latex_leverage_table() → str

# Figure generation
plot_volatility_around_events(major_events: List[Tuple])
plot_diagnostic_charts()
plot_event_impact_comparison()

# CSV exports
export_all_to_csv()

# Master function
generate_all_outputs()  # Generates everything
```

**Output Directory Structure:**
```
outputs/publication/
├── latex/
│   ├── model_comparison.tex
│   ├── event_comparison.tex
│   └── leverage_parameters.tex
├── csv_exports/
│   ├── btc_parameters.csv
│   ├── eth_parameters.csv
│   ├── xrp_parameters.csv
│   ├── model_comparison.csv
│   ├── event_impacts_fdr.csv
│   └── hypothesis_test.csv
└── [PNG figures in root]
    ├── volatility_major_events.png
    ├── diagnostic_plots.png
    └── event_impact_comparison.png
```

**Publication Quality Settings:**
```python
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 10
```

---

### 2. `create_publication_figures.py` - Advanced Figure Generator

**Purpose:** Creates 4 main publication-quality figures for top-tier finance journals.

**Target Journals:** Journal of Finance (JoF), Journal of Financial Economics (JFE), Review of Financial Studies (RFS)

**Requirements:**
- Vector graphics (PDF/SVG)
- Grayscale-friendly (patterns + shapes, not just colors)
- LaTeX-compatible fonts (Times New Roman)
- 300 DPI resolution

**Generated Figures:**

| Figure | Filename | Visualization | Data Required |
|--------|----------|---------------|---------------|
| Figure 1 | `figure1_event_timeline` | Timeline with event impacts and significance markers | `events_df` (date, event_name, type, impact, p_value) |
| Figure 2 | `figure2_volatility_comparison` | Pre/during/post event volatility comparison | `volatility_df` (period, event_type, mean_vol, CI) |
| Figure 3 | `figure3_impact_heatmap` | Event × Crypto impact matrix | `impact_matrix` (events × cryptos) |
| Figure 4 | `figure4_model_comparison` | 4-panel model performance (RMSE, MAE, AIC, BIC) | `model_results` (model metrics) |

**Color Palette (Grayscale-Friendly):**
```python
COLORS = {
    'infrastructure': '#000000',  # Black
    'regulatory': '#666666',      # Dark gray
    'primary': '#000000',
    'secondary': '#4D4D4D',
    'tertiary': '#999999',
    'light': '#CCCCCC',
}

PATTERNS = {
    'infrastructure': '///',
    'regulatory': '\\\\\\',
    'significant': 'xxx',
    'non_significant': '...',
}
```

**Output Directory:** `/home/kawaiikali/event-study/publication_figures/`

**Formats:** PDF (vector, required) + SVG (backup)

---

### 3. `generate_latex_tables.py` - Standalone Table Generator

**Purpose:** Generate LaTeX tables independent of main analysis pipeline.

**Output Directory:** `/home/kawaiikali/event-study/publication_tables/`

**Generated Tables:**

| Table | Filename | Content | LaTeX Packages Required |
|-------|----------|---------|------------------------|
| Table 1 | `table1_event_study_results.tex` | Event CAR with t-stats | booktabs, threeparttable |
| Table 2 | `table2_descriptive_statistics.tex` | Return statistics (mean, std, skew, kurtosis) | booktabs, threeparttable |
| Table 3 | `table3_volatility_models.tex` | GARCH parameter estimates | booktabs, threeparttable |
| Table 4 | `table4_regression_results.tex` | Cross-sectional regression results | booktabs, threeparttable |
| Master | `all_tables.tex` | Compilable document including all tables | geometry |

**Key Functions:**

```python
format_coef_se(coef, se, pval) → Tuple[str, str]
    # Formats coefficients with significance stars
    # *** p<0.01, ** p<0.05, * p<0.10

generate_event_study_table(results_df) → Path
generate_descriptive_stats_table(data_df) → Path
generate_volatility_model_table(model_results) → Path
generate_regression_table(regression_results) → Path
create_master_latex_file() → Path
```

**LaTeX Format Standards:**
- Uses `\toprule`, `\midrule`, `\bottomrule` from booktabs
- Panel structure for grouped results (Panel A: Infrastructure, Panel B: Regulatory)
- Tablenotes with methodology descriptions
- Significance markers as superscripts

**Master File Usage:**
```bash
pdflatex all_tables.tex  # Compiles all tables into one document
```

---

### 4. `create_heterogeneity_figures.py` - Key Results Visualization

**Purpose:** Generate the 3 KEY FIGURES emphasizing the main contribution: 97.4 percentage point spread in cross-sectional heterogeneity.

**Target Journal:** Journal of Banking & Finance

**Main Finding:** BNB (0.947%) vs LTC (-0.027%) = 35× difference in event sensitivity

**Generated Figures:**

| Figure | Filename | Purpose | Key Insight |
|--------|----------|---------|-------------|
| Figure 1 (MONEY SHOT) | `figure1_heterogeneity` | Horizontal bar chart of crypto sensitivity | 97.4pp spread, 35× heterogeneity |
| Figure 2 (NULL RESULT) | `figure2_infrastructure_vs_regulatory` | Box plots showing no difference | p=0.997, infrastructure ≈ regulatory |
| Figure 3 (TOKEN-SPECIFIC) | `figure3_event_coefficients_heatmap` | Event type × crypto heatmap | Token-specific responses vary by event |

**Additional Output:**
- `table1_heterogeneity.tex` - LaTeX table with rankings and statistics

**Color Scheme (Grayscale Gradient):**
```python
COLORS = {
    'bnb': '#000000',      # Black (highest sensitivity)
    'xrp': '#333333',      # Very dark gray
    'btc': '#666666',      # Medium-dark gray
    'ada': '#888888',      # Medium gray
    'eth': '#AAAAAA',      # Light gray
    'ltc': '#CCCCCC',      # Very light gray (lowest)
}
```

**Data Sources:**
```python
crypto_df = pd.read_csv('outputs/analysis_results/analysis_by_crypto.csv')
hypothesis_df = pd.read_csv('outputs/analysis_results/hypothesis_test_results.csv')
event_impacts_df = pd.read_csv('outputs/publication/csv_exports/event_impacts_fdr.csv')
```

**Output Directory:** `/home/kawaiikali/event-study/publication_figures/`

---

### 5. `create_temporal_stability_figure.py` - Robustness Visualization

**Purpose:** Show that cross-sectional heterogeneity persists across market regimes.

**Main Insight:** Perfect ranking stability (ρ = 1.00, no rank changes between early/late periods)

**Generated Figure:** `temporal_stability_analysis.png`

**3-Panel Layout:**

| Panel | Title | Content |
|-------|-------|---------|
| Panel A | Coefficient Magnitude by Period | Grouped bars: Early (2019-2021), Full Sample, Late (2022-2025) |
| Panel B | Ranking Stability | Line plot showing rank consistency across periods |
| Panel C | Heterogeneity Magnitude Stability | Dual-axis: Spread (max-min) + Cohen's d effect size |

**Key Statistics Visualized:**
- Coefficient compression in late period: -11.5%
- Ranking correlation: ρ = 1.00 (perfect stability)
- Effect size stability: Cohen's d = 2.51 → 2.50 (BNB vs LTC)

**Hardcoded Data:** Contains baseline, early, and late period coefficients for 6 cryptocurrencies.

**Output Directories:**
- Primary: `publication_figures/temporal_stability_analysis.png`
- Backup: `event_study/outputs/publication/figures/temporal_stability_analysis.png`

---

## Output Directory Structure

```
/home/kawaiikali/event-study/
│
├── publication_figures/               # Main figure output directory
│   ├── figure1_event_timeline.pdf
│   ├── figure1_event_timeline.svg
│   ├── figure2_volatility_comparison.pdf
│   ├── figure2_volatility_comparison.svg
│   ├── figure3_impact_heatmap.pdf
│   ├── figure3_impact_heatmap.svg
│   ├── figure4_model_comparison.pdf
│   ├── figure4_model_comparison.svg
│   ├── figure1_heterogeneity.pdf      # MONEY SHOT
│   ├── figure1_heterogeneity.png
│   ├── figure2_infrastructure_vs_regulatory.pdf
│   ├── figure2_infrastructure_vs_regulatory.png
│   ├── figure3_event_coefficients_heatmap.pdf
│   ├── figure3_event_coefficients_heatmap.png
│   └── temporal_stability_analysis.png
│
├── publication_tables/                # LaTeX table output directory
│   ├── table1_event_study_results.tex
│   ├── table2_descriptive_statistics.tex
│   ├── table3_volatility_models.tex
│   ├── table4_regression_results.tex
│   ├── table1_heterogeneity.tex
│   └── all_tables.tex                 # Master compilation file
│
└── event_study/outputs/
    ├── publication/
    │   ├── latex/
    │   │   ├── model_comparison.tex
    │   │   ├── event_comparison.tex
    │   │   └── leverage_parameters.tex
    │   ├── csv_exports/
    │   │   ├── btc_parameters.csv
    │   │   ├── eth_parameters.csv
    │   │   ├── xrp_parameters.csv
    │   │   ├── ada_parameters.csv
    │   │   ├── bnb_parameters.csv
    │   │   ├── ltc_parameters.csv
    │   │   ├── model_comparison.csv
    │   │   ├── event_impacts_fdr.csv
    │   │   └── hypothesis_test.csv
    │   ├── figures/
    │   │   └── temporal_stability_analysis.png
    │   ├── volatility_major_events.png
    │   ├── diagnostic_plots.png
    │   └── event_impact_comparison.png
    └── analysis_results/
        ├── analysis_by_crypto.csv
        └── hypothesis_test_results.csv
```

---

## Figure Generation Pipeline

### Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    ANALYSIS RESULTS                          │
│  (model_results, analysis_results, crypto_data)             │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
        ┌───────────────┴──────────────┐
        │                               │
        ▼                               ▼
┌──────────────────┐          ┌──────────────────┐
│ Publication      │          │ Standalone       │
│ Outputs Class    │          │ Figure Scripts   │
└────────┬─────────┘          └────────┬─────────┘
         │                              │
         ├─────────────┬────────────┬───┼────────────┬─────────────┐
         ▼             ▼            ▼   ▼            ▼             ▼
    ┌────────┐   ┌──────────┐  ┌──────┐ ┌──────┐ ┌──────┐  ┌──────────┐
    │ LaTeX  │   │  Plots   │  │ CSV  │ │ Fig1 │ │ Fig2 │  │ Temporal │
    │ Tables │   │ (3 types)│  │Export│ │-4    │ │Hetero│  │ Stability│
    └────┬───┘   └─────┬────┘  └───┬──┘ └───┬──┘ └───┬──┘  └─────┬────┘
         │             │            │        │        │            │
         └─────────────┴────────────┴────────┴────────┴────────────┘
                                    │
                                    ▼
                    ┌──────────────────────────────┐
                    │    Publication Outputs        │
                    │  • Tables (LaTeX)             │
                    │  • Figures (PDF/PNG/SVG)      │
                    │  • Data (CSV)                 │
                    └──────────────────────────────┘
```

### Figure Types and Their Purposes

**1. Timeline Visualizations**
- Event timeline with scatter points
- Significance markers (asterisks)
- Separate infrastructure vs regulatory markers

**2. Volatility Dynamics**
- Pre/during/post event periods
- Confidence intervals as error bars
- Dual-panel (infrastructure vs regulatory)

**3. Heatmaps**
- Event × Cryptocurrency matrices
- Diverging colormaps (RdGy_r)
- Cell values overlaid on colors

**4. Model Comparison Charts**
- Multi-panel layouts (2×2 grids)
- Bar charts with highlighting for best models
- Dual metrics (forecast accuracy + information criteria)

**5. Box Plots**
- Distribution comparisons
- Overlay scatter points (individual cryptos)
- Statistical significance annotations

**6. Bar Charts**
- Horizontal bars for ranking visualization
- Value labels at bar ends
- Gradient colors showing magnitude

**7. Line Plots**
- Ranking stability across periods
- Connected markers showing transitions
- Annotated with correlation coefficients

---

## Data Flow Through Pipeline

### Step 1: Model Estimation (Upstream)
```
data_preparation.py → garch_models.py → tarch_x_integration.py
                                              ↓
                                    model_results Dict
```

### Step 2: Statistical Analysis (Upstream)
```
event_impact_analysis.py → hypothesis_testing_results.py
                                     ↓
                            analysis_results Dict
```

### Step 3: Publication Output Generation (This Layer)
```python
# Instantiate output generator
publisher = PublicationOutputs(
    model_results=model_results,
    analysis_results=analysis_results,
    crypto_data=crypto_data
)

# Generate all outputs
publisher.generate_all_outputs()
```

**Output:**
- 3 LaTeX tables in `outputs/publication/latex/`
- 3 PNG figures in `outputs/publication/`
- 10+ CSV files in `outputs/publication/csv_exports/`

### Step 4: Advanced Figure Generation (Optional)
```python
# Load processed data
crypto_df = pd.read_csv('outputs/analysis_results/analysis_by_crypto.csv')
hypothesis_df = pd.read_csv('outputs/analysis_results/hypothesis_test_results.csv')
event_impacts_df = pd.read_csv('outputs/publication/csv_exports/event_impacts_fdr.csv')

# Generate key figures
create_heterogeneity_bar_chart(crypto_df)
create_infra_vs_regulatory_comparison(crypto_df, hypothesis_df)
create_event_coefficients_heatmap(event_impacts_df)
```

**Output:**
- 3 PDF + 3 PNG figures in `publication_figures/`
- 1 LaTeX table

---

## LaTeX Table Formatting Standards

### Structure Template
```latex
\begin{table}[htbp]
  \centering
  \caption{Table Title}
  \label{tab:table_label}
  \begin{tabular}{lcccc}
    \toprule
    \toprule
    Column Headers \\
    \midrule
    Data rows with formatting \\
    \midrule
    \bottomrule
    \bottomrule
  \end{tabular}
  \begin{tablenotes}
    \small
    \item Notes: Methodology description, data sources, significance levels
  \end{tablenotes}
\end{table}
```

### Significance Markers
```python
if pval < 0.01:
    stars = '^{***}'
elif pval < 0.05:
    stars = '^{**}'
elif pval < 0.10:
    stars = '^{*}'
```

### Number Formatting
- Coefficients: `.4f` (4 decimal places)
- Standard errors: `({se:.4f})` (in parentheses)
- AIC/BIC: `.2f` (2 decimal places)
- Percentages: `.3f` (3 decimal places)

---

## CSV Export Specifications

### Model Parameters Export
**Filename:** `{crypto}_parameters.csv`

**Columns:**
- `model` - Model name (e.g., "GARCH(1,1)", "TARCH-X")
- `parameter` - Parameter name (e.g., "omega", "alpha[1]", "beta[1]")
- `value` - Estimated coefficient
- `std_error` - Standard error
- `p_value` - Statistical significance

### Model Comparison Export
**Filename:** `model_comparison.csv`

**Columns:**
- `crypto` - Cryptocurrency ticker
- `model` - Model specification
- `AIC` - Akaike Information Criterion
- `BIC` - Bayesian Information Criterion
- `log_likelihood` - Log-likelihood value

### Event Impacts Export
**Filename:** `event_impacts_fdr.csv`

**Columns:**
- `crypto` - Cryptocurrency ticker
- `event_type` - "infrastructure" or "regulatory"
- `coefficient` - Event impact coefficient
- `p_value` - Original p-value
- `fdr_adjusted_p` - FDR-adjusted p-value
- `significant_fdr` - Boolean flag for FDR significance

### Hypothesis Test Export
**Filename:** `hypothesis_test.csv`

**Columns:**
- `Infrastructure_mean` - Mean infrastructure event effect
- `Infrastructure_std` - Standard deviation
- `Infrastructure_n` - Number of observations
- `Regulatory_mean` - Mean regulatory event effect
- `Regulatory_std` - Standard deviation
- `Regulatory_n` - Number of observations
- `t_statistic` - Student's t-test statistic
- `t_pvalue` - t-test p-value
- `mann_whitney_statistic` - Mann-Whitney U statistic
- `mann_whitney_pvalue` - Mann-Whitney p-value
- `cohens_d` - Cohen's d effect size

---

## Matplotlib Configuration

### Publication Quality Settings
```python
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif'],
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.titlesize': 13,
    'text.usetex': False,        # Set to True if LaTeX installed
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.format': 'pdf',
    'savefig.bbox': 'tight',
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linestyle': '--',
    'lines.linewidth': 1.5,
})
```

### Grayscale-Friendly Design Principles
1. **Use patterns (hatching) in addition to colors**
   - Infrastructure: `///`
   - Regulatory: `\\\`
   - Significant: `xxx`

2. **Use shapes in addition to colors**
   - Infrastructure: circles (`o`)
   - Regulatory: squares (`s`)

3. **Use varying line widths**
   - Primary elements: 1.5-2.0
   - Secondary elements: 1.0
   - Grid lines: 0.5

4. **Ensure text contrast**
   - White text on dark backgrounds (>60% intensity)
   - Black text on light backgrounds (<60% intensity)

---

## Example Usage

### Generate All Publication Outputs
```python
from code.publication_outputs import PublicationOutputs

# Assume you have these from upstream analysis
model_results = {...}        # Dict of GARCH results by crypto
analysis_results = {...}     # Dict of hypothesis tests, event impacts
crypto_data = {...}          # Dict of prepared data

# Generate all outputs
publisher = PublicationOutputs(model_results, analysis_results, crypto_data)
publisher.generate_all_outputs()

# Output:
# outputs/publication/latex/model_comparison.tex
# outputs/publication/latex/event_comparison.tex
# outputs/publication/latex/leverage_parameters.tex
# outputs/publication/volatility_major_events.png
# outputs/publication/diagnostic_plots.png
# outputs/publication/event_impact_comparison.png
# outputs/publication/csv_exports/*.csv
```

### Generate Standalone Figures
```python
from code.create_publication_figures import main

# Generates 4 figures with example data or loads actual data
main()

# Output:
# publication_figures/figure1_event_timeline.pdf
# publication_figures/figure2_volatility_comparison.pdf
# publication_figures/figure3_impact_heatmap.pdf
# publication_figures/figure4_model_comparison.pdf
```

### Generate LaTeX Tables
```python
from code.generate_latex_tables import generate_example_tables, create_master_latex_file

# Generate all tables
generate_example_tables()

# Create master file
create_master_latex_file()

# Output:
# publication_tables/table1_event_study_results.tex
# publication_tables/table2_descriptive_statistics.tex
# publication_tables/table3_volatility_models.tex
# publication_tables/table4_regression_results.tex
# publication_tables/all_tables.tex
```

### Generate Heterogeneity Figures (Key Results)
```python
from code.create_heterogeneity_figures import main

# Generates 3 key figures emphasizing main contribution
main()

# Output:
# publication_figures/figure1_heterogeneity.pdf (THE MONEY SHOT)
# publication_figures/figure2_infrastructure_vs_regulatory.pdf (NULL RESULT)
# publication_figures/figure3_event_coefficients_heatmap.pdf (TOKEN-SPECIFIC)
# publication_figures/table1_heterogeneity.tex
```

### Generate Temporal Stability Figure
```python
from code.create_temporal_stability_figure import main

# Generates robustness visualization
# No function call shown in code, runs on import

# Output:
# publication_figures/temporal_stability_analysis.png
```

---

## Key Outputs Summary

### For Main Text

| Output | File | Purpose |
|--------|------|---------|
| **Table 1** | `table1_heterogeneity.tex` | Cross-sectional heterogeneity (main finding) |
| **Figure 1** | `figure1_heterogeneity.pdf` | Horizontal bar chart (97.4pp spread) |
| **Figure 2** | `figure2_infrastructure_vs_regulatory.pdf` | Box plots (p=0.997 null result) |
| **Figure 3** | `figure3_event_coefficients_heatmap.pdf` | Token-specific responses |

### For Appendix

| Output | File | Purpose |
|--------|------|---------|
| Model Comparison | `model_comparison.tex` | AIC/BIC across models |
| Event Comparison | `event_comparison.tex` | Hypothesis test results |
| Leverage Parameters | `leverage_parameters.tex` | Asymmetric volatility effects |
| Descriptive Statistics | `table2_descriptive_statistics.tex` | Return statistics |
| All Parameters | `{crypto}_parameters.csv` | Complete parameter estimates |

### For Robustness Checks

| Output | File | Purpose |
|--------|------|---------|
| Temporal Stability | `temporal_stability_analysis.png` | Heterogeneity persistence |
| Event Timeline | `figure1_event_timeline.pdf` | Event impact visualization |
| Volatility Dynamics | `figure2_volatility_comparison.pdf` | Pre/during/post event volatility |
| Diagnostic Plots | `diagnostic_plots.png` | ACF + Q-Q plots for model validation |

---

## Integration with Main Analysis Pipeline

### Prerequisites (Upstream Outputs)
1. **Model Results** from `garch_models.py` and `tarch_x_integration.py`
2. **Analysis Results** from `event_impact_analysis.py` and `hypothesis_testing_results.py`
3. **Prepared Data** from `data_preparation.py`

### Typical Workflow
```python
# Step 1: Data preparation (upstream)
from code.data_preparation import DataPreparation
data_prep = DataPreparation(data_path='data/')
crypto_data = data_prep.prepare_all_data()

# Step 2: Model estimation (upstream)
from code.tarch_x_integration import run_tarch_x_for_crypto
model_results = {}
for crypto in ['btc', 'eth', 'xrp', 'ada', 'bnb', 'ltc']:
    model_results[crypto] = run_tarch_x_for_crypto(crypto, events_df, crypto_data[crypto])

# Step 3: Event impact analysis (upstream)
from code.event_impact_analysis import EventImpactAnalysis
eia = EventImpactAnalysis(model_results, events_df)
analysis_results = eia.run_full_analysis()

# Step 4: Publication outputs (THIS LAYER)
from code.publication_outputs import generate_publication_outputs
generate_publication_outputs(model_results, analysis_results, crypto_data)

# Step 5: Advanced figures (THIS LAYER - optional)
from code.create_heterogeneity_figures import main as generate_heterogeneity_figures
generate_heterogeneity_figures()
```

---

## Notes on Implementation

### Safe Model Statistics Extraction
The `PublicationOutputs` class includes a helper method to safely extract statistics from models that may not have converged:

```python
def _safe_get_model_stats(self, models: Dict, model_name: str) -> Tuple[float, float]:
    """
    Safely extract AIC and BIC from model results.
    Returns (np.nan, np.nan) if model doesn't exist or didn't converge.
    """
    if model_name in models and hasattr(models[model_name], 'convergence') and models[model_name].convergence:
        return models[model_name].aic, models[model_name].bic
    return np.nan, np.nan
```

### Major Events for Volatility Plots
Default major events used in `plot_volatility_around_events()`:
- **2022-11-11:** FTX Bankruptcy
- **2022-05-09:** Terra/Luna Collapse
- **2024-01-10:** BTC ETF Approval

### Timezone Handling
All event dates are converted to timezone-aware timestamps (`UTC`) for consistent comparison with time-series data.

### Diagnostic Charts
Generated for `['btc', 'eth', 'xrp']` by default:
1. **ACF of squared standardized residuals** - Tests for remaining ARCH effects
2. **Q-Q plots** - Tests for normality assumption

---

## Dependencies

### Python Packages
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `matplotlib` - Plotting
- `seaborn` - Statistical visualizations
- `scipy` - Statistical tests (Q-Q plots, probplot)
- `statsmodels` - ACF plots

### LaTeX Packages (for table compilation)
- `booktabs` - Professional table formatting
- `threeparttable` - Table notes
- `geometry` - Page margins (for master file)

---

## Future Enhancements

### Potential Additions
1. **Interactive plots** using Plotly for presentations
2. **Robustness table generation** from `robustness_checks.py` results
3. **Automated significance testing** in figure annotations
4. **Bootstrap confidence intervals** visualization
5. **Rolling window analysis** figures
6. **Network analysis** visualizations (if using GDELT sentiment data)

### Suggested Workflow Improvements
1. **Configuration file** for output paths and figure settings
2. **Logging** of generated outputs with timestamps
3. **Validation checks** to ensure all required data exists before generation
4. **Batch processing** for multiple event windows or cryptocurrency sets
5. **Version control** for figure revisions (figure_v1.pdf, figure_v2.pdf)

---

## Troubleshooting

### Common Issues

**1. "No data files found" warning**
- **Cause:** `create_publication_figures.py` tries to load data from `data/` directory
- **Solution:** Either provide actual data files or use generated example data

**2. LaTeX compilation errors**
- **Cause:** Missing LaTeX packages (booktabs, threeparttable)
- **Solution:** Install packages via `tlmgr install booktabs threeparttable`

**3. Font not found warnings**
- **Cause:** Times New Roman not available on system
- **Solution:** matplotlib falls back to DejaVu Serif automatically

**4. Empty plots or missing figures**
- **Cause:** Model didn't converge or data is missing
- **Solution:** Check `model.convergence` flag and ensure data preparation completed successfully

**5. CSV export fails**
- **Cause:** Missing keys in `analysis_results` dictionary
- **Solution:** Verify upstream analysis completed all required hypothesis tests

---

## Summary Statistics

**Total Scripts:** 5 main publication scripts
**Total Outputs Generated:** ~30 files (10 figures, 8 tables, 12+ CSVs)
**Figure Formats:** PDF (vector), PNG (raster), SVG (vector)
**Table Format:** LaTeX (.tex)
**Data Format:** CSV (.csv)

**Primary Output Directories:**
- `/home/kawaiikali/event-study/publication_figures/`
- `/home/kawaiikali/event-study/publication_tables/`
- `/home/kawaiikali/event-study/event_study/outputs/publication/`

---

## Related Documentation

- `DOCS_DATA_PREPARATION.md` - Upstream data processing
- `DOCS_GARCH_MODELS.md` - Model estimation layer
- `DOCS_TARCH_X.md` - Event dummy integration
- `DOCS_ANALYSIS_LAYER.md` - Statistical analysis and hypothesis testing

---

**Last Updated:** October 28, 2025
**Maintainer:** Farzulla Research
**Status:** Production - Ready for journal submission
