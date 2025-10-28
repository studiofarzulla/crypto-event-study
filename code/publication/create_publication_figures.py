"""
Publication-Quality Visualization Generator for Cryptocurrency Event Study
============================================================================

Creates publication-ready figures for top-tier finance journals (JoF, JFE, RFS)
Requirements: Vector graphics, grayscale-friendly, LaTeX-compatible

Author: Farzulla Research
Date: October 2025
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
import seaborn as sns
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# PUBLICATION SETTINGS
# ============================================================================

# Configure matplotlib for publication quality
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif'],
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.titlesize': 13,
    'text.usetex': False,  # Set to True if LaTeX is installed
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.format': 'pdf',
    'savefig.bbox': 'tight',
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linestyle': '--',
    'lines.linewidth': 1.5,
})

# Grayscale-friendly color palette with distinct patterns
COLORS = {
    'infrastructure': '#000000',  # Black
    'regulatory': '#666666',      # Dark gray
    'primary': '#000000',
    'secondary': '#4D4D4D',
    'tertiary': '#999999',
    'light': '#CCCCCC',
}

# Pattern styles for grayscale differentiation
PATTERNS = {
    'infrastructure': '///',
    'regulatory': '\\\\\\',
    'significant': 'xxx',
    'non_significant': '...',
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def ensure_output_dir():
    """Create output directory if it doesn't exist"""
    output_dir = Path('/home/kawaiikali/event-study/publication_figures')
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def save_figure(fig, filename, formats=['pdf', 'svg']):
    """Save figure in multiple formats"""
    output_dir = ensure_output_dir()
    for fmt in formats:
        filepath = output_dir / f"{filename}.{fmt}"
        fig.savefig(filepath, format=fmt, bbox_inches='tight',
                   transparent=True, dpi=300)
        print(f"Saved: {filepath}")

def add_significance_markers(ax, x_positions, y_positions, significance_levels):
    """Add asterisks for statistical significance"""
    for x, y, sig in zip(x_positions, y_positions, significance_levels):
        if sig <= 0.01:
            marker = '***'
        elif sig <= 0.05:
            marker = '**'
        elif sig <= 0.10:
            marker = '*'
        else:
            continue
        ax.text(x, y, marker, ha='center', va='bottom', fontsize=8)

# ============================================================================
# FIGURE 1: EVENT TIMELINE VISUALIZATION
# ============================================================================

def create_event_timeline(events_df):
    """
    Creates a timeline showing all 18 events with impact magnitudes

    Parameters:
    -----------
    events_df : pd.DataFrame
        Columns: ['date', 'event_name', 'event_type', 'impact_magnitude', 'p_value']
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    # Sort events by date
    events_df = events_df.sort_values('date')
    events_df['date_num'] = pd.to_datetime(events_df['date']).astype(np.int64) // 10**9

    # Separate infrastructure and regulatory events
    infra_mask = events_df['event_type'] == 'infrastructure'
    reg_mask = events_df['event_type'] == 'regulatory'

    # Plot infrastructure events
    infra_events = events_df[infra_mask]
    if len(infra_events) > 0:
        ax.scatter(pd.to_datetime(infra_events['date']),
                  infra_events['impact_magnitude'],
                  s=150, marker='o', c=COLORS['infrastructure'],
                  edgecolors='black', linewidths=1.5,
                  label='Infrastructure Events', zorder=3)

    # Plot regulatory events
    reg_events = events_df[reg_mask]
    if len(reg_events) > 0:
        ax.scatter(pd.to_datetime(reg_events['date']),
                  reg_events['impact_magnitude'],
                  s=150, marker='s', c=COLORS['regulatory'],
                  edgecolors='black', linewidths=1.5,
                  label='Regulatory Events', zorder=3)

    # Add significance markers
    for _, event in events_df.iterrows():
        y_offset = 0.02 if event['impact_magnitude'] >= 0 else -0.02
        if event['p_value'] <= 0.01:
            ax.text(pd.to_datetime(event['date']),
                   event['impact_magnitude'] + y_offset,
                   '***', ha='center', va='bottom' if event['impact_magnitude'] >= 0 else 'top',
                   fontsize=10, fontweight='bold')
        elif event['p_value'] <= 0.05:
            ax.text(pd.to_datetime(event['date']),
                   event['impact_magnitude'] + y_offset,
                   '**', ha='center', va='bottom' if event['impact_magnitude'] >= 0 else 'top',
                   fontsize=10, fontweight='bold')
        elif event['p_value'] <= 0.10:
            ax.text(pd.to_datetime(event['date']),
                   event['impact_magnitude'] + y_offset,
                   '*', ha='center', va='bottom' if event['impact_magnitude'] >= 0 else 'top',
                   fontsize=10, fontweight='bold')

    # Add horizontal line at zero
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8, alpha=0.5)

    # Formatting
    ax.set_xlabel('Event Date', fontweight='bold')
    ax.set_ylabel('Cumulative Abnormal Return (%)', fontweight='bold')
    ax.set_title('Timeline of Cryptocurrency Market Events and Impact Magnitudes',
                fontweight='bold', pad=20)

    # Rotate date labels
    plt.xticks(rotation=45, ha='right')

    # Legend with significance explanation
    legend_elements = [
        mpatches.Patch(facecolor=COLORS['infrastructure'], edgecolor='black',
                      label='Infrastructure Events'),
        mpatches.Patch(facecolor=COLORS['regulatory'], edgecolor='black',
                      label='Regulatory Events'),
        mpatches.Patch(facecolor='white', edgecolor='white',
                      label='Significance: * p<0.10, ** p<0.05, *** p<0.01'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', frameon=True,
             fancybox=False, shadow=False, framealpha=1)

    plt.tight_layout()
    save_figure(fig, 'figure1_event_timeline')
    plt.close()

    return fig

# ============================================================================
# FIGURE 2: VOLATILITY RESPONSE COMPARISON
# ============================================================================

def create_volatility_comparison(volatility_df):
    """
    Compares volatility dynamics before/during/after events

    Parameters:
    -----------
    volatility_df : pd.DataFrame
        Columns: ['period', 'event_type', 'mean_volatility', 'ci_lower', 'ci_upper']
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), sharey=True)

    periods = ['Pre-Event\n(-10 to -1)', 'Event\n(0 to +5)', 'Post-Event\n(+6 to +20)']
    x_pos = np.arange(len(periods))
    width = 0.35

    # Infrastructure events (left panel)
    infra_data = volatility_df[volatility_df['event_type'] == 'infrastructure']
    if len(infra_data) > 0:
        bars1 = ax1.bar(x_pos, infra_data['mean_volatility'], width,
                       color=COLORS['infrastructure'], edgecolor='black',
                       linewidth=1.5, label='Infrastructure', hatch=PATTERNS['infrastructure'])

        # Add confidence intervals
        ax1.errorbar(x_pos, infra_data['mean_volatility'],
                    yerr=[infra_data['mean_volatility'] - infra_data['ci_lower'],
                          infra_data['ci_upper'] - infra_data['mean_volatility']],
                    fmt='none', ecolor='black', capsize=5, capthick=1.5,
                    linewidth=1.5, zorder=10)

    ax1.set_xlabel('Event Period', fontweight='bold')
    ax1.set_ylabel('Realized Volatility (% per day)', fontweight='bold')
    ax1.set_title('Infrastructure Events', fontweight='bold', pad=15)
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(periods)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')

    # Regulatory events (right panel)
    reg_data = volatility_df[volatility_df['event_type'] == 'regulatory']
    if len(reg_data) > 0:
        bars2 = ax2.bar(x_pos, reg_data['mean_volatility'], width,
                       color=COLORS['regulatory'], edgecolor='black',
                       linewidth=1.5, label='Regulatory', hatch=PATTERNS['regulatory'])

        # Add confidence intervals
        ax2.errorbar(x_pos, reg_data['mean_volatility'],
                    yerr=[reg_data['mean_volatility'] - reg_data['ci_lower'],
                          reg_data['ci_upper'] - reg_data['mean_volatility']],
                    fmt='none', ecolor='black', capsize=5, capthick=1.5,
                    linewidth=1.5, zorder=10)

    ax2.set_xlabel('Event Period', fontweight='bold')
    ax2.set_title('Regulatory Events', fontweight='bold', pad=15)
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(periods)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')

    # Add overall title
    fig.suptitle('Volatility Dynamics Around Infrastructure and Regulatory Events',
                fontweight='bold', fontsize=13, y=1.02)

    plt.tight_layout()
    save_figure(fig, 'figure2_volatility_comparison')
    plt.close()

    return fig

# ============================================================================
# FIGURE 3: CROSS-SECTIONAL HEATMAP
# ============================================================================

def create_impact_heatmap(impact_matrix):
    """
    Creates event × cryptocurrency impact matrix heatmap

    Parameters:
    -----------
    impact_matrix : pd.DataFrame
        Index: Event names, Columns: Cryptocurrency tickers
        Values: CAR (Cumulative Abnormal Returns)
    """
    fig, ax = plt.subplots(figsize=(12, 10))

    # Create heatmap with grayscale colormap
    cmap = plt.cm.RdGy_r  # Reversed Red-Gray colormap (works in grayscale)

    # Plot heatmap
    im = ax.imshow(impact_matrix.values, cmap=cmap, aspect='auto',
                   vmin=-impact_matrix.abs().max().max(),
                   vmax=impact_matrix.abs().max().max())

    # Set ticks and labels
    ax.set_xticks(np.arange(len(impact_matrix.columns)))
    ax.set_yticks(np.arange(len(impact_matrix.index)))
    ax.set_xticklabels(impact_matrix.columns, rotation=45, ha='right')
    ax.set_yticklabels(impact_matrix.index)

    # Add values to cells
    for i in range(len(impact_matrix.index)):
        for j in range(len(impact_matrix.columns)):
            value = impact_matrix.iloc[i, j]
            text_color = 'white' if abs(value) > impact_matrix.abs().max().max() * 0.5 else 'black'
            ax.text(j, i, f'{value:.2f}', ha='center', va='center',
                   color=text_color, fontsize=8)

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Cumulative Abnormal Return (%)', rotation=270,
                   labelpad=20, fontweight='bold')

    # Labels and title
    ax.set_xlabel('Cryptocurrency', fontweight='bold', labelpad=10)
    ax.set_ylabel('Event', fontweight='bold', labelpad=10)
    ax.set_title('Cross-Sectional Event Impact Matrix\n(Cumulative Abnormal Returns by Event and Cryptocurrency)',
                fontweight='bold', pad=20)

    # Grid
    ax.set_xticks(np.arange(len(impact_matrix.columns)) + 0.5, minor=True)
    ax.set_yticks(np.arange(len(impact_matrix.index)) + 0.5, minor=True)
    ax.grid(which='minor', color='black', linestyle='-', linewidth=0.5)
    ax.tick_params(which='minor', size=0)

    plt.tight_layout()
    save_figure(fig, 'figure3_impact_heatmap')
    plt.close()

    return fig

# ============================================================================
# FIGURE 4: MODEL PERFORMANCE COMPARISON
# ============================================================================

def create_model_comparison(model_results):
    """
    Compares out-of-sample forecast accuracy and information criteria

    Parameters:
    -----------
    model_results : pd.DataFrame
        Columns: ['model_name', 'rmse', 'mae', 'aic', 'bic']
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))

    models = model_results['model_name']
    x_pos = np.arange(len(models))

    # Panel A: RMSE (Root Mean Squared Error)
    bars1 = ax1.bar(x_pos, model_results['rmse'], color=COLORS['primary'],
                   edgecolor='black', linewidth=1.5, hatch=PATTERNS['infrastructure'])
    ax1.set_ylabel('RMSE (%)', fontweight='bold')
    ax1.set_title('(a) Out-of-Sample Root Mean Squared Error',
                 fontweight='bold', loc='left')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(models, rotation=45, ha='right')
    ax1.grid(axis='y', alpha=0.3, linestyle='--')

    # Highlight best model
    best_rmse_idx = model_results['rmse'].idxmin()
    bars1[best_rmse_idx].set_facecolor(COLORS['light'])
    bars1[best_rmse_idx].set_hatch(PATTERNS['significant'])

    # Panel B: MAE (Mean Absolute Error)
    bars2 = ax2.bar(x_pos, model_results['mae'], color=COLORS['primary'],
                   edgecolor='black', linewidth=1.5, hatch=PATTERNS['infrastructure'])
    ax2.set_ylabel('MAE (%)', fontweight='bold')
    ax2.set_title('(b) Out-of-Sample Mean Absolute Error',
                 fontweight='bold', loc='left')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(models, rotation=45, ha='right')
    ax2.grid(axis='y', alpha=0.3, linestyle='--')

    # Highlight best model
    best_mae_idx = model_results['mae'].idxmin()
    bars2[best_mae_idx].set_facecolor(COLORS['light'])
    bars2[best_mae_idx].set_hatch(PATTERNS['significant'])

    # Panel C: AIC (Akaike Information Criterion)
    bars3 = ax3.bar(x_pos, model_results['aic'], color=COLORS['secondary'],
                   edgecolor='black', linewidth=1.5, hatch=PATTERNS['regulatory'])
    ax3.set_ylabel('AIC', fontweight='bold')
    ax3.set_xlabel('Model', fontweight='bold')
    ax3.set_title('(c) Akaike Information Criterion',
                 fontweight='bold', loc='left')
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(models, rotation=45, ha='right')
    ax3.grid(axis='y', alpha=0.3, linestyle='--')

    # Highlight best model (lower is better)
    best_aic_idx = model_results['aic'].idxmin()
    bars3[best_aic_idx].set_facecolor(COLORS['light'])
    bars3[best_aic_idx].set_hatch(PATTERNS['significant'])

    # Panel D: BIC (Bayesian Information Criterion)
    bars4 = ax4.bar(x_pos, model_results['bic'], color=COLORS['secondary'],
                   edgecolor='black', linewidth=1.5, hatch=PATTERNS['regulatory'])
    ax4.set_ylabel('BIC', fontweight='bold')
    ax4.set_xlabel('Model', fontweight='bold')
    ax4.set_title('(d) Bayesian Information Criterion',
                 fontweight='bold', loc='left')
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels(models, rotation=45, ha='right')
    ax4.grid(axis='y', alpha=0.3, linestyle='--')

    # Highlight best model (lower is better)
    best_bic_idx = model_results['bic'].idxmin()
    bars4[best_bic_idx].set_facecolor(COLORS['light'])
    bars4[best_bic_idx].set_hatch(PATTERNS['significant'])

    # Add overall title
    fig.suptitle('Model Performance Comparison: Forecast Accuracy and Information Criteria',
                fontweight='bold', fontsize=13, y=0.995)

    # Add legend for best model highlighting
    legend_elements = [
        mpatches.Patch(facecolor=COLORS['light'], edgecolor='black',
                      hatch=PATTERNS['significant'], label='Best Performance'),
    ]
    fig.legend(handles=legend_elements, loc='upper right',
              bbox_to_anchor=(0.98, 0.96), frameon=True)

    plt.tight_layout(rect=[0, 0, 1, 0.98])
    save_figure(fig, 'figure4_model_comparison')
    plt.close()

    return fig

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

def load_or_generate_example_data():
    """
    Attempts to load actual data, or generates example data for demonstration
    """
    data_path = Path('/home/kawaiikali/event-study/data')

    # Try to load actual data files
    try:
        events_df = pd.read_csv(data_path / 'events.csv')
        volatility_df = pd.read_csv(data_path / 'volatility_results.csv')
        impact_matrix = pd.read_csv(data_path / 'impact_matrix.csv', index_col=0)
        model_results = pd.read_csv(data_path / 'model_results.csv')

        print("✓ Loaded actual data files")
        return events_df, volatility_df, impact_matrix, model_results

    except FileNotFoundError:
        print("⚠ Data files not found. Generating example data for demonstration...")
        return generate_example_data()

def generate_example_data():
    """
    Generates realistic example data that matches the expected format
    """
    np.random.seed(42)

    # Example events data
    event_dates = pd.date_range('2022-01-01', '2024-12-31', periods=18)
    event_types = ['infrastructure'] * 9 + ['regulatory'] * 9
    event_names = [
        'Lightning Network Upgrade', 'Ethereum Merge', 'Bitcoin Taproot',
        'Solana Outage', 'FTX Collapse', 'Polygon zkEVM Launch',
        'Circle USDC Depeg', 'Binance Security Breach', 'Coinbase Delisting',
        'SEC vs Ripple Ruling', 'EU MiCA Regulation', 'China Mining Ban',
        'US Infrastructure Bill', 'SEC Bitcoin ETF Denial', 'CFTC DeFi Guidance',
        'Singapore Token Standards', 'UK Crypto Asset Regime', 'Japan FSA Framework'
    ]

    events_df = pd.DataFrame({
        'date': event_dates,
        'event_name': event_names,
        'event_type': event_types,
        'impact_magnitude': np.random.uniform(-0.15, 0.15, 18),
        'p_value': np.random.choice([0.001, 0.02, 0.08, 0.15], 18)
    })

    # Example volatility data
    volatility_df = pd.DataFrame({
        'period': ['Pre-Event\n(-10 to -1)', 'Event\n(0 to +5)', 'Post-Event\n(+6 to +20)'] * 2,
        'event_type': ['infrastructure'] * 3 + ['regulatory'] * 3,
        'mean_volatility': [2.5, 4.2, 3.1, 2.8, 5.5, 3.8],
        'ci_lower': [2.2, 3.8, 2.7, 2.5, 5.0, 3.4],
        'ci_upper': [2.8, 4.6, 3.5, 3.1, 6.0, 4.2]
    })

    # Example impact matrix
    cryptocurrencies = ['BTC', 'ETH', 'BNB', 'SOL', 'ADA', 'XRP', 'DOT', 'MATIC']
    impact_matrix = pd.DataFrame(
        np.random.uniform(-0.20, 0.20, (18, len(cryptocurrencies))),
        index=event_names,
        columns=cryptocurrencies
    )

    # Example model results
    model_results = pd.DataFrame({
        'model_name': ['Market Model', 'GARCH(1,1)', 'EGARCH', 'GJR-GARCH', 'Factor Model'],
        'rmse': [3.45, 2.87, 2.92, 2.85, 3.12],
        'mae': [2.76, 2.31, 2.35, 2.28, 2.54],
        'aic': [4521.3, 4398.7, 4405.2, 4392.1, 4467.8],
        'bic': [4536.8, 4429.5, 4436.0, 4422.9, 4498.6]
    })

    print("✓ Generated example data")
    return events_df, volatility_df, impact_matrix, model_results

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Main function to generate all publication figures
    """
    print("=" * 80)
    print("CRYPTOCURRENCY EVENT STUDY - PUBLICATION FIGURE GENERATOR")
    print("=" * 80)
    print()

    # Load or generate data
    events_df, volatility_df, impact_matrix, model_results = load_or_generate_example_data()

    print()
    print("Generating publication-quality figures...")
    print("-" * 80)

    # Generate Figure 1: Event Timeline
    print("\n[1/4] Creating Event Timeline Visualization...")
    create_event_timeline(events_df)
    print("✓ Figure 1 complete")

    # Generate Figure 2: Volatility Comparison
    print("\n[2/4] Creating Volatility Response Comparison...")
    create_volatility_comparison(volatility_df)
    print("✓ Figure 2 complete")

    # Generate Figure 3: Impact Heatmap
    print("\n[3/4] Creating Cross-Sectional Impact Heatmap...")
    create_impact_heatmap(impact_matrix)
    print("✓ Figure 3 complete")

    # Generate Figure 4: Model Comparison
    print("\n[4/4] Creating Model Performance Comparison...")
    create_model_comparison(model_results)
    print("✓ Figure 4 complete")

    print()
    print("=" * 80)
    print("ALL FIGURES GENERATED SUCCESSFULLY")
    print("=" * 80)
    print()
    print("Output directory: /home/kawaiikali/event-study/publication_figures/")
    print()
    print("Formats generated: PDF (vector), SVG (vector)")
    print("Features:")
    print("  • Grayscale-friendly (patterns + shapes, not just colors)")
    print("  • LaTeX-compatible fonts (Times/serif)")
    print("  • Statistical significance markers (* p<0.10, ** p<0.05, *** p<0.01)")
    print("  • Confidence intervals on volatility charts")
    print("  • Publication-ready 300 DPI resolution")
    print()

if __name__ == '__main__':
    main()
