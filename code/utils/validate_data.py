"""
Data Validation Script for Event Study Visualizations
======================================================

Run this before generating figures to catch formatting errors early.

Usage:
    python validate_data.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from code.core import config

DATA_DIR = Path(config.DATA_DIR)

class ValidationError(Exception):
    """Custom exception for validation failures"""
    pass

def validate_events_csv():
    """Validate events.csv format and content"""
    print("\n[1/4] Validating events.csv...")

    filepath = DATA_DIR / 'events.csv'
    if not filepath.exists():
        raise ValidationError(f"File not found: {filepath}")

    df = pd.read_csv(filepath)

    # Check required columns
    required_cols = ['date', 'event_name', 'event_type', 'impact_magnitude', 'p_value']
    missing_cols = set(required_cols) - set(df.columns)
    if missing_cols:
        raise ValidationError(f"Missing columns: {missing_cols}")

    # Check data types and ranges
    errors = []

    # Validate dates
    try:
        pd.to_datetime(df['date'])
    except Exception as e:
        errors.append(f"Invalid date format: {e}")

    # Validate event types
    valid_types = {'infrastructure', 'regulatory'}
    invalid_types = set(df['event_type'].unique()) - valid_types
    if invalid_types:
        errors.append(f"Invalid event_type values: {invalid_types}. Must be 'infrastructure' or 'regulatory'")

    # Validate impact magnitudes (should be reasonable, e.g., -1 to 1)
    if (df['impact_magnitude'].abs() > 1).any():
        errors.append("impact_magnitude values seem too large (>100%). Check if they should be decimals (e.g., 0.05 not 5)")

    # Validate p-values (must be 0-1)
    if ((df['p_value'] < 0) | (df['p_value'] > 1)).any():
        errors.append("p_value must be between 0 and 1")

    # Check for missing values
    if df.isnull().any().any():
        errors.append(f"Missing values detected:\n{df.isnull().sum()}")

    # Count events
    n_infra = (df['event_type'] == 'infrastructure').sum()
    n_reg = (df['event_type'] == 'regulatory').sum()

    if errors:
        raise ValidationError('\n'.join(errors))

    print(f"  ✓ Valid: {len(df)} events ({n_infra} infrastructure, {n_reg} regulatory)")
    print(f"  ✓ Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"  ✓ Significant events (p<0.05): {(df['p_value'] < 0.05).sum()}")

    return df

def validate_volatility_csv():
    """Validate volatility_results.csv format and content"""
    print("\n[2/4] Validating volatility_results.csv...")

    filepath = DATA_DIR / 'volatility_results.csv'
    if not filepath.exists():
        raise ValidationError(f"File not found: {filepath}")

    df = pd.read_csv(filepath)

    # Check required columns
    required_cols = ['period', 'event_type', 'mean_volatility', 'ci_lower', 'ci_upper']
    missing_cols = set(required_cols) - set(df.columns)
    if missing_cols:
        raise ValidationError(f"Missing columns: {missing_cols}")

    errors = []

    # Validate periods
    valid_periods = {'Pre-Event\n(-10 to -1)', 'Event\n(0 to +5)', 'Post-Event\n(+6 to +20)'}
    invalid_periods = set(df['period'].unique()) - valid_periods
    if invalid_periods:
        errors.append(f"Invalid period values: {invalid_periods}\nExpected: {valid_periods}")

    # Validate event types
    valid_types = {'infrastructure', 'regulatory'}
    invalid_types = set(df['event_type'].unique()) - valid_types
    if invalid_types:
        errors.append(f"Invalid event_type values: {invalid_types}")

    # Validate volatility values (should be positive)
    if (df['mean_volatility'] <= 0).any():
        errors.append("mean_volatility must be positive")

    # Validate confidence intervals
    if (df['ci_lower'] > df['mean_volatility']).any():
        errors.append("ci_lower cannot be greater than mean_volatility")
    if (df['ci_upper'] < df['mean_volatility']).any():
        errors.append("ci_upper cannot be less than mean_volatility")

    # Check structure: should have 6 rows (3 periods × 2 event types)
    expected_rows = 6
    if len(df) != expected_rows:
        errors.append(f"Expected {expected_rows} rows (3 periods × 2 event types), got {len(df)}")

    if errors:
        raise ValidationError('\n'.join(errors))

    print(f"  ✓ Valid: {len(df)} period-event type combinations")
    print(f"  ✓ Mean volatility range: {df['mean_volatility'].min():.2f}% to {df['mean_volatility'].max():.2f}%")

    return df

def validate_impact_matrix_csv():
    """Validate impact_matrix.csv format and content"""
    print("\n[3/4] Validating impact_matrix.csv...")

    filepath = DATA_DIR / 'impact_matrix.csv'
    if not filepath.exists():
        raise ValidationError(f"File not found: {filepath}")

    df = pd.read_csv(filepath, index_col=0)

    errors = []

    # Check it's actually a matrix (no missing values in expected grid)
    if df.isnull().any().any():
        errors.append(f"Missing values detected:\n{df.isnull().sum()}")

    # Validate values are reasonable (typically -1 to 1 for returns)
    if (df.abs() > 1).any().any():
        errors.append("Some impact values > 100%. Check if they should be decimals (e.g., 0.05 not 5)")

    # Check dimensions
    n_events, n_cryptos = df.shape
    if n_events == 0 or n_cryptos == 0:
        errors.append(f"Matrix has zero dimension: {n_events} events × {n_cryptos} cryptocurrencies")

    if errors:
        raise ValidationError('\n'.join(errors))

    print(f"  ✓ Valid: {n_events} events × {n_cryptos} cryptocurrencies")
    print(f"  ✓ Cryptocurrencies: {', '.join(df.columns[:5])}{'...' if n_cryptos > 5 else ''}")
    print(f"  ✓ Impact range: {df.min().min():.3f} to {df.max().max():.3f}")

    return df

def validate_model_results_csv():
    """Validate model_results.csv format and content"""
    print("\n[4/4] Validating model_results.csv...")

    filepath = DATA_DIR / 'model_results.csv'
    if not filepath.exists():
        raise ValidationError(f"File not found: {filepath}")

    df = pd.read_csv(filepath)

    # Check required columns
    required_cols = ['model_name', 'rmse', 'mae', 'aic', 'bic']
    missing_cols = set(required_cols) - set(df.columns)
    if missing_cols:
        raise ValidationError(f"Missing columns: {missing_cols}")

    errors = []

    # Validate error metrics are positive
    if (df['rmse'] <= 0).any():
        errors.append("RMSE must be positive")
    if (df['mae'] <= 0).any():
        errors.append("MAE must be positive")

    # Validate information criteria
    # AIC/BIC can be negative, but should be finite
    if (~np.isfinite(df['aic'])).any():
        errors.append("AIC contains non-finite values")
    if (~np.isfinite(df['bic'])).any():
        errors.append("BIC contains non-finite values")

    # Check for duplicates
    if df['model_name'].duplicated().any():
        errors.append(f"Duplicate model names: {df[df['model_name'].duplicated()]['model_name'].tolist()}")

    # Check we have at least 2 models (otherwise comparison is meaningless)
    if len(df) < 2:
        errors.append("Need at least 2 models for comparison")

    if errors:
        raise ValidationError('\n'.join(errors))

    print(f"  ✓ Valid: {len(df)} models")
    print(f"  ✓ Models: {', '.join(df['model_name'])}")
    print(f"  ✓ Best RMSE: {df.loc[df['rmse'].idxmin(), 'model_name']} ({df['rmse'].min():.3f})")
    print(f"  ✓ Best AIC: {df.loc[df['aic'].idxmin(), 'model_name']} ({df['aic'].min():.1f})")

    return df

def cross_validate_consistency():
    """Check consistency across multiple files"""
    print("\n[Bonus] Cross-file consistency checks...")

    events_df = pd.read_csv(DATA_DIR / 'events.csv')
    impact_df = pd.read_csv(DATA_DIR / 'impact_matrix.csv', index_col=0)

    # Check event names match
    events_set = set(events_df['event_name'])
    impact_set = set(impact_df.index)

    missing_in_impact = events_set - impact_set
    missing_in_events = impact_set - events_set

    if missing_in_impact:
        print(f"  ⚠ Events in events.csv but not in impact_matrix.csv: {missing_in_impact}")
    if missing_in_events:
        print(f"  ⚠ Events in impact_matrix.csv but not in events.csv: {missing_in_events}")

    if not (missing_in_impact or missing_in_events):
        print(f"  ✓ Event names consistent across files ({len(events_set)} events)")

def main():
    """Run all validation checks"""
    print("=" * 80)
    print("EVENT STUDY DATA VALIDATION")
    print("=" * 80)

    try:
        # Validate each file
        events_df = validate_events_csv()
        volatility_df = validate_volatility_csv()
        impact_df = validate_impact_matrix_csv()
        model_df = validate_model_results_csv()

        # Cross-validate
        cross_validate_consistency()

        print("\n" + "=" * 80)
        print("✓ ALL VALIDATION CHECKS PASSED")
        print("=" * 80)
        print("\nYour data files are properly formatted.")
        print("You can now run: python create_publication_figures.py")
        print()

    except ValidationError as e:
        print("\n" + "=" * 80)
        print("✗ VALIDATION FAILED")
        print("=" * 80)
        print(f"\nError details:\n{e}")
        print("\nPlease fix the issues above and run validation again.")
        print("See data_preparation_template.py for correct format examples.")
        print()
        return 1

    except FileNotFoundError as e:
        print("\n" + "=" * 80)
        print("✗ DATA FILES NOT FOUND")
        print("=" * 80)
        print(f"\n{e}")
        print(f"\nCreate the required data files in: {DATA_DIR}/")
        print("Use data_preparation_template.py as a guide.")
        print()
        return 1

    return 0

if __name__ == '__main__':
    exit(main())
