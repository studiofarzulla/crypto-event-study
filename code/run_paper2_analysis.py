"""
Main Analysis Script for Paper 2
=================================

Runs complete Paper 2 analysis pipeline:
1. Pilot study (microstructure event study)
2. Extended TARCH-X estimation (with microstructure)
3. Variance decomposition
4. Generate publication figures

Usage:
    # Quick diagnostic:
    python code/run_paper2_analysis.py --diagnostic

    # Full pilot study:
    python code/run_paper2_analysis.py --pilot

    # Complete analysis (requires full dataset):
    python code/run_paper2_analysis.py --full
"""

import argparse
import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

import config
from microstructure_data import MicrostructureDataCollector
from comparative_analysis import ComparativeEventStudy, run_pilot_comparative_study
from variance_decomposition import VarianceDecomposer
from paper2_visualizations import create_all_paper2_figures, Paper2Visualizer


def print_header(title: str):
    """Print formatted header."""
    print("\n" + "="*70)
    print(f"{title:^70}")
    print("="*70 + "\n")


def run_diagnostic():
    """
    Quick diagnostic check of data availability.
    """
    print_header("PAPER 2 DIAGNOSTIC CHECK")

    collector = MicrostructureDataCollector()

    print("Testing data collection capabilities...\n")

    # Test 1: Crypto data
    print("1. Cryptocurrency Data (BTC):")
    try:
        btc_data = collector.collect_crypto_spread(
            symbol='BTC',
            start_date='2024-01-01',
            end_date='2024-01-15'
        )
        if not btc_data.empty:
            print(f"   ✓ SUCCESS - {len(btc_data)} days collected")
            print(f"   Average spread: {btc_data['spread_pct'].mean():.4f}%")
        else:
            print("   ✗ FAILED - No data returned")
    except Exception as e:
        print(f"   ✗ ERROR: {e}")

    # Test 2: Traditional data
    print("\n2. Traditional Data (SPY):")
    try:
        spy_data = collector.collect_traditional_spread(
            symbol='SPY',
            start_date='2024-01-01',
            end_date='2024-01-15'
        )
        if not spy_data.empty:
            print(f"   ✓ SUCCESS - {len(spy_data)} days collected")
            print(f"   Average spread: {spy_data['spread_pct'].mean():.4f}%")
        else:
            print("   ✗ FAILED - No data returned")
    except Exception as e:
        print(f"   ✗ ERROR: {e}")

    # Test 3: Event window analysis
    print("\n3. Event Window Analysis:")
    try:
        result = collector.compare_crypto_vs_traditional(
            crypto_symbol='BTC',
            trad_symbol='SPY',
            event_date='2024-01-10'  # BTC ETF approval
        )
        if result:
            print("   ✓ SUCCESS - Event analysis functional")
            print(f"   Crypto spread change: {result['crypto']['change_pct']:+.2f}%")
            print(f"   Traditional spread change: {result['traditional']['change_pct']:+.2f}%")
        else:
            print("   ✗ FAILED - Event analysis returned empty")
    except Exception as e:
        print(f"   ✗ ERROR: {e}")

    print("\n" + "="*70)
    print("DIAGNOSTIC COMPLETE")
    print("="*70)
    print("\nNext steps:")
    print("  - If all tests passed: Run pilot study")
    print("  - If any failed: Check API access and internet connection")
    print("\nCommands:")
    print("  Pilot study: python code/run_paper2_analysis.py --pilot")


def run_pilot_study(with_robustness: bool = False):
    """
    Run pilot study on 5 major events.

    Args:
        with_robustness: If True, run full robustness check suite
    """
    print_header("PAPER 2 PILOT STUDY")

    print("Configuration:")
    print(f"  Events: {len(config.PILOT_EVENTS)}")
    print(f"  Crypto assets: {config.CRYPTO_ASSETS}")
    print(f"  Traditional assets: {config.TRADITIONAL_ASSETS}")
    print(f"  Event window: ±{config.EVENT_WINDOW_PRE} days")
    print(f"  Robustness checks: {'YES' if with_robustness else 'NO'}")

    print("\nPilot Events:")
    for i, event in enumerate(config.PILOT_EVENTS, 1):
        print(f"  {i}. {event['name']} ({event['date']}) - {event['type']}")

    input("\nPress Enter to start pilot study (or Ctrl+C to cancel)...")

    # Run comparative analysis
    print_header("PHASE 1: MICROSTRUCTURE EVENT STUDY")
    results_df = run_pilot_comparative_study()

    if results_df.empty:
        print("\n[ERROR] Pilot study failed - no valid results")
        return

    # Save intermediate results
    results_path = config.OUTPUTS_DIR / 'pilot_microstructure_results.csv'
    results_df.to_csv(results_path, index=False)
    print(f"\n[SAVED] Microstructure results: {results_path}")

    # Create figures
    print_header("PHASE 2: GENERATE FIGURES")

    viz = Paper2Visualizer()

    # Simple microstructure comparison figure
    print("Creating microstructure comparison figure...")
    viz.plot_microstructure_comparison(results_df,
                                      save_name='pilot_microstructure_comparison')

    # Run robustness checks if requested
    if with_robustness:
        print_header("PHASE 3: ROBUSTNESS CHECKS")

        from robustness_paper2 import run_complete_robustness_suite

        print("Running comprehensive robustness check suite...")
        print("This will take approximately 15-30 minutes.\n")

        robustness_results = run_complete_robustness_suite(
            events=config.PILOT_EVENTS,
            results_df=results_df,
            save_dir=config.OUTPUTS_DIR
        )

        print("\n[SUCCESS] Robustness checks complete")
        print(f"Results saved to: {config.OUTPUTS_DIR}")

    # Summary
    print_header("PILOT STUDY COMPLETE")

    success_rate = (results_df['hypothesis_supported'].sum() / len(results_df)) * 100

    print(f"Success Rate: {success_rate:.0f}%")
    print(f"Hypothesis Supported: {results_df['hypothesis_supported'].sum()}/{len(results_df)} events")

    if success_rate >= 60:
        print("\n✓ HYPOTHESIS SUPPORTED - Proceed to full study")
    else:
        print("\n✗ MIXED RESULTS - Review data quality")

    print("\nOutputs:")
    print(f"  - Results: {results_path}")
    print(f"  - Figures: {config.OUTPUTS_DIR / 'figures'}")

    if with_robustness:
        print("\n  Robustness Check Outputs:")
        print(f"    - robustness_windows_summary.csv")
        print(f"    - robustness_bootstrap_ci.csv")
        print(f"    - robustness_placebo_tests.csv")
        print(f"    - robustness_heterogeneity.csv")
        print(f"    - robustness_summary_report.txt")


def run_full_analysis():
    """
    Run complete Paper 2 analysis (requires full dataset).
    """
    print_header("PAPER 2 FULL ANALYSIS")

    print("[INFO] Full analysis requires:")
    print("  - Complete price data (2019-2025)")
    print("  - All 20+ regulatory events")
    print("  - High-quality microstructure data")
    print("  - TARCH-X estimation (~1-2 hours)")

    input("\nPress Enter to continue (or Ctrl+C to cancel)...")

    # Phase 1: Data collection
    print_header("PHASE 1: DATA COLLECTION")
    print("[TODO] Implement full data collection")
    print("  - See docs/DATA_SOURCES.md for data sources")
    print("  - Run: python code/microstructure_data.py --download")

    # Phase 2: Event study
    print_header("PHASE 2: MICROSTRUCTURE EVENT STUDY")
    print("[TODO] Run on all regulatory events")

    # Phase 3: TARCH-X estimation
    print_header("PHASE 3: EXTENDED TARCH-X ESTIMATION")
    print("[TODO] Estimate TARCH-X-Micro models")

    # Phase 4: Variance decomposition
    print_header("PHASE 4: VARIANCE DECOMPOSITION")
    print("[TODO] Decompose channels")

    # Phase 5: Figures
    print_header("PHASE 5: PUBLICATION FIGURES")
    print("[TODO] Generate all figures")

    print("\n[INFO] Full analysis pipeline is under development")
    print("Run pilot study for now: --pilot")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Paper 2 Analysis: Sentiment Without Structure"
    )
    parser.add_argument('--diagnostic', action='store_true',
                       help='Run quick diagnostic check')
    parser.add_argument('--pilot', action='store_true',
                       help='Run pilot study (5 events)')
    parser.add_argument('--robustness', action='store_true',
                       help='Include comprehensive robustness checks')
    parser.add_argument('--full', action='store_true',
                       help='Run full analysis (all events)')

    args = parser.parse_args()

    # Banner
    print("\n" + "="*70)
    print("PAPER 2: SENTIMENT WITHOUT STRUCTURE")
    print("Regulatory Microstructure in Crypto vs Traditional Markets")
    print("="*70)

    if args.diagnostic:
        run_diagnostic()
    elif args.pilot:
        run_pilot_study(with_robustness=args.robustness)
    elif args.full:
        run_full_analysis()
    else:
        # Default: show help
        print("\nUsage:")
        print("  Quick check:        python code/run_paper2_analysis.py --diagnostic")
        print("  Pilot study:        python code/run_paper2_analysis.py --pilot")
        print("  With robustness:    python code/run_paper2_analysis.py --pilot --robustness")
        print("  Full analysis:      python code/run_paper2_analysis.py --full")
        print("\nStart with --diagnostic to verify data access")
        print("\nRobustness checks include:")
        print("  - Alternative event windows (±7, ±14, ±60 days)")
        print("  - Bootstrap confidence intervals (1000 iterations)")
        print("  - Placebo tests (20 random dates)")
        print("  - Cross-sectional heterogeneity (6 cryptocurrencies)")


if __name__ == "__main__":
    main()
