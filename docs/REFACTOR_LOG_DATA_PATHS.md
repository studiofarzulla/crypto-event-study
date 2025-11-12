# Data Path Reference Audit (Post-Refactor)

**Date:** October 28, 2025
**Context:** Files were reorganized into subdirectories (`code/core/`, `code/analysis/`, etc.) but `data/` and `outputs/` directories remained at project root. This audit identifies all data path references that may be broken.

## Executive Summary

**CRITICAL ISSUE IDENTIFIED:** `config.py` BASE_DIR calculation is broken after move to `code/core/` subdirectory.

```python
# config.py line 16
BASE_DIR = Path(__file__).parent.parent
```

When `config.py` was at project root:
- `BASE_DIR = Path('config.py').parent = /home/kawaiikali/event-study/`
- `DATA_DIR = BASE_DIR / 'data' = /home/kawaiikali/event-study/data/` ✓

After move to `code/core/config.py`:
- `BASE_DIR = Path('code/core/config.py').parent.parent = /home/kawaiikali/event-study/code/`
- `DATA_DIR = BASE_DIR / 'data' = /home/kawaiikali/event-study/code/data/` ✗ WRONG!

**Impact:** Any file using `config.DATA_DIR` will look for data in the wrong location.

---

## Category 1: CRITICAL - Broken config.DATA_DIR Reference

### File: `code/core/config.py`

**Line 16:** `BASE_DIR = Path(__file__).parent.parent`

**Problem:**
- Now resolves to `code/` directory instead of project root
- Should be `Path(__file__).parent.parent.parent` to get to project root

**Fix Required:**
```python
# OLD (broken after refactor)
BASE_DIR = Path(__file__).parent.parent

# NEW (correct for code/core/config.py location)
BASE_DIR = Path(__file__).parent.parent.parent
```

**Files Affected (use config.DATA_DIR):**
1. `code/core/data_preparation.py` (line 32)
2. `code/scripts/run_event_study_analysis.py` (line 77, 101)
3. `code/robustness/robustness_checks.py` (line 751)
4. `code/core/tarch_x_integration.py` (line 187)
5. `code/analysis/hypothesis_testing_results.py` (line 37)

---

## Category 2: HIGH PRIORITY - Hardcoded Absolute Paths (Old Structure)

### Files with `/home/kawaiikali/event-study/` paths

These paths assume the old project structure and won't work in the new location.

| File | Line | Current Path | Needs Fix? |
|------|------|--------------|------------|
| `code/utils/quick_anomaly_scan.py` | 5 | `/home/kawaiikali/event-study/event_study/data` | YES - double event_study |
| `code/exploratory/ftx_anomaly_detection.py` | 26-27 | `/home/kawaiikali/event-study/event_study/data` | YES - double event_study |
| `code/exploratory/ftx_time_series_forecast.py` | 35-36 | `/home/kawaiikali/event-study/event_study/data` | YES - double event_study |
| `code/utils/validate_data.py` | 16 | `/home/kawaiikali/event-study/data` | YES - old location |
| `code/publication/generate_latex_tables.py` | 18 | `/home/kawaiikali/event-study/publication_tables` | YES - old location |
| `code/publication/create_heterogeneity_figures.py` | 64 | `/home/kawaiikali/event-study/publication_figures` | YES - old location |
| `code/publication/create_heterogeneity_figures.py` | 90 | `/home/kawaiikali/event-study/event_study/outputs` | YES - double event_study |
| `code/publication/create_publication_figures.py` | 73 | `/home/kawaiikali/event-study/publication_figures` | YES - old location |
| `code/publication/create_publication_figures.py` | 426 | `/home/kawaiikali/event-study/data` | YES - old location |
| `code/robustness/robustness_alternative_windows.py` | 33 | `/home/kawaiikali/event-study` | YES - old location |
| `code/legacy/data_preparation_template.py` | 19 | `/home/kawaiikali/event-study/data` | MAYBE - in legacy/ |

**Pattern:** Most files have old absolute paths that should use `config.DATA_DIR` instead.

**Recommended Fix:** Replace all hardcoded paths with config imports:
```python
# BAD
DATA_DIR = "/home/kawaiikali/event-study/event_study/data"

# GOOD
from code.core import config
DATA_DIR = config.DATA_DIR
```

---

## Category 3: MEDIUM PRIORITY - Relative Paths with `event_study/` Prefix

### Files using `event_study/data/` or `event_study/outputs/` patterns

These paths assume execution from parent directory of `event_study/` folder. They work if you run scripts from `/home/kawaiikali/Resurrexi/projects/planned-publish/` but fail if you run from project root.

| File | Line | Path Pattern | Context |
|------|------|--------------|---------|
| `tests/publication_final_analysis.py` | 28-29 | `'event_study/data/events.csv'` | Assumes running from parent dir |
| `tests/publication_final_analysis.py` | 454 | `'event_study/outputs/publication_final_statistics.csv'` | Assumes running from parent dir |
| `code/legacy/fix_correlation_matrix.py` | 35 | `'event_study/outputs/analysis_results/model_parameters'` | Legacy script |
| `code/legacy/fix_correlation_matrix.py` | 44 | `f'event_study/outputs/volatility_{crypto}.csv'` | Legacy script |
| `code/robustness/robustness_placebo_outlier.py` | 34-38 | `'event_study/data/events.csv'` | Active robustness check |
| `code/legacy/temporal_stability_analysis.py` | 30-31 | `'event_study/outputs/publication/csv_exports/event_impacts_fdr.csv'` | Legacy analysis |

**Problem:** These paths only work when CWD is `/home/kawaiikali/Resurrexi/projects/planned-publish/`, not when CWD is the project root.

**Recommended Fix:** Use `config.DATA_DIR` and `config.OUTPUTS_DIR` for portable paths:
```python
# BAD
events = pd.read_csv('event_study/data/events.csv')

# GOOD
from code.core import config
from pathlib import Path
events = pd.read_csv(Path(config.DATA_DIR) / 'events.csv')
```

---

## Category 4: LOW PRIORITY - Files Using config Properly (Good Examples)

These files demonstrate correct usage of the config module:

| File | Usage Pattern | Status |
|------|---------------|--------|
| `code/core/data_preparation.py` | `self.data_path = Path(data_path) if data_path else Path(config.DATA_DIR)` | ✓ GOOD (once config fixed) |
| `code/scripts/run_event_study_analysis.py` | `data_path = Path(config.DATA_DIR)` | ✓ GOOD (once config fixed) |
| `code/robustness/robustness_checks.py` | `data_prep = DataPreparation()  # Will use config.DATA_DIR by default` | ✓ GOOD (once config fixed) |

---

## Category 5: LEGACY FILES - May Not Need Fixing

Files in `[legacy]files-docs/` directory with hardcoded paths:

| File | Line | Path | Fix? |
|------|------|------|------|
| `[legacy]files-docs/coingecko_fetcher.py` | 61 | `"data/events"` | NO - deprecated |
| `[legacy]files-docs/run_complete_demo.py` | 77 | `/home/kawaiikali/event-study/publication_figures` | NO - deprecated |
| `[legacy]files-docs/convert_docx.py` | 173 | `/home/kawaiikali/event-study/temp_docx_extract/` | NO - one-time script |

**Recommendation:** Leave legacy files as-is unless they're actively used.

---

## Detailed Path Reference Table

### All Data Path References (Sorted by Priority)

| Priority | File | Line | Pattern | Type | Fix Required |
|----------|------|------|---------|------|--------------|
| **CRITICAL** | `code/core/config.py` | 16 | `Path(__file__).parent.parent` | BASE_DIR calc | YES - add .parent |
| **HIGH** | `code/utils/quick_anomaly_scan.py` | 5 | `/home/kawaiikali/event-study/event_study/data` | Absolute | YES - use config |
| **HIGH** | `code/exploratory/ftx_anomaly_detection.py` | 26 | `/home/kawaiikali/event-study/event_study/data` | Absolute | YES - use config |
| **HIGH** | `code/exploratory/ftx_time_series_forecast.py` | 35 | `/home/kawaiikali/event-study/event_study/data` | Absolute | YES - use config |
| **HIGH** | `code/utils/validate_data.py` | 16 | `/home/kawaiikali/event-study/data` | Absolute | YES - use config |
| **HIGH** | `code/publication/generate_latex_tables.py` | 18 | `/home/kawaiikali/event-study/publication_tables` | Absolute | YES - use config |
| **HIGH** | `code/publication/create_heterogeneity_figures.py` | 64 | `/home/kawaiikali/event-study/publication_figures` | Absolute | YES - use config |
| **HIGH** | `code/publication/create_heterogeneity_figures.py` | 90 | `/home/kawaiikali/event-study/event_study/outputs` | Absolute | YES - use config |
| **HIGH** | `code/publication/create_publication_figures.py` | 73 | `/home/kawaiikali/event-study/publication_figures` | Absolute | YES - use config |
| **HIGH** | `code/publication/create_publication_figures.py` | 426 | `/home/kawaiikali/event-study/data` | Absolute | YES - use config |
| **HIGH** | `code/robustness/robustness_alternative_windows.py` | 33 | `/home/kawaiikali/event-study` | Absolute | YES - use config |
| **MEDIUM** | `tests/publication_final_analysis.py` | 28 | `'event_study/data/events.csv'` | Relative | YES - use config |
| **MEDIUM** | `tests/publication_final_analysis.py` | 454 | `'event_study/outputs/publication_final_statistics.csv'` | Relative | YES - use config |
| **MEDIUM** | `code/robustness/robustness_placebo_outlier.py` | 34 | `'event_study/data/events.csv'` | Relative | YES - use config |
| **MEDIUM** | `code/robustness/robustness_placebo_outlier.py` | 35 | `'event_study/outputs/publication/csv_exports/event_impacts_fdr.csv'` | Relative | YES - use config |
| **MEDIUM** | `code/robustness/robustness_placebo_outlier.py` | 38 | `'event_study/data/btc.csv'` | Relative | YES - use config |
| **LOW** | `code/legacy/fix_correlation_matrix.py` | 35 | `'event_study/outputs/analysis_results/model_parameters'` | Relative | MAYBE - legacy |
| **LOW** | `code/legacy/temporal_stability_analysis.py` | 30 | `'event_study/outputs/publication/csv_exports/event_impacts_fdr.csv'` | Relative | MAYBE - legacy |
| **LOW** | `code/legacy/data_preparation_template.py` | 19 | `/home/kawaiikali/event-study/data` | Absolute | NO - template |
| **SKIP** | `[legacy]files-docs/coingecko_fetcher.py` | 61 | `"data/events"` | Relative | NO - deprecated |
| **SKIP** | `[legacy]files-docs/run_complete_demo.py` | 77 | `/home/kawaiikali/event-study/publication_figures` | Absolute | NO - deprecated |

---

## Recommended Fix Order

### Step 1: Fix config.py BASE_DIR (CRITICAL)
This fixes all files that properly use `config.DATA_DIR`:

```python
# code/core/config.py line 16
# OLD
BASE_DIR = Path(__file__).parent.parent

# NEW
BASE_DIR = Path(__file__).parent.parent.parent
```

**Validates:** 5 files immediately work correctly after this fix.

### Step 2: Fix High-Priority Hardcoded Paths
Replace all `/home/kawaiikali/event-study/` paths in active code:

1. `code/utils/quick_anomaly_scan.py`
2. `code/utils/validate_data.py`
3. `code/exploratory/ftx_anomaly_detection.py`
4. `code/exploratory/ftx_time_series_forecast.py`
5. `code/publication/*.py` (3 files)
6. `code/robustness/robustness_alternative_windows.py`

**Pattern:**
```python
# Add at top of file
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from code.core import config

# Replace hardcoded paths
DATA_DIR = config.DATA_DIR
OUTPUTS_DIR = config.OUTPUTS_DIR
```

### Step 3: Fix Medium-Priority Relative Paths
Replace `event_study/data/` patterns in active scripts:

1. `tests/publication_final_analysis.py`
2. `code/robustness/robustness_placebo_outlier.py`

**Pattern:**
```python
# OLD
events = pd.read_csv('event_study/data/events.csv')

# NEW
from code.core import config
events = pd.read_csv(Path(config.DATA_DIR) / 'events.csv')
```

### Step 4: Evaluate Legacy Files
Review files in `code/legacy/` to determine if they're still used:
- If used: Apply fixes from Steps 2-3
- If deprecated: Add warning comment or move to `[legacy]files-docs/`

---

## Files Using config Correctly (No Changes Needed)

These files will work correctly once `config.py` BASE_DIR is fixed:

1. `code/core/data_preparation.py` - Uses `config.DATA_DIR` as default parameter
2. `code/scripts/run_event_study_analysis.py` - Imports and uses `config.DATA_DIR`
3. `code/robustness/robustness_checks.py` - Uses `DataPreparation()` which uses config
4. `code/core/tarch_x_integration.py` - Uses `DataPreparation()` which uses config
5. `code/analysis/hypothesis_testing_results.py` - Uses `DataPreparation()` which uses config

---

## Testing Validation

### Test 1: Verify config.DATA_DIR Resolution
```bash
python3 -c "from code.core.config import DATA_DIR; print(f'DATA_DIR: {DATA_DIR}')"
# Expected: /home/kawaiikali/Resurrexi/projects/planned-publish/event-study/data
```

### Test 2: Verify data files accessible
```bash
python3 -c "from code.core.config import DATA_DIR; from pathlib import Path; print(list(Path(DATA_DIR).glob('*.csv')))"
# Expected: List of btc.csv, eth.csv, events.csv, etc.
```

### Test 3: Run data preparation
```bash
python3 -c "from code.core.data_preparation import DataPreparation; prep = DataPreparation('btc'); print('Data path:', prep.data_path)"
# Expected: /home/kawaiikali/Resurrexi/projects/planned-publish/event-study/data
```

### Test 4: Run smoke tests
```bash
python code/scripts/run_smoke_tests.py
# Expected: All tests pass
```

---

## Impact Analysis

### Files Broken by Current config.py (5 files)
All files using `config.DATA_DIR` will fail to find data:
1. `code/core/data_preparation.py`
2. `code/scripts/run_event_study_analysis.py`
3. `code/robustness/robustness_checks.py`
4. `code/core/tarch_x_integration.py`
5. `code/analysis/hypothesis_testing_results.py`

### Files with Incorrect Hardcoded Paths (11 files)
Will fail regardless of config.py fix:
1. `code/utils/quick_anomaly_scan.py`
2. `code/utils/validate_data.py`
3. `code/exploratory/ftx_anomaly_detection.py`
4. `code/exploratory/ftx_time_series_forecast.py`
5. `code/publication/generate_latex_tables.py`
6. `code/publication/create_heterogeneity_figures.py` (2 paths)
7. `code/publication/create_publication_figures.py` (2 paths)
8. `code/robustness/robustness_alternative_windows.py`

### Files with Relative Path Issues (3 files)
Will fail when run from project root:
1. `tests/publication_final_analysis.py`
2. `code/robustness/robustness_placebo_outlier.py`
3. `code/legacy/temporal_stability_analysis.py`

### Total Files Requiring Fixes: 19 files
- 1 CRITICAL (config.py)
- 11 HIGH priority (hardcoded paths)
- 3 MEDIUM priority (relative paths)
- 4 LOW priority (legacy files - evaluate first)

---

## Additional Notes

### Double `event_study/` Pattern
Several files have paths like `/home/kawaiikali/event-study/event_study/data` suggesting the project was nested:
- `/home/kawaiikali/event-study/` (outer directory)
- `/home/kawaiikali/event-study/event_study/` (project root)

This pattern appears in:
- `code/utils/quick_anomaly_scan.py`
- `code/exploratory/ftx_anomaly_detection.py`
- `code/exploratory/ftx_time_series_forecast.py`
- `code/publication/create_heterogeneity_figures.py`

**Current Structure:**
```
/home/kawaiikali/Resurrexi/projects/planned-publish/event-study/
├── code/
├── data/
├── outputs/
└── tests/
```

### CSV File References
Files frequently access these CSVs:
1. `data/*.csv` - Crypto price data (btc.csv, eth.csv, etc.)
2. `data/events.csv` - Event definitions
3. `data/gdelt.csv` - Sentiment data
4. `outputs/publication/csv_exports/event_impacts_fdr.csv` - Analysis results
5. `outputs/analysis_results/*.csv` - Various analysis outputs

All should use `config.DATA_DIR` and `config.OUTPUTS_DIR` for portable access.

---

## Conclusion

**The refactor broke data path resolution in 19 files.** The root cause is `config.py` BASE_DIR calculation being off by one `.parent` level after moving from project root to `code/core/` subdirectory.

**Single-line fix** in `config.py` resolves 5 files immediately. The remaining 14 active files need hardcoded path replacements with config imports.

**Estimated fix time:** 30-45 minutes for all high/medium priority files.

---

## Verification of Current State

### Data Directory Location (Verified Oct 28, 2025)

**✓ CORRECT:** Data directory is at project root
```
/home/kawaiikali/Resurrexi/projects/planned-publish/event-study/data/
├── ada.csv
├── bnb.csv
├── btc.csv
├── eth.csv
├── events.csv
├── gdelt.csv
├── ltc.csv
└── xrp.csv
```

**✓ CONFIRMED:** No data directory exists at `code/data/` (would be wrong location)

### config.py Resolution Test

```python
# Current (BROKEN)
config_file = Path('code/core/config.py')
BASE_DIR = config_file.parent.parent
# Result: /home/kawaiikali/Resurrexi/projects/planned-publish/event-study/code/
DATA_DIR = BASE_DIR / 'data'
# Result: /home/kawaiikali/Resurrexi/projects/planned-publish/event-study/code/data/
# Status: ✗ WRONG - directory doesn't exist

# After Fix (CORRECT)
config_file = Path('code/core/config.py')
BASE_DIR = config_file.parent.parent.parent
# Result: /home/kawaiikali/Resurrexi/projects/planned-publish/event-study/
DATA_DIR = BASE_DIR / 'data'
# Result: /home/kawaiikali/Resurrexi/projects/planned-publish/event-study/data/
# Status: ✓ CORRECT - matches actual data location
```

### Expected Directory Structure

```
event-study/                                    ← BASE_DIR should point here
├── code/                                       ← Current (broken) BASE_DIR
│   ├── core/
│   │   └── config.py                           ← Path(__file__).parent.parent.parent
│   ├── analysis/
│   ├── publication/
│   ├── robustness/
│   ├── scripts/
│   └── utils/
├── data/                                       ← DATA_DIR (actual location)
│   ├── btc.csv
│   ├── eth.csv
│   └── ...
├── outputs/                                    ← OUTPUTS_DIR (actual location)
└── tests/
```

