"""
Robustness check for overlapping event treatment.

Tests sensitivity of results to alternative weighting schemes for overlapping events:
1. Current: Both events set to 0.5 (conservative, independent effects)
2. Max: Dominant event gets 1.0, other gets 0.0
3. Additive: Both events get 1.0 (full additive effects)

Known overlaps (from data_preparation.py):
- Aug 7-8, 2021: EIP-1559 (event 17) + Polygon hack (event 18)
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import pickle

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from data_preparation import EventDataPreparation
from garch_models import GARCHModels
from config import CRYPTO_SYMBOLS, DATA_DIR, OUTPUTS_DIR


def create_overlap_variants(data_prep):
    """
    Create three versions of event dummies with different overlap treatments.

    Returns:
        dict: Keys are 'current', 'max', 'additive' with corresponding dummy DataFrames
    """
    # Get base data
    merged_data = data_prep.merged_data.copy()

    # Overlapping events (from data_preparation.py lines 258-280)
    overlap_dates = pd.date_range('2021-08-07', '2021-08-08')
    overlap_events = ['D_event_17', 'D_event_18']  # EIP-1559, Polygon hack

    variants = {}

    # Variant 1: Current approach (0.5 each)
    dummies_current = data_prep.event_dummies.copy()
    variants['current'] = dummies_current

    # Variant 2: Max (dominant event only)
    dummies_max = data_prep.event_dummies.copy()
    # EIP-1559 (event 17) is infrastructure, arguably more impactful
    for date in overlap_dates:
        if date in dummies_max.index:
            dummies_max.loc[date, 'D_event_17'] = 1.0  # Dominant
            dummies_max.loc[date, 'D_event_18'] = 0.0  # Suppressed
    variants['max'] = dummies_max

    # Variant 3: Additive (both at 1.0)
    dummies_additive = data_prep.event_dummies.copy()
    for date in overlap_dates:
        if date in dummies_additive.index:
            dummies_additive.loc[date, 'D_event_17'] = 1.0
            dummies_additive.loc[date, 'D_event_18'] = 1.0
    variants['additive'] = dummies_additive

    return variants


def estimate_robustness_models(variant_name, event_dummies):
    """
    Estimate TARCH-X models with alternative event dummy specification.

    Args:
        variant_name: 'current', 'max', or 'additive'
        event_dummies: DataFrame of event dummies with specified overlap treatment

    Returns:
        dict: Model results for each cryptocurrency
    """
    print(f"\nEstimating models with '{variant_name}' overlap treatment...")

    # Initialize analyzer
    garch_analyzer = GARCHModels()

    # We need to re-prepare data with new dummies
    # This is a bit hacky but avoids rewriting entire data prep
    from data_preparation import EventDataPreparation

    data_prep = EventDataPreparation()
    data_prep.load_data()
    data_prep.prepare_event_dummies()
    data_prep.prepare_gdelt_sentiment()
    data_prep.merge_data()

    # Replace event dummies with our variant
    data_prep.event_dummies = event_dummies
    data_prep.merge_data()  # Re-merge with new dummies

    # Estimate models
    models = {}
    for crypto in CRYPTO_SYMBOLS:
        print(f"  {crypto}...", end=' ')
        crypto_data = data_prep.merged_data[data_prep.merged_data['cryptocurrency'] == crypto].copy()

        result = garch_analyzer.estimate_tarch_x(crypto_data, crypto)
        models[crypto] = result

        if result.convergence:
            infra_coef = result.event_effects.get('D_infrastructure', np.nan)
            reg_coef = result.event_effects.get('D_regulatory', np.nan)
            print(f"✓ Infra={infra_coef:.4f}, Reg={reg_coef:.4f}")
        else:
            print("✗ Failed to converge")

    return models


def compare_event_coefficients(results_dict):
    """
    Compare infrastructure and regulatory coefficients across overlap treatments.

    Args:
        results_dict: dict of {variant_name: {crypto: ModelResults}}

    Returns:
        DataFrame with comparison
    """
    rows = []

    for variant, models in results_dict.items():
        for crypto, model_result in models.items():
            if not model_result.convergence:
                continue

            infra_coef = model_result.event_effects.get('D_infrastructure', np.nan)
            reg_coef = model_result.event_effects.get('D_regulatory', np.nan)
            infra_se = model_result.std_errors.get('D_infrastructure', np.nan)
            reg_se = model_result.std_errors.get('D_regulatory', np.nan)

            rows.append({
                'Variant': variant,
                'Cryptocurrency': crypto,
                'Infrastructure Coef': infra_coef,
                'Infrastructure SE': infra_se,
                'Regulatory Coef': reg_coef,
                'Regulatory SE': reg_se,
                'Difference': infra_coef - reg_coef if not np.isnan(infra_coef) else np.nan
            })

    comparison_df = pd.DataFrame(rows)
    return comparison_df


def run_robustness_check():
    """Main function to run overlap robustness check."""

    print("="*70)
    print("OVERLAPPING EVENTS ROBUSTNESS CHECK")
    print("="*70)
    print("\nTesting three overlap treatments:")
    print("  1. Current: Both events at 0.5 (conservative)")
    print("  2. Max: Dominant event at 1.0, other at 0.0")
    print("  3. Additive: Both events at 1.0 (full additive effects)")
    print()

    # Prepare data
    print("Loading data...")
    data_prep = EventDataPreparation()
    data_prep.load_data()
    data_prep.prepare_event_dummies()
    data_prep.prepare_gdelt_sentiment()
    data_prep.merge_data()

    # Create overlap variants
    print("Creating overlap variants...")
    variants = create_overlap_variants(data_prep)

    # Estimate models for each variant
    results_dict = {}
    for variant_name, event_dummies in variants.items():
        results = estimate_robustness_models(variant_name, event_dummies)
        results_dict[variant_name] = results

    # Compare results
    print("\n" + "="*70)
    print("COMPARISON OF EVENT COEFFICIENTS")
    print("="*70)

    comparison_df = compare_event_coefficients(results_dict)

    # Save results
    output_path = OUTPUTS_DIR / 'robustness_overlapping_events.csv'
    comparison_df.to_csv(output_path, index=False)
    print(f"\n✓ Results saved to {output_path}")

    # Print summary
    print("\nSummary by variant:")
    summary = comparison_df.groupby('Variant').agg({
        'Infrastructure Coef': ['mean', 'std'],
        'Regulatory Coef': ['mean', 'std'],
        'Difference': ['mean', 'std']
    })
    print(summary)

    # Test if differences are stable across variants
    pivot = comparison_df.pivot_table(
        index='Cryptocurrency',
        columns='Variant',
        values='Difference'
    )
    print("\nInfrastructure-Regulatory Difference by Variant:")
    print(pivot)

    return comparison_df, results_dict


if __name__ == '__main__':
    try:
        comparison_df, results = run_robustness_check()
    except Exception as e:
        print(f"Error running robustness check: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
