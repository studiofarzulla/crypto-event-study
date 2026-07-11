#!/usr/bin/env python3
"""
Rebuild the Binance daily-OHLCV parquet cache used by the c11 SMOKE TEST.
=========================================================================

The smoke test in ``c11_returns_block_bootstrap.py`` reproduces the retired
returns paper's headline on its ORIGINAL sample: 4 assets (BTC/ETH/SOL/ADA)
priced from Binance daily klines. Those parquet files are derived data and are
not committed (see .gitignore); this script rebuilds them from the public
Binance klines API — no API key required.

The gate runs (A/B), which produce ``results/c-gate-returns-unified-results.csv``,
use only the committed CoinGecko CSVs in ``data/`` and do NOT need this cache.

Reproducibility notes
---------------------
- The window is frozen at 2019-01-01 .. 2026-01-28 (complete UTC days only).
  The original cache was fetched intraday on 2026-01-29, so its final candle
  was partial; we stop at the last complete day instead. No smoke-test event
  window extends past 2025-03-23, so the smoke numbers are unaffected.
- Binance historical daily klines are immutable, so ``returns``
  (= close.pct_change(), as in the original pipeline) must match the original
  cache exactly. The script verifies this against embedded SHA-256
  fingerprints of the per-symbol returns series and reports MATCH/MISMATCH.

Usage:  python code/fetch_binance_cache.py
Writes: data/cache/{SYM}_ohlcv_2019-01-01_2026-01-28.parquet
        (c11 globs {SYM}_ohlcv_2019-01-01_*.parquet, so the name resolves)
Needs:  requests, pandas, pyarrow (see requirements.txt)
"""

import hashlib
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))

from src.config import BINANCE_SPOT_SYMBOLS  # noqa: E402

# Same layout resolution as c11: paper-side keeps data under code/data/,
# the public repo keeps it at the repo root.
DATA = CODE_DIR / 'data'
if not DATA.exists():
    DATA = CODE_DIR.parent / 'data'
CACHE_DIR = DATA / 'cache'

SYMBOLS = ['BTC', 'ETH', 'SOL', 'ADA']
START = '2019-01-01'
END = '2026-01-28'          # last complete UTC day of the original sample

# data-api.binance.vision is Binance's public market-data mirror (no auth,
# fewer geo restrictions); api.binance.com is the fallback.
ENDPOINTS = [
    'https://data-api.binance.vision/api/v3/klines',
    'https://api.binance.com/api/v3/klines',
]

# SHA-256 of the per-symbol returns series (date,%.10f per line) from the
# original cache behind the published smoke-test numbers, truncated to END.
EXPECTED_FINGERPRINTS = {
    'BTC': '59abc685ff9f0a0a1e293c98c50c3a321a0a2289ec2731c8e4eb26aa5d119fbf',
    'ETH': '0e949eacab06fe09c428488580c745ec21774b032d7a6cc6ecd44f9ddbe42693',
    'SOL': '199aac1d54a84de872edc0ef13c57f347903666465b08bb839d43c91d2782861',
    'ADA': '5346137c695768d53f98ca8e05205f37b565c0a6ed9da5ef7d67f9cbf2d27a88',
}


def _ms(date_str, end_of_day=False):
    dt = datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
    ms = int(dt.timestamp() * 1000)
    return ms + (86_400_000 - 1 if end_of_day else 0)


def fetch_klines(binance_symbol):
    """All daily klines for one symbol over [START, END], paginated by 1000."""
    rows = []
    start_ms, end_ms = _ms(START), _ms(END, end_of_day=True)
    cursor = start_ms
    last_err = None
    for endpoint in ENDPOINTS:
        rows, cursor, last_err = [], start_ms, None
        try:
            while cursor <= end_ms:
                resp = requests.get(endpoint, params={
                    'symbol': binance_symbol, 'interval': '1d',
                    'startTime': cursor, 'endTime': end_ms, 'limit': 1000,
                }, timeout=30)
                resp.raise_for_status()
                batch = resp.json()
                if not batch:
                    break
                rows.extend(batch)
                cursor = batch[-1][0] + 86_400_000
                time.sleep(0.2)
            return rows
        except requests.RequestException as e:
            last_err = e
            print(f'    endpoint {endpoint} failed ({e}); trying next')
    raise RuntimeError(f'all endpoints failed for {binance_symbol}: {last_err}')


def klines_to_df(klines, symbol):
    """Mirror the original data_fetcher schema: open/high/low/close/volume/
    quote_volume/returns (+symbol), daily timestamp index, returns=pct_change."""
    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_volume', 'n_trades',
        'taker_buy_base', 'taker_buy_quote', 'ignore',
    ])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df = df.set_index('timestamp')
    for col in ['open', 'high', 'low', 'close', 'volume', 'quote_volume']:
        df[col] = df[col].astype(float)
    df['returns'] = df['close'].pct_change()
    df = df[['open', 'high', 'low', 'close', 'volume', 'quote_volume', 'returns']]
    df['symbol'] = symbol
    return df


def fingerprint(returns):
    payload = '\n'.join(f'{ts:%Y-%m-%d},{v:.10f}' for ts, v in returns.items())
    return hashlib.sha256(payload.encode()).hexdigest()


def main():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    all_ok = True
    for sym in SYMBOLS:
        bsym = BINANCE_SPOT_SYMBOLS[sym]
        print(f'{sym} ({bsym}): fetching {START}..{END} daily klines')
        df = klines_to_df(fetch_klines(bsym), sym)
        out = CACHE_DIR / f'{sym}_ohlcv_{START}_{END}.parquet'
        df.to_parquet(out)
        fp = fingerprint(df['returns'])
        ok = fp == EXPECTED_FINGERPRINTS[sym]
        all_ok &= ok
        print(f'  {len(df)} rows ({df.index[0].date()} -> {df.index[-1].date()}) -> {out.name}')
        print(f'  returns fingerprint: {fp}')
        print(f'  vs original cache:   {"MATCH" if ok else "MISMATCH -- smoke numbers may differ"}')
    print()
    if all_ok:
        print('Cache rebuilt; all returns series match the original run exactly.')
    else:
        print('WARNING: at least one series differs from the original cache.')
        print('The c11 gate results are unaffected (they use data/*.csv), but the')
        print('smoke test may not reproduce the published headline bit-exactly.')
    return 0 if all_ok else 1


if __name__ == '__main__':
    sys.exit(main())
