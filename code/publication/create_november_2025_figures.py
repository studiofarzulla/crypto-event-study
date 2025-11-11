"""
Publication-Ready Figures for Cryptocurrency Event Study
=========================================================

Based on November 10, 2025 analysis results with corrected findings:
- Infrastructure > Regulatory (2.32% vs 0.42%, p=0.0057)
- Cross-sectional heterogeneity: ADA (3.37%) to BTC (1.13%)
- Only ETH survives FDR correction (p=0.016)
- TARCH-X wins on AIC 5/6 times (83%)

Author: Farzulla Research
Date: November 10, 2025
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# PUBLICATION SETTINGS
# ============================================================================

plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif'],
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 9,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})

# Professional color scheme
COLORS = {
    'infrastructure': '#d62728',  # Red
    'regulatory': '#2ca02c',      # Green
    'gradient': ['#08519c', '#3182bd', '#6baed6', '#9ecae1', '#c6dbef', '#eff3ff'],
}

# ============================================================================
# SETUP PATHS
# ============================================================================

BASE_DIR = Path(__file__).parent.parent.parent
RESULTS_DIR = BASE_DIR / 'outputs' / 'analysis_results'
OUTPUT_DIR = BASE_DIR / 'outputs' / 'publication' / 'figures'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# LOAD DATA
# ============================================================================

def load_data():
    """Load all analysis results"""
    print("Loading analysis results...")

    # Main results
    crypto_df = pd.read_csv(RESULTS_DIR / 'analysis_by_crypto.csv')
    hypothesis_df = pd.read_csv(RESULTS_DIR / 'hypothesis_test_results.csv', index_col=0)
    fdr_df = pd.read_csv(RESULTS_DIR / 'fdr_corrected_pvalues.csv')

    # Model parameters for AIC/BIC comparison
    model_params = {}
    param_dir = RESULTS_DIR / 'model_parameters'
    for param_file in param_dir.glob('*_parameters.json'):
        crypto = param_file.stem.replace('_parameters', '')
        with open(param_file) as f:
            model_params[crypto] = json.load(f)

    print(f"  Loaded results for {len(crypto_df)} cryptocurrencies")
    print(f"  Loaded model parameters for {len(model_params)} cryptocurrencies")

    return crypto_df, hypothesis_df, fdr_df, model_params

def save_figure(fig, filename):
    """Save figure as both PDF and PNG"""
    pdf_path = OUTPUT_DIR / f"{filename}.pdf"
    png_path = OUTPUT_DIR / f"{filename}.png"

    fig.savefig(pdf_path, format='pdf', bbox_inches='tight', transparent=False)
    fig.savefig(png_path, format='png', bbox_inches='tight', transparent=False)

    print(f"  Saved: {pdf_path}")
    print(f"  Saved: {png_path}")

# ============================================================================
# FIGURE 1: INFRASTRUCTURE VS REGULATORY BOX PLOT
# ============================================================================

def create_figure1_infrastructure_vs_regulatory(crypto_df, hypothesis_df):
    """
    Box plot showing Infrastructure events generate 5.5× larger volatility impacts

    Key findings:
    - Infrastructure: mean 2.32%, median 2.59%, std 0.78
    - Regulatory: mean 0.42%, median 0.24%, std 0.50
    - p=0.0057, Cohen's d=2.88
    """
    print("\n[1/4] Creating Figure 1: Infrastructure vs Regulatory Box Plot...")

    fig, ax = plt.subplots(figsize=(8, 6))

    # Prepare data
    infra_effects = crypto_df['mean_infra_effect'].values
    reg_effects = crypto_df['mean_reg_effect'].values

    # Create box plots
    bp = ax.boxplot([infra_effects, reg_effects],
                     positions=[1, 2],
                     widths=0.5,
                     patch_artist=True,
                     showmeans=True,
                     meanprops=dict(marker='D', markerfacecolor='red',
                                   markeredgecolor='black', markersize=8),
                     boxprops=dict(linewidth=1.5),
                     whiskerprops=dict(linewidth=1.5),
                     capprops=dict(linewidth=1.5),
                     medianprops=dict(color='black', linewidth=2))

    # Color boxes
    bp['boxes'][0].set_facecolor(COLORS['infrastructure'])
    bp['boxes'][0].set_alpha(0.6)
    bp['boxes'][1].set_facecolor(COLORS['regulatory'])
    bp['boxes'][1].set_alpha(0.6)

    # Overlay individual data points with jitter
    np.random.seed(42)
    x1 = np.random.normal(1, 0.04, len(infra_effects))
    x2 = np.random.normal(2, 0.04, len(reg_effects))

    ax.scatter(x1, infra_effects, alpha=0.7, s=100, edgecolors='black',
              linewidths=1.5, c='white', zorder=3)
    ax.scatter(x2, reg_effects, alpha=0.7, s=100, edgecolors='black',
              linewidths=1.5, c='white', zorder=3)

    # Add statistical annotation
    y_max = max(infra_effects.max(), reg_effects.max())
    y_line = y_max + 0.4
    ax.plot([1, 1, 2, 2], [y_line, y_line + 0.15, y_line + 0.15, y_line],
            'k-', linewidth=1.5)
    ax.text(1.5, y_line + 0.25, 'p = 0.0057***\nCohen\'s d = 2.88',
            ha='center', va='bottom', fontsize=10, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))

    # Add mean annotations
    infra_mean = hypothesis_df.loc['Infrastructure', 'mean']
    reg_mean = hypothesis_df.loc['Regulatory', 'mean']
    infra_median = hypothesis_df.loc['Infrastructure', 'median']
    reg_median = hypothesis_df.loc['Regulatory', 'median']

    ax.text(1, -0.6, f'Mean: {infra_mean:.2f}%\nMedian: {infra_median:.2f}%',
            ha='center', fontsize=9, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    ax.text(2, -0.6, f'Mean: {reg_mean:.2f}%\nMedian: {reg_median:.2f}%',
            ha='center', fontsize=9, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    # Labels and formatting
    ax.set_xticks([1, 2])
    ax.set_xticklabels(['Infrastructure Events', 'Regulatory Events'],
                       fontweight='bold', fontsize=11)
    ax.set_ylabel('Volatility Impact Coefficient (%)', fontweight='bold', fontsize=11)
    ax.set_title('Infrastructure Events Generate 5.5× Larger Volatility Impacts',
                 fontweight='bold', pad=15, fontsize=13)

    # Add horizontal line at zero
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=1, alpha=0.5)

    # Grid
    ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)
    ax.set_axisbelow(True)

    # Set y-limits to accommodate annotations
    ax.set_ylim(-1.2, y_max + 1.0)

    plt.tight_layout()
    save_figure(fig, 'figure1_infrastructure_vs_regulatory')
    plt.close()

    print("  Figure 1 complete!")

# ============================================================================
# FIGURE 2: CROSS-SECTIONAL INFRASTRUCTURE SENSITIVITY
# ============================================================================

def create_figure2_infrastructure_sensitivity(crypto_df, fdr_df):
    """
    Bar chart showing cross-sectional heterogeneity in infrastructure sensitivity

    Key findings:
    - ADA: 3.37% (highest)
    - BTC: 1.13% (lowest)
    - 2.24pp spread
    - Only ETH survives FDR correction (p=0.016)
    """
    print("\n[2/4] Creating Figure 2: Cross-Sectional Infrastructure Sensitivity...")

    # Prepare data - focus on infrastructure events only
    infra_data = fdr_df[fdr_df['event_type'] == 'Infrastructure'].copy()
    infra_data = infra_data.sort_values('coefficient', ascending=True)

    fig, ax = plt.subplots(figsize=(10, 6))

    # Create horizontal bar chart
    cryptos = [c.upper() for c in infra_data['crypto'].values]
    coefficients = infra_data['coefficient'].values
    std_errors = infra_data['std_error'].values
    fdr_sig = infra_data['fdr_significant'].values

    # Color bars - highlight FDR-significant ones
    colors = ['#d62728' if sig else '#AAAAAA' for sig in fdr_sig]

    bars = ax.barh(range(len(cryptos)), coefficients, xerr=std_errors,
                   color=colors, edgecolor='black', linewidth=1.2,
                   capsize=5, error_kw={'linewidth': 1.5})

    # Add value labels
    for i, (coef, se, sig) in enumerate(zip(coefficients, std_errors, fdr_sig)):
        label = f'{coef:.2f}%'
        if sig:
            label += '**'  # Mark FDR-significant

        x_pos = coef + se + 0.15
        ax.text(x_pos, i, label, va='center', ha='left',
               fontsize=10, fontweight='bold' if sig else 'normal')

    # Y-axis labels
    ax.set_yticks(range(len(cryptos)))
    ax.set_yticklabels(cryptos, fontweight='bold', fontsize=11)

    # X-axis (with extra headroom for ADA label)
    x_max = max(coefficients + std_errors) * 1.15  # Add 15% headroom
    ax.set_xlim(left=min(coefficients - std_errors) - 0.2, right=x_max)
    ax.set_xlabel('Infrastructure Event Sensitivity (%)', fontweight='bold', fontsize=11)
    ax.set_title('Cross-Sectional Heterogeneity in Infrastructure Event Sensitivity\n' +
                 '2.24 percentage point spread (ADA 3.37% to BTC 1.13%)',
                 fontweight='bold', pad=15, fontsize=12)

    # Add vertical line at zero
    ax.axvline(x=0, color='black', linestyle='-', linewidth=0.8)

    # Grid
    ax.grid(axis='x', alpha=0.3, linestyle='--', linewidth=0.5)
    ax.set_axisbelow(True)

    # Add legend (repositioned to upper left to avoid overlap)
    legend_elements = [
        mpatches.Patch(facecolor='#d62728', edgecolor='black',
                      label='FDR-Significant (q < 0.05)'),
        mpatches.Patch(facecolor='#AAAAAA', edgecolor='black',
                      label='Not FDR-Significant'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', frameon=True)

    # Add annotation for spread (repositioned to bottom left)
    spread = coefficients.max() - coefficients.min()
    ax.text(0.02, 0.02, f'Spread: {spread:.2f}pp\n** ETH only FDR-significant (p=0.016)',
            transform=ax.transAxes, ha='left', va='bottom',
            fontsize=9, style='italic',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

    plt.tight_layout()
    save_figure(fig, 'figure2_infrastructure_sensitivity')
    plt.close()

    print("  Figure 2 complete!")

# ============================================================================
# FIGURE 3: EVENT COEFFICIENTS HEATMAP
# ============================================================================

def create_figure3_event_coefficients_heatmap(fdr_df):
    """
    Heatmap showing event type coefficients by cryptocurrency

    6 cryptos × 2 event types = 12 cells
    Mark ETH infrastructure with ** (FDR-significant)
    """
    print("\n[3/4] Creating Figure 3: Event Coefficients Heatmap...")

    # Pivot data
    pivot_data = fdr_df.pivot_table(
        index='crypto',
        columns='event_type',
        values='coefficient'
    )

    # Reorder rows by infrastructure effect (descending)
    row_order = ['ada', 'ltc', 'eth', 'xrp', 'bnb', 'btc']
    pivot_data = pivot_data.reindex(row_order)

    # Create significance matrix for annotations
    sig_matrix = fdr_df.pivot_table(
        index='crypto',
        columns='event_type',
        values='fdr_significant'
    ).reindex(row_order)

    fig, ax = plt.subplots(figsize=(8, 7))

    # Create heatmap with diverging colormap
    vmax = max(abs(pivot_data.min().min()), abs(pivot_data.max().max()))

    im = ax.imshow(pivot_data.values, cmap='RdBu_r', aspect='auto',
                   vmin=-vmax, vmax=vmax)

    # Set ticks and labels
    ax.set_xticks(np.arange(len(pivot_data.columns)))
    ax.set_yticks(np.arange(len(pivot_data.index)))
    ax.set_xticklabels(pivot_data.columns, fontweight='bold', fontsize=11)
    ax.set_yticklabels([c.upper() for c in pivot_data.index],
                       fontweight='bold', fontsize=11)

    # Add values to cells with significance markers
    for i in range(len(pivot_data.index)):
        for j in range(len(pivot_data.columns)):
            value = pivot_data.iloc[i, j]
            is_sig = sig_matrix.iloc[i, j]

            # Choose text color based on background
            text_color = 'white' if abs(value) > vmax * 0.5 else 'black'

            # Add significance marker
            text = f'{value:.2f}%'
            if is_sig:
                text += '\n**'

            ax.text(j, i, text, ha='center', va='center',
                   color=text_color, fontsize=10, fontweight='bold')

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Event Sensitivity Coefficient (%)',
                   rotation=270, labelpad=25, fontweight='bold', fontsize=10)

    # Labels and title
    ax.set_xlabel('Event Type', fontweight='bold', labelpad=10, fontsize=11)
    ax.set_ylabel('Cryptocurrency', fontweight='bold', labelpad=10, fontsize=11)
    ax.set_title('Event Type Coefficients by Cryptocurrency\n' +
                 '** indicates FDR-corrected significance (q < 0.05)',
                 fontweight='bold', pad=15, fontsize=12)

    # Add grid for cell separation
    ax.set_xticks(np.arange(len(pivot_data.columns)) + 0.5, minor=True)
    ax.set_yticks(np.arange(len(pivot_data.index)) + 0.5, minor=True)
    ax.grid(which='minor', color='black', linestyle='-', linewidth=2)
    ax.tick_params(which='minor', size=0)

    plt.tight_layout()
    save_figure(fig, 'figure3_event_coefficients_heatmap')
    plt.close()

    print("  Figure 3 complete!")

# ============================================================================
# FIGURE 4: TARCH-X MODEL PERFORMANCE
# ============================================================================

def create_figure4_tarchx_performance(model_params):
    """
    Dual-axis plot showing TARCH-X AIC and BIC performance

    Key findings:
    - 5/6 AIC wins (83%)
    - 0/6 BIC wins (0%)
    - Illustrates parsimony-performance trade-off
    """
    print("\n[4/4] Creating Figure 4: TARCH-X Model Performance...")

    # Extract AIC and BIC data
    cryptos = []
    aic_improvements = []
    bic_improvements = []

    for crypto, params in sorted(model_params.items()):
        cryptos.append(crypto.upper())

        tarchx_aic = params['TARCH-X']['AIC']
        garch_aic = params['GARCH(1,1)']['AIC']
        aic_improvements.append(tarchx_aic - garch_aic)  # Negative = better

        tarchx_bic = params['TARCH-X']['BIC']
        garch_bic = params['GARCH(1,1)']['BIC']
        bic_improvements.append(tarchx_bic - garch_bic)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # ---- Panel A: AIC Comparison ----
    aic_colors = ['green' if imp < 0 else 'red' for imp in aic_improvements]
    bars1 = ax1.barh(range(len(cryptos)), aic_improvements,
                     color=aic_colors, alpha=0.7, edgecolor='black', linewidth=1.5)

    # Add value labels
    for i, (bar, imp) in enumerate(zip(bars1, aic_improvements)):
        width = bar.get_width()
        label_x = width - 2 if width < 0 else width + 2
        ax1.text(label_x, i, f'{imp:.1f}',
                ha='right' if width < 0 else 'left', va='center',
                fontsize=10, fontweight='bold')

    ax1.set_yticks(range(len(cryptos)))
    ax1.set_yticklabels(cryptos, fontweight='bold', fontsize=11)
    ax1.set_xlabel('ΔAIC (TARCH-X - GARCH)\nNegative = TARCH-X Superior',
                   fontweight='bold', fontsize=10)
    ax1.set_title('Panel A: AIC Comparison\nTARCH-X Wins 5/6 (83%)',
                  fontweight='bold', pad=10, fontsize=11)
    ax1.axvline(x=0, color='black', linestyle='-', linewidth=2)
    ax1.grid(axis='x', alpha=0.3)

    # ---- Panel B: BIC Comparison ----
    bic_colors = ['green' if imp < 0 else 'red' for imp in bic_improvements]
    bars2 = ax2.barh(range(len(cryptos)), bic_improvements,
                     color=bic_colors, alpha=0.7, edgecolor='black', linewidth=1.5)

    # Add value labels
    for i, (bar, imp) in enumerate(zip(bars2, bic_improvements)):
        width = bar.get_width()
        label_x = width - 2 if width < 0 else width + 2
        ax2.text(label_x, i, f'{imp:.1f}',
                ha='right' if width < 0 else 'left', va='center',
                fontsize=10, fontweight='bold')

    ax2.set_yticks(range(len(cryptos)))
    ax2.set_yticklabels(cryptos, fontweight='bold', fontsize=11)
    ax2.set_xlabel('ΔBIC (TARCH-X - GARCH)\nNegative = TARCH-X Superior',
                   fontweight='bold', fontsize=10)
    ax2.set_title('Panel B: BIC Comparison\nTARCH-X Wins 0/6 (0%)',
                  fontweight='bold', pad=10, fontsize=11)
    ax2.axvline(x=0, color='black', linestyle='-', linewidth=2)
    ax2.grid(axis='x', alpha=0.3)

    # Main title
    fig.suptitle('TARCH-X Model Performance: Parsimony-Performance Trade-off\n' +
                 'AIC favors TARCH-X (information gain), BIC penalizes complexity',
                 fontweight='bold', fontsize=13, y=1.00)

    plt.tight_layout()
    save_figure(fig, 'figure4_tarchx_performance')
    plt.close()

    print("  Figure 4 complete!")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Generate all publication figures"""
    print("=" * 80)
    print("CRYPTOCURRENCY EVENT STUDY - PUBLICATION FIGURES")
    print("November 10, 2025 Analysis Results")
    print("=" * 80)
    print("\nKey Findings:")
    print("  • Infrastructure > Regulatory (2.32% vs 0.42%, p=0.0057)")
    print("  • Cross-sectional spread: 2.24pp (ADA 3.37% to BTC 1.13%)")
    print("  • Only ETH survives FDR correction (p=0.016)")
    print("  • TARCH-X wins on AIC 5/6 times (83%)")
    print("\nGenerating 4 publication figures...")
    print("-" * 80)

    # Load data
    crypto_df, hypothesis_df, fdr_df, model_params = load_data()

    # Generate figures
    create_figure1_infrastructure_vs_regulatory(crypto_df, hypothesis_df)
    create_figure2_infrastructure_sensitivity(crypto_df, fdr_df)
    create_figure3_event_coefficients_heatmap(fdr_df)
    create_figure4_tarchx_performance(model_params)

    print("\n" + "=" * 80)
    print("ALL FIGURES GENERATED SUCCESSFULLY")
    print("=" * 80)
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print("\nFiles generated:")
    print("  • figure1_infrastructure_vs_regulatory.pdf / .png")
    print("  • figure2_infrastructure_sensitivity.pdf / .png")
    print("  • figure3_event_coefficients_heatmap.pdf / .png")
    print("  • figure4_tarchx_performance.pdf / .png")
    print("\nFeatures:")
    print("  ✓ Times New Roman serif fonts")
    print("  ✓ 300 DPI publication quality")
    print("  ✓ Vector PDF + raster PNG formats")
    print("  ✓ Professional color scheme")
    print("  ✓ Statistical annotations (p-values, effect sizes)")
    print("  ✓ FDR correction indicators")
    print("\nReady for academic publication!")
    print()

if __name__ == '__main__':
    main()
