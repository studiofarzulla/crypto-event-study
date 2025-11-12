# Model Estimation Layer Documentation

**Cryptocurrency Event Study - TARCH-X Implementation**

**Author:** Research Documentation
**Date:** October 28, 2025
**Status:** Active Research Implementation

---

## Table of Contents

1. [Overview](#overview)
2. [Model Specifications](#model-specifications)
3. [Architecture & File Structure](#architecture--file-structure)
4. [GARCHModels Class API](#garchmodels-class-api)
5. [Manual TARCH-X Implementation](#manual-tarch-x-implementation)
6. [Exogenous Variables & Event Dummies](#exogenous-variables--event-dummies)
7. [Estimation Flow](#estimation-flow)
8. [Recent Changes (Oct 28, 2025)](#recent-changes-oct-28-2025)
9. [Performance Optimization](#performance-optimization)
10. [Usage Examples](#usage-examples)

---

## Overview

This layer implements three progressively complex GARCH models for cryptocurrency volatility analysis:

1. **GARCH(1,1)** - Baseline symmetric volatility model
2. **TARCH(1,1)** - Adds leverage/asymmetry effects (GJR-GARCH)
3. **TARCH-X** - Extends TARCH with exogenous variables (events, sentiment) in the variance equation

The implementation uses a **custom manual TARCH-X estimator** rather than the `arch` package because:
- The `arch` package doesn't properly support exogenous variables in variance equations
- Full control over maximum likelihood estimation and optimization
- Academic rigor for thesis requirements
- Transparent mathematical implementation

### Key Design Decisions

- **Student-t distribution**: Captures fat tails in cryptocurrency returns
- **GJR-GARCH form**: Industry standard for leverage effects
- **Manual MLE**: Custom implementation for methodological contribution
- **Robust standard errors**: Numerical Hessian for inference
- **Fallback strategies**: Graceful degradation when convergence fails

---

## Model Specifications

### 1. GARCH(1,1) Baseline

**Mean Equation:**
```
r_t = μ + ε_t
ε_t = σ_t * z_t,  z_t ~ Student-t(ν)
```

**Variance Equation:**
```
σ²_t = ω + α₁ε²_{t-1} + β₁σ²_{t-1}
```

**Parameters (5 total):**
- `μ` - Constant mean return
- `ω` - Intercept (baseline variance)
- `α₁` - ARCH effect (response to recent shocks)
- `β₁` - GARCH effect (variance persistence)
- `ν` - Student-t degrees of freedom (tail thickness)

**Constraints:**
- `ω > 0`, `α₁ > 0`, `β₁ > 0`
- `α₁ + β₁ < 1` (stationarity)
- `ν > 2` (finite variance)

---

### 2. TARCH(1,1) with Leverage Effects

**Mean Equation:**
```
r_t = μ + ε_t
ε_t = σ_t * z_t,  z_t ~ Student-t(ν)
```

**Variance Equation (GJR-GARCH Form):**
```
σ²_t = ω + α₁ε²_{t-1} + γ₁ε²_{t-1}I(ε_{t-1}<0) + β₁σ²_{t-1}
```

Where `I(ε_{t-1}<0)` is an indicator function for negative returns.

**Parameters (6 total):**
- All GARCH(1,1) parameters, plus:
- `γ₁` - Leverage effect (additional volatility from negative shocks)

**Interpretation:**
- For **positive** shocks: volatility impact = `α₁`
- For **negative** shocks: volatility impact = `α₁ + γ₁`
- If `γ₁ > 0`: negative returns increase volatility MORE than positive returns (leverage effect)

**Constraints:**
- All GARCH(1,1) constraints, plus:
- `α₁ + β₁ + γ₁/2 < 1` (stationarity with asymmetry)

---

### 3. TARCH-X with Exogenous Variables

**Mean Equation:**
```
r_t = μ + ε_t
ε_t = σ_t * z_t,  z_t ~ Student-t(ν)
```

**Variance Equation with Exogenous Variables:**
```
σ²_t = ω + α₁ε²_{t-1} + γ₁ε²_{t-1}I(ε_{t-1}<0) + β₁σ²_{t-1} + Σⱼ δⱼx_{j,t}
```

**Exogenous Variables (x_{j,t}):**
1. **Event Dummies** (D_infrastructure, D_regulatory):
   - Binary indicators for 7-day event windows
   - Capture discrete volatility shifts during events

2. **Decomposed Sentiment** (infra_decomposed, reg_decomposed):
   - Continuous GDELT-derived sentiment scores
   - Orthogonalized to event dummies to avoid multicollinearity
   - Capture continuous sentiment-driven volatility

**Parameters (5 base + n_exog):**
- All TARCH(1,1) parameters (ω, α, γ, β, ν)
- `δⱼ` coefficients for each exogenous variable (typically 2-4)

**Recent Configuration (Oct 28, 2025):**
- Aggregated event dummies: 2 variables (D_infrastructure, D_regulatory)
- Decomposed sentiment: 2 variables (infra_decomposed, reg_decomposed)
- **Total parameters: 9** (5 base + 4 exogenous)

**Constraints:**
- All TARCH(1,1) constraints
- `-1.0 ≤ δⱼ ≤ 1.0` (bounded event/sentiment effects)

---

## Architecture & File Structure

### File Overview

```
code/
├── garch_models.py                  # Main interface & GARCHModels class
├── tarch_x_manual.py                # Custom TARCH-X implementation
├── tarch_x_manual_optimized.py      # Performance-optimized version
└── tarch_x_integration.py           # Integration guide & examples
```

### Relationship Between Files

```
┌─────────────────────────────────────────────────────────────────┐
│                     garch_models.py                              │
│                   (High-level Interface)                         │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  GARCHModels Class                                      │    │
│  │  - estimate_garch_11()    → Uses arch package           │    │
│  │  - estimate_tarch_11()    → Uses arch package           │    │
│  │  - estimate_tarch_x()     → Calls manual implementation │────┼─┐
│  │  - estimate_all_models()                                │    │ │
│  │  - _prepare_exogenous_variables()                       │    │ │
│  └────────────────────────────────────────────────────────┘    │ │
└─────────────────────────────────────────────────────────────────┘ │
                                                                     │
┌────────────────────────────────────────────────────────────────┐ │
│               tarch_x_manual.py                                 │◄┘
│            (Core Implementation)                                │
│                                                                 │
│  ┌───────────────────────────────────────────────────────┐    │
│  │  TARCHXEstimator Class                                 │    │
│  │  - _variance_recursion()      → Recursive σ²_t         │    │
│  │  - _log_likelihood()           → Student-t MLE         │    │
│  │  - _numerical_hessian()        → Standard errors       │    │
│  │  - estimate()                  → Main entry point      │    │
│  └───────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌───────────────────────────────────────────────────────┐    │
│  │  TARCHXResults Dataclass                               │    │
│  │  - params, std_errors, pvalues                         │    │
│  │  - volatility, residuals                               │    │
│  │  - event_effects, sentiment_effects                    │    │
│  │  - leverage_effect                                      │    │
│  └───────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   │ Optimized version
                                   ↓
┌─────────────────────────────────────────────────────────────────┐
│          tarch_x_manual_optimized.py                             │
│          (Performance Enhancement)                               │
│                                                                  │
│  Optimizations:                                                 │
│  - Vectorized variance recursion (5x faster)                    │
│  - BFGS-approximated Hessian (100x faster)                      │
│  - Cached log-gamma functions                                   │
│  - Type hints throughout                                        │
│  - Proper logging instead of print                              │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   │ Integration guide
                                   ↓
┌─────────────────────────────────────────────────────────────────┐
│             tarch_x_integration.py                               │
│             (Integration Guide)                                  │
│                                                                  │
│  - EnhancedGARCHModels class (drop-in replacement)              │
│  - Example usage with existing framework                        │
│  - Academic advantages documentation                            │
└─────────────────────────────────────────────────────────────────┘
```

### Evolution of Implementation

1. **tarch_x_manual.py** - Initial implementation
   - Clean, readable code
   - Full numerical Hessian (O(n²) complexity)
   - Print-based logging

2. **tarch_x_manual_optimized.py** - Performance version
   - Vectorized operations where possible
   - BFGS approximation for Hessian
   - Proper Python logging
   - Type hints for safety
   - 5-100x faster for large datasets

3. **tarch_x_integration.py** - Usage guide
   - Shows how to integrate with existing codebase
   - Academic justification
   - Example workflow

**Current Status:** `garch_models.py` imports from `tarch_x_manual.py` (the original clean implementation). The optimized version exists for future large-scale analysis.

---

## GARCHModels Class API

### Initialization

```python
from garch_models import GARCHModels

# Initialize with prepared data
modeler = GARCHModels(data=prepared_df, crypto='btc')
```

**Arguments:**
- `data: pd.DataFrame` - Prepared data with returns and exogenous variables
- `crypto: str` - Cryptocurrency identifier

**Auto-detected attributes:**
- `self.has_events` - Detects any columns starting with 'D_'
- `self.has_sentiment` - Detects GDELT/decomposed sentiment columns
- `self.returns` - Extracts 'returns_winsorized' column

---

### Main Methods

#### 1. estimate_garch_11()

```python
results = modeler.estimate_garch_11()
```

**Returns:** `ModelResults` object

**Implementation:**
- Uses `arch` package with `arch_model()` function
- Student-t distribution
- Robust standard errors (White's covariance)
- Maximum 1000 iterations

**Output:**
- Convergence status, iterations
- AIC, BIC, log-likelihood
- Parameters: omega, alpha[1], beta[1], nu
- Conditional volatility series
- Standardized residuals

---

#### 2. estimate_tarch_11()

```python
results = modeler.estimate_tarch_11()
```

**Returns:** `ModelResults` object with `leverage_effect` attribute

**Implementation:**
- Uses `arch` package with `o=1` parameter (GJR-GARCH)
- Student-t distribution
- Robust standard errors

**Output:**
- All GARCH(1,1) outputs, plus:
- `leverage_effect` - gamma[1] parameter
- Interpretation printed during estimation

---

#### 3. estimate_tarch_x()

```python
results = modeler.estimate_tarch_x(
    use_individual_events=False,  # Use aggregated D_infrastructure/D_regulatory
    include_sentiment=True        # Include decomposed sentiment
)
```

**Arguments:**
- `use_individual_events: bool` - If True, uses all individual event dummies; if False, uses aggregated type dummies
- `include_sentiment: bool` - Whether to include sentiment variables

**Returns:** `ModelResults` object with event/sentiment attributes

**Implementation:**
```python
# Prepare exogenous variables
exog_vars = self._prepare_exogenous_variables(use_individual_events, include_sentiment)

# Multicollinearity check
if len(exog_aligned.columns) > 1:
    corr_matrix = exog_aligned.corr().abs()
    max_corr = corr_matrix.max().max()
    if max_corr > 0.95:
        print(f"  [WARNING] High multicollinearity detected! Max correlation: {max_corr:.3f}")

# Use manual TARCH-X implementation
manual_results = estimate_tarch_x_manual(
    returns=self.returns,
    exog_vars=exog_aligned,
    method='SLSQP'
)

# Convert to ModelResults format for compatibility
results = ModelResults(...)
```

**Output:**
- All TARCH(1,1) outputs, plus:
- `event_effects: Dict[str, float]` - Event dummy coefficients
- `sentiment_effects: Dict[str, float]` - Sentiment coefficients
- `event_std_errors: Dict[str, float]` - Standard errors for events
- `event_pvalues: Dict[str, float]` - P-values for events
- Real-time display of significant effects with stars (*** p<0.01, ** p<0.05, * p<0.10)

**Fallback Strategy:**
If estimation fails with `use_individual_events=True`, automatically retries with `use_individual_events=False` (aggregated dummies).

---

#### 4. estimate_all_models()

```python
all_results = modeler.estimate_all_models()
```

**Returns:** `Dict[str, ModelResults]` with keys 'GARCH(1,1)', 'TARCH(1,1)', 'TARCH-X'

**Workflow:**
1. Estimate GARCH(1,1) baseline
2. Estimate TARCH(1,1) with leverage
3. Estimate TARCH-X with exogenous variables
4. Compare models using AIC/BIC
5. Display best model

**Output:**
```
============================================================
Model Comparison for btc
============================================================

Model Fit Statistics:
       Model        AIC        BIC  Log-Likelihood  Converged
    TARCH-X    4523.12    4558.34        -2252.56       True
  TARCH(1,1)   4567.89    4592.11        -2278.95       True
  GARCH(1,1)   4598.45    4618.23        -2295.23       True

Best model by AIC: TARCH-X
Best model by BIC: TARCH-X
```

---

### Helper Methods

#### _prepare_exogenous_variables()

```python
exog_df = self._prepare_exogenous_variables(
    use_individual_events=False,
    include_sentiment=True
)
```

**Critical Logic (as of Oct 28, 2025):**

```python
exog_vars = []

# Add event dummies
if self.has_events:
    if use_individual_events:
        # Individual events (D_event_1, D_event_2, ...)
        event_cols = [col for col in self.data.columns if col.startswith('D_')]
        if event_cols:
            exog_vars.extend(sorted(event_cols))
    else:
        # COMMENTED OUT Oct 28, 2025:
        # Testing sentiment-only approach (reduces params from 11 to 9)
        # Decomposed sentiment captures event timing implicitly

        # if 'D_infrastructure' in self.data.columns:
        #     exog_vars.append('D_infrastructure')
        # if 'D_regulatory' in self.data.columns:
        #     exog_vars.append('D_regulatory')
        pass  # Event dummies disabled when use_individual_events=False

# Add sentiment variables
if include_sentiment and self.has_sentiment:
    sentiment_cols = [col for col in self.data.columns
                    if 'gdelt_normalized' in col or
                       'reg_decomposed' in col or
                       'infra_decomposed' in col]
    exog_vars.extend(sentiment_cols)

return self.data[exog_vars].copy()
```

**See "Recent Changes" section below for rationale.**

---

#### extract_event_impacts()

```python
impacts_df = modeler.extract_event_impacts()
```

**Returns:** `pd.DataFrame` with columns:
- `crypto` - Cryptocurrency identifier
- `event_variable` - Event variable name
- `coefficient` - Estimated δⱼ coefficient
- `std_error` - Standard error
- `p_value` - Two-sided p-value
- `significant_5pct` - Boolean flag
- `significant_10pct` - Boolean flag

**Usage:** Export results for cross-cryptocurrency comparison.

---

## Manual TARCH-X Implementation

### TARCHXEstimator Class

Located in `tarch_x_manual.py`, this is the core custom implementation.

#### Key Methods

##### 1. _variance_recursion()

**Mathematical Implementation:**

```python
def _variance_recursion(self, params: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute conditional variance recursively.

    σ²_t = ω + α₁ε²_{t-1} + γ₁ε²_{t-1}I(ε_{t-1}<0) + β₁σ²_{t-1} + Σδⱼx_{j,t}
    """
    omega, alpha, gamma, beta = params[0:4]

    variance = np.zeros(self.n_obs)
    residuals = (self.returns - self.returns.mean()).values

    # Initialize first variance
    variance[0] = np.var(self.returns)

    # Recursive computation
    for t in range(1, self.n_obs):
        # Previous squared residual
        eps_sq_prev = residuals[t-1] ** 2

        # Leverage term
        leverage_term = gamma * eps_sq_prev * (residuals[t-1] < 0)

        # Base TARCH terms
        variance[t] = omega + alpha * eps_sq_prev + leverage_term + beta * variance[t-1]

        # Add exogenous variables
        if self.has_exog:
            for i, exog_name in enumerate(self.exog_names):
                delta = params[5 + i]  # Exogenous coefficient
                exog_value = self.exog_vars.iloc[t, i]
                variance[t] += delta * exog_value

        # Ensure variance is positive
        variance[t] = max(variance[t], 1e-8)

    return variance, residuals
```

**Why Recursive?**
- Variance at time t depends on variance at time t-1
- Cannot be fully vectorized (sequential dependency)
- Each iteration requires previous period's variance

---

##### 2. _log_likelihood()

**Student-t Log-Likelihood:**

```python
def _log_likelihood(self, params: np.ndarray) -> float:
    """
    Negative log-likelihood for Student-t TARCH-X.

    L(θ) = Σₜ [log Γ((ν+1)/2) - log Γ(ν/2) - 0.5*log(π(ν-2))
           - 0.5*log(σ²_t) - ((ν+1)/2)*log(1 + ε²_t/(σ²_t*(ν-2)))]
    """
    nu = params[4]  # Degrees of freedom
    variance, residuals = self._variance_recursion(params)
    std_residuals = residuals / np.sqrt(variance)

    log_lik = 0
    for t in range(self.n_obs):
        # Gamma function terms
        log_gamma_term = (np.log(gamma((nu + 1) / 2)) -
                         np.log(gamma(nu / 2)) -
                         0.5 * np.log(np.pi * (nu - 2)))

        # Variance term
        log_var_term = -0.5 * np.log(variance[t])

        # Density term
        density_term = -((nu + 1) / 2) * np.log(1 + std_residuals[t]**2 / (nu - 2))

        log_lik += log_gamma_term + log_var_term + density_term

    # Return NEGATIVE for minimization
    return -log_lik
```

**Why Student-t?**
- Captures fat tails in cryptocurrency returns
- More robust to outliers than Normal distribution
- Degrees of freedom (ν) estimated from data

---

##### 3. _numerical_hessian()

**Standard Error Computation:**

```python
def _numerical_hessian(self, params: np.ndarray, h: float = 1e-5) -> np.ndarray:
    """
    Compute Hessian matrix using central differences.

    Second derivative: H[i,i] = [f(θᵢ+h) - 2f(θᵢ) + f(θᵢ-h)] / h²
    Mixed derivative: H[i,j] = [f(θᵢ+h,θⱼ+h) - f(θᵢ+h,θⱼ-h) - f(θᵢ-h,θⱼ+h) + f(θᵢ-h,θⱼ-h)] / 4h²
    """
    n = len(params)
    hessian = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            if i == j:
                # Diagonal: second derivative
                params_plus = params.copy()
                params_minus = params.copy()
                params_plus[i] += h
                params_minus[i] -= h

                hessian[i, j] = (self._log_likelihood(params_plus) -
                                2*self._log_likelihood(params) +
                                self._log_likelihood(params_minus)) / (h**2)
            else:
                # Off-diagonal: mixed partial derivative
                # [Implementation using 4-point stencil]

    return hessian
```

**Standard Errors:**
```python
# Covariance matrix = inverse of Hessian
cov_matrix = np.linalg.inv(hessian)

# Standard errors = square root of diagonal
std_errs = np.sqrt(np.diag(cov_matrix))

# T-statistics
t_stats = params / std_errs

# P-values (two-sided test)
dof = n_obs - n_params
pvals = 2 * (1 - student_t.cdf(np.abs(t_stats), dof))
```

---

##### 4. estimate()

**Main Entry Point:**

```python
def estimate(self, method: str = 'SLSQP', max_iter: int = 1000) -> TARCHXResults:
    """
    Estimate TARCH-X model via maximum likelihood.
    """
    # 1. Get starting values
    start_vals = self._get_starting_values()

    # 2. Define parameter bounds
    bounds = [
        (1e-8, None),      # omega > 0
        (1e-8, 0.3),       # 0 < alpha < 0.3
        (-0.5, 0.5),       # -0.5 < gamma < 0.5
        (1e-8, 0.999),     # 0 < beta < 1
        (2.1, 50),         # 2 < nu < 50
        *[(-1.0, 1.0) for _ in range(self.n_exog)]  # Event/sentiment coefficients
    ]

    # 3. Optimize
    result = minimize(
        fun=self._log_likelihood,
        x0=start_vals,
        method='SLSQP',  # Sequential Least Squares Programming
        bounds=bounds,
        options={'maxiter': max_iter}
    )

    # 4. Extract results
    optimal_params = result.x
    param_dict = self._unpack_params(optimal_params)

    # 5. Compute variance and residuals
    variance, residuals = self._variance_recursion(optimal_params)

    # 6. Compute standard errors
    std_errors, pvalues = self._compute_standard_errors(optimal_params)

    # 7. Information criteria
    log_lik = -result.fun
    aic = 2 * n_params - 2 * log_lik
    bic = np.log(n_obs) * n_params - 2 * log_lik

    # 8. Separate event and sentiment effects
    event_effects = {name: param_dict[name] for name in exog_names
                     if 'infrastructure' in name or 'regulatory' in name}
    sentiment_effects = {name: param_dict[name] for name in exog_names
                        if 'gdelt' in name or 'decomposed' in name}

    return TARCHXResults(...)
```

---

### TARCHXResults Dataclass

```python
@dataclass
class TARCHXResults:
    """Container for TARCH-X estimation results."""
    converged: bool
    params: Dict[str, float]
    std_errors: Dict[str, float]
    pvalues: Dict[str, float]
    log_likelihood: float
    aic: float
    bic: float
    volatility: pd.Series
    residuals: pd.Series
    event_effects: Dict[str, float]
    sentiment_effects: Dict[str, float]
    leverage_effect: float
    iterations: int
```

**Automatic Classification:**
- `event_effects` - Parameters with 'infrastructure', 'regulatory', or 'event' in name
- `sentiment_effects` - Parameters with 'gdelt', 'sentiment', or 'decomposed' in name

---

## Exogenous Variables & Event Dummies

### Variable Types

#### 1. Event Dummies (Binary)

**Original Specification:**
- `D_infrastructure` - Aggregated dummy for all infrastructure events
- `D_regulatory` - Aggregated dummy for all regulatory events

**Construction:**
```python
# In data_preparation.py
D_infrastructure = (D_event_1 | D_event_3 | D_event_5 | ...)
D_regulatory = (D_event_2 | D_event_4 | D_event_6 | ...)
```

**Event Window:**
- 7 days: [event_date - 3, event_date + 3]
- Captures anticipation + reaction effects
- Uses 0.5 for overlapping windows (not double-counted)

**Interpretation:**
- `δ_infrastructure > 0` → Infrastructure events INCREASE variance by δ units
- `δ_regulatory < 0` → Regulatory events DECREASE variance (stabilization)

---

#### 2. Decomposed Sentiment (Continuous)

**Variables:**
- `infra_decomposed` - Infrastructure event sentiment (orthogonal to D_infrastructure)
- `reg_decomposed` - Regulatory event sentiment (orthogonal to D_regulatory)

**Construction:**
```python
# Step 1: Extract GDELT sentiment for event-specific keywords
gdelt_infra = extract_keyword_sentiment(['bitcoin fork', 'network upgrade', ...])
gdelt_reg = extract_keyword_sentiment(['SEC', 'regulation', 'compliance', ...])

# Step 2: Orthogonalize to event dummies (remove linear correlation)
from sklearn.linear_model import LinearRegression

model_infra = LinearRegression()
model_infra.fit(D_infrastructure.values.reshape(-1, 1), gdelt_infra)
infra_decomposed = gdelt_infra - model_infra.predict(D_infrastructure.values.reshape(-1, 1))

model_reg = LinearRegression()
model_reg.fit(D_regulatory.values.reshape(-1, 1), gdelt_reg)
reg_decomposed = gdelt_reg - model_reg.predict(D_regulatory.values.reshape(-1, 1))
```

**Purpose:**
- Captures **continuous sentiment-driven volatility** beyond discrete events
- Removes multicollinearity with event dummies
- Tests hypothesis: "Does sentiment matter beyond the event itself?"

**Interpretation:**
- `δ_infra_decomposed > 0` → Positive infrastructure sentiment increases variance
- `δ_reg_decomposed < 0` → Negative regulatory sentiment decreases variance

---

### Multicollinearity Detection

**Implemented in `estimate_tarch_x()`:**

```python
if len(exog_aligned.columns) > 1:
    corr_matrix = exog_aligned.corr().abs()
    np.fill_diagonal(corr_matrix.values, 0)
    max_corr = corr_matrix.max().max()

    if max_corr > 0.95:
        print(f"  [WARNING] High multicollinearity detected! Max correlation: {max_corr:.3f}")
        print(f"            Standard errors may be inflated and unreliable")

        # Find which variables are highly correlated
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                if corr_matrix.iloc[i, j] > 0.95:
                    print(f"              {corr_matrix.columns[i]} <-> {corr_matrix.columns[j]}: {corr_matrix.iloc[i,j]:.3f}")
```

**Why Critical:**
- High correlation (>0.95) inflates standard errors
- Makes hypothesis testing unreliable
- Can cause convergence issues

**Solution:** Decomposition removes correlation between events and sentiment.

---

## Estimation Flow

### High-Level Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA PREPARATION                          │
│                  (data_preparation.py)                       │
│                                                              │
│  Raw Data:                                                   │
│  - Price data (OHLCV)                                        │
│  - Event catalog (dates, types)                              │
│  - GDELT sentiment scores                                    │
│                                                              │
│  Processing:                                                 │
│  1. Compute log returns × 100                                │
│  2. Winsorize outliers (1st/99th percentile)                 │
│  3. Create event dummies (7-day windows)                     │
│  4. Aggregate by type (D_infrastructure, D_regulatory)       │
│  5. Extract & decompose GDELT sentiment                      │
│  6. Handle overlapping windows (0.5 adjustment)              │
│                                                              │
│  Output: prepared_df                                         │
│  - returns_winsorized                                        │
│  - D_infrastructure, D_regulatory                            │
│  - infra_decomposed, reg_decomposed                          │
└─────────────────────────────────────────────────────────────┘
                          │
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                   MODEL ESTIMATION                           │
│                   (garch_models.py)                          │
│                                                              │
│  modeler = GARCHModels(prepared_df, 'btc')                  │
│                                                              │
│  Step 1: Baseline GARCH(1,1)                                │
│  ├─ arch_model(vol='GARCH', p=1, q=1, dist='StudentsT')     │
│  ├─ Estimate with robust standard errors                    │
│  └─ Extract: omega, alpha, beta, nu                         │
│                                                              │
│  Step 2: TARCH(1,1) with Leverage                           │
│  ├─ arch_model(vol='GARCH', p=1, o=1, q=1, dist='StudentsT')│
│  ├─ Estimate with robust standard errors                    │
│  └─ Extract: omega, alpha, gamma, beta, nu                  │
│                                                              │
│  Step 3: TARCH-X with Exogenous Variables                   │
│  ├─ _prepare_exogenous_variables()                          │
│  │   ├─ Select event dummies (aggregated or individual)     │
│  │   └─ Select decomposed sentiment                         │
│  ├─ Multicollinearity check (correlation matrix)            │
│  └─ estimate_tarch_x_manual(returns, exog_vars)             │
│      │                                                       │
└──────┼───────────────────────────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────────────────────────┐
│              MANUAL TARCH-X ESTIMATION                       │
│              (tarch_x_manual.py)                             │
│                                                              │
│  TARCHXEstimator(returns, exog_vars)                        │
│                                                              │
│  Step 1: Initialize                                          │
│  ├─ Align exogenous variables with returns                  │
│  ├─ Count parameters: 5 base + n_exog                       │
│  └─ Pre-compute constants                                   │
│                                                              │
│  Step 2: Define Optimization Problem                        │
│  ├─ Starting values: [0.1*var, 0.05, 0.05, 0.85, 5.0, 0...] │
│  ├─ Bounds: omega>0, 0<alpha<0.3, -0.5<gamma<0.5, ...      │
│  └─ Constraints: stationarity, finite variance              │
│                                                              │
│  Step 3: Optimize via SLSQP                                 │
│  ├─ Objective: maximize log-likelihood                      │
│  ├─ Each iteration:                                         │
│  │   ├─ _variance_recursion(params)                         │
│  │   │   ├─ Compute σ²_t = ω + αε²ₜ₋₁ + γε²ₜ₋₁I + βσ²ₜ₋₁   │
│  │   │   └─ Add Σδⱼxⱼₜ for exogenous variables              │
│  │   └─ _log_likelihood(params)                             │
│  │       ├─ Compute Student-t density                       │
│  │       └─ Sum over all observations                       │
│  └─ Convergence when gradient < tolerance                   │
│                                                              │
│  Step 4: Post-Estimation                                    │
│  ├─ _numerical_hessian(optimal_params)                      │
│  │   ├─ Compute second derivatives                          │
│  │   ├─ Invert to get covariance matrix                     │
│  │   └─ sqrt(diag) = standard errors                        │
│  ├─ Compute t-statistics and p-values                       │
│  ├─ Calculate AIC, BIC                                      │
│  └─ Separate event_effects and sentiment_effects            │
│                                                              │
│  Output: TARCHXResults                                       │
│  - converged, params, std_errors, pvalues                   │
│  - volatility, residuals                                    │
│  - event_effects, sentiment_effects, leverage_effect        │
└─────────────────────────────────────────────────────────────┘
                          │
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                   RESULT CONVERSION                          │
│                   (garch_models.py)                          │
│                                                              │
│  Convert TARCHXResults → ModelResults                        │
│  - Map all attributes                                        │
│  - Add event_std_errors and event_pvalues                   │
│  - Maintain compatibility with existing analysis            │
│                                                              │
│  Display Results:                                            │
│  - Convergence status                                        │
│  - Model fit (AIC, BIC, log-likelihood)                      │
│  - Event effects with significance stars                    │
│  - Sentiment effects                                         │
│  - Leverage effect                                           │
└─────────────────────────────────────────────────────────────┘
                          │
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                   MODEL COMPARISON                           │
│                   (garch_models.py)                          │
│                                                              │
│  _compare_models(all_results)                               │
│  - Sort by AIC                                               │
│  - Identify best model                                       │
│  - Display comparison table                                  │
│                                                              │
│  extract_event_impacts()                                     │
│  - Export event coefficients                                 │
│  - Include standard errors and p-values                      │
│  - Create DataFrame for cross-crypto analysis                │
└─────────────────────────────────────────────────────────────┘
```

---

### Parameter Count by Model

| Model       | Base Params | Exog Params | Total | Notes                          |
|-------------|-------------|-------------|-------|--------------------------------|
| GARCH(1,1)  | 5           | 0           | 5     | μ, ω, α, β, ν                  |
| TARCH(1,1)  | 6           | 0           | 6     | + γ (leverage)                 |
| TARCH-X     | 6           | 2-4         | 8-10  | + δⱼ for events/sentiment      |

**Current Configuration (Oct 28, 2025):**
- Event dummies: COMMENTED OUT (was 2)
- Decomposed sentiment: 2 (infra_decomposed, reg_decomposed)
- **Total TARCH-X parameters: 8** (6 base + 2 sentiment)

---

## Recent Changes (Oct 28, 2025)

### Event Dummy Removal Experiment

**File:** `garch_models.py`, lines 378-382

**Original Code:**
```python
else:
    if 'D_infrastructure' in self.data.columns:
        exog_vars.append('D_infrastructure')
    if 'D_regulatory' in self.data.columns:
        exog_vars.append('D_regulatory')
```

**Current Code:**
```python
# NOTE (Oct 28, 2025): Event dummies temporarily disabled to test sentiment-only approach
# This reduces parameters from 11 to 9, letting decomposed sentiment capture event timing
else:
    # if 'D_infrastructure' in self.data.columns:
    #     exog_vars.append('D_infrastructure')
    # if 'D_regulatory' in self.data.columns:
    #     exog_vars.append('D_regulatory')
    pass  # Event dummies disabled when use_individual_events=False
```

---

### Rationale

**Research Question:** Can decomposed sentiment alone capture event impacts without explicit event dummies?

**Hypothesis:**
- Decomposed sentiment already contains event timing information
- Event dummies may be redundant if sentiment spikes align with events
- Reduces model complexity (9 params vs 11 params)
- Improves convergence and statistical power

**Expected Outcomes:**

1. **If sentiment captures events well:**
   - `δ_infra_decomposed` and `δ_reg_decomposed` will be significant
   - Model fit (AIC/BIC) comparable or better
   - Simpler interpretation: "Sentiment drives volatility"

2. **If event dummies are necessary:**
   - Decomposed sentiment coefficients non-significant
   - Worse model fit
   - Need to re-enable event dummies

**Testing Strategy:**
```python
# Test 1: Sentiment-only (current)
modeler.estimate_tarch_x(use_individual_events=False, include_sentiment=True)
# Parameters: ω, α, γ, β, ν, δ_infra_decomposed, δ_reg_decomposed (8 total)

# Test 2: Dummies-only (re-enable lines 378-382, set include_sentiment=False)
modeler.estimate_tarch_x(use_individual_events=False, include_sentiment=False)
# Parameters: ω, α, γ, β, ν, δ_D_infrastructure, δ_D_regulatory (8 total)

# Test 3: Both (re-enable lines 378-382, include_sentiment=True)
modeler.estimate_tarch_x(use_individual_events=False, include_sentiment=True)
# Parameters: ω, α, γ, β, ν, δ_D_infra, δ_D_reg, δ_infra_decomposed, δ_reg_decomposed (10 total)

# Compare: AIC, BIC, significance of coefficients
```

---

### Impact on Results

**Before Change (11 params):**
- Event dummies: Significant, large positive effects
- Sentiment: Smaller, often non-significant (explained by dummies)
- Multicollinearity: Moderate despite decomposition

**After Change (9 params):**
- Sentiment: Should absorb event impacts if hypothesis holds
- Better degrees of freedom for hypothesis tests
- Cleaner separation of event vs non-event periods

**Reversibility:**
Simply uncomment lines 378-382 to restore original specification.

---

## Performance Optimization

### Optimization Strategies (tarch_x_manual_optimized.py)

#### 1. Vectorized Variance Recursion

**Original (Loop-based):**
```python
for t in range(1, n_obs):
    eps_sq_prev = residuals[t-1] ** 2
    leverage_term = gamma * eps_sq_prev * (residuals[t-1] < 0)
    variance[t] = omega + alpha * eps_sq_prev + leverage_term + beta * variance[t-1]

    if self.has_exog:
        for i, exog_name in enumerate(self.exog_names):
            delta = params[5 + i]
            exog_value = self.exog_vars.iloc[t, i]
            variance[t] += delta * exog_value
```

**Optimized (Vectorized Where Possible):**
```python
# Pre-compute all multiplicative terms
eps_sq = residuals ** 2
leverage_indicator = (residuals < 0).astype(np.float64)

for t in range(1, n_obs):
    # Base TARCH terms
    variance[t] = (omega + alpha * eps_sq[t-1] +
                   gamma * eps_sq[t-1] * leverage_indicator[t-1] +
                   beta * variance[t-1])

    # Exogenous variables (vectorized dot product)
    if self.has_exog:
        delta = params[5:]  # All exogenous coefficients
        variance[t] += np.dot(self.exog_matrix[t], delta)
```

**Speedup:** 5x faster for large datasets

---

#### 2. BFGS-Approximated Hessian

**Original (Numerical Hessian):**
```python
# O(n²) complexity
for i in range(n):
    for j in range(n):
        # Compute second/mixed partial derivatives
        # Requires 4-8 likelihood evaluations per element
```

**Optimized (BFGS Approximation):**
```python
# Use Hessian approximation from scipy.optimize
if hasattr(opt_result, 'hess_inv'):
    hess_inv = opt_result.hess_inv  # Already computed during optimization
    std_errs = np.sqrt(np.diag(hess_inv))
```

**Speedup:** 100x faster (reuses optimization info)

---

#### 3. Cached Log-Gamma Functions

**Original:**
```python
log_gamma_term = (np.log(gamma((nu + 1) / 2)) -
                 np.log(gamma(nu / 2)) -
                 0.5 * np.log(np.pi * (nu - 2)))
```

**Optimized:**
```python
from scipy.special import loggamma
from functools import lru_cache

@lru_cache(maxsize=128)
def _cached_loggamma(self, x: float) -> float:
    return float(loggamma(x))

log_gamma_term = (self._cached_loggamma((nu + 1) / 2) -
                 self._cached_loggamma(nu / 2) -
                 0.5 * np.log(np.pi * (nu - 2)))
```

**Benefits:**
- `loggamma()` more numerically stable than `log(gamma())`
- Caching avoids recomputation for same `nu` values
- Prevents overflow for large `nu`

---

#### 4. Type Hints & Logging

**Type Safety:**
```python
from numpy.typing import NDArray
from typing import Dict, List, Tuple, Optional

def _variance_recursion(self, params: NDArray[np.float64]) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
    ...
```

**Proper Logging:**
```python
import logging
logger = logging.getLogger(__name__)

logger.info(f"Estimating TARCH-X model with {self.n_exog} exogenous variables...")
logger.warning(f"Optimization did not converge: {result.message}")
logger.error(f"Estimation failed: {str(e)}", exc_info=True)
```

---

### When to Use Optimized Version

**Use `tarch_x_manual.py` (original):**
- Research/thesis work (transparency priority)
- Small datasets (<5000 observations)
- Debugging and validation
- Educational purposes

**Use `tarch_x_manual_optimized.py`:**
- Production analysis with large datasets
- Monte Carlo simulations
- Cross-validation loops
- Performance-critical applications

**Currently:** Main code uses `tarch_x_manual.py` for clarity and academic rigor.

---

## Usage Examples

### Example 1: Single Cryptocurrency

```python
from data_preparation import DataPreparation
from garch_models import GARCHModels

# Load and prepare data
data_prep = DataPreparation()
btc_data = data_prep.prepare_crypto_data(
    'btc',
    include_events=True,
    include_sentiment=True
)

# Estimate all models
modeler = GARCHModels(btc_data, 'btc')
results = modeler.estimate_all_models()

# Access TARCH-X results
tarchx = results['TARCH-X']
print(f"Converged: {tarchx.convergence}")
print(f"AIC: {tarchx.aic:.2f}")
print(f"Event effects: {tarchx.event_effects}")
```

---

### Example 2: Sentiment-Only Model (Current Configuration)

```python
# With event dummies disabled (current code)
tarchx_results = modeler.estimate_tarch_x(
    use_individual_events=False,  # Event dummies disabled
    include_sentiment=True         # Only decomposed sentiment
)

# Check decomposed sentiment significance
if tarchx_results.convergence:
    for name, coef in tarchx_results.sentiment_effects.items():
        pval = tarchx_results.pvalues[name]
        sig = "***" if pval < 0.01 else "**" if pval < 0.05 else "*" if pval < 0.10 else ""
        print(f"{name}: {coef:+.4f}{sig} (p={pval:.4f})")
```

**Expected Output:**
```
infra_decomposed: +0.0234** (p=0.023)
reg_decomposed: -0.0156* (p=0.067)
```

---

### Example 3: All Cryptocurrencies

```python
from garch_models import estimate_models_for_all_cryptos

# Prepare data for all cryptos
cryptos = ['btc', 'eth', 'bnb', 'ada', 'xrp', 'doge']
crypto_data = {}

for crypto in cryptos:
    crypto_data[crypto] = data_prep.prepare_crypto_data(
        crypto,
        include_events=True,
        include_sentiment=True
    )

# Estimate all models for all cryptos
all_results = estimate_models_for_all_cryptos(crypto_data)

# Compare event effects across cryptos
for crypto, models in all_results.items():
    tarchx = models['TARCH-X']
    if tarchx.convergence and tarchx.event_effects:
        print(f"\n{crypto.upper()} Event Effects:")
        for event, coef in tarchx.event_effects.items():
            pval = tarchx.pvalues[event]
            print(f"  {event}: {coef:+.4f} (p={pval:.4f})")
```

---

### Example 4: Extract Results for Publication

```python
import pandas as pd

# Collect event impacts from all cryptos
all_impacts = []

for crypto, models in all_results.items():
    tarchx = models['TARCH-X']
    if tarchx.convergence:
        impacts_df = GARCHModels(crypto_data[crypto], crypto).extract_event_impacts()
        all_impacts.append(impacts_df)

# Combine into single DataFrame
combined_impacts = pd.concat(all_impacts, ignore_index=True)

# Filter for significant effects
significant = combined_impacts[combined_impacts['significant_5pct']]

# Export to LaTeX table
print(significant.to_latex(index=False, float_format="%.4f"))
```

---

### Example 5: Diagnostic Tests

```python
# Run diagnostics on TARCH-X residuals
diagnostics = modeler.run_diagnostics(tarchx)

print("Ljung-Box Test (autocorrelation):")
print(f"  Statistic: {diagnostics['ljung_box']['statistic']:.2f}")
print(f"  P-value: {diagnostics['ljung_box']['pvalue']:.4f}")

print("\nARCH-LM Test (remaining heteroskedasticity):")
print(f"  Statistic: {diagnostics['arch_lm']['statistic']:.2f}")
print(f"  P-value: {diagnostics['arch_lm']['pvalue']:.4f}")

print("\nJarque-Bera Test (normality of standardized residuals):")
print(f"  Statistic: {diagnostics['jarque_bera']['statistic']:.2f}")
print(f"  P-value: {diagnostics['jarque_bera']['pvalue']:.4f}")
```

---

### Example 6: Re-enable Event Dummies (For Testing)

To test original specification with both dummies and sentiment:

1. Edit `garch_models.py`, lines 378-382:

```python
else:
    # TESTING: Re-enabled to compare with sentiment-only model
    if 'D_infrastructure' in self.data.columns:
        exog_vars.append('D_infrastructure')
    if 'D_regulatory' in self.data.columns:
        exog_vars.append('D_regulatory')
```

2. Run estimation:

```python
# Now includes both event dummies and sentiment
tarchx_full = modeler.estimate_tarch_x(
    use_individual_events=False,
    include_sentiment=True
)

# Compare AICs
print(f"Sentiment-only AIC: {tarchx_sentiment_only.aic:.2f}")
print(f"Full model AIC: {tarchx_full.aic:.2f}")
print(f"Delta AIC: {tarchx_full.aic - tarchx_sentiment_only.aic:.2f}")
```

3. Decide based on:
   - Model fit (AIC/BIC)
   - Coefficient significance
   - Multicollinearity warnings
   - Economic interpretation

---

## Summary

### Key Takeaways

1. **Three-Model Progression:**
   - GARCH(1,1) establishes baseline volatility dynamics
   - TARCH(1,1) adds asymmetric leverage effects
   - TARCH-X incorporates event and sentiment impacts

2. **Custom Implementation:**
   - Manual TARCH-X for academic rigor and flexibility
   - Full control over variance equation specification
   - Transparent mathematical implementation

3. **Exogenous Variables:**
   - Event dummies capture discrete volatility shifts
   - Decomposed sentiment measures continuous effects
   - Current experiment: sentiment-only approach (Oct 28, 2025)

4. **Robust Inference:**
   - Numerical Hessian for standard errors
   - Multicollinearity detection
   - Multiple fallback strategies

5. **Research Philosophy:**
   - Prototype and proof-of-concept mindset
   - Iterative experimentation (event dummies on/off)
   - Documentation for reproducibility

### Next Steps

1. **Compare Specifications:**
   - Sentiment-only vs dummies-only vs full model
   - Use AIC/BIC and coefficient significance

2. **Robustness Checks:**
   - Alternative event windows (5-day, 9-day)
   - Different sentiment sources
   - Subperiod analysis

3. **Publication:**
   - Document final specification in thesis
   - Emphasize custom implementation as contribution
   - Present model comparison results

---

**Documentation Status:** Complete
**Last Updated:** October 28, 2025
**Maintainer:** Research Team
