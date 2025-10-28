"""
Temporal Stability Visualization
Creates publication-quality figure showing ranking stability across periods
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set publication style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_context("paper", font_scale=1.3)
sns.set_palette("husl")

# Load data from analysis
baseline_effects = pd.Series({
    'bnb': 0.946983,
    'xrp': 0.789792,
    'btc': 0.475259,
    'ada': 0.220385,
    'eth': 0.092022,
    'ltc': -0.027433
}).sort_values(ascending=False)

early_effects = pd.Series({
    'bnb': 1.020181,
    'xrp': 0.846081,
    'btc': 0.529568,
    'ada': 0.276783,
    'eth': 0.115425,
    'ltc': -0.009405
}).sort_values(ascending=False)

late_effects = pd.Series({
    'bnb': 0.899068,
    'xrp': 0.744533,
    'btc': 0.441362,
    'ada': 0.227134,
    'eth': 0.095585,
    'ltc': -0.012259
}).sort_values(ascending=False)

# Create figure with subplots
fig, axes = plt.subplots(1, 3, figsize=(16, 6))
fig.suptitle('Temporal Subsample Stability Analysis\nCross-Sectional Heterogeneity Across Market Regimes',
             fontsize=14, fontweight='bold', y=1.02)

# Colors for each crypto (consistent across plots)
crypto_colors = {
    'bnb': '#E74C3C',    # Red (highest sensitivity)
    'xrp': '#F39C12',    # Orange
    'btc': '#F1C40F',    # Yellow
    'ada': '#2ECC71',    # Green
    'eth': '#3498DB',    # Blue
    'ltc': '#9B59B6'     # Purple (lowest sensitivity)
}

# ============================================================================
# PANEL A: Coefficient Comparison by Period
# ============================================================================

ax1 = axes[0]

# Prepare data
x = np.arange(len(baseline_effects))
width = 0.25

# Plot bars
bars1 = ax1.bar(x - width, early_effects.values, width, label='Early (2019-2021)',
                color='#3498DB', alpha=0.8, edgecolor='black', linewidth=0.5)
bars2 = ax1.bar(x, baseline_effects.values, width, label='Full Sample',
                color='#95A5A6', alpha=0.8, edgecolor='black', linewidth=0.5)
bars3 = ax1.bar(x + width, late_effects.values, width, label='Late (2022-2025)',
                color='#E74C3C', alpha=0.8, edgecolor='black', linewidth=0.5)

# Formatting
ax1.set_xlabel('Cryptocurrency', fontsize=11, fontweight='bold')
ax1.set_ylabel('Event Impact Coefficient', fontsize=11, fontweight='bold')
ax1.set_title('A. Coefficient Magnitude by Period', fontsize=12, fontweight='bold', pad=10)
ax1.set_xticks(x)
ax1.set_xticklabels([c.upper() for c in baseline_effects.index], fontsize=10)
ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.8, alpha=0.3)
ax1.legend(fontsize=9, framealpha=0.9, loc='upper right')
ax1.grid(True, alpha=0.3, linestyle='--', axis='y')

# Add value labels on bars (for late period only, to reduce clutter)
for i, (bar, val) in enumerate(zip(bars3, late_effects.values)):
    if val > 0:
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{val:.2f}', ha='center', va='bottom', fontsize=8)

# ============================================================================
# PANEL B: Ranking Stability Visualization
# ============================================================================

ax2 = axes[1]

# Create ranking lines
early_ranks = early_effects.rank(ascending=False)
late_ranks = late_effects.rank(ascending=False)

for crypto in baseline_effects.index:
    color = crypto_colors[crypto]
    ax2.plot([1, 2], [early_ranks[crypto], late_ranks[crypto]],
            marker='o', markersize=12, linewidth=3, color=color,
            label=crypto.upper(), alpha=0.8)

# Formatting
ax2.set_xlim(0.8, 2.2)
ax2.set_ylim(0.5, 6.5)
ax2.set_xticks([1, 2])
ax2.set_xticklabels(['Early Period\n(2019-2021)', 'Late Period\n(2022-2025)'], fontsize=10)
ax2.set_ylabel('Rank (1 = Highest Sensitivity)', fontsize=11, fontweight='bold')
ax2.set_title('B. Ranking Stability (ρ = 1.00)', fontsize=12, fontweight='bold', pad=10)
ax2.invert_yaxis()  # Rank 1 at top
ax2.set_yticks([1, 2, 3, 4, 5, 6])
ax2.legend(fontsize=9, framealpha=0.9, loc='upper left', ncol=2)
ax2.grid(True, alpha=0.3, linestyle='--', axis='y')

# Add annotation
ax2.text(1.5, 0.7, 'Perfect Stability\n(No rank changes)',
        ha='center', va='top', fontsize=10, style='italic',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.3))

# ============================================================================
# PANEL C: Heterogeneity Metrics
# ============================================================================

ax3 = axes[2]

# Calculate metrics
periods = ['Early\n(2019-2021)', 'Full\nSample', 'Late\n(2022-2025)']
spreads = [
    early_effects.max() - early_effects.min(),
    baseline_effects.max() - baseline_effects.min(),
    late_effects.max() - late_effects.min()
]
cohens_d = [2.51, 2.50, 2.50]  # BNB vs LTC for each period

# Create grouped bars
x_pos = np.arange(len(periods))
width_metric = 0.35

bars_spread = ax3.bar(x_pos - width_metric/2, spreads, width_metric,
                     label='Spread (max-min)', color='#3498DB', alpha=0.8,
                     edgecolor='black', linewidth=0.5)
ax3_twin = ax3.twinx()
bars_cohens = ax3_twin.bar(x_pos + width_metric/2, cohens_d, width_metric,
                          label="Cohen's d (extremes)", color='#E74C3C', alpha=0.8,
                          edgecolor='black', linewidth=0.5)

# Formatting
ax3.set_xlabel('Period', fontsize=11, fontweight='bold')
ax3.set_ylabel('Spread (Coefficient Range)', fontsize=11, fontweight='bold', color='#3498DB')
ax3.set_title('C. Heterogeneity Magnitude Stability', fontsize=12, fontweight='bold', pad=10)
ax3.set_xticks(x_pos)
ax3.set_xticklabels(periods, fontsize=9)
ax3.tick_params(axis='y', labelcolor='#3498DB')
ax3.set_ylim(0, 1.2)
ax3.grid(True, alpha=0.3, linestyle='--', axis='y')

ax3_twin.set_ylabel("Cohen's d Effect Size", fontsize=11, fontweight='bold', color='#E74C3C')
ax3_twin.tick_params(axis='y', labelcolor='#E74C3C')
ax3_twin.set_ylim(0, 3)

# Add value labels
for bars, values in [(bars_spread, spreads), (bars_cohens, cohens_d)]:
    for bar, val in zip(bars, values):
        height = bar.get_height()
        if bars == bars_spread:
            ax3.text(bar.get_x() + bar.get_width()/2, height + 0.02,
                    f'{val:.2f}', ha='center', va='bottom', fontsize=8, color='#3498DB')
        else:
            ax3_twin.text(bar.get_x() + bar.get_width()/2, height + 0.05,
                         f'{val:.2f}', ha='center', va='bottom', fontsize=8, color='#E74C3C')

# Combined legend
lines1, labels1 = ax3.get_legend_handles_labels()
lines2, labels2 = ax3_twin.get_legend_handles_labels()
ax3.legend(lines1 + lines2, labels1 + labels2, fontsize=9, framealpha=0.9, loc='upper left')

# Add interpretation box
ax3.text(1, 0.55, 'Spread: -11.5% change\nEffect size: Stable\n→ Heterogeneity persists',
        ha='center', va='center', fontsize=9, style='italic',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.3),
        transform=ax3.transData)

# ============================================================================
# SAVE FIGURE
# ============================================================================

plt.tight_layout()

# Save to publication figures directory
output_dir = Path('publication_figures')
output_dir.mkdir(exist_ok=True)
output_file = output_dir / 'temporal_stability_analysis.png'

plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
print(f"\nFigure saved: {output_file}")

# Also save to event_study outputs
alt_output_dir = Path('event_study/outputs/publication/figures')
alt_output_dir.mkdir(parents=True, exist_ok=True)
alt_output_file = alt_output_dir / 'temporal_stability_analysis.png'
plt.savefig(alt_output_file, dpi=300, bbox_inches='tight', facecolor='white')
print(f"Figure also saved: {alt_output_file}")

# Don't show in headless mode
# plt.show()

print("\n" + "="*80)
print("Temporal Stability Visualization Complete!")
print("="*80)
print("\nKey insights:")
print("- Panel A: Coefficients slightly compressed in late period (-11.5%)")
print("- Panel B: PERFECT ranking stability (ρ = 1.00, no changes)")
print("- Panel C: Effect sizes stable (Cohen's d: 2.51 vs 2.50)")
print("\nConclusion: Heterogeneity is a STRUCTURAL characteristic")
print("="*80)
