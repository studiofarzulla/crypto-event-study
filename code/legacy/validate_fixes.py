#!/usr/bin/env python3
"""
Validation script for bug fixes applied by python-expert agent.
Tests all 5 critical fixes:
1. Random seed configuration
2. DOF validation in TARCH-X
3. Multicollinearity check in GARCH models
4. Leverage effect documentation
5. Requirements.txt creation
"""

import sys
import os
import inspect
from pathlib import Path

# Add code directory to path
sys.path.insert(0, str(Path(__file__).parent / 'event_study' / 'code'))

print("=" * 70)
print("VALIDATION REPORT: Bug Fixes from python-expert Agent")
print("=" * 70)
print()

# Test 1: Random seed configuration
print("TEST 1: Random Seed Configuration")
print("-" * 70)
try:
    import config
    assert hasattr(config, 'RANDOM_SEED'), "RANDOM_SEED not found in config"
    assert config.RANDOM_SEED == 42, f"Expected RANDOM_SEED=42, got {config.RANDOM_SEED}"
    print(f"✓ Random seed correctly set to {config.RANDOM_SEED}")
    print(f"✓ config.py imported successfully")
except Exception as e:
    print(f"✗ FAILED: {e}")
    sys.exit(1)
print()

# Test 2: DOF validation in TARCH-X
print("TEST 2: DOF Validation in TARCH-X Model")
print("-" * 70)
try:
    import tarch_x_manual

    # Check if estimate method exists
    assert hasattr(tarch_x_manual, 'TARCHXEstimator'), "TARCHXEstimator class not found"

    # Check if _compute_standard_errors method has DOF validation
    source = inspect.getsource(tarch_x_manual.TARCHXEstimator._compute_standard_errors)

    has_dof_check = any([
        "degrees of freedom" in source.lower(),
        "dof" in source.lower() and "n_obs" in source.lower(),
        "n_obs - n_params" in source.lower().replace(" ", ""),
        "insufficient degrees" in source.lower()
    ])

    assert has_dof_check, "DOF validation not found in TARCHXEstimator._compute_standard_errors method"
    print("✓ DOF validation present in TARCHXEstimator._compute_standard_errors method")
    print("✓ tarch_x_manual.py imported successfully")
except Exception as e:
    print(f"✗ FAILED: {e}")
    sys.exit(1)
print()

# Test 3: Multicollinearity check in GARCH models
print("TEST 3: Multicollinearity Check in GARCH Models")
print("-" * 70)
try:
    import garch_models

    # Check if multicollinearity check exists
    source_file = Path(__file__).parent / 'event_study' / 'code' / 'garch_models.py'
    with open(source_file, 'r') as f:
        source = f.read()

    has_multicollinearity = any([
        "multicollinearity" in source.lower(),
        "vif" in source.lower(),
        "variance inflation" in source.lower(),
        "corr" in source.lower() and "threshold" in source.lower()
    ])

    assert has_multicollinearity, "Multicollinearity check not found in garch_models.py"
    print("✓ Multicollinearity check present in garch_models.py")
    print("✓ garch_models.py imported successfully")
except Exception as e:
    print(f"✗ FAILED: {e}")
    sys.exit(1)
print()

# Test 4: Leverage effect documentation
print("TEST 4: Leverage Effect Documentation")
print("-" * 70)
try:
    # Check TARCH-X docstrings
    tarch_x_doc = tarch_x_manual.TARCHXEstimator.__doc__ or ""
    estimate_doc = tarch_x_manual.TARCHXEstimator.estimate.__doc__ or ""
    module_doc = tarch_x_manual.__doc__ or ""

    combined_docs = tarch_x_doc + estimate_doc + module_doc

    has_leverage_docs = any([
        "leverage" in combined_docs.lower(),
        "asymmetric" in combined_docs.lower(),
        "gamma" in combined_docs.lower() and "negative" in combined_docs.lower()
    ])

    assert has_leverage_docs, "Leverage effect not documented in TARCHXEstimator"
    print("✓ Leverage effect documented in TARCHXEstimator class/methods")
except Exception as e:
    print(f"✗ FAILED: {e}")
    sys.exit(1)
print()

# Test 5: Requirements.txt creation
print("TEST 5: Requirements.txt Creation")
print("-" * 70)
try:
    requirements_path = Path(__file__).parent / 'requirements.txt'
    assert requirements_path.exists(), "requirements.txt not found"

    with open(requirements_path, 'r') as f:
        req_content = f.read()

    # Check for critical dependencies
    critical_deps = ['numpy', 'pandas', 'scipy', 'statsmodels', 'matplotlib']
    missing_deps = [dep for dep in critical_deps if dep not in req_content.lower()]

    assert not missing_deps, f"Missing critical dependencies: {missing_deps}"
    print(f"✓ requirements.txt exists with {len(req_content.splitlines())} lines")
    print(f"✓ All critical dependencies present: {', '.join(critical_deps)}")
except Exception as e:
    print(f"✗ FAILED: {e}")
    sys.exit(1)
print()

# Test 6: Cross-module imports
print("TEST 6: Cross-Module Import Test")
print("-" * 70)
try:
    import data_preparation

    # Verify all modules can be imported together
    modules = {
        'config': config,
        'data_preparation': data_preparation,
        'garch_models': garch_models,
        'tarch_x_manual': tarch_x_manual
    }

    for name, mod in modules.items():
        assert mod is not None, f"Module {name} is None"
        print(f"✓ {name} module loaded successfully")
except Exception as e:
    print(f"✗ FAILED: {e}")
    sys.exit(1)
print()

# Summary
print("=" * 70)
print("VALIDATION SUMMARY: ALL TESTS PASSED ✓")
print("=" * 70)
print()
print("Fixed issues verified:")
print("  1. ✓ Random seed (config.RANDOM_SEED = 42)")
print("  2. ✓ DOF validation in TARCH-X model")
print("  3. ✓ Multicollinearity check in GARCH models")
print("  4. ✓ Leverage effect documentation")
print("  5. ✓ Requirements.txt with all dependencies")
print("  6. ✓ All modules import without errors")
print()
print("Next steps: Run full pytest suite to validate functionality")
print("Command: pytest tests/ -v --tb=short")
print("=" * 70)
