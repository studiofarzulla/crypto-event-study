"""
Minimal public DataPreparation shim.

The full pre-revision data pipeline (the original ``data_preparation.py``) is not
part of the public repo. The only method any shipped c-series script needs is the
canonical rolling winsoriser, used by ``c8c_mechanical_rolling_winsor.py``. This
shim provides exactly that -- identical to the canonical rule (clip each
observation to a 30-day rolling mean +/- ``n_std`` sigma band, ``min_periods=1``)
-- so the public repo runs end to end from ``data/*.csv`` alone.
"""

import pandas as pd


class DataPreparation:
    def __init__(self, data_path: str | None = None):
        self.data_path = data_path

    @staticmethod
    def winsorize_returns(returns: pd.Series, window: int = 30, n_std: float = 5.0) -> pd.Series:
        """Clip each return to a rolling mean +/- n_std sigma band (canonical rule)."""
        rolling_mean = returns.rolling(window=window, min_periods=1).mean()
        rolling_std = returns.rolling(window=window, min_periods=1).std()
        upper = rolling_mean + n_std * rolling_std
        lower = rolling_mean - n_std * rolling_std
        return returns.clip(lower=lower, upper=upper)
