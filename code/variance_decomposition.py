"""
Variance Decomposition Analysis
================================

Decomposes regulatory event volatility into channels:
1. Sentiment channel (δ_sent × Sentiment)
2. Microstructure channel (δ_spread × Spread + δ_depth × Depth)
3. Direct effect (δ_reg)

Key insight for Paper 2:
- Crypto: ~75% sentiment, ~0% microstructure
- Traditional: ~20% sentiment, ~60% microstructure
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass

import config
from tarch_x_microstructure import TARCHXMicroResults


@dataclass
class VarianceDecomposition:
    """Container for variance decomposition results."""
    asset_name: str
    asset_type: str  # 'crypto' or 'traditional'

    # Total regulatory impact
    total_impact: float

    # Channel contributions (absolute)
    sentiment_contrib: float
    microstructure_contrib: float
    direct_contrib: float

    # Channel shares (%)
    sentiment_share: float
    microstructure_share: float
    direct_share: float

    # Supporting data
    avg_sentiment_during_events: float
    avg_spread_change_during_events: float
    n_regulatory_events: int


class VarianceDecomposer:
    """
    Decompose variance contributions from TARCH-X-Micro results.
    """

    def __init__(self):
        """Initialize variance decomposer."""
        self.decompositions = []

    def decompose_from_tarchx_results(self,
                                     asset_name: str,
                                     asset_type: str,
                                     tarchx_results: TARCHXMicroResults,
                                     event_windows: pd.DataFrame) -> VarianceDecomposition:
        """
        Decompose variance from TARCH-X-Micro estimation results.

        Args:
            asset_name: Asset identifier (e.g., 'BTC', 'SPY')
            asset_type: 'crypto' or 'traditional'
            tarchx_results: Results from extended TARCH-X estimation
            event_windows: DataFrame with event indicators and microstructure data

        Returns:
            VarianceDecomposition object
        """
        print(f"\nDecomposing variance for {asset_name} ({asset_type})...")

        if not tarchx_results.converged:
            print(f"  [SKIP] Model did not converge for {asset_name}")
            return self._create_empty_decomposition(asset_name, asset_type)

        # Extract coefficients
        params = tarchx_results.params

        # Regulatory event coefficient
        delta_reg = 0
        for key in params.keys():
            if 'regulatory' in key.lower() or 'D_event' in key:
                delta_reg = params[key]
                break

        if delta_reg == 0:
            print(f"  [INFO] No regulatory event coefficient found")

        # Sentiment coefficient
        delta_sent = sum(params.get(name, 0)
                        for name in tarchx_results.sentiment_effects.keys())

        # Microstructure coefficients
        delta_spread = params.get('spread', params.get('spread_pct', 0))
        delta_depth = params.get('depth', params.get('total_depth', 0))

        # Calculate average values during regulatory events
        reg_events = event_windows[event_windows.get('regulatory_event', False)]

        if len(reg_events) == 0:
            print(f"  [WARN] No regulatory events found in data")
            avg_sentiment = 0
            avg_spread_change = 0
            n_events = 0
        else:
            avg_sentiment = reg_events.get('sentiment', pd.Series([0])).mean()
            avg_spread_change = reg_events.get('spread_pct', pd.Series([0])).mean()
            n_events = len(reg_events)

        # Decompose contributions
        sentiment_contrib = delta_sent * avg_sentiment
        microstructure_contrib = delta_spread * avg_spread_change
        direct_contrib = delta_reg - sentiment_contrib - microstructure_contrib

        # Total impact
        total_impact = delta_reg

        # Calculate shares
        if total_impact != 0 and abs(total_impact) > 1e-6:
            sentiment_share = (sentiment_contrib / total_impact) * 100
            microstructure_share = (microstructure_contrib / total_impact) * 100
            direct_share = (direct_contrib / total_impact) * 100
        else:
            sentiment_share = 0
            microstructure_share = 0
            direct_share = 0

        decomp = VarianceDecomposition(
            asset_name=asset_name,
            asset_type=asset_type,
            total_impact=total_impact,
            sentiment_contrib=sentiment_contrib,
            microstructure_contrib=microstructure_contrib,
            direct_contrib=direct_contrib,
            sentiment_share=sentiment_share,
            microstructure_share=microstructure_share,
            direct_share=direct_share,
            avg_sentiment_during_events=avg_sentiment,
            avg_spread_change_during_events=avg_spread_change,
            n_regulatory_events=n_events
        )

        self.decompositions.append(decomp)

        # Print results
        self._print_decomposition(decomp)

        return decomp

    def _print_decomposition(self, decomp: VarianceDecomposition):
        """Print variance decomposition results."""
        print(f"\n{'='*60}")
        print(f"VARIANCE DECOMPOSITION: {decomp.asset_name} ({decomp.asset_type})")
        print(f"{'='*60}\n")

        print(f"Total regulatory impact: {decomp.total_impact:+.4f}%")
        print(f"Based on {decomp.n_regulatory_events} regulatory events\n")

        print("Channel Contributions:")
        print(f"{'Channel':<25} {'Absolute':<15} {'Share'}")
        print("-" * 60)
        print(f"{'Sentiment':<25} {decomp.sentiment_contrib:+.4f}% {decomp.sentiment_share:>12.1f}%")
        print(f"{'Microstructure':<25} {decomp.microstructure_contrib:+.4f}% {decomp.microstructure_share:>12.1f}%")
        print(f"{'Direct':<25} {decomp.direct_contrib:+.4f}% {decomp.direct_share:>12.1f}%")
        print("-" * 60)
        print(f"{'Total':<25} {decomp.total_impact:+.4f}% {'100.0%':>12}\n")

        # Interpretation
        print("Interpretation:")
        if decomp.asset_type == 'crypto':
            if abs(decomp.microstructure_share) < 10:
                print("  ✓ Crypto shows minimal microstructure channel (<10%)")
                print("  → Regulation affects primarily via sentiment")
            else:
                print("  ✗ Unexpected: crypto shows significant microstructure channel")
        else:  # traditional
            if abs(decomp.microstructure_share) > 40:
                print("  ✓ Traditional shows dominant microstructure channel (>40%)")
                print("  → Regulation operates through market structure changes")
            else:
                print("  ✗ Unexpected: traditional shows weak microstructure channel")

    def compare_decompositions(self, crypto_decomp: VarianceDecomposition,
                               trad_decomp: VarianceDecomposition) -> Dict:
        """
        Compare crypto vs traditional decompositions.

        Args:
            crypto_decomp: Crypto variance decomposition
            trad_decomp: Traditional variance decomposition

        Returns:
            Dictionary with comparison statistics
        """
        print(f"\n{'='*70}")
        print("COMPARATIVE VARIANCE DECOMPOSITION")
        print(f"{'='*70}\n")

        print(f"{'Channel':<20} {crypto_decomp.asset_name:<15} {trad_decomp.asset_name:<15} {'Difference'}")
        print("-" * 70)
        print(f"{'Sentiment share:':<20} {crypto_decomp.sentiment_share:<15.1f}% "
              f"{trad_decomp.sentiment_share:<15.1f}% "
              f"{(crypto_decomp.sentiment_share - trad_decomp.sentiment_share):+.1f}pp")
        print(f"{'Microstructure:':<20} {crypto_decomp.microstructure_share:<15.1f}% "
              f"{trad_decomp.microstructure_share:<15.1f}% "
              f"{(crypto_decomp.microstructure_share - trad_decomp.microstructure_share):+.1f}pp")
        print(f"{'Direct effect:':<20} {crypto_decomp.direct_share:<15.1f}% "
              f"{trad_decomp.direct_share:<15.1f}% "
              f"{(crypto_decomp.direct_share - trad_decomp.direct_share):+.1f}pp")

        print("\n" + "="*70)
        print("KEY FINDING")
        print("="*70 + "\n")

        sent_diff = crypto_decomp.sentiment_share - trad_decomp.sentiment_share
        micro_diff = crypto_decomp.microstructure_share - trad_decomp.microstructure_share

        if sent_diff > 30 and micro_diff < -30:
            print("✓ HYPOTHESIS STRONGLY SUPPORTED")
            print("\nCryptocurrency markets:")
            print(f"  - Sentiment channel dominates: {crypto_decomp.sentiment_share:.0f}%")
            print(f"  - Microstructure channel negligible: {crypto_decomp.microstructure_share:.0f}%")
            print("\nTraditional markets:")
            print(f"  - Microstructure channel dominates: {trad_decomp.microstructure_share:.0f}%")
            print(f"  - Sentiment channel secondary: {trad_decomp.sentiment_share:.0f}%")
            print("\n→ Regulation operates through fundamentally different channels")
            hypothesis_supported = True
        else:
            print("✗ HYPOTHESIS PARTIALLY SUPPORTED OR NOT SUPPORTED")
            print(f"\nSentiment difference: {sent_diff:+.1f}pp (expected >+30pp)")
            print(f"Microstructure difference: {micro_diff:+.1f}pp (expected <-30pp)")
            hypothesis_supported = False

        return {
            'sentiment_diff': sent_diff,
            'microstructure_diff': micro_diff,
            'hypothesis_supported': hypothesis_supported,
            'crypto_sentiment_dominant': crypto_decomp.sentiment_share > 50,
            'trad_microstructure_dominant': trad_decomp.microstructure_share > 50
        }

    def _create_empty_decomposition(self, asset_name: str, asset_type: str) -> VarianceDecomposition:
        """Create empty decomposition for failed estimations."""
        return VarianceDecomposition(
            asset_name=asset_name,
            asset_type=asset_type,
            total_impact=np.nan,
            sentiment_contrib=np.nan,
            microstructure_contrib=np.nan,
            direct_contrib=np.nan,
            sentiment_share=np.nan,
            microstructure_share=np.nan,
            direct_share=np.nan,
            avg_sentiment_during_events=np.nan,
            avg_spread_change_during_events=np.nan,
            n_regulatory_events=0
        )

    def plot_decomposition_comparison(self, crypto_decomp: VarianceDecomposition,
                                     trad_decomp: VarianceDecomposition,
                                     save_path: Optional[str] = None):
        """
        Create stacked bar chart comparing variance decompositions.

        Args:
            crypto_decomp: Crypto decomposition
            trad_decomp: Traditional decomposition
            save_path: Optional path to save figure
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        # Data
        assets = [crypto_decomp.asset_name, trad_decomp.asset_name]
        sentiment = [crypto_decomp.sentiment_share, trad_decomp.sentiment_share]
        microstructure = [crypto_decomp.microstructure_share, trad_decomp.microstructure_share]
        direct = [crypto_decomp.direct_share, trad_decomp.direct_share]

        # Stacked bar chart
        x = np.arange(len(assets))
        width = 0.5

        p1 = ax.bar(x, sentiment, width, label='Sentiment Channel', color='#2E86AB')
        p2 = ax.bar(x, microstructure, width, bottom=sentiment,
                   label='Microstructure Channel', color='#A23B72')
        p3 = ax.bar(x, direct, width,
                   bottom=[i+j for i,j in zip(sentiment, microstructure)],
                   label='Direct Effect', color='#F18F01')

        # Labels and formatting
        ax.set_ylabel('Share of Total Volatility Impact (%)', fontsize=12)
        ax.set_title('Variance Decomposition: Regulatory Event Channels\n'
                    'Crypto vs Traditional Markets', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(assets, fontsize=12)
        ax.legend(loc='upper right', fontsize=10)
        ax.axhline(y=0, color='black', linew=0.8)
        ax.grid(axis='y', alpha=0.3)

        # Add value labels on bars
        for i, (s, m, d) in enumerate(zip(sentiment, microstructure, direct)):
            if abs(s) > 5:
                ax.text(i, s/2, f'{s:.0f}%', ha='center', va='center',
                       fontweight='bold', color='white')
            if abs(m) > 5:
                ax.text(i, s + m/2, f'{m:.0f}%', ha='center', va='center',
                       fontweight='bold', color='white')
            if abs(d) > 5:
                ax.text(i, s + m + d/2, f'{d:.0f}%', ha='center', va='center',
                       fontweight='bold', color='white')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"\n[SAVED] Figure saved to: {save_path}")

        return fig

    def export_to_dataframe(self) -> pd.DataFrame:
        """Export all decompositions to DataFrame."""
        if not self.decompositions:
            return pd.DataFrame()

        rows = []
        for decomp in self.decompositions:
            rows.append({
                'asset': decomp.asset_name,
                'type': decomp.asset_type,
                'total_impact': decomp.total_impact,
                'sentiment_contrib': decomp.sentiment_contrib,
                'microstructure_contrib': decomp.microstructure_contrib,
                'direct_contrib': decomp.direct_contrib,
                'sentiment_share_pct': decomp.sentiment_share,
                'microstructure_share_pct': decomp.microstructure_share,
                'direct_share_pct': decomp.direct_share,
                'n_events': decomp.n_regulatory_events
            })

        return pd.DataFrame(rows)


if __name__ == "__main__":
    # Example usage (requires actual TARCH-X results)
    print("Variance Decomposition Module")
    print("=" * 60)
    print("\nThis module decomposes regulatory volatility into channels:")
    print("  1. Sentiment channel")
    print("  2. Microstructure channel")
    print("  3. Direct effect")
    print("\nExpected findings (Paper 2):")
    print("  - Crypto: ~75% sentiment, ~0% microstructure")
    print("  - Traditional: ~20% sentiment, ~60% microstructure")
