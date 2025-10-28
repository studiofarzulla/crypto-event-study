"""
FTX Event Study - Advanced Time Series Forecasting Analysis
Analyzes crypto price dynamics around the FTX bankruptcy event
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ML/Stats libraries
from statsmodels.tsa.stattools import adfuller, acf, pacf
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import MinMaxScaler

# Prophet for advanced forecasting
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    print("Prophet not available, skipping Prophet forecasts")
    PROPHET_AVAILABLE = False

from code.core import config

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (15, 8)

# Paths
DATA_DIR = config.DATA_DIR
OUTPUT_DIR = config.OUTPUTS_DIR

# FTX bankruptcy event date (timezone-aware to match data)
FTX_EVENT_DATE = pd.Timestamp("2022-11-11", tz='UTC')

def load_crypto_data(symbol):
    """Load and preprocess crypto price data"""
    df = pd.read_csv(f"{DATA_DIR}/{symbol}.csv")
    df['snapped_at'] = pd.to_datetime(df['snapped_at'])
    df = df.set_index('snapped_at')
    df = df.sort_index()

    # Calculate returns
    df['returns'] = df['price'].pct_change()
    df['log_returns'] = np.log(df['price'] / df['price'].shift(1))

    # Volatility (rolling 30-day)
    df['volatility_30d'] = df['returns'].rolling(window=30).std() * np.sqrt(365)

    return df

def test_stationarity(timeseries, title=''):
    """Augmented Dickey-Fuller test for stationarity"""
    result = adfuller(timeseries.dropna(), autolag='AIC')

    print(f'\n=== Stationarity Test: {title} ===')
    print(f'ADF Statistic: {result[0]:.6f}')
    print(f'p-value: {result[1]:.6f}')
    print(f'Critical Values:')
    for key, value in result[4].items():
        print(f'\t{key}: {value:.3f}')

    if result[1] <= 0.05:
        print("✓ Series is stationary (reject H0)")
        return True
    else:
        print("✗ Series is non-stationary (fail to reject H0)")
        return False

def create_event_window(df, event_date, days_before=90, days_after=90):
    """Extract event window around FTX bankruptcy"""
    start_date = event_date - timedelta(days=days_before)
    end_date = event_date + timedelta(days=days_after)

    event_window = df[start_date:end_date].copy()
    event_window['days_from_event'] = (event_window.index - event_date).days

    return event_window

def fit_arima_model(train_data, order=(5,1,0)):
    """Fit ARIMA model"""
    model = ARIMA(train_data, order=order)
    fitted_model = model.fit()
    return fitted_model

def fit_prophet_model(df, symbol):
    """Fit Prophet model for robust forecasting"""
    if not PROPHET_AVAILABLE:
        return None

    # Prepare data for Prophet
    prophet_df = df.reset_index()[['snapped_at', 'price']]
    prophet_df.columns = ['ds', 'y']

    # Fit model
    model = Prophet(
        daily_seasonality=True,
        weekly_seasonality=True,
        yearly_seasonality=True,
        changepoint_prior_scale=0.05
    )
    model.fit(prophet_df)

    return model

def forecast_comparison(df, symbol, event_date, forecast_days=30):
    """Compare multiple forecasting models"""

    # Split data: train up to 90 days before event, forecast the crash period
    train_end = event_date - timedelta(days=90)
    test_start = event_date - timedelta(days=30)
    test_end = event_date + timedelta(days=30)

    train_data = df[df.index < train_end]['price']
    test_data = df[test_start:test_end]['price']

    results = {}

    # ARIMA Model
    print(f"\n{'='*60}")
    print(f"Fitting ARIMA model for {symbol.upper()}...")
    print(f"{'='*60}")

    try:
        arima_model = fit_arima_model(train_data, order=(5,1,2))
        print(arima_model.summary())

        # Forecast
        arima_forecast = arima_model.forecast(steps=len(test_data))
        arima_mse = mean_squared_error(test_data, arima_forecast)
        arima_mae = mean_absolute_error(test_data, arima_forecast)

        results['ARIMA'] = {
            'model': arima_model,
            'forecast': arima_forecast,
            'mse': arima_mse,
            'mae': arima_mae,
            'rmse': np.sqrt(arima_mse)
        }

        print(f"\nARIMA Performance:")
        print(f"  RMSE: ${arima_mse**0.5:,.2f}")
        print(f"  MAE:  ${arima_mae:,.2f}")

    except Exception as e:
        print(f"ARIMA failed: {e}")

    # Prophet Model
    if PROPHET_AVAILABLE:
        print(f"\n{'='*60}")
        print(f"Fitting Prophet model for {symbol.upper()}...")
        print(f"{'='*60}")

        try:
            prophet_model = fit_prophet_model(df[df.index < train_end], symbol)

            # Create future dataframe
            future = pd.DataFrame({'ds': test_data.index})
            prophet_forecast = prophet_model.predict(future)

            prophet_pred = prophet_forecast.set_index('ds')['yhat']
            prophet_mse = mean_squared_error(test_data, prophet_pred)
            prophet_mae = mean_absolute_error(test_data, prophet_pred)

            results['Prophet'] = {
                'model': prophet_model,
                'forecast': prophet_pred,
                'forecast_full': prophet_forecast,
                'mse': prophet_mse,
                'mae': prophet_mae,
                'rmse': np.sqrt(prophet_mse)
            }

            print(f"\nProphet Performance:")
            print(f"  RMSE: ${prophet_mse**0.5:,.2f}")
            print(f"  MAE:  ${prophet_mae:,.2f}")

        except Exception as e:
            print(f"Prophet failed: {e}")

    return results, test_data

def plot_forecast_comparison(symbol, df, results, test_data, event_date):
    """Visualize forecast performance"""

    fig, axes = plt.subplots(2, 1, figsize=(16, 12))

    # Plot 1: Full time series with forecasts
    ax1 = axes[0]

    # Historical data
    train_end = event_date - timedelta(days=90)
    df_plot = df[df.index >= train_end - timedelta(days=180)]
    ax1.plot(df_plot.index, df_plot['price'], label='Actual Price', color='black', linewidth=1.5)

    # Event marker
    ax1.axvline(event_date, color='red', linestyle='--', linewidth=2, label='FTX Bankruptcy', alpha=0.7)

    # Forecasts
    colors = {'ARIMA': 'blue', 'Prophet': 'green'}
    for model_name, result in results.items():
        forecast = result['forecast']
        ax1.plot(test_data.index, forecast,
                label=f'{model_name} Forecast (RMSE: ${result["rmse"]:,.0f})',
                color=colors.get(model_name, 'orange'),
                linewidth=2, alpha=0.7, linestyle='--')

    ax1.set_title(f'{symbol.upper()} - Price Forecasts vs Actual (FTX Event)', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Date', fontsize=12)
    ax1.set_ylabel('Price (USD)', fontsize=12)
    ax1.legend(loc='best', fontsize=10)
    ax1.grid(True, alpha=0.3)

    # Plot 2: Forecast errors
    ax2 = axes[1]

    for model_name, result in results.items():
        forecast = result['forecast']
        errors = test_data - forecast
        ax2.plot(test_data.index, errors,
                label=f'{model_name} Error',
                color=colors.get(model_name, 'orange'),
                linewidth=2, marker='o', markersize=4)

    ax2.axhline(0, color='black', linestyle='-', linewidth=1)
    ax2.axvline(event_date, color='red', linestyle='--', linewidth=2, alpha=0.7)
    ax2.set_title(f'{symbol.upper()} - Forecast Errors', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Date', fontsize=12)
    ax2.set_ylabel('Error (Actual - Predicted)', fontsize=12)
    ax2.legend(loc='best', fontsize=10)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/{symbol}_forecast_comparison.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved forecast comparison plot: {symbol}_forecast_comparison.png")

    return fig

def analyze_volatility_forecast(df, symbol, event_date):
    """Forecast volatility around FTX event"""

    # Calculate rolling volatility
    df['volatility'] = df['returns'].rolling(window=30).std() * np.sqrt(365) * 100

    # Event window
    event_window = create_event_window(df, event_date, days_before=180, days_after=90)

    # Plot volatility dynamics
    fig, ax = plt.subplots(figsize=(16, 8))

    ax.plot(event_window.index, event_window['volatility'],
            label='30-day Realized Volatility', color='darkblue', linewidth=2)

    # Mark event
    ax.axvline(event_date, color='red', linestyle='--', linewidth=2, label='FTX Bankruptcy', alpha=0.7)

    # Pre/post event regions
    ax.axvspan(event_date - timedelta(days=30), event_date, alpha=0.2, color='orange', label='Pre-Event (30d)')
    ax.axvspan(event_date, event_date + timedelta(days=30), alpha=0.2, color='red', label='Post-Event (30d)')

    ax.set_title(f'{symbol.upper()} - Volatility Dynamics Around FTX Bankruptcy', fontsize=14, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Annualized Volatility (%)', fontsize=12)
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/{symbol}_volatility_dynamics.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved volatility plot: {symbol}_volatility_dynamics.png")

    # Calculate volatility statistics
    pre_event_vol = event_window[event_window['days_from_event'] < -30]['volatility'].mean()
    event_vol = event_window[(event_window['days_from_event'] >= -30) &
                             (event_window['days_from_event'] <= 0)]['volatility'].mean()
    post_event_vol = event_window[(event_window['days_from_event'] > 0) &
                                  (event_window['days_from_event'] <= 30)]['volatility'].mean()

    print(f"\n{symbol.upper()} Volatility Analysis:")
    print(f"  Pre-Event (30d before):  {pre_event_vol:.2f}%")
    print(f"  Event Window (-30 to 0): {event_vol:.2f}%")
    print(f"  Post-Event (30d after):  {post_event_vol:.2f}%")
    print(f"  Volatility Spike:        {((event_vol / pre_event_vol - 1) * 100):.1f}%")

    return event_window

def main():
    """Main analysis pipeline"""

    print("\n" + "="*80)
    print("FTX EVENT STUDY - TIME SERIES FORECASTING ANALYSIS")
    print("="*80)

    # Cryptocurrencies to analyze
    symbols = ['btc', 'eth', 'bnb', 'ada', 'xrp', 'ltc']

    all_results = {}

    for symbol in symbols:
        print(f"\n\n{'#'*80}")
        print(f"# ANALYZING {symbol.upper()}")
        print(f"{'#'*80}\n")

        # Load data
        df = load_crypto_data(symbol)
        print(f"Loaded {len(df)} daily observations from {df.index.min().date()} to {df.index.max().date()}")

        # Test stationarity
        test_stationarity(df['price'], f'{symbol.upper()} Price')
        test_stationarity(df['returns'].dropna(), f'{symbol.upper()} Returns')

        # Forecast comparison
        results, test_data = forecast_comparison(df, symbol, FTX_EVENT_DATE, forecast_days=60)

        # Visualize forecasts
        if results:
            plot_forecast_comparison(symbol, df, results, test_data, FTX_EVENT_DATE)

        # Volatility analysis
        vol_window = analyze_volatility_forecast(df, symbol, FTX_EVENT_DATE)

        all_results[symbol] = {
            'data': df,
            'forecasts': results,
            'volatility_window': vol_window
        }

    # Summary report
    print("\n\n" + "="*80)
    print("FORECAST PERFORMANCE SUMMARY")
    print("="*80)

    summary_data = []
    for symbol, data in all_results.items():
        for model_name, result in data['forecasts'].items():
            summary_data.append({
                'Asset': symbol.upper(),
                'Model': model_name,
                'RMSE': result['rmse'],
                'MAE': result['mae'],
                'MSE': result['mse']
            })

    summary_df = pd.DataFrame(summary_data)
    print("\n" + summary_df.to_string(index=False))

    # Save summary
    summary_df.to_csv(f'{OUTPUT_DIR}/forecast_summary.csv', index=False)
    print(f"\n✓ Saved summary to forecast_summary.csv")

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE!")
    print("="*80)
    print(f"\nOutputs saved to: {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
