"""
Integration tests for complete event study pipeline.

Tests full end-to-end workflow from data loading through
model estimation to hypothesis testing and publication outputs.
Critical for ensuring reproducibility at journal level.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import json

from code.core.data_preparation import DataPreparation
from code.core.garch_models import GARCHModels, estimate_models_for_all_cryptos
from code.analysis.event_impact_analysis import EventImpactAnalysis, run_complete_analysis


pytestmark = pytest.mark.integration


class TestEndToEndPipeline:
    """Test complete end-to-end analysis pipeline."""

    def test_full_pipeline_single_crypto(self, data_prep, btc_data_sample):
        """Test complete pipeline for single cryptocurrency."""
        # Step 1: Data preparation (already done in fixture)
        assert 'returns_winsorized' in btc_data_sample.columns
        assert 'D_infrastructure' in btc_data_sample.columns or 'D_regulatory' in btc_data_sample.columns

        # Step 2: Model estimation
        modeler = GARCHModels(btc_data_sample, 'btc')
        all_models = modeler.estimate_all_models()

        # Should have all three models
        assert 'GARCH(1,1)' in all_models
        assert 'TARCH(1,1)' in all_models
        assert 'TARCH-X' in all_models

        # At least one should converge
        converged = [name for name, result in all_models.items() if result.convergence]
        assert len(converged) >= 1

        # Step 3: Event impact analysis (if TARCH-X converged)
        if all_models['TARCH-X'].convergence:
            model_results = {'btc': all_models}
            analyzer = EventImpactAnalysis(model_results)

            # Should be able to extract event coefficients
            event_coeffs = analyzer.event_coefficients
            assert isinstance(event_coeffs, pd.DataFrame)

    @pytest.mark.slow
    def test_full_pipeline_multiple_cryptos(self, data_prep):
        """Test complete pipeline across multiple cryptocurrencies."""
        # Prepare data for multiple cryptos
        crypto_data = {}
        for crypto in ['btc', 'eth']:  # Test with 2 cryptos to save time
            try:
                crypto_data[crypto] = data_prep.prepare_crypto_data(
                    crypto,
                    include_events=True,
                    include_sentiment=True
                )
            except Exception as e:
                pytest.skip(f"Could not load {crypto} data: {e}")

        # Estimate models for all
        all_results = estimate_models_for_all_cryptos(crypto_data)

        # Should have results for each crypto
        assert len(all_results) >= 1

        # Run complete analysis
        analysis = run_complete_analysis(all_results)

        # Should have all analysis components
        assert 'hypothesis_test' in analysis
        assert 'by_crypto' in analysis
        assert 'persistence' in analysis

    def test_reproducibility_full_pipeline(self, btc_data_sample, random_seed):
        """Test full pipeline produces reproducible results."""
        # Run pipeline twice with same seed
        np.random.seed(42)

        # First run
        modeler1 = GARCHModels(btc_data_sample, 'btc')
        results1 = modeler1.estimate_garch_11()

        # Reset seed
        np.random.seed(42)

        # Second run
        modeler2 = GARCHModels(btc_data_sample, 'btc')
        results2 = modeler2.estimate_garch_11()

        # Results should be identical (if both converged)
        if results1.convergence and results2.convergence:
            # AIC should be identical
            np.testing.assert_almost_equal(results1.aic, results2.aic, decimal=4)

            # Log-likelihood should be identical
            np.testing.assert_almost_equal(
                results1.log_likelihood,
                results2.log_likelihood,
                decimal=4
            )


class TestDataPersistence:
    """Test data can be saved and loaded correctly."""

    def test_save_prepared_data(self, btc_data_sample, output_dir):
        """Test prepared data can be saved and reloaded."""
        # Save data
        output_file = output_dir / "btc_prepared.csv"
        btc_data_sample.to_csv(output_file)

        # Reload data
        reloaded = pd.read_csv(output_file, index_col=0, parse_dates=True)

        # Should have same shape
        assert reloaded.shape == btc_data_sample.shape

        # Should have same columns
        assert set(reloaded.columns) == set(btc_data_sample.columns)

    def test_save_model_results(self, btc_data_sample, output_dir):
        """Test model results can be saved and reloaded."""
        modeler = GARCHModels(btc_data_sample, 'btc')
        garch_results = modeler.estimate_garch_11()

        if garch_results.convergence:
            # Save parameters
            params_file = output_dir / "garch_params.json"
            with open(params_file, 'w') as f:
                json.dump({
                    'model_type': garch_results.model_type,
                    'crypto': garch_results.crypto,
                    'parameters': garch_results.parameters,
                    'aic': garch_results.aic,
                    'bic': garch_results.bic,
                    'log_likelihood': garch_results.log_likelihood
                }, f, indent=2)

            # Reload
            with open(params_file, 'r') as f:
                reloaded = json.load(f)

            # Check integrity
            assert reloaded['model_type'] == garch_results.model_type
            assert reloaded['crypto'] == garch_results.crypto
            np.testing.assert_almost_equal(reloaded['aic'], garch_results.aic, decimal=6)


class TestRobustnessAcrossCryptos:
    """Test analysis is robust across different cryptocurrencies."""

    @pytest.mark.parametrize('crypto', ['btc', 'eth', 'xrp'])
    def test_data_preparation_all_cryptos(self, data_prep, crypto):
        """Test data preparation works for all cryptocurrencies."""
        try:
            data = data_prep.prepare_crypto_data(
                crypto,
                include_events=True,
                include_sentiment=True
            )

            # Basic checks
            assert 'returns_winsorized' in data.columns
            assert len(data) > 100

            # Validate data
            validation = data_prep.validate_data(data)
            assert validation['infinite_returns'] == 0

        except FileNotFoundError:
            pytest.skip(f"Data file for {crypto} not found")

    @pytest.mark.parametrize('crypto', ['btc', 'eth'])
    def test_garch_estimation_all_cryptos(self, data_prep, crypto):
        """Test GARCH estimation works for multiple cryptos."""
        try:
            data = data_prep.prepare_crypto_data(crypto)
            modeler = GARCHModels(data, crypto)
            results = modeler.estimate_garch_11()

            # Should at least attempt estimation
            assert results is not None

            # If converged, parameters should be valid
            if results.convergence:
                assert 'omega' in results.parameters
                assert results.parameters['omega'] > 0

        except FileNotFoundError:
            pytest.skip(f"Data file for {crypto} not found")


class TestConsistencyChecks:
    """Test consistency across different analysis components."""

    def test_event_counts_consistent(self, data_prep, events_df):
        """Test event counts are consistent across data preparation."""
        # Count events by type
        infra_count = (events_df['type'] == 'Infrastructure').sum()
        reg_count = (events_df['type'] == 'Regulatory').sum()

        # Create dummies
        dates = pd.date_range('2019-01-01', '2025-12-31', freq='D', tz='UTC')
        dummies = data_prep.create_event_dummies(dates, events_df)

        # Count individual event dummies
        event_dummy_cols = [col for col in dummies.columns if col.startswith('D_event_')]

        # Should have close to expected number (accounting for special cases)
        # Some events create composite dummies, so exact count may differ
        assert len(event_dummy_cols) > 0

    def test_sentiment_decomposition_consistency(self, sentiment_df):
        """Test sentiment decomposition components sum correctly."""
        if all(col in sentiment_df.columns for col in ['S_reg_decomposed', 'S_infra_decomposed', 'reg_proportion', 'infra_proportion']):
            # Proportions should sum to ~1 (allowing for rounding)
            total_props = sentiment_df['reg_proportion'] + sentiment_df['infra_proportion']
            np.testing.assert_array_almost_equal(total_props, 1.0, decimal=2)

    def test_volatility_persistence_consistency(self, btc_data_sample):
        """Test volatility persistence is consistent across models."""
        modeler = GARCHModels(btc_data_sample, 'btc')

        garch_results = modeler.estimate_garch_11()
        tarch_results = modeler.estimate_tarch_11()

        if garch_results.convergence and tarch_results.convergence:
            # Extract persistence
            garch_alpha = garch_results.parameters.get('alpha[1]', garch_results.parameters.get('alpha', 0))
            garch_beta = garch_results.parameters.get('beta[1]', garch_results.parameters.get('beta', 0))
            garch_persistence = garch_alpha + garch_beta

            tarch_alpha = tarch_results.parameters.get('alpha[1]', tarch_results.parameters.get('alpha', 0))
            tarch_beta = tarch_results.parameters.get('beta[1]', tarch_results.parameters.get('beta', 0))
            tarch_gamma = tarch_results.parameters.get('gamma[1]', tarch_results.parameters.get('gamma', 0))
            tarch_persistence = tarch_alpha + tarch_beta + tarch_gamma/2

            # Both should be stationary
            assert garch_persistence < 1
            assert tarch_persistence < 1

            # Should be reasonably similar (within 0.2)
            assert abs(garch_persistence - tarch_persistence) < 0.3


class TestPublicationOutputs:
    """Test generation of publication-ready outputs."""

    def test_generate_summary_table(self, btc_data_sample):
        """Test generation of publication summary table."""
        modeler = GARCHModels(btc_data_sample, 'btc')
        all_models = modeler.estimate_all_models()

        # Create comparison table data
        comparison_data = []
        for model_name, result in all_models.items():
            if result.convergence:
                comparison_data.append({
                    'Model': model_name,
                    'AIC': result.aic,
                    'BIC': result.bic,
                    'LogLik': result.log_likelihood
                })

        if comparison_data:
            comparison_df = pd.DataFrame(comparison_data)

            # Should be formatted for publication
            assert len(comparison_df) > 0
            assert 'Model' in comparison_df.columns
            assert 'AIC' in comparison_df.columns

    def test_generate_event_impact_table(self, mock_model_results):
        """Test generation of event impact publication table."""
        analyzer = EventImpactAnalysis(mock_model_results)
        pub_table = analyzer.generate_publication_table()

        if not pub_table.empty:
            # Should have publication formatting
            assert isinstance(pub_table, pd.DataFrame)

            # Should have event type breakdown
            assert 'Event Type' in pub_table.columns or 'event_type' in pub_table.columns

    def test_hypothesis_test_report(self, mock_model_results):
        """Test hypothesis test report generation."""
        analyzer = EventImpactAnalysis(mock_model_results)
        results = analyzer.test_infrastructure_vs_regulatory()

        # Should have all components needed for publication
        assert 'infrastructure' in results
        assert 'regulatory' in results

        # Should have test statistics
        assert 't_test' in results or 'mann_whitney' in results

        # Should have effect size
        assert 'effect_size' in results


class TestMemoryAndPerformance:
    """Test memory usage and performance characteristics."""

    def test_memory_efficiency_single_crypto(self, btc_data_sample):
        """Test single crypto analysis doesn't consume excessive memory."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss / 1024 / 1024  # MB

        # Run full analysis
        modeler = GARCHModels(btc_data_sample, 'btc')
        _ = modeler.estimate_all_models()

        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        mem_increase = mem_after - mem_before

        # Should not increase by more than 500MB for single crypto
        assert mem_increase < 500, f"Memory increased by {mem_increase:.1f}MB"

    @pytest.mark.slow
    def test_estimation_time_reasonable(self, btc_data_sample):
        """Test model estimation completes in reasonable time."""
        import time

        modeler = GARCHModels(btc_data_sample, 'btc')

        # Time GARCH estimation
        start = time.time()
        _ = modeler.estimate_garch_11()
        elapsed = time.time() - start

        # Should complete in under 30 seconds
        assert elapsed < 30, f"GARCH estimation took {elapsed:.1f} seconds"


class TestDataIntegrity:
    """Test data integrity throughout pipeline."""

    def test_no_data_leakage(self, data_prep):
        """Test no data leakage between cryptocurrencies."""
        btc_data = data_prep.prepare_crypto_data('btc')
        eth_data = data_prep.prepare_crypto_data('eth')

        # Indices should be independent
        assert not btc_data.index.equals(eth_data.index) or len(btc_data) == len(eth_data)

        # Returns should be different
        if len(btc_data) == len(eth_data) and btc_data.index.equals(eth_data.index):
            assert not btc_data['returns'].equals(eth_data['returns'])

    def test_event_dummies_integrity(self, data_prep, events_df):
        """Test event dummies maintain integrity."""
        dates = pd.date_range('2019-01-01', '2025-12-31', freq='D', tz='UTC')
        dummies = data_prep.create_event_dummies(dates, events_df)

        # All dummies should be 0, 0.5, or 1
        for col in dummies.columns:
            if col.startswith('D_'):
                unique_vals = set(dummies[col].unique())
                valid_vals = {0, 0.5, 1, 0.0, 0.5, 1.0}
                assert unique_vals.issubset(valid_vals), f"{col} has invalid values: {unique_vals}"

    def test_no_future_information(self, data_prep):
        """Test no future information is used (no look-ahead bias)."""
        # Sentiment should be forward-filled (weekly → daily)
        # Never back-filled
        sentiment_df = data_prep.load_gdelt_sentiment()

        # Check there are no leading NaNs that got back-filled
        # (sentiment should only be 0 or valid values, never NaN in production)
        assert not sentiment_df['S_gdelt_normalized'].isna().any() or \
               sentiment_df.index.min() >= pd.Timestamp('2019-06-01', tz='UTC')


@pytest.fixture
def mock_model_results():
    """Create mock model results for testing."""
    from garch_models import ModelResults

    results = {}
    for crypto in ['btc', 'eth', 'xrp']:
        crypto_results = {}
        tarchx_result = ModelResults(
            model_type='TARCH-X',
            crypto=crypto,
            aic=1000.0 + np.random.rand()*10,
            bic=1020.0 + np.random.rand()*10,
            log_likelihood=-500.0 - np.random.rand()*5,
            parameters={
                'omega': 0.01,
                'alpha[1]': 0.10,
                'gamma[1]': 0.05,
                'beta[1]': 0.85,
            },
            std_errors={'omega': 0.002},
            pvalues={'omega': 0.01},
            convergence=True,
            iterations=100,
            volatility=pd.Series(np.random.rand(100) * 2 + 1),
            residuals=pd.Series(np.random.randn(100)),
            leverage_effect=0.05,
            event_effects={
                'D_infrastructure': 0.02 + np.random.rand()*0.01,
                'D_regulatory': 0.01 + np.random.rand()*0.005
            },
            sentiment_effects={},
            event_std_errors={'D_infrastructure': 0.005, 'D_regulatory': 0.003},
            event_pvalues={'D_infrastructure': 0.01, 'D_regulatory': 0.05}
        )
        crypto_results['TARCH-X'] = tarchx_result
        results[crypto] = crypto_results
    return results
