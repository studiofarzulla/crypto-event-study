# REDUNDANCY REFACTOR SUMMARY
**Date:** October 28, 2025
**Analysis Complete:** Ready for execution

---

## VISUAL FILE MAP

```
CURRENT STATE:
event-study/
├── code/
│   ├── core/
│   │   ├── tarch_x_manual.py ✓ ACTIVE (used in published research)
│   │   ├── tarch_x_manual_optimized.py ⚡ EXPERIMENTAL (5-10x faster, not used)
│   │   ├── tarch_x_integration.py 📄 DOCUMENTATION ONLY → MOVE TO docs/
│   │   └── (other core files...)
│   │
│   ├── inference/
│   │   ├── bootstrap_inference.py ✓ ACTIVE (used in robustness checks)
│   │   └── bootstrap_inference_optimized.py ⚡ EXPERIMENTAL (5-10x faster, not used)
│   │
│   ├── data_preparation_template.py ❌ TEMPLATE → MOVE TO legacy/
│   ├── extract_volatility_template.py ❌ TEMPLATE → MOVE TO legacy/
│   ├── extract_volatility.py ❌ OLD LOGIC → MOVE TO legacy/
│   ├── fix_correlation_matrix.py ❌ ONE-TIME FIX → MOVE TO legacy/
│   ├── validate_fixes.py ❌ ONE-TIME VALIDATION → MOVE TO legacy/
│   └── temporal_stability_analysis.py ❌ SUPERSEDED → MOVE TO legacy/

PROPOSED STATE:
event-study/
├── code/
│   ├── core/
│   │   ├── tarch_x_manual.py ✓ ACTIVE
│   │   ├── tarch_x_manual_optimized.py ⚡ EXPERIMENTAL
│   │   └── README_TARCH_IMPLEMENTATION.md 📝 NEW
│   │
│   ├── inference/
│   │   ├── bootstrap_inference.py ✓ ACTIVE
│   │   ├── bootstrap_inference_optimized.py ⚡ EXPERIMENTAL
│   │   └── README_BOOTSTRAP.md 📝 NEW
│   │
│   └── legacy/ 📦 NEW DIRECTORY
│       ├── README_TEMPLATES.md 📝 NEW
│       ├── README_ONE_TIME_SCRIPTS.md 📝 NEW
│       ├── data_preparation_template.py ← MOVED
│       ├── extract_volatility_template.py ← MOVED
│       ├── extract_volatility.py ← MOVED
│       ├── fix_correlation_matrix.py ← MOVED
│       ├── validate_fixes.py ← MOVED
│       └── temporal_stability_analysis.py ← MOVED
│
└── docs/
    └── tarch_x_integration.py ← MOVED (documentation)
```

---

## REDUNDANCY ANALYSIS AT A GLANCE

| File Pair | Original | Optimized | Currently Used | Action |
|-----------|----------|-----------|----------------|--------|
| **TARCH-X** | 539 lines | 566 lines | ✓ Original | Keep both, document |
| **Bootstrap** | 367 lines | 488 lines | ✓ Original | Keep both, document |

**Speedup Available:**
- TARCH-X Optimized: 5-10x faster variance recursion
- Bootstrap Optimized: 5-10x faster (parallelized with joblib)

**Why Not Using Optimized?**
- Original versions used in published research (DOI: 10.5281/zenodo.17449736)
- Numerical reproducibility critical for academic work
- Optimized versions available for future performance work

---

## IMPORT DEPENDENCY MAP

```
CRITICAL DEPENDENCIES (DO NOT REMOVE):

tarch_x_manual.py ← REQUIRED BY:
├── core/garch_models.py:33
├── core/tarch_x_integration.py:16
└── scripts/run_smoke_tests.py:100,132

bootstrap_inference.py ← REQUIRED BY:
├── scripts/run_event_study_analysis.py:22
├── analysis/hypothesis_testing_results.py:26
├── robustness/robustness_checks.py:745
└── tests/test_statistical_methods.py:326,338,392

tarch_x_manual_optimized.py ← REQUIRED BY:
└── (NONE - not imported by any active code)

bootstrap_inference_optimized.py ← REQUIRED BY:
└── (NONE - not imported by any active code)
```

---

## FILES TO MOVE (7 files, NO ACTIVE IMPORTS)

### Documentation Only (1 file → docs/)
- `code/core/tarch_x_integration.py` (298 lines)
  - Purpose: Integration guide for TARCH-X
  - Why move: This is documentation, not production code
  - Imports from: `tarch_x_manual`, `data_preparation`, `garch_models`
  - Imported by: NONE

### Templates (2 files → legacy/)
- `code/data_preparation_template.py` (273 lines)
- `code/extract_volatility_template.py` (61 lines)

### One-Time Scripts (4 files → legacy/)
- `code/extract_volatility.py` (142 lines)
- `code/fix_correlation_matrix.py` (361 lines)
- `code/validate_fixes.py` (167 lines)
- `code/temporal_stability_analysis.py` (unknown lines)

---

## RISK ASSESSMENT

### Phase 1: Documentation (30 min)
**Risk:** ZERO
**Impact:** Clarifies which files are active vs experimental
**Reversibility:** N/A (only adds files)

### Phase 2: Move Files (1 hour)
**Risk:** LOW
**Impact:** Organizes legacy code, improves clarity
**Reversibility:** Easy (git checkout or mv back)
**Validation:** No broken imports (verified with grep)

### Phase 3: Switch to Optimized (Optional, NOT RECOMMENDED)
**Risk:** MEDIUM
**Impact:** 5-10x speedup, but breaks numerical reproducibility
**Reversibility:** Easy (change imports back)
**Validation Required:** Extensive testing, baseline comparison
**Recommendation:** DO NOT DO for published research

---

## EXECUTION PLAN (SAFE PATH)

### What We're Doing
1. Create README files documenting which versions are active
2. Move 7 files that have NO active imports to appropriate directories
3. Verify no breakage with import tests
4. Update master refactor reference

### What We're NOT Doing
- NOT removing any code (just moving to legacy/)
- NOT changing which versions are imported by active code
- NOT breaking any existing functionality
- NOT affecting published research results

### Time Estimate
- Phase 1 (Documentation): 30 minutes
- Phase 2 (Move files): 15 minutes
- Phase 3 (Verification): 15 minutes
- Phase 4 (Update docs): 15 minutes
- **Total: ~1.5 hours**

---

## SUCCESS CRITERIA

After execution, verify:

1. **Imports Work**
   ```bash
   python -c "import sys; sys.path.append('code'); from core.garch_models import GARCHModels; print('OK')"
   ```

2. **Tests Pass**
   ```bash
   pytest tests/ -v
   ```

3. **Files Organized**
   - 7 files moved to `legacy/`
   - 1 file moved to `docs/`
   - 4 README files created
   - No active code broken

4. **Documentation Updated**
   - MASTER_REFACTOR_REFERENCE.md reflects completed actions
   - README files explain which versions to use

---

## ROLLBACK PROCEDURE

If anything breaks:

```bash
# Restore all moved files
git checkout code/core/tarch_x_integration.py
git checkout code/data_preparation_template.py
git checkout code/extract_volatility_template.py
git checkout code/extract_volatility.py
git checkout code/fix_correlation_matrix.py
git checkout code/validate_fixes.py
git checkout code/temporal_stability_analysis.py
```

---

## DELIVERABLES

Three documents created:

1. **REFACTOR_LOG_REDUNDANCIES.md** (full analysis, 5000+ lines)
   - Comprehensive redundancy analysis
   - Import dependency mapping
   - Detailed recommendations
   - Step-by-step safe removal strategy

2. **REFACTOR_ACTIONS_CHECKLIST.md** (quick reference, ~300 lines)
   - Executable bash scripts for each phase
   - Verification commands
   - Rollback plan
   - Success checklist

3. **REFACTOR_SUMMARY.md** (this file, visual overview)
   - File map visualization
   - Import dependency diagram
   - Risk assessment
   - Executive summary

---

## NEXT STEPS

1. User reviews analysis
2. User approves Phase 1 & 2 (safe, low risk)
3. Execute Phase 1: Create README files (30 min)
4. Execute Phase 2: Move files to legacy/ and docs/ (15 min)
5. Execute Phase 3: Verify no breakage (15 min)
6. Execute Phase 4: Update master reference (15 min)
7. Optional: Consider Phase 3 (optimized versions) for future performance work

---

**Analysis Status:** COMPLETE
**Recommendation:** PROCEED with Phase 1 & 2 (low risk, high value)
**Risk Level:** LOW (no active code depends on moved files)
**Time Required:** 1.5 hours
**Reversibility:** HIGH (easy to rollback if needed)

---

**Key Insight:** The optimized versions exist but are NOT used. This is good design - keep original for reproducibility, have optimized ready for future performance work. Document which is which, move legacy code to appropriate location, done.
