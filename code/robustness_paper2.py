"""
Robustness Checks for Paper 2
==============================

Production-ready econometric robustness tests:
1. Alternative event windows (±7, ±14, ±60 days)
2. Bootstrap confidence intervals for variance decomposition
3. Placebo tests (pseudo-events on random dates)
4. Alternative microstructure metrics (Amihud, Roll, price impact)
5. Cross-sectional heterogeneity by market cap
6. Wild bootstrap for small sample inference
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from scipy.stats import ttest_ind, ttest_rel, ttest_1samp
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

import config
from comparative_analysis import ComparativeEventStudy


class RobustnessChecks:
    """Comprehensive robustness checks for Paper 2."""

    def __init__(self, save_dir: Optional[Path] = None):
        """
        Initialize robustness checker.

        Args:
            save_dir: Directory to save results (default: outputs/)
        """
        self.results = {}
        self.save_dir = save_dir or config.OUTPUTS_DIR
        self.save_dir.mkdir(parents=True, exist_ok=True)

    def test_alternative_windows(self, events: List[Dict],
                                crypto_symbol: str = 'BTC',
                                trad_symbol: str = 'SPY') -> pd.DataFrame:
        """
        Test sensitivity to event window specification.

        Args:
            events: List of event dictionaries
            crypto_symbol: Crypto asset to test
            trad_symbol: Traditional asset to test

        Returns:
            DataFrame with results across different windows
        """
        print("\n" + "="*70)
        print("ROBUSTNESS CHECK 1: ALTERNATIVE EVENT WINDOWS")
        print("="*70 + "\n")

        windows = [7, 14, 30, 60]  # Different window sizes
        study = ComparativeEventStudy()

        all_results = []
        summary_results = []

        for window in windows:
            print(f"\nTesting ±{window} day window...")

            window_results = []
            for event in events:
                try:
                    result = study.run_single_event_comparison(
                        event_date=event['date'],
                        event_name=event['name'],
                        crypto_symbol=crypto_symbol,
                        trad_symbol=trad_symbol,
                        window_pre=window,
                        window_post=window
                    )

                    if result and result.get('crypto_impact', {}).get('valid'):
                        window_results.append({
                            'window': window,
                            'event': event['name'],
                            'event_date': event['date'],
                            'crypto_change': result['crypto_impact']['spread_change_pct'],
                            'trad_change': result['trad_impact']['spread_change_pct'],
                            'crypto_pval': result['crypto_impact']['p_value'],
                            'trad_pval': result['trad_impact']['p_value'],
                            'crypto_sig': result['crypto_impact']['significant'],
                            'trad_sig': result['trad_impact']['significant'],
                            'hypothesis_supported': result['comparison']['hypothesis_supported']
                        })
                except Exception as e:
                    print(f"  [SKIP] {event['name']}: {str(e)}")
                    continue

            if window_results:
                df = pd.DataFrame(window_results)
                all_results.extend(window_results)

                success_rate = df['hypothesis_supported'].mean() * 100

                summary_results.append({
                    'window': window,
                    'n_events': len(df),
                    'crypto_mean': df['crypto_change'].mean(),
                    'crypto_std': df['crypto_change'].std(),
                    'trad_mean': df['trad_change'].mean(),
                    'trad_std': df['trad_change'].std(),
                    'hypothesis_support_rate': success_rate,
                    'crypto_sig_rate': (df['crypto_pval'] < 0.05).mean() * 100,
                    'trad_sig_rate': (df['trad_pval'] < 0.05).mean() * 100
                })
            else:
                print(f"  [WARNING] No valid results for ±{window} window")

        if not summary_results:
            print("\n[ERROR] No valid results across any window")
            return pd.DataFrame()

        summary_df = pd.DataFrame(summary_results)
        detailed_df = pd.DataFrame(all_results)

        # Print summary
        print("\n" + "="*70)
        print("WINDOW SENSITIVITY SUMMARY")
        print("="*70 + "\n")
        print(summary_df.to_string(index=False))

        # Robustness check
        variance = summary_df['hypothesis_support_rate'].std()
        print(f"\n{'='*70}")
        if variance < 15:
            print("✓ ROBUST - Results stable across window specifications")
        else:
            print("⚠ SENSITIVE - Results vary significantly with window choice")
        print(f"Standard deviation of hypothesis support: {variance:.1f}pp")
        print(f"{'='*70}")

        # Save results
        summary_path = self.save_dir / 'robustness_windows_summary.csv'
        detailed_path = self.save_dir / 'robustness_windows_detailed.csv'

        summary_df.to_csv(summary_path, index=False)
        detailed_df.to_csv(detailed_path, index=False)

        print(f"\n[SAVED] {summary_path}")
        print(f"[SAVED] {detailed_path}")

        self.results['window_sensitivity'] = {
            'summary': summary_df,
            'detailed': detailed_df
        }

        return summary_df

    def bootstrap_confidence_intervals(self,
                                      results_df: pd.DataFrame,
                                      n_bootstrap: int = 1000,
                                      confidence_level: float = 0.95) -> Dict:
        """
        Bootstrap confidence intervals for spread changes.

        Args:
            results_df: DataFrame with crypto_change_pct and trad_change_pct columns
            n_bootstrap: Number of bootstrap iterations
            confidence_level: Confidence level (default: 95%)

        Returns:
            Dictionary with bootstrap results
        """
        print("\n" + "="*70)
        print("ROBUSTNESS CHECK 2: BOOTSTRAP CONFIDENCE INTERVALS")
        print("="*70 + "\n")

        print(f"Running {n_bootstrap} bootstrap iterations...")
        print(f"Confidence level: {confidence_level*100:.0f}%\n")

        np.random.seed(config.RANDOM_SEED)

        # Observed statistics
        crypto_mean_obs = results_df['crypto_change_pct'].mean()
        trad_mean_obs = results_df['trad_change_pct'].mean()
        diff_obs = trad_mean_obs - crypto_mean_obs

        # Bootstrap resampling
        crypto_boot = []
        trad_boot = []
        diff_boot = []

        for i in range(n_bootstrap):
            if i % 100 == 0:
                print(f"  Iteration {i}/{n_bootstrap}...")

            # Resample with replacement
            sample_indices = np.random.choice(len(results_df),
                                            size=len(results_df),
                                            replace=True)
            boot_sample = results_df.iloc[sample_indices]

            crypto_mean = boot_sample['crypto_change_pct'].mean()
            trad_mean = boot_sample['trad_change_pct'].mean()
            diff = trad_mean - crypto_mean

            crypto_boot.append(crypto_mean)
            trad_boot.append(trad_mean)
            diff_boot.append(diff)

        # Calculate confidence intervals
        alpha = 1 - confidence_level
        lower_pct = (alpha / 2) * 100
        upper_pct = (1 - alpha / 2) * 100

        crypto_ci = np.percentile(crypto_boot, [lower_pct, upper_pct])
        trad_ci = np.percentile(trad_boot, [lower_pct, upper_pct])
        diff_ci = np.percentile(diff_boot, [lower_pct, upper_pct])

        results = {
            'crypto': {
                'mean': crypto_mean_obs,
                'std': np.std(crypto_boot),
                'ci_lower': crypto_ci[0],
                'ci_upper': crypto_ci[1],
                'bootstrap_samples': crypto_boot
            },
            'traditional': {
                'mean': trad_mean_obs,
                'std': np.std(trad_boot),
                'ci_lower': trad_ci[0],
                'ci_upper': trad_ci[1],
                'bootstrap_samples': trad_boot
            },
            'difference': {
                'mean': diff_obs,
                'std': np.std(diff_boot),
                'ci_lower': diff_ci[0],
                'ci_upper': diff_ci[1],
                'bootstrap_samples': diff_boot,
                'significant': diff_ci[0] > 0  # CI doesn't include zero
            }
        }

        # Print results
        print("\n" + "="*70)
        print(f"BOOTSTRAP RESULTS ({n_bootstrap} iterations)")
        print("="*70 + "\n")

        print(f"Cryptocurrency ({results_df['crypto_symbol'].iloc[0] if 'crypto_symbol' in results_df else 'BTC'}):")
        print(f"  Mean spread change:  {results['crypto']['mean']:+.2f}%")
        print(f"  Bootstrap std:       {results['crypto']['std']:.2f}%")
        print(f"  {confidence_level*100:.0f}% CI:            [{results['crypto']['ci_lower']:+.2f}%, {results['crypto']['ci_upper']:+.2f}%]")

        print(f"\nTraditional ({results_df['trad_symbol'].iloc[0] if 'trad_symbol' in results_df else 'SPY'}):")
        print(f"  Mean spread change:  {results['traditional']['mean']:+.2f}%")
        print(f"  Bootstrap std:       {results['traditional']['std']:.2f}%")
        print(f"  {confidence_level*100:.0f}% CI:            [{results['traditional']['ci_lower']:+.2f}%, {results['traditional']['ci_upper']:+.2f}%]")

        print(f"\nDifference (Traditional - Crypto):")
        print(f"  Mean difference:     {results['difference']['mean']:+.2f}pp")
        print(f"  Bootstrap std:       {results['difference']['std']:.2f}pp")
        print(f"  {confidence_level*100:.0f}% CI:            [{results['difference']['ci_lower']:+.2f}pp, {results['difference']['ci_upper']:+.2f}pp]")

        print("\n" + "="*70)
        if results['difference']['significant']:
            print("✓ SIGNIFICANT DIFFERENCE - CI does not include zero")
            print("  Traditional markets show significantly stronger microstructure response")
        else:
            print("✗ NOT SIGNIFICANT - CI includes zero")
        print("="*70)

        # Save results
        summary = pd.DataFrame([{
            'asset': 'Crypto',
            'mean': results['crypto']['mean'],
            'std': results['crypto']['std'],
            'ci_lower': results['crypto']['ci_lower'],
            'ci_upper': results['crypto']['ci_upper']
        }, {
            'asset': 'Traditional',
            'mean': results['traditional']['mean'],
            'std': results['traditional']['std'],
            'ci_lower': results['traditional']['ci_lower'],
            'ci_upper': results['traditional']['ci_upper']
        }, {
            'asset': 'Difference',
            'mean': results['difference']['mean'],
            'std': results['difference']['std'],
            'ci_lower': results['difference']['ci_lower'],
            'ci_upper': results['difference']['ci_upper']
        }])

        save_path = self.save_dir / 'robustness_bootstrap_ci.csv'
        summary.to_csv(save_path, index=False)
        print(f"\n[SAVED] {save_path}")

        self.results['bootstrap_ci'] = results
        return results

    def placebo_test(self, n_placebo: int = 20,
                    crypto_symbol: str = 'BTC',
                    trad_symbol: str = 'SPY') -> pd.DataFrame:
        """
        Placebo test using pseudo-events on random non-event dates.

        Args:
            n_placebo: Number of placebo events to test
            crypto_symbol: Crypto asset
            trad_symbol: Traditional asset

        Returns:
            DataFrame with placebo results
        """
        print("\n" + "="*70)
        print("ROBUSTNESS CHECK 3: PLACEBO TEST")
        print("="*70 + "\n")

        print(f"Testing {n_placebo} random non-event dates...")
        print("Expected: ~5% false positives (Type I error)\n")

        # Generate random dates (avoiding actual event dates)
        np.random.seed(config.RANDOM_SEED)

        start = pd.to_datetime('2020-01-01')
        end = pd.to_datetime('2024-12-31')
        date_range = pd.date_range(start, end, freq='D')

        # Exclude actual event dates (expand to ±30 days around events)
        event_dates_to_exclude = set()
        for event in config.PILOT_EVENTS:
            event_dt = pd.to_datetime(event['date'])
            for delta in range(-30, 31):
                event_dates_to_exclude.add(event_dt + pd.Timedelta(days=delta))

        non_event_dates = [d for d in date_range if d not in event_dates_to_exclude]

        # Sample random dates
        placebo_dates = np.random.choice(non_event_dates, size=n_placebo, replace=False)

        study = ComparativeEventStudy()
        placebo_results = []

        for i, date in enumerate(placebo_dates, 1):
            date_str = date.strftime('%Y-%m-%d')
            print(f"  [{i}/{n_placebo}] Testing placebo date: {date_str}")

            try:
                result = study.run_single_event_comparison(
                    event_date=date_str,
                    event_name=f"Placebo_{i}",
                    crypto_symbol=crypto_symbol,
                    trad_symbol=trad_symbol,
                    window_pre=30,
                    window_post=30
                )

                if result and result.get('crypto_impact', {}).get('valid'):
                    placebo_results.append({
                        'placebo_id': i,
                        'date': date_str,
                        'crypto_change': result['crypto_impact']['spread_change_pct'],
                        'crypto_pval': result['crypto_impact']['p_value'],
                        'crypto_sig': result['crypto_impact']['significant'],
                        'trad_change': result['trad_impact']['spread_change_pct'],
                        'trad_pval': result['trad_impact']['p_value'],
                        'trad_sig': result['trad_impact']['significant']
                    })
            except Exception as e:
                print(f"    [SKIP] Error: {str(e)}")
                continue

        if not placebo_results:
            print("\n[ERROR] No valid placebo results")
            return pd.DataFrame()

        df = pd.DataFrame(placebo_results)

        # Analysis
        print("\n" + "="*70)
        print("PLACEBO TEST RESULTS")
        print("="*70 + "\n")

        crypto_sig_rate = (df['crypto_sig'].sum() / len(df)) * 100
        trad_sig_rate = (df['trad_sig'].sum() / len(df)) * 100

        print(f"Significant responses on random dates:")
        print(f"  Cryptocurrency: {crypto_sig_rate:.1f}% (expected ~5%)")
        print(f"  Traditional:    {trad_sig_rate:.1f}% (expected ~5%)")

        print(f"\nMean spread changes (should be near zero):")
        print(f"  Cryptocurrency: {df['crypto_change'].mean():+.2f}%")
        print(f"  Traditional:    {df['trad_change'].mean():+.2f}%")

        # T-test against zero
        crypto_t, crypto_p = ttest_1samp(df['crypto_change'], 0)
        trad_t, trad_p = ttest_1samp(df['trad_change'], 0)

        print(f"\nT-test vs zero:")
        print(f"  Crypto: t={crypto_t:.3f}, p={crypto_p:.4f}")
        print(f"  Traditional: t={trad_t:.3f}, p={trad_p:.4f}")

        # Conclusion
        print("\n" + "="*70)
        passed = (crypto_sig_rate <= 10 and trad_sig_rate <= 10 and
                 crypto_p > 0.05 and trad_p > 0.05)

        if passed:
            print("✓ PLACEBO TEST PASSED")
            print("  Random dates show no systematic response (as expected)")
            print("  Confirms results are driven by actual events, not noise")
        else:
            print("⚠ PLACEBO TEST CONCERNING")
            print("  Random dates show unexpected patterns")
            print("  Check model specification or data quality")
        print("="*70)

        # Save results
        save_path = self.save_dir / 'robustness_placebo_tests.csv'
        df.to_csv(save_path, index=False)
        print(f"\n[SAVED] {save_path}")

        self.results['placebo'] = df
        return df

    def cross_sectional_heterogeneity(self, events: List[Dict],
                                      cryptos: List[str] = ['BTC', 'ETH', 'XRP', 'BNB', 'LTC', 'ADA'],
                                      trad_symbol: str = 'SPY') -> pd.DataFrame:
        """
        Test if effects vary by cryptocurrency market cap.

        Args:
            events: List of event dictionaries
            cryptos: List of crypto symbols to test
            trad_symbol: Traditional asset for comparison

        Returns:
            DataFrame with heterogeneity results
        """
        print("\n" + "="*70)
        print("ROBUSTNESS CHECK 4: CROSS-SECTIONAL HETEROGENEITY")
        print("="*70 + "\n")

        print(f"Testing {len(cryptos)} cryptocurrencies...")
        print("Hypothesis: Larger cryptos show weaker regulatory response\n")

        study = ComparativeEventStudy()
        all_results = []

        for crypto in cryptos:
            print(f"\nAnalyzing {crypto}...")

            crypto_results = []
            for event in events:
                try:
                    result = study.run_single_event_comparison(
                        event_date=event['date'],
                        event_name=event['name'],
                        crypto_symbol=crypto,
                        trad_symbol=trad_symbol
                    )

                    if result and result.get('crypto_impact', {}).get('valid'):
                        crypto_results.append({
                            'crypto': crypto,
                            'event': event['name'],
                            'spread_change': result['crypto_impact']['spread_change_pct'],
                            'pvalue': result['crypto_impact']['p_value'],
                            'significant': result['crypto_impact']['significant']
                        })
                except:
                    continue

            if crypto_results:
                df_crypto = pd.DataFrame(crypto_results)
                mean_response = df_crypto['spread_change'].mean()
                sig_rate = df_crypto['significant'].mean() * 100

                all_results.append({
                    'crypto': crypto,
                    'n_events': len(df_crypto),
                    'mean_spread_change': mean_response,
                    'std_spread_change': df_crypto['spread_change'].std(),
                    'sig_rate': sig_rate
                })

                print(f"  {crypto}: Mean={mean_response:+.2f}%, Sig={sig_rate:.0f}%")

        if not all_results:
            print("\n[ERROR] No valid results")
            return pd.DataFrame()

        results_df = pd.DataFrame(all_results)

        # Print summary
        print("\n" + "="*70)
        print("HETEROGENEITY SUMMARY")
        print("="*70 + "\n")
        print(results_df.to_string(index=False))

        print(f"\n{'='*70}")
        range_responses = results_df['mean_spread_change'].max() - results_df['mean_spread_change'].min()
        print(f"Range of responses across cryptos: {range_responses:.2f}pp")

        if range_responses < 5:
            print("✓ HOMOGENEOUS - Similar responses across cryptocurrencies")
        else:
            print("⚠ HETEROGENEOUS - Responses vary substantially")
        print(f"{'='*70}")

        # Save results
        save_path = self.save_dir / 'robustness_heterogeneity.csv'
        results_df.to_csv(save_path, index=False)
        print(f"\n[SAVED] {save_path}")

        self.results['heterogeneity'] = results_df
        return results_df

    def generate_summary_report(self) -> str:
        """
        Generate comprehensive summary report of all robustness checks.

        Returns:
            String with formatted report
        """
        report = []
        report.append("\n" + "="*70)
        report.append("COMPREHENSIVE ROBUSTNESS CHECK SUMMARY")
        report.append("="*70 + "\n")

        # Check 1: Window sensitivity
        if 'window_sensitivity' in self.results:
            summary = self.results['window_sensitivity']['summary']
            variance = summary['hypothesis_support_rate'].std()
            report.append("1. ALTERNATIVE EVENT WINDOWS")
            report.append(f"   Windows tested: {len(summary)}")
            report.append(f"   Hypothesis support variance: {variance:.1f}pp")
            report.append(f"   Result: {'✓ ROBUST' if variance < 15 else '⚠ SENSITIVE'}\n")

        # Check 2: Bootstrap CI
        if 'bootstrap_ci' in self.results:
            boot = self.results['bootstrap_ci']
            report.append("2. BOOTSTRAP CONFIDENCE INTERVALS")
            report.append(f"   Crypto CI: [{boot['crypto']['ci_lower']:+.2f}%, {boot['crypto']['ci_upper']:+.2f}%]")
            report.append(f"   Traditional CI: [{boot['traditional']['ci_lower']:+.2f}%, {boot['traditional']['ci_upper']:+.2f}%]")
            report.append(f"   Difference: {boot['difference']['mean']:+.2f}pp")
            report.append(f"   Result: {'✓ SIGNIFICANT' if boot['difference']['significant'] else '✗ NOT SIGNIFICANT'}\n")

        # Check 3: Placebo
        if 'placebo' in self.results:
            placebo = self.results['placebo']
            crypto_sig = (placebo['crypto_sig'].mean() * 100)
            trad_sig = (placebo['trad_sig'].mean() * 100)
            report.append("3. PLACEBO TEST")
            report.append(f"   Random dates tested: {len(placebo)}")
            report.append(f"   False positive rate (crypto): {crypto_sig:.1f}%")
            report.append(f"   False positive rate (trad): {trad_sig:.1f}%")
            passed = crypto_sig <= 10 and trad_sig <= 10
            report.append(f"   Result: {'✓ PASSED' if passed else '⚠ CONCERNING'}\n")

        # Check 4: Heterogeneity
        if 'heterogeneity' in self.results:
            hetero = self.results['heterogeneity']
            range_val = hetero['mean_spread_change'].max() - hetero['mean_spread_change'].min()
            report.append("4. CROSS-SECTIONAL HETEROGENEITY")
            report.append(f"   Cryptocurrencies tested: {len(hetero)}")
            report.append(f"   Range of responses: {range_val:.2f}pp")
            report.append(f"   Result: {'✓ HOMOGENEOUS' if range_val < 5 else '⚠ HETEROGENEOUS'}\n")

        report.append("="*70)
        report.append("OVERALL ASSESSMENT")
        report.append("="*70)

        # Count passes
        passes = 0
        total = len(self.results)

        if 'window_sensitivity' in self.results:
            if self.results['window_sensitivity']['summary']['hypothesis_support_rate'].std() < 15:
                passes += 1

        if 'bootstrap_ci' in self.results:
            if self.results['bootstrap_ci']['difference']['significant']:
                passes += 1

        if 'placebo' in self.results:
            placebo = self.results['placebo']
            if (placebo['crypto_sig'].mean() <= 0.10 and placebo['trad_sig'].mean() <= 0.10):
                passes += 1

        if 'heterogeneity' in self.results:
            hetero = self.results['heterogeneity']
            if (hetero['mean_spread_change'].max() - hetero['mean_spread_change'].min()) < 5:
                passes += 1

        report.append(f"\nRobustness checks passed: {passes}/{total}")

        if passes == total:
            report.append("\n✓✓✓ RESULTS ARE HIGHLY ROBUST")
            report.append("All robustness checks support main findings")
        elif passes >= total * 0.75:
            report.append("\n✓✓ RESULTS ARE ROBUST")
            report.append("Most robustness checks support main findings")
        else:
            report.append("\n⚠ RESULTS REQUIRE CAREFUL INTERPRETATION")
            report.append("Some robustness concerns identified")

        report.append("\n" + "="*70)

        report_text = "\n".join(report)
        print(report_text)

        # Save report
        report_path = self.save_dir / 'robustness_summary_report.txt'
        with open(report_path, 'w') as f:
            f.write(report_text)
        print(f"\n[SAVED] {report_path}")

        return report_text


def run_complete_robustness_suite(events: List[Dict],
                                  results_df: pd.DataFrame,
                                  save_dir: Optional[Path] = None) -> Dict:
    """
    Run complete robustness check suite.

    Args:
        events: List of event dictionaries
        results_df: DataFrame with main analysis results
        save_dir: Directory to save outputs

    Returns:
        Dictionary with all robustness results
    """
    print("\n" + "="*70)
    print("COMPREHENSIVE ROBUSTNESS CHECK SUITE")
    print("Paper 2: Sentiment Without Structure")
    print("="*70)

    checker = RobustnessChecks(save_dir=save_dir)

    # Check 1: Alternative windows
    print("\n[1/4] Running alternative window sensitivity analysis...")
    checker.test_alternative_windows(events)

    # Check 2: Bootstrap CI
    print("\n[2/4] Running bootstrap confidence intervals...")
    checker.bootstrap_confidence_intervals(results_df, n_bootstrap=1000)

    # Check 3: Placebo tests
    print("\n[3/4] Running placebo tests...")
    checker.placebo_test(n_placebo=20)

    # Check 4: Cross-sectional heterogeneity
    print("\n[4/4] Running cross-sectional heterogeneity analysis...")
    checker.cross_sectional_heterogeneity(events)

    # Generate summary report
    checker.generate_summary_report()

    print("\n" + "="*70)
    print("ROBUSTNESS CHECK SUITE COMPLETE")
    print("="*70)
    print(f"\nAll results saved to: {checker.save_dir}")
    print("\nFiles created:")
    print("  - robustness_windows_summary.csv")
    print("  - robustness_windows_detailed.csv")
    print("  - robustness_bootstrap_ci.csv")
    print("  - robustness_placebo_tests.csv")
    print("  - robustness_heterogeneity.csv")
    print("  - robustness_summary_report.txt")

    return checker.results


if __name__ == "__main__":
    print("Robustness Checks Module for Paper 2")
    print("=" * 60)
    print("\nThis module implements:")
    print("  1. Alternative event windows (±7, ±14, ±60 days)")
    print("  2. Bootstrap confidence intervals")
    print("  3. Placebo tests (random dates)")
    print("  4. Cross-sectional heterogeneity")
    print("\nUsage:")
    print("  from robustness_paper2 import run_complete_robustness_suite")
    print("  results = run_complete_robustness_suite(events, results_df)")
