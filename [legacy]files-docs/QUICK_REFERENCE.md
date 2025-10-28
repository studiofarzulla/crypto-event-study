# Quick Reference Card

**Event Study Publication Package - Common Commands**

---

## 1-Minute Quick Start

```bash
cd /home/kawaiikali/event-study

# See example outputs
python create_publication_figures.py
python generate_latex_tables.py

# View results
ls publication_figures/
ls publication_tables/
```

---

## Common Tasks

### Generate All Outputs

```bash
# Step 1: Validate your data
python validate_data.py

# Step 2: Generate figures
python create_publication_figures.py

# Step 3: Generate tables
python generate_latex_tables.py
```

### Check Output Quality

```bash
# View figures (Linux)
evince publication_figures/figure1_event_timeline.pdf

# Compile LaTeX tables
cd publication_tables/
pdflatex all_tables.tex
```

### Update After Data Changes

```bash
# Quick regeneration
python validate_data.py && \
python create_publication_figures.py && \
python generate_latex_tables.py
```

---

## Data File Quick Reference

### Required CSV Files

Located in: `/home/kawaiikali/event-study/data/`

**events.csv** - 18 rows
```
Columns: date, event_name, event_type, impact_magnitude, p_value
```

**volatility_results.csv** - 6 rows
```
Columns: period, event_type, mean_volatility, ci_lower, ci_upper
```

**impact_matrix.csv** - 18×N matrix
```
Index: Event names
Columns: Crypto tickers (BTC, ETH, etc.)
```

**model_results.csv** - 5+ rows
```
Columns: model_name, rmse, mae, aic, bic
```

---

## Output Files Generated

### Figures (8 files)

```
publication_figures/
├── figure1_event_timeline.pdf ← Use this for journal
├── figure1_event_timeline.svg
├── figure2_volatility_comparison.pdf
├── figure2_volatility_comparison.svg
├── figure3_impact_heatmap.pdf
├── figure3_impact_heatmap.svg
├── figure4_model_comparison.pdf
└── figure4_model_comparison.svg
```

### Tables (5 files)

```
publication_tables/
├── table1_event_study_results.tex ← \input{} these
├── table2_descriptive_statistics.tex
├── table3_volatility_models.tex
├── table4_regression_results.tex
└── all_tables.tex ← Master file
```

---

## Customization Quick Edits

### Change Figure Size

Edit `create_publication_figures.py`:
```python
# Find this line:
fig, ax = plt.subplots(figsize=(12, 6))

# Change to (width, height in inches):
fig, ax = plt.subplots(figsize=(10, 5))
```

### Change Font Size

Edit `create_publication_figures.py`:
```python
# Find this section:
plt.rcParams['font.size'] = 10

# Change to:
plt.rcParams['font.size'] = 11
```

### Add Cryptocurrencies

Edit `data/impact_matrix.csv`:
```csv
# Just add more columns
,BTC,ETH,BNB,SOL,MATIC,DOT  ← Add more here
Event1,-0.05,-0.08,-0.06,-0.14,-0.07,-0.09
```

---

## Error Diagnosis

### "FileNotFoundError"

**Cause:** Missing data files
**Fix:**
```bash
# Check what exists
ls data/

# Create template files
python data_preparation_template.py
```

### "ValidationError"

**Cause:** Incorrect data format
**Fix:**
```bash
# See specific error
python validate_data.py

# Compare to template
cat data_preparation_template.py
```

### "Figures look blurry"

**Cause:** Viewing PNG preview
**Fix:** Open the PDF/SVG files instead

---

## LaTeX Integration

### Include Figures in Paper

```latex
\begin{figure}[htbp]
  \centering
  \includegraphics[width=0.8\textwidth]{publication_figures/figure1_event_timeline.pdf}
  \caption{Event Timeline and Impact Magnitudes}
  \label{fig:timeline}
\end{figure}
```

### Include Tables in Paper

```latex
\input{publication_tables/table1_event_study_results.tex}
```

### Required LaTeX Packages

```latex
\usepackage{graphicx}      % For figures
\usepackage{booktabs}      % For tables
\usepackage{threeparttable} % For table notes
```

---

## Data Format Examples

### Event Data (events.csv)

```csv
date,event_name,event_type,impact_magnitude,p_value
2022-11-08,FTX Collapse,infrastructure,-0.087,0.001
2022-09-15,Ethereum Merge,infrastructure,0.042,0.023
2023-06-13,SEC vs Ripple,regulatory,0.065,0.008
```

**Notes:**
- `impact_magnitude`: Decimal (0.05 = 5%)
- `p_value`: Between 0 and 1
- `event_type`: Either "infrastructure" or "regulatory"

### Volatility Data (volatility_results.csv)

```csv
period,event_type,mean_volatility,ci_lower,ci_upper
"Pre-Event\n(-10 to -1)",infrastructure,2.45,2.15,2.75
"Event\n(0 to +5)",infrastructure,4.12,3.78,4.46
```

**Notes:**
- Period labels MUST match exactly (including \n)
- Volatility in % per day
- CI bounds should bracket mean

---

## Quality Checks

### Before Submission

```bash
# 1. Validate data
python validate_data.py

# 2. Generate outputs
python create_publication_figures.py

# 3. Visual inspection
# Open each PDF and check:
#   - Text is readable
#   - Axes have units
#   - Legends are clear
#   - Prints well in grayscale

# 4. Test LaTeX compilation
cd publication_tables/
pdflatex all_tables.tex
```

### Print Test

```bash
# Convert figure to grayscale
pdftoppm figure1_event_timeline.pdf test -gray -singlefile
# View test.ppm to ensure clarity
```

---

## One-Line Commands

### Full regeneration
```bash
python validate_data.py && python create_publication_figures.py && python generate_latex_tables.py
```

### Check data format
```bash
python validate_data.py 2>&1 | grep "✓"
```

### Count events by type
```bash
grep -c "infrastructure" data/events.csv
grep -c "regulatory" data/events.csv
```

### List all outputs
```bash
find publication_* -name "*.pdf" -o -name "*.tex"
```

---

## File Locations

**Scripts:** `/home/kawaiikali/event-study/`
**Input Data:** `/home/kawaiikali/event-study/data/`
**Figures:** `/home/kawaiikali/event-study/publication_figures/`
**Tables:** `/home/kawaiikali/event-study/publication_tables/`

---

## Get Help

**Documentation:**
- `README.md` - Full overview
- `VISUALIZATION_README.md` - Detailed figure docs
- This file - Quick commands

**Examples:**
- `data_preparation_template.py` - Data format
- Run scripts without data to see examples

**Validation:**
- `validate_data.py` - Specific error messages

---

## Publication Standards

**Required:**
- ✓ Vector format (PDF/SVG)
- ✓ Grayscale-friendly
- ✓ LaTeX-compatible fonts
- ✓ Statistical significance markers
- ✓ Units on all axes

**Optional but Recommended:**
- Enable LaTeX rendering if available
- Test print at 75% scale
- Verify all cross-references work
- Check journal-specific requirements

---

## Version

**Last Updated:** October 2025
**Python:** 3.8+
**matplotlib:** 3.3+

---

**Need more detail?** See `README.md` or `VISUALIZATION_README.md`
