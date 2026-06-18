# Data Sources Guide

Complete guide to collecting microstructure data for Paper 2.

## Cryptocurrency Microstructure Data

### Option 1: Binance API (Free, Good Quality)

**Access:** Free public API
**Signup:** https://www.binance.com/en/register
**Docs:** https://binance-docs.github.io/apidocs/spot/en/

**Setup:**
```python
import ccxt
exchange = ccxt.binance({
    'enableRateLimit': True
})

# Fetch orderbook
orderbook = exchange.fetch_order_book('BTC/USDT')
print(f"Best bid: {orderbook['bids'][0][0]}")
print(f"Best ask: {orderbook['asks'][0][0]}")
```

**Rate Limits:** 1200 requests/minute
**Historical:** Limited to recent data (use CoinGecko for historical)

### Option 2: CoinGecko API (Free, Historical)

**Access:** Free tier available
**Signup:** https://www.coingecko.com/en/api
**Docs:** https://www.coingecko.com/en/api/documentation

**Setup:**
```bash
# No API key needed for basic tier
curl "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range?vs_currency=usd&from=1609459200&to=1640995200"
```

**Limitations:**
- No true bid/ask (must use OHLC proxy)
- 10-50 calls/minute (free tier)
- Good for pilot study

### Option 3: Kaiko (Premium, Best Quality)

**Access:** Paid subscription (~$500-1000/month)
**Signup:** https://www.kaiko.com/
**Quality:** Institutional-grade tick data

**Features:**
- Tick-by-tick orderbook snapshots
- 100+ exchanges
- Historical data back to 2013
- Order flow analytics

**Recommendation:** Use for final paper, not pilot

---

## Traditional Market Microstructure Data

### Option 1: Yahoo Finance (Free, Proxy Data)

**Access:** Free via yfinance library
**Install:** `pip install yfinance`

**Setup:**
```python
import yfinance as yf
spy = yf.Ticker('SPY')
hist = spy.history(start='2024-01-01', end='2024-01-31')

# Compute spread proxy
hist['spread_proxy'] = ((hist['High'] - hist['Low']) / hist['Close']) * 100
```

**Limitations:**
- No true bid/ask (OHLC proxy only)
- Daily data only
- Good enough for pilot study

### Option 2: WRDS TAQ (Institutional, Best Quality)

**Access:** Requires university subscription
**Signup:** https://wrds-www.wharton.upenn.edu/
**Cost:** Free for academic users with institutional access

**Features:**
- Trade and Quote (TAQ) data from NYSE/NASDAQ
- Millisecond timestamps
- True bid/ask quotes
- Depth at each price level

**Setup (Python):**
```python
import wrds
db = wrds.Connection()

# Query TAQ data
query = """
SELECT time, bid, ask, bidsiz, asksiz
FROM taq.ctm_20240110
WHERE sym_root = 'SPY'
"""
df = db.raw_sql(query)
```

**Recommendation:** Use if available, otherwise Yahoo is acceptable

### Option 3: Alpha Vantage (Free API)

**Access:** Free API key
**Signup:** https://www.alphavantage.co/support/#api-key
**Limits:** 5 calls/minute, 500 calls/day

**Setup:**
```python
import requests

url = 'https://www.alphavantage.co/query'
params = {
    'function': 'TIME_SERIES_DAILY',
    'symbol': 'SPY',
    'apikey': 'YOUR_API_KEY',
    'outputsize': 'full'
}
response = requests.get(url, params=params)
data = response.json()
```

**Limitations:**
- No bid/ask (OHLC only)
- Rate limits restrictive
- Use only if Yahoo fails

---

## Exchange Volume Data

### CoinGecko Volume API (Free)

**Endpoint:** `/coins/{id}/market_chart/range`
**Includes:** Volume by exchange

**Example:**
```python
import requests

url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range"
params = {
    'vs_currency': 'usd',
    'from': 1609459200,  # Unix timestamp
    'to': 1640995200
}
response = requests.get(url, params=params)
data = response.json()
volumes = data['total_volumes']
```

### Exchange-Specific APIs

**Coinbase:**
```python
import ccxt
coinbase = ccxt.coinbase()
volume = coinbase.fetch_ticker('BTC/USD')['baseVolume']
```

**Binance:**
```python
binance = ccxt.binance()
volume = binance.fetch_ticker('BTC/USDT')['baseVolume']
```

### Nomics API (Historical Volume by Exchange)

**Access:** Free tier available
**Signup:** https://nomics.com/
**Docs:** https://nomics.com/docs/

**Features:**
- Volume by exchange (historical)
- Aggregated global volume
- 1-day to 1-hour granularity

**Example:**
```bash
curl "https://api.nomics.com/v1/exchange-markets/ticker?key=YOUR_KEY&exchange=binance"
```

---

## Regulatory Events Database

### From Paper 1

Use the 50 curated events from Paper 1:
- File: `data/events.csv`
- Filter: `type == 'Regulatory'`
- Result: ~20 regulatory events

### Additional Sources

**SEC Press Releases:**
- URL: https://www.sec.gov/news/pressreleases
- Filter: Cryptocurrency, enforcement
- Format: Date, title, description

**CFTC Announcements:**
- URL: https://www.cftc.gov/PressRoom/PressReleases/index.htm
- Filter: Digital assets, bitcoin

**CoinDesk News Archive:**
- URL: https://www.coindesk.com/policy/
- Manual curation of major events
- Cross-check with market data for impact

### Event Validation

For each potential event:
1. Check if it affected both crypto AND traditional markets
2. Verify using Google Trends spike
3. Confirm with GDELT article counts
4. Validate with abnormal trading volume

Example validation:
```python
# BTC ETF Approval (2024-01-10)
- SEC press release: ✓
- Google Trends spike: ✓
- BTC volume spike: ✓ (3× baseline)
- SPY volume spike: ✓ (1.5× baseline)
- Traditional relevance: ✓ (affected COIN, MARA, GBTC)
```

---

## GDELT Sentiment Data

### From Paper 1

Reuse GDELT processing from Paper 1:
- File: `data/gdelt.csv`
- Columns: `S_gdelt_normalized`, `S_reg_decomposed`, `S_infra_decomposed`

### Extending for Paper 2

No additional GDELT collection needed. Use existing:
- Regulatory sentiment: `S_reg_decomposed`
- Infrastructure sentiment: `S_infra_decomposed`

---

## API Key Management

### Setup Environment Variables

Create `.env` file in project root:
```bash
# Cryptocurrency APIs
BINANCE_API_KEY=your_key_here
BINANCE_API_SECRET=your_secret_here
COINGECKO_API_KEY=your_key_here

# Traditional market APIs
WRDS_USERNAME=your_username
WRDS_PASSWORD=your_password
ALPHA_VANTAGE_KEY=your_key_here

# Other
NOMICS_API_KEY=your_key_here
```

### Load in Code

```python
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('BINANCE_API_KEY')
```

**Security:** Add `.env` to `.gitignore` (never commit API keys!)

---

## Data Collection Workflow

### Pilot Study (Quick Start)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run diagnostic
python code/pilot_study.py --diagnostic

# 3. If successful, run pilot
python code/pilot_study.py
```

**Expected Runtime:** ~10 minutes
**Data Required:** CoinGecko (free) + Yahoo Finance (free)

### Full Study (Complete Dataset)

```bash
# 1. Collect crypto microstructure
python code/microstructure_data.py --crypto --start 2019-01-01 --end 2025-01-31

# 2. Collect traditional microstructure
python code/microstructure_data.py --traditional --start 2019-01-01 --end 2025-01-31

# 3. Collect exchange volumes
python code/microstructure_data.py --volumes --start 2019-01-01 --end 2025-01-31

# 4. Run full analysis
python code/run_full_analysis.py
```

**Expected Runtime:** 4-8 hours (with rate limits)
**Storage:** ~500MB compressed

---

## Data Quality Checklist

Before analysis, verify:

- [ ] No gaps in date ranges (handle weekends/holidays)
- [ ] Spreads are positive (bid < ask)
- [ ] Outliers removed (spreads > 10% flagged)
- [ ] Volume data matches across sources
- [ ] Event dates align with market data timestamps
- [ ] UTC timezone consistency

---

## Recommended Setup for Pilot

**Minimal (Free):**
- Crypto: CoinGecko API
- Traditional: Yahoo Finance
- Volume: CoinGecko aggregates

**Optimal (Mixed):**
- Crypto: Binance API (free) for recent + CoinGecko for historical
- Traditional: WRDS (if available), else Yahoo
- Volume: Exchange APIs + CoinGecko

**Production (Paid):**
- Crypto: Kaiko subscription
- Traditional: WRDS TAQ
- Volume: Nomics + exchange APIs

---

## Troubleshooting

### "API rate limit exceeded"
**Solution:** Add delays between requests
```python
import time
time.sleep(2)  # 2 second delay
```

### "No data returned"
**Solution:** Check date ranges and symbol names
```python
# Binance uses different formats
'BTC/USDT'  # Binance
'bitcoin'   # CoinGecko
'BTC-USD'   # Yahoo Finance
```

### "Missing values in spread"
**Solution:** Forward-fill small gaps
```python
df['spread_pct'].fillna(method='ffill', limit=3, inplace=True)
```

---

## Contact for Data Issues

If you encounter persistent data collection issues:
1. Check API status pages (e.g., status.binance.com)
2. Verify API keys are active
3. Test with single-day requests first
4. Open GitHub issue with error details

---

## Storage & Version Control

**DO NOT commit raw data to GitHub**

Add to `.gitignore`:
```
data/crypto_microstructure/*.csv
data/traditional_microstructure/*.csv
data/exchange_volumes/*.csv
*.h5
*.feather
```

**Recommended:** Store raw data in cloud (AWS S3, Google Drive) and version with DVC

---

## Reproducibility

For complete reproducibility, document:
1. API versions used (ccxt==4.0.0, yfinance==0.2.28)
2. Data collection dates (e.g., "Downloaded 2025-01-15")
3. Any manual adjustments (outlier removal, gap filling)
4. Random seeds for any sampling

Include in `data/COLLECTION_LOG.md`
