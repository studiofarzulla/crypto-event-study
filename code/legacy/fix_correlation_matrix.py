"""
FIX: Correlation Matrix Calculation
====================================
PROBLEM: Current correlation matrix uses mean event effects (only 2-6 values per crypto)
         resulting in perfect ±1.0 correlations (mathematically impossible with real data)

SOLUTION: Use daily conditional volatility from TARCH-X models (2000+ daily observations)
          to calculate proper correlations for portfolio analysis

Author: Claude Code
Date: October 26, 2025
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("CORRELATION MATRIX FIX")
print("Replacing mean-based correlations with volatility time-series correlations")
print("="*80)
print()

# ============================================================================
# STEP 1: Load GARCH model results to extract conditional volatility
# ============================================================================

print("STEP 1: Checking for conditional volatility data...")
print("-"*80)

# Check if we have saved model results with volatility
model_params_dir = Path('event_study/outputs/analysis_results/model_parameters')
cryptos = ['btc', 'eth', 'xrp', 'bnb', 'ltc', 'ada']

# Try to find pickle files or volatility CSVs
volatility_data = {}
missing_volatility = []

for crypto in cryptos:
    # Check for saved volatility time series
    vol_file = Path(f'event_study/outputs/volatility_{crypto}.csv')
    if vol_file.exists():
        vol_df = pd.read_csv(vol_file, index_col=0, parse_dates=True)
        volatility_data[crypto] = vol_df['conditional_volatility']
        print(f"  ✓ {crypto.upper()}: Loaded {len(vol_df)} daily volatility observations")
    else:
        missing_volatility.append(crypto)
        print(f"  ✗ {crypto.upper()}: Volatility data not found at {vol_file}")

print()

# ============================================================================
# STEP 2: If volatility data missing, provide extraction template
# ============================================================================

if missing_volatility:
    print("STEP 2: MISSING VOLATILITY DATA")
    print("-"*80)
    print(f"Missing volatility for: {', '.join(c.upper() for c in missing_volatility)}")
    print()
    print("REQUIRED ACTION:")
    print("You need to extract conditional volatility from GARCH model results.")
    print()
    print("Use this template to extract volatility from your GARCH estimation:")
    print()
    print("```python")
    print("# After running GARCH estimation:")
    print("from event_study.code.garch_models import GARCHModels")
    print("from event_study.code.data_preparation import DataPreparation")
    print()
    print("# For each crypto:")
    print("for crypto in ['btc', 'eth', 'xrp', 'bnb', 'ltc', 'ada']:")
    print("    # Load prepared data")
    print("    data_prep = DataPreparation()")
    print("    crypto_data = data_prep.prepare_crypto_data(crypto)")
    print("    ")
    print("    # Estimate models")
    print("    modeler = GARCHModels(crypto_data, crypto)")
    print("    results = modeler.estimate_all_models()")
    print("    ")
    print("    # Extract conditional volatility from TARCH-X (or TARCH if TARCH-X failed)")
    print("    if 'TARCH-X' in results and results['TARCH-X'].convergence:")
    print("        vol = results['TARCH-X'].volatility")
    print("    elif 'TARCH(1,1)' in results and results['TARCH(1,1)'].convergence:")
    print("        vol = results['TARCH(1,1)'].volatility")
    print("    else:")
    print("        vol = results['GARCH(1,1)'].volatility")
    print("    ")
    print("    # Save to CSV")
    print("    vol_df = pd.DataFrame({")
    print("        'date': vol.index,")
    print("        'conditional_volatility': vol.values")
    print("    })")
    print("    vol_df.to_csv(f'event_study/outputs/volatility_{crypto}.csv', index=False)")
    print("    print(f'Saved {len(vol)} observations for {crypto.upper()}')")
    print("```")
    print()

    # Save the template as a separate file
    template_path = Path('event_study/extract_volatility_template.py')
    with open(template_path, 'w') as f:
        f.write('''"""
Template: Extract Conditional Volatility from GARCH Models
Run this to generate the required volatility time-series data
"""

import pandas as pd
import sys
from pathlib import Path

# Add project to path
sys.path.append(str(Path(__file__).parent))

from event_study.code.garch_models import GARCHModels
from event_study.code.data_preparation import DataPreparation

print("Extracting conditional volatility from GARCH models...")
print("="*80)

# Initialize data preparation
data_prep = DataPreparation()

cryptos = ['btc', 'eth', 'xrp', 'bnb', 'ltc', 'ada']

for crypto in cryptos:
    print(f"\\nProcessing {crypto.upper()}...")

    try:
        # Load prepared data
        crypto_data = data_prep.prepare_crypto_data(crypto)

        # Estimate models
        modeler = GARCHModels(crypto_data, crypto)
        results = modeler.estimate_all_models()

        # Extract conditional volatility from best model
        if 'TARCH-X' in results and results['TARCH-X'].convergence:
            vol = results['TARCH-X'].volatility
            model_used = 'TARCH-X'
        elif 'TARCH(1,1)' in results and results['TARCH(1,1)'].convergence:
            vol = results['TARCH(1,1)'].volatility
            model_used = 'TARCH(1,1)'
        else:
            vol = results['GARCH(1,1)'].volatility
            model_used = 'GARCH(1,1)'

        # Save to CSV
        vol_df = pd.DataFrame({
            'date': vol.index,
            'conditional_volatility': vol.values
        })
        vol_df.to_csv(f'event_study/outputs/volatility_{crypto}.csv', index=False)
        print(f"  ✓ Saved {len(vol)} observations from {model_used}")

    except Exception as e:
        print(f"  ✗ Error: {e}")

print("\\nExtraction complete!")
''')

    print(f"Template saved to: {template_path}")
    print()
    print("STOPPING HERE - Please run the template to generate volatility data first.")
    print("="*80)
    exit(0)

# ============================================================================
# STEP 3: Calculate proper correlation matrix from volatility time-series
# ============================================================================

print("STEP 3: Calculating correlation matrix from daily volatility...")
print("-"*80)

# Combine all volatility series into one dataframe
vol_df = pd.DataFrame(volatility_data)

# Align dates (use intersection of available dates)
vol_df = vol_df.dropna()

print(f"Total aligned observations: {len(vol_df)}")
print(f"Date range: {vol_df.index.min()} to {vol_df.index.max()}")
print()

# Calculate correlation matrix
corr_matrix = vol_df.corr()

print("CORRELATION MATRIX (Daily Conditional Volatility):")
print("-"*80)
print(corr_matrix.round(4))
print()

# Verify no perfect correlations (except diagonal)
corr_matrix_no_diag = corr_matrix.copy()
np.fill_diagonal(corr_matrix_no_diag.values, np.nan)

max_corr = corr_matrix_no_diag.max().max()
min_corr = corr_matrix_no_diag.min().min()

print("VERIFICATION:")
print("-"*80)
print(f"Maximum off-diagonal correlation: {max_corr:.4f}")
print(f"Minimum off-diagonal correlation: {min_corr:.4f}")

if abs(max_corr - 1.0) < 0.01 or abs(min_corr + 1.0) < 0.01:
    print("⚠️  WARNING: Still seeing perfect/near-perfect correlations!")
    print("This suggests insufficient data variation.")
else:
    print("✓ Correlations are realistic (no perfect ±1.0 values)")
print()

# ============================================================================
# STEP 4: Calculate portfolio metrics with CORRECT correlations
# ============================================================================

print("STEP 4: Recalculating portfolio implications...")
print("-"*80)

# Calculate average volatilities
avg_vols = vol_df.mean()

# Equal-weight portfolio variance
n_assets = len(cryptos)
equal_weight = 1 / n_assets

# Portfolio variance = w'Σw where w is weights vector, Σ is covariance matrix
# Covariance matrix from correlation matrix and standard deviations
std_vols = vol_df.std()
cov_matrix = corr_matrix * np.outer(std_vols, std_vols)

# Equal-weight portfolio variance
weights = np.array([equal_weight] * n_assets)
portfolio_variance = weights @ cov_matrix @ weights

# Individual average variance (unweighted average)
individual_avg_variance = (std_vols ** 2).mean()

# Variance reduction from diversification
variance_reduction = (1 - portfolio_variance / individual_avg_variance) * 100

print("PORTFOLIO METRICS:")
print("-"*80)
print(f"Individual average variance: {individual_avg_variance:.6f}")
print(f"Equal-weight portfolio variance: {portfolio_variance:.6f}")
print(f"Variance reduction: {variance_reduction:.2f}%")
print()

# Diversification ratio
# Weighted average std / portfolio std
weighted_avg_std = (weights * std_vols).sum()
portfolio_std = np.sqrt(portfolio_variance)
diversification_ratio = weighted_avg_std / portfolio_std

print(f"Diversification ratio: {diversification_ratio:.4f}")
print(f"Interpretation: Portfolio is {diversification_ratio:.2f}x less risky than weighted average")
print()

# ============================================================================
# STEP 5: Hedge ratio calculations (BNB-LTC example)
# ============================================================================

print("STEP 5: Hedge ratio analysis (BNB vs LTC)...")
print("-"*80)

if 'bnb' in vol_df.columns and 'ltc' in vol_df.columns:
    bnb_ltc_corr = corr_matrix.loc['bnb', 'ltc']

    # Optimal hedge ratio = Cov(BNB, LTC) / Var(LTC)
    cov_bnb_ltc = cov_matrix.loc['bnb', 'ltc']
    var_ltc = cov_matrix.loc['ltc', 'ltc']
    hedge_ratio = cov_bnb_ltc / var_ltc

    # Hedge effectiveness (R²)
    hedge_effectiveness = bnb_ltc_corr ** 2

    print(f"BNB-LTC correlation: {bnb_ltc_corr:.4f}")
    print(f"Optimal hedge ratio: {hedge_ratio:.4f}")
    print(f"Hedge effectiveness (R²): {hedge_effectiveness:.4f} ({hedge_effectiveness*100:.2f}%)")
    print()

    if abs(bnb_ltc_corr) < 0.3:
        print("Interpretation: WEAK correlation - poor hedge but good diversification")
    elif abs(bnb_ltc_corr) < 0.7:
        print("Interpretation: MODERATE correlation - reasonable diversification")
    else:
        print("Interpretation: STRONG correlation - limited diversification benefit")
else:
    print("⚠️  BNB or LTC data not available for hedge analysis")

print()

# ============================================================================
# STEP 6: Save corrected results
# ============================================================================

print("STEP 6: Saving corrected results...")
print("-"*80)

# Save correlation matrix
corr_matrix.to_csv('event_study/outputs/correlation_matrix_corrected.csv')
print(f"✓ Correlation matrix saved to: event_study/outputs/correlation_matrix_corrected.csv")

# Save portfolio metrics
portfolio_metrics = pd.DataFrame({
    'metric': [
        'individual_avg_variance',
        'portfolio_variance',
        'variance_reduction_pct',
        'diversification_ratio',
        'bnb_ltc_correlation',
        'bnb_ltc_hedge_ratio',
        'hedge_effectiveness_r2'
    ],
    'value': [
        individual_avg_variance,
        portfolio_variance,
        variance_reduction,
        diversification_ratio,
        bnb_ltc_corr if 'bnb' in vol_df.columns and 'ltc' in vol_df.columns else np.nan,
        hedge_ratio if 'bnb' in vol_df.columns and 'ltc' in vol_df.columns else np.nan,
        hedge_effectiveness if 'bnb' in vol_df.columns and 'ltc' in vol_df.columns else np.nan
    ]
})

portfolio_metrics.to_csv('event_study/outputs/portfolio_metrics_corrected.csv', index=False)
print(f"✓ Portfolio metrics saved to: event_study/outputs/portfolio_metrics_corrected.csv")

print()
print("="*80)
print("CORRELATION MATRIX FIX COMPLETE")
print("="*80)
print()
print("WHAT CHANGED:")
print("  • OLD: Correlation from 2-6 mean event effects → perfect ±1.0 correlations")
print(f"  • NEW: Correlation from {len(vol_df)} daily volatility observations → realistic correlations")
print()
print("NEXT STEPS:")
print("  1. Review correlation_matrix_corrected.csv")
print("  2. Update manuscript portfolio section with new metrics")
print("  3. Verify hedge ratios make economic sense")
print("  4. Update any figures that show correlations")
print()
