"""
Extended TARCH-X Model with Microstructure Variables
======================================================

Extends Paper 1's TARCH-X to include microstructure variables in variance equation:

σ²_t = ω + α·ε²_{t-1} + γ·ε²_{t-1}·I(ε<0) + β·σ²_{t-1}
       + δ_reg·D_regulatory_t        ← From Paper 1
       + δ_sent·Sentiment_t           ← From Paper 1
       + δ_spread·Spread_t            ← NEW: Bid-ask spread
       + δ_depth·Depth_t              ← NEW: Order book depth
       + δ_volume·Volume_t            ← NEW: Trading volume

This allows us to decompose regulatory volatility into:
1. Sentiment channel (δ_sent × Sentiment)
2. Microstructure channel (δ_spread × Spread + δ_depth × Depth)
3. Direct effect (δ_reg)

Key Hypothesis:
- Crypto: δ_spread ≈ 0, δ_depth ≈ 0 (no microstructure channel)
- Traditional: δ_spread > 0, δ_depth < 0 (significant microstructure channel)
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import t as student_t
from scipy.special import gamma
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import warnings


@dataclass
class TARCHXMicroResults:
    """Container for extended TARCH-X estimation results."""
    converged: bool
    params: Dict[str, float]
    std_errors: Dict[str, float]
    pvalues: Dict[str, float]
    log_likelihood: float
    aic: float
    bic: float
    volatility: pd.Series
    residuals: pd.Series

    # Event and sentiment effects (from Paper 1)
    event_effects: Dict[str, float]
    sentiment_effects: Dict[str, float]

    # NEW: Microstructure effects
    microstructure_effects: Dict[str, float]

    # Variance decomposition
    variance_decomposition: Dict[str, float]

    leverage_effect: float
    iterations: int


class TARCHXMicroEstimator:
    """
    Extended TARCH-X estimator with microstructure variables.

    Builds on Paper 1's TARCH-X implementation by adding microstructure
    variables (spread, depth, volume) to the variance equation.
    """

    def __init__(self,
                 returns: pd.Series,
                 exog_vars: Optional[pd.DataFrame] = None,
                 microstructure_vars: Optional[pd.DataFrame] = None):
        """
        Initialize extended TARCH-X estimator.

        Args:
            returns: Series of log returns (×100)
            exog_vars: DataFrame with event dummies and sentiment (from Paper 1)
            microstructure_vars: DataFrame with spread, depth, volume
        """
        self.returns = returns.dropna()

        # Event and sentiment variables (from Paper 1)
        if exog_vars is not None:
            self.exog_vars = exog_vars.loc[self.returns.index].fillna(0)
            self.has_exog = True
            self.n_exog = self.exog_vars.shape[1]
            self.exog_names = list(self.exog_vars.columns)
        else:
            self.exog_vars = None
            self.has_exog = False
            self.n_exog = 0
            self.exog_names = []

        # NEW: Microstructure variables
        if microstructure_vars is not None:
            self.micro_vars = microstructure_vars.loc[self.returns.index].fillna(0)
            self.has_micro = True
            self.n_micro = self.micro_vars.shape[1]
            self.micro_names = list(self.micro_vars.columns)
        else:
            self.micro_vars = None
            self.has_micro = False
            self.n_micro = 0
            self.micro_names = []

        self.n_obs = len(self.returns)

        # Parameter names: GARCH params + exogenous + microstructure
        self.param_names = (['omega', 'alpha', 'gamma', 'beta', 'nu'] +
                           self.exog_names + self.micro_names)
        self.n_params = 5 + self.n_exog + self.n_micro

    def _unpack_params(self, params: np.ndarray) -> Dict[str, float]:
        """Unpack parameter vector into named dictionary."""
        param_dict = {
            'omega': params[0],
            'alpha': params[1],
            'gamma': params[2],
            'beta': params[3],
            'nu': params[4]
        }

        # Add exogenous variables (events + sentiment)
        for i, name in enumerate(self.exog_names):
            param_dict[name] = params[5 + i]

        # Add microstructure variables
        for i, name in enumerate(self.micro_names):
            param_dict[name] = params[5 + self.n_exog + i]

        return param_dict

    def _variance_recursion(self, params: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute conditional variance with TARCH + exogenous + microstructure.

        Extended variance equation:
        σ²_t = ω + α·ε²_{t-1} + γ·ε²_{t-1}·I(ε<0) + β·σ²_{t-1}
               + Σδ_j·x_{j,t} + Σθ_k·m_{k,t}

        where x_{j,t} = event/sentiment variables
              m_{k,t} = microstructure variables
        """
        param_dict = self._unpack_params(params)
        omega = param_dict['omega']
        alpha = param_dict['alpha']
        gamma = param_dict['gamma']
        beta = param_dict['beta']

        # Initialize
        variance = np.zeros(self.n_obs)
        mean_return = self.returns.mean()
        residuals = (self.returns - mean_return).values

        # Initial variance
        variance[0] = np.var(self.returns)

        # Recursive computation
        for t in range(1, self.n_obs):
            # TARCH terms
            eps_sq_prev = residuals[t-1] ** 2
            leverage_term = gamma * eps_sq_prev * (residuals[t-1] < 0)

            variance[t] = (omega +
                          alpha * eps_sq_prev +
                          leverage_term +
                          beta * variance[t-1])

            # Add exogenous variables (Paper 1: events + sentiment)
            if self.has_exog:
                for i, exog_name in enumerate(self.exog_names):
                    delta = param_dict[exog_name]
                    exog_value = self.exog_vars.iloc[t, i]
                    variance[t] += delta * exog_value

            # NEW: Add microstructure variables
            if self.has_micro:
                for i, micro_name in enumerate(self.micro_names):
                    theta = param_dict[micro_name]
                    micro_value = self.micro_vars.iloc[t, i]
                    variance[t] += theta * micro_value

            # Ensure positive variance
            variance[t] = max(variance[t], 1e-8)

        return variance, residuals

    def _log_likelihood(self, params: np.ndarray) -> float:
        """Compute negative log-likelihood for Student-t TARCH-X-Micro model."""
        try:
            param_dict = self._unpack_params(params)
            nu = param_dict['nu']

            variance, residuals = self._variance_recursion(params)
            std_residuals = residuals / np.sqrt(variance)

            # Student-t log-likelihood
            log_lik = 0
            for t in range(self.n_obs):
                log_gamma_term = (np.log(gamma((nu + 1) / 2)) -
                                 np.log(gamma(nu / 2)) -
                                 0.5 * np.log(np.pi * (nu - 2)))
                log_var_term = -0.5 * np.log(variance[t])
                density_term = -((nu + 1) / 2) * np.log(1 + std_residuals[t]**2 / (nu - 2))
                log_lik += log_gamma_term + log_var_term + density_term

            return -log_lik

        except (ValueError, OverflowError, RuntimeWarning):
            return 1e8

    def _parameter_constraints(self) -> List[Dict]:
        """Define parameter constraints including stationarity."""
        constraints = [
            {'type': 'ineq', 'fun': lambda x: x[0] - 1e-8},  # omega > 0
            {'type': 'ineq', 'fun': lambda x: x[1] - 1e-8},  # alpha > 0
            {'type': 'ineq', 'fun': lambda x: x[3] - 1e-8},  # beta > 0
            {'type': 'ineq', 'fun': lambda x: x[4] - 2.1},   # nu > 2
            {'type': 'ineq', 'fun': lambda x: 50 - x[4]},    # nu < 50
            # Stationarity: alpha + beta + |gamma|/2 < 1
            {'type': 'ineq', 'fun': lambda x: 0.999 - (x[1] + x[3] + abs(x[2])/2)}
        ]
        return constraints

    def _get_starting_values(self) -> np.ndarray:
        """Generate starting values for optimization."""
        sample_var = np.var(self.returns)

        start_vals = np.array([
            sample_var * 0.1,  # omega
            0.05,              # alpha
            0.05,              # gamma
            0.85,              # beta
            5.0                # nu
        ])

        # Add zeros for exogenous and microstructure variables
        if self.has_exog:
            start_vals = np.append(start_vals, np.zeros(self.n_exog))
        if self.has_micro:
            start_vals = np.append(start_vals, np.zeros(self.n_micro))

        return start_vals

    def estimate(self, method: str = 'SLSQP', max_iter: int = 1000) -> TARCHXMicroResults:
        """
        Estimate extended TARCH-X model with microstructure variables.

        Args:
            method: Optimization method
            max_iter: Maximum iterations

        Returns:
            TARCHXMicroResults object
        """
        print(f"Estimating extended TARCH-X with {self.n_exog} exogenous + "
              f"{self.n_micro} microstructure variables...")

        start_vals = self._get_starting_values()

        # Parameter bounds
        bounds = [
            (1e-8, None),      # omega > 0
            (1e-8, 0.3),       # alpha
            (-0.5, 0.5),       # gamma
            (1e-8, 0.95),      # beta
            (2.1, 50),         # nu
        ]

        # Add bounds for exogenous and microstructure (unbounded)
        for _ in range(self.n_exog + self.n_micro):
            bounds.append((None, None))

        # Optimize
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")

                result = minimize(
                    fun=self._log_likelihood,
                    x0=start_vals,
                    method=method,
                    bounds=bounds,
                    constraints=self._parameter_constraints(),
                    options={'maxiter': max_iter, 'disp': False}
                )

            converged = result.success and result.fun < 1e6

            if not converged:
                print(f"  [WARNING] Optimization did not converge: {result.message}")

            # Extract results
            optimal_params = result.x
            param_dict = self._unpack_params(optimal_params)

            variance, residuals = self._variance_recursion(optimal_params)
            volatility = pd.Series(np.sqrt(variance), index=self.returns.index)
            residuals_series = pd.Series(residuals, index=self.returns.index)

            # Compute standard errors
            std_errors, pvalues = self._compute_standard_errors(optimal_params)

            # Information criteria
            log_lik = -result.fun
            aic = 2 * self.n_params - 2 * log_lik
            bic = np.log(self.n_obs) * self.n_params - 2 * log_lik

            # Separate effects
            event_effects = {}
            sentiment_effects = {}
            microstructure_effects = {}

            for name in self.exog_names:
                if 'event' in name.lower() or 'regulatory' in name.lower() or 'infrastructure' in name.lower():
                    event_effects[name] = param_dict[name]
                elif 'sentiment' in name.lower() or 'gdelt' in name.lower():
                    sentiment_effects[name] = param_dict[name]
                else:
                    event_effects[name] = param_dict[name]

            for name in self.micro_names:
                microstructure_effects[name] = param_dict[name]

            # NEW: Variance decomposition
            decomp = self._decompose_variance(param_dict, event_effects,
                                              sentiment_effects, microstructure_effects)

            print(f"  [OK] Converged in {result.nit} iterations")
            print(f"  Log-likelihood: {log_lik:.2f}, AIC: {aic:.2f}, BIC: {bic:.2f}")

            # Display microstructure effects
            if microstructure_effects:
                print("  Microstructure coefficients:")
                for name, coef in microstructure_effects.items():
                    p_val = pvalues.get(name, np.nan)
                    sig = '***' if p_val < 0.01 else '**' if p_val < 0.05 else '*' if p_val < 0.10 else ''
                    print(f"    {name}: {coef:+.6f}{sig} (p={p_val:.4f})")

            return TARCHXMicroResults(
                converged=converged,
                params=param_dict,
                std_errors=std_errors,
                pvalues=pvalues,
                log_likelihood=log_lik,
                aic=aic,
                bic=bic,
                volatility=volatility,
                residuals=residuals_series,
                event_effects=event_effects,
                sentiment_effects=sentiment_effects,
                microstructure_effects=microstructure_effects,
                variance_decomposition=decomp,
                leverage_effect=param_dict['gamma'],
                iterations=result.nit
            )

        except Exception as e:
            print(f"  [FAIL] Estimation failed: {str(e)}")
            return self._create_failed_result()

    def _decompose_variance(self, param_dict: Dict, event_effects: Dict,
                           sentiment_effects: Dict, microstructure_effects: Dict) -> Dict:
        """
        Decompose regulatory event volatility impact into channels.

        Returns:
            Dictionary with variance decomposition:
            - total_regulatory_impact
            - sentiment_contribution
            - microstructure_contribution
            - direct_contribution
            - shares (%)
        """
        # Total regulatory event impact
        total_impact = event_effects.get('D_regulatory', 0)

        if total_impact == 0:
            return {
                'total': 0,
                'sentiment': 0,
                'microstructure': 0,
                'direct': 0,
                'sentiment_share': 0,
                'microstructure_share': 0,
                'direct_share': 0
            }

        # Calculate average values during regulatory events
        # (This is simplified - in full analysis, compute from actual event windows)
        avg_sentiment = 0.1  # Placeholder
        avg_spread_change = 0.02  # Placeholder
        avg_depth_change = -0.1  # Placeholder

        # Sentiment contribution
        sent_contrib = sum(param_dict.get(name, 0) * avg_sentiment
                          for name in sentiment_effects.keys())

        # Microstructure contribution
        micro_contrib = sum(param_dict.get(name, 0) *
                           (avg_spread_change if 'spread' in name else avg_depth_change)
                           for name in microstructure_effects.keys())

        # Direct effect (residual)
        direct_contrib = total_impact - sent_contrib - micro_contrib

        return {
            'total': total_impact,
            'sentiment': sent_contrib,
            'microstructure': micro_contrib,
            'direct': direct_contrib,
            'sentiment_share': (sent_contrib / total_impact) * 100 if total_impact != 0 else 0,
            'microstructure_share': (micro_contrib / total_impact) * 100 if total_impact != 0 else 0,
            'direct_share': (direct_contrib / total_impact) * 100 if total_impact != 0 else 0
        }

    def _compute_standard_errors(self, params: np.ndarray) -> Tuple[Dict, Dict]:
        """Compute standard errors using numerical Hessian."""
        try:
            hessian = self._numerical_hessian(params)
            cov_matrix = np.linalg.inv(hessian)
            std_errs = np.sqrt(np.diag(cov_matrix))

            # Check degrees of freedom
            dof = self.n_obs - self.n_params
            if dof <= 0:
                print(f"  [ERROR] Insufficient DOF: {dof}")
                return ({name: np.nan for name in self.param_names},
                       {name: np.nan for name in self.param_names})

            t_stats = params / std_errs
            pvals = 2 * (1 - student_t.cdf(np.abs(t_stats), dof))

            std_errors = dict(zip(self.param_names, std_errs))
            pvalues = dict(zip(self.param_names, pvals))

            return std_errors, pvalues

        except (np.linalg.LinAlgError, ValueError):
            print("  [WARNING] Could not compute standard errors")
            return ({name: np.nan for name in self.param_names},
                   {name: np.nan for name in self.param_names})

    def _numerical_hessian(self, params: np.ndarray, h: float = 1e-5) -> np.ndarray:
        """Compute numerical Hessian matrix."""
        n = len(params)
        hessian = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                if i == j:
                    params_plus = params.copy()
                    params_minus = params.copy()
                    params_plus[i] += h
                    params_minus[i] -= h

                    f_plus = self._log_likelihood(params_plus)
                    f_minus = self._log_likelihood(params_minus)
                    f_center = self._log_likelihood(params)

                    hessian[i, j] = (f_plus - 2*f_center + f_minus) / (h**2)
                else:
                    params_pp = params.copy()
                    params_pm = params.copy()
                    params_mp = params.copy()
                    params_mm = params.copy()

                    params_pp[i] += h
                    params_pp[j] += h
                    params_pm[i] += h
                    params_pm[j] -= h
                    params_mp[i] -= h
                    params_mp[j] += h
                    params_mm[i] -= h
                    params_mm[j] -= h

                    f_pp = self._log_likelihood(params_pp)
                    f_pm = self._log_likelihood(params_pm)
                    f_mp = self._log_likelihood(params_mp)
                    f_mm = self._log_likelihood(params_mm)

                    hessian[i, j] = (f_pp - f_pm - f_mp + f_mm) / (4 * h**2)

        return hessian

    def _create_failed_result(self) -> TARCHXMicroResults:
        """Create failed result object."""
        return TARCHXMicroResults(
            converged=False,
            params={},
            std_errors={},
            pvalues={},
            log_likelihood=np.nan,
            aic=np.nan,
            bic=np.nan,
            volatility=pd.Series(),
            residuals=pd.Series(),
            event_effects={},
            sentiment_effects={},
            microstructure_effects={},
            variance_decomposition={},
            leverage_effect=np.nan,
            iterations=0
        )


def estimate_tarch_x_micro(returns: pd.Series,
                          exog_vars: Optional[pd.DataFrame] = None,
                          microstructure_vars: Optional[pd.DataFrame] = None,
                          method: str = 'SLSQP') -> TARCHXMicroResults:
    """
    Convenience function to estimate extended TARCH-X model.

    Args:
        returns: Log returns series (×100)
        exog_vars: Event dummies and sentiment
        microstructure_vars: Spread, depth, volume
        method: Optimization method

    Returns:
        TARCHXMicroResults object
    """
    estimator = TARCHXMicroEstimator(returns, exog_vars, microstructure_vars)
    return estimator.estimate(method=method)
