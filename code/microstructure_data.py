"""
Microstructure Data Collection Module
======================================

Collects bid-ask spreads, order book depth, and volume data for:
- Cryptocurrency markets (Binance API, CoinGecko)
- Traditional markets (Yahoo Finance, WRDS TAQ)

Metrics computed:
1. Bid-ask spread (percentage): (ask - bid) / midpoint × 100
2. Order book depth: sum of bid/ask sizes at top N levels
3. Trading volume: daily volume in USD
4. Price impact: |price change| / volume^0.5 (Kyle's lambda approximation)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import requests
import time
from pathlib import Path

try:
    import ccxt
    CCXT_AVAILABLE = True
except ImportError:
    CCXT_AVAILABLE = False
    print("Warning: ccxt not installed. Crypto orderbook data unavailable.")
    print("Install with: pip install ccxt")

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("Warning: yfinance not installed. Traditional market data unavailable.")
    print("Install with: pip install yfinance")

import config


class MicrostructureDataCollector:
    """Collect microstructure data for crypto and traditional markets."""

    def __init__(self):
        """Initialize data collector."""
        self.crypto_exchange = None
        if CCXT_AVAILABLE:
            try:
                self.crypto_exchange = ccxt.binance({
                    'apiKey': config.BINANCE_API_KEY,
                    'secret': config.BINANCE_API_SECRET,
                    'enableRateLimit': True
                })
            except Exception as e:
                print(f"Warning: Could not initialize Binance: {e}")

    def collect_crypto_spread(self, symbol: str, start_date: str, end_date: str,
                             frequency: str = '1d') -> pd.DataFrame:
        """
        Collect bid-ask spread data for cryptocurrency.

        Args:
            symbol: Crypto symbol (e.g., 'BTC', 'ETH')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            frequency: Data frequency ('1m', '5m', '1h', '1d')

        Returns:
            DataFrame with columns: date, bid, ask, spread_abs, spread_pct
        """
        if not CCXT_AVAILABLE or self.crypto_exchange is None:
            print(f"Using CoinGecko for {symbol} spread estimation (lower quality)")
            return self._coingecko_spread_proxy(symbol, start_date, end_date)

        print(f"Collecting {symbol} orderbook data from Binance...")

        # Convert to Binance symbol format
        trading_pair = f"{symbol}/USDT"

        results = []
        current_date = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)

        while current_date <= end:
            try:
                # Fetch orderbook
                orderbook = self.crypto_exchange.fetch_order_book(trading_pair)

                if len(orderbook['bids']) > 0 and len(orderbook['asks']) > 0:
                    bid = orderbook['bids'][0][0]  # Best bid price
                    ask = orderbook['asks'][0][0]  # Best ask price
                    midpoint = (bid + ask) / 2

                    spread_abs = ask - bid
                    spread_pct = (spread_abs / midpoint) * 100

                    results.append({
                        'date': current_date,
                        'bid': bid,
                        'ask': ask,
                        'midpoint': midpoint,
                        'spread_abs': spread_abs,
                        'spread_pct': spread_pct
                    })

                # Rate limiting
                time.sleep(1)
                current_date += timedelta(days=1)

            except Exception as e:
                print(f"  Error on {current_date}: {e}")
                current_date += timedelta(days=1)
                continue

        df = pd.DataFrame(results)
        df.set_index('date', inplace=True)

        print(f"  Collected {len(df)} observations")
        return df

    def _coingecko_spread_proxy(self, symbol: str, start_date: str,
                                end_date: str) -> pd.DataFrame:
        """
        Estimate spread using CoinGecko OHLC data (rough proxy).

        Spread proxy = (high - low) / close × 100
        """
        print(f"  Using OHLC spread proxy for {symbol}...")

        # Map symbol to CoinGecko ID
        coin_map = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'XRP': 'ripple',
            'BNB': 'binancecoin',
            'LTC': 'litecoin',
            'ADA': 'cardano'
        }

        coin_id = coin_map.get(symbol.upper())
        if not coin_id:
            raise ValueError(f"Unknown symbol: {symbol}")

        # CoinGecko API call
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart/range"

        start_timestamp = int(pd.to_datetime(start_date).timestamp())
        end_timestamp = int(pd.to_datetime(end_date).timestamp())

        params = {
            'vs_currency': 'usd',
            'from': start_timestamp,
            'to': end_timestamp
        }

        try:
            response = requests.get(url, params=params)
            data = response.json()

            if 'prices' not in data:
                raise ValueError("Invalid CoinGecko response")

            # Convert to DataFrame
            prices = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
            prices['date'] = pd.to_datetime(prices['timestamp'], unit='ms')
            prices.set_index('date', inplace=True)
            prices.drop('timestamp', axis=1, inplace=True)

            # Compute daily high-low as spread proxy
            daily = prices.resample('D').agg({'price': ['min', 'max', 'last']})
            daily.columns = ['low', 'high', 'close']
            daily['spread_proxy'] = ((daily['high'] - daily['low']) / daily['close']) * 100
            daily['bid'] = daily['close'] - (daily['high'] - daily['low']) / 2
            daily['ask'] = daily['close'] + (daily['high'] - daily['low']) / 2
            daily['spread_pct'] = daily['spread_proxy']

            print(f"  Collected {len(daily)} days (proxy spread)")
            return daily[['bid', 'ask', 'spread_pct']]

        except Exception as e:
            print(f"  Error fetching from CoinGecko: {e}")
            return pd.DataFrame()

    def collect_traditional_spread(self, symbol: str, start_date: str,
                                   end_date: str) -> pd.DataFrame:
        """
        Collect bid-ask spread for traditional asset.

        Args:
            symbol: Ticker symbol (e.g., 'SPY', 'GLD')
            start_date: Start date
            end_date: End date

        Returns:
            DataFrame with spread data
        """
        if not YFINANCE_AVAILABLE:
            print("yfinance not available. Install with: pip install yfinance")
            return pd.DataFrame()

        print(f"Collecting {symbol} data from Yahoo Finance...")

        try:
            ticker = yf.Ticker(symbol)

            # Fetch historical data with bid/ask if available
            df = ticker.history(start=start_date, end=end_date, interval='1d')

            if df.empty:
                print(f"  No data available for {symbol}")
                return pd.DataFrame()

            # Yahoo Finance doesn't provide bid/ask for most assets
            # Use high-low as proxy (similar to crypto proxy)
            df['spread_proxy'] = ((df['High'] - df['Low']) / df['Close']) * 100
            df['bid'] = df['Close'] - (df['High'] - df['Low']) / 2
            df['ask'] = df['Close'] + (df['High'] - df['Low']) / 2
            df['spread_pct'] = df['spread_proxy']

            result = df[['bid', 'ask', 'spread_pct', 'Volume']].copy()
            result.rename(columns={'Volume': 'volume'}, inplace=True)

            print(f"  Collected {len(result)} days")
            return result

        except Exception as e:
            print(f"  Error: {e}")
            return pd.DataFrame()

    def collect_orderbook_depth(self, symbol: str, date: datetime,
                                levels: int = 10) -> Dict:
        """
        Collect order book depth at specific date.

        Args:
            symbol: Crypto symbol
            date: Date to fetch
            levels: Number of orderbook levels to aggregate

        Returns:
            Dictionary with bid_depth, ask_depth, total_depth
        """
        if not CCXT_AVAILABLE or self.crypto_exchange is None:
            return {'bid_depth': np.nan, 'ask_depth': np.nan, 'total_depth': np.nan}

        trading_pair = f"{symbol}/USDT"

        try:
            orderbook = self.crypto_exchange.fetch_order_book(trading_pair)

            # Sum volumes at top N levels
            bid_depth = sum(bid[1] for bid in orderbook['bids'][:levels])
            ask_depth = sum(ask[1] for ask in orderbook['asks'][:levels])
            total_depth = bid_depth + ask_depth

            return {
                'bid_depth': bid_depth,
                'ask_depth': ask_depth,
                'total_depth': total_depth
            }

        except Exception as e:
            print(f"  Error fetching depth for {symbol}: {e}")
            return {'bid_depth': np.nan, 'ask_depth': np.nan, 'total_depth': np.nan}

    def collect_event_window_microstructure(self, symbol: str, event_date: str,
                                           days_before: int = 30,
                                           days_after: int = 30,
                                           asset_type: str = 'crypto') -> pd.DataFrame:
        """
        Collect microstructure data around an event.

        Args:
            symbol: Asset symbol
            event_date: Event date (YYYY-MM-DD)
            days_before: Days before event
            days_after: Days after event
            asset_type: 'crypto' or 'traditional'

        Returns:
            DataFrame with microstructure metrics and event indicators
        """
        event_dt = pd.to_datetime(event_date)
        start_date = (event_dt - timedelta(days=days_before)).strftime('%Y-%m-%d')
        end_date = (event_dt + timedelta(days=days_after)).strftime('%Y-%m-%d')

        print(f"\nCollecting {symbol} microstructure around {event_date}...")

        if asset_type == 'crypto':
            df = self.collect_crypto_spread(symbol, start_date, end_date)
        else:
            df = self.collect_traditional_spread(symbol, start_date, end_date)

        if df.empty:
            return df

        # Add event indicators
        df['days_to_event'] = (df.index - event_dt).days
        df['pre_event'] = df['days_to_event'] < 0
        df['post_event'] = df['days_to_event'] > 0
        df['event_day'] = df['days_to_event'] == 0

        # Calculate baseline (pre-event average)
        pre_event_data = df[df['pre_event']]
        if not pre_event_data.empty:
            df['spread_baseline'] = pre_event_data['spread_pct'].mean()
            df['spread_change'] = df['spread_pct'] - df['spread_baseline']
            df['spread_change_pct'] = (df['spread_change'] / df['spread_baseline']) * 100

        return df

    def compare_crypto_vs_traditional(self, crypto_symbol: str, trad_symbol: str,
                                     event_date: str) -> Dict:
        """
        Compare microstructure response between crypto and traditional asset.

        Args:
            crypto_symbol: Crypto symbol (e.g., 'BTC')
            trad_symbol: Traditional symbol (e.g., 'SPY')
            event_date: Event date

        Returns:
            Dictionary with comparison statistics
        """
        print(f"\n{'='*60}")
        print(f"COMPARATIVE MICROSTRUCTURE ANALYSIS")
        print(f"Event: {event_date}")
        print(f"{'='*60}")

        # Collect data
        crypto_data = self.collect_event_window_microstructure(
            crypto_symbol, event_date, asset_type='crypto'
        )
        trad_data = self.collect_event_window_microstructure(
            trad_symbol, event_date, asset_type='traditional'
        )

        if crypto_data.empty or trad_data.empty:
            print("Insufficient data for comparison")
            return {}

        # Calculate statistics
        def calc_event_impact(df):
            pre = df[df['pre_event']]['spread_pct'].mean()
            post = df[df['post_event']]['spread_pct'].mean()
            change = post - pre
            change_pct = (change / pre) * 100 if pre > 0 else 0

            from scipy.stats import ttest_ind
            t_stat, p_val = ttest_ind(
                df[df['post_event']]['spread_pct'].dropna(),
                df[df['pre_event']]['spread_pct'].dropna()
            )

            return {
                'pre_mean': pre,
                'post_mean': post,
                'change': change,
                'change_pct': change_pct,
                't_stat': t_stat,
                'p_value': p_val,
                'significant': p_val < 0.05
            }

        crypto_impact = calc_event_impact(crypto_data)
        trad_impact = calc_event_impact(trad_data)

        # Print results
        print(f"\n{crypto_symbol} (Cryptocurrency):")
        print(f"  Pre-event spread:  {crypto_impact['pre_mean']:.4f}%")
        print(f"  Post-event spread: {crypto_impact['post_mean']:.4f}%")
        print(f"  Change:           {crypto_impact['change_pct']:+.2f}%")
        print(f"  t-statistic:      {crypto_impact['t_stat']:.3f}")
        print(f"  p-value:          {crypto_impact['p_value']:.4f}")
        print(f"  Significant:      {'YES***' if crypto_impact['p_value'] < 0.01 else 'YES**' if crypto_impact['p_value'] < 0.05 else 'NO'}")

        print(f"\n{trad_symbol} (Traditional):")
        print(f"  Pre-event spread:  {trad_impact['pre_mean']:.4f}%")
        print(f"  Post-event spread: {trad_impact['post_mean']:.4f}%")
        print(f"  Change:           {trad_impact['change_pct']:+.2f}%")
        print(f"  t-statistic:      {trad_impact['t_stat']:.3f}")
        print(f"  p-value:          {trad_impact['p_value']:.4f}")
        print(f"  Significant:      {'YES***' if trad_impact['p_value'] < 0.01 else 'YES**' if trad_impact['p_value'] < 0.05 else 'NO'}")

        print(f"\nDifference (Traditional - Crypto):")
        diff_change = trad_impact['change_pct'] - crypto_impact['change_pct']
        print(f"  Spread change difference: {diff_change:+.2f} pp")

        return {
            'crypto': crypto_impact,
            'traditional': trad_impact,
            'difference': diff_change,
            'crypto_data': crypto_data,
            'trad_data': trad_data
        }


def download_all_microstructure_data():
    """Download microstructure data for all assets and events."""
    collector = MicrostructureDataCollector()

    # Regulatory events from config
    events = config.PILOT_EVENTS

    print("Downloading microstructure data for pilot study...")
    print(f"Events: {len(events)}")
    print(f"Crypto assets: {config.CRYPTO_ASSETS}")
    print(f"Traditional assets: {config.TRADITIONAL_ASSETS}")

    all_results = []

    for event in events:
        event_date = event['date']
        event_name = event['name']

        print(f"\n{'='*60}")
        print(f"Event: {event_name} ({event_date})")
        print(f"{'='*60}")

        # Collect for one crypto and one traditional asset (pilot)
        result = collector.compare_crypto_vs_traditional(
            crypto_symbol='BTC',
            trad_symbol='SPY',
            event_date=event_date
        )

        result['event_name'] = event_name
        result['event_date'] = event_date
        all_results.append(result)

    return all_results


if __name__ == "__main__":
    # Test on single event
    collector = MicrostructureDataCollector()

    print("Testing microstructure data collection...")
    result = collector.compare_crypto_vs_traditional(
        crypto_symbol='BTC',
        trad_symbol='SPY',
        event_date='2024-01-10'  # BTC ETF approval
    )

    if result:
        print("\n[SUCCESS] Microstructure data collection working!")
    else:
        print("\n[FAIL] Check API keys and network connection")
