"""
Run diagnostic tests (Ljung-Box, ARCH-LM, Jarque-Bera) on all TARCH-X models.

This script validates model specifications by testing for:
- Serial correlation in standardized residuals (Ljung-Box)
- Remaining ARCH effects (ARCH-LM)
- Normality of standardized residuals (Jarque-Bera)

Usage:
    python run_diagnostics.py
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import pickle

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from garch_models import GARCHModels
from config import CRYPTO_SYMBOLS, DATA_DIR, OUTPUTS_DIR


def load_models():
    """Load estimated TARCH-X models from saved results."""
    models_path = OUTPUTS_DIR / 'tarch_x_models.pkl'

    if not models_path.exists():
        raise FileNotFoundError(
            f"Models not found at {models_path}. "
            "Run the main analysis script first to estimate models."
        )

    with open(models_path, 'rb') as f:
        models = pickle.load(f)

    return models


def run_all_diagnostics():
    """Run diagnostics on all cryptocurrencies and compile results."""

    print("Loading estimated models...")
    models = load_models()

    print(f"Running diagnostics for {len(models)} cryptocurrencies...\n")

    # Storage for results
    diagnostics_results = {}
    summary_rows = []

    garch_analyzer = GARCHModels()

    for crypto, model_result in models.items():
        print(f"Processing {crypto}...")

        if not model_result.convergence:
            print(f"  ⚠️  Model did not converge - skipping diagnostics")
            continue

        # Run diagnostics
        diagnostics = garch_analyzer.run_diagnostics(model_result)
        diagnostics_results[crypto] = diagnostics

        # Extract key results
        lb_stat = diagnostics['ljung_box']['statistic']
        lb_pval = diagnostics['ljung_box']['pvalue']
        arch_stat = diagnostics['arch_lm']['statistic']
        arch_pval = diagnostics['arch_lm']['pvalue']
        jb_stat = diagnostics['jarque_bera']['statistic']
        jb_pval = diagnostics['jarque_bera']['pvalue']

        # Interpret results
        lb_pass = "✓" if lb_pval > 0.05 else "✗"
        arch_pass = "✓" if arch_pval > 0.05 else "✗"
        jb_pass = "✓" if jb_pval > 0.05 else "✗"

        print(f"  Ljung-Box:  {lb_stat:.2f} (p={lb_pval:.4f}) {lb_pass}")
        print(f"  ARCH-LM:    {arch_stat:.2f} (p={arch_pval:.4f}) {arch_pass}")
        print(f"  Jarque-Bera: {jb_stat:.2f} (p={jb_pval:.4f}) {jb_pass}")
        print()

        # Store for DataFrame
        summary_rows.append({
            'Cryptocurrency': crypto,
            'Ljung-Box Stat': lb_stat,
            'Ljung-Box p-value': lb_pval,
            'LB Pass': lb_pass,
            'ARCH-LM Stat': arch_stat,
            'ARCH-LM p-value': arch_pval,
            'ARCH Pass': arch_pass,
            'Jarque-Bera Stat': jb_stat,
            'Jarque-Bera p-value': jb_pval,
            'JB Pass': jb_pass
        })

    # Create summary DataFrame
    summary_df = pd.DataFrame(summary_rows)

    # Save results
    output_path = OUTPUTS_DIR / 'model_diagnostics.csv'
    summary_df.to_csv(output_path, index=False)
    print(f"✓ Diagnostics saved to {output_path}")

    # Save full diagnostics dictionary
    diagnostics_path = OUTPUTS_DIR / 'diagnostics_full.pkl'
    with open(diagnostics_path, 'wb') as f:
        pickle.dump(diagnostics_results, f)
    print(f"✓ Full diagnostics saved to {diagnostics_path}")

    # Print summary
    print("\n" + "="*70)
    print("DIAGNOSTICS SUMMARY")
    print("="*70)
    print("\nTest Interpretations:")
    print("  Ljung-Box:  Tests for serial correlation in residuals (want p > 0.05)")
    print("  ARCH-LM:    Tests for remaining ARCH effects (want p > 0.05)")
    print("  Jarque-Bera: Tests for normality (expect to fail for crypto)")
    print()
    print(summary_df.to_string(index=False))
    print()

    # Count passes
    n_cryptos = len(summary_df)
    lb_passes = (summary_df['LB Pass'] == '✓').sum()
    arch_passes = (summary_df['ARCH Pass'] == '✓').sum()
    jb_passes = (summary_df['JB Pass'] == '✓').sum()

    print(f"Pass Rates:")
    print(f"  Ljung-Box:  {lb_passes}/{n_cryptos} ({100*lb_passes/n_cryptos:.1f}%)")
    print(f"  ARCH-LM:    {arch_passes}/{n_cryptos} ({100*arch_passes/n_cryptos:.1f}%)")
    print(f"  Jarque-Bera: {jb_passes}/{n_cryptos} ({100*jb_passes/n_cryptos:.1f}%)")
    print()

    return summary_df, diagnostics_results


if __name__ == '__main__':
    try:
        summary_df, diagnostics = run_all_diagnostics()
    except Exception as e:
        print(f"Error running diagnostics: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
