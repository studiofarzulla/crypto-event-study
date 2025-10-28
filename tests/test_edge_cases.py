"""
Edge case and error handling tests.

Tests boundary conditions, missing data, non-convergence scenarios,
and extreme values to ensure robustness.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import timedelta

from data_preparation import DataPreparation
from garch_models import GARCHModels


pytestmark = pytest.mark.edge_case


class TestMissingData:
    """Test handling of missing data scenarios."""

    def test_missing_price_data(self, data_with_missing):
        """Test handling of missing price data."""
        # Create DataPreparation instance
        prep = DataPreparation()

        # Calculate returns should skip/drop NaN
        returns = prep.calculate_log_returns(data_with_missing['price'])

        # Should handle NaN gracefully
        assert isinstance(returns, pd.Series)

    def test_missing_event_dates(self, data_prep):
        """Test event dummies when event falls outside date range."""
        # Create date range that doesn't include some events
        dates = pd.date_range('2024-01-01', '2024-12-31', freq='D', tz='UTC')

        # Create event outside range
        events = pd.DataFrame({
            'event_id': [999],
            'date': [pd.Timestamp('2018-01-01', tz='UTC')],
            'type': ['Infrastructure']
        })

        dummies = data_prep.create_event_dummies(dates, events)

        # Should create dummy column but with all zeros
        assert 'D_event_999' in dummies.columns
        assert dummies['D_event_999'].sum() == 0

    def test_sparse_sentiment_data(self, data_prep):
        """Test handling of sparse sentiment data."""
        # Create daily data with gaps
        dates = pd.date_range('2019-06-01', '2019-06-30', freq='D', tz='UTC')
        daily_data = pd.DataFrame({'price': np.ones(len(dates))}, index=dates)

        sentiment_df = data_prep.load_gdelt_sentiment()

        # Merge should forward-fill
        merged = data_prep.merge_sentiment_data(daily_data, sentiment_df)

        # Should not have NaN (either 0 or forward-filled)
        if 'S_gdelt_normalized' in merged.columns:
            assert not merged['S_gdelt_normalized'].isna().any()


class TestExtremeValues:
    """Test handling of extreme values."""

    def test_extreme_returns_winsorization(self, data_with_outliers):
        """Test winsorization caps extreme returns."""
        prep = DataPreparation()
        winsorized = prep.winsorize_returns(data_with_outliers, window=30, n_std=5)

        # Extreme values should be capped
        assert winsorized.max() < data_with_outliers.max()
        assert winsorized.min() > data_with_outliers.min()

        # No infinite values
        assert not np.isinf(winsorized).any()

    def test_zero_variance_period(self, data_with_zero_variance):
        """Test GARCH estimation with near-zero variance period."""
        data = pd.DataFrame({'returns_winsorized': data_with_zero_variance})
        modeler = GARCHModels(data, 'test')

        # Should not crash
        try:
            results = modeler.estimate_garch_11()
            assert results is not None
        except Exception as e:
            # Some failures are acceptable for pathological data
            assert "variance" in str(e).lower() or "convergence" in str(e).lower()

    def test_extreme_price_movements(self):
        """Test handling of extreme price movements (e.g., flash crash)."""
        # Create data with sudden price drop
        dates = pd.date_range('2020-01-01', periods=365, freq='D', tz='UTC')
        prices = np.ones(len(dates)) * 1000

        # Flash crash on day 100
        prices[100] = 100  # 90% drop
        prices[101:] = 1000  # Recovery

        price_series = pd.Series(prices, index=dates)

        prep = DataPreparation()
        returns = prep.calculate_log_returns(price_series)

        # Should compute valid returns
        assert not np.isinf(returns).any()

        # Winsorize to handle extreme
        winsorized = prep.winsorize_returns(returns, window=30, n_std=5)

        # Extreme should be capped
        assert abs(winsorized.min()) < abs(returns.min())


class TestShortTimeSeries:
    """Test behavior with short time series."""

    def test_very_short_series_garch(self):
        """Test GARCH with minimum viable observations."""
        # Create minimal time series (50 observations)
        short_returns = pd.Series(
            np.random.normal(0, 2, 50),
            index=pd.date_range('2020-01-01', periods=50, tz='UTC'),
            name='returns_winsorized'
        )

        data = pd.DataFrame({'returns_winsorized': short_returns})
        modeler = GARCHModels(data, 'test')

        # May or may not converge, but should not crash
        results = modeler.estimate_garch_11()
        assert results is not None

    def test_insufficient_data_for_window(self):
        """Test winsorization with insufficient data for window."""
        prep = DataPreparation()

        # Create series shorter than window
        short_returns = pd.Series(
            np.random.normal(0, 2, 20),
            index=pd.date_range('2020-01-01', periods=20, tz='UTC')
        )

        # Window is larger than data
        winsorized = prep.winsorize_returns(short_returns, window=30, n_std=5)

        # Should still work with min_periods
        assert len(winsorized) == len(short_returns)


class TestNonConvergence:
    """Test handling of model non-convergence."""

    def test_non_convergent_garch_handling(self):
        """Test graceful handling when GARCH doesn't converge."""
        # Create pathological data (very high autocorrelation)
        ar_data = np.zeros(500)
        ar_data[0] = 1
        for t in range(1, 500):
            ar_data[t] = 0.99 * ar_data[t-1] + np.random.normal(0, 0.1)

        returns = pd.Series(
            ar_data,
            index=pd.date_range('2020-01-01', periods=500, tz='UTC'),
            name='returns_winsorized'
        )

        data = pd.DataFrame({'returns_winsorized': returns})
        modeler = GARCHModels(data, 'test')

        results = modeler.estimate_garch_11()

        # Should have result object even if not converged
        assert results is not None
        assert hasattr(results, 'convergence')

        # If not converged, should have NaN values
        if not results.convergence:
            assert np.isnan(results.aic) or results.aic == np.nan or results.aic is None or np.isinf(results.aic)

    def test_tarchx_fallback_on_failure(self, btc_data_sample):
        """Test TARCH-X fallback mechanism when individual events fail."""
        modeler = GARCHModels(btc_data_sample, 'btc')

        # Reset fallback flag
        modeler._is_fallback_attempt = False

        # Try with individual events (may fail with too many parameters)
        results = modeler.estimate_tarch_x(use_individual_events=True, include_sentiment=True)

        # Should get a result (either converged or after fallback)
        assert results is not None


class TestBoundaryConditions:
    """Test boundary conditions and limits."""

    def test_single_event_in_data(self, data_prep):
        """Test with only one event in the entire dataset."""
        dates = pd.date_range('2020-01-01', '2020-12-31', freq='D', tz='UTC')

        events = pd.DataFrame({
            'event_id': [1],
            'date': [pd.Timestamp('2020-06-15', tz='UTC')],
            'type': ['Infrastructure']
        })

        dummies = data_prep.create_event_dummies(dates, events)

        assert 'D_event_1' in dummies.columns
        assert dummies['D_event_1'].sum() == 7  # 7-day window

    def test_overlapping_events_all_days(self, data_prep):
        """Test when events overlap on every day."""
        dates = pd.date_range('2020-06-01', '2020-06-30', freq='D', tz='UTC')

        # Create many overlapping events
        event_dates = pd.date_range('2020-06-01', '2020-06-30', freq='7D', tz='UTC')

        events = pd.DataFrame({
            'event_id': range(len(event_dates)),
            'date': event_dates,
            'type': ['Infrastructure'] * len(event_dates)
        })

        dummies = data_prep.create_event_dummies(dates, events)

        # Infrastructure dummy should be mostly 1s
        assert dummies['D_infrastructure'].sum() > 20  # Most days have event

    def test_zero_events(self, data_prep):
        """Test with no events."""
        dates = pd.date_range('2020-01-01', '2020-12-31', freq='D', tz='UTC')

        events = pd.DataFrame({
            'event_id': [],
            'date': [],
            'type': []
        })

        dummies = data_prep.create_event_dummies(dates, events)

        # Should still create aggregate dummies (all zeros)
        if 'D_infrastructure' in dummies.columns:
            assert dummies['D_infrastructure'].sum() == 0


class TestInvalidInputs:
    """Test handling of invalid inputs."""

    def test_negative_prices(self):
        """Test handling of negative prices (should error or handle gracefully)."""
        prep = DataPreparation()

        # Create series with negative price
        prices = pd.Series(
            [100, 110, -50, 120],  # Negative price is invalid
            index=pd.date_range('2020-01-01', periods=4, tz='UTC')
        )

        # Log returns with negative price will produce NaN
        returns = prep.calculate_log_returns(prices)

        # Should have NaN where negative
        assert returns.isna().any()

    def test_zero_prices(self):
        """Test handling of zero prices."""
        prep = DataPreparation()

        # Create series with zero price
        prices = pd.Series(
            [100, 110, 0, 120],  # Zero price
            index=pd.date_range('2020-01-01', periods=4, tz='UTC')
        )

        returns = prep.calculate_log_returns(prices)

        # Log of zero is -inf
        assert np.isinf(returns).any()

    def test_non_datetime_index(self):
        """Test that non-datetime index is handled."""
        prep = DataPreparation()

        # Create series with integer index
        prices = pd.Series([100, 110, 105, 115])  # No datetime index

        # Should still compute returns
        returns = prep.calculate_log_returns(prices)
        assert len(returns) == 3

    def test_empty_data(self):
        """Test handling of empty data."""
        prep = DataPreparation()

        empty_series = pd.Series([], dtype=float)

        # Should handle empty series
        returns = prep.calculate_log_returns(empty_series)
        assert len(returns) == 0


class TestTimezoneHandling:
    """Test timezone awareness and handling."""

    def test_timezone_mismatch(self, data_prep):
        """Test handling of timezone mismatches."""
        # Create dates without timezone
        dates_naive = pd.date_range('2020-01-01', '2020-12-31', freq='D')

        events = pd.DataFrame({
            'event_id': [1],
            'date': [pd.Timestamp('2020-06-15', tz='UTC')],
            'type': ['Infrastructure']
        })

        # Should handle timezone conversion
        try:
            dummies = data_prep.create_event_dummies(dates_naive, events)
            assert True  # Handled successfully
        except Exception as e:
            # Timezone conversion may fail, which is acceptable
            assert "timezone" in str(e).lower() or "tz" in str(e).lower()

    def test_utc_consistency(self, data_prep):
        """Test all timestamps are consistently UTC."""
        events = data_prep.load_events()
        sentiment = data_prep.load_gdelt_sentiment()

        # Events should be UTC
        assert events['date'].dtype == 'datetime64[ns, UTC]'

        # Sentiment index should be UTC
        assert sentiment.index.tz.zone == 'UTC' or str(sentiment.index.tz) == 'UTC'


class TestNumericalStability:
    """Test numerical stability in edge cases."""

    def test_very_small_returns(self):
        """Test with extremely small returns."""
        # Create near-zero returns
        tiny_returns = pd.Series(
            np.random.normal(0, 1e-8, 500),
            index=pd.date_range('2020-01-01', periods=500, tz='UTC'),
            name='returns_winsorized'
        )

        data = pd.DataFrame({'returns_winsorized': tiny_returns})
        modeler = GARCHModels(data, 'test')

        # Should handle without numerical errors
        results = modeler.estimate_garch_11()
        assert results is not None

    def test_very_large_returns(self):
        """Test with extremely large returns."""
        # Create very large returns
        large_returns = pd.Series(
            np.random.normal(0, 100, 500),
            index=pd.date_range('2020-01-01', periods=500, tz='UTC'),
            name='returns_winsorized'
        )

        data = pd.DataFrame({'returns_winsorized': large_returns})
        modeler = GARCHModels(data, 'test')

        results = modeler.estimate_garch_11()
        assert results is not None

        # If converged, omega should be very large
        if results.convergence:
            assert results.parameters.get('omega', 0) > 1


class TestConcurrentEstimation:
    """Test behavior with multiple simultaneous estimations."""

    def test_multiple_models_same_data(self, btc_data_sample):
        """Test estimating multiple models on same data simultaneously."""
        modeler = GARCHModels(btc_data_sample, 'btc')

        # Estimate all models
        all_results = modeler.estimate_all_models()

        # All should be independent
        assert len(all_results) == 3

        # Results should be stored correctly
        assert all_results['GARCH(1,1)'].model_type == 'GARCH(1,1)'
        assert all_results['TARCH(1,1)'].model_type == 'TARCH(1,1)'
        assert all_results['TARCH-X'].model_type == 'TARCH-X'


class TestRegressionPrevention:
    """Tests to prevent regression of known issues."""

    def test_sec_twin_suits_no_double_count(self, data_prep):
        """Ensure SEC twin suits don't create both individual and composite dummies."""
        dates = pd.date_range('2023-06-01', '2023-06-15', freq='D', tz='UTC')

        events = pd.DataFrame({
            'event_id': [31, 32],
            'date': [pd.Timestamp('2023-06-05', tz='UTC'), pd.Timestamp('2023-06-06', tz='UTC')],
            'type': ['Regulatory', 'Regulatory']
        })

        dummies = data_prep.create_event_dummies(dates, events)

        # Should NOT have individual dummies
        assert 'D_event_31' not in dummies.columns
        assert 'D_event_32' not in dummies.columns

        # Should have composite
        assert 'D_SEC_enforcement_2023' in dummies.columns

    def test_overlap_adjustment_exactly_half(self, data_prep):
        """Ensure overlap adjustment is exactly 0.5, not approximately."""
        dates = pd.date_range('2021-08-01', '2021-08-15', freq='D', tz='UTC')

        events = pd.DataFrame({
            'event_id': [17, 18],
            'date': [pd.Timestamp('2021-08-05', tz='UTC'), pd.Timestamp('2021-08-10', tz='UTC')],
            'type': ['Infrastructure', 'Infrastructure']
        })

        dummies = data_prep.create_event_dummies(dates, events)

        overlap_date = pd.Timestamp('2021-08-07', tz='UTC')
        if overlap_date in dummies.index:
            # Should be exactly 0.5
            assert dummies.loc[overlap_date, 'D_event_17'] == 0.5
            assert dummies.loc[overlap_date, 'D_event_18'] == 0.5

            # Not approximately 0.5
            np.testing.assert_equal(dummies.loc[overlap_date, 'D_event_17'], 0.5)

    def test_winsorization_no_infinite_values(self, data_prep):
        """Ensure winsorization never produces infinite values."""
        # Create data with extreme outliers
        extreme_data = pd.Series(
            [0.1] * 100 + [1000, -1000] + [0.1] * 100,
            index=pd.date_range('2020-01-01', periods=202, tz='UTC')
        )

        winsorized = data_prep.winsorize_returns(extreme_data, window=30, n_std=5)

        # Should have no infinite values
        assert not np.isinf(winsorized).any()
        assert not winsorized.isna().any()
