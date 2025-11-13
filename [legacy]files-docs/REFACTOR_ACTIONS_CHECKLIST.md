# REFACTOR ACTIONS CHECKLIST
**Date:** October 28, 2025
**Status:** Ready to execute
**Full Analysis:** See `REFACTOR_LOG_REDUNDANCIES.md`

---

## QUICK SUMMARY

**Total Redundant Files:** 9
**Safe to Move:** 7 files
**Keep Both:** 2 pairs (document which is active)
**Estimated Time:** 1.5 hours

---

## PHASE 1: DOCUMENTATION (30 min) ✓ DO THIS FIRST

### Create README Files

```bash
cd /home/kawaiikali/Resurrexi/projects/planned-publish/event-study

# 1. Document TARCH implementations
cat > code/core/README_TARCH_IMPLEMENTATION.md << 'EOFDOC'
# TARCH-X Implementation Versions

## Active Version (DO NOT MODIFY)
- **File:** `tarch_x_manual.py`
- **Status:** Used in published research (Zenodo DOI: 10.5281/zenodo.17449736)
- **Imports:** `core/garch_models.py`, `scripts/run_smoke_tests.py`

## Experimental Version  
- **File:** `tarch_x_manual_optimized.py`
- **Status:** Performance-optimized (5-10x speedup), NOT currently used
- **Purpose:** Future performance work

## Which Should I Import?
- For reproducible research: `from tarch_x_manual import estimate_tarch_x_manual`
- For performance testing: `from tarch_x_manual_optimized import estimate_tarch_x_manual`
EOFDOC

# 2. Document bootstrap implementations
cat > code/inference/README_BOOTSTRAP.md << 'EOFDOC'
# Bootstrap Inference Implementations

## Active Version (DO NOT MODIFY)
- **File:** `bootstrap_inference.py`
- **Status:** Used in published robustness checks
- **Imports:** `scripts/run_event_study_analysis.py`, `analysis/hypothesis_testing_results.py`

## Experimental Version
- **File:** `bootstrap_inference_optimized.py`
- **Status:** Parallelized (5-10x speedup), NOT currently used
- **Purpose:** Future large-scale simulations

## Performance
- Original: ~30-60 minutes for 500 replications × 6 cryptos
- Optimized: ~5-10 minutes (parallelized with joblib)
EOFDOC

# 3. Document legacy templates
cat > code/legacy/README_TEMPLATES.md << 'EOFDOC'
# Legacy Template Files

**Status:** NOT part of active analysis pipeline
**Purpose:** Historical reference for development process

## Files
- `data_preparation_template.py` - Data preparation template (superseded)
- `extract_volatility_template.py` - Volatility extraction template (superseded)

## Active Versions
Use `code/core/data_preparation.py` instead.
EOFDOC

# 4. Document one-time scripts
cat > code/legacy/README_ONE_TIME_SCRIPTS.md << 'EOFDOC'
# Legacy One-Time Scripts

**Status:** Completed and archived
**Purpose:** Historical reference for development decisions

## Files
- `extract_volatility.py` - Old extraction logic (superseded by core/data_preparation.py)
- `fix_correlation_matrix.py` - One-time correlation matrix fix (applied)
- `validate_fixes.py` - One-time validation (complete)
- `temporal_stability_analysis.py` - Analysis script (results hardcoded in figure script)

## Do NOT Use
These scripts are not part of the active analysis pipeline.
EOFDOC

echo "✓ Documentation files created"
```

---

## PHASE 2: MOVE NON-CRITICAL FILES (1 hour) ✓ DO THIS SECOND

### Move Files to Appropriate Locations

```bash
cd /home/kawaiikali/Resurrexi/projects/planned-publish/event-study

# 1. Move integration guide to docs
mv code/core/tarch_x_integration.py docs/

# 2. Move templates to legacy
mv code/data_preparation_template.py code/legacy/
mv code/extract_volatility_template.py code/legacy/

# 3. Move one-time scripts to legacy
mv code/extract_volatility.py code/legacy/
mv code/fix_correlation_matrix.py code/legacy/
mv code/validate_fixes.py code/legacy/
mv code/temporal_stability_analysis.py code/legacy/

echo "✓ Files moved to legacy/"
```

---

## PHASE 3: VERIFY NO BREAKAGE (15 min) ✓ DO THIS THIRD

### Test Critical Imports

```bash
cd /home/kawaiikali/Resurrexi/projects/planned-publish/event-study

# Test Python imports
python3 << 'PYEOF'
import sys
sys.path.append('code')

print("Testing critical imports...")

# Test TARCH-X import
from core.garch_models import GARCHModels
print("✓ GARCHModels imports successfully")

# Test bootstrap import  
from inference.bootstrap_inference import BootstrapInference
print("✓ BootstrapInference imports successfully")

# Test data preparation
from core.data_preparation import DataPreparation
print("✓ DataPreparation imports successfully")

# Test event analysis
from analysis.event_impact_analysis import EventImpactAnalysis
print("✓ EventImpactAnalysis imports successfully")

print("\n✓ ALL CRITICAL IMPORTS WORK")
PYEOF

# Run smoke tests if available
if [ -f "code/scripts/run_smoke_tests.py" ]; then
    echo "Running smoke tests..."
    python3 code/scripts/run_smoke_tests.py
fi

# Run unit tests
if [ -d "tests" ]; then
    echo "Running unit tests..."
    pytest tests/ -v --tb=short
fi

echo "✓ Verification complete"
```

---

## PHASE 4: UPDATE DOCUMENTATION (15 min) ✓ DO THIS LAST

### Update Master Reference

```bash
cd /home/kawaiikali/Resurrexi/projects/planned-publish/event-study

# Update MASTER_REFACTOR_REFERENCE.md redundancy table
# Mark actions as COMPLETED in the redundancies section

echo "✓ Update MASTER_REFACTOR_REFERENCE.md redundancy section"
echo "✓ Mark moved files as 'RESOLVED - Moved to legacy/ on Oct 28, 2025'"
```

---

## FILES MOVED SUMMARY

### To `code/legacy/` (6 files)
- [x] `data_preparation_template.py`
- [x] `extract_volatility_template.py`
- [x] `extract_volatility.py`
- [x] `fix_correlation_matrix.py`
- [x] `validate_fixes.py`
- [x] `temporal_stability_analysis.py`

### To `docs/` (1 file)
- [x] `tarch_x_integration.py` (documentation only)

### Kept with Documentation (4 files)
- [x] `core/tarch_x_manual.py` (ACTIVE)
- [x] `core/tarch_x_manual_optimized.py` (EXPERIMENTAL)
- [x] `inference/bootstrap_inference.py` (ACTIVE)
- [x] `inference/bootstrap_inference_optimized.py` (EXPERIMENTAL)

---

## CRITICAL: DO NOT REMOVE

### These Files Are Imported by Active Code

**TARCH-X Original:**
- `core/garch_models.py:33` → `from tarch_x_manual import estimate_tarch_x_manual`
- `scripts/run_smoke_tests.py` → `from tarch_x_manual import TARCHXEstimator`

**Bootstrap Original:**
- `scripts/run_event_study_analysis.py:22` → `from bootstrap_inference import run_bootstrap_analysis`
- `analysis/hypothesis_testing_results.py:26` → `from bootstrap_inference import BootstrapInference`
- `robustness/robustness_checks.py:745` → `from bootstrap_inference import run_bootstrap_analysis`

**Removing these will BREAK the entire analysis pipeline!**

---

## VERIFICATION CHECKLIST

After completing all phases:

- [ ] All critical imports work (`python -c "import sys; sys.path.append('code'); from core.garch_models import GARCHModels; print('OK')"`)
- [ ] Smoke tests pass (if available)
- [ ] Unit tests pass (`pytest tests/`)
- [ ] No broken imports in analysis pipeline
- [ ] README files created in `core/`, `inference/`, `legacy/`
- [ ] Integration guide moved to `docs/`
- [ ] MASTER_REFACTOR_REFERENCE.md updated

---

## ROLLBACK PLAN (If Something Breaks)

```bash
# If verification fails, restore files from git:
git checkout code/data_preparation_template.py
git checkout code/extract_volatility_template.py
git checkout code/extract_volatility.py
git checkout code/fix_correlation_matrix.py
git checkout code/validate_fixes.py
git checkout code/temporal_stability_analysis.py
git checkout code/core/tarch_x_integration.py

# Or restore from backup if not in git
```

---

## ESTIMATED TIMELINE

- **Phase 1 (Documentation):** 30 minutes
- **Phase 2 (Move files):** 15 minutes
- **Phase 3 (Verification):** 15 minutes
- **Phase 4 (Update docs):** 15 minutes

**Total:** ~1.5 hours

---

## NOTES

- The optimized versions (`*_optimized.py`) are NOT used by the current pipeline
- All moved files have NO active imports (verified with grep)
- The original versions are used in published research (DOI: 10.5281/zenodo.17449736)
- Keep optimized versions for future performance work, but document clearly

---

**Status:** Ready to execute
**Risk:** LOW (no active code depends on moved files)
**Next:** Review with user, then execute Phase 1-4
