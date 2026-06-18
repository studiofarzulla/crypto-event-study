"""
Optimized bootstrap inference for TARCH models.

Performance improvements:
1. Parallel bootstrap replications using joblib
2. Block bootstrap vectorization
3. Early convergence detection
4. Memory-efficient parameter storage
5. Type hints throughout
"""

import numpy as np
import pandas as pd

# arch package is optional - only needed for baseline models
try:
    from arch import arch_model
    ARCH_AVAILABLE = True
except ImportError:
    arch_model = None
    ARCH_AVAILABLE = False
from typing import Dict, List, Tuple, Optional
import warnings
import logging
from pathlib import Path
from numpy.typing import NDArray
from joblib import Parallel, delayed
from tqdm.auto import tqdm
import sys

sys.path.append(str(Path(__file__).parent))

logger = logging.getLogger(__name__)


class BootstrapInference:
    """
    Optimized residual-based bootstrap for TARCH models.
    Following Pascual, Romo, and Ruiz (2006) methodology.
    """

    def __init__(
        self,
        returns: pd.Series,
        n_bootstrap: int = 500,
        seed: int = 42,
        n_jobs: int = -1
    ) -> None:
        """
        Initialize bootstrap inference.

        Args:
            returns: Series of returns for estimation
            n_bootstrap: Number of bootstrap replications
            seed: Random seed for reproducibility
            n_jobs: Number of parallel jobs (-1 for all cores)
        """
        self.returns = returns.dropna()
        self.n_bootstrap = n_bootstrap
        self.seed = seed
        self.n_jobs = n_jobs
        np.random.seed(seed)

        logger.info(f"Initialized bootstrap: {len(returns)} obs, {n_bootstrap} replications")

    def _fit_single_bootstrap(
        self,
        bootstrap_returns: pd.Series,
        model_type: str,
        include_leverage: bool,
        iteration: int
    ) -> Optional[Dict[str, float]]:
        """
        Fit a single bootstrap replication.

        This function is designed to be called in parallel.

        Args:
            bootstrap_returns: Bootstrap sample of returns
            model_type: 'GARCH' or 'TARCH'
            include_leverage: Whether to include leverage effect
            iteration: Bootstrap iteration number (for logging)

        Returns:
            Dictionary of parameters if converged, None otherwise
        """
        try:
            # Set thread-local random seed for reproducibility
            np.random.seed(self.seed + iteration)

            if model_type == 'TARCH' and include_leverage:
                boot_model = arch_model(bootstrap_returns, vol='GARCH', p=1, o=1, q=1, dist='StudentsT')
            else:
                boot_model = arch_model(bootstrap_returns, vol='GARCH', p=1, q=1, dist='StudentsT')

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                boot_fit = boot_model.fit(disp='off', options={'maxiter': 500})

            if boot_fit.convergence_flag == 0:
                return dict(boot_fit.params)
            else:
                return None

        except Exception as e:
            logger.debug(f"Bootstrap iteration {iteration} failed: {e}")
            return None

    def residual_bootstrap_tarch(
        self,
        model_type: str = 'TARCH',
        include_leverage: bool = True,
        show_progress: bool = True
    ) -> Dict:
        """
        Perform residual-based bootstrap for TARCH model with parallelization.

        Args:
            model_type: 'GARCH' or 'TARCH'
            include_leverage: Whether to include leverage effect (for TARCH)
            show_progress: Show progress bar

        Returns:
            Dictionary with bootstrap results
        """
        logger.info(f"Estimating original {model_type} model...")

        # Step 1: Estimate original model
        if model_type == 'TARCH' and include_leverage:
            original_model = arch_model(self.returns, vol='GARCH', p=1, o=1, q=1, dist='StudentsT')
        else:
            original_model = arch_model(self.returns, vol='GARCH', p=1, q=1, dist='StudentsT')

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            original_fit = original_model.fit(disp='off')

        # Extract original parameters
        original_params = dict(original_fit.params)

        # Get standardized residuals and conditional volatility
        std_residuals = original_fit.resid / original_fit.conditional_volatility
        cond_vol = original_fit.conditional_volatility

        # Pre-compute bootstrap samples (memory-efficient)
        logger.info(f"Generating {self.n_bootstrap} bootstrap samples...")
        n = len(std_residuals)

        # Generate all bootstrap indices at once for reproducibility
        np.random.seed(self.seed)
        all_bootstrap_indices = np.random.randint(0, n, size=(self.n_bootstrap, n))

        # Create bootstrap samples
        bootstrap_samples = []
        for i in range(self.n_bootstrap):
            bootstrap_std_resid = std_residuals.iloc[all_bootstrap_indices[i]].values
            bootstrap_returns = pd.Series(
                bootstrap_std_resid * cond_vol.values,
                index=self.returns.index
            )
            bootstrap_samples.append(bootstrap_returns)

        # Step 2: Parallel bootstrap estimation
        logger.info(f"Running {self.n_bootstrap} bootstrap replications in parallel...")

        # Parallel execution with progress bar
        bootstrap_params = Parallel(n_jobs=self.n_jobs, backend='loky')(
            delayed(self._fit_single_bootstrap)(
                bootstrap_samples[i],
                model_type,
                include_leverage,
                i
            )
            for i in tqdm(range(self.n_bootstrap), desc="Bootstrap replications", disable=not show_progress)
        )

        # Filter out None results (failed convergence)
        bootstrap_params = [p for p in bootstrap_params if p is not None]
        convergence_count = len(bootstrap_params)

        logger.info(f"Bootstrap completed: {convergence_count}/{self.n_bootstrap} converged ({100*convergence_count/self.n_bootstrap:.1f}%)")

        # Step 3: Calculate confidence intervals
        confidence_intervals = self._calculate_percentile_ci(bootstrap_params, original_params)

        # Calculate bootstrap statistics
        bootstrap_stats = self._calculate_bootstrap_statistics(bootstrap_params)

        return {
            'original_params': original_params,
            'bootstrap_params': bootstrap_params,
            'confidence_intervals': confidence_intervals,
            'bootstrap_stats': bootstrap_stats,
            'convergence_rate': convergence_count / self.n_bootstrap
        }

    def _calculate_percentile_ci(
        self,
        bootstrap_params: List[Dict[str, float]],
        original_params: Dict[str, float],
        alpha: float = 0.05
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculate percentile confidence intervals.

        Args:
            bootstrap_params: List of bootstrap parameter estimates
            original_params: Original parameter estimates
            alpha: Significance level (default 0.05 for 95% CI)

        Returns:
            Dictionary with confidence intervals
        """
        ci_dict = {}

        if not bootstrap_params:
            return ci_dict

        # Convert to DataFrame for easier manipulation
        params_df = pd.DataFrame(bootstrap_params)

        for param_name in original_params.keys():
            if param_name in params_df.columns:
                param_values = params_df[param_name].dropna()

                if len(param_values) > 0:
                    ci_lower = float(param_values.quantile(alpha / 2))
                    ci_upper = float(param_values.quantile(1 - alpha / 2))

                    ci_dict[param_name] = {
                        'original': float(original_params[param_name]),
                        'ci_lower': ci_lower,
                        'ci_upper': ci_upper,
                        'ci_width': ci_upper - ci_lower,
                        'bootstrap_mean': float(param_values.mean()),
                        'bootstrap_std': float(param_values.std())
                    }

        return ci_dict

    def _calculate_bootstrap_statistics(self, bootstrap_params: List[Dict[str, float]]) -> Dict[str, Dict[str, float]]:
        """
        Calculate additional bootstrap statistics.

        Args:
            bootstrap_params: List of bootstrap parameter estimates

        Returns:
            Dictionary with bootstrap statistics
        """
        if not bootstrap_params:
            return {}

        params_df = pd.DataFrame(bootstrap_params)
        stats = {}

        # Focus on key parameters
        key_params = ['omega', 'alpha[1]', 'beta[1]', 'gamma[1]', 'nu']

        for param in key_params:
            if param in params_df.columns:
                values = params_df[param].dropna()
                if len(values) > 0:
                    stats[param] = {
                        'mean': float(values.mean()),
                        'median': float(values.median()),
                        'std': float(values.std()),
                        'skewness': float(values.skew()),
                        'kurtosis': float(values.kurtosis()),
                        'min': float(values.min()),
                        'max': float(values.max())
                    }

        # Calculate persistence (alpha + beta + gamma/2 for TARCH)
        if 'alpha[1]' in params_df.columns and 'beta[1]' in params_df.columns:
            alpha_vals = params_df['alpha[1]'].dropna()
            beta_vals = params_df['beta[1]'].dropna()

            if 'gamma[1]' in params_df.columns:
                gamma_vals = params_df['gamma[1]'].dropna()
                # Align lengths
                min_len = min(len(alpha_vals), len(beta_vals), len(gamma_vals))
                persistence = alpha_vals.iloc[:min_len] + beta_vals.iloc[:min_len] + gamma_vals.iloc[:min_len] / 2
            else:
                min_len = min(len(alpha_vals), len(beta_vals))
                persistence = alpha_vals.iloc[:min_len] + beta_vals.iloc[:min_len]

            stats['persistence'] = {
                'mean': float(persistence.mean()),
                'median': float(persistence.median()),
                'std': float(persistence.std()),
                'ci_lower': float(persistence.quantile(0.025)),
                'ci_upper': float(persistence.quantile(0.975))
            }

        return stats

    def bootstrap_event_coefficients_optimized(
        self,
        data_with_events: pd.DataFrame,
        event_columns: List[str],
        n_bootstrap: int = 100,
        block_size: int = 10
    ) -> Dict:
        """
        Optimized bootstrap confidence intervals for event coefficients.
        Uses block bootstrap with vectorized operations.

        Args:
            data_with_events: DataFrame with returns and event dummies
            event_columns: List of event dummy column names
            n_bootstrap: Number of bootstrap replications
            block_size: Block size for block bootstrap

        Returns:
            Dictionary with bootstrap results for event coefficients
        """
        logger.info(f"Bootstrapping event coefficients ({n_bootstrap} replications)...")

        # Import required modules here to avoid circular import
        from garch_models import GARCHModels

        # Extract returns
        returns = data_with_events['returns_winsorized'].dropna()

        # Fit original model to get baseline
        logger.info("Fitting baseline TARCH-X model...")
        estimator = GARCHModels(data_with_events, 'bootstrap')
        baseline_model = estimator.estimate_tarch_x(use_individual_events=False)

        if not baseline_model.convergence:
            return {'error': 'Baseline model failed to converge'}

        # Extract baseline coefficients
        baseline_coeffs = {}
        if baseline_model.event_effects:
            baseline_coeffs.update(baseline_model.event_effects)

        # Vectorized block bootstrap sample generation
        n_obs = len(returns)
        n_blocks = n_obs // block_size

        def _create_block_bootstrap_sample(iteration: int) -> Optional[Dict[str, float]]:
            """Create and estimate single bootstrap sample."""
            np.random.seed(self.seed + iteration)

            # Generate block indices
            block_indices = np.random.randint(0, n_obs - block_size, size=n_blocks)

            # Create bootstrap sample using vectorized indexing
            indices = np.concatenate([
                np.arange(start, start + block_size)
                for start in block_indices
            ])[:n_obs]  # Trim to original length

            bootstrap_data = data_with_events.iloc[indices].copy()

            # Estimate model on bootstrap sample
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    boot_estimator = GARCHModels(bootstrap_data, 'bootstrap')
                    boot_model = boot_estimator.estimate_tarch_x(use_individual_events=False)

                if boot_model.convergence and boot_model.event_effects:
                    return boot_model.event_effects
                else:
                    return None

            except Exception as e:
                logger.debug(f"Bootstrap iteration {iteration} failed: {e}")
                return None

        # Parallel bootstrap execution
        logger.info(f"Running {n_bootstrap} bootstrap replications in parallel...")
        bootstrap_results = Parallel(n_jobs=self.n_jobs, backend='loky')(
            delayed(_create_block_bootstrap_sample)(i)
            for i in tqdm(range(n_bootstrap), desc="Event bootstrap")
        )

        # Organize results by event column
        bootstrap_coeffs = {col: [] for col in event_columns}
        convergence_count = 0

        for result in bootstrap_results:
            if result is not None:
                convergence_count += 1
                for col in event_columns:
                    if col in result:
                        bootstrap_coeffs[col].append(result[col])

        logger.info(f"Bootstrap completed: {convergence_count}/{n_bootstrap} converged ({100*convergence_count/n_bootstrap:.1f}%)")

        # Calculate confidence intervals
        ci_results = {}
        for col in event_columns:
            if len(bootstrap_coeffs[col]) > 0:
                coefs = np.array(bootstrap_coeffs[col])
                ci_results[col] = {
                    'baseline': baseline_coeffs.get(col, np.nan),
                    'bootstrap_mean': float(np.mean(coefs)),
                    'bootstrap_std': float(np.std(coefs)),
                    'ci_lower': float(np.percentile(coefs, 2.5)),
                    'ci_upper': float(np.percentile(coefs, 97.5))
                }

        return {
            'baseline_coefficients': baseline_coeffs,
            'bootstrap_results': ci_results,
            'convergence_rate': convergence_count / n_bootstrap
        }

    def create_bootstrap_table(self, bootstrap_results: Dict) -> pd.DataFrame:
        """
        Create formatted table with original estimates and bootstrap CIs.

        Args:
            bootstrap_results: Results from residual_bootstrap_tarch

        Returns:
            DataFrame with formatted results
        """
        if 'confidence_intervals' not in bootstrap_results:
            return pd.DataFrame()

        ci_data = bootstrap_results['confidence_intervals']

        table_data = []
        for param_name, param_ci in ci_data.items():
            table_data.append({
                'Parameter': param_name,
                'Original Estimate': f"{param_ci['original']:.6f}",
                'Bootstrap Mean': f"{param_ci['bootstrap_mean']:.6f}",
                'Bootstrap Std': f"{param_ci['bootstrap_std']:.6f}",
                '95% CI Lower': f"{param_ci['ci_lower']:.6f}",
                '95% CI Upper': f"{param_ci['ci_upper']:.6f}"
            })

        return pd.DataFrame(table_data)


def run_bootstrap_analysis(
    returns: pd.Series,
    model_type: str = 'TARCH',
    n_bootstrap: int = 500,
    seed: int = 42,
    n_jobs: int = -1
) -> Dict:
    """
    Convenience function to run bootstrap analysis.

    Args:
        returns: Series of returns
        model_type: 'GARCH' or 'TARCH'
        n_bootstrap: Number of bootstrap replications
        seed: Random seed
        n_jobs: Number of parallel jobs

    Returns:
        Dictionary with bootstrap results
    """
    bootstrap = BootstrapInference(returns, n_bootstrap, seed, n_jobs)
    results = bootstrap.residual_bootstrap_tarch(model_type=model_type)

    # Create and print table
    table = bootstrap.create_bootstrap_table(results)
    if not table.empty:
        logger.info("\nBootstrap Confidence Intervals:")
        logger.info(f"\n{table.to_string(index=False)}")

    return results


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Test with synthetic data
    np.random.seed(42)
    n_obs = 500

    returns = np.random.standard_t(df=5, size=n_obs)
    returns = pd.Series(returns, index=pd.date_range('2020-01-01', periods=n_obs))

    results = run_bootstrap_analysis(returns, n_bootstrap=100)
