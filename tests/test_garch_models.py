"""
Comprehensive tests for GARCH model estimation.

Tests model convergence, parameter validation, volatility forecasting,
and TARCH-X exogenous variable integration.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from code.core.garch_models import GARCHModels, ModelResults, estimate_models_for_crypto


pytestmark = pytest.mark.statistical


class TestGARCHModelInitialization:
    """Test GARCH model initialization and setup."""

    def test_garch_model_init(self, sample_prepared_data):
        """Test GARCHModels initialization."""
        modeler = GARCHModels(sample_prepared_data, 'btc')

        assert modeler.crypto == 'btc'
        assert len(modeler.returns) > 0
        assert modeler.has_events is True
        assert modeler.has_sentiment is True

    def test_garch_model_returns_extraction(self, sample_prepared_data):
        """Test returns are correctly extracted."""
        modeler = GARCHModels(sample_prepared_data, 'btc')

        # Should use winsorized returns
        assert modeler.returns.name == 'returns_winsorized' or modeler.returns.dtype == np.float64
        assert not modeler.returns.isna().any()

    def test_exogenous_variable_detection(self, sample_prepared_data):
        """Test detection of exogenous variables."""
        modeler = GARCHModels(sample_prepared_data, 'btc')

        # Should detect event dummies
        assert modeler.has_events

        # Should detect sentiment
        assert modeler.has_sentiment


class TestGARCH11Estimation:
    """Test GARCH(1,1) baseline model estimation."""

    @pytest.mark.unit
    def test_garch_11_converges(self, sample_prepared_data, random_seed):
        """Test GARCH(1,1) model converges on sample data."""
        modeler = GARCHModels(sample_prepared_data, 'test')
        results = modeler.estimate_garch_11()

        assert results is not None
        assert results.model_type == 'GARCH(1,1)'

        # May or may not converge on random data, but should not crash
        assert isinstance(results.convergence, bool)

    @pytest.mark.unit
    def test_garch_11_parameters(self, sample_prepared_data, assert_valid_garch_params, random_seed):
        """Test GARCH(1,1) produces valid parameters if converged."""
        modeler = GARCHModels(sample_prepared_data, 'test')
        results = modeler.estimate_garch_11()

        if results.convergence:
            # Should have expected parameters
            assert 'omega' in results.parameters
            assert 'alpha[1]' in results.parameters or 'alpha' in results.parameters
            assert 'beta[1]' in results.parameters or 'beta' in results.parameters

            # Validate parameter constraints
            assert_valid_garch_params(results.parameters)

    @pytest.mark.integration
    def test_garch_11_on_actual_data(self, btc_data_sample):
        """Test GARCH(1,1) on actual BTC data."""
        modeler = GARCHModels(btc_data_sample, 'btc')
        results = modeler.estimate_garch_11()

        # Should converge on real data
        assert results.convergence, "GARCH(1,1) should converge on actual BTC data"

        # Check information criteria
        assert not np.isnan(results.aic)
        assert not np.isnan(results.bic)
        assert not np.isnan(results.log_likelihood)

        # Volatility should be computed
        assert len(results.volatility) > 0
        assert results.volatility.min() > 0  # Volatility must be positive

    def test_garch_11_volatility_output(self, sample_prepared_data, random_seed):
        """Test GARCH(1,1) produces volatility series."""
        modeler = GARCHModels(sample_prepared_data, 'test')
        results = modeler.estimate_garch_11()

        if results.convergence:
            assert isinstance(results.volatility, pd.Series)
            assert len(results.volatility) > 0

            # Volatility should be positive
            assert (results.volatility > 0).all()


class TestTARCH11Estimation:
    """Test TARCH(1,1) model with asymmetric effects."""

    @pytest.mark.unit
    def test_tarch_11_converges(self, sample_prepared_data, random_seed):
        """Test TARCH(1,1) model estimation."""
        modeler = GARCHModels(sample_prepared_data, 'test')
        results = modeler.estimate_tarch_11()

        assert results is not None
        assert results.model_type == 'TARCH(1,1)'

    @pytest.mark.unit
    def test_tarch_11_leverage_effect(self, sample_prepared_data, random_seed):
        """Test TARCH(1,1) includes leverage effect parameter."""
        modeler = GARCHModels(sample_prepared_data, 'test')
        results = modeler.estimate_tarch_11()

        if results.convergence:
            # Should have gamma parameter (leverage effect)
            assert 'gamma[1]' in results.parameters or 'gamma' in results.parameters

            # Leverage effect should be accessible
            assert results.leverage_effect is not None or 'gamma' in results.parameters

    @pytest.mark.integration
    def test_tarch_11_on_actual_data(self, btc_data_sample, assert_valid_garch_params):
        """Test TARCH(1,1) on actual cryptocurrency data."""
        modeler = GARCHModels(btc_data_sample, 'btc')
        results = modeler.estimate_tarch_11()

        assert results.convergence, "TARCH(1,1) should converge on actual data"

        # Validate GARCH parameters
        assert_valid_garch_params(results.parameters)

        # Leverage effect should be non-negative for crypto (negative returns increase volatility)
        if 'gamma[1]' in results.parameters:
            assert results.parameters['gamma[1]'] >= 0

    def test_tarch_improves_on_garch(self, sample_prepared_data, random_seed):
        """Test TARCH should have better or equal fit than GARCH."""
        modeler = GARCHModels(sample_prepared_data, 'test')

        garch_results = modeler.estimate_garch_11()
        tarch_results = modeler.estimate_tarch_11()

        if garch_results.convergence and tarch_results.convergence:
            # TARCH adds one parameter, so BIC might be worse, but AIC should improve or stay similar
            # (TARCH nests GARCH when gamma=0)
            assert tarch_results.log_likelihood >= garch_results.log_likelihood - 0.01


class TestTARCHXEstimation:
    """Test TARCH-X model with exogenous variables."""

    @pytest.mark.unit
    def test_tarchx_with_events(self, sample_prepared_data, random_seed):
        """Test TARCH-X estimation with event dummies."""
        modeler = GARCHModels(sample_prepared_data, 'test')
        results = modeler.estimate_tarch_x(use_individual_events=False, include_sentiment=False)

        assert results is not None
        assert results.model_type == 'TARCH-X'

    @pytest.mark.unit
    def test_tarchx_event_effects(self, sample_prepared_data, random_seed):
        """Test TARCH-X extracts event effects."""
        modeler = GARCHModels(sample_prepared_data, 'test')
        results = modeler.estimate_tarch_x(use_individual_events=False, include_sentiment=False)

        if results.convergence:
            # Should have event effects dictionary
            assert results.event_effects is not None
            assert isinstance(results.event_effects, dict)

            # Should have infrastructure and regulatory if data has them
            if 'D_infrastructure' in sample_prepared_data.columns:
                assert 'D_infrastructure' in results.event_effects

    @pytest.mark.unit
    def test_tarchx_sentiment_effects(self, sample_prepared_data, random_seed):
        """Test TARCH-X includes sentiment effects."""
        modeler = GARCHModels(sample_prepared_data, 'test')
        results = modeler.estimate_tarch_x(use_individual_events=False, include_sentiment=True)

        if results.convergence and results.sentiment_effects:
            assert isinstance(results.sentiment_effects, dict)

    @pytest.mark.integration
    def test_tarchx_on_actual_data(self, btc_data_sample):
        """Test TARCH-X on actual data with events and sentiment."""
        modeler = GARCHModels(btc_data_sample, 'btc')
        results = modeler.estimate_tarch_x(use_individual_events=False, include_sentiment=True)

        # TARCH-X should converge on actual data
        assert results.convergence, "TARCH-X should converge on actual BTC data"

        # Should have event effects
        assert len(results.event_effects) > 0

        # Check information criteria
        assert not np.isnan(results.aic)
        assert not np.isnan(results.bic)

    @pytest.mark.integration
    def test_tarchx_improves_on_tarch(self, btc_data_sample):
        """Test TARCH-X should have better likelihood than TARCH."""
        modeler = GARCHModels(btc_data_sample, 'btc')

        tarch_results = modeler.estimate_tarch_11()
        tarchx_results = modeler.estimate_tarch_x(use_individual_events=False, include_sentiment=False)

        if tarch_results.convergence and tarchx_results.convergence:
            # TARCH-X adds event parameters, should improve log-likelihood
            assert tarchx_results.log_likelihood >= tarch_results.log_likelihood

    def test_tarchx_fallback_mechanism(self, btc_data_sample):
        """Test TARCH-X fallback to aggregated events if individual events fail."""
        modeler = GARCHModels(btc_data_sample, 'btc')

        # Try with individual events first (might fail with many events)
        # Fallback mechanism should handle this
        results = modeler.estimate_tarch_x(use_individual_events=True, include_sentiment=False)

        # Should either converge or attempt fallback
        assert results is not None

    def test_extract_event_impacts(self, btc_data_sample):
        """Test extraction of event impacts from TARCH-X."""
        modeler = GARCHModels(btc_data_sample, 'btc')
        tarchx_results = modeler.estimate_tarch_x(use_individual_events=False, include_sentiment=False)

        if tarchx_results.convergence:
            # Store results
            modeler.results['TARCH-X'] = tarchx_results

            # Extract event impacts
            impacts = modeler.extract_event_impacts()

            if not impacts.empty:
                assert 'crypto' in impacts.columns
                assert 'event_variable' in impacts.columns
                assert 'coefficient' in impacts.columns
                assert 'p_value' in impacts.columns


class TestModelComparison:
    """Test model comparison and selection."""

    @pytest.mark.integration
    def test_estimate_all_models(self, btc_data_sample):
        """Test estimating all three models in sequence."""
        modeler = GARCHModels(btc_data_sample, 'btc')
        all_results = modeler.estimate_all_models()

        # Should have all three models
        assert 'GARCH(1,1)' in all_results
        assert 'TARCH(1,1)' in all_results
        assert 'TARCH-X' in all_results

        # At least GARCH should converge on real data
        converged = [name for name, result in all_results.items() if result.convergence]
        assert len(converged) >= 1, "At least one model should converge"

    @pytest.mark.integration
    def test_model_selection_aic(self, btc_data_sample):
        """Test model selection based on AIC."""
        modeler = GARCHModels(btc_data_sample, 'btc')
        all_results = modeler.estimate_all_models()

        # Filter to converged models
        converged = {name: result for name, result in all_results.items() if result.convergence}

        if len(converged) > 1:
            # Find best model by AIC
            best_model = min(converged.items(), key=lambda x: x[1].aic)

            # TARCH-X should typically be best if it converged
            if 'TARCH-X' in converged:
                # TARCH-X should have lower or similar AIC to simpler models
                assert converged['TARCH-X'].aic <= converged['GARCH(1,1)'].aic + 10  # Allow some tolerance


class TestModelDiagnostics:
    """Test model diagnostic tests."""

    @pytest.mark.unit
    def test_run_diagnostics_on_converged(self, sample_prepared_data, random_seed):
        """Test running diagnostics on converged model."""
        modeler = GARCHModels(sample_prepared_data, 'test')
        garch_results = modeler.estimate_garch_11()

        if garch_results.convergence:
            diagnostics = modeler.run_diagnostics(garch_results)

            # Should have diagnostic tests
            assert 'ljung_box' in diagnostics or diagnostics.get('error') is not None
            assert 'arch_lm' in diagnostics or diagnostics.get('error') is not None

    @pytest.mark.integration
    def test_diagnostics_on_actual_data(self, btc_data_sample):
        """Test diagnostics on actual BTC data."""
        modeler = GARCHModels(btc_data_sample, 'btc')
        tarch_results = modeler.estimate_tarch_11()

        if tarch_results.convergence:
            diagnostics = modeler.run_diagnostics(tarch_results)

            # Ljung-Box test for autocorrelation
            if 'ljung_box' in diagnostics:
                assert 'statistic' in diagnostics['ljung_box']
                assert 'pvalue' in diagnostics['ljung_box']

            # ARCH-LM test for remaining heteroskedasticity
            if 'arch_lm' in diagnostics:
                assert 'statistic' in diagnostics['arch_lm']
                assert 'pvalue' in diagnostics['arch_lm']

                # TARCH should capture most ARCH effects
                # p-value > 0.05 would indicate no remaining ARCH
                # (though this is not guaranteed on all data)

    def test_diagnostics_on_failed_model(self, sample_prepared_data):
        """Test diagnostics gracefully handles failed models."""
        modeler = GARCHModels(sample_prepared_data, 'test')

        # Create a failed result
        from garch_models import ModelResults
        failed_result = ModelResults(
            model_type='FAILED',
            crypto='test',
            aic=np.nan,
            bic=np.nan,
            log_likelihood=np.nan,
            parameters={},
            std_errors={},
            pvalues={},
            convergence=False,
            iterations=0,
            volatility=pd.Series(),
            residuals=pd.Series()
        )

        diagnostics = modeler.run_diagnostics(failed_result)

        # Should return error indicator
        assert 'error' in diagnostics


class TestParameterStability:
    """Test parameter stability and persistence."""

    @pytest.mark.integration
    def test_persistence_calculation(self, btc_data_sample, assert_valid_garch_params):
        """Test GARCH persistence is calculated correctly."""
        modeler = GARCHModels(btc_data_sample, 'btc')
        garch_results = modeler.estimate_garch_11()

        if garch_results.convergence:
            # Validate parameters
            assert_valid_garch_params(garch_results.parameters)

            # Calculate persistence
            alpha = garch_results.parameters.get('alpha[1]', garch_results.parameters.get('alpha', 0))
            beta = garch_results.parameters.get('beta[1]', garch_results.parameters.get('beta', 0))
            persistence = alpha + beta

            # For crypto, high persistence is common (0.9+)
            assert 0 < persistence < 1, "Model should be stationary"
            assert persistence > 0.5, "Crypto typically has high persistence"

    @pytest.mark.integration
    def test_half_life_calculation(self, btc_data_sample):
        """Test half-life of volatility shocks."""
        modeler = GARCHModels(btc_data_sample, 'btc')
        garch_results = modeler.estimate_garch_11()

        if garch_results.convergence:
            alpha = garch_results.parameters.get('alpha[1]', garch_results.parameters.get('alpha', 0))
            beta = garch_results.parameters.get('beta[1]', garch_results.parameters.get('beta', 0))
            persistence = alpha + beta

            if 0 < persistence < 1:
                half_life = -np.log(0.5) / np.log(persistence)

                # Crypto half-life typically 10-50 days
                assert 1 < half_life < 200, f"Half-life {half_life} seems unreasonable"


class TestConvenienceFunctions:
    """Test convenience functions for model estimation."""

    @pytest.mark.integration
    def test_estimate_models_for_crypto(self, btc_data_sample):
        """Test convenience function for estimating all models."""
        results = estimate_models_for_crypto('btc', btc_data_sample)

        assert isinstance(results, dict)
        assert 'GARCH(1,1)' in results
        assert 'TARCH(1,1)' in results
        assert 'TARCH-X' in results


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.edge_case
    def test_very_short_series(self):
        """Test model handles very short time series."""
        # Create very short series
        short_returns = pd.Series(
            np.random.normal(0, 2, 50),
            index=pd.date_range('2020-01-01', periods=50, tz='UTC'),
            name='returns_winsorized'
        )

        data = pd.DataFrame({'returns_winsorized': short_returns})
        modeler = GARCHModels(data, 'test')

        # Should not crash, but may not converge
        try:
            results = modeler.estimate_garch_11()
            assert results is not None
        except Exception as e:
            pytest.fail(f"Should handle short series gracefully: {e}")

    @pytest.mark.edge_case
    def test_constant_returns(self):
        """Test model handles near-constant returns."""
        # Create near-constant series
        constant_returns = pd.Series(
            0.01 + np.random.normal(0, 0.001, 500),
            index=pd.date_range('2020-01-01', periods=500, tz='UTC'),
            name='returns_winsorized'
        )

        data = pd.DataFrame({'returns_winsorized': constant_returns})
        modeler = GARCHModels(data, 'test')

        # Model should handle this (may not converge)
        results = modeler.estimate_garch_11()
        assert results is not None

    @pytest.mark.edge_case
    def test_high_volatility_regime(self):
        """Test model handles high volatility periods."""
        np.random.seed(42)

        # Create series with very high volatility
        high_vol_returns = pd.Series(
            np.random.normal(0, 10, 500),  # Very high std
            index=pd.date_range('2020-01-01', periods=500, tz='UTC'),
            name='returns_winsorized'
        )

        data = pd.DataFrame({'returns_winsorized': high_vol_returns})
        modeler = GARCHModels(data, 'test')

        results = modeler.estimate_garch_11()
        assert results is not None

        # If converged, omega should be large
        if results.convergence:
            assert results.parameters.get('omega', 0) > 0
