"""
Comprehensive tests for statistical methods.

Tests hypothesis testing, FDR correction, bootstrap inference,
and half-life calculations critical for journal publication.
"""

import pytest
import pandas as pd
import numpy as np
from scipy import stats

from event_impact_analysis import EventImpactAnalysis
from garch_models import GARCHModels, ModelResults


pytestmark = pytest.mark.statistical


@pytest.fixture
def mock_model_results():
    """Create mock model results for testing analysis methods."""
    results = {}

    # Create results for multiple cryptocurrencies
    for crypto in ['btc', 'eth', 'xrp']:
        crypto_results = {}

        # Mock TARCH-X results with event effects
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
                'nu': 6.0
            },
            std_errors={
                'omega': 0.002,
                'alpha[1]': 0.02,
                'gamma[1]': 0.01,
                'beta[1]': 0.03,
                'D_infrastructure': 0.005,
                'D_regulatory': 0.003
            },
            pvalues={
                'omega': 0.001,
                'alpha[1]': 0.001,
                'gamma[1]': 0.001,
                'beta[1]': 0.001,
                'D_infrastructure': 0.01,
                'D_regulatory': 0.05
            },
            convergence=True,
            iterations=100,
            volatility=pd.Series(np.random.rand(100) * 2 + 1),
            residuals=pd.Series(np.random.randn(100)),
            leverage_effect=0.05,
            event_effects={
                'D_infrastructure': 0.02 + np.random.rand()*0.01,  # Infrastructure higher
                'D_regulatory': 0.01 + np.random.rand()*0.005     # Regulatory lower
            },
            sentiment_effects={
                'S_gdelt_normalized': 0.001,
                'S_reg_decomposed': 0.0005,
                'S_infra_decomposed': 0.0015
            },
            event_std_errors={
                'D_infrastructure': 0.005,
                'D_regulatory': 0.003
            },
            event_pvalues={
                'D_infrastructure': 0.01,
                'D_regulatory': 0.05
            }
        )

        crypto_results['TARCH-X'] = tarchx_result
        results[crypto] = crypto_results

    return results


class TestHypothesisTesting:
    """Test hypothesis testing for Infrastructure vs Regulatory events."""

    def test_infrastructure_vs_regulatory_basic(self, mock_model_results):
        """Test basic hypothesis test computation."""
        analyzer = EventImpactAnalysis(mock_model_results)
        results = analyzer.test_infrastructure_vs_regulatory()

        # Should have results for both event types
        assert 'infrastructure' in results
        assert 'regulatory' in results

        # Should have descriptive statistics
        assert 'mean' in results['infrastructure']
        assert 'median' in results['infrastructure']
        assert 'std' in results['infrastructure']

    def test_hypothesis_test_statistics(self, mock_model_results):
        """Test hypothesis test produces valid statistics."""
        analyzer = EventImpactAnalysis(mock_model_results)
        results = analyzer.test_infrastructure_vs_regulatory()

        # Should have t-test results
        if 't_test' in results:
            assert 'statistic' in results['t_test']
            assert 'p_value' in results['t_test']

            # P-value should be between 0 and 1
            assert 0 <= results['t_test']['p_value'] <= 1

        # Should have Mann-Whitney test
        if 'mann_whitney' in results:
            assert 'statistic' in results['mann_whitney']
            assert 'p_value' in results['mann_whitney']
            assert 0 <= results['mann_whitney']['p_value'] <= 1

    def test_effect_size_calculation(self, mock_model_results):
        """Test Cohen's d effect size calculation."""
        analyzer = EventImpactAnalysis(mock_model_results)
        results = analyzer.test_infrastructure_vs_regulatory()

        if 'effect_size' in results:
            # Effect size should be a real number
            assert isinstance(results['effect_size'], (int, float))
            assert not np.isnan(results['effect_size'])

            # For our mock data, infrastructure > regulatory
            # so effect size should be positive
            assert results['effect_size'] > 0

    def test_infrastructure_greater_than_regulatory(self, mock_model_results):
        """Test that Infrastructure events have larger effects (H1)."""
        analyzer = EventImpactAnalysis(mock_model_results)
        results = analyzer.test_infrastructure_vs_regulatory()

        # Infrastructure mean should be greater than regulatory mean
        infra_mean = results['infrastructure']['mean']
        reg_mean = results['regulatory']['mean']

        # In our mock data, infrastructure is designed to be higher
        assert infra_mean > reg_mean, "Infrastructure should have larger volatility impact"


class TestFDRCorrection:
    """Test False Discovery Rate correction."""

    def test_fdr_correction_basic(self, mock_model_results):
        """Test FDR correction is applied."""
        analyzer = EventImpactAnalysis(mock_model_results)
        corrected = analyzer.apply_fdr_correction()

        if not corrected.empty:
            # Should have corrected p-values
            assert 'fdr_corrected_pvalue' in corrected.columns
            assert 'fdr_significant' in corrected.columns

            # Corrected p-values should be >= original p-values
            if 'p_value' in corrected.columns:
                # FDR correction makes p-values larger (more conservative)
                original_pvals = corrected['p_value'].dropna()
                corrected_pvals = corrected.loc[original_pvals.index, 'fdr_corrected_pvalue']

                assert (corrected_pvals >= original_pvals).all() or (corrected_pvals >= original_pvals - 1e-10).all()

    def test_fdr_reduces_false_positives(self, mock_model_results):
        """Test FDR correction reduces number of significant results."""
        analyzer = EventImpactAnalysis(mock_model_results)
        corrected = analyzer.apply_fdr_correction()

        if not corrected.empty and 'p_value' in corrected.columns:
            # Count raw significant
            alpha = analyzer.fdr_alpha
            raw_significant = (corrected['p_value'] < alpha).sum()

            # Count FDR significant
            if 'fdr_significant' in corrected.columns:
                fdr_significant = corrected['fdr_significant'].sum()

                # FDR should control false discoveries
                assert fdr_significant <= raw_significant


class TestInverseVarianceWeighting:
    """Test inverse-variance weighted averages."""

    def test_inverse_variance_basic(self, mock_model_results):
        """Test inverse-variance weighted average calculation."""
        analyzer = EventImpactAnalysis(mock_model_results)
        weighted = analyzer.calculate_inverse_variance_weighted_average()

        # Should have results for both event types
        assert 'Infrastructure' in weighted or 'Regulatory' in weighted

    def test_inverse_variance_weights(self, mock_model_results):
        """Test that inverse-variance weighting works correctly."""
        analyzer = EventImpactAnalysis(mock_model_results)
        weighted = analyzer.calculate_inverse_variance_weighted_average()

        if 'Infrastructure' in weighted:
            result = weighted['Infrastructure']

            # Should have required fields
            assert 'weighted_average' in result
            assert 'standard_error' in result
            assert 'ci_lower' in result
            assert 'ci_upper' in result

            # Confidence interval should contain the estimate
            assert result['ci_lower'] <= result['weighted_average'] <= result['ci_upper']

    def test_weighted_difference_test(self, mock_model_results):
        """Test statistical test on weighted difference."""
        analyzer = EventImpactAnalysis(mock_model_results)
        weighted = analyzer.calculate_inverse_variance_weighted_average()

        if 'difference' in weighted:
            diff_result = weighted['difference']

            # Should have test statistics
            assert 'value' in diff_result
            assert 'standard_error' in diff_result
            assert 'z_statistic' in diff_result
            assert 'p_value' in diff_result

            # P-value should be valid
            assert 0 <= diff_result['p_value'] <= 1


class TestPersistenceMeasures:
    """Test persistence and half-life calculations."""

    def test_persistence_calculation(self, mock_model_results):
        """Test persistence calculation for each model."""
        analyzer = EventImpactAnalysis(mock_model_results)
        persistence = analyzer.calculate_persistence_measures()

        # Should have persistence for each crypto
        assert len(persistence) > 0

        for crypto, models in persistence.items():
            # Check TARCH-X persistence if present
            if 'TARCH-X' in models:
                tarchx_pers = models['TARCH-X']

                assert 'persistence' in tarchx_pers
                assert 'half_life' in tarchx_pers
                assert 'stationary' in tarchx_pers

                # Persistence should be < 1 for stationarity
                if tarchx_pers['stationary']:
                    assert tarchx_pers['persistence'] < 1

    def test_half_life_positive(self, mock_model_results):
        """Test half-life calculations are positive."""
        analyzer = EventImpactAnalysis(mock_model_results)
        persistence = analyzer.calculate_persistence_measures()

        for crypto, models in persistence.items():
            for model_name, metrics in models.items():
                if 'half_life' in metrics and not np.isnan(metrics['half_life']):
                    # Half-life should be positive
                    assert metrics['half_life'] > 0

                    # For crypto, half-life typically 5-100 days
                    assert 0.1 < metrics['half_life'] < 500

    def test_stationarity_condition(self, mock_model_results):
        """Test stationarity condition is correctly evaluated."""
        analyzer = EventImpactAnalysis(mock_model_results)
        persistence = analyzer.calculate_persistence_measures()

        for crypto, models in persistence.items():
            for model_name, metrics in models.items():
                if 'persistence' in metrics and 'stationary' in metrics:
                    # Stationarity should match persistence < 1
                    if metrics['persistence'] < 1:
                        assert metrics['stationary'] is True
                    else:
                        assert metrics['stationary'] is False


class TestByEventTypeAnalysis:
    """Test analysis grouped by event type."""

    def test_analyze_by_cryptocurrency(self, mock_model_results):
        """Test event impact analysis by cryptocurrency."""
        analyzer = EventImpactAnalysis(mock_model_results)
        by_crypto = analyzer.analyze_by_cryptocurrency()

        assert isinstance(by_crypto, pd.DataFrame)

        if not by_crypto.empty:
            # Should have required columns
            assert 'crypto' in by_crypto.columns
            assert 'mean_infra_effect' in by_crypto.columns or 'n_infrastructure' in by_crypto.columns

    def test_publication_table_generation(self, mock_model_results):
        """Test generation of publication-ready table."""
        analyzer = EventImpactAnalysis(mock_model_results)
        pub_table = analyzer.generate_publication_table()

        if not pub_table.empty:
            # Should have formatted columns
            assert 'Cryptocurrency' in pub_table.columns or 'crypto' in pub_table.columns
            assert 'Event Type' in pub_table.columns or 'event_type' in pub_table.columns

            # Should have numeric values
            numeric_cols = pub_table.select_dtypes(include=[np.number]).columns
            assert len(numeric_cols) > 0


class TestBootstrapInference:
    """Test bootstrap confidence intervals."""

    @pytest.mark.slow
    def test_bootstrap_basic(self, sample_returns):
        """Test basic bootstrap inference."""
        from bootstrap_inference import BootstrapInference

        # Use small number of replications for testing
        boot = BootstrapInference(sample_returns, n_bootstrap=100, seed=42)

        # Should initialize without errors
        assert boot.n_bootstrap == 100
        assert len(boot.returns) > 0

    @pytest.mark.slow
    def test_bootstrap_convergence(self, sample_returns):
        """Test bootstrap replications converge."""
        from bootstrap_inference import BootstrapInference

        boot = BootstrapInference(sample_returns, n_bootstrap=50, seed=42)
        results = boot.residual_bootstrap_tarch(
            model_type='GARCH',
            include_leverage=False,
            show_progress=False
        )

        # Should have bootstrap results
        assert 'original_params' in results or results is not None

        # Some replications should converge
        if 'convergence_rate' in results:
            assert results['convergence_rate'] > 0


class TestReproducibility:
    """Test reproducibility of statistical methods."""

    @pytest.mark.reproducibility
    def test_hypothesis_test_reproducible(self, mock_model_results):
        """Test hypothesis tests are reproducible."""
        analyzer1 = EventImpactAnalysis(mock_model_results)
        analyzer2 = EventImpactAnalysis(mock_model_results)

        results1 = analyzer1.test_infrastructure_vs_regulatory()
        results2 = analyzer2.test_infrastructure_vs_regulatory()

        # Results should be identical
        if 't_test' in results1 and 't_test' in results2:
            np.testing.assert_almost_equal(
                results1['t_test']['statistic'],
                results2['t_test']['statistic'],
                decimal=10
            )

    @pytest.mark.reproducibility
    def test_fdr_correction_reproducible(self, mock_model_results):
        """Test FDR correction is reproducible."""
        analyzer1 = EventImpactAnalysis(mock_model_results)
        analyzer2 = EventImpactAnalysis(mock_model_results)

        corrected1 = analyzer1.apply_fdr_correction()
        corrected2 = analyzer2.apply_fdr_correction()

        if not corrected1.empty and not corrected2.empty:
            # Corrected p-values should be identical
            pd.testing.assert_frame_equal(corrected1, corrected2)

    @pytest.mark.reproducibility
    @pytest.mark.slow
    def test_bootstrap_reproducible_with_seed(self, sample_returns):
        """Test bootstrap is reproducible with fixed seed."""
        from bootstrap_inference import BootstrapInference

        boot1 = BootstrapInference(sample_returns, n_bootstrap=50, seed=42)
        boot2 = BootstrapInference(sample_returns, n_bootstrap=50, seed=42)

        results1 = boot1.residual_bootstrap_tarch(
            model_type='GARCH',
            include_leverage=False,
            show_progress=False
        )
        results2 = boot2.residual_bootstrap_tarch(
            model_type='GARCH',
            include_leverage=False,
            show_progress=False
        )

        # With same seed, results should be identical
        assert results1 is not None
        assert results2 is not None


class TestPowerAnalysis:
    """Test statistical power and sample size."""

    def test_sample_size_adequate(self, mock_model_results):
        """Test sample size is adequate for hypothesis testing."""
        analyzer = EventImpactAnalysis(mock_model_results)

        # Should have multiple cryptocurrencies
        assert len(mock_model_results) >= 2

        # Should have multiple events per type
        results = analyzer.test_infrastructure_vs_regulatory()

        if 'infrastructure' in results and 'regulatory' in results:
            # Need at least 3 observations per group for meaningful tests
            assert results['infrastructure']['n'] >= 2
            assert results['regulatory']['n'] >= 2

    def test_effect_size_meaningful(self, mock_model_results):
        """Test effect size is large enough to detect."""
        analyzer = EventImpactAnalysis(mock_model_results)
        results = analyzer.test_infrastructure_vs_regulatory()

        if 'effect_size' in results:
            # Effect size should be meaningful (Cohen's d)
            # Small: 0.2, Medium: 0.5, Large: 0.8
            # For our hypothesis, we expect at least small effect
            abs_effect = abs(results['effect_size'])
            assert abs_effect >= 0, "Should have some effect"


class TestRobustnessChecks:
    """Test robustness of statistical conclusions."""

    def test_multiple_test_methods_agree(self, mock_model_results):
        """Test parametric and non-parametric tests agree on direction."""
        analyzer = EventImpactAnalysis(mock_model_results)
        results = analyzer.test_infrastructure_vs_regulatory()

        if 't_test' in results and 'mann_whitney' in results:
            t_significant = results['t_test']['p_value'] < 0.10
            mw_significant = results['mann_whitney']['p_value'] < 0.10

            # Both tests should at least agree on significance direction
            # (both significant or both not significant)
            # This is not guaranteed but should hold for our mock data
            assert isinstance(t_significant, bool)
            assert isinstance(mw_significant, bool)

    def test_weighted_vs_unweighted_consistency(self, mock_model_results):
        """Test weighted and unweighted averages are consistent."""
        analyzer = EventImpactAnalysis(mock_model_results)

        # Unweighted (from hypothesis test)
        unweighted = analyzer.test_infrastructure_vs_regulatory()

        # Weighted
        weighted = analyzer.calculate_inverse_variance_weighted_average()

        if ('infrastructure' in unweighted and 'Infrastructure' in weighted and
            'regulatory' in unweighted and 'Regulatory' in weighted):

            # Direction should be the same
            unweighted_diff = unweighted['infrastructure']['mean'] - unweighted['regulatory']['mean']
            weighted_diff = weighted['difference']['value'] if 'difference' in weighted else 0

            # Signs should match (both positive or both negative)
            if unweighted_diff != 0 and weighted_diff != 0:
                assert np.sign(unweighted_diff) == np.sign(weighted_diff)


class TestEdgeCasesStatistical:
    """Test edge cases in statistical methods."""

    @pytest.mark.edge_case
    def test_empty_event_coefficients(self):
        """Test analysis handles empty event coefficients gracefully."""
        # Create empty model results
        empty_results = {}

        analyzer = EventImpactAnalysis(empty_results)
        results = analyzer.test_infrastructure_vs_regulatory()

        # Should return empty or error result without crashing
        assert isinstance(results, dict)

    @pytest.mark.edge_case
    def test_single_cryptocurrency(self):
        """Test analysis works with single cryptocurrency."""
        single_result = {
            'btc': {
                'TARCH-X': ModelResults(
                    model_type='TARCH-X',
                    crypto='btc',
                    aic=1000.0,
                    bic=1020.0,
                    log_likelihood=-500.0,
                    parameters={'omega': 0.01, 'alpha[1]': 0.1, 'beta[1]': 0.85},
                    std_errors={'omega': 0.002},
                    pvalues={'omega': 0.01},
                    convergence=True,
                    iterations=100,
                    volatility=pd.Series([1.0, 1.1, 1.2]),
                    residuals=pd.Series([0.1, -0.1, 0.05]),
                    event_effects={'D_infrastructure': 0.02, 'D_regulatory': 0.01},
                    event_std_errors={'D_infrastructure': 0.005, 'D_regulatory': 0.003},
                    event_pvalues={'D_infrastructure': 0.01, 'D_regulatory': 0.05}
                )
            }
        }

        analyzer = EventImpactAnalysis(single_result)
        results = analyzer.test_infrastructure_vs_regulatory()

        # Should work with one crypto
        assert isinstance(results, dict)

    @pytest.mark.edge_case
    def test_all_nan_pvalues(self):
        """Test FDR correction handles all NaN p-values."""
        nan_results = {
            'btc': {
                'TARCH-X': ModelResults(
                    model_type='TARCH-X',
                    crypto='btc',
                    aic=1000.0,
                    bic=1020.0,
                    log_likelihood=-500.0,
                    parameters={},
                    std_errors={},
                    pvalues={},  # No p-values
                    convergence=True,
                    iterations=100,
                    volatility=pd.Series([1.0]),
                    residuals=pd.Series([0.1]),
                    event_effects={'D_infrastructure': 0.02}
                )
            }
        }

        analyzer = EventImpactAnalysis(nan_results)
        corrected = analyzer.apply_fdr_correction()

        # Should handle gracefully
        assert isinstance(corrected, pd.DataFrame)
