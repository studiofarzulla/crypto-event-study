# Event Study Publication Workflow

Visual guide showing how all components work together.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    EVENT STUDY PUBLICATION SYSTEM                    │
│                                                                       │
│  INPUT DATA                PROCESSING              OUTPUT             │
│  ───────────              ──────────────           ──────────         │
│                                                                       │
│  ┌──────────┐             ┌─────────────┐         ┌──────────────┐  │
│  │events.csv│────────────▶│  Validate   │────────▶│ 4 PDF Figures│  │
│  └──────────┘             │    Data     │         └──────────────┘  │
│                           └─────────────┘                            │
│  ┌──────────────┐                │                ┌──────────────┐  │
│  │volatility.csv│────────────────┤                │ 4 SVG Figures│  │
│  └──────────────┘                │                └──────────────┘  │
│                                   │                                  │
│  ┌──────────────┐                │                ┌──────────────┐  │
│  │impact_matrix │────────────────┤                │ 4 LaTeX Tables│ │
│  │    .csv      │                │                └──────────────┘  │
│  └──────────────┘                │                                  │
│                                   │                ┌──────────────┐  │
│  ┌──────────────┐                │                │Master LaTeX  │  │
│  │ model_results│────────────────┘                │    File      │  │
│  │    .csv      │                                 └──────────────┘  │
│  └──────────────┘                                                    │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Complete Research Pipeline

```
PHASE 1: DATA COLLECTION
═══════════════════════════════════════════════════════════════════════

  ┌─────────────────┐
  │ Download crypto │
  │ price data      │
  │ (CoinGecko, etc)│
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │ Identify 18     │
  │ events (news,   │
  │ announcements)  │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │ Clean & merge   │
  │ data            │
  └────────┬────────┘
           │
           ▼

PHASE 2: STATISTICAL ANALYSIS
═══════════════════════════════════════════════════════════════════════

  ┌─────────────────┐
  │ Estimate market │
  │ model (CAPM)    │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │ Calculate       │
  │ abnormal returns│
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │ Compute CARs    │
  │ by event        │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │ Statistical     │
  │ significance    │
  │ tests (t-tests) │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │ Estimate GARCH  │
  │ volatility      │
  │ models          │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │ Cross-sectional │
  │ regressions     │
  └────────┬────────┘
           │
           ▼

PHASE 3: DATA PREPARATION (THIS PACKAGE STARTS HERE)
═══════════════════════════════════════════════════════════════════════

  ┌─────────────────┐
  │ Format results  │
  │ into 4 CSV files│
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐    Use data_preparation_template.py
  │ Save to data/   │◀── as guide for correct format
  │ directory       │
  └────────┬────────┘
           │
           ▼

PHASE 4: VALIDATION
═══════════════════════════════════════════════════════════════════════

  ┌─────────────────┐
  │ Run validator:  │
  │ validate_data.py│
  └────────┬────────┘
           │
           ├───▶ ✓ Format correct ──────┐
           │                             │
           └───▶ ✗ Errors found          │
                      │                  │
                      ▼                  │
              ┌─────────────┐            │
              │ Fix errors  │            │
              │ Re-validate │            │
              └─────────────┘            │
                                         │
                                         ▼

PHASE 5: VISUALIZATION GENERATION
═══════════════════════════════════════════════════════════════════════

  ┌────────────────────────────────────────┐
  │ Run: create_publication_figures.py     │
  └───────────────┬────────────────────────┘
                  │
      ┌───────────┼───────────┬──────────┐
      │           │           │          │
      ▼           ▼           ▼          ▼
  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
  │Figure 1│ │Figure 2│ │Figure 3│ │Figure 4│
  │Timeline│ │Volatil.│ │Heatmap │ │Models  │
  └────────┘ └────────┘ └────────┘ └────────┘
      │           │           │          │
      └───────────┴───────────┴──────────┘
                  │
                  ▼
          ┌──────────────┐
          │ PDF + SVG    │
          │ outputs saved│
          └──────────────┘


PHASE 6: TABLE GENERATION
═══════════════════════════════════════════════════════════════════════

  ┌────────────────────────────────────────┐
  │ Run: generate_latex_tables.py          │
  └───────────────┬────────────────────────┘
                  │
      ┌───────────┼──────────┬──────────┐
      │           │          │          │
      ▼           ▼          ▼          ▼
  ┌───────┐ ┌────────┐ ┌────────┐ ┌─────────┐
  │Table 1│ │Table 2 │ │Table 3 │ │Table 4  │
  │Events │ │Descrip.│ │Volatil.│ │Regress. │
  └───────┘ └────────┘ └────────┘ └─────────┘
      │           │          │          │
      └───────────┴──────────┴──────────┘
                  │
                  ▼
          ┌──────────────┐
          │ LaTeX .tex   │
          │ files saved  │
          └──────────────┘


PHASE 7: MANUSCRIPT INTEGRATION
═══════════════════════════════════════════════════════════════════════

  ┌─────────────────┐
  │ Write paper in  │
  │ LaTeX           │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │ \input{tables}  │
  │ \include{figs}  │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │ pdflatex paper  │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │ Review output   │
  │ Iterate         │
  └────────┬────────┘
           │
           ▼

PHASE 8: SUBMISSION
═══════════════════════════════════════════════════════════════════════

  ┌─────────────────┐
  │ Submit to       │
  │ JoF/JFE/RFS     │
  └─────────────────┘
```

---

## Data Flow Diagram

```
                          INPUT FILES
                    ┌──────────────────────┐
                    │  data/events.csv     │
                    │  - 18 events         │
                    │  - Impact magnitudes │
                    │  - P-values          │
                    └──────────┬───────────┘
                               │
                               ├──────────────────────┐
                               │                      │
                               ▼                      ▼
                    ┌──────────────────┐   ┌──────────────────┐
                    │ Figure 1:        │   │ Table 1:         │
                    │ Event Timeline   │   │ Event Study      │
                    │                  │   │ Results          │
                    └──────────────────┘   └──────────────────┘


                    ┌──────────────────────┐
                    │ data/volatility_     │
                    │ results.csv          │
                    │ - 6 rows (3×2)       │
                    │ - Confidence bands   │
                    └──────────┬───────────┘
                               │
                               ├──────────────────────┐
                               │                      │
                               ▼                      ▼
                    ┌──────────────────┐   ┌──────────────────┐
                    │ Figure 2:        │   │ Table 3:         │
                    │ Volatility       │   │ Volatility       │
                    │ Comparison       │   │ Models           │
                    └──────────────────┘   └──────────────────┘


                    ┌──────────────────────┐
                    │ data/impact_         │
                    │ matrix.csv           │
                    │ - 18 × N matrix      │
                    │ - CAR by crypto      │
                    └──────────┬───────────┘
                               │
                               ├──────────────────────┐
                               │                      │
                               ▼                      ▼
                    ┌──────────────────┐   ┌──────────────────┐
                    │ Figure 3:        │   │ Table 2:         │
                    │ Impact Heatmap   │   │ Descriptive      │
                    │                  │   │ Statistics       │
                    └──────────────────┘   └──────────────────┘


                    ┌──────────────────────┐
                    │ data/model_          │
                    │ results.csv          │
                    │ - 5+ models          │
                    │ - AIC/BIC/errors     │
                    └──────────┬───────────┘
                               │
                               ├──────────────────────┐
                               │                      │
                               ▼                      ▼
                    ┌──────────────────┐   ┌──────────────────┐
                    │ Figure 4:        │   │ Table 4:         │
                    │ Model            │   │ Regression       │
                    │ Performance      │   │ Results          │
                    └──────────────────┘   └──────────────────┘
```

---

## File Dependency Graph

```
create_publication_figures.py
│
├─ Reads: data/events.csv
│  └─▶ Generates: figure1_event_timeline.{pdf,svg}
│
├─ Reads: data/volatility_results.csv
│  └─▶ Generates: figure2_volatility_comparison.{pdf,svg}
│
├─ Reads: data/impact_matrix.csv
│  └─▶ Generates: figure3_impact_heatmap.{pdf,svg}
│
└─ Reads: data/model_results.csv
   └─▶ Generates: figure4_model_comparison.{pdf,svg}


generate_latex_tables.py
│
├─ Reads: data/events.csv
│  └─▶ Generates: table1_event_study_results.tex
│
├─ Reads: data/ (returns data)
│  └─▶ Generates: table2_descriptive_statistics.tex
│
├─ Reads: data/model_results.csv
│  └─▶ Generates: table3_volatility_models.tex
│
└─ Reads: data/ (regression results)
   └─▶ Generates: table4_regression_results.tex


validate_data.py
│
├─ Checks: data/events.csv
├─ Checks: data/volatility_results.csv
├─ Checks: data/impact_matrix.csv
├─ Checks: data/model_results.csv
│
└─▶ Reports: Validation status (pass/fail)
```

---

## Decision Tree: Which Script to Run?

```
START
  │
  ├─▶ Have data files ready? ──NO──▶ Run: data_preparation_template.py
  │        │                          (See format examples)
  │       YES                         │
  │        │                          │
  │        ▼                          │
  ├─▶ Data validated? ──NO──▶ Run: validate_data.py ◀───┘
  │        │                    Fix errors and retry
  │       YES
  │        │
  │        ▼
  ├─▶ Need figures? ──YES──▶ Run: create_publication_figures.py
  │        │
  │        ▼
  ├─▶ Need tables? ──YES──▶ Run: generate_latex_tables.py
  │        │
  │        ▼
  └─▶ Review outputs in publication_figures/ and publication_tables/
```

---

## Typical User Journey

```
┌────────────────────────────────────────────────────────────────┐
│ FIRST-TIME USER (Testing the System)                           │
│                                                                 │
│ 1. Clone/download package                                      │
│ 2. cd /home/kawaiikali/event-study                             │
│ 3. python create_publication_figures.py  ← Runs with examples  │
│ 4. ls publication_figures/                                     │
│ 5. Open PDFs to see output quality                             │
│ 6. Decide: "This is what I need!"                              │
│                                                                 │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ RESEARCHER (Using Real Data)                                   │
│                                                                 │
│ 1. Complete statistical analysis in R/Python/Stata             │
│ 2. Export results to CSV files                                 │
│ 3. Save to data/ directory                                     │
│ 4. python validate_data.py  ← Check format                     │
│ 5. Fix any errors                                              │
│ 6. python create_publication_figures.py                        │
│ 7. python generate_latex_tables.py                             │
│ 8. Review outputs                                              │
│ 9. Integrate into LaTeX manuscript                             │
│ 10. Submit to journal                                          │
│                                                                 │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ POWER USER (Customizing Visuals)                               │
│                                                                 │
│ 1. Run basic pipeline first                                    │
│ 2. Edit create_publication_figures.py                          │
│    - Change color schemes                                      │
│    - Modify figure dimensions                                  │
│    - Add custom annotations                                    │
│ 3. Regenerate outputs                                          │
│ 4. Iterate until perfect                                       │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

## Error Recovery Flowchart

```
ERROR OCCURRED
      │
      ▼
┌────────────────┐
│ What type?     │
└───┬───┬────┬──┘
    │   │    │
    │   │    └──▶ ValidationError
    │   │              │
    │   │              ▼
    │   │        ┌──────────────────┐
    │   │        │ Check error msg  │
    │   │        │ Compare to       │
    │   │        │ template format  │
    │   │        │ Fix CSV file     │
    │   │        │ Re-run validator │
    │   │        └──────────────────┘
    │   │
    │   └──▶ FileNotFoundError
    │              │
    │              ▼
    │        ┌──────────────────┐
    │        │ Check data/      │
    │        │ directory exists │
    │        │ Create CSV files │
    │        │ Re-run script    │
    │        └──────────────────┘
    │
    └──▶ Other Python error
              │
              ▼
        ┌──────────────────┐
        │ Check Python     │
        │ version (3.8+)   │
        │ Install packages │
        │ Read traceback   │
        └──────────────────┘
```

---

## Quality Assurance Checkpoints

```
CHECKPOINT 1: Data Preparation
├─ [ ] All CSV files created
├─ [ ] Correct column names
├─ [ ] No missing values
└─ [ ] Passes validate_data.py
        │
        ▼

CHECKPOINT 2: Figure Generation
├─ [ ] All 4 figures created
├─ [ ] PDF files are vector (not raster)
├─ [ ] Readable in grayscale
├─ [ ] Axes have units
└─ [ ] Legends are clear
        │
        ▼

CHECKPOINT 3: Table Generation
├─ [ ] All 4 tables created
├─ [ ] LaTeX compiles without errors
├─ [ ] Numbers have correct precision
├─ [ ] Significance stars correct
└─ [ ] Table notes are complete
        │
        ▼

CHECKPOINT 4: Integration
├─ [ ] Figures insert into manuscript
├─ [ ] Tables insert into manuscript
├─ [ ] Cross-references work (\ref{})
├─ [ ] Caption numbering consistent
└─ [ ] Print test looks good
        │
        ▼

READY FOR SUBMISSION ✓
```

---

## Time Estimates

```
Task                                  First Time    Subsequent
────────────────────────────────────────────────────────────────
Install & setup                       5 min         N/A
Test with example data                2 min         1 min
Prepare your data files               30-60 min     10-20 min
Validate data                         2 min         1 min
Generate figures                      1 min         30 sec
Generate tables                       1 min         30 sec
Review outputs                        10 min        5 min
Customize (optional)                  20-60 min     10-30 min
Integrate into manuscript             15 min        5 min
────────────────────────────────────────────────────────────────
TOTAL (first time)                    ~90 min
TOTAL (updates after revision)        ~20 min
```

---

This workflow assumes you've already completed your statistical analysis. The visualization package focuses solely on creating publication-quality outputs from your results.
