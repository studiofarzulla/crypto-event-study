"""
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
    print(f"\nProcessing {crypto.upper()}...")

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

print("\nExtraction complete!")
