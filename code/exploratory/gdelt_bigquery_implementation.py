#!/usr/bin/env python3
"""
GDELT BigQuery Implementation Guide for Daily Cryptocurrency Sentiment
Author: Research Assistant
Date: October 2025

This script provides a complete implementation for fetching daily GDELT sentiment
data from BigQuery for cryptocurrency event studies.
"""

import pandas as pd
from google.cloud import bigquery
from typing import List, Dict, Optional
from datetime import datetime, timedelta

# ===========================
# BIGQUERY SETUP INSTRUCTIONS
# ===========================
"""
1. Create a Google Cloud Project:
   - Go to https://console.cloud.google.com
   - Create new project or select existing
   - Enable BigQuery API

2. Set up Authentication:
   - Install Google Cloud SDK: `pip install google-cloud-bigquery pandas-gbq`
   - Create service account key:
     * Go to IAM & Admin > Service Accounts
     * Create new service account
     * Download JSON key file
   - Set environment variable:
     export GOOGLE_APPLICATION_CREDENTIALS="path/to/keyfile.json"

3. BigQuery Costs (as of 2025):
   - First 1 TB/month of queries: FREE
   - After that: $5/TB processed
   - Our queries: ~50-100 GB per year of data (well within free tier)
"""

class GDELTBigQueryFetcher:
    """Fetch daily GDELT sentiment data from BigQuery"""

    def __init__(self, project_id: str):
        """
        Initialize BigQuery client

        Args:
            project_id: Your Google Cloud Project ID
        """
        self.client = bigquery.Client(project=project_id)
        self.project_id = project_id

    def get_crypto_keywords(self) -> List[str]:
        """
        Get comprehensive cryptocurrency keywords for GDELT queries

        Returns list optimized for regulatory and infrastructure topics
        """

        # Core cryptocurrency terms
        core_terms = [
            'bitcoin', 'btc', 'ethereum', 'eth', 'cryptocurrency', 'crypto',
            'blockchain', 'defi', 'decentralized finance', 'altcoin', 'stablecoin',
            'digital asset', 'virtual currency', 'token', 'mining', 'staking'
        ]

        # Regulatory terms
        regulatory_terms = [
            'sec cryptocurrency', 'crypto regulation', 'bitcoin etf', 'crypto law',
            'digital asset regulation', 'cryptocurrency bill', 'crypto enforcement',
            'stablecoin regulation', 'defi regulation', 'crypto compliance',
            'cryptocurrency tax', 'aml cryptocurrency', 'kyc crypto'
        ]

        # Infrastructure terms
        infrastructure_terms = [
            'crypto exchange', 'blockchain upgrade', 'bitcoin halving', 'ethereum merge',
            'crypto hack', 'exchange hack', 'defi exploit', 'blockchain fork',
            'mainnet launch', 'testnet', 'layer 2', 'rollup', 'crypto wallet',
            'mining pool', 'hashrate', 'crypto custody'
        ]

        # Major exchanges and platforms
        platforms = [
            'coinbase', 'binance', 'kraken', 'ftx', 'celsius', 'blockfi',
            'uniswap', 'opensea', 'metamask', 'ledger', 'trezor'
        ]

        # Combine all terms
        all_terms = core_terms + regulatory_terms + infrastructure_terms + platforms

        return all_terms

    def build_daily_sentiment_query(
        self,
        start_date: str,
        end_date: str,
        keywords: Optional[List[str]] = None
    ) -> str:
        """
        Build BigQuery SQL for daily GDELT sentiment extraction

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            keywords: Optional custom keywords (uses defaults if None)

        Returns:
            SQL query string
        """

        if keywords is None:
            keywords = self.get_crypto_keywords()

        # Create keyword filter clause
        keyword_conditions = ' OR '.join([
            f"LOWER(DocumentIdentifier) LIKE '%{kw.lower()}%'"
            for kw in keywords
        ])

        # Build the query
        query = f"""
        WITH crypto_articles AS (
            SELECT
                DATE(PARSE_TIMESTAMP('%Y%m%d%H%M%S', CAST(DATEADDED AS STRING))) as article_date,
                DocumentIdentifier,
                Tone,
                -- Extract first tone value (overall document tone)
                CAST(SPLIT(Tone, ',')[SAFE_OFFSET(0)] AS FLOAT64) as tone_score,
                -- Get positive and negative scores
                CAST(SPLIT(Tone, ',')[SAFE_OFFSET(1)] AS FLOAT64) as positive_score,
                CAST(SPLIT(Tone, ',')[SAFE_OFFSET(2)] AS FLOAT64) as negative_score,
                -- Article metadata
                ARRAY_LENGTH(SPLIT(V2Themes, ';')) as theme_count,
                GoldsteinScale,
                -- Categorize as regulatory or infrastructure
                CASE
                    WHEN REGEXP_CONTAINS(LOWER(DocumentIdentifier),
                        r'regulat|sec|law|bill|compli|enforce|legal|court|lawsuit|settle')
                    THEN 1 ELSE 0
                END as is_regulatory,
                CASE
                    WHEN REGEXP_CONTAINS(LOWER(DocumentIdentifier),
                        r'hack|breach|exploit|upgrade|fork|launch|halving|merge|mainnet|testnet')
                    THEN 1 ELSE 0
                END as is_infrastructure
            FROM
                `gdelt-bq.gdeltv2.gkg`
            WHERE
                DATE(PARSE_TIMESTAMP('%Y%m%d%H%M%S', CAST(DATEADDED AS STRING)))
                    BETWEEN '{start_date}' AND '{end_date}'
                AND ({keyword_conditions})
                AND Tone IS NOT NULL
                AND Tone != ''
        )
        SELECT
            article_date,
            COUNT(*) as article_count,
            AVG(tone_score) as avg_tone,
            STDDEV(tone_score) as tone_stddev,
            PERCENTILE_CONT(tone_score, 0.5) OVER (PARTITION BY article_date) as median_tone,
            AVG(positive_score) as avg_positive,
            AVG(negative_score) as avg_negative,
            SUM(is_regulatory) as regulatory_count,
            SUM(is_infrastructure) as infrastructure_count,
            -- Calculate proportions
            SAFE_DIVIDE(SUM(is_regulatory), COUNT(*)) as reg_proportion,
            SAFE_DIVIDE(SUM(is_infrastructure), COUNT(*)) as infra_proportion,
            -- Weighted sentiment by article importance (using theme count as proxy)
            SUM(tone_score * theme_count) / NULLIF(SUM(theme_count), 0) as weighted_tone
        FROM
            crypto_articles
        GROUP BY
            article_date
        ORDER BY
            article_date
        """

        return query

    def fetch_daily_sentiment(
        self,
        start_date: str,
        end_date: str,
        save_path: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Fetch daily GDELT sentiment data

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            save_path: Optional path to save CSV

        Returns:
            DataFrame with daily sentiment data
        """

        print(f"Fetching GDELT data from {start_date} to {end_date}...")

        # Build and run query
        query = self.build_daily_sentiment_query(start_date, end_date)

        # Execute query
        df = self.client.query(query).to_dataframe()

        print(f"Retrieved {len(df)} days of data")

        # Post-processing
        df['article_date'] = pd.to_datetime(df['article_date'])

        # Calculate normalized sentiment (z-score with 30-day rolling window)
        df['tone_zscore'] = (
            df['avg_tone'] - df['avg_tone'].rolling(30, min_periods=15).mean()
        ) / df['avg_tone'].rolling(30, min_periods=15).std()

        # Calculate decomposed sentiment
        df['reg_sentiment'] = df['tone_zscore'] * df['reg_proportion']
        df['infra_sentiment'] = df['tone_zscore'] * df['infra_proportion']

        # Fill missing values
        df['tone_zscore'] = df['tone_zscore'].fillna(0)
        df['reg_sentiment'] = df['reg_sentiment'].fillna(0)
        df['infra_sentiment'] = df['infra_sentiment'].fillna(0)

        if save_path:
            df.to_csv(save_path, index=False)
            print(f"Saved to {save_path}")

        return df

    def fetch_event_window_sentiment(
        self,
        event_date: str,
        window_days: int = 7
    ) -> pd.DataFrame:
        """
        Fetch sentiment for a specific event window

        Args:
            event_date: Event date (YYYY-MM-DD)
            window_days: Days before and after event

        Returns:
            DataFrame with event window sentiment
        """

        event_dt = datetime.strptime(event_date, '%Y-%m-%d')
        start_dt = event_dt - timedelta(days=window_days)
        end_dt = event_dt + timedelta(days=window_days)

        return self.fetch_daily_sentiment(
            start_dt.strftime('%Y-%m-%d'),
            end_dt.strftime('%Y-%m-%d')
        )


class GDELTPyRImplementation:
    """Alternative implementation using gdeltPyR library"""

    @staticmethod
    def get_implementation_code() -> str:
        """Return gdeltPyR implementation code"""

        return """
# Installation:
# pip install gdeltPyR

import gdelt

# Initialize gdelt object
gd = gdelt.gdelt()

# Method 1: Search for crypto articles
def fetch_crypto_articles(date_range):
    '''
    Fetch cryptocurrency articles for date range

    Args:
        date_range: List of dates ['2019-01-01', '2019-01-02', ...]
    '''

    results = []
    for date in date_range:
        # Search for articles
        data = gd.Search(
            date=date,
            table='gkg',
            coverage=True,  # Full text
            translation=False
        )

        # Filter for crypto keywords
        crypto_data = data[
            data['DocumentIdentifier'].str.contains(
                'bitcoin|ethereum|cryptocurrency|blockchain|defi',
                case=False,
                na=False
            )
        ]

        results.append(crypto_data)

    return pd.concat(results, ignore_index=True)

# Method 2: Use BigQuery through gdeltPyR
def query_bigquery_gdelt():
    '''
    Query GDELT BigQuery tables directly
    '''

    # Set your project ID
    project_id = 'your-project-id'

    # Query using pandas-gbq
    query = '''
    SELECT
        DATE(DATEADDED) as date,
        AVG(CAST(SPLIT(Tone, ',')[OFFSET(0)] AS FLOAT64)) as avg_tone,
        COUNT(*) as article_count
    FROM
        `gdelt-bq.gdeltv2.gkg`
    WHERE
        DATE(DATEADDED) BETWEEN '2019-01-01' AND '2023-12-31'
        AND LOWER(DocumentIdentifier) LIKE '%crypto%'
    GROUP BY
        date
    ORDER BY
        date
    '''

    df = pd.read_gbq(query, project_id=project_id)
    return df
"""


def estimate_query_costs(
    years: int = 5,
    gb_per_year: float = 75
) -> Dict[str, float]:
    """
    Estimate BigQuery costs for GDELT queries

    Args:
        years: Number of years of data
        gb_per_year: Estimated GB scanned per year

    Returns:
        Cost estimates
    """

    total_gb = years * gb_per_year
    total_tb = total_gb / 1024

    # BigQuery pricing (as of 2025)
    free_tb = 1.0  # First 1 TB/month free
    price_per_tb = 5.0  # $5/TB after free tier

    # Calculate monthly costs
    monthly_tb = total_tb / 12  # Spread queries over time
    billable_tb = max(0, monthly_tb - free_tb)
    monthly_cost = billable_tb * price_per_tb

    return {
        'total_data_gb': total_gb,
        'total_data_tb': total_tb,
        'monthly_tb': monthly_tb,
        'monthly_cost_usd': monthly_cost,
        'annual_cost_usd': monthly_cost * 12,
        'within_free_tier': monthly_tb <= free_tb
    }


def main():
    """Demonstrate BigQuery implementation"""

    print("=" * 80)
    print("GDELT BIGQUERY IMPLEMENTATION GUIDE")
    print("Daily Cryptocurrency Sentiment Data")
    print("=" * 80)

    # Cost estimation
    print("\n1. COST ESTIMATION")
    print("-" * 40)
    costs = estimate_query_costs(years=5, gb_per_year=75)

    for key, value in costs.items():
        if isinstance(value, bool):
            print(f"   {key}: {'Yes' if value else 'No'}")
        elif isinstance(value, float):
            print(f"   {key}: {value:.2f}")
        else:
            print(f"   {key}: {value}")

    # Sample query
    print("\n2. SAMPLE BIGQUERY QUERY")
    print("-" * 40)

    fetcher = GDELTBigQueryFetcher(project_id='your-project-id')
    sample_query = fetcher.build_daily_sentiment_query(
        '2019-01-01',
        '2019-01-31',
        keywords=['bitcoin', 'ethereum']
    )

    print("First 500 characters of query:")
    print(sample_query[:500] + "...")

    # Keywords
    print("\n3. RECOMMENDED KEYWORDS")
    print("-" * 40)
    keywords = fetcher.get_crypto_keywords()
    print(f"Total keywords: {len(keywords)}")
    print("Sample keywords:", ', '.join(keywords[:10]))

    # Implementation steps
    print("\n4. IMPLEMENTATION STEPS")
    print("-" * 40)
    steps = [
        "Set up Google Cloud Project and enable BigQuery API",
        "Create service account and download credentials JSON",
        "Install required packages: google-cloud-bigquery, pandas-gbq",
        "Set GOOGLE_APPLICATION_CREDENTIALS environment variable",
        "Initialize GDELTBigQueryFetcher with your project ID",
        "Run fetch_daily_sentiment() for your date range",
        "Process results and merge with price data",
        "Re-run TARCH-X models with daily sentiment"
    ]

    for i, step in enumerate(steps, 1):
        print(f"   {i}. {step}")

    # Alternative implementation
    print("\n5. ALTERNATIVE: gdeltPyR LIBRARY")
    print("-" * 40)
    print("   - Simpler setup but less flexible")
    print("   - Good for small-scale testing")
    print("   - Can also access BigQuery through pandas-gbq")
    print("   - See get_implementation_code() for examples")

    print("\n" + "=" * 80)
    print("Ready to implement! Choose BigQuery for production or gdeltPyR for testing.")
    print("=" * 80)


if __name__ == "__main__":
    main()