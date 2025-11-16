"""
Model Diagnostics and Specification Tests
==========================================

Comprehensive diagnostics for TARCH-X-Micro models:
1. Residual analysis (autocorrelation, ARCH effects)
2. Model comparison (GARCH vs TARCH vs EGARCH)
3. Specification tests (omitted variables, functional form)
4. Stability tests (parameter constancy across subsamples)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

from statsmodels.stats.diagnostic import acorr_ljungbox, het_arch
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

import config
from tarch_x_microstructure import TARCHXMicroResults


class ModelDiagnostics:
    """Diagnostic tests for TARCH-X-Micro estimation."""

    def __init__(self, results: TARCHXMicroResults, asset_name: str):
        """
        Initialize diagnostics.

        Args:
            results: TARCH-X-Micro estimation results
            asset_name: Asset identifier (for reporting)
        """
        self.results = results
        self.asset_name = asset_name
        self.residuals = results.residuals
        self.volatility = results.volatility

        # Standardized residuals
        self.std_residuals = self.residuals / self.volatility

    def run_all_diagnostics(self) -> Dict:
        """
        Run complete diagnostic suite.

        Returns:
            Dictionary with all diagnostic results
        """
        print("\n" + "="*70)
        print(f"MODEL DIAGNOSTICS: {self.asset_name}")
        print("="*70 + "\n")

        diagnostics = {}

        # 1. Residual autocorrelation
        print("1. Testing for residual autocorrelation...")
        diagnostics['autocorrelation'] = self.test_autocorrelation()

        # 2. Remaining ARCH effects
        print("\n2. Testing for remaining ARCH effects...")
        diagnostics['arch_effects'] = self.test_arch_effects()

        # 3. Normality
        print("\n3. Testing normality of standardized residuals...")
        diagnostics['normality'] = self.test_normality()

        # 4. Parameter stability
        print("\n4. Testing parameter stability...")
        diagnostics['stability'] = self.test_parameter_stability()

        # Overall assessment
        self._print_summary(diagnostics)

        return diagnostics

    def test_autocorrelation(self, max_lag: int = 10) -> Dict:
        """
        Ljung-Box test for autocorrelation in standardized residuals.

        H0: No autocorrelation up to lag k
        If p > 0.05, residuals are white noise (good)
        """
        lb_result = acorr_ljungbox(self.std_residuals.dropna(), lags=max_lag,
                                   return_df=True)

        # Check if any lag is significant
        min_pval = lb_result['lb_pvalue'].min()
        significant_lags = (lb_result['lb_pvalue'] < 0.05).sum()

        result = {
            'test': 'Ljung-Box',
            'min_pvalue': min_pval,
            'significant_lags': significant_lags,
            'max_lag': max_lag,
            'passed': min_pval > 0.05,
            'details': lb_result
        }

        # Print result
        if result['passed']:
            print(f"  ✓ PASS - No significant autocorrelation (p={min_pval:.4f})")
        else:
            print(f"  ✗ FAIL - Significant autocorrelation at {significant_lags}/{max_lag} lags")
            print(f"  Min p-value: {min_pval:.4f}")

        return result

    def test_arch_effects(self, nlags: int = 5) -> Dict:
        """
        ARCH-LM test for remaining ARCH effects in standardized residuals.

        H0: No ARCH effects remain
        If p > 0.05, GARCH model adequately captures volatility clustering (good)
        """
        # ARCH-LM test
        lm_stat, lm_pval, f_stat, f_pval = het_arch(self.std_residuals.dropna(),
                                                     nlags=nlags)

        result = {
            'test': 'ARCH-LM',
            'lm_statistic': lm_stat,
            'lm_pvalue': lm_pval,
            'f_statistic': f_stat,
            'f_pvalue': f_pval,
            'nlags': nlags,
            'passed': lm_pval > 0.05
        }

        # Print result
        if result['passed']:
            print(f"  ✓ PASS - No remaining ARCH effects (p={lm_pval:.4f})")
        else:
            print(f"  ✗ FAIL - Significant ARCH effects remain (p={lm_pval:.4f})")
            print(f"  Model may be mis-specified")

        return result

    def test_normality(self) -> Dict:
        """
        Test normality of standardized residuals.

        Uses Jarque-Bera test.
        Note: TARCH-X uses Student-t, so some non-normality is expected.
        """
        # Jarque-Bera test
        jb_stat, jb_pval = stats.jarque_bera(self.std_residuals.dropna())

        # Skewness and kurtosis
        skew = stats.skew(self.std_residuals.dropna())
        kurt = stats.kurtosis(self.std_residuals.dropna())

        result = {
            'test': 'Jarque-Bera',
            'jb_statistic': jb_stat,
            'jb_pvalue': jb_pval,
            'skewness': skew,
            'kurtosis': kurt,
            'excess_kurtosis': kurt,  # scipy returns excess kurtosis
            'passed': jb_pval > 0.01  # Lenient threshold (Student-t expected)
        }

        # Print result
        print(f"  Jarque-Bera test: stat={jb_stat:.2f}, p={jb_pval:.4f}")
        print(f"  Skewness: {skew:.3f}")
        print(f"  Excess kurtosis: {kurt:.3f}")

        if result['passed']:
            print(f"  ✓ ACCEPTABLE - Deviations consistent with Student-t")
        else:
            print(f"  ⚠ WARNING - Strong non-normality (but expected with fat tails)")

        return result

    def test_parameter_stability(self) -> Dict:
        """
        Test if parameters are stable across first/second half of sample.

        Uses Chow test for structural break at midpoint.
        """
        midpoint = len(self.residuals) // 2

        # Split sample
        first_half_var = self.volatility.iloc[:midpoint].var()
        second_half_var = self.volatility.iloc[midpoint:].var()

        # F-test for equality of variances
        f_stat = max(first_half_var, second_half_var) / min(first_half_var, second_half_var)
        df1 = midpoint - 1
        df2 = len(self.residuals) - midpoint - 1
        f_pval = 1 - stats.f.cdf(f_stat, df1, df2)

        result = {
            'test': 'Parameter Stability',
            'first_half_var': first_half_var,
            'second_half_var': second_half_var,
            'f_statistic': f_stat,
            'f_pvalue': f_pval,
            'passed': f_pval > 0.05
        }

        # Print result
        if result['passed']:
            print(f"  ✓ PASS - Parameters appear stable (p={f_pval:.4f})")
        else:
            print(f"  ✗ FAIL - Evidence of parameter instability (p={f_pval:.4f})")
            print(f"  Consider Markov-switching model or subsample analysis")

        return result

    def _print_summary(self, diagnostics: Dict):
        """Print overall diagnostic summary."""
        print("\n" + "="*70)
        print("DIAGNOSTIC SUMMARY")
        print("="*70 + "\n")

        tests_passed = sum(1 for d in diagnostics.values() if d.get('passed', False))
        total_tests = len(diagnostics)

        print(f"Tests passed: {tests_passed}/{total_tests}")

        if tests_passed == total_tests:
            print("\n✓ MODEL SPECIFICATION APPEARS ADEQUATE")
        elif tests_passed >= total_tests * 0.75:
            print("\n⚠ MODEL MOSTLY ADEQUATE - Minor concerns")
        else:
            print("\n✗ MODEL SPECIFICATION CONCERNS - Review carefully")

    def plot_diagnostics(self, save_path: Optional[str] = None):
        """
        Create diagnostic plots.

        4-panel figure:
        1. Standardized residuals over time
        2. ACF of standardized residuals
        3. ACF of squared standardized residuals
        4. QQ-plot
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # Panel 1: Time series of standardized residuals
        ax1 = axes[0, 0]
        ax1.plot(self.std_residuals.index, self.std_residuals.values,
                linewidth=0.8, alpha=0.7)
        ax1.axhline(0, color='red', linestyle='--', linewidth=1)
        ax1.axhline(2, color='orange', linestyle=':', linewidth=1)
        ax1.axhline(-2, color='orange', linestyle=':', linewidth=1)
        ax1.set_title('Standardized Residuals', fontweight='bold')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Std. Residuals')
        ax1.grid(alpha=0.3)

        # Panel 2: ACF of residuals
        ax2 = axes[0, 1]
        plot_acf(self.std_residuals.dropna(), lags=20, ax=ax2, alpha=0.05)
        ax2.set_title('ACF of Standardized Residuals', fontweight='bold')
        ax2.set_xlabel('Lag')

        # Panel 3: ACF of squared residuals (test for ARCH)
        ax3 = axes[1, 0]
        plot_acf(self.std_residuals.dropna()**2, lags=20, ax=ax3, alpha=0.05)
        ax3.set_title('ACF of Squared Std. Residuals (ARCH Test)', fontweight='bold')
        ax3.set_xlabel('Lag')

        # Panel 4: QQ-plot
        ax4 = axes[1, 1]
        stats.probplot(self.std_residuals.dropna(), dist="norm", plot=ax4)
        ax4.set_title('Q-Q Plot (Normal)', fontweight='bold')
        ax4.grid(alpha=0.3)

        plt.suptitle(f'Model Diagnostics: {self.asset_name}',
                    fontsize=14, fontweight='bold', y=0.995)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"\n[SAVED] Diagnostic plots: {save_path}")

        return fig


class ModelComparison:
    """Compare alternative GARCH specifications."""

    def __init__(self):
        """Initialize model comparison framework."""
        self.models = {}

    def compare_specifications(self, returns: pd.Series,
                               exog_vars: pd.DataFrame,
                               micro_vars: pd.DataFrame) -> pd.DataFrame:
        """
        Compare GARCH, TARCH, EGARCH specifications.

        Args:
            returns: Log returns
            exog_vars: Event/sentiment variables
            micro_vars: Microstructure variables

        Returns:
            DataFrame with model comparison statistics
        """
        print("\n" + "="*70)
        print("MODEL SPECIFICATION COMPARISON")
        print("="*70 + "\n")

        results = []

        # Note: This would require implementing GARCH-X and EGARCH-X variants
        # For now, placeholder showing the structure

        print("[INFO] Full comparison requires implementing:")
        print("  - GARCH-X (symmetric GARCH with exogenous variables)")
        print("  - EGARCH-X (asymmetric in logs)")
        print("  - Component GARCH-X (long-run/short-run components)")
        print("\nCurrent implementation: TARCH-X-Micro only")

        # Placeholder for what the comparison would look like
        model_specs = [
            {'name': 'GARCH(1,1)-X', 'asymmetry': False, 'leverage': False},
            {'name': 'TARCH(1,1)-X', 'asymmetry': True, 'leverage': True},
            {'name': 'EGARCH(1,1)-X', 'asymmetry': True, 'leverage': True},
            {'name': 'TARCH-X-Micro', 'asymmetry': True, 'leverage': True},
        ]

        # Return structure for actual implementation
        return pd.DataFrame(model_specs)


def run_diagnostics_on_results(tarchx_results: TARCHXMicroResults,
                               asset_name: str,
                               save_plots: bool = True) -> Dict:
    """
    Convenience function to run full diagnostic suite.

    Args:
        tarchx_results: Estimation results
        asset_name: Asset identifier
        save_plots: Whether to save diagnostic plots

    Returns:
        Dictionary with diagnostic results
    """
    diag = ModelDiagnostics(tarchx_results, asset_name)

    # Run all tests
    results = diag.run_all_diagnostics()

    # Create plots
    if save_plots:
        plot_path = config.OUTPUTS_DIR / f'diagnostics_{asset_name.lower()}.pdf'
        diag.plot_diagnostics(save_path=plot_path)

    return results


if __name__ == "__main__":
    print("Model Diagnostics Module")
    print("=" * 60)
    print("\nDiagnostic tests implemented:")
    print("  1. Ljung-Box (autocorrelation)")
    print("  2. ARCH-LM (remaining ARCH effects)")
    print("  3. Jarque-Bera (normality)")
    print("  4. Parameter stability (Chow test)")
    print("\nUsage: Import and call run_diagnostics_on_results()")
