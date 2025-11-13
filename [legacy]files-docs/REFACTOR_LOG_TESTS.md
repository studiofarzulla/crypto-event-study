# Test Suite Integrity Analysis - File Reorganization Impact

**Date:** October 28, 2025
**Task:** Verify test suite integrity after code reorganization from flat structure to subdirectories
**Status:** CRITICAL ISSUES IDENTIFIED - All tests will fail without import fixes

---

## Executive Summary

**Verdict:** All test files have broken imports and will fail immediately upon execution.

**Impact:** Complete test suite failure - 0% tests will pass without fixes.

**Root Cause:** Tests use hardcoded paths and direct imports that assume flat code structure. Reorganization moved files into subdirectories (`code/core/`, `code/analysis/`, etc.) but tests still point to old locations.

**Critical Path:** Import fixer agent must update ALL test files before pytest can run successfully.

---

## New File Organization Structure

### Code Files Reorganized Into:
```
code/
├── __init__.py
├── core/                         # Core models and data pipeline
│   ├── __init__.py
│   ├── config.py                 # Was: code/config.py
│   ├── data_preparation.py       # Was: code/data_preparation.py
│   ├── garch_models.py           # Was: code/garch_models.py
│   ├── tarch_x_manual.py         # Was: code/tarch_x_manual.py
│   ├── tarch_x_manual_optimized.py
│   └── tarch_x_integration.py
├── analysis/                     # Event impact and hypothesis testing
│   ├── __init__.py
│   ├── event_impact_analysis.py  # Was: code/event_impact_analysis.py
│   └── hypothesis_testing_results.py
├── robustness/                   # Robustness checks
│   ├── __init__.py
│   ├── robustness_checks.py
│   ├── robustness_alternative_windows.py
│   └── robustness_placebo_outlier.py
├── inference/                    # Bootstrap inference
│   ├── __init__.py
│   ├── bootstrap_inference.py
│   └── bootstrap_inference_optimized.py
└── publication/                  # Publication outputs
    ├── __init__.py
    ├── publication_outputs.py
    ├── create_publication_figures.py
    ├── create_heterogeneity_figures.py
    └── generate_latex_tables.py
```

### Test Files (Unchanged Location):
```
tests/
├── __init__.py
├── conftest.py                   # Pytest fixtures and configuration
├── test_data_preparation_original.py
├── test_data_validation.py
├── test_edge_cases.py
├── test_garch_models.py
├── test_integration.py
├── test_statistical_methods.py
├── test_tarch_x_integration.py   # NOT a pytest test - script
└── publication_final_analysis.py # NOT a pytest test - script
```

---

## Test File Analysis - Broken Imports

### 1. `conftest.py` - CRITICAL FAILURE
**Status:** BROKEN
**Lines:** 15, 17-19

**Current Imports:**
```python
# Line 15: Hardcoded path manipulation
sys.path.insert(0, str(Path(__file__).parent.parent / 'event_study' / 'code'))

# Lines 17-19: Direct imports from flat structure
from data_preparation import DataPreparation
from garch_models import GARCHModels
import config
```

**Required Fixes:**
```python
# Option 1: Update path to include code/ directory
sys.path.insert(0, str(Path(__file__).parent.parent / 'code'))

# Option 2: Use proper package imports (RECOMMENDED)
from code.core.data_preparation import DataPreparation
from code.core.garch_models import GARCHModels
from code.core import config
```

**Impact:** ALL tests depend on conftest.py fixtures. This breaks the entire test suite.

---

### 2. `test_data_preparation_original.py` - BROKEN
**Status:** BROKEN
**Lines:** 14, 16

**Current Imports:**
```python
# Line 14: Hardcoded path
sys.path.append(str(Path(__file__).parent.parent / 'code'))

# Line 16: Direct import
from data_preparation import DataPreparation
```

**Required Fixes:**
```python
from code.core.data_preparation import DataPreparation
```

**Test Count:** 26 test methods
**All Affected:** Yes - cannot even import the module

---

### 3. `test_data_validation.py` - PARTIALLY BROKEN
**Status:** RELIES ON CONFTEST
**Lines:** No direct imports (uses fixtures)

**Analysis:**
- Uses `data_prep` fixture from conftest.py
- Will fail when conftest.py fails to import
- No direct import statements to fix in this file
- **Fix required:** Only conftest.py needs updating

**Test Count:** 42 test methods
**Dependency:** Breaks when conftest.py breaks

---

### 4. `test_edge_cases.py` - BROKEN
**Status:** BROKEN
**Lines:** 13-14

**Current Imports:**
```python
from data_preparation import DataPreparation
from garch_models import GARCHModels
```

**Required Fixes:**
```python
from code.core.data_preparation import DataPreparation
from code.core.garch_models import GARCHModels
```

**Test Count:** 45 test methods
**All Affected:** Yes

---

### 5. `test_garch_models.py` - BROKEN
**Status:** BROKEN
**Lines:** 13

**Current Imports:**
```python
from garch_models import GARCHModels, ModelResults, estimate_models_for_crypto
```

**Required Fixes:**
```python
from code.core.garch_models import GARCHModels, ModelResults, estimate_models_for_crypto
```

**Test Count:** 38 test methods
**All Affected:** Yes

---

### 6. `test_integration.py` - BROKEN
**Status:** BROKEN
**Lines:** 15-17

**Current Imports:**
```python
from data_preparation import DataPreparation
from garch_models import GARCHModels, estimate_models_for_all_cryptos
from event_impact_analysis import EventImpactAnalysis, run_complete_analysis
```

**Required Fixes:**
```python
from code.core.data_preparation import DataPreparation
from code.core.garch_models import GARCHModels, estimate_models_for_all_cryptos
from code.analysis.event_impact_analysis import EventImpactAnalysis, run_complete_analysis
```

**Test Count:** 28 test methods (integration tests)
**All Affected:** Yes
**CRITICAL:** These are integration tests - most important for verifying end-to-end functionality

---

### 7. `test_statistical_methods.py` - BROKEN
**Status:** BROKEN
**Lines:** 13-14

**Current Imports:**
```python
from event_impact_analysis import EventImpactAnalysis
from garch_models import GARCHModels, ModelResults
```

**Required Fixes:**
```python
from code.analysis.event_impact_analysis import EventImpactAnalysis
from code.core.garch_models import GARCHModels, ModelResults
```

**Test Count:** 51 test methods (statistical validation)
**All Affected:** Yes
**CRITICAL:** These verify hypothesis testing and FDR correction - essential for publication

---

### 8. `test_tarch_x_integration.py` - NOT A PYTEST TEST
**Status:** BROKEN (but not a test file)
**Lines:** 12, 14-15

**Analysis:**
- This is a **standalone verification script**, NOT a pytest test
- Filename suggests it's a test but contains `if __name__ == "__main__"` execution
- Located in `tests/` directory but not discoverable by pytest (no `test_` methods)
- Will still break if executed directly

**Current Imports:**
```python
sys.path.append(str(Path(__file__).parent / 'code'))  # Line 12: Wrong path
from data_preparation import DataPreparation
from garch_models import GARCHModels
```

**Required Fixes:**
```python
from code.core.data_preparation import DataPreparation
from code.core.garch_models import GARCHModels
```

**Action:** Fix imports but exclude from pytest test count

---

### 9. `publication_final_analysis.py` - NOT A PYTEST TEST
**Status:** Analysis script in wrong location
**Lines:** No imports to fix (uses CSV files)

**Analysis:**
- This is a **publication analysis script**, NOT a test
- Located in `tests/` directory but shouldn't be
- Reads CSV outputs, doesn't import code modules
- Should be moved to `code/publication/` or `docs/analysis/`

**Action:** Move to appropriate directory, exclude from pytest

---

## Pytest Configuration Analysis

### `pytest.ini` - NEEDS UPDATE
**Status:** Coverage path needs updating

**Current Configuration:**
```ini
# Line 19: Coverage target points to old location
--cov=event_study/code
```

**Required Fix:**
```ini
--cov=code
```

**Impact:** Code coverage reporting will fail to find code files

---

## Import Pattern Summary

### Broken Import Patterns (All Files):
| Pattern | Count | New Pattern Required |
|---------|-------|----------------------|
| `from data_preparation import` | 4 files | `from code.core.data_preparation import` |
| `from garch_models import` | 5 files | `from code.core.garch_models import` |
| `from event_impact_analysis import` | 2 files | `from code.analysis.event_impact_analysis import` |
| `import config` | 1 file | `from code.core import config` |
| `sys.path.append/insert(...)` | 3 files | Should be removed or updated |

### Total Broken Imports: 15+ import statements across 8 files

---

## Test Discovery Impact

### Pytest Discovery Patterns (from pytest.ini):
```ini
python_files = test_*.py
python_classes = Test*
python_functions = test_*
testpaths = tests
```

**Will Discover:**
- ✓ `test_data_preparation_original.py` - 26 tests (all fail)
- ✓ `test_data_validation.py` - 42 tests (all fail)
- ✓ `test_edge_cases.py` - 45 tests (all fail)
- ✓ `test_garch_models.py` - 38 tests (all fail)
- ✓ `test_integration.py` - 28 tests (all fail)
- ✓ `test_statistical_methods.py` - 51 tests (all fail)
- ✗ `test_tarch_x_integration.py` - 0 tests (not a pytest file)
- ✗ `publication_final_analysis.py` - 0 tests (not a pytest file)

**Total Discoverable Tests:** 230 tests
**Currently Passing:** 0 tests (100% import failures)

---

## Verification Checklist for Post-Fix Testing

### Phase 1: Import Verification (MUST PASS FIRST)
```bash
# Test 1: Verify conftest.py imports work
python -c "from code.core.data_preparation import DataPreparation; print('OK')"
python -c "from code.core.garch_models import GARCHModels; print('OK')"
python -c "from code.core import config; print('OK')"

# Test 2: Verify analysis imports work
python -c "from code.analysis.event_impact_analysis import EventImpactAnalysis; print('OK')"

# Test 3: Verify conftest.py can be imported
python -c "import sys; sys.path.insert(0, 'tests'); import conftest; print('OK')"
```

### Phase 2: Fixture Validation
```bash
# Test fixtures are accessible
pytest tests/conftest.py --collect-only
```

### Phase 3: Individual Test File Execution
```bash
# Run each test file individually to isolate failures
pytest tests/test_data_preparation_original.py -v
pytest tests/test_data_validation.py -v
pytest tests/test_edge_cases.py -v
pytest tests/test_garch_models.py -v
pytest tests/test_integration.py -v
pytest tests/test_statistical_methods.py -v
```

### Phase 4: Full Test Suite
```bash
# Run complete test suite with coverage
pytest -v --cov=code --cov-report=html --cov-report=term-missing
```

### Phase 5: Coverage Validation
```bash
# Verify coverage report generates correctly
ls -la htmlcov/index.html  # Should exist after pytest run
```

---

## Recommended Test Execution Order

After import fixes are applied, run tests in this order to minimize debugging:

1. **Unit Tests (Least Dependencies):**
   - `test_data_preparation_original.py` - Core data pipeline
   - `test_garch_models.py` - Model estimation
   - `test_statistical_methods.py` - Statistical functions

2. **Data Validation Tests:**
   - `test_data_validation.py` - Data quality checks

3. **Edge Case Tests:**
   - `test_edge_cases.py` - Boundary conditions

4. **Integration Tests (Most Dependencies):**
   - `test_integration.py` - End-to-end pipeline

**Rationale:** If unit tests fail, integration tests will definitely fail. Fix foundation first.

---

## Critical Path Items

### Must Fix Before ANY Tests Can Run:
1. ✅ **conftest.py imports** - Blocks all tests via fixtures
2. ✅ **Individual test file imports** - Each file must import correctly
3. ✅ **pytest.ini coverage path** - Must point to `code/` not `event_study/code/`

### Should Fix But Not Blocking:
4. ⚠️ Move `publication_final_analysis.py` out of `tests/` directory
5. ⚠️ Rename or relocate `test_tarch_x_integration.py` (misleading name)

---

## Import Fix Strategy for Each File

### Priority 1 (CRITICAL - Breaks Everything):
**File:** `conftest.py`
**Changes Required:**
```python
# BEFORE (Lines 15, 17-19):
sys.path.insert(0, str(Path(__file__).parent.parent / 'event_study' / 'code'))
from data_preparation import DataPreparation
from garch_models import GARCHModels
import config

# AFTER:
# Remove sys.path manipulation entirely
from code.core.data_preparation import DataPreparation
from code.core.garch_models import GARCHModels
from code.core import config
```

### Priority 2 (HIGH - Individual Test Files):
**Files:** `test_data_preparation_original.py`, `test_edge_cases.py`, `test_garch_models.py`, `test_integration.py`, `test_statistical_methods.py`

**Pattern to Apply:**
```python
# REPLACE ALL:
from data_preparation import X
from garch_models import X
from event_impact_analysis import X
import config

# WITH:
from code.core.data_preparation import X
from code.core.garch_models import X
from code.analysis.event_impact_analysis import X
from code.core import config
```

### Priority 3 (MEDIUM - Configuration):
**File:** `pytest.ini`
**Change:**
```ini
# BEFORE:
--cov=event_study/code

# AFTER:
--cov=code
```

---

## Test Suite Health Metrics (Post-Fix Expected)

### Current State (Pre-Fix):
- **Discoverable Tests:** 230
- **Runnable Tests:** 0 (100% import failures)
- **Passing Tests:** 0
- **Code Coverage:** 0% (cannot execute)

### Expected State (Post-Fix):
- **Discoverable Tests:** 230
- **Runnable Tests:** 230 (100% if imports fixed correctly)
- **Passing Tests:** ~184-207 (80-90% based on CLAUDE.md target)
- **Code Coverage:** >80% (per publication requirements)

### Known Test Markers (from pytest.ini):
- `@pytest.mark.unit` - Unit tests for individual functions
- `@pytest.mark.integration` - Integration tests (slower)
- `@pytest.mark.statistical` - Statistical validation tests
- `@pytest.mark.edge_case` - Edge case and error handling
- `@pytest.mark.slow` - Long-running tests (bootstrap, robustness)
- `@pytest.mark.reproducibility` - Fixed-seed verification
- `@pytest.mark.data_validation` - Data quality tests

---

## Potential Runtime Issues (Beyond Imports)

### 1. Data File Dependencies
**Files Affected:** All integration tests
**Requirement:** Test data must exist in `data/` directory:
- `data/btc.csv`, `data/eth.csv`, etc.
- `data/events.csv`
- `data/gdelt.csv`

**Current Handling:** Tests use `pytest.skip()` if data not found (good practice)

### 2. Output Directory Creation
**Files Affected:** Integration tests, publication tests
**Requirement:** `outputs/` directory structure
**Current Handling:** Uses `tmp_path_factory` fixture for test outputs (good practice)

### 3. Slow Tests
**Markers:** `@pytest.mark.slow` on bootstrap and robustness tests
**Recommendation:** Run fast tests first, slow tests separately:
```bash
# Fast tests only
pytest -v -m "not slow"

# Slow tests only
pytest -v -m "slow"
```

### 4. External Dependencies
**Bootstrap Tests:** Require `psutil` for memory monitoring
**Statistical Tests:** Require `scipy.stats` for hypothesis testing
**Current Handling:** Listed in `requirements-test.txt` (should be installed)

---

## Files Requiring No Changes

**Good News:** These test files don't need import updates because they use fixtures exclusively:

1. `test_data_validation.py` - Uses `data_prep` fixture from conftest
2. `tests/__init__.py` - Empty init file, no imports

**Condition:** These will work once `conftest.py` is fixed.

---

## Summary of Required Actions

### For Import Fixer Agent:

1. **Update conftest.py** (CRITICAL - Priority 1)
   - Line 15: Remove or update sys.path manipulation
   - Lines 17-19: Change to `from code.core.X import Y`

2. **Update test_data_preparation_original.py**
   - Line 14: Remove sys.path manipulation
   - Line 16: Change to `from code.core.data_preparation import DataPreparation`

3. **Update test_edge_cases.py**
   - Lines 13-14: Change to `from code.core.X import Y`

4. **Update test_garch_models.py**
   - Line 13: Change to `from code.core.garch_models import ...`

5. **Update test_integration.py**
   - Lines 15-17: Update to use `code.core.X` and `code.analysis.Y`

6. **Update test_statistical_methods.py**
   - Lines 13-14: Update to use `code.analysis.X` and `code.core.Y`

7. **Update pytest.ini**
   - Line 19: Change `--cov=event_study/code` to `--cov=code`

8. **Update test_tarch_x_integration.py** (Optional - not a pytest test)
   - Lines 12, 14-15: Update imports for standalone execution

### Total Files to Modify: 8 files
### Total Import Statements to Fix: ~15 import lines
### Total sys.path Manipulations to Remove: 3 instances

---

## Post-Fix Validation Commands

After import fixer completes, run these commands to verify:

```bash
# 1. Verify Python can import code modules
python -c "from code.core.data_preparation import DataPreparation; print('✓ core.data_preparation')"
python -c "from code.core.garch_models import GARCHModels; print('✓ core.garch_models')"
python -c "from code.analysis.event_impact_analysis import EventImpactAnalysis; print('✓ analysis.event_impact_analysis')"

# 2. Test collection (should find 230 tests)
pytest --collect-only | grep "test session starts"

# 3. Run quick smoke test (single test file)
pytest tests/test_data_validation.py::TestDataLoading::test_load_crypto_prices_btc -v

# 4. Run full suite if smoke test passes
pytest -v --tb=short

# 5. Generate coverage report
pytest --cov=code --cov-report=term-missing --cov-report=html
```

---

## Risk Assessment

### High Risk (Certain Failure):
- **Import errors** - 100% of tests will fail until fixed
- **Fixture failures** - All tests using `data_prep`, `btc_data_sample`, etc.

### Medium Risk (Likely Issues):
- **Path assumptions** - Hardcoded paths in test data loading
- **Coverage reporting** - Wrong coverage target path

### Low Risk (Unlikely):
- **Test logic** - Tests themselves are well-written
- **Data fixtures** - Fixture design is sound (uses conftest.py correctly)
- **Test markers** - Proper use of pytest markers

---

## Conclusion

**Current Status:** Complete test suite failure due to import path changes.

**Fix Complexity:** Low - Straightforward import path updates, no test logic changes needed.

**Fix Time Estimate:** 10-15 minutes for automated import fixer.

**Testing Time Estimate:** 5-10 minutes to validate fixes, 30-60 minutes for full test suite run.

**Success Criteria:**
1. All imports resolve without errors
2. Pytest discovers 230 tests
3. At least 80% of tests pass (per CLAUDE.md target)
4. Code coverage >80% in `code/` directory

**Next Steps:**
1. Import fixer agent updates all import statements
2. Verify imports work with Python interpreter
3. Run pytest collection to confirm 230 tests found
4. Execute tests in recommended order
5. Review failures and iterate if needed

---

**Report Generated:** October 28, 2025
**Analysis Complete:** Ready for import fixer agent to proceed
