# REFACTOR LOG: REDUNDANCY ANALYSIS
**Created:** October 28, 2025
**Repository:** `/home/kawaiikali/Resurrexi/projects/planned-publish/event-study/`
**Purpose:** Identify redundant files and provide safe removal strategy

---

## EXECUTIVE SUMMARY

**Files Already Organized:** The codebase has been partially refactored into subdirectories (core/, inference/, analysis/, etc.), but several redundant pairs exist.

**Key Finding:** All redundant "optimized" versions are **NOT currently used** by the main analysis pipeline. The original versions are imported and actively used.

**Safe Action:** The optimized versions can be kept for future performance work, but should be clearly documented as "experimental" or moved to a separate performance/ directory.

---

## REDUNDANCY ANALYSIS TABLE

| Original File | Optimized/Redundant File | Lines | Currently Used? | Import Dependencies | Status |
|--------------|-------------------------|-------|-----------------|-------------------|---------|
| `core/tarch_x_manual.py` | `core/tarch_x_manual_optimized.py` | 539 vs 566 | **Original used** | `core/garch_models.py`, `core/tarch_x_integration.py`, `scripts/run_smoke_tests.py` | Keep both (document) |
| `inference/bootstrap_inference.py` | `inference/bootstrap_inference_optimized.py` | 367 vs 488 | **Original used** | `scripts/run_event_study_analysis.py`, `analysis/hypothesis_testing_results.py`, `robustness/robustness_checks.py`, `tests/test_statistical_methods.py` | Keep both (document) |
| N/A | `core/tarch_x_integration.py` | 298 | **NOT used** | None (documentation only) | **MOVE to docs/** |
| `temporal_stability_analysis.py` | `publication/create_temporal_stability_figure.py` | Unknown vs exists | **Figure script used** | None (hardcoded data) | **REMOVE temporal_stability_analysis.py** |
| N/A | `data_preparation_template.py` | 273 | **NOT used** | None (template) | **MOVE to legacy/** |
| N/A | `extract_volatility_template.py` | 61 | **NOT used** | None (template) | **MOVE to legacy/** |
| N/A | `extract_volatility.py` | 142 | **NOT used** | None (superseded) | **MOVE to legacy/** |
| N/A | `fix_correlation_matrix.py` | 361 | **NOT used** | None (one-time fix) | **MOVE to legacy/** |
| N/A | `validate_fixes.py` | 167 | **NOT used** | None (one-time validation) | **MOVE to legacy/** |

---

## DETAILED ANALYSIS

### 1. `tarch_x_manual.py` vs `tarch_x_manual_optimized.py`

#### Status: **BOTH SHOULD BE KEPT**

#### File Locations
- **Original:** `/code/core/tarch_x_manual.py` (539 lines)
- **Optimized:** `/code/core/tarch_x_manual_optimized.py` (566 lines)

#### Currently Used: **Original (tarch_x_manual.py)**

#### Import Dependencies (Original)
```python
# Direct imports found:
1. code/core/garch_models.py:33
   from tarch_x_manual import estimate_tarch_x_manual

2. code/core/tarch_x_integration.py:16
   from tarch_x_manual import estimate_tarch_x_manual, TARCHXResults

3. code/scripts/run_smoke_tests.py:100,132
   from tarch_x_manual import TARCHXEstimator
```

#### Import Dependencies (Optimized)
**NONE** - The optimized version is NOT imported by any active code.

#### Key Differences
- **Original:**
  - Clear academic implementation
  - Full docstrings explaining TARCH-X methodology
  - GJR-GARCH specification with Student-t distribution
  - Standard numerical Hessian for standard errors

- **Optimized:**
  - 5x faster variance recursion (vectorized)
  - 100x faster Hessian (BFGS approximation)
  - Caching and logging improvements
  - Type hints with numpy.typing

#### Recommendation: **KEEP BOTH**

**Rationale:**
1. Original is used in published research (DOI: 10.5281/zenodo.17449736)
2. Optimized version provides performance gains for future work
3. Both implementations serve as cross-validation

**Action Required:**
```bash
# Add README to core/ directory documenting which to use
cat > code/core/README_TARCH_IMPLEMENTATION.md << 'EOF'
# TARCH-X Implementation Versions

## Active Version (DO NOT MODIFY)
**File:** `tarch_x_manual.py`
**Status:** Used in published research (Zenodo DOI: 10.5281/zenodo.17449736)
**Purpose:** Academic reference implementation with full documentation

## Experimental Version
**File:** `tarch_x_manual_optimized.py`
**Status:** Performance-optimized (5-10x speedup), NOT currently used
**Purpose:** Future performance work, requires validation against original

## Which Should I Import?
- For reproducible research: `from tarch_x_manual import estimate_tarch_x_manual`
- For performance testing: `from tarch_x_manual_optimized import estimate_tarch_x_manual`

## Validation Required Before Switching
- [ ] Numerical results match within rtol=1e-6
- [ ] All tests pass with optimized version
- [ ] Convergence rates are similar
- [ ] Standard errors are consistent
EOF
```

---

### 2. `bootstrap_inference.py` vs `bootstrap_inference_optimized.py`

#### Status: **BOTH SHOULD BE KEPT**

#### File Locations
- **Original:** `/code/inference/bootstrap_inference.py` (367 lines)
- **Optimized:** `/code/inference/bootstrap_inference_optimized.py` (488 lines)

#### Currently Used: **Original (bootstrap_inference.py)**

#### Import Dependencies (Original)
```python
# Direct imports found:
1. code/scripts/run_event_study_analysis.py:22
   from bootstrap_inference import run_bootstrap_analysis

2. code/analysis/hypothesis_testing_results.py:26
   from bootstrap_inference import BootstrapInference

3. code/robustness/robustness_checks.py:745
   from bootstrap_inference import run_bootstrap_analysis

4. tests/test_statistical_methods.py:326,338,392
   from bootstrap_inference import BootstrapInference
```

#### Import Dependencies (Optimized)
**NONE** - The optimized version is NOT imported by any active code.

#### Key Differences
- **Original:**
  - Standard residual bootstrap (Pascual et al. 2006)
  - Sequential processing (500 replications)
  - Progress bars with tqdm
  - arch package optional import

- **Optimized:**
  - Parallelized with joblib (5-10x speedup)
  - Vectorized block bootstrap
  - Better logging
  - Type safety with numpy.typing

#### Recommendation: **KEEP BOTH**

**Rationale:**
1. Original is used in published robustness checks
2. Optimized version provides 5-10x speedup for future analyses
3. Bootstrap is computationally expensive (30-60 minutes), optimization valuable

**Action Required:**
```bash
# Add README to inference/ directory
cat > code/inference/README_BOOTSTRAP.md << 'EOF'
# Bootstrap Inference Implementations

## Active Version (DO NOT MODIFY)
**File:** `bootstrap_inference.py`
**Status:** Used in published robustness checks
**Purpose:** Standard residual bootstrap following Pascual et al. (2006)

## Experimental Version
**File:** `bootstrap_inference_optimized.py`
**Status:** Parallelized version (5-10x speedup), NOT currently used
**Purpose:** Future performance work for large bootstrap replications

## Performance Comparison
- Original: ~30-60 minutes for 500 replications × 6 cryptos
- Optimized: ~5-10 minutes (parallelized with joblib)

## Which Should I Import?
- For reproducible research: `from bootstrap_inference import BootstrapInference`
- For large-scale simulations: `from bootstrap_inference_optimized import BootstrapInference`

## Validation Required Before Switching
- [ ] Confidence intervals match within acceptable tolerance
- [ ] Convergence rates are similar (>80%)
- [ ] Random seed reproducibility maintained
- [ ] No race conditions in parallel execution
EOF
```

---

### 3. `tarch_x_integration.py` - DOCUMENTATION ONLY

#### Status: **MOVE TO docs/**

#### File Location
- **Current:** `/code/core/tarch_x_integration.py` (298 lines)
- **Proposed:** `/docs/INTEGRATION_GUIDE_TARCH_X.md`

#### Currently Used: **NO**

#### Purpose
This file is a **standalone integration guide** showing how to use the manual TARCH-X implementation. It defines an `EnhancedGARCHModels` class that wraps the manual implementation, but this class is NOT used anywhere in the codebase.

#### Import Analysis
```bash
# Check if EnhancedGARCHModels is imported anywhere:
grep -r "EnhancedGARCHModels\|from.*tarch_x_integration" code/ tests/
# Result: NO IMPORTS FOUND
```

The file imports FROM other modules but is never imported BY other modules:
```python
from tarch_x_manual import estimate_tarch_x_manual, TARCHXResults
from data_preparation import DataPreparation
from garch_models import ModelResults
```

#### Recommendation: **MOVE TO docs/**

**Rationale:**
1. This is documentation, not production code
2. The integration pattern it describes is already implemented in `core/garch_models.py`
3. Keeping it in `code/` suggests it's part of the active codebase (misleading)
4. It provides valuable context for understanding the TARCH-X integration

**Action:**
```bash
# Move to docs and convert to markdown
mv code/core/tarch_x_integration.py docs/INTEGRATION_GUIDE_TARCH_X.py

# Add note at top explaining this is documentation
cat > docs/INTEGRATION_GUIDE_TARCH_X.md << 'EOF'
# TARCH-X Integration Guide

**Note:** This is documentation showing how the manual TARCH-X implementation
was integrated into the event study framework. The integration is already
complete in `code/core/garch_models.py` - this file is for reference only.

**Original File:** `code/core/tarch_x_integration.py` (moved to docs/ Oct 28, 2025)

---

[Convert Python docstrings and comments to markdown format here]
EOF
```

---

### 4. Template Files - MOVE TO legacy/

#### Files to Move
1. `data_preparation_template.py` (273 lines)
2. `extract_volatility_template.py` (61 lines)

#### Status: **MOVE TO legacy/**

#### Currently Used: **NO**

These are template files that were likely used during initial development but are no longer part of the active pipeline.

#### Recommendation: **MOVE TO legacy/**

**Action:**
```bash
# Move templates to legacy
mv code/data_preparation_template.py code/legacy/
mv code/extract_volatility_template.py code/legacy/

# Document what they were
cat > code/legacy/README_TEMPLATES.md << 'EOF'
# Legacy Template Files

These files were templates used during initial development.
They are NOT part of the active analysis pipeline.

## Files
- `data_preparation_template.py` - Template for data preparation module
- `extract_volatility_template.py` - Template for volatility extraction

## Why Kept
Historical reference for development process.

## Do NOT Use
Use the active versions in `code/core/data_preparation.py` instead.
EOF
```

---

### 5. One-Time Fix Scripts - MOVE TO legacy/

#### Files to Move
1. `extract_volatility.py` (142 lines) - Old extraction logic, superseded
2. `fix_correlation_matrix.py` (361 lines) - One-time correlation matrix fix
3. `validate_fixes.py` (167 lines) - One-time validation script
4. `temporal_stability_analysis.py` (Unknown lines) - Analysis script, results hardcoded in figure script

#### Status: **MOVE TO legacy/**

#### Currently Used: **NO**

These were one-time scripts for specific fixes/validations during development.

#### Recommendation: **MOVE TO legacy/**

**Action:**
```bash
# Move one-time scripts to legacy
mv code/extract_volatility.py code/legacy/
mv code/fix_correlation_matrix.py code/legacy/
mv code/validate_fixes.py code/legacy/
mv code/temporal_stability_analysis.py code/legacy/

# Document what they did
cat > code/legacy/README_ONE_TIME_SCRIPTS.md << 'EOF'
# Legacy One-Time Scripts

These scripts were used for specific fixes and validations during development.
They have been superseded by the main analysis pipeline.

## Files

### `extract_volatility.py`
**Purpose:** Old volatility extraction logic
**Superseded By:** `core/data_preparation.py` (integrated into main ETL pipeline)
**Date:** Pre-October 2025

### `fix_correlation_matrix.py`
**Purpose:** One-time fix for correlation matrix issues
**Status:** Fix applied, no longer needed
**Date:** October 2025

### `validate_fixes.py`
**Purpose:** One-time validation after applying fixes
**Status:** Validation complete, archived for reference
**Date:** October 2025

### `temporal_stability_analysis.py`
**Purpose:** Analysis script for temporal stability
**Superseded By:** `publication/create_temporal_stability_figure.py` (uses hardcoded results)
**Date:** October 2025

## Why Kept
Historical reference for understanding development decisions and fixes applied.

## Do NOT Use
These scripts are not part of the active analysis pipeline.
EOF
```

---

## IMPORT DEPENDENCY ANALYSIS

### Critical Imports That Would Break If Files Removed

#### 1. If `tarch_x_manual.py` is removed:
**BREAKS:**
- `core/garch_models.py` - Cannot estimate TARCH-X models
- `core/tarch_x_integration.py` - Integration guide broken (but already moving to docs/)
- `scripts/run_smoke_tests.py` - Smoke tests fail
- **ENTIRE ANALYSIS PIPELINE FAILS** - No TARCH-X estimation possible

#### 2. If `bootstrap_inference.py` is removed:
**BREAKS:**
- `scripts/run_event_study_analysis.py` - Cannot run bootstrap robustness checks
- `analysis/hypothesis_testing_results.py` - No confidence intervals
- `robustness/robustness_checks.py` - Robustness analysis incomplete
- `tests/test_statistical_methods.py` - Tests fail
- **ROBUSTNESS CHECKS INCOMPLETE** - Missing confidence intervals

#### 3. If optimized versions are removed:
**DOES NOT BREAK ANYTHING** - No active imports found

---

## SAFE REMOVAL STRATEGY

### Phase 1: Documentation Only (SAFE - No Code Changes)

**Actions:**
1. Create README files in `code/core/`, `code/inference/`, `code/legacy/`, `docs/`
2. Document which files are active vs experimental vs legacy
3. Add comments to import statements clarifying version choice

**Timeline:** Immediate (30 minutes)

**Risk:** ZERO - Only adds documentation

---

### Phase 2: Move Non-Critical Files (LOW RISK)

**Actions:**
1. Move `tarch_x_integration.py` to `docs/`
2. Move template files to `legacy/`
3. Move one-time scripts to `legacy/`
4. Update `.gitignore` to prevent accidental execution of legacy scripts

**Timeline:** Immediate (1 hour)

**Risk:** LOW - None of these files are imported by active code

**Verification:**
```bash
# After moving, verify no broken imports
python -c "
import sys
sys.path.append('code')
from core.garch_models import GARCHModels
from inference.bootstrap_inference import BootstrapInference
print('✓ All critical imports work')
"

# Run smoke tests
python code/scripts/run_smoke_tests.py
```

---

### Phase 3: Optional - Switch to Optimized Versions (MEDIUM RISK)

**Actions:**
1. Validate optimized versions match original results within tolerance
2. Update imports in main analysis pipeline
3. Run full test suite
4. Compare outputs with baseline

**Timeline:** 1-2 days (requires extensive validation)

**Risk:** MEDIUM - Could break numerical reproducibility

**Requirements Before Switching:**
- [ ] Numerical results match within rtol=1e-6
- [ ] All pytest tests pass
- [ ] Convergence rates are similar
- [ ] Standard errors are consistent
- [ ] AIC/BIC values match
- [ ] Publication figures unchanged
- [ ] CSV exports match baseline

**NOT RECOMMENDED FOR PUBLISHED RESEARCH** - Keep original versions for reproducibility

---

## RECOMMENDED ACTIONS (IN ORDER)

### Step 1: Document Current State (30 minutes)
```bash
# Create documentation files
touch code/core/README_TARCH_IMPLEMENTATION.md
touch code/inference/README_BOOTSTRAP.md
touch code/legacy/README_TEMPLATES.md
touch code/legacy/README_ONE_TIME_SCRIPTS.md
touch docs/INTEGRATION_GUIDE_TARCH_X.md

# Populate with content from this analysis
# (see individual sections above for content)
```

### Step 2: Move Non-Critical Files (1 hour)
```bash
# Move documentation file
mv code/core/tarch_x_integration.py docs/INTEGRATION_GUIDE_TARCH_X.py

# Move templates
mv code/data_preparation_template.py code/legacy/
mv code/extract_volatility_template.py code/legacy/

# Move one-time scripts
mv code/extract_volatility.py code/legacy/
mv code/fix_correlation_matrix.py code/legacy/
mv code/validate_fixes.py code/legacy/
mv code/temporal_stability_analysis.py code/legacy/
```

### Step 3: Verify No Breakage (15 minutes)
```bash
# Test imports
python -c "
import sys; sys.path.append('code')
from core.garch_models import GARCHModels
from inference.bootstrap_inference import BootstrapInference
print('✓ Critical imports work')
"

# Run smoke tests
python code/scripts/run_smoke_tests.py

# Run unit tests
pytest tests/ -v
```

### Step 4: Update Master Refactor Reference (15 minutes)
```bash
# Update MASTER_REFACTOR_REFERENCE.md to reflect completed actions
# Mark redundancies as "RESOLVED" in the table
```

---

## FILES TO KEEP (DO NOT REMOVE)

### Critical for Published Research
1. `core/tarch_x_manual.py` - Active TARCH-X implementation
2. `inference/bootstrap_inference.py` - Active bootstrap inference
3. `core/data_preparation.py` - ETL pipeline
4. `core/garch_models.py` - Model estimation interface
5. `analysis/event_impact_analysis.py` - Event coefficient extraction
6. `analysis/hypothesis_testing_results.py` - Statistical tests
7. `publication/*` - All publication output scripts

### Useful for Future Work
1. `core/tarch_x_manual_optimized.py` - Performance optimization
2. `inference/bootstrap_inference_optimized.py` - Parallelized bootstrap

### Historical Reference (Move to legacy/)
1. `data_preparation_template.py`
2. `extract_volatility_template.py`
3. `extract_volatility.py`
4. `fix_correlation_matrix.py`
5. `validate_fixes.py`
6. `temporal_stability_analysis.py`

### Documentation (Move to docs/)
1. `tarch_x_integration.py` → `docs/INTEGRATION_GUIDE_TARCH_X.md`

---

## SUMMARY

### Redundancies Identified: 9 files

### Safe to Move Immediately: 7 files
- `tarch_x_integration.py` → `docs/`
- `data_preparation_template.py` → `legacy/`
- `extract_volatility_template.py` → `legacy/`
- `extract_volatility.py` → `legacy/`
- `fix_correlation_matrix.py` → `legacy/`
- `validate_fixes.py` → `legacy/`
- `temporal_stability_analysis.py` → `legacy/`

### Keep Both Versions (Document): 2 pairs
- `tarch_x_manual.py` + `tarch_x_manual_optimized.py`
- `bootstrap_inference.py` + `bootstrap_inference_optimized.py`

### Critical Dependencies (DO NOT REMOVE)
- `tarch_x_manual.py` - 3 direct imports
- `bootstrap_inference.py` - 4 direct imports

### Risk Assessment
- **Phase 1 (Documentation):** ZERO risk
- **Phase 2 (Move files):** LOW risk (no active imports)
- **Phase 3 (Switch to optimized):** MEDIUM risk (requires validation)

### Estimated Time
- **Phase 1:** 30 minutes
- **Phase 2:** 1 hour
- **Total Safe Cleanup:** 1.5 hours

---

## NEXT STEPS

1. Review this analysis with user
2. Get approval for Phase 1 & 2 actions
3. Execute file moves
4. Verify no breakage
5. Update master refactor reference
6. Consider Phase 3 (optimized versions) as future performance work

---

**Analysis Complete**
**Date:** October 28, 2025
**Status:** Ready for review and execution
