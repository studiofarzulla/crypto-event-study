"""
Paper 2 Visualization Tools
============================

Creates publication-ready figures for Paper 2:
1. Microstructure response comparison (crypto vs traditional)
2. Variance decomposition stacked bars
3. Event-by-event spread changes
4. Time series of spread around events
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import config


# Set publication style
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")

FIGURE_DPI = 300
FIGURE_FORMAT = 'pdf'


class Paper2Visualizer:
    """Create all figures for Paper 2."""

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize visualizer.

        Args:
            output_dir: Directory to save figures (default: outputs/figures)
        """
        self.output_dir = output_dir or (config.OUTPUTS_DIR / 'figures')
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def plot_microstructure_comparison(self,
                                      results_df: pd.DataFrame,
                                      save_name: str = 'figure1_microstructure_comparison'):
        """
        Figure 1: Microstructure response comparison.

        Shows spread changes for crypto vs traditional across events.

        Args:
            results_df: DataFrame with crypto_change_pct, trad_change_pct columns
            save_name: Output filename (without extension)
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        # Prepare data
        x = np.arange(len(results_df))
        width = 0.35

        # Bar plot
        crypto_bars = ax.bar(x - width/2, results_df['crypto_change_pct'],
                            width, label='Cryptocurrency (BTC)',
                            color='#2E86AB', alpha=0.8)
        trad_bars = ax.bar(x + width/2, results_df['trad_change_pct'],
                          width, label='Traditional (SPY)',
                          color='#A23B72', alpha=0.8)

        # Significance markers
        for i, row in results_df.iterrows():
            # Crypto significance
            if row['crypto_pval'] < 0.01:
                ax.text(i - width/2, row['crypto_change_pct'],
                       '***', ha='center', va='bottom', fontsize=10)
            elif row['crypto_pval'] < 0.05:
                ax.text(i - width/2, row['crypto_change_pct'],
                       '**', ha='center', va='bottom', fontsize=10)

            # Traditional significance
            if row['trad_pval'] < 0.01:
                ax.text(i + width/2, row['trad_change_pct'],
                       '***', ha='center', va='bottom', fontsize=10)
            elif row['trad_pval'] < 0.05:
                ax.text(i + width/2, row['trad_change_pct'],
                       '**', ha='center', va='bottom', fontsize=10)

        # Formatting
        ax.set_ylabel('Spread Change (%)', fontsize=12)
        ax.set_xlabel('Regulatory Event', fontsize=12)
        ax.set_title('Microstructure Response to Regulatory Events:\n'
                    'Cryptocurrency vs Traditional Markets',
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(results_df['event'], rotation=45, ha='right', fontsize=10)
        ax.legend(fontsize=11, loc='upper left')
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        ax.grid(axis='y', alpha=0.3)

        # Add note about significance
        ax.text(0.02, 0.98, '*** p<0.01, ** p<0.05',
               transform=ax.transAxes, fontsize=9, va='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.tight_layout()

        # Save
        save_path = self.output_dir / f"{save_name}.{FIGURE_FORMAT}"
        plt.savefig(save_path, dpi=FIGURE_DPI, bbox_inches='tight')
        plt.savefig(self.output_dir / f"{save_name}.png", dpi=150, bbox_inches='tight')

        print(f"[SAVED] {save_path}")
        return fig

    def plot_variance_decomposition(self,
                                    decomp_df: pd.DataFrame,
                                    save_name: str = 'figure2_variance_decomposition'):
        """
        Figure 2: Variance decomposition stacked bars.

        Shows how regulatory volatility breaks down by channel.

        Args:
            decomp_df: DataFrame with sentiment/microstructure/direct shares
            save_name: Output filename
        """
        fig, ax = plt.subplots(figsize=(10, 7))

        # Data
        assets = decomp_df['asset'].values
        sentiment = decomp_df['sentiment_share_pct'].values
        microstructure = decomp_df['microstructure_share_pct'].values
        direct = decomp_df['direct_share_pct'].values

        # Stacked bars
        x = np.arange(len(assets))
        width = 0.6

        p1 = ax.barh(x, sentiment, width, label='Sentiment Channel',
                    color='#2E86AB', alpha=0.9)
        p2 = ax.barh(x, microstructure, width, left=sentiment,
                    label='Microstructure Channel', color='#A23B72', alpha=0.9)
        p3 = ax.barh(x, direct, width,
                    left=sentiment + microstructure,
                    label='Direct Effect', color='#F18F01', alpha=0.9)

        # Labels
        ax.set_xlabel('Share of Total Volatility Impact (%)', fontsize=12)
        ax.set_title('Variance Decomposition: Regulatory Event Channels\n'
                    'How Regulation Affects Volatility in Crypto vs Traditional Markets',
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_yticks(x)
        ax.set_yticklabels(assets, fontsize=12)
        ax.legend(loc='lower right', fontsize=11)
        ax.axvline(x=0, color='black', linewidth=0.8)
        ax.grid(axis='x', alpha=0.3)

        # Add percentage labels
        for i, (s, m, d) in enumerate(zip(sentiment, microstructure, direct)):
            if abs(s) > 8:
                ax.text(s/2, i, f'{s:.0f}%', ha='center', va='center',
                       fontweight='bold', color='white', fontsize=11)
            if abs(m) > 8:
                ax.text(s + m/2, i, f'{m:.0f}%', ha='center', va='center',
                       fontweight='bold', color='white', fontsize=11)
            if abs(d) > 8:
                ax.text(s + m + d/2, i, f'{d:.0f}%', ha='center', va='center',
                       fontweight='bold', color='white', fontsize=11)

        plt.tight_layout()

        # Save
        save_path = self.output_dir / f"{save_name}.{FIGURE_FORMAT}"
        plt.savefig(save_path, dpi=FIGURE_DPI, bbox_inches='tight')
        plt.savefig(self.output_dir / f"{save_name}.png", dpi=150, bbox_inches='tight')

        print(f"[SAVED] {save_path}")
        return fig

    def plot_event_time_series(self,
                               event_data: pd.DataFrame,
                               event_name: str,
                               event_date: str,
                               save_name: Optional[str] = None):
        """
        Plot spread time series around single event.

        Args:
            event_data: DataFrame with crypto and traditional spread data
            event_name: Event name for title
            event_date: Event date for vertical line
            save_name: Output filename (auto-generated if None)
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

        event_dt = pd.to_datetime(event_date)

        # Crypto plot
        crypto_data = event_data[event_data['asset_type'] == 'crypto']
        if not crypto_data.empty:
            ax1.plot(crypto_data.index, crypto_data['spread_pct'],
                    linewidth=2, color='#2E86AB', label='BTC')
            ax1.axvline(event_dt, color='red', linestyle='--',
                       linewidth=2, label='Event Date')
            ax1.fill_between(crypto_data.index,
                            crypto_data['spread_pct'].min() * 0.95,
                            crypto_data['spread_pct'].max() * 1.05,
                            where=(crypto_data.index >= event_dt),
                            alpha=0.1, color='red', label='Post-event')
            ax1.set_ylabel('Bid-Ask Spread (%)', fontsize=11)
            ax1.set_title(f'Cryptocurrency Market Response\n{event_name}',
                         fontsize=12, fontweight='bold')
            ax1.legend(fontsize=10)
            ax1.grid(alpha=0.3)

        # Traditional plot
        trad_data = event_data[event_data['asset_type'] == 'traditional']
        if not trad_data.empty:
            ax2.plot(trad_data.index, trad_data['spread_pct'],
                    linewidth=2, color='#A23B72', label='SPY')
            ax2.axvline(event_dt, color='red', linestyle='--',
                       linewidth=2, label='Event Date')
            ax2.fill_between(trad_data.index,
                            trad_data['spread_pct'].min() * 0.95,
                            trad_data['spread_pct'].max() * 1.05,
                            where=(trad_data.index >= event_dt),
                            alpha=0.1, color='red')
            ax2.set_xlabel('Date', fontsize=11)
            ax2.set_ylabel('Bid-Ask Spread (%)', fontsize=11)
            ax2.set_title('Traditional Market Response', fontsize=12, fontweight='bold')
            ax2.legend(fontsize=10)
            ax2.grid(alpha=0.3)

        plt.tight_layout()

        # Save
        if save_name is None:
            save_name = f"event_timeseries_{event_date.replace('-', '')}"
        save_path = self.output_dir / f"{save_name}.{FIGURE_FORMAT}"
        plt.savefig(save_path, dpi=FIGURE_DPI, bbox_inches='tight')

        print(f"[SAVED] {save_path}")
        return fig

    def create_summary_figure(self,
                             results_df: pd.DataFrame,
                             decomp_df: pd.DataFrame,
                             save_name: str = 'figure_summary'):
        """
        Create comprehensive summary figure with multiple panels.

        Args:
            results_df: Microstructure comparison results
            decomp_df: Variance decomposition data
            save_name: Output filename
        """
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

        # Panel A: Average spread changes
        ax1 = fig.add_subplot(gs[0, 0])
        crypto_mean = results_df['crypto_change_pct'].mean()
        trad_mean = results_df['trad_change_pct'].mean()
        crypto_std = results_df['crypto_change_pct'].std()
        trad_std = results_df['trad_change_pct'].std()

        bars = ax1.bar(['Cryptocurrency', 'Traditional'], [crypto_mean, trad_mean],
                      yerr=[crypto_std, trad_std], capsize=10,
                      color=['#2E86AB', '#A23B72'], alpha=0.8)
        ax1.set_ylabel('Mean Spread Change (%)', fontsize=11)
        ax1.set_title('Panel A: Average Microstructure Response',
                     fontsize=12, fontweight='bold')
        ax1.axhline(0, color='black', linewidth=0.8)
        ax1.grid(axis='y', alpha=0.3)

        # Panel B: Significance rates
        ax2 = fig.add_subplot(gs[0, 1])
        crypto_sig_rate = (results_df['crypto_sig'].sum() / len(results_df)) * 100
        trad_sig_rate = (results_df['trad_sig'].sum() / len(results_df)) * 100

        bars = ax2.bar(['Cryptocurrency', 'Traditional'],
                      [crypto_sig_rate, trad_sig_rate],
                      color=['#2E86AB', '#A23B72'], alpha=0.8)
        ax2.set_ylabel('Significant Responses (%)', fontsize=11)
        ax2.set_title('Panel B: Statistical Significance Rate',
                     fontsize=12, fontweight='bold')
        ax2.set_ylim(0, 100)
        ax2.grid(axis='y', alpha=0.3)

        # Panel C: Variance decomposition
        ax3 = fig.add_subplot(gs[1, :])
        assets = decomp_df['asset'].values
        sentiment = decomp_df['sentiment_share_pct'].values
        microstructure = decomp_df['microstructure_share_pct'].values
        direct = decomp_df['direct_share_pct'].values

        x = np.arange(len(assets))
        width = 0.6

        p1 = ax3.barh(x, sentiment, width, label='Sentiment Channel', color='#2E86AB')
        p2 = ax3.barh(x, microstructure, width, left=sentiment,
                     label='Microstructure Channel', color='#A23B72')
        p3 = ax3.barh(x, direct, width, left=sentiment + microstructure,
                     label='Direct Effect', color='#F18F01')

        ax3.set_xlabel('Share of Volatility Impact (%)', fontsize=11)
        ax3.set_title('Panel C: Variance Decomposition by Channel',
                     fontsize=12, fontweight='bold')
        ax3.set_yticks(x)
        ax3.set_yticklabels(assets, fontsize=11)
        ax3.legend(loc='lower right', fontsize=10)
        ax3.grid(axis='x', alpha=0.3)

        # Overall title
        fig.suptitle('Sentiment Without Structure: Regulatory Effects in Crypto vs Traditional Markets',
                    fontsize=16, fontweight='bold', y=0.98)

        # Save
        save_path = self.output_dir / f"{save_name}.{FIGURE_FORMAT}"
        plt.savefig(save_path, dpi=FIGURE_DPI, bbox_inches='tight')
        plt.savefig(self.output_dir / f"{save_name}.png", dpi=150, bbox_inches='tight')

        print(f"[SAVED] {save_path}")
        return fig


def create_all_paper2_figures(results_df: pd.DataFrame,
                               decomp_df: pd.DataFrame):
    """
    Create all figures for Paper 2.

    Args:
        results_df: Comparative microstructure results
        decomp_df: Variance decomposition data
    """
    print("\nCreating Paper 2 figures...")
    print("=" * 60)

    viz = Paper2Visualizer()

    # Figure 1: Microstructure comparison
    print("\n[1/3] Creating microstructure comparison figure...")
    viz.plot_microstructure_comparison(results_df)

    # Figure 2: Variance decomposition
    print("\n[2/3] Creating variance decomposition figure...")
    viz.plot_variance_decomposition(decomp_df)

    # Figure 3: Summary figure
    print("\n[3/3] Creating summary figure...")
    viz.create_summary_figure(results_df, decomp_df)

    print("\n" + "=" * 60)
    print("All figures created successfully!")
    print(f"Output directory: {viz.output_dir}")


if __name__ == "__main__":
    print("Paper 2 Visualization Tools")
    print("=" * 60)
    print("\nThis module creates publication-ready figures:")
    print("  - Figure 1: Microstructure response comparison")
    print("  - Figure 2: Variance decomposition")
    print("  - Figure 3: Summary panel figure")
    print("\nUsage: Import and call create_all_paper2_figures()")
