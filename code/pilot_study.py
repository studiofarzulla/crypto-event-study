"""
Pilot Study: Sentiment Without Structure
=========================================

Quick test of Paper 2 methodology on 5 major regulatory events:
1. China crypto ban (2021-09-24)
2. FTX collapse (2022-11-10)
3. BTC ETF approval (2024-01-10)
4. SEC Binance suit (2023-06-05)
5. Terra/UST collapse (2022-05-09)

Tests core hypothesis:
- Crypto: No microstructure response to regulation
- Traditional: Significant microstructure response

Runtime: ~10 minutes (with API rate limits)
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

import config
from microstructure_data import MicrostructureDataCollector


def print_header(title):
    """Print formatted section header."""
    print(f"\n{'='*70}")
    print(f"{title:^70}")
    print(f"{'='*70}\n")


def run_pilot_study():
    """Run pilot study on 5 major events."""
    print_header("PAPER 2 PILOT STUDY: SENTIMENT WITHOUT STRUCTURE")

    print("Methodology Test:")
    print("  - Compare crypto (BTC) vs traditional (SPY) microstructure response")
    print("  - 5 major regulatory/infrastructure events (2021-2024)")
    print("  - Metrics: Bid-ask spread changes around events")
    print(f"  - Event window: ±{config.EVENT_WINDOW_PRE} days")

    # Initialize data collector
    collector = MicrostructureDataCollector()

    # Pilot events
    events = config.PILOT_EVENTS

    print(f"\nPilot Events ({len(events)}):")
    for i, event in enumerate(events, 1):
        print(f"  {i}. {event['name']} ({event['date']}) - {event['type']}")

    # Results storage
    results_summary = []

    # Run analysis for each event
    for event in events:
        event_date = event['date']
        event_name = event['name']
        event_type = event['type']

        print_header(f"EVENT {events.index(event) + 1}: {event_name}")
        print(f"Date: {event_date}")
        print(f"Type: {event_type}")

        try:
            # Compare crypto vs traditional
            result = collector.compare_crypto_vs_traditional(
                crypto_symbol='BTC',
                trad_symbol='SPY',
                event_date=event_date
            )

            if not result:
                print(f"  [SKIP] Insufficient data for {event_name}")
                continue

            # Extract key statistics
            crypto_change = result['crypto']['change_pct']
            crypto_pval = result['crypto']['p_value']
            crypto_sig = crypto_pval < 0.05

            trad_change = result['traditional']['change_pct']
            trad_pval = result['traditional']['p_value']
            trad_sig = trad_pval < 0.05

            difference = trad_change - crypto_change

            # Store results
            results_summary.append({
                'event': event_name,
                'date': event_date,
                'type': event_type,
                'crypto_change_pct': crypto_change,
                'crypto_pval': crypto_pval,
                'crypto_significant': crypto_sig,
                'trad_change_pct': trad_change,
                'trad_pval': trad_pval,
                'trad_significant': trad_sig,
                'difference': difference,
                'hypothesis_supported': (not crypto_sig) and trad_sig
            })

            print(f"\n[RESULT] Hypothesis check:")
            print(f"  Crypto response: {crypto_change:+.2f}% (sig={crypto_sig})")
            print(f"  Traditional response: {trad_change:+.2f}% (sig={trad_sig})")
            print(f"  Hypothesis supported: {'YES ✓' if results_summary[-1]['hypothesis_supported'] else 'NO ✗'}")

        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            continue

    # Overall summary
    print_header("PILOT STUDY RESULTS SUMMARY")

    if not results_summary:
        print("No successful event analyses. Check data availability.")
        return None

    df_results = pd.DataFrame(results_summary)

    print("Microstructure Response by Event:\n")
    print(f"{'Event':<25} {'Date':<12} {'Crypto':<10} {'Trad':<10} {'Diff':<10} {'H0 Supported'}")
    print("-" * 70)

    for _, row in df_results.iterrows():
        crypto_str = f"{row['crypto_change_pct']:+.1f}%"
        crypto_str += "***" if row['crypto_pval'] < 0.01 else "**" if row['crypto_pval'] < 0.05 else ""

        trad_str = f"{row['trad_change_pct']:+.1f}%"
        trad_str += "***" if row['trad_pval'] < 0.01 else "**" if row['trad_pval'] < 0.05 else ""

        diff_str = f"{row['difference']:+.1f}pp"

        supported = "YES ✓" if row['hypothesis_supported'] else "NO ✗"

        print(f"{row['event']:<25} {row['date']:<12} {crypto_str:<10} {trad_str:<10} "
              f"{diff_str:<10} {supported}")

    # Aggregate statistics
    print("\n" + "="*70)
    print("AGGREGATE STATISTICS")
    print("="*70 + "\n")

    print("Cryptocurrency (BTC):")
    print(f"  Mean spread change:      {df_results['crypto_change_pct'].mean():+.2f}%")
    print(f"  Median spread change:    {df_results['crypto_change_pct'].median():+.2f}%")
    print(f"  Std deviation:           {df_results['crypto_change_pct'].std():.2f}%")
    print(f"  Significant responses:   {df_results['crypto_significant'].sum()}/{len(df_results)}")

    print("\nTraditional Market (SPY):")
    print(f"  Mean spread change:      {df_results['trad_change_pct'].mean():+.2f}%")
    print(f"  Median spread change:    {df_results['trad_change_pct'].median():+.2f}%")
    print(f"  Std deviation:           {df_results['trad_change_pct'].std():.2f}%")
    print(f"  Significant responses:   {df_results['trad_significant'].sum()}/{len(df_results)}")

    print("\nComparative Analysis:")
    print(f"  Mean difference (Trad - Crypto): {df_results['difference'].mean():+.2f} pp")
    print(f"  Events supporting hypothesis:    {df_results['hypothesis_supported'].sum()}/{len(df_results)}")
    print(f"  Success rate:                    {(df_results['hypothesis_supported'].sum()/len(df_results))*100:.1f}%")

    # Statistical test
    from scipy.stats import ttest_rel

    # Paired t-test (same events, different markets)
    t_stat, p_value = ttest_rel(
        df_results['trad_change_pct'],
        df_results['crypto_change_pct']
    )

    print("\nPaired t-test (Traditional vs Crypto):")
    print(f"  t-statistic:  {t_stat:.3f}")
    print(f"  p-value:      {p_value:.4f}")
    print(f"  Conclusion:   {'Traditional > Crypto (significant)' if p_value < 0.05 else 'No significant difference'}")

    # Interpretation
    print("\n" + "="*70)
    print("INTERPRETATION")
    print("="*70 + "\n")

    if df_results['hypothesis_supported'].sum() / len(df_results) >= 0.6:
        print("✓ HYPOTHESIS SUPPORTED")
        print("\nEvidence suggests cryptocurrency markets show minimal microstructure")
        print("response to regulatory events, while traditional markets exhibit")
        print("significant changes. This supports the 'sentiment without structure'")
        print("mechanism: crypto regulation affects only sentiment, not market mechanics.")
    else:
        print("✗ HYPOTHESIS NOT SUPPORTED (in pilot)")
        print("\nData shows mixed results. This could indicate:")
        print("  - Data quality issues (using OHLC proxy instead of true bid-ask)")
        print("  - Event selection bias")
        print("  - Need for larger sample size")
        print("\nRecommendation: Proceed with caution to full study with better data.")

    # Save results
    output_file = config.OUTPUTS_DIR / 'pilot_study_results.csv'
    df_results.to_csv(output_file, index=False)
    print(f"\n[SAVED] Results saved to: {output_file}")

    return df_results


def quick_diagnostic():
    """Quick diagnostic test of data availability."""
    print_header("DIAGNOSTIC: DATA AVAILABILITY CHECK")

    collector = MicrostructureDataCollector()

    print("Testing data sources...\n")

    # Test crypto data
    print("1. Cryptocurrency data (BTC via CoinGecko):")
    try:
        btc_data = collector.collect_crypto_spread(
            symbol='BTC',
            start_date='2024-01-01',
            end_date='2024-01-15',
            frequency='1d'
        )
        if not btc_data.empty:
            print(f"   ✓ SUCCESS - {len(btc_data)} days collected")
            print(f"   Sample spread: {btc_data['spread_pct'].mean():.4f}%")
        else:
            print("   ✗ FAILED - No data returned")
    except Exception as e:
        print(f"   ✗ ERROR: {e}")

    print("\n2. Traditional data (SPY via Yahoo Finance):")
    try:
        spy_data = collector.collect_traditional_spread(
            symbol='SPY',
            start_date='2024-01-01',
            end_date='2024-01-15'
        )
        if not spy_data.empty:
            print(f"   ✓ SUCCESS - {len(spy_data)} days collected")
            print(f"   Sample spread: {spy_data['spread_pct'].mean():.4f}%")
        else:
            print("   ✗ FAILED - No data returned")
    except Exception as e:
        print(f"   ✗ ERROR: {e}")

    print("\n3. Event window analysis:")
    try:
        result = collector.compare_crypto_vs_traditional(
            crypto_symbol='BTC',
            trad_symbol='SPY',
            event_date='2024-01-10'  # BTC ETF approval
        )
        if result:
            print("   ✓ SUCCESS - Event analysis working")
        else:
            print("   ✗ FAILED - Event analysis returned empty")
    except Exception as e:
        print(f"   ✗ ERROR: {e}")

    print("\n" + "="*70)
    print("DIAGNOSTIC COMPLETE")
    print("="*70)
    print("\nIf all tests passed, proceed with: python code/pilot_study.py")
    print("If any failed, check internet connection and API availability.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--diagnostic':
        # Run diagnostic only
        quick_diagnostic()
    else:
        # Run full pilot study
        print("Starting pilot study...")
        print("Note: This will take ~10 minutes due to API rate limits")
        print("      Run with --diagnostic flag for quick test\n")

        input("Press Enter to continue (or Ctrl+C to cancel)...")

        results = run_pilot_study()

        if results is not None:
            print("\n" + "="*70)
            print("PILOT STUDY COMPLETE")
            print("="*70)
            print("\nNext steps:")
            print("  1. Review results in outputs/pilot_study_results.csv")
            print("  2. If hypothesis supported, proceed to full data collection")
            print("  3. Run: python code/microstructure_data.py --download")
            print("  4. Then: python code/run_full_analysis.py")
        else:
            print("\n[FAILED] Pilot study did not complete successfully")
            print("Run with --diagnostic flag to check data availability")
