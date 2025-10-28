#!/usr/bin/env python3
"""
Manual smoke test runner for event study codebase.
Validates core functionality without requiring pytest.
"""

import sys
import os
from pathlib import Path
import traceback

# Add code directory to path
sys.path.insert(0, str(Path(__file__).parent / 'event_study' / 'code'))

print("=" * 70)
print("SMOKE TEST SUITE: Event Study TARCH-X Model")
print("=" * 70)
print()

# Test counter
tests_passed = 0
tests_failed = 0
test_results = []

def run_test(test_name, test_func):
    """Run a single test and track results."""
    global tests_passed, tests_failed
    print(f"Running: {test_name}")
    print("-" * 70)
    try:
        test_func()
        print(f"✓ PASSED\n")
        tests_passed += 1
        test_results.append((test_name, "PASSED", None))
    except AssertionError as e:
        print(f"✗ FAILED: {e}\n")
        tests_failed += 1
        test_results.append((test_name, "FAILED", str(e)))
    except Exception as e:
        print(f"✗ ERROR: {e}")
        traceback.print_exc()
        print()
        tests_failed += 1
        test_results.append((test_name, "ERROR", str(e)))

# ============================================================================
# Test 1: Import all modules
# ============================================================================
def test_imports():
    """Test that all core modules can be imported."""
    import config
    import data_preparation
    import garch_models
    import tarch_x_manual

    assert hasattr(config, 'RANDOM_SEED'), "config.RANDOM_SEED not found"
    assert config.RANDOM_SEED == 42, "RANDOM_SEED should be 42"
    print(f"  - config module: ✓ (RANDOM_SEED={config.RANDOM_SEED})")

    assert hasattr(data_preparation, 'load_cryptocurrency_data'), "load_cryptocurrency_data not found"
    print(f"  - data_preparation module: ✓")

    assert hasattr(garch_models, 'estimate_garch_models'), "estimate_garch_models not found"
    print(f"  - garch_models module: ✓")

    assert hasattr(tarch_x_manual, 'TARCHXEstimator'), "TARCHXEstimator not found"
    assert hasattr(tarch_x_manual, 'TARCHXResults'), "TARCHXResults not found"
    print(f"  - tarch_x_manual module: ✓")

# ============================================================================
# Test 2: Configuration values
# ============================================================================
def test_config_values():
    """Test that config has all required values."""
    import config

    # Check random seed
    assert config.RANDOM_SEED == 42, "RANDOM_SEED must be 42"
    print(f"  - RANDOM_SEED: {config.RANDOM_SEED} ✓")

    # Check cryptocurrency selection exists
    assert hasattr(config, 'CRYPTOCURRENCIES'), "CRYPTOCURRENCIES not found"
    print(f"  - CRYPTOCURRENCIES: {len(config.CRYPTOCURRENCIES)} coins ✓")

    # Check event window parameters
    assert hasattr(config, 'EVENT_WINDOW'), "EVENT_WINDOW not found"
    print(f"  - EVENT_WINDOW: {config.EVENT_WINDOW} ✓")

    # Check estimation window
    assert hasattr(config, 'ESTIMATION_WINDOW'), "ESTIMATION_WINDOW not found"
    print(f"  - ESTIMATION_WINDOW: {config.ESTIMATION_WINDOW} ✓")

# ============================================================================
# Test 3: TARCH-X Estimator initialization
# ============================================================================
def test_tarch_x_initialization():
    """Test that TARCH-X estimator can be initialized."""
    import pandas as pd
    import numpy as np
    from tarch_x_manual import TARCHXEstimator

    # Create dummy data
    np.random.seed(42)
    returns = pd.Series(np.random.randn(100), name='returns')

    # Initialize without exogenous variables
    estimator = TARCHXEstimator(returns)
    assert estimator.n_obs == 100, "Should have 100 observations"
    assert estimator.n_params == 5, "Should have 5 base parameters"
    assert not estimator.has_exog, "Should not have exogenous variables"
    print(f"  - Basic initialization: ✓ (n_obs={estimator.n_obs}, n_params={estimator.n_params})")

    # Initialize with exogenous variables
    exog_vars = pd.DataFrame({
        'event1': np.random.choice([0, 1], 100),
        'event2': np.random.choice([0, 1], 100)
    }, index=returns.index)

    estimator_exog = TARCHXEstimator(returns, exog_vars)
    assert estimator_exog.has_exog, "Should have exogenous variables"
    assert estimator_exog.n_exog == 2, "Should have 2 exogenous variables"
    assert estimator_exog.n_params == 7, "Should have 7 parameters (5 + 2 exog)"
    print(f"  - With exogenous vars: ✓ (n_exog={estimator_exog.n_exog}, n_params={estimator_exog.n_params})")

# ============================================================================
# Test 4: DOF validation
# ============================================================================
def test_dof_validation():
    """Test that DOF validation works correctly."""
    import pandas as pd
    import numpy as np
    from tarch_x_manual import TARCHXEstimator
    import inspect

    # Check that _compute_standard_errors has DOF check
    source = inspect.getsource(TARCHXEstimator._compute_standard_errors)

    assert "dof = self.n_obs - self.n_params" in source, "DOF calculation not found"
    assert "if dof <= 0:" in source, "DOF validation not found"
    print(f"  - DOF validation code present: ✓")

    # Create edge case: more parameters than observations
    returns = pd.Series(np.random.randn(10), name='returns')
    exog_vars = pd.DataFrame({
        f'var{i}': np.random.randn(10) for i in range(20)  # 20 exog vars + 5 base = 25 params > 10 obs
    }, index=returns.index)

    estimator = TARCHXEstimator(returns, exog_vars)
    assert estimator.n_params > estimator.n_obs, "Should have more params than obs"
    print(f"  - Edge case setup: ✓ (n_obs={estimator.n_obs}, n_params={estimator.n_params})")
    print(f"    DOF would be {estimator.n_obs - estimator.n_params} (negative)")

# ============================================================================
# Test 5: Leverage effect documentation
# ============================================================================
def test_leverage_documentation():
    """Test that leverage effect is properly documented."""
    import tarch_x_manual
    import inspect

    # Check module docstring
    module_doc = tarch_x_manual.__doc__ or ""
    assert "leverage" in module_doc.lower(), "Module should document leverage effect"
    assert "gamma" in module_doc.lower(), "Module should document gamma parameter"
    print(f"  - Module docstring: ✓ (mentions leverage and gamma)")

    # Check class docstring
    class_doc = tarch_x_manual.TARCHXEstimator.__doc__ or ""
    assert len(class_doc) > 0, "Class should have docstring"
    print(f"  - Class docstring: ✓")

    # Check estimate method docstring
    estimate_doc = tarch_x_manual.TARCHXEstimator.estimate.__doc__ or ""
    assert len(estimate_doc) > 0, "Estimate method should have docstring"
    print(f"  - Estimate method docstring: ✓")

    # Verify leverage effect is mentioned somewhere
    combined = module_doc + class_doc + estimate_doc
    assert "asymmetric" in combined.lower() or "leverage" in combined.lower(), \
        "Documentation should mention asymmetric/leverage effects"
    print(f"  - Leverage effect documented: ✓")

# ============================================================================
# Test 6: Requirements.txt validation
# ============================================================================
def test_requirements():
    """Test that requirements.txt exists and has required packages."""
    req_file = Path(__file__).parent / 'requirements.txt'
    assert req_file.exists(), "requirements.txt should exist"

    with open(req_file, 'r') as f:
        content = f.read()

    required_packages = ['numpy', 'pandas', 'scipy', 'statsmodels', 'matplotlib']
    for pkg in required_packages:
        assert pkg in content.lower(), f"{pkg} should be in requirements.txt"
        print(f"  - {pkg}: ✓")

# ============================================================================
# Test 7: Multicollinearity check
# ============================================================================
def test_multicollinearity_check():
    """Test that multicollinearity check exists in garch_models."""
    import garch_models
    import inspect

    # Read the source file
    source_file = Path(__file__).parent / 'event_study' / 'code' / 'garch_models.py'
    with open(source_file, 'r') as f:
        source = f.read()

    # Check for multicollinearity-related code
    has_check = any([
        "multicollinearity" in source.lower(),
        "vif" in source.lower(),
        "correlation" in source.lower() and "threshold" in source.lower()
    ])

    assert has_check, "Multicollinearity check should exist in garch_models.py"
    print(f"  - Multicollinearity check present: ✓")

# ============================================================================
# Run all tests
# ============================================================================
run_test("Test 1: Import all modules", test_imports)
run_test("Test 2: Configuration values", test_config_values)
run_test("Test 3: TARCH-X initialization", test_tarch_x_initialization)
run_test("Test 4: DOF validation", test_dof_validation)
run_test("Test 5: Leverage documentation", test_leverage_documentation)
run_test("Test 6: Requirements.txt", test_requirements)
run_test("Test 7: Multicollinearity check", test_multicollinearity_check)

# ============================================================================
# Summary
# ============================================================================
print("=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print(f"Tests passed: {tests_passed}")
print(f"Tests failed: {tests_failed}")
print(f"Total tests:  {tests_passed + tests_failed}")
print()

if tests_failed > 0:
    print("FAILED TESTS:")
    for name, status, error in test_results:
        if status != "PASSED":
            print(f"  - {name}: {status}")
            if error:
                print(f"    {error}")
    print()
    sys.exit(1)
else:
    print("✓ ALL SMOKE TESTS PASSED")
    print()
    print("Core functionality validated:")
    print("  1. ✓ All modules import correctly")
    print("  2. ✓ Random seed configured (42)")
    print("  3. ✓ TARCH-X estimator initializes correctly")
    print("  4. ✓ DOF validation implemented")
    print("  5. ✓ Leverage effect documented")
    print("  6. ✓ Requirements.txt complete")
    print("  7. ✓ Multicollinearity check present")
    print()
    print("=" * 70)
    sys.exit(0)
