import pandas as pd
import numpy as np
from code.core import config

# Quick anomaly scan for FTX event
DATA_DIR = config.DATA_DIR
FTX_DATE = pd.Timestamp("2022-11-11", tz='UTC')

symbols = ['btc', 'eth', 'bnb', 'ada', 'xrp', 'ltc']

print("\n" + "="*80)
print("FTX EVENT - QUICK ANOMALY SCAN")
print("="*80 + "\n")

for symbol in symbols:
    df = pd.read_csv(f"{DATA_DIR}/{symbol}.csv")
    df['snapped_at'] = pd.to_datetime(df['snapped_at'])
    df = df.set_index('snapped_at').sort_index()
    df['returns'] = df['price'].pct_change()

    # Event window
    start = FTX_DATE - pd.Timedelta(days=30)
    end = FTX_DATE + pd.Timedelta(days=30)
    window = df[start:end]

    # Find biggest drops
    worst_days = window['returns'].nsmallest(5)

    print(f"\n{symbol.upper()} - Top 5 Worst Days Around FTX:")
    print("-" * 60)
    for date, ret in worst_days.items():
        days_from_event = (date - FTX_DATE).days
        print(f"  {date.date()}: {ret*100:+.2f}% (FTX {days_from_event:+d} days)")

print("\n" + "="*80)
