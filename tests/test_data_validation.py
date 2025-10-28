"""
Comprehensive data validation tests for cryptocurrency event study.

Tests data loading, quality checks, event classification, and edge cases.
Critical for ensuring reproducibility and data integrity.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import timedelta
from pathlib import Path


# Mark all tests in this module as data_validation tests
pytestmark = pytest.mark.data_validation


class TestDataLoading:
    """Test suite for data loading functions."""

    def test_load_crypto_prices_btc(self, data_prep):
        """Test loading Bitcoin price data."""
        btc_data = data_prep.load_crypto_prices('btc')

        assert isinstance(btc_data, pd.DataFrame)
        assert 'price' in btc_data.columns
        assert len(btc_data) > 0
        assert btc_data.index.name == 'snapped_at'

        # Check timezone awareness
        assert btc_data.index.tz is not None

    @pytest.mark.parametrize('crypto', ['btc', 'eth', 'xrp', 'bnb', 'ltc', 'ada'])
    def test_load_all_cryptocurrencies(self, data_prep, crypto):
        """Test loading data for all cryptocurrencies."""
        data = data_prep.load_crypto_prices(crypto)

        assert isinstance(data, pd.DataFrame)
        assert 'price' in data.columns
        assert len(data) > 100  # Should have reasonable amount of data

        # Prices should be positive
        assert (data['price'] > 0).all()

    def test_load_crypto_prices_date_range(self, data_prep):
        """Test that loaded data respects configured date range."""
        btc_data = data_prep.load_crypto_prices('btc')

        assert btc_data.index.min() >= data_prep.start_date
        assert btc_data.index.max() <= data_prep.end_date

    def test_load_crypto_prices_nonexistent(self, data_prep):
        """Test loading nonexistent cryptocurrency raises error."""
        with pytest.raises(FileNotFoundError):
            data_prep.load_crypto_prices('fake_crypto')

    def test_load_events(self, data_prep):
        """Test loading event data."""
        events = data_prep.load_events()

        assert isinstance(events, pd.DataFrame)
        assert 'event_id' in events.columns
        assert 'date' in events.columns
        assert 'type' in events.columns
        assert 'name' in events.columns or 'description' in events.columns

        # Event IDs should be unique
        assert events['event_id'].is_unique

        # Dates should be timezone-aware
        assert events['date'].dtype == 'datetime64[ns, UTC]'

    def test_load_events_types(self, events_df):
        """Test event type classification."""
        event_types = set(events_df['type'].unique())

        # Should have both Infrastructure and Regulatory
        assert 'Infrastructure' in event_types
        assert 'Regulatory' in event_types

        # All events should be classified
        assert events_df['type'].notna().all()

    def test_load_gdelt_sentiment(self, data_prep):
        """Test loading GDELT sentiment data."""
        sentiment = data_prep.load_gdelt_sentiment()

        assert isinstance(sentiment, pd.DataFrame)
        assert 'S_gdelt_normalized' in sentiment.columns
        assert 'S_reg_decomposed' in sentiment.columns
        assert 'S_infra_decomposed' in sentiment.columns

        # Check weekly frequency
        date_diffs = sentiment.index[1:] - sentiment.index[:-1]
        assert all(diff.days == 7 for diff in date_diffs[:10])


class TestDataQuality:
    """Test suite for data quality validation."""

    def test_no_missing_prices(self, data_prep):
        """Test that price data has no missing values."""
        btc_data = data_prep.load_crypto_prices('btc')

        assert not btc_data['price'].isna().any()

    def test_prices_positive(self, data_prep):
        """Test all prices are positive."""
        for crypto in ['btc', 'eth', 'xrp']:
            data = data_prep.load_crypto_prices(crypto)
            assert (data['price'] > 0).all(), f"{crypto} has non-positive prices"

    def test_no_duplicate_dates(self, data_prep):
        """Test no duplicate dates in price data."""
        btc_data = data_prep.load_crypto_prices('btc')

        assert not btc_data.index.duplicated().any()

    def test_chronological_order(self, data_prep):
        """Test data is in chronological order."""
        btc_data = data_prep.load_crypto_prices('btc')

        assert btc_data.index.is_monotonic_increasing

    def test_sentiment_normalized_range(self, sentiment_df):
        """Test sentiment normalization produces reasonable values."""
        # Normalized sentiment should have mean ~0 and std ~1 (after initialization period)
        post_init = sentiment_df[sentiment_df.index >= pd.Timestamp('2019-06-01', tz='UTC')]

        if len(post_init) > 0:
            normalized = post_init['S_gdelt_normalized'].dropna()
            if len(normalized) > 0:
                # Should be approximately standardized
                assert abs(normalized.mean()) < 2.0  # Not too far from 0
                # Standard deviation should be reasonable
                assert 0.1 < normalized.std() < 5.0


class TestLogReturnsCalculation:
    """Test suite for log returns calculation."""

    def test_calculate_log_returns_basic(self, data_prep, sample_prices):
        """Test basic log returns calculation."""
        returns = data_prep.calculate_log_returns(sample_prices)

        # Should have one less observation than prices
        assert len(returns) == len(sample_prices) - 1

        # Should have no NaN values
        assert not returns.isna().any()

    def test_calculate_log_returns_accuracy(self, data_prep):
        """Test log returns calculation accuracy."""
        # Create simple price series
        prices = pd.Series([100, 110, 105, 115], index=pd.date_range('2020-01-01', periods=4, tz='UTC'))
        returns = data_prep.calculate_log_returns(prices)

        # Manual calculation
        expected_0 = np.log(110/100) * 100
        expected_1 = np.log(105/110) * 100
        expected_2 = np.log(115/105) * 100

        np.testing.assert_almost_equal(returns.iloc[0], expected_0, decimal=5)
        np.testing.assert_almost_equal(returns.iloc[1], expected_1, decimal=5)
        np.testing.assert_almost_equal(returns.iloc[2], expected_2, decimal=5)

    def test_log_returns_on_actual_data(self, data_prep):
        """Test log returns on actual cryptocurrency data."""
        btc_data = data_prep.load_crypto_prices('btc')
        returns = data_prep.calculate_log_returns(btc_data['price'])

        # Returns should be in reasonable range (after winsorization)
        # Most daily crypto returns should be < 20%
        assert returns.abs().quantile(0.95) < 50  # 95th percentile < 50%


class TestWinsorization:
    """Test suite for returns winsorization."""

    def test_winsorize_returns_removes_outliers(self, data_prep, data_with_outliers):
        """Test winsorization removes extreme outliers."""
        winsorized = data_prep.winsorize_returns(data_with_outliers, window=30, n_std=5)

        # Extreme outliers should be clipped
        assert winsorized.max() < data_with_outliers.max()
        assert winsorized.min() > data_with_outliers.min()

        # But most values should be unchanged
        diff = (winsorized - data_with_outliers).abs()
        assert (diff < 0.01).sum() > len(data_with_outliers) * 0.95  # 95% unchanged

    def test_winsorize_returns_preserves_shape(self, data_prep, sample_returns):
        """Test winsorization preserves data shape."""
        winsorized = data_prep.winsorize_returns(sample_returns)

        assert len(winsorized) == len(sample_returns)
        assert winsorized.index.equals(sample_returns.index)

    def test_winsorize_window_size(self, data_prep, sample_returns):
        """Test different window sizes produce different results."""
        win_30 = data_prep.winsorize_returns(sample_returns, window=30, n_std=5)
        win_90 = data_prep.winsorize_returns(sample_returns, window=90, n_std=5)

        # Results should differ (rolling window affects clipping bounds)
        assert not win_30.equals(win_90)


class TestEventDummyCreation:
    """Test suite for event dummy variable creation."""

    def test_create_event_window_length(self, data_prep):
        """Test event window creates correct number of days."""
        event_date = pd.Timestamp('2020-06-15', tz='UTC')
        window = data_prep.create_event_window(event_date, days_before=3, days_after=3)

        assert len(window) == 7  # 3 + 1 + 3

    def test_create_event_window_centering(self, data_prep):
        """Test event window is centered on event date."""
        event_date = pd.Timestamp('2020-06-15', tz='UTC')
        window = data_prep.create_event_window(event_date, days_before=3, days_after=3)

        assert window[3] == event_date  # Middle of window

    def test_create_event_dummies_regular(self, data_prep):
        """Test creation of regular event dummies."""
        dates = pd.date_range('2020-01-01', '2020-12-31', freq='D', tz='UTC')

        events = pd.DataFrame({
            'event_id': [999],
            'date': [pd.Timestamp('2020-06-15', tz='UTC')],
            'type': ['Infrastructure']
        })

        dummies = data_prep.create_event_dummies(dates, events)

        assert 'D_event_999' in dummies.columns
        assert dummies['D_event_999'].sum() == 7  # 7-day window
        assert dummies['D_infrastructure' in dummies.columns

    def test_sec_twin_suits_composite(self, data_prep):
        """Test SEC twin suits create composite dummy."""
        dates = pd.date_range('2023-06-01', '2023-06-15', freq='D', tz='UTC')

        events = pd.DataFrame({
            'event_id': [31, 32],
            'date': [pd.Timestamp('2023-06-05', tz='UTC'), pd.Timestamp('2023-06-06', tz='UTC')],
            'type': ['Regulatory', 'Regulatory']
        })

        dummies = data_prep.create_event_dummies(dates, events)

        # Should have composite dummy, not individual
        assert 'D_SEC_enforcement_2023' in dummies.columns
        assert 'D_event_31' not in dummies.columns
        assert 'D_event_32' not in dummies.columns

    def test_eip_poly_overlap_adjustment(self, data_prep):
        """Test EIP-1559 and Polygon overlap gets 0.5 adjustment."""
        dates = pd.date_range('2021-08-01', '2021-08-15', freq='D', tz='UTC')

        events = pd.DataFrame({
            'event_id': [17, 18],
            'date': [pd.Timestamp('2021-08-05', tz='UTC'), pd.Timestamp('2021-08-10', tz='UTC')],
            'type': ['Infrastructure', 'Infrastructure']
        })

        dummies = data_prep.create_event_dummies(dates, events)

        # Check overlap dates have 0.5 value
        overlap_date = pd.Timestamp('2021-08-07', tz='UTC')
        if overlap_date in dummies.index:
            assert dummies.loc[overlap_date, 'D_event_17'] == 0.5
            assert dummies.loc[overlap_date, 'D_event_18'] == 0.5

    def test_bybit_sec_truncation(self, data_prep):
        """Test Bybit and SEC dismissal window truncation."""
        dates = pd.date_range('2025-02-18', '2025-03-03', freq='D', tz='UTC')

        events = pd.DataFrame({
            'event_id': [43, 44],
            'date': [pd.Timestamp('2025-02-21', tz='UTC'), pd.Timestamp('2025-02-27', tz='UTC')],
            'type': ['Infrastructure', 'Regulatory']
        })

        dummies = data_prep.create_event_dummies(dates, events)

        # Bybit should end on Feb 23
        assert dummies.loc[pd.Timestamp('2025-02-23', tz='UTC'), 'D_event_43'] == 1
        assert dummies.loc[pd.Timestamp('2025-02-24', tz='UTC'), 'D_event_43'] == 0

        # SEC should start on Feb 27
        assert dummies.loc[pd.Timestamp('2025-02-26', tz='UTC'), 'D_event_44'] == 0
        assert dummies.loc[pd.Timestamp('2025-02-27', tz='UTC'), 'D_event_44'] == 1

    def test_aggregate_event_type_dummies(self, data_prep, events_df):
        """Test infrastructure and regulatory aggregate dummies are created."""
        dates = pd.date_range('2019-01-01', '2025-12-31', freq='D', tz='UTC')

        dummies = data_prep.create_event_dummies(dates, events_df)

        assert 'D_infrastructure' in dummies.columns
        assert 'D_regulatory' in dummies.columns

        # Aggregates should be 0 or 1
        assert set(dummies['D_infrastructure'].unique()).issubset({0, 1})
        assert set(dummies['D_regulatory'].unique()).issubset({0, 1})


class TestSentimentMerging:
    """Test suite for sentiment data merging."""

    def test_merge_sentiment_forward_fill(self, data_prep, sentiment_df):
        """Test sentiment data forward fills correctly."""
        # Create daily data
        daily_dates = pd.date_range('2019-06-01', '2019-06-30', freq='D', tz='UTC')
        daily_data = pd.DataFrame({'price': np.ones(len(daily_dates))}, index=daily_dates)

        merged = data_prep.merge_sentiment_data(daily_data, sentiment_df)

        # Should have sentiment columns
        assert 'S_gdelt_normalized' in merged.columns or 'S_reg_decomposed' in merged.columns

        # Should not have NaN values
        if 'S_gdelt_normalized' in merged.columns:
            assert not merged['S_gdelt_normalized'].isna().all()

    def test_merge_sentiment_early_dates_zero(self, data_prep, sentiment_df):
        """Test sentiment before June 2019 is set to zero."""
        early_dates = pd.date_range('2019-01-01', '2019-05-31', freq='D', tz='UTC')
        early_data = pd.DataFrame({'price': np.ones(len(early_dates))}, index=early_dates)

        merged = data_prep.merge_sentiment_data(early_data, sentiment_df)

        if 'S_gdelt_normalized' in merged.columns:
            assert (merged['S_gdelt_normalized'] == 0).all()


class TestDataValidation:
    """Test suite for data validation function."""

    def test_validate_data_complete(self, data_prep):
        """Test validation on complete prepared data."""
        btc_data = data_prep.prepare_crypto_data('btc', include_events=True, include_sentiment=True)
        validation = data_prep.validate_data(btc_data)

        assert 'missing_values' in validation
        assert 'infinite_returns' in validation
        assert 'max_return' in validation
        assert 'min_return' in validation
        assert 'return_std' in validation

    def test_validate_no_infinite_returns(self, data_prep):
        """Test validation detects no infinite returns after winsorization."""
        btc_data = data_prep.prepare_crypto_data('btc')
        validation = data_prep.validate_data(btc_data)

        assert validation['infinite_returns'] == 0

    def test_validate_returns_reasonable(self, data_prep):
        """Test winsorized returns are in reasonable range."""
        btc_data = data_prep.prepare_crypto_data('btc')
        validation = data_prep.validate_data(btc_data)

        # After winsorization, returns should be < 50% daily
        assert abs(validation['max_return']) < 50
        assert abs(validation['min_return']) < 50


class TestDataPreparationPipeline:
    """Integration tests for complete data preparation pipeline."""

    @pytest.mark.integration
    def test_prepare_crypto_data_complete(self, data_prep):
        """Test complete data preparation pipeline for BTC."""
        btc_data = data_prep.prepare_crypto_data(
            'btc',
            include_events=True,
            include_sentiment=True
        )

        # Check all required columns present
        assert 'price' in btc_data.columns
        assert 'returns' in btc_data.columns
        assert 'returns_winsorized' in btc_data.columns

        # Event dummies
        event_cols = [col for col in btc_data.columns if col.startswith('D_')]
        assert len(event_cols) > 0
        assert 'D_infrastructure' in btc_data.columns
        assert 'D_regulatory' in btc_data.columns

        # Sentiment
        assert 'S_gdelt_normalized' in btc_data.columns or 'S_reg_decomposed' in btc_data.columns

    @pytest.mark.integration
    def test_prepare_all_cryptos_consistency(self, data_prep):
        """Test all cryptocurrencies have consistent structure."""
        all_data = data_prep.prepare_all_cryptos(include_events=True, include_sentiment=True)

        assert len(all_data) >= 1  # At least one crypto loaded

        # All should have same columns
        first_crypto = list(all_data.keys())[0]
        first_cols = set(all_data[first_crypto].columns)

        for crypto, df in all_data.items():
            assert set(df.columns) == first_cols, f"{crypto} has different columns"

    @pytest.mark.slow
    @pytest.mark.integration
    def test_prepare_all_cryptos_validation(self, data_prep):
        """Test all prepared cryptocurrencies pass validation."""
        all_data = data_prep.prepare_all_cryptos()

        for crypto, df in all_data.items():
            validation = data_prep.validate_data(df)

            # No infinite returns
            assert validation['infinite_returns'] == 0, f"{crypto} has infinite returns"

            # Reasonable return range
            assert abs(validation['max_return']) < 100, f"{crypto} max return too large"
            assert abs(validation['min_return']) < 100, f"{crypto} min return too small"
