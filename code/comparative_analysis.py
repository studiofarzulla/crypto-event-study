"""
Comparative Analysis Framework
===============================

Compares crypto vs traditional market responses to regulatory events.

Key analyses:
1. Microstructure event study (spread/depth changes)
2. Extended TARCH-X estimation (crypto vs traditional)
3. Variance decomposition (sentiment vs microstructure channels)
4. Statistical significance testing
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from scipy.stats import ttest_ind, ttest_rel
import config
from microstructure_data import MicrostructureDataCollector
from tarch_x_microstructure import estimate_tarch_x_micro, TARCHXMicroResults


class ComparativeEventStudy:
    """
    Comparative event study framework for crypto vs traditional markets.
    """

    def __init__(self):
        """Initialize comparative analysis framework."""
        self.collector = MicrostructureDataCollector()
        self.results = []

    def run_single_event_comparison(self,
                                    event_date: str,
                                    event_name: str,
                                    crypto_symbol: str = 'BTC',
                                    trad_symbol: str = 'SPY',
                                    window_pre: int = 30,
                                    window_post: int = 30) -> Dict:
        """
        Run comparative analysis for single event.

        Args:
            event_date: Event date (YYYY-MM-DD)
            event_name: Event name
            crypto_symbol: Cryptocurrency symbol
            trad_symbol: Traditional asset symbol
            window_pre: Days before event
            window_post: Days after event

        Returns:
            Dictionary with comparison results
        """
        print(f"\n{'='*70}")
        print(f"COMPARATIVE ANALYSIS: {event_name}")
        print(f"Date: {event_date}")
        print(f"{'='*70}\n")

        # Collect microstructure data
        crypto_micro = self.collector.collect_event_window_microstructure(
            symbol=crypto_symbol,
            event_date=event_date,
            days_before=window_pre,
            days_after=window_post,
            asset_type='crypto'
        )

        trad_micro = self.collector.collect_event_window_microstructure(
            symbol=trad_symbol,
            event_date=event_date,
            days_before=window_pre,
            days_after=window_post,
            asset_type='traditional'
        )

        if crypto_micro.empty or trad_micro.empty:
            print("[SKIP] Insufficient data")
            return {}

        # Calculate event impact on microstructure
        crypto_impact = self._calculate_microstructure_impact(crypto_micro)
        trad_impact = self._calculate_microstructure_impact(trad_micro)

        # Statistical comparison
        comparison = self._compare_impacts(crypto_impact, trad_impact, event_name)

        # Store results
        result = {
            'event_date': event_date,
            'event_name': event_name,
            'crypto_symbol': crypto_symbol,
            'trad_symbol': trad_symbol,
            'crypto_impact': crypto_impact,
            'trad_impact': trad_impact,
            'comparison': comparison,
            'crypto_data': crypto_micro,
            'trad_data': trad_micro
        }

        self.results.append(result)
        return result

    def _calculate_microstructure_impact(self, df: pd.DataFrame) -> Dict:
        """
        Calculate microstructure impact from event window data.

        Args:
            df: DataFrame with pre_event/post_event indicators

        Returns:
            Dictionary with impact statistics
        """
        pre_data = df[df['pre_event']]
        post_data = df[df['post_event']]

        if pre_data.empty or post_data.empty:
            return {'valid': False}

        # Spread analysis
        pre_spread = pre_data['spread_pct'].mean()
        post_spread = post_data['spread_pct'].mean()
        spread_change = post_spread - pre_spread
        spread_change_pct = (spread_change / pre_spread) * 100 if pre_spread > 0 else 0

        # T-test for significance
        t_stat, p_val = ttest_ind(
            post_data['spread_pct'].dropna(),
            pre_data['spread_pct'].dropna()
        )

        # Volume analysis (if available)
        volume_change = 0
        volume_change_pct = 0
        if 'volume' in df.columns:
            pre_vol = pre_data['volume'].mean()
            post_vol = post_data['volume'].mean()
            if pre_vol > 0:
                volume_change = post_vol - pre_vol
                volume_change_pct = (volume_change / pre_vol) * 100

        return {
            'valid': True,
            'pre_spread_mean': pre_spread,
            'post_spread_mean': post_spread,
            'spread_change_abs': spread_change,
            'spread_change_pct': spread_change_pct,
            't_statistic': t_stat,
            'p_value': p_val,
            'significant': p_val < 0.05,
            'highly_significant': p_val < 0.01,
            'pre_volume_mean': pre_data.get('volume', pd.Series()).mean(),
            'post_volume_mean': post_data.get('volume', pd.Series()).mean(),
            'volume_change_pct': volume_change_pct,
            'n_pre': len(pre_data),
            'n_post': len(post_data)
        }

    def _compare_impacts(self, crypto: Dict, trad: Dict, event_name: str) -> Dict:
        """
        Compare crypto vs traditional impacts.

        Args:
            crypto: Crypto impact statistics
            trad: Traditional impact statistics
            event_name: Event name for display

        Returns:
            Comparison dictionary
        """
        if not crypto.get('valid') or not trad.get('valid'):
            return {'hypothesis_supported': False, 'reason': 'Invalid data'}

        # Difference in spread changes
        diff_spread = trad['spread_change_pct'] - crypto['spread_change_pct']

        # Hypothesis: crypto shows no/weak response, traditional shows strong response
        hypothesis_supported = (not crypto['significant']) and trad['significant']

        # Print comparison
        print("Microstructure Response Comparison:\n")
        print(f"{'Metric':<30} {'Crypto':<15} {'Traditional':<15} {'Difference'}")
        print("-" * 70)
        print(f"{'Pre-event spread (%):':<30} {crypto['pre_spread_mean']:<15.4f} "
              f"{trad['pre_spread_mean']:<15.4f}")
        print(f"{'Post-event spread (%):':<30} {crypto['post_spread_mean']:<15.4f} "
              f"{trad['post_spread_mean']:<15.4f}")
        print(f"{'Spread change (%):':<30} {crypto['spread_change_pct']:<15.2f} "
              f"{trad['spread_change_pct']:<15.2f} {diff_spread:+.2f}pp")
        print(f"{'p-value:':<30} {crypto['p_value']:<15.4f} {trad['p_value']:<15.4f}")
        print(f"{'Significant:':<30} {str(crypto['significant']):<15} "
              f"{str(trad['significant']):<15}")

        print(f"\n{'='*70}")
        print(f"HYPOTHESIS CHECK: {'SUPPORTED ✓' if hypothesis_supported else 'NOT SUPPORTED ✗'}")
        print(f"{'='*70}\n")

        if hypothesis_supported:
            print("✓ Crypto shows no significant microstructure response")
            print("✓ Traditional shows significant microstructure response")
            print("→ Supports 'sentiment without structure' mechanism\n")

        return {
            'diff_spread_change': diff_spread,
            'hypothesis_supported': hypothesis_supported,
            'crypto_significant': crypto['significant'],
            'trad_significant': trad['significant'],
            'crypto_pval': crypto['p_value'],
            'trad_pval': trad['p_value']
        }

    def run_multi_event_analysis(self, events: List[Dict]) -> pd.DataFrame:
        """
        Run analysis across multiple events.

        Args:
            events: List of event dictionaries with 'date' and 'name' keys

        Returns:
            DataFrame with aggregated results
        """
        print("\n" + "="*70)
        print("MULTI-EVENT COMPARATIVE ANALYSIS")
        print("="*70 + "\n")
        print(f"Analyzing {len(events)} events...")

        results_list = []

        for i, event in enumerate(events, 1):
            print(f"\n[{i}/{len(events)}] {event['name']}")

            result = self.run_single_event_comparison(
                event_date=event['date'],
                event_name=event['name'],
                crypto_symbol='BTC',
                trad_symbol='SPY'
            )

            if result:
                results_list.append({
                    'event': event['name'],
                    'date': event['date'],
                    'type': event.get('type', 'Unknown'),
                    'crypto_change_pct': result['crypto_impact']['spread_change_pct'],
                    'crypto_pval': result['crypto_impact']['p_value'],
                    'crypto_sig': result['crypto_impact']['significant'],
                    'trad_change_pct': result['trad_impact']['spread_change_pct'],
                    'trad_pval': result['trad_impact']['p_value'],
                    'trad_sig': result['trad_impact']['significant'],
                    'difference': result['comparison']['diff_spread_change'],
                    'hypothesis_supported': result['comparison']['hypothesis_supported']
                })

        if not results_list:
            print("\n[ERROR] No valid results obtained")
            return pd.DataFrame()

        df = pd.DataFrame(results_list)

        # Summary statistics
        print("\n" + "="*70)
        print("AGGREGATE RESULTS SUMMARY")
        print("="*70 + "\n")

        print(f"Events analyzed: {len(df)}")
        print(f"Hypothesis supported: {df['hypothesis_supported'].sum()}/{len(df)} "
              f"({(df['hypothesis_supported'].sum()/len(df))*100:.1f}%)\n")

        print("Cryptocurrency Markets:")
        print(f"  Mean spread change:    {df['crypto_change_pct'].mean():+.2f}%")
        print(f"  Median spread change:  {df['crypto_change_pct'].median():+.2f}%")
        print(f"  Significant responses: {df['crypto_sig'].sum()}/{len(df)}")

        print("\nTraditional Markets:")
        print(f"  Mean spread change:    {df['trad_change_pct'].mean():+.2f}%")
        print(f"  Median spread change:  {df['trad_change_pct'].median():+.2f}%")
        print(f"  Significant responses: {df['trad_sig'].sum()}/{len(df)}")

        # Paired t-test
        if len(df) > 1:
            t_stat, p_val = ttest_rel(df['trad_change_pct'], df['crypto_change_pct'])
            print(f"\nPaired t-test (Traditional vs Crypto):")
            print(f"  t-statistic: {t_stat:.3f}")
            print(f"  p-value: {p_val:.4f}")
            print(f"  Result: {'Traditional > Crypto (significant)' if p_val < 0.05 else 'No significant difference'}")

        return df

    def save_results(self, filename: str = 'comparative_analysis_results.csv'):
        """Save results to CSV."""
        if not self.results:
            print("[ERROR] No results to save")
            return

        # Flatten results for CSV
        rows = []
        for r in self.results:
            if 'crypto_impact' in r and r['crypto_impact'].get('valid'):
                rows.append({
                    'event_date': r['event_date'],
                    'event_name': r['event_name'],
                    'crypto_symbol': r['crypto_symbol'],
                    'trad_symbol': r['trad_symbol'],
                    'crypto_spread_change_pct': r['crypto_impact']['spread_change_pct'],
                    'crypto_pvalue': r['crypto_impact']['p_value'],
                    'crypto_significant': r['crypto_impact']['significant'],
                    'trad_spread_change_pct': r['trad_impact']['spread_change_pct'],
                    'trad_pvalue': r['trad_impact']['p_value'],
                    'trad_significant': r['trad_impact']['significant'],
                    'difference_pp': r['comparison']['diff_spread_change'],
                    'hypothesis_supported': r['comparison']['hypothesis_supported']
                })

        df = pd.DataFrame(rows)
        output_path = config.OUTPUTS_DIR / filename
        df.to_csv(output_path, index=False)
        print(f"\n[SAVED] Results saved to: {output_path}")


def run_pilot_comparative_study():
    """
    Run pilot comparative study on configured events.
    """
    print("\n" + "="*70)
    print("PILOT COMPARATIVE STUDY")
    print("Paper 2: Sentiment Without Structure")
    print("="*70 + "\n")

    study = ComparativeEventStudy()

    # Run on pilot events
    results_df = study.run_multi_event_analysis(config.PILOT_EVENTS)

    if not results_df.empty:
        # Save results
        study.save_results('pilot_comparative_results.csv')

        # Interpretation
        success_rate = (results_df['hypothesis_supported'].sum() / len(results_df)) * 100

        print("\n" + "="*70)
        print("PILOT STUDY CONCLUSION")
        print("="*70 + "\n")

        if success_rate >= 60:
            print(f"✓ HYPOTHESIS SUPPORTED ({success_rate:.0f}% success rate)")
            print("\nFindings support the core mechanism:")
            print("  - Cryptocurrency markets show minimal microstructure response")
            print("  - Traditional markets show significant microstructure response")
            print("  - Regulation affects crypto via sentiment, not structure")
            print("\nRecommendation: PROCEED to full study with expanded event set")
        else:
            print(f"✗ MIXED RESULTS ({success_rate:.0f}% success rate)")
            print("\nPossible explanations:")
            print("  - Data quality limitations (OHLC proxy vs true bid-ask)")
            print("  - Event selection requires refinement")
            print("  - Larger sample size needed")
            print("\nRecommendation: Investigate further before full study")

    return results_df


if __name__ == "__main__":
    # Run pilot study
    results = run_pilot_comparative_study()

    if not results.empty:
        print("\n[SUCCESS] Pilot study complete")
        print("Next step: Review outputs/pilot_comparative_results.csv")
    else:
        print("\n[FAILED] Pilot study did not complete")
        print("Check data availability and API access")
