"""
FTX Event Study - Anomaly Detection System
Identifies abnormal price movements and volatility spikes around FTX bankruptcy
Using Isolation Forest, Statistical Methods, and DBSCAN clustering
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from scipy import stats
import json

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)

# Paths
DATA_DIR = "/home/kawaiikali/event-study/event_study/data"
OUTPUT_DIR = "/home/kawaiikali/event-study/event_study/outputs"

# FTX bankruptcy event
FTX_EVENT_DATE = pd.Timestamp("2022-11-11", tz='UTC')

def load_crypto_data(symbol):
    """Load crypto price data"""
    df = pd.read_csv(f"{DATA_DIR}/{symbol}.csv")
    df['snapped_at'] = pd.to_datetime(df['snapped_at'])
    df = df.set_index('snapped_at').sort_index()

    # Calculate features for anomaly detection
    df['returns'] = df['price'].pct_change()
    df['log_returns'] = np.log(df['price'] / df['price'].shift(1))
    df['volatility_7d'] = df['returns'].rolling(window=7).std() * np.sqrt(365)
    df['volatility_30d'] = df['returns'].rolling(window=30).std() * np.sqrt(365)
    df['volume_change'] = df['total_volume'].pct_change()

    # Price momentum indicators
    df['price_change_1d'] = df['price'].pct_change(1)
    df['price_change_7d'] = df['price'].pct_change(7)
    df['price_change_30d'] = df['price'].pct_change(30)

    # Z-scores for statistical anomalies (handle NaN properly)
    df['returns_zscore'] = stats.zscore(df['returns'], nan_policy='omit')
    df['volume_zscore'] = stats.zscore(df['total_volume'], nan_policy='omit')

    return df

def statistical_anomaly_detection(df, threshold=3.0):
    """
    Detect anomalies using statistical methods (Z-score)
    threshold: number of standard deviations
    """
    anomalies = pd.DataFrame(index=df.index)

    # Z-score based anomalies
    anomalies['returns_anomaly'] = np.abs(df['returns_zscore']) > threshold
    anomalies['volume_anomaly'] = np.abs(df['volume_zscore']) > threshold

    # Extreme price movements
    anomalies['extreme_drop'] = df['returns'] < -0.10  # >10% daily drop
    anomalies['extreme_spike'] = df['returns'] > 0.10   # >10% daily spike

    # Combined anomaly flag
    anomalies['is_anomaly'] = (
        anomalies['returns_anomaly'] |
        anomalies['volume_anomaly'] |
        anomalies['extreme_drop'] |
        anomalies['extreme_spike']
    )

    # Anomaly score (0-1)
    anomalies['anomaly_score'] = (
        anomalies['returns_anomaly'].astype(int) * 0.3 +
        anomalies['volume_anomaly'].astype(int) * 0.2 +
        anomalies['extreme_drop'].astype(int) * 0.25 +
        anomalies['extreme_spike'].astype(int) * 0.25
    )

    return anomalies

def isolation_forest_detection(df, contamination=0.05):
    """
    Use Isolation Forest for multivariate anomaly detection
    contamination: expected proportion of anomalies
    """
    # Select features
    features = ['returns', 'volatility_7d', 'volatility_30d',
                'price_change_7d', 'volume_change']

    # Prepare data - clean infinities and NaN
    X = df[features].copy()
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.dropna()

    if len(X) == 0:
        print("  Warning: No valid data after cleaning")
        return pd.DataFrame(index=df.index), None

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Fit Isolation Forest
    iso_forest = IsolationForest(
        contamination=contamination,
        random_state=42,
        n_estimators=100
    )

    predictions = iso_forest.fit_predict(X_scaled)
    scores = iso_forest.score_samples(X_scaled)

    # Create results dataframe
    results = pd.DataFrame(index=X.index)
    results['is_anomaly'] = predictions == -1
    results['anomaly_score'] = -scores  # Negative for anomaly scores (higher = more anomalous)

    # Align with original dataframe
    anomalies = pd.DataFrame(index=df.index)
    anomalies['isolation_forest_anomaly'] = False
    anomalies.loc[results.index, 'isolation_forest_anomaly'] = results['is_anomaly']
    anomalies['isolation_forest_score'] = 0.0
    anomalies.loc[results.index, 'isolation_forest_score'] = results['anomaly_score']

    return anomalies, iso_forest

def detect_regime_changes(df, window=30):
    """Detect volatility regime changes"""
    df['vol_regime'] = pd.cut(
        df['volatility_30d'],
        bins=[0, 0.3, 0.6, 1.0, np.inf],
        labels=['Low', 'Medium', 'High', 'Extreme']
    )

    # Regime change detection
    df['regime_change'] = df['vol_regime'] != df['vol_regime'].shift(1)

    return df

def analyze_ftx_event_window(df, anomalies, symbol, days_before=90, days_after=90):
    """Analyze anomalies specifically around FTX event"""

    start_date = FTX_EVENT_DATE - timedelta(days=days_before)
    end_date = FTX_EVENT_DATE + timedelta(days=days_after)

    event_window = df[start_date:end_date].copy()
    event_anomalies = anomalies[start_date:end_date].copy()

    # Merge data
    event_data = pd.concat([event_window, event_anomalies], axis=1)
    event_data['days_from_event'] = (event_data.index - FTX_EVENT_DATE).days

    # Count anomalies by period
    pre_event = event_data[event_data['days_from_event'] < -30]
    event_period = event_data[(event_data['days_from_event'] >= -30) &
                              (event_data['days_from_event'] <= 30)]
    post_event = event_data[event_data['days_from_event'] > 30]

    stats = {
        'symbol': symbol.upper(),
        'pre_event_anomalies': int(pre_event['is_anomaly'].sum()),
        'event_period_anomalies': int(event_period['is_anomaly'].sum()),
        'post_event_anomalies': int(post_event['is_anomaly'].sum()),
        'pre_event_days': len(pre_event),
        'event_period_days': len(event_period),
        'post_event_days': len(post_event),
        'max_drop_date': str(event_data['returns'].idxmin()),
        'max_drop_pct': float(event_data['returns'].min() * 100),
        'peak_volatility': float(event_data['volatility_7d'].max()),
        'peak_volatility_date': str(event_data['volatility_7d'].idxmax())
    }

    stats['pre_event_rate'] = stats['pre_event_anomalies'] / stats['pre_event_days']
    stats['event_period_rate'] = stats['event_period_anomalies'] / stats['event_period_days']
    stats['post_event_rate'] = stats['post_event_anomalies'] / stats['post_event_days']

    return event_data, stats

def plot_anomaly_timeline(symbol, df, anomalies, event_data):
    """Visualize anomalies over time"""

    fig, axes = plt.subplots(3, 1, figsize=(18, 14))

    # Plot 1: Price with anomalies
    ax1 = axes[0]
    ax1.plot(event_data.index, event_data['price'],
             label='Price', color='black', linewidth=1.5, alpha=0.7)

    # Mark anomalies
    anomaly_points = event_data[event_data['is_anomaly']]
    ax1.scatter(anomaly_points.index, anomaly_points['price'],
                color='red', s=100, alpha=0.6, label='Anomalies', zorder=5)

    # FTX event marker
    ax1.axvline(FTX_EVENT_DATE, color='darkred', linestyle='--',
                linewidth=2, label='FTX Bankruptcy', alpha=0.8)

    ax1.set_title(f'{symbol.upper()} - Price with Detected Anomalies',
                  fontsize=14, fontweight='bold')
    ax1.set_ylabel('Price (USD)', fontsize=12)
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)

    # Plot 2: Returns with anomaly scores
    ax2 = axes[1]
    ax2.bar(event_data.index, event_data['returns'] * 100,
            color='steelblue', alpha=0.6, label='Daily Returns')

    # Highlight anomalous returns
    anomaly_returns = event_data[event_data['is_anomaly']]['returns'] * 100
    ax2.bar(anomaly_returns.index, anomaly_returns,
            color='red', alpha=0.8, label='Anomalous Returns')

    ax2.axvline(FTX_EVENT_DATE, color='darkred', linestyle='--',
                linewidth=2, alpha=0.8)
    ax2.axhline(0, color='black', linestyle='-', linewidth=0.5)

    ax2.set_title(f'{symbol.upper()} - Daily Returns (Anomalies Highlighted)',
                  fontsize=14, fontweight='bold')
    ax2.set_ylabel('Returns (%)', fontsize=12)
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3)

    # Plot 3: Volatility regimes
    ax3 = axes[2]
    ax3.plot(event_data.index, event_data['volatility_7d'] * 100,
             label='7-day Volatility', color='darkblue', linewidth=2)
    ax3.plot(event_data.index, event_data['volatility_30d'] * 100,
             label='30-day Volatility', color='orange', linewidth=2, alpha=0.7)

    ax3.axvline(FTX_EVENT_DATE, color='darkred', linestyle='--',
                linewidth=2, label='FTX Bankruptcy', alpha=0.8)

    # Shade high volatility periods
    high_vol_threshold = event_data['volatility_7d'].quantile(0.75)
    high_vol_periods = event_data[event_data['volatility_7d'] > high_vol_threshold]

    ax3.fill_between(event_data.index, 0,
                     event_data['volatility_7d'] * 100,
                     where=event_data['volatility_7d'] > high_vol_threshold,
                     color='red', alpha=0.2, label='High Volatility')

    ax3.set_title(f'{symbol.upper()} - Volatility Dynamics',
                  fontsize=14, fontweight='bold')
    ax3.set_xlabel('Date', fontsize=12)
    ax3.set_ylabel('Annualized Volatility (%)', fontsize=12)
    ax3.legend(loc='best')
    ax3.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/{symbol}_anomaly_detection.png',
                dpi=300, bbox_inches='tight')
    print(f"✓ Saved anomaly visualization: {symbol}_anomaly_detection.png")

    return fig

def main():
    """Main anomaly detection pipeline"""

    print("\n" + "="*80)
    print("FTX EVENT STUDY - ANOMALY DETECTION ANALYSIS")
    print("="*80)

    symbols = ['btc', 'eth', 'bnb', 'ada', 'xrp', 'ltc']
    all_results = {}
    summary_stats = []

    for symbol in symbols:
        print(f"\n{'#'*80}")
        print(f"# ANALYZING {symbol.upper()}")
        print(f"{'#'*80}\n")

        # Load data
        df = load_crypto_data(symbol)
        print(f"Loaded {len(df)} observations from {df.index.min().date()} to {df.index.max().date()}")

        # Statistical anomaly detection
        print("\n[1/3] Running statistical anomaly detection...")
        stat_anomalies = statistical_anomaly_detection(df, threshold=3.0)
        print(f"  Found {stat_anomalies['is_anomaly'].sum()} statistical anomalies")

        # Isolation Forest
        print("[2/3] Running Isolation Forest detection...")
        iso_anomalies, iso_model = isolation_forest_detection(df, contamination=0.05)
        print(f"  Found {iso_anomalies['isolation_forest_anomaly'].sum()} Isolation Forest anomalies")

        # Regime detection
        print("[3/3] Detecting volatility regime changes...")
        df = detect_regime_changes(df)

        # Combine anomaly detections
        combined_anomalies = stat_anomalies.copy()
        combined_anomalies['isolation_forest_anomaly'] = iso_anomalies['isolation_forest_anomaly']
        combined_anomalies['isolation_forest_score'] = iso_anomalies['isolation_forest_score']

        # Final combined anomaly flag
        combined_anomalies['is_anomaly'] = (
            stat_anomalies['is_anomaly'] |
            iso_anomalies['isolation_forest_anomaly']
        )

        # Analyze FTX event window
        print("\nAnalyzing FTX event window...")
        event_data, stats = analyze_ftx_event_window(df, combined_anomalies, symbol)

        print(f"\n  FTX Event Window Analysis:")
        print(f"  Pre-Event (-90 to -30):  {stats['pre_event_anomalies']} anomalies ({stats['pre_event_rate']:.2%} rate)")
        print(f"  Event Period (-30 to +30): {stats['event_period_anomalies']} anomalies ({stats['event_period_rate']:.2%} rate)")
        print(f"  Post-Event (+30 to +90): {stats['post_event_anomalies']} anomalies ({stats['post_event_rate']:.2%} rate)")
        print(f"  Maximum Drop: {stats['max_drop_pct']:.2f}% on {stats['max_drop_date']}")
        print(f"  Peak Volatility: {stats['peak_volatility']*100:.1f}% on {stats['peak_volatility_date']}")

        # Visualize
        plot_anomaly_timeline(symbol, df, combined_anomalies, event_data)

        # Store results
        all_results[symbol] = {
            'data': df,
            'anomalies': combined_anomalies,
            'event_data': event_data,
            'stats': stats
        }
        summary_stats.append(stats)

    # Save summary
    summary_df = pd.DataFrame(summary_stats)
    print("\n\n" + "="*80)
    print("ANOMALY DETECTION SUMMARY")
    print("="*80)
    print("\n" + summary_df.to_string(index=False))

    summary_df.to_csv(f'{OUTPUT_DIR}/anomaly_detection_summary.csv', index=False)
    print(f"\n✓ Saved summary to anomaly_detection_summary.csv")

    # Save detailed results
    for symbol, results in all_results.items():
        # Save anomaly timestamps
        anomaly_dates = results['event_data'][results['event_data']['is_anomaly']]
        anomaly_report = anomaly_dates[['price', 'returns', 'volatility_7d',
                                         'days_from_event', 'anomaly_score']]
        anomaly_report.to_csv(f'{OUTPUT_DIR}/{symbol}_anomalies.csv')
        print(f"✓ Saved {symbol.upper()} anomaly details")

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE!")
    print("="*80)
    print(f"\nOutputs saved to: {OUTPUT_DIR}/")
    print(f"  - Anomaly visualizations (*_anomaly_detection.png)")
    print(f"  - Summary statistics (anomaly_detection_summary.csv)")
    print(f"  - Individual anomaly details (*_anomalies.csv)")

if __name__ == "__main__":
    main()
