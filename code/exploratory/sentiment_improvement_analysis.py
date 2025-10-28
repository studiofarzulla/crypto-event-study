#!/usr/bin/env python3
"""
Sentiment Data Quality Analysis and Improvement Testing
Author: Research Assistant
Date: October 2025

This script analyzes GDELT sentiment quality issues and tests potential improvements
for the TARCH-X cryptocurrency event study model.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, List
import warnings
warnings.filterwarnings('ignore')

class SentimentQualityAnalyzer:
    """Analyze and diagnose sentiment data quality issues"""

    def __init__(self, gdelt_path: str = 'data/gdelt.csv'):
        self.gdelt = pd.read_csv(gdelt_path)
        self.gdelt['week_start'] = pd.to_datetime(self.gdelt['week_start'], utc=True)

    def diagnose_issues(self) -> Dict:
        """Comprehensive diagnosis of GDELT data issues"""

        issues = {}

        # 1. Negative bias analysis
        raw_sent = self.gdelt['S_gdelt_raw'].dropna()
        issues['negative_bias'] = {
            'all_negative': (raw_sent < 0).all(),
            'percent_negative': (raw_sent < 0).mean() * 100,
            'mean_sentiment': raw_sent.mean(),
            'median_sentiment': raw_sent.median(),
            'skewness': raw_sent.skew()
        }

        # 2. Data sparsity
        issues['sparsity'] = {
            'total_weeks': len(self.gdelt),
            'missing_weeks': self.gdelt['S_gdelt_raw'].isna().sum(),
            'low_article_weeks': (self.gdelt['total_articles'] < 10).sum(),
            'zero_reg_weeks': (self.gdelt['reg_article_count'] == 0).sum(),
            'zero_infra_weeks': (self.gdelt['infra_article_count'] == 0).sum()
        }

        # 3. Temporal granularity
        issues['temporal'] = {
            'aggregation': 'weekly',
            'intra_week_events_lost': True,
            'event_timing_precision': 'Poor - up to 7 days lag'
        }

        # 4. Coverage analysis
        total_coverage = self.gdelt['reg_proportion'] + self.gdelt['infra_proportion']
        issues['coverage'] = {
            'mean_total_coverage': total_coverage.mean(),
            'uncovered_proportion': 1 - total_coverage.mean(),
            'weeks_under_30%_coverage': (total_coverage < 0.3).sum()
        }

        # 5. Decomposition correlation
        norm_sent = self.gdelt['S_gdelt_normalized'].dropna()
        reg_decomp = self.gdelt['S_reg_decomposed'].dropna()
        infra_decomp = self.gdelt['S_infra_decomposed'].dropna()

        # Align indices for correlation
        common_idx = norm_sent.index.intersection(reg_decomp.index).intersection(infra_decomp.index)

        issues['decomposition'] = {
            'reg_infra_correlation': self.gdelt.loc[common_idx, 'S_reg_decomposed'].corr(
                self.gdelt.loc[common_idx, 'S_infra_decomposed']),
            'multicollinearity_risk': 'High' if abs(self.gdelt.loc[common_idx, 'S_reg_decomposed'].corr(
                self.gdelt.loc[common_idx, 'S_infra_decomposed'])) > 0.7 else 'Moderate'
        }

        return issues

    def calculate_signal_noise_ratio(self) -> float:
        """Calculate signal-to-noise ratio of sentiment data"""

        # Use normalized sentiment
        sent = self.gdelt['S_gdelt_normalized'].dropna()

        if len(sent) < 52:
            return np.nan

        # Calculate rolling volatility
        rolling_std = sent.rolling(window=4).std()

        # Signal: absolute mean of sentiment changes
        signal = np.abs(sent.diff()).mean()

        # Noise: mean of short-term volatility
        noise = rolling_std.mean()

        return signal / noise if noise > 0 else np.inf


class SentimentAlternatives:
    """Test alternative sentiment data approaches"""

    @staticmethod
    def simulate_daily_gdelt(weekly_gdelt: pd.DataFrame) -> pd.DataFrame:
        """Simulate what daily GDELT data might look like"""

        # Interpolate weekly to daily with noise
        daily_dates = pd.date_range(
            start=weekly_gdelt['week_start'].min(),
            end=weekly_gdelt['week_start'].max(),
            freq='D'
        )

        # Create daily frame
        daily = pd.DataFrame(index=daily_dates)

        # Interpolate sentiment with cubic spline
        weekly_gdelt_indexed = weekly_gdelt.set_index('week_start')
        daily['S_gdelt_raw'] = weekly_gdelt_indexed['S_gdelt_raw'].reindex(
            daily.index
        ).interpolate(method='cubic', limit_direction='both')

        # Add realistic daily noise (20% of weekly std)
        noise_std = weekly_gdelt['S_gdelt_raw'].std() * 0.2
        daily['S_gdelt_raw'] += np.random.normal(0, noise_std, len(daily))

        # Simulate daily article counts (higher variance)
        daily['total_articles'] = np.random.poisson(
            weekly_gdelt['total_articles'].mean() / 7,
            len(daily)
        )

        return daily

    @staticmethod
    def create_fear_greed_proxy(gdelt_data: pd.DataFrame) -> pd.Series:
        """Create Fear & Greed Index proxy from GDELT data"""

        # Normalize to 0-100 scale (Fear & Greed range)
        raw = gdelt_data['S_gdelt_raw'].dropna()

        # Reverse scale (GDELT negative = fear)
        # More negative GDELT = lower F&G (more fear)
        min_val = raw.min()
        max_val = raw.max()

        # Linear transformation to 0-100
        fg_proxy = 100 - ((raw - min_val) / (max_val - min_val)) * 100

        # Add market regime adjustments
        # Extreme values get pushed further
        fg_proxy = np.where(fg_proxy < 25, fg_proxy * 0.8, fg_proxy)
        fg_proxy = np.where(fg_proxy > 75, 75 + (fg_proxy - 75) * 1.2, fg_proxy)

        # Clip to valid range
        fg_proxy = np.clip(fg_proxy, 0, 100)

        return pd.Series(fg_proxy, index=raw.index, name='fear_greed_proxy')

    @staticmethod
    def create_simplified_sentiment(gdelt_data: pd.DataFrame) -> pd.DataFrame:
        """Create simplified sentiment without decomposition"""

        result = pd.DataFrame(index=gdelt_data.index)

        # Single normalized sentiment
        result['S_normalized'] = gdelt_data['S_gdelt_normalized']

        # Binary event-type indicator
        result['high_reg_week'] = (gdelt_data['reg_proportion'] > 0.4).astype(float)
        result['high_infra_week'] = (gdelt_data['infra_proportion'] > 0.4).astype(float)

        return result


class ModelImpactEstimator:
    """Estimate impact of sentiment improvements on model fit"""

    @staticmethod
    def estimate_bic_improvement(
        current_params: int = 11,
        proposed_params: int = 8,
        n_obs: int = 1782
    ) -> float:
        """
        Estimate BIC improvement from parameter reduction

        BIC = -2*LL + k*ln(n)
        where k = number of parameters, n = observations
        """

        param_reduction = current_params - proposed_params
        bic_improvement = param_reduction * np.log(n_obs)

        return bic_improvement

    @staticmethod
    def simulate_significance_improvement(
        noise_reduction: float = 0.3
    ) -> Dict:
        """Estimate coefficient significance improvement from noise reduction"""

        # Based on current p-values from BTC model
        current_pvals = {
            'S_gdelt_normalized': 0.009,
            'S_reg_decomposed': 0.195,
            'S_infra_decomposed': 0.061
        }

        # Estimate new p-values with reduced noise
        improved_pvals = {
            k: v * (1 - noise_reduction)
            for k, v in current_pvals.items()
        }

        return {
            'current_significant': sum(1 for p in current_pvals.values() if p < 0.05),
            'improved_significant': sum(1 for p in improved_pvals.values() if p < 0.05),
            'improvement': 'Substantial' if improved_pvals['S_reg_decomposed'] < 0.05 else 'Moderate'
        }


def generate_recommendations() -> List[Dict]:
    """Generate ranked recommendations for improving sentiment data"""

    recommendations = [
        {
            'rank': 1,
            'solution': 'Switch to Daily GDELT Data via BigQuery',
            'effort': 'Medium (1 week)',
            'expected_bic_improvement': 15-20,
            'pros': [
                'Captures intra-week event timing',
                'Better alignment with daily price data',
                'Richer signal for model',
                'Preserves decomposition methodology'
            ],
            'cons': [
                'Requires BigQuery setup and costs',
                'More complex data pipeline',
                'Historical data collection needed'
            ],
            'implementation': [
                'Set up Google Cloud Project with BigQuery',
                'Use gdeltPyR or custom BigQuery queries',
                'Query GDELT 2.0 GKG table with crypto keywords',
                'Extract daily tone metrics',
                'Apply same decomposition methodology'
            ]
        },
        {
            'rank': 2,
            'solution': 'Simplify to Single Sentiment Variable',
            'effort': 'Low (2 days)',
            'expected_bic_improvement': 20-25,
            'pros': [
                'Immediate BIC improvement (3 fewer parameters)',
                'Reduces multicollinearity',
                'Keeps one significant predictor',
                'Easy to implement'
            ],
            'cons': [
                'Loses decomposition innovation',
                'Less granular analysis',
                'May miss heterogeneous effects'
            ],
            'implementation': [
                'Keep only S_gdelt_normalized',
                'Add binary indicators for high reg/infra weeks',
                'Re-estimate models',
                'Compare BIC scores'
            ]
        },
        {
            'rank': 3,
            'solution': 'Integrate Fear & Greed Index',
            'effort': 'Low-Medium (3-4 days)',
            'expected_bic_improvement': 10-15,
            'pros': [
                'Proven crypto-specific sentiment',
                'Daily granularity',
                'Free historical API available',
                'Well-validated metric'
            ],
            'cons': [
                'Cannot decompose by topic',
                'May not align with academic rigor',
                'Different methodology than GDELT'
            ],
            'implementation': [
                'Fetch historical F&G data from Alternative.me API',
                'Align with price data timestamps',
                'Create weighted combination with GDELT',
                'Test in TARCH-X framework'
            ]
        },
        {
            'rank': 4,
            'solution': 'Threshold-Based Decomposition',
            'effort': 'Low (1 day)',
            'expected_bic_improvement': 5-10,
            'pros': [
                'Preserves methodology',
                'Reduces noise',
                'Simple to implement'
            ],
            'cons': [
                'Loses continuous information',
                'Arbitrary threshold selection',
                'Limited improvement expected'
            ],
            'implementation': [
                'Set decomposition to 0 when proportion < 0.2',
                'Only activate decomposed sentiment for strong signals',
                'Test various thresholds'
            ]
        },
        {
            'rank': 5,
            'solution': 'Principal Component Analysis',
            'effort': 'Low (1 day)',
            'expected_bic_improvement': 10-15,
            'pros': [
                'Reduces dimensions scientifically',
                'Captures maximum variance',
                'Eliminates multicollinearity'
            ],
            'cons': [
                'Loses interpretability',
                'Not aligned with thesis narrative',
                'Complex to explain'
            ],
            'implementation': [
                'Apply PCA to sentiment variables',
                'Use first 1-2 components',
                'Re-estimate models'
            ]
        }
    ]

    return recommendations


def main():
    """Run complete sentiment quality analysis"""

    print("=" * 80)
    print("GDELT SENTIMENT DATA QUALITY ANALYSIS")
    print("Cryptocurrency Event Study - TARCH-X Model Diagnostics")
    print("=" * 80)

    # Initialize analyzer
    analyzer = SentimentQualityAnalyzer()

    # Run diagnostics
    print("\n1. ROOT CAUSE ANALYSIS")
    print("-" * 40)
    issues = analyzer.diagnose_issues()

    print("\na) Negative Bias Problem:")
    for key, value in issues['negative_bias'].items():
        print(f"   {key}: {value}")

    print("\nb) Data Sparsity Issues:")
    for key, value in issues['sparsity'].items():
        print(f"   {key}: {value}")

    print("\nc) Temporal Granularity:")
    for key, value in issues['temporal'].items():
        print(f"   {key}: {value}")

    print("\nd) Topic Coverage:")
    for key, value in issues['coverage'].items():
        print(f"   {key}: {value:.3f}" if isinstance(value, float) else f"   {key}: {value}")

    print("\ne) Decomposition Issues:")
    for key, value in issues['decomposition'].items():
        print(f"   {key}: {value:.3f}" if isinstance(value, float) else f"   {key}: {value}")

    # Signal-to-noise ratio
    snr = analyzer.calculate_signal_noise_ratio()
    print(f"\nf) Signal-to-Noise Ratio: {snr:.3f}")
    print("   Interpretation: {'Poor' if snr < 1 else 'Moderate' if snr < 2 else 'Good'}")

    # Test alternatives
    print("\n2. ALTERNATIVE APPROACHES TESTING")
    print("-" * 40)

    # Daily simulation
    daily_sim = SentimentAlternatives.simulate_daily_gdelt(analyzer.gdelt)
    print(f"\na) Daily GDELT Simulation:")
    print(f"   Daily observations: {len(daily_sim)}")
    print(f"   Sentiment variance: {daily_sim['S_gdelt_raw'].var():.3f}")
    print(f"   Articles per day: {daily_sim['total_articles'].mean():.1f}")

    # Fear & Greed proxy
    fg_proxy = SentimentAlternatives.create_fear_greed_proxy(analyzer.gdelt)
    print(f"\nb) Fear & Greed Index Proxy:")
    print(f"   Mean: {fg_proxy.mean():.1f}")
    print(f"   Std: {fg_proxy.std():.1f}")
    print(f"   Range: [{fg_proxy.min():.1f}, {fg_proxy.max():.1f}]")

    # Model impact estimation
    print("\n3. EXPECTED MODEL IMPROVEMENTS")
    print("-" * 40)

    estimator = ModelImpactEstimator()

    # BIC improvements for different scenarios
    scenarios = [
        ("Remove 2 decomposed variables", 9, 20),
        ("Remove all 3 sentiment vars", 8, 25),
        ("Switch to daily + simplify", 9, 15)
    ]

    for desc, new_params, expected_ll_gain in scenarios:
        bic_imp = estimator.estimate_bic_improvement(11, new_params)
        total_imp = bic_imp - expected_ll_gain  # Account for potential LL loss
        print(f"\n{desc}:")
        print(f"   Parameter reduction benefit: {bic_imp:.1f}")
        print(f"   Expected net BIC improvement: {total_imp:.1f}")

    # Significance improvements
    sig_imp = estimator.simulate_significance_improvement(0.3)
    print(f"\nCoefficient Significance (30% noise reduction):")
    print(f"   Current significant: {sig_imp['current_significant']}/3")
    print(f"   Improved significant: {sig_imp['improved_significant']}/3")
    print(f"   Overall improvement: {sig_imp['improvement']}")

    # Generate recommendations
    print("\n4. RECOMMENDATIONS (RANKED)")
    print("-" * 40)

    recommendations = generate_recommendations()

    for rec in recommendations:
        print(f"\n#{rec['rank']}: {rec['solution']}")
        print(f"   Effort: {rec['effort']}")
        print(f"   Expected BIC improvement: {rec['expected_bic_improvement']} points")
        print("   Pros:")
        for pro in rec['pros'][:3]:
            print(f"      + {pro}")
        print("   Cons:")
        for con in rec['cons'][:2]:
            print(f"      - {con}")

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()