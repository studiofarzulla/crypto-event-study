# Event Study Test Suite

Comprehensive test suite for cryptocurrency event study providing journal-level reproducibility standards.

## Overview

This test suite provides complete coverage of:
- **Data Validation**: Loading, quality checks, event classification
- **GARCH Models**: Estimation, convergence, parameter validation
- **Statistical Methods**: Hypothesis testing, FDR correction, bootstrap inference
- **Integration**: Full pipeline, reproducibility verification
- **Edge Cases**: Missing data, non-convergence, extreme values

## Test Structure

```
tests/
├── conftest.py                      # Shared fixtures and configuration
├── test_data_validation.py          # Data loading and quality tests
├── test_garch_models.py             # GARCH/TARCH/TARCH-X estimation tests
├── test_statistical_methods.py      # Hypothesis testing and inference
├── test_integration.py              # End-to-end pipeline tests
├── test_edge_cases.py               # Edge cases and error handling
├── test_data_preparation_original.py # Original comprehensive tests
└── test_tarch_x_integration.py      # TARCH-X specific integration
```

## Quick Start

### Install Dependencies

```bash
# Install pytest and coverage tools
pip install pytest pytest-cov pytest-xdist

# Install test dependencies
pip install psutil tqdm
```

### Run All Tests

```bash
# From project root
pytest

# With verbose output
pytest -v

# With coverage report
pytest --cov=event_study/code --cov-report=html
```

### Run Specific Test Categories

```bash
# Data validation only
pytest -m data_validation

# Statistical tests only
pytest -m statistical

# Integration tests
pytest -m integration

# Unit tests only
pytest -m unit

# Edge case tests
pytest -m edge_case

# Reproducibility tests
pytest -m reproducibility
```

### Run Specific Test Files

```bash
# Data validation tests
pytest tests/test_data_validation.py

# GARCH model tests
pytest tests/test_garch_models.py

# Statistical methods
pytest tests/test_statistical_methods.py

# Integration tests
pytest tests/test_integration.py

# Edge cases
pytest tests/test_edge_cases.py
```

### Skip Slow Tests

```bash
# Skip slow tests (for quick validation)
pytest -m "not slow"

# Run only slow tests (for comprehensive validation)
pytest -m slow
```

## Test Markers

Tests are organized with markers for easy filtering:

- `unit`: Unit tests for individual functions
- `integration`: Integration tests for multiple components
- `statistical`: Statistical tests for model validation
- `edge_case`: Edge case and error handling tests
- `slow`: Tests that take significant time to run (>5 seconds)
- `reproducibility`: Tests verifying reproducibility of results
- `data_validation`: Tests for data quality and validation

## Parallel Execution

Speed up test execution with parallel processing:

```bash
# Run with 4 workers
pytest -n 4

# Run with auto-detect CPU count
pytest -n auto
```

## Coverage Requirements

For journal publication, aim for **80%+ code coverage**:

```bash
# Generate coverage report
pytest --cov=event_study/code --cov-report=term-missing --cov-report=html

# View HTML report
open htmlcov/index.html
```

## Test Data

Tests use a combination of:
- **Real cryptocurrency data**: From `data/` directory (BTC, ETH, XRP, etc.)
- **Mock data**: Generated synthetic data for controlled testing
- **Fixtures**: Shared test data defined in `conftest.py`

### Required Data Files

Ensure these files exist in `data/` directory:
- `btc.csv`, `eth.csv`, `xrp.csv`, `bnb.csv`, `ltc.csv`, `ada.csv`
- `events.csv` (event classification)
- `gdelt.csv` (sentiment data)

## Continuous Integration

Example GitHub Actions configuration:

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-xdist
      - name: Run tests
        run: pytest --cov=event_study/code --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Debugging Failed Tests

### Verbose Output

```bash
# Show full output for failed tests
pytest -vv

# Show local variables on failure
pytest -l

# Drop into debugger on first failure
pytest --pdb

# Drop into debugger on all failures
pytest --pdb -x
```

### Specific Test Function

```bash
# Run single test function
pytest tests/test_data_validation.py::TestDataLoading::test_load_crypto_prices_btc

# Run all tests in a class
pytest tests/test_garch_models.py::TestGARCH11Estimation
```

### Test Output

```bash
# Show print statements
pytest -s

# Show warnings
pytest -v --tb=short

# Minimal output
pytest -q
```

## Reproducibility Testing

Critical for academic publication:

```bash
# Run reproducibility tests specifically
pytest -m reproducibility -v

# Test with multiple random seeds
for seed in 42 123 456; do
    echo "Testing with seed $seed"
    PYTEST_RANDOM_SEED=$seed pytest -m reproducibility
done
```

## Performance Benchmarking

```bash
# Show 10 slowest tests
pytest --durations=10

# Show all test durations
pytest --durations=0

# Profile memory usage
pytest --memprof
```

## Expected Test Results

For a healthy codebase:

- **All tests pass**: ✓ 100+ tests
- **Code coverage**: ≥ 80%
- **No critical warnings**: Deprecation warnings OK
- **Reproducibility**: All reproducibility tests pass
- **Performance**: Most tests < 1 second, full suite < 5 minutes

## Troubleshooting

### Common Issues

**Import Errors**:
```bash
# Ensure code directory is in path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/event_study/code"
pytest
```

**Missing Data**:
```bash
# Tests will skip if data files missing
pytest -v  # Shows skipped tests
```

**Convergence Failures**:
- Some GARCH models may not converge on synthetic data
- Tests are designed to handle non-convergence gracefully
- Real data tests should converge

**Memory Issues**:
```bash
# Run tests sequentially if parallel fails
pytest -n 1

# Skip slow/memory-intensive tests
pytest -m "not slow"
```

## Test Development

### Adding New Tests

1. Create test file: `test_<module_name>.py`
2. Import from `conftest.py` for fixtures
3. Use descriptive test names: `test_<what>_<condition>`
4. Add appropriate markers
5. Document test purpose in docstring

Example:

```python
import pytest

@pytest.mark.unit
def test_calculate_returns_accuracy(data_prep, sample_prices):
    """Test log returns calculation produces accurate results."""
    returns = data_prep.calculate_log_returns(sample_prices)

    # Manual calculation for verification
    expected = np.log(sample_prices.iloc[1] / sample_prices.iloc[0]) * 100

    assert abs(returns.iloc[0] - expected) < 1e-10
```

### Test Fixtures

Shared fixtures in `conftest.py`:
- `data_prep`: DataPreparation instance
- `sample_returns`: Synthetic return series
- `sample_prices`: Synthetic price series
- `btc_data_sample`: Real BTC data
- `events_df`: Event classification data
- `sentiment_df`: Sentiment time series
- `assert_valid_garch_params`: Parameter validation helper
- `assert_reproducible`: Reproducibility checker

## Code Quality Checks

```bash
# Run linting
flake8 event_study/code

# Type checking
mypy event_study/code

# Style checking
black --check event_study/code

# Combined quality check
pytest && flake8 && mypy && black --check .
```

## Documentation

For detailed information on specific test modules:

- **Data Validation**: See `test_data_validation.py` docstrings
- **GARCH Models**: See `test_garch_models.py` docstrings
- **Statistical Methods**: See `test_statistical_methods.py` docstrings
- **Integration**: See `test_integration.py` docstrings
- **Edge Cases**: See `test_edge_cases.py` docstrings

## Support

For issues or questions about tests:

1. Check test docstrings for detailed explanations
2. Review `conftest.py` for available fixtures
3. Examine similar existing tests
4. Run with `-vv` for detailed output
5. Use `--pdb` to debug interactively

## Academic Publication Checklist

Before submission, ensure:

- [ ] All tests pass
- [ ] Code coverage ≥ 80%
- [ ] Reproducibility tests pass
- [ ] Integration tests pass
- [ ] No critical warnings
- [ ] Tests run on clean environment
- [ ] Results match paper figures/tables
- [ ] Random seeds documented
- [ ] Test data sources documented

## License

Tests are part of the cryptocurrency event study codebase.
See main project LICENSE for details.
