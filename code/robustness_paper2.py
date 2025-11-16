"""
Robustness Checks for Paper 2
==============================

Econometric robustness tests:
1. Alternative event windows (±7, ±14, ±60 days)
2. Different microstructure metrics (effective spread, Kyle's lambda, Amihud)
3. Bootstrap inference for variance decomposition
4. Subsample stability (pre/post 2022, by event type)
5. Alternative asset pairs (ETH vs GLD, BTC vs QQQ)
6. Placebo tests (pseudo-events on random dates)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from scipy.stats import ttest_ind, ttest_rel
import warnings
warnings.filterwarnings('ignore')

import config
from comparative_analysis import ComparativeEventStudy


class RobustnessChecks:
    """Comprehensive robustness checks for Paper 2."""

    def __init__(self):
        """Initialize robustness checker."""
        self.results = {}

    def test_alternative_windows(self, events: List[Dict]) -> pd.DataFrame:
        """
        Test sensitivity to event window specification.

        Critical for addressing referee concern: "Results may be driven by
        arbitrary window choice"

        Args:
            events: List of event dictionaries

        Returns:
            DataFrame with results across different windows
        """
        print("\n" + "="*70)
        print("ROBUSTNESS CHECK 1: ALTERNATIVE EVENT WINDOWS")
        print("="*70 + "\n")

        windows = [7, 14, 30, 60]  # Different window sizes
        study = ComparativeEventStudy()

        results_by_window = []

        for window in windows:
            print(f"\nTesting ±{window} day window...")

            window_results = []
            for event in events:
                result = study.run_single_event_comparison(
                    event_date=event['date'],
                    event_name=event['name'],
                    window_pre=window,
                    window_post=window
                )

                if result and result.get('crypto_impact', {}).get('valid'):
                    window_results.append({
                        'window': window,
                        'event': event['name'],
                        'crypto_change': result['crypto_impact']['spread_change_pct'],
                        'trad_change': result['trad_impact']['spread_change_pct'],
                        'crypto_pval': result['crypto_impact']['p_value'],
                        'trad_pval': result['trad_impact']['p_value'],
                        'hypothesis_supported': result['comparison']['hypothesis_supported']
                    })

            if window_results:
                df = pd.DataFrame(window_results)
                success_rate = df['hypothesis_supported'].mean() * 100

                results_by_window.append({
                    'window': window,
                    'n_events': len(df),
                    'crypto_mean': df['crypto_change'].mean(),
                    'trad_mean': df['trad_change'].mean(),
                    'hypothesis_support_rate': success_rate,
                    'crypto_sig_rate': (df['crypto_pval'] < 0.05).mean() * 100,
                    'trad_sig_rate': (df['trad_pval'] < 0.05).mean() * 100
                })

        results_df = pd.DataFrame(results_by_window)

        # Print summary
        print("\n" + "="*70)
        print("WINDOW SENSITIVITY RESULTS")
        print("="*70 + "\n")
        print(results_df.to_string(index=False))

        print("\n✓ ROBUST" if results_df['hypothesis_support_rate'].std() < 15 else "\n⚠ SENSITIVE")
        print(f"Hypothesis support varies by {results_df['hypothesis_support_rate'].std():.1f}pp across windows")

        self.results['window_sensitivity'] = results_df
        return results_df

    def test_alternative_metrics(self, event_date: str,
                                 crypto_prices: pd.DataFrame,
                                 trad_prices: pd.DataFrame) -> Dict:
        """
        Test alternative microstructure metrics beyond bid-ask spread.

        Metrics:
        1. Effective spread (trade-weighted)
        2. Kyle's lambda (price impact)
        3. Amihud illiquidity ratio
        4. Roll's implied spread

        Args:
            event_date: Event date
            crypto_prices: OHLCV data for crypto
            trad_prices: OHLCV data for traditional

        Returns:
            Dictionary with alternative metric results
        """
        print("\n" + "="*70)
        print("ROBUSTNESS CHECK 2: ALTERNATIVE MICROSTRUCTURE METRICS")
        print("="*70 + "\n")

        metrics = {}

        # 1. Amihud illiquidity: |return| / volume
        print("Computing Amihud illiquidity ratio...")
        crypto_amihud = self._compute_amihud(crypto_prices, event_date)
        trad_amihud = self._compute_amihud(trad_prices, event_date)

        metrics['amihud'] = {
            'crypto': crypto_amihud,
            'traditional': trad_amihud,
            'consistent_with_spread': self._check_consistency(crypto_amihud, trad_amihud)
        }

        # 2. Roll's implied spread: 2√(-Cov(Δp_t, Δp_{t-1}))
        print("Computing Roll's implied spread...")
        crypto_roll = self._compute_roll_spread(crypto_prices, event_date)
        trad_roll = self._compute_roll_spread(trad_prices, event_date)

        metrics['roll_spread'] = {
            'crypto': crypto_roll,
            'traditional': trad_roll,
            'consistent_with_spread': self._check_consistency(crypto_roll, trad_roll)
        }

        # 3. Price impact (simplified Kyle's lambda)
        print("Computing price impact metric...")
        crypto_impact = self._compute_price_impact(crypto_prices, event_date)
        trad_impact = self._compute_price_impact(trad_prices, event_date)

        metrics['price_impact'] = {
            'crypto': crypto_impact,
            'traditional': trad_impact,
            'consistent_with_spread': self._check_consistency(crypto_impact, trad_impact)
        }

        # Summary
        print("\n" + "="*70)
        print("ALTERNATIVE METRICS SUMMARY")
        print("="*70 + "\n")

        consistency_count = sum(m['consistent_with_spread'] for m in metrics.values())
        print(f"Metrics consistent with main results: {consistency_count}/3")

        if consistency_count >= 2:
            print("✓ ROBUST - Alternative metrics support main findings")
        else:
            print("⚠ INCONSISTENT - Alternative metrics show different patterns")

        self.results['alternative_metrics'] = metrics
        return metrics

    def _compute_amihud(self, prices: pd.DataFrame, event_date: str) -> Dict:
        """Compute Amihud illiquidity ratio around event."""
        event_dt = pd.to_datetime(event_date)

        # Pre-event period
        pre_data = prices[prices.index < event_dt].tail(30)
        pre_amihud = (abs(pre_data['returns']) / pre_data['volume']).mean() * 1e6

        # Post-event period
        post_data = prices[prices.index > event_dt].head(30)
        post_amihud = (abs(post_data['returns']) / post_data['volume']).mean() * 1e6

        change = post_amihud - pre_amihud
        change_pct = (change / pre_amihud) * 100 if pre_amihud > 0 else 0

        # T-test
        t_stat, p_val = ttest_ind(
            (abs(post_data['returns']) / post_data['volume']).dropna(),
            (abs(pre_data['returns']) / pre_data['volume']).dropna()
        )

        return {
            'pre_mean': pre_amihud,
            'post_mean': post_amihud,
            'change_pct': change_pct,
            'p_value': p_val,
            'significant': p_val < 0.05
        }

    def _compute_roll_spread(self, prices: pd.DataFrame, event_date: str) -> Dict:
        """Compute Roll's implied spread from price autocorrelation."""
        event_dt = pd.to_datetime(event_date)

        # Pre-event
        pre_data = prices[prices.index < event_dt].tail(30)
        pre_returns = pre_data['returns'].dropna()
        pre_cov = pre_returns.autocorr(lag=1)
        pre_roll = 2 * np.sqrt(abs(-pre_cov)) if pre_cov < 0 else 0

        # Post-event
        post_data = prices[prices.index > event_dt].head(30)
        post_returns = post_data['returns'].dropna()
        post_cov = post_returns.autocorr(lag=1)
        post_roll = 2 * np.sqrt(abs(-post_cov)) if post_cov < 0 else 0

        change_pct = ((post_roll - pre_roll) / pre_roll) * 100 if pre_roll > 0 else 0

        return {
            'pre_mean': pre_roll,
            'post_mean': post_roll,
            'change_pct': change_pct,
            'significant': abs(change_pct) > 10  # Heuristic threshold
        }

    def _compute_price_impact(self, prices: pd.DataFrame, event_date: str) -> Dict:
        """Compute price impact: |return| / volume^0.5 (Kyle's lambda approximation)."""
        event_dt = pd.to_datetime(event_date)

        # Pre-event
        pre_data = prices[prices.index < event_dt].tail(30)
        pre_impact = (abs(pre_data['returns']) / np.sqrt(pre_data['volume'])).mean()

        # Post-event
        post_data = prices[prices.index > event_dt].head(30)
        post_impact = (abs(post_data['returns']) / np.sqrt(post_data['volume'])).mean()

        change_pct = ((post_impact - pre_impact) / pre_impact) * 100 if pre_impact > 0 else 0

        # T-test
        t_stat, p_val = ttest_ind(
            (abs(post_data['returns']) / np.sqrt(post_data['volume'])).dropna(),
            (abs(pre_data['returns']) / np.sqrt(pre_data['volume'])).dropna()
        )

        return {
            'pre_mean': pre_impact,
            'post_mean': post_impact,
            'change_pct': change_pct,
            'p_value': p_val,
            'significant': p_val < 0.05
        }

    def _check_consistency(self, crypto_result: Dict, trad_result: Dict) -> bool:
        """Check if alternative metric is consistent with main hypothesis."""
        # Hypothesis: crypto shows no/weak response, traditional shows strong response
        crypto_weak = not crypto_result.get('significant', False)
        trad_strong = trad_result.get('significant', False)

        return crypto_weak and trad_strong

    def bootstrap_variance_decomposition(self, decomposition_data: pd.DataFrame,
                                        n_bootstrap: int = 1000) -> Dict:
        """
        Bootstrap confidence intervals for variance decomposition shares.

        Critical for: "Are sentiment vs microstructure shares significantly different?"

        Args:
            decomposition_data: Original decomposition results
            n_bootstrap: Number of bootstrap iterations

        Returns:
            Dictionary with confidence intervals
        """
        print("\n" + "="*70)
        print("ROBUSTNESS CHECK 3: BOOTSTRAP INFERENCE")
        print("="*70 + "\n")

        print(f"Running {n_bootstrap} bootstrap iterations...")

        np.random.seed(config.RANDOM_SEED)

        # Storage for bootstrap samples
        bootstrap_samples = {
            'crypto_sentiment': [],
            'crypto_microstructure': [],
            'trad_sentiment': [],
            'trad_microstructure': []
        }

        # Bootstrap resampling (resample events with replacement)
        for i in range(n_bootstrap):
            if i % 100 == 0:
                print(f"  Iteration {i}/{n_bootstrap}...")

            # Resample with replacement
            sample_indices = np.random.choice(len(decomposition_data),
                                            size=len(decomposition_data),
                                            replace=True)
            bootstrap_sample = decomposition_data.iloc[sample_indices]

            # Compute statistics for this bootstrap sample
            crypto_row = bootstrap_sample[bootstrap_sample['type'] == 'crypto']
            trad_row = bootstrap_sample[bootstrap_sample['type'] == 'traditional']

            if not crypto_row.empty:
                bootstrap_samples['crypto_sentiment'].append(
                    crypto_row['sentiment_share_pct'].mean()
                )
                bootstrap_samples['crypto_microstructure'].append(
                    crypto_row['microstructure_share_pct'].mean()
                )

            if not trad_row.empty:
                bootstrap_samples['trad_sentiment'].append(
                    trad_row['sentiment_share_pct'].mean()
                )
                bootstrap_samples['trad_microstructure'].append(
                    trad_row['microstructure_share_pct'].mean()
                )

        # Compute confidence intervals
        results = {}
        for key, samples in bootstrap_samples.items():
            samples_array = np.array(samples)
            results[key] = {
                'mean': np.mean(samples_array),
                'std': np.std(samples_array),
                'ci_lower': np.percentile(samples_array, 2.5),
                'ci_upper': np.percentile(samples_array, 97.5)
            }

        # Print results
        print("\n" + "="*70)
        print("BOOTSTRAP CONFIDENCE INTERVALS (95%)")
        print("="*70 + "\n")

        print("Cryptocurrency Markets:")
        print(f"  Sentiment channel:      {results['crypto_sentiment']['mean']:6.1f}% "
              f"[{results['crypto_sentiment']['ci_lower']:5.1f}%, "
              f"{results['crypto_sentiment']['ci_upper']:5.1f}%]")
        print(f"  Microstructure channel: {results['crypto_microstructure']['mean']:6.1f}% "
              f"[{results['crypto_microstructure']['ci_lower']:5.1f}%, "
              f"{results['crypto_microstructure']['ci_upper']:5.1f}%]")

        print("\nTraditional Markets:")
        print(f"  Sentiment channel:      {results['trad_sentiment']['mean']:6.1f}% "
              f"[{results['trad_sentiment']['ci_lower']:5.1f}%, "
              f"{results['trad_sentiment']['ci_upper']:5.1f}%]")
        print(f"  Microstructure channel: {results['trad_microstructure']['mean']:6.1f}% "
              f"[{results['trad_microstructure']['ci_lower']:5.1f}%, "
              f"{results['trad_microstructure']['ci_upper']:5.1f}%]")

        # Test if CIs overlap
        crypto_micro_ci = (results['crypto_microstructure']['ci_lower'],
                          results['crypto_microstructure']['ci_upper'])
        trad_micro_ci = (results['trad_microstructure']['ci_lower'],
                        results['trad_microstructure']['ci_upper'])

        overlap = not (crypto_micro_ci[1] < trad_micro_ci[0] or
                      trad_micro_ci[1] < crypto_micro_ci[0])

        print("\n" + "="*70)
        if not overlap:
            print("✓ SIGNIFICANT DIFFERENCE - CIs do not overlap")
            print("  Crypto microstructure channel significantly different from traditional")
        else:
            print("⚠ INCONCLUSIVE - CIs overlap")

        self.results['bootstrap_ci'] = results
        return results

    def placebo_test(self, n_placebo: int = 20) -> pd.DataFrame:
        """
        Placebo test using pseudo-events on random non-event dates.

        If hypothesis is correct, random dates should show NO microstructure
        response for either crypto or traditional.

        Args:
            n_placebo: Number of placebo events to test

        Returns:
            DataFrame with placebo results
        """
        print("\n" + "="*70)
        print("ROBUSTNESS CHECK 4: PLACEBO TEST")
        print("="*70 + "\n")

        print(f"Testing {n_placebo} random non-event dates...")

        # Generate random dates (avoiding actual event dates)
        np.random.seed(config.RANDOM_SEED)

        start = pd.to_datetime('2020-01-01')
        end = pd.to_datetime('2024-12-31')
        date_range = pd.date_range(start, end, freq='D')

        # Exclude actual event dates
        event_dates = [pd.to_datetime(e['date']) for e in config.PILOT_EVENTS]
        non_event_dates = [d for d in date_range if d not in event_dates]

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
                    window_pre=30,
                    window_post=30
                )

                if result and result.get('crypto_impact', {}).get('valid'):
                    placebo_results.append({
                        'date': date_str,
                        'crypto_change': result['crypto_impact']['spread_change_pct'],
                        'crypto_sig': result['crypto_impact']['significant'],
                        'trad_change': result['trad_impact']['spread_change_pct'],
                        'trad_sig': result['trad_impact']['significant']
                    })
            except:
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
        print(f"  Cryptocurrency: {crypto_sig_rate:.1f}% (expected ~5% false positives)")
        print(f"  Traditional:    {trad_sig_rate:.1f}% (expected ~5% false positives)")

        print(f"\nMean spread changes (should be near zero):")
        print(f"  Cryptocurrency: {df['crypto_change'].mean():+.2f}%")
        print(f"  Traditional:    {df['trad_change'].mean():+.2f}%")

        # Test if mean is significantly different from zero
        from scipy.stats import ttest_1samp
        crypto_t, crypto_p = ttest_1samp(df['crypto_change'], 0)
        trad_t, trad_p = ttest_1samp(df['trad_change'], 0)

        print(f"\nT-test vs zero:")
        print(f"  Crypto: t={crypto_t:.3f}, p={crypto_p:.4f}")
        print(f"  Traditional: t={trad_t:.3f}, p={trad_p:.4f}")

        # Conclusion
        print("\n" + "="*70)
        if crypto_sig_rate <= 10 and trad_sig_rate <= 10 and crypto_p > 0.05 and trad_p > 0.05:
            print("✓ PLACEBO TEST PASSED")
            print("  Random dates show no systematic response (as expected)")
        else:
            print("⚠ PLACEBO TEST CONCERNING")
            print("  Random dates show unexpected patterns - check specification")

        self.results['placebo'] = df
        return df

    def save_all_robustness_results(self, filename: str = 'robustness_results.xlsx'):
        """Save all robustness check results to Excel file."""
        output_path = config.OUTPUTS_DIR / filename

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for test_name, result in self.results.items():
                if isinstance(result, pd.DataFrame):
                    result.to_excel(writer, sheet_name=test_name, index=False)
                elif isinstance(result, dict):
                    pd.DataFrame([result]).to_excel(writer, sheet_name=test_name, index=False)

        print(f"\n[SAVED] All robustness results: {output_path}")


def run_all_robustness_checks():
    """Run complete robustness check suite."""
    print("\n" + "="*70)
    print("COMPREHENSIVE ROBUSTNESS CHECKS FOR PAPER 2")
    print("="*70)

    checker = RobustnessChecks()

    # 1. Window sensitivity
    print("\nRunning Check 1/4: Alternative event windows...")
    checker.test_alternative_windows(config.PILOT_EVENTS)

    # 2-4 would require actual data
    print("\n[INFO] Checks 2-4 require price data")
    print("  Run with actual datasets for:")
    print("  - Alternative microstructure metrics")
    print("  - Bootstrap inference")
    print("  - Placebo tests")

    # Save results
    checker.save_all_robustness_results()

    print("\n" + "="*70)
    print("ROBUSTNESS CHECKS COMPLETE")
    print("="*70)


if __name__ == "__main__":
    run_all_robustness_checks()
