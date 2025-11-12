# Event Study Publication Package - File Index

**Quick navigation guide for all package components**

---

## Start Here

**New to the package?** Read these in order:

1. **README.md** - Complete overview and quick start
2. **QUICK_REFERENCE.md** - Common commands and examples
3. **run_complete_demo.py** - Interactive demonstration

**Ready to use your data?**

4. **data_preparation_template.py** - Format guide for your CSV files
5. **validate_data.py** - Check your data before generating outputs

---

## Core Scripts (Run These)

### Main Generation Scripts

| File | Purpose | Output | Runtime |
|------|---------|--------|---------|
| `create_publication_figures.py` | Generate all figures | 8 files (4 PDF + 4 SVG) | ~30s |
| `generate_latex_tables.py` | Generate all tables | 4 LaTeX .tex files | ~10s |
| `validate_data.py` | Validate data format | Console report | ~1s |
| `run_complete_demo.py` | Full system demo | All outputs + summary | ~3min |

### Support Scripts

| File | Purpose | When to Use |
|------|---------|-------------|
| `data_preparation_template.py` | Data format examples | When creating CSV files |

---

## Documentation Files (Read These)

### Getting Started

| File | Length | Purpose | Read Time |
|------|--------|---------|-----------|
| **README.md** | 500 lines | Complete package guide | 10 min |
| **QUICK_REFERENCE.md** | 300 lines | Command cheat sheet | 5 min |
| **PACKAGE_SUMMARY.md** | 400 lines | Feature overview | 8 min |

### Detailed Documentation

| File | Length | Purpose | Read Time |
|------|--------|---------|-----------|
| **VISUALIZATION_README.md** | 450 lines | Figure specifications | 12 min |
| **WORKFLOW_DIAGRAM.md** | 400 lines | Visual workflows | 8 min |
| **INDEX.md** | This file | Navigation guide | 2 min |

---

## By Task

### "I want to see what this does"

1. **PACKAGE_SUMMARY.md** - High-level overview
2. **run_complete_demo.py** - See it in action
3. View outputs in `publication_figures/` and `publication_tables/`

### "I want to use my own data"

1. **data_preparation_template.py** - See required format
2. Create CSV files in `data/` directory
3. **validate_data.py** - Check format
4. **create_publication_figures.py** - Generate figures
5. **generate_latex_tables.py** - Generate tables

### "I want to customize the visuals"

1. **VISUALIZATION_README.md** - Customization options
2. Edit **create_publication_figures.py**
3. Regenerate outputs

### "I need help with errors"

1. **QUICK_REFERENCE.md** - Common errors section
2. **validate_data.py** - Specific error messages
3. **data_preparation_template.py** - Correct format examples

### "I want to understand the system"

1. **README.md** - Architecture overview
2. **WORKFLOW_DIAGRAM.md** - Visual diagrams
3. **PACKAGE_SUMMARY.md** - Design philosophy

---

## By Audience

### First-Time Users

**Recommended reading order:**
1. PACKAGE_SUMMARY.md (understand what it does)
2. README.md (learn how to use it)
3. Run: `python run_complete_demo.py` (see outputs)
4. QUICK_REFERENCE.md (bookmark for commands)

### Researchers with Data Ready

**Recommended path:**
1. QUICK_REFERENCE.md (get started fast)
2. data_preparation_template.py (format your data)
3. Run: `python validate_data.py` (check format)
4. Run: `python create_publication_figures.py` (generate)
5. VISUALIZATION_README.md (customize if needed)

### Advanced Users

**Direct to:**
- create_publication_figures.py (modify code)
- generate_latex_tables.py (extend tables)
- VISUALIZATION_README.md (advanced features)

---

## File Relationships

```
README.md
├── Points to: QUICK_REFERENCE.md (commands)
├── Points to: VISUALIZATION_README.md (details)
└── Points to: data_preparation_template.py (format)

QUICK_REFERENCE.md
├── References: create_publication_figures.py
├── References: generate_latex_tables.py
└── References: validate_data.py

VISUALIZATION_README.md
├── Explains: create_publication_figures.py
└── Shows: Example captions and customization

WORKFLOW_DIAGRAM.md
├── Visualizes: Complete pipeline
└── Shows: Data flow and decisions

PACKAGE_SUMMARY.md
├── Summarizes: All components
└── Explains: Design philosophy
```

---

## Output Directories (Generated)

### publication_figures/

Created by: `create_publication_figures.py`

```
figure1_event_timeline.pdf
figure1_event_timeline.svg
figure2_volatility_comparison.pdf
figure2_volatility_comparison.svg
figure3_impact_heatmap.pdf
figure3_impact_heatmap.svg
figure4_model_comparison.pdf
figure4_model_comparison.svg
```

**Size:** ~50-200 KB per figure
**Format:** Vector (PDF/SVG)
**Use:** Insert into manuscript

### publication_tables/

Created by: `generate_latex_tables.py`

```
table1_event_study_results.tex
table2_descriptive_statistics.tex
table3_volatility_models.tex
table4_regression_results.tex
all_tables.tex (master file)
```

**Size:** ~2-5 KB per table
**Format:** LaTeX (.tex)
**Use:** \input{} into manuscript

---

## Input Data (You Create)

### data/

Required CSV files (see data_preparation_template.py for format):

```
events.csv              (18 rows: your events)
volatility_results.csv  (6 rows: 3 periods × 2 types)
impact_matrix.csv       (18 × N matrix: events × cryptos)
model_results.csv       (5+ rows: your models)
```

---

## Quick Command Reference

### See Example Outputs
```bash
python run_complete_demo.py
```

### Generate Figures
```bash
python create_publication_figures.py
```

### Generate Tables
```bash
python generate_latex_tables.py
```

### Validate Data
```bash
python validate_data.py
```

### Full Pipeline
```bash
python validate_data.py && \
python create_publication_figures.py && \
python generate_latex_tables.py
```

---

## Documentation Statistics

| Type | Count | Total Lines |
|------|-------|-------------|
| Core Scripts | 5 | ~2,200 |
| Documentation | 6 | ~2,500 |
| Total Files | 11 | ~4,700 |

---

## What Each File Is Best For

**README.md**
- First-time orientation
- Installation guide
- Publication checklist

**QUICK_REFERENCE.md**
- Quick lookups
- Common commands
- Error solutions

**PACKAGE_SUMMARY.md**
- Understanding features
- Design philosophy
- Comparison to alternatives

**VISUALIZATION_README.md**
- Customization details
- Figure specifications
- LaTeX integration

**WORKFLOW_DIAGRAM.md**
- Visual learners
- Understanding flow
- Decision trees

**INDEX.md** (this file)
- Navigation
- File relationships
- Quick access

**create_publication_figures.py**
- Generating figures
- Customizing visuals
- Understanding code

**generate_latex_tables.py**
- Creating tables
- LaTeX formatting
- Statistical display

**validate_data.py**
- Error checking
- Format compliance
- Debugging data issues

**data_preparation_template.py**
- Learning format
- Example structures
- Helper functions

**run_complete_demo.py**
- System overview
- Testing installation
- Learning workflow

---

## Recommended Bookmarks

**Everyday Use:**
- QUICK_REFERENCE.md
- validate_data.py
- create_publication_figures.py

**Reference:**
- README.md
- VISUALIZATION_README.md
- data_preparation_template.py

**Learning:**
- WORKFLOW_DIAGRAM.md
- PACKAGE_SUMMARY.md
- run_complete_demo.py

---

## Search Guide

### Looking for...

**Installation instructions?**
→ README.md (Technical Requirements section)

**Command examples?**
→ QUICK_REFERENCE.md (Common Tasks section)

**Error solutions?**
→ QUICK_REFERENCE.md (Error Diagnosis section)

**Data format?**
→ data_preparation_template.py (all prepare_*() functions)

**Customization options?**
→ VISUALIZATION_README.md (Customization Options section)

**Figure specifications?**
→ VISUALIZATION_README.md (Figure Descriptions section)

**Workflow overview?**
→ WORKFLOW_DIAGRAM.md (Complete Research Pipeline)

**Design philosophy?**
→ PACKAGE_SUMMARY.md (Design Philosophy section)

**Feature list?**
→ PACKAGE_SUMMARY.md (Key Features section)

**Publication standards?**
→ README.md (Publication Checklist section)

---

## Print-Friendly Summary

**Essential Files (print these):**
1. QUICK_REFERENCE.md - Daily reference
2. data_preparation_template.py - Format guide

**Read Online:**
- Everything else (searchable, linkable)

---

## Version Information

**Package Version:** 1.0
**Documentation Last Updated:** October 2025
**Compatibility:** Python 3.8+, matplotlib 3.3+

---

## Navigation Tips

1. **Start with README.md** for overview
2. **Use QUICK_REFERENCE.md** for daily tasks
3. **Refer to VISUALIZATION_README.md** for customization
4. **Check this INDEX.md** when lost

**Most Important Files:**
- README.md (start here)
- QUICK_REFERENCE.md (use daily)
- create_publication_figures.py (main script)

**Everything else is supplementary but helpful.**

---

**Need help?** Check the "By Task" section above to find the right file for your needs.
