"""
Extract Conditional Volatility from GARCH Models
Standalone script to generate volatility time-series for correlation matrix calculation
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add event_study.code to path
sys.path.insert(0, str(Path(__file__).parent / 'event_study' / 'code'))

try:
    from garch_models import GARCHModels
    from data_preparation import DataPreparation
    print("✓ Successfully imported modules")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("\nAttempting alternative import method...")

    # Try changing directory
    import os
    os.chdir(Path(__file__).parent / 'event_study' / 'code')
    sys.path.insert(0, os.getcwd())

    try:
        from garch_models import GARCHModels
        from data_preparation import DataPreparation
        print("✓ Successfully imported modules (alternative method)")
    except ImportError as e2:
        print(f"✗ Still failed: {e2}")
        print("\nPlease run this script from the event_study/code directory:")
        print("  cd event_study/code")
        print("  python ../../extract_volatility.py")
        sys.exit(1)

print("="*80)
print("EXTRACTING CONDITIONAL VOLATILITY FROM GARCH MODELS")
print("="*80)
print()

# Create output directory
output_dir = Path(__file__).parent / 'event_study' / 'outputs'
output_dir.mkdir(exist_ok=True)

# Initialize data preparation
try:
    data_prep = DataPreparation()
    print("✓ Initialized DataPreparation")
except Exception as e:
    print(f"✗ Failed to initialize DataPreparation: {e}")
    sys.exit(1)

cryptos = ['btc', 'eth', 'xrp', 'bnb', 'ltc', 'ada']
successful_extractions = []
failed_extractions = []

for crypto in cryptos:
    print(f"\n{'='*80}")
    print(f"Processing {crypto.upper()}...")
    print(f"{'='*80}")

    try:
        # Load prepared data
        print(f"  Loading data for {crypto}...")
        crypto_data = data_prep.prepare_crypto_data(crypto)
        print(f"  ✓ Loaded {len(crypto_data)} observations")

        # Estimate models
        print(f"  Estimating GARCH models...")
        modeler = GARCHModels(crypto_data, crypto)
        results = modeler.estimate_all_models()

        # Extract conditional volatility from best model
        vol = None
        model_used = None

        if 'TARCH-X' in results and results['TARCH-X'].convergence:
            vol = results['TARCH-X'].volatility
            model_used = 'TARCH-X'
        elif 'TARCH(1,1)' in results and results['TARCH(1,1)'].convergence:
            vol = results['TARCH(1,1)'].volatility
            model_used = 'TARCH(1,1)'
        elif 'GARCH(1,1)' in results and results['GARCH(1,1)'].convergence:
            vol = results['GARCH(1,1)'].volatility
            model_used = 'GARCH(1,1)'

        if vol is None or len(vol) == 0:
            raise ValueError("No converged models found")

        # Save to CSV
        vol_df = pd.DataFrame({
            'date': vol.index,
            'conditional_volatility': vol.values
        })

        output_file = output_dir / f'volatility_{crypto}.csv'
        vol_df.to_csv(output_file, index=False)

        print(f"  ✓ Saved {len(vol)} observations from {model_used}")
        print(f"  ✓ Output: {output_file}")

        successful_extractions.append({
            'crypto': crypto,
            'model': model_used,
            'observations': len(vol),
            'file': str(output_file)
        })

    except Exception as e:
        print(f"  ✗ Error processing {crypto}: {e}")
        import traceback
        traceback.print_exc()
        failed_extractions.append({'crypto': crypto, 'error': str(e)})

print("\n" + "="*80)
print("EXTRACTION SUMMARY")
print("="*80)

if successful_extractions:
    print(f"\n✓ Successfully extracted {len(successful_extractions)} cryptocurrencies:")
    for item in successful_extractions:
        print(f"  - {item['crypto'].upper()}: {item['observations']} obs from {item['model']}")

if failed_extractions:
    print(f"\n✗ Failed to extract {len(failed_extractions)} cryptocurrencies:")
    for item in failed_extractions:
        print(f"  - {item['crypto'].upper()}: {item['error']}")

if successful_extractions:
    print("\n" + "="*80)
    print("NEXT STEP: Run the correlation matrix fix")
    print("="*80)
    print("  python fix_correlation_matrix.py")
    print()
else:
    print("\n⚠️  No volatility data extracted. Check errors above.")
