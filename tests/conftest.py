"""
Pytest fixtures and configuration for event study tests.
Provides shared test data, mock objects, and utilities.
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from datetime import datetime, timedelta
import warnings

# Add code directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from code.core.data_preparation import DataPreparation
from code.core.garch_models import GARCHModels
from code.core import config


# ==============================================================================
# Session-level fixtures (created once per test session)
# ==============================================================================

@pytest.fixture(scope="session")
def data_dir():
    """Path to data directory."""
    return Path(__file__).parent.parent / "data"


@pytest.fixture(scope="session")
def output_dir(tmp_path_factory):
    """Temporary output directory for test results."""
    return tmp_path_factory.mktemp("test_outputs")


# ==============================================================================
# Module-level fixtures (created once per test module)
# ==============================================================================

@pytest.fixture(scope="module")
def data_prep(data_dir):
    """Create DataPreparation instance with actual data."""
    return DataPreparation(data_path=str(data_dir))


@pytest.fixture(scope="module")
def events_df(data_prep):
    """Load actual events data."""
    return data_prep.load_events()


@pytest.fixture(scope="module")
def sentiment_df(data_prep):
    """Load actual sentiment data."""
    return data_prep.load_gdelt_sentiment()


# ==============================================================================
# Function-level fixtures (created for each test function)
# ==============================================================================

@pytest.fixture
def sample_returns():
    """Generate realistic sample return series for testing."""
    np.random.seed(42)
    dates = pd.date_range(start='2019-01-01', end='2021-12-31', freq='D', tz='UTC')

    # Generate returns with GARCH-like properties
    n = len(dates)
    returns = np.zeros(n)
    volatility = np.zeros(n)

    # GARCH(1,1) parameters
    omega = 0.01
    alpha = 0.10
    beta = 0.85

    # Initial volatility
    volatility[0] = np.sqrt(omega / (1 - alpha - beta))

    for t in range(1, n):
        # GARCH recursion
        volatility[t] = np.sqrt(omega + alpha * returns[t-1]**2 + beta * volatility[t-1]**2)
        # Generate returns
        returns[t] = volatility[t] * np.random.standard_t(df=6)

    return pd.Series(returns * 100, index=dates, name='returns')  # Scale to percentage


@pytest.fixture
def sample_prices():
    """Generate realistic sample price series."""
    np.random.seed(42)
    dates = pd.date_range(start='2019-01-01', end='2021-12-31', freq='D', tz='UTC')

    # Generate log prices with random walk + drift
    n = len(dates)
    log_prices = np.zeros(n)
    log_prices[0] = np.log(10000)  # Start at 10,000

    for t in range(1, n):
        # Random walk with small drift
        log_prices[t] = log_prices[t-1] + np.random.normal(0.0002, 0.02)

    prices = np.exp(log_prices)
    return pd.Series(prices, index=dates, name='price')


@pytest.fixture
def sample_event_dummies():
    """Generate sample event dummy variables."""
    dates = pd.date_range(start='2019-01-01', end='2021-12-31', freq='D', tz='UTC')

    dummies = pd.DataFrame(index=dates)

    # Create infrastructure event (simulated exchange hack)
    infra_date = pd.Timestamp('2020-06-15', tz='UTC')
    dummies['D_infrastructure'] = 0
    for i in range(-3, 4):  # 7-day window
        date = infra_date + timedelta(days=i)
        if date in dummies.index:
            dummies.loc[date, 'D_infrastructure'] = 1

    # Create regulatory event (simulated regulation announcement)
    reg_date = pd.Timestamp('2020-09-20', tz='UTC')
    dummies['D_regulatory'] = 0
    for i in range(-3, 4):
        date = reg_date + timedelta(days=i)
        if date in dummies.index:
            dummies.loc[date, 'D_regulatory'] = 1

    return dummies


@pytest.fixture
def sample_prepared_data(sample_returns, sample_event_dummies):
    """Create a complete prepared dataset for testing."""
    # Combine returns and event dummies
    data = pd.DataFrame({'returns_winsorized': sample_returns})
    data = data.merge(sample_event_dummies, left_index=True, right_index=True, how='left')
    data[['D_infrastructure', 'D_regulatory']] = data[['D_infrastructure', 'D_regulatory']].fillna(0)

    # Add sentiment variables (simulated)
    data['S_gdelt_normalized'] = np.random.normal(0, 1, len(data))
    data['S_reg_decomposed'] = data['S_gdelt_normalized'] * 0.3
    data['S_infra_decomposed'] = data['S_gdelt_normalized'] * 0.7

    return data


@pytest.fixture
def btc_data_sample(data_prep):
    """Load a sample of actual BTC data for integration tests."""
    try:
        return data_prep.prepare_crypto_data('btc', include_events=True, include_sentiment=True)
    except Exception as e:
        pytest.skip(f"Could not load BTC data: {e}")


# ==============================================================================
# Utility fixtures
# ==============================================================================

@pytest.fixture
def suppress_warnings():
    """Suppress warnings during tests."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        yield


@pytest.fixture
def random_seed():
    """Set random seed for reproducibility."""
    np.random.seed(42)
    yield
    np.random.seed(None)  # Reset


# ==============================================================================
# Parametrization helpers
# ==============================================================================

@pytest.fixture(params=['btc', 'eth', 'xrp'])
def crypto_symbol(request):
    """Parametrize over multiple cryptocurrencies."""
    return request.param


@pytest.fixture(params=['GARCH(1,1)', 'TARCH(1,1)', 'TARCH-X'])
def model_type(request):
    """Parametrize over model types."""
    return request.param


# ==============================================================================
# Mock fixtures for edge case testing
# ==============================================================================

@pytest.fixture
def data_with_missing():
    """Create data with missing values."""
    dates = pd.date_range(start='2019-01-01', end='2019-12-31', freq='D', tz='UTC')
    data = pd.DataFrame({
        'price': np.random.lognormal(8, 0.02, len(dates)),
        'returns': np.random.normal(0, 2, len(dates))
    }, index=dates)

    # Introduce missing values
    missing_indices = np.random.choice(len(data), size=10, replace=False)
    data.iloc[missing_indices, :] = np.nan

    return data


@pytest.fixture
def data_with_outliers():
    """Create data with extreme outliers."""
    dates = pd.date_range(start='2019-01-01', end='2019-12-31', freq='D', tz='UTC')
    returns = np.random.normal(0, 2, len(dates))

    # Add extreme outliers
    returns[100] = 50   # Extreme positive
    returns[200] = -50  # Extreme negative
    returns[300] = 100  # Very extreme

    return pd.Series(returns, index=dates, name='returns')


@pytest.fixture
def data_with_zero_variance():
    """Create data with zero or near-zero variance periods."""
    dates = pd.date_range(start='2019-01-01', end='2019-12-31', freq='D', tz='UTC')
    returns = np.random.normal(0, 2, len(dates))

    # Create zero variance period
    returns[50:100] = 0.0001  # Nearly constant

    return pd.Series(returns, index=dates, name='returns')


# ==============================================================================
# Assertion helpers
# ==============================================================================

@pytest.fixture
def assert_valid_garch_params():
    """Helper to assert GARCH parameters are valid."""
    def _assert(params_dict):
        """
        Validate GARCH model parameters.

        Args:
            params_dict: Dictionary of parameter estimates
        """
        # Omega should be positive
        assert params_dict.get('omega', -1) > 0, "Omega must be positive"

        # Alpha and beta should be non-negative
        assert params_dict.get('alpha', -1) >= 0, "Alpha must be non-negative"
        assert params_dict.get('beta', -1) >= 0, "Beta must be non-negative"

        # Stationarity condition: alpha + beta < 1
        persistence = params_dict.get('alpha', 0) + params_dict.get('beta', 0)
        assert persistence < 1, f"Persistence {persistence} >= 1, model not stationary"

        # Gamma (if present) should be reasonable
        if 'gamma' in params_dict:
            assert params_dict['gamma'] >= 0, "Gamma should be non-negative for most financial data"

        # Nu (degrees of freedom) should be > 2
        if 'nu' in params_dict:
            assert params_dict['nu'] > 2, f"Degrees of freedom {params_dict['nu']} <= 2"

    return _assert


@pytest.fixture
def assert_reproducible():
    """Helper to assert reproducibility of results."""
    def _assert(result1, result2, tolerance=1e-6):
        """
        Assert two results are identical within tolerance.

        Args:
            result1: First result
            result2: Second result
            tolerance: Numerical tolerance
        """
        if isinstance(result1, (pd.Series, pd.DataFrame)):
            pd.testing.assert_frame_equal(result1, result2, atol=tolerance)
        elif isinstance(result1, np.ndarray):
            np.testing.assert_allclose(result1, result2, atol=tolerance)
        elif isinstance(result1, (int, float)):
            assert abs(result1 - result2) < tolerance
        else:
            assert result1 == result2

    return _assert


# ==============================================================================
# Pytest configuration hooks
# ==============================================================================

def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual functions"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests for multiple components"
    )
    config.addinivalue_line(
        "markers", "statistical: Statistical tests for model validation"
    )
    config.addinivalue_line(
        "markers", "edge_case: Edge case and error handling tests"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take significant time to run"
    )
    config.addinivalue_line(
        "markers", "reproducibility: Tests verifying reproducibility"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add slow marker to tests with 'slow' in name
        if 'slow' in item.nodeid.lower():
            item.add_marker(pytest.mark.slow)

        # Add integration marker to integration test files
        if 'test_integration' in item.nodeid:
            item.add_marker(pytest.mark.integration)

        # Add edge_case marker to edge case tests
        if 'edge_case' in item.nodeid.lower() or 'test_edge' in item.nodeid:
            item.add_marker(pytest.mark.edge_case)
