# Type Hints Implementation Guide
## Adding Type Safety to Event Study Codebase

---

## Why Type Hints Matter for Academic Research

1. **Catch bugs before runtime** - mypy can detect type errors in your analysis pipeline
2. **Self-documenting code** - reviewers understand interfaces immediately
3. **IDE support** - autocomplete and inline documentation
4. **Refactoring confidence** - know what breaks when you change signatures

---

## Quick Reference: Common Types in Financial Econometrics

```python
from typing import Dict, List, Tuple, Optional, Union, Any
from numpy.typing import NDArray
import numpy as np
import pandas as pd

# Pandas types
returns_series: pd.Series  # Time series of returns
price_data: pd.DataFrame   # DataFrame with price columns
date_index: pd.DatetimeIndex  # Datetime index

# NumPy types
params_array: NDArray[np.float64]  # Array of float64 parameters
residuals: NDArray[np.float64]     # Residual array

# Scalar types
log_likelihood: float
num_iterations: int
converged: bool
crypto_symbol: str

# Optional types (can be None)
exog_vars: Optional[pd.DataFrame] = None

# Union types (multiple possibilities)
data_source: Union[str, Path]  # Can be string or Path object

# Dictionary types
model_results: Dict[str, float]  # Keys are strings, values are floats
nested_results: Dict[str, Dict[str, float]]  # Nested dictionaries

# List types
event_ids: List[int]
crypto_list: List[str]

# Tuple types (fixed length)
ci_bounds: Tuple[float, float]  # Exactly 2 floats
variance_and_resid: Tuple[NDArray[np.float64], NDArray[np.float64]]

# Function types
from typing import Callable
objective_function: Callable[[NDArray[np.float64]], float]
```

---

## Example: data_preparation.py with Full Type Hints

```python
"""
Data preparation module with comprehensive type hints.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from pathlib import Path
from numpy.typing import NDArray

class DataPreparation:
    """Main class for preparing cryptocurrency event study data."""

    def __init__(self, data_path: Optional[str] = None) -> None:
        """
        Initialize the data preparation module.

        Args:
            data_path: Path to data directory (defaults to config.DATA_DIR)
        """
        self.data_path: Path = Path(data_path) if data_path else Path(config.DATA_DIR)
        self.cryptocurrencies: List[str] = ['btc', 'eth', 'xrp', 'bnb', 'ltc', 'ada']
        self.start_date: pd.Timestamp = pd.Timestamp('2019-01-01', tz='UTC')
        self.end_date: pd.Timestamp = pd.Timestamp('2025-08-31', tz='UTC')

    def load_crypto_prices(self, crypto: str) -> pd.DataFrame:
        """
        Load cryptocurrency price data from CSV file.

        Args:
            crypto: Cryptocurrency symbol (e.g., 'btc', 'eth')

        Returns:
            DataFrame with date index and price columns

        Raises:
            FileNotFoundError: If price data file doesn't exist
            ValueError: If required columns are missing
        """
        file_path: Path = self.data_path / f"{crypto}.csv"

        if not file_path.exists():
            raise FileNotFoundError(f"Price data file not found: {file_path}")

        df: pd.DataFrame = pd.read_csv(file_path)
        df['snapped_at'] = self._ensure_utc_timezone(df['snapped_at'])
        df.set_index('snapped_at', inplace=True)

        return df

    def calculate_log_returns(self, prices: pd.Series) -> pd.Series:
        """
        Calculate log returns from price series.

        Args:
            prices: Series of prices

        Returns:
            Series of log returns (multiplied by 100 for percentage)
        """
        log_returns: pd.Series = np.log(prices / prices.shift(1)) * 100
        return log_returns.dropna()

    def winsorize_returns(
        self,
        returns: pd.Series,
        window: int = 30,
        n_std: float = 5.0
    ) -> pd.Series:
        """
        Winsorize returns at specified standard deviations.

        Args:
            returns: Series of returns
            window: Rolling window size in days
            n_std: Number of standard deviations for winsorization

        Returns:
            Winsorized returns series
        """
        rolling_mean: pd.Series = returns.rolling(window=window, min_periods=1).mean()
        rolling_std: pd.Series = returns.rolling(window=window, min_periods=1).std()

        upper_bound: pd.Series = rolling_mean + n_std * rolling_std
        lower_bound: pd.Series = rolling_mean - n_std * rolling_std

        winsorized: pd.Series = returns.clip(lower=lower_bound, upper=upper_bound)
        return winsorized

    def create_event_window(
        self,
        event_date: pd.Timestamp,
        days_before: int = 3,
        days_after: int = 3
    ) -> List[pd.Timestamp]:
        """
        Create event window dates.

        Args:
            event_date: Date of the event
            days_before: Days before event
            days_after: Days after event

        Returns:
            List of dates in event window
        """
        event_date = self._ensure_utc_timezone(event_date)
        start: pd.Timestamp = event_date - timedelta(days=days_before)
        end: pd.Timestamp = event_date + timedelta(days=days_after)

        return pd.date_range(start=start, end=end, freq='D').tolist()

    def create_event_dummies(
        self,
        date_index: pd.DatetimeIndex,
        events_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Create event dummy variables with special overlap handling.

        Args:
            date_index: DatetimeIndex for the data
            events_df: DataFrame with event information

        Returns:
            DataFrame with event dummy variables
        """
        dummies: pd.DataFrame = pd.DataFrame(index=date_index)

        # Process each event
        for idx, event in events_df.iterrows():
            event_id: int = int(event['event_id'])
            event_date: pd.Timestamp = self._ensure_utc_timezone(event['date'])

            # ... rest of implementation

        return dummies

    def prepare_crypto_data(
        self,
        crypto: str,
        include_events: bool = True,
        include_sentiment: bool = True
    ) -> pd.DataFrame:
        """
        Complete data preparation pipeline for a single cryptocurrency.

        Args:
            crypto: Cryptocurrency symbol
            include_events: Whether to include event dummies
            include_sentiment: Whether to include sentiment data

        Returns:
            Prepared DataFrame with all features
        """
        print(f"Preparing data for {crypto.upper()}...")

        price_data: pd.DataFrame = self.load_crypto_prices(crypto)
        price_data['returns'] = self.calculate_log_returns(price_data['price'])
        price_data['returns_winsorized'] = self.winsorize_returns(price_data['returns'])

        result: pd.DataFrame = price_data[['price', 'returns', 'returns_winsorized']].copy()

        if include_events:
            events_df: pd.DataFrame = self.load_events()
            event_dummies: pd.DataFrame = self.create_event_dummies(result.index, events_df)
            result = result.merge(event_dummies, left_index=True, right_index=True, how='left')

        return result

    def prepare_all_cryptos(self, **kwargs: Any) -> Dict[str, pd.DataFrame]:
        """
        Prepare data for all cryptocurrencies.

        Args:
            **kwargs: Arguments to pass to prepare_crypto_data

        Returns:
            Dictionary mapping crypto symbols to prepared DataFrames
        """
        results: Dict[str, pd.DataFrame] = {}

        for crypto in self.cryptocurrencies:
            try:
                results[crypto] = self.prepare_crypto_data(crypto, **kwargs)
            except Exception as e:
                warnings.warn(f"Failed to prepare data for {crypto}: {str(e)}")
                continue

        return results

    def validate_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate prepared data for quality issues.

        Args:
            df: Prepared DataFrame

        Returns:
            Dictionary with validation results
        """
        validation: Dict[str, Any] = {}

        # Check for missing values
        validation['missing_values'] = df.isnull().sum().to_dict()

        # Check for infinite values
        if 'returns_winsorized' in df.columns:
            validation['infinite_returns'] = int(np.isinf(df['returns_winsorized']).sum())

        return validation
```

---

## mypy Configuration

Create `mypy.ini` in your project root:

```ini
[mypy]
python_version = 3.10
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True

# Third-party libraries without stubs
[mypy-arch.*]
ignore_missing_imports = True

[mypy-scipy.*]
ignore_missing_imports = True

[mypy-tqdm.*]
ignore_missing_imports = True

[mypy-joblib.*]
ignore_missing_imports = True
```

---

## Running Type Checks

```bash
# Install mypy
pip install mypy

# Check single file
mypy event_study/code/tarch_x_manual_optimized.py

# Check entire codebase
mypy event_study/code/

# Generate HTML report
mypy --html-report mypy_report/ event_study/code/
```

---

## Common Type Hint Patterns in Your Codebase

### 1. ModelResults Dataclass

```python
from dataclasses import dataclass

@dataclass
class ModelResults:
    """Container for model estimation results."""
    model_type: str
    crypto: str
    aic: float
    bic: float
    log_likelihood: float
    parameters: Dict[str, float]
    std_errors: Dict[str, float]
    pvalues: Dict[str, float]
    convergence: bool
    iterations: int
    volatility: pd.Series
    residuals: pd.Series
    leverage_effect: Optional[float] = None
    event_effects: Optional[Dict[str, float]] = None
```

### 2. Function Returning Multiple Values

```python
def _variance_recursion(
    self,
    params: NDArray[np.float64]
) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
    """
    Returns:
        Tuple of (conditional_variance, residuals)
    """
    variance = np.zeros(self.n_obs)
    residuals = self.returns.values
    return variance, residuals
```

### 3. Optional Parameters with Defaults

```python
def bootstrap_analysis(
    returns: pd.Series,
    n_bootstrap: int = 500,
    seed: Optional[int] = None,
    show_progress: bool = True
) -> Dict[str, Any]:
    """
    Args:
        seed: Random seed (None for random)
    """
    if seed is None:
        seed = np.random.randint(0, 2**31)
```

### 4. Generic Dictionary Types

```python
# Nested model results
all_results: Dict[str, Dict[str, ModelResults]]

# Mixed value types
config: Dict[str, Union[str, int, float, bool]]

# Any type (avoid when possible)
metadata: Dict[str, Any]
```

---

## Gradual Typing Strategy

You don't need to add all type hints at once. Recommended order:

1. **Start with function signatures** (inputs and outputs)
2. **Add return types** for all functions
3. **Add parameter types** for all functions
4. **Type class attributes** in `__init__`
5. **Type local variables** in critical functions (optional)

---

## Type Stub Files for Third-Party Libraries

If mypy complains about missing stubs:

```bash
# Install type stubs for pandas, numpy
pip install pandas-stubs types-numpy

# Or ignore missing imports (in mypy.ini)
[mypy-arch.*]
ignore_missing_imports = True
```

---

## Common Type Errors and Fixes

### Error: Incompatible return type

```python
# Error
def get_aic(self) -> float:
    return self.aic if self.aic else None  # Returns Optional[float]!

# Fix
def get_aic(self) -> Optional[float]:
    return self.aic if self.aic else None

# Or
def get_aic(self) -> float:
    return self.aic if self.aic is not None else np.nan
```

### Error: Argument type mismatch

```python
# Error
def process_returns(returns: pd.Series) -> None:
    ...

process_returns(df['returns'].values)  # Passing NDArray, not Series!

# Fix
process_returns(pd.Series(df['returns'].values))
```

### Error: Missing return statement

```python
# Error
def estimate_model(self) -> ModelResults:
    if self.converged:
        return self.results
    # Missing return for else case!

# Fix
def estimate_model(self) -> ModelResults:
    if self.converged:
        return self.results
    else:
        return self._create_failed_result()
```

---

## Type Hints Cheat Sheet

| Concept | Type Hint | Example |
|---------|-----------|---------|
| Any type | `Any` | `data: Any` |
| None type | `None` | `def f() -> None:` |
| Optional | `Optional[T]` | `x: Optional[int] = None` |
| Union | `Union[A, B]` | `x: Union[int, float]` |
| List | `List[T]` | `names: List[str]` |
| Dict | `Dict[K, V]` | `params: Dict[str, float]` |
| Tuple (fixed) | `Tuple[T, U]` | `bounds: Tuple[float, float]` |
| Tuple (variable) | `Tuple[T, ...]` | `args: Tuple[int, ...]` |
| Callable | `Callable[[Arg], Ret]` | `f: Callable[[int], str]` |
| NumPy array | `NDArray[T]` | `x: NDArray[np.float64]` |

---

## Benefits You'll See

1. **Catch bugs early**: mypy will find parameter mismatches before runtime
2. **Better IDE support**: VS Code/PyCharm autocomplete works better
3. **Documentation**: Types explain what functions expect/return
4. **Refactoring safety**: Know what breaks when you change code
5. **Reviewer confidence**: Clear interfaces for journal reviewers

---

**Next Steps:**

1. Add type hints to function signatures in your existing code
2. Run mypy to check for type errors
3. Fix any issues mypy finds
4. Add to your CI/CD pipeline (optional but recommended)

