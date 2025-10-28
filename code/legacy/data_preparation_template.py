"""
Data Preparation Template for Event Study Visualizations
==========================================================

This script shows how to prepare your actual analysis results
for the publication figure generator.

Adapt this to your specific analysis pipeline.
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

DATA_DIR = Path('/home/kawaiikali/event-study/data')
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# 1. EVENTS DATA
# ============================================================================

def prepare_events_data():
    """
    Prepare events.csv with the following columns:
    - date: Event date (YYYY-MM-DD format)
    - event_name: Short descriptive name
    - event_type: 'infrastructure' or 'regulatory'
    - impact_magnitude: Cumulative abnormal return (decimal, e.g., 0.05 for 5%)
    - p_value: Statistical significance level
    """

    # Example structure - replace with your actual data
    events = pd.DataFrame({
        'date': [
            '2022-06-15',  # Example: Celsius Network freeze
            '2022-09-15',  # Example: Ethereum Merge
            # ... add your 18 events
        ],
        'event_name': [
            'Celsius Network Freeze',
            'Ethereum Merge',
            # ... add corresponding names
        ],
        'event_type': [
            'infrastructure',
            'infrastructure',
            # ... infrastructure or regulatory
        ],
        'impact_magnitude': [
            -0.087,  # -8.7% CAR
            0.042,   # +4.2% CAR
            # ... your calculated CARs
        ],
        'p_value': [
            0.003,   # Highly significant
            0.045,   # Significant at 5%
            # ... from your statistical tests
        ]
    })

    events.to_csv(DATA_DIR / 'events.csv', index=False)
    print(f"✓ Saved events.csv ({len(events)} events)")
    return events

# ============================================================================
# 2. VOLATILITY DATA
# ============================================================================

def prepare_volatility_data():
    """
    Prepare volatility_results.csv with:
    - period: 'Pre-Event\n(-10 to -1)', 'Event\n(0 to +5)', 'Post-Event\n(+6 to +20)'
    - event_type: 'infrastructure' or 'regulatory'
    - mean_volatility: Average realized volatility (% per day)
    - ci_lower: Lower bound of 95% confidence interval
    - ci_upper: Upper bound of 95% confidence interval
    """

    # Calculate these from your GARCH/realized volatility analysis
    volatility = pd.DataFrame({
        'period': [
            'Pre-Event\n(-10 to -1)',
            'Event\n(0 to +5)',
            'Post-Event\n(+6 to +20)',
        ] * 2,  # Repeat for both event types

        'event_type': [
            'infrastructure',
            'infrastructure',
            'infrastructure',
            'regulatory',
            'regulatory',
            'regulatory',
        ],

        'mean_volatility': [
            2.45,  # Pre-event infrastructure
            4.12,  # Event window infrastructure
            3.05,  # Post-event infrastructure
            2.78,  # Pre-event regulatory
            5.43,  # Event window regulatory
            3.67,  # Post-event regulatory
        ],

        'ci_lower': [
            2.15, 3.78, 2.71,  # Infrastructure CIs
            2.48, 5.01, 3.32,  # Regulatory CIs
        ],

        'ci_upper': [
            2.75, 4.46, 3.39,  # Infrastructure CIs
            3.08, 5.85, 4.02,  # Regulatory CIs
        ]
    })

    volatility.to_csv(DATA_DIR / 'volatility_results.csv', index=False)
    print("✓ Saved volatility_results.csv")
    return volatility

# ============================================================================
# 3. IMPACT MATRIX
# ============================================================================

def prepare_impact_matrix():
    """
    Prepare impact_matrix.csv as a matrix:
    - Rows: Event names (same as in events.csv)
    - Columns: Cryptocurrency tickers (BTC, ETH, etc.)
    - Values: Cumulative abnormal returns (%)
    """

    # List of events (should match events.csv)
    event_names = [
        'Celsius Network Freeze',
        'Ethereum Merge',
        'FTX Collapse',
        # ... all 18 events
    ]

    # List of cryptocurrencies in your sample
    cryptos = ['BTC', 'ETH', 'BNB', 'SOL', 'ADA', 'XRP', 'DOT', 'MATIC']

    # Create matrix of CARs (event × crypto)
    # Replace with your actual calculated CARs
    impact_data = np.array([
        [-0.052, -0.089, -0.067, -0.145, -0.078, -0.034, -0.092, -0.112],  # Event 1
        [0.023, 0.087, 0.034, 0.045, 0.067, 0.012, 0.056, 0.078],          # Event 2
        # ... add rows for each event
    ])

    impact_matrix = pd.DataFrame(
        impact_data,
        index=event_names,
        columns=cryptos
    )

    impact_matrix.to_csv(DATA_DIR / 'impact_matrix.csv')
    print(f"✓ Saved impact_matrix.csv ({impact_matrix.shape[0]} events × {impact_matrix.shape[1]} cryptos)")
    return impact_matrix

# ============================================================================
# 4. MODEL RESULTS
# ============================================================================

def prepare_model_results():
    """
    Prepare model_results.csv with:
    - model_name: Name of the model (e.g., 'Market Model', 'GARCH(1,1)')
    - rmse: Root mean squared error from out-of-sample forecast
    - mae: Mean absolute error from out-of-sample forecast
    - aic: Akaike Information Criterion
    - bic: Bayesian Information Criterion
    """

    # Extract these from your model estimation output
    models = pd.DataFrame({
        'model_name': [
            'Market Model',
            'GARCH(1,1)',
            'EGARCH',
            'GJR-GARCH',
            'Multi-Factor',
        ],

        'rmse': [
            3.452,  # From out-of-sample forecasts
            2.871,
            2.923,
            2.847,
            3.124,
        ],

        'mae': [
            2.763,
            2.314,
            2.356,
            2.281,
            2.542,
        ],

        'aic': [
            4521.34,  # From model estimation
            4398.67,
            4405.23,
            4392.15,
            4467.89,
        ],

        'bic': [
            4536.78,  # BIC = AIC + penalty for parameters
            4429.54,
            4436.01,
            4422.93,
            4498.67,
        ]
    })

    models.to_csv(DATA_DIR / 'model_results.csv', index=False)
    print("✓ Saved model_results.csv")
    return models

# ============================================================================
# HELPER: CALCULATE CAR FROM DAILY RETURNS
# ============================================================================

def calculate_car(returns, event_window=(0, 5)):
    """
    Calculate Cumulative Abnormal Return

    Parameters:
    -----------
    returns : pd.Series
        Daily abnormal returns indexed by date
    event_window : tuple
        (start_day, end_day) relative to event (0 = event day)

    Returns:
    --------
    float : CAR over the event window
    """
    start, end = event_window
    car = returns.iloc[start:end+1].sum()
    return car

# ============================================================================
# HELPER: CALCULATE REALIZED VOLATILITY
# ============================================================================

def calculate_realized_volatility(returns, annualize=False):
    """
    Calculate realized volatility from returns

    Parameters:
    -----------
    returns : pd.Series
        Daily returns
    annualize : bool
        If True, multiply by sqrt(252) for annual volatility

    Returns:
    --------
    float : Realized volatility (%)
    """
    vol = returns.std() * 100  # Convert to percentage
    if annualize:
        vol *= np.sqrt(252)
    return vol

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Run all data preparation functions

    Customize this based on your actual analysis pipeline.
    """
    print("=" * 80)
    print("EVENT STUDY DATA PREPARATION")
    print("=" * 80)
    print()

    print("This is a TEMPLATE script. Please customize with your actual data.")
    print()
    print("Current mode: Creating example structure")
    print("Modify the functions above to load your actual analysis results.")
    print()

    # Uncomment these when you've filled in your actual data:
    # events = prepare_events_data()
    # volatility = prepare_volatility_data()
    # impact = prepare_impact_matrix()
    # models = prepare_model_results()

    print("=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print()
    print("1. Fill in the prepare_*() functions with your actual data")
    print("2. Run this script: python data_preparation_template.py")
    print("3. Verify CSV files in: /home/kawaiikali/event-study/data/")
    print("4. Run figure generator: python create_publication_figures.py")
    print()

if __name__ == '__main__':
    main()
