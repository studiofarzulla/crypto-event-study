#!/usr/bin/env python3
"""
GATE: Returns (first-moment) event study on the UNIFIED variance basis.
======================================================================

Purpose
-------
The no-structure (returns) paper estimates its headline null on a 4-asset
(BTC/ETH/SOL/ADA), negative-valence-only subset (8 infra vs 7 reg events) and
finds CAR_infra=-7.6% vs CAR_reg=-11.1%, diff=+3.6pp, p~=0.81 (block bootstrap).

The companion variance (infra/event-study) paper is estimated on a DIFFERENT
basis: 6 assets (BTC/ETH/XRP/BNB/LTC/ADA) and 50 events (binary infra/reg).

For the merged paper, BOTH moments must be reported on ONE common basis. We
adopt the variance basis and re-run the SAME returns methodology on it. This
script reuses the EXACT engine (ConstantMeanModel CAR, event-equal-weighted
block bootstrap, Ibragimov-Mueller few-cluster t-test) and changes ONLY the
sample.

It does THREE things:
  1. SMOKE TEST  -- reproduce the published headline on the ORIGINAL sample
                    (4 assets from the Binance parquet cache, Infra_Negative /
                    Reg_Negative events from events_reclassified.json).
  2. GATE (A)    -- 6-asset basis (incl. XRP), 50 events from events.csv.
  3. GATE (B)    -- 5-asset basis (ex-XRP), 50 events from events.csv.

This is ANALYSIS ONLY. It writes NEW files only:
  - c-gate-returns-unified-results.csv  (one row per basis)
  - prints a FINDING summary to stdout
It touches nothing existing.

Methodology faithfully matched to:
  - code/src/event_study.py            (ConstantMeanModel, window (-5,30),
                                         250d estimation, 30d gap)
  - code/scripts/run_corrected_bootstrap.py (event-equal-weighted block
                                         bootstrap: average across assets
                                         within event FIRST, resample whole
                                         events, seed 42, 5000 reps)
  - code/scripts/run_im_test.py        (Welch t-test on event-level mean CARs)
"""

import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))

import numpy as np
import pandas as pd
from scipy import stats

from src import config
from src.event_study import ConstantMeanModel

# ----------------------------------------------------------------------------
# Fixed methodology parameters (mirror config / scripts exactly)
# ----------------------------------------------------------------------------
WINDOW = (-5, 30)
N_BOOTSTRAP = 5000
SEED = config.RANDOM_SEED          # 42
ESTIMATION_WINDOW = config.ESTIMATION_WINDOW_DAYS   # 250
GAP_WINDOW = config.GAP_WINDOW_DAYS                 # 30

# Paper-side working copy keeps data under code/data/; the public repo keeps
# the byte-identical files at the repo root (data/, results/). Resolve both.
DATA = CODE_DIR / 'data'
if not DATA.exists():
    DATA = CODE_DIR.parent / 'data'
OUT_DIR = CODE_DIR.parent / 'results'
if not OUT_DIR.exists():
    OUT_DIR = CODE_DIR


# ----------------------------------------------------------------------------
# CAR engine (identical to ConstantMeanModel.compute_abnormal_returns)
# ----------------------------------------------------------------------------
MODEL = ConstantMeanModel(estimation_window=ESTIMATION_WINDOW, gap_window=GAP_WINDOW)


def event_level_cars(returns_dict, events, window=WINDOW):
    """For each event: list of {event_id, mean_car, asset_cars}.

    mean_car = average of per-asset CARs (within-event averaging FIRST), which
    is the equal-event-weighting scheme used by run_corrected_bootstrap.py and
    run_im_test.py. Events with zero valid assets are dropped (engine returns
    'error' when an asset has no data / insufficient estimation window).
    """
    out = []
    for ev in events:
        date = ev['date']
        asset_cars = {}
        for sym, ret in returns_dict.items():
            res = MODEL.compute_abnormal_returns(ret, date, window)
            if 'error' not in res:
                asset_cars[sym] = res['car']
        if asset_cars:
            out.append({
                'event_id': ev['event_id'],
                'date': date,
                'mean_car': float(np.mean(list(asset_cars.values()))),
                'n_assets': len(asset_cars),
            })
    return out


def block_bootstrap_diff(infra_means, reg_means, n_boot=N_BOOTSTRAP, seed=SEED):
    """Event-level block bootstrap of the difference in mean CARs.

    Mirrors CorrectedEventBlockBootstrap.bootstrap_difference_test: resample
    whole events (the event-level mean CARs) with replacement within each
    group independently, recompute group means, take difference. Two-tailed
    p against zero, percentile 95% CI.
    """
    rng = np.random.default_rng(seed)
    infra_means = np.asarray(infra_means, dtype=float)
    reg_means = np.asarray(reg_means, dtype=float)
    na, nb = len(infra_means), len(reg_means)
    orig_diff = infra_means.mean() - reg_means.mean()

    diffs = np.empty(n_boot)
    for i in range(n_boot):
        a = rng.choice(infra_means, size=na, replace=True)
        b = rng.choice(reg_means, size=nb, replace=True)
        diffs[i] = a.mean() - b.mean()

    ci_low = float(np.percentile(diffs, 2.5))
    ci_high = float(np.percentile(diffs, 97.5))
    if orig_diff >= 0:
        p_two = 2 * np.mean(diffs <= 0)
    else:
        p_two = 2 * np.mean(diffs >= 0)
    p_two = float(min(p_two, 1.0))
    # one-sided p in the direction of the point estimate
    p_one = float(min(p_two / 2.0, 1.0))
    return {
        'diff': float(orig_diff),
        'ci_low': ci_low,
        'ci_high': ci_high,
        'p_two': p_two,
        'p_one': p_one,
        'se': float(diffs.std()),
    }


def im_test(infra_means, reg_means):
    """Ibragimov-Mueller few-cluster test = Welch t-test on event-level means.
    Identical to run_im_test.ibragimov_muller_test."""
    g1 = np.asarray(infra_means, dtype=float)
    g2 = np.asarray(reg_means, dtype=float)
    n1, n2 = len(g1), len(g2)
    m1, m2 = g1.mean(), g2.mean()
    v1, v2 = g1.var(ddof=1), g2.var(ddof=1)
    se = np.sqrt(v1 / n1 + v2 / n2)
    t = (m1 - m2) / se
    df_num = (v1 / n1 + v2 / n2) ** 2
    df_den = (v1 / n1) ** 2 / (n1 - 1) + (v2 / n2) ** 2 / (n2 - 1)
    df = df_num / df_den
    p = 2 * (1 - stats.t.cdf(abs(t), df))
    tcrit = stats.t.ppf(0.975, df)
    return {
        'mean_infra': float(m1),
        'mean_reg': float(m2),
        'diff': float(m1 - m2),
        'se': float(se),
        't': float(t),
        'df': float(df),
        'p': float(p),
        'ci_low': float((m1 - m2) - tcrit * se),
        'ci_high': float((m1 - m2) + tcrit * se),
    }


def pooled_obs_bootstrap_diff(infra_obs, reg_obs, n_boot=N_BOOTSTRAP, seed=SEED):
    """OBSERVATION-weighted bootstrap of the difference (the ORIGINAL scheme
    behind the published -7.6/-11.1/p=0.81 headline). Pools all per-asset CARs,
    resamples observations with replacement. Used in the smoke test only, to
    show both published numbers reconcile."""
    rng = np.random.default_rng(seed)
    a = np.asarray(infra_obs, dtype=float)
    b = np.asarray(reg_obs, dtype=float)
    orig = a.mean() - b.mean()
    diffs = np.empty(n_boot)
    for i in range(n_boot):
        diffs[i] = rng.choice(a, size=len(a), replace=True).mean() - \
                   rng.choice(b, size=len(b), replace=True).mean()
    if orig >= 0:
        p = 2 * np.mean(diffs <= 0)
    else:
        p = 2 * np.mean(diffs >= 0)
    return {
        'mean_infra': float(a.mean()),
        'mean_reg': float(b.mean()),
        'diff': float(orig),
        'ci_low': float(np.percentile(diffs, 2.5)),
        'ci_high': float(np.percentile(diffs, 97.5)),
        'p_two': float(min(p, 1.0)),
    }


def mde_note(infra_means, reg_means, alpha=0.05, power=0.80):
    """Minimum detectable effect (two-sample t, equal-ish n) + Cohen's d of the
    observed effect, matching the paper's power discussion."""
    g1 = np.asarray(infra_means, float)
    g2 = np.asarray(reg_means, float)
    n1, n2 = len(g1), len(g2)
    sp = np.sqrt(((n1 - 1) * g1.var(ddof=1) + (n2 - 1) * g2.var(ddof=1)) / (n1 + n2 - 2))
    d_obs = (g1.mean() - g2.mean()) / sp if sp > 0 else np.nan
    # MDE in Cohen's d for a two-sample test with harmonic-mean n per group
    n_h = 2.0 / (1.0 / n1 + 1.0 / n2)
    z_a = stats.norm.ppf(1 - alpha / 2)
    z_b = stats.norm.ppf(power)
    d_mde = (z_a + z_b) * np.sqrt(2.0 / n_h)
    mde_pp = d_mde * sp  # back to CAR units (decimal CAR over window)
    return {
        'pooled_sd': float(sp),
        'cohens_d_obs': float(d_obs),
        'cohens_d_mde': float(d_mde),
        'mde_car': float(mde_pp),  # in CAR decimal units (e.g. 0.40 = 40pp)
    }


# ============================================================================
# SMOKE TEST -- original sample (4 assets from cache, reclassified events)
# ============================================================================
def load_cache_returns(symbols):
    """Load returns from the Binance parquet cache (original engine's source)."""
    import glob
    rd = {}
    for sym in symbols:
        # full-range cache file: SYM_ohlcv_2019-01-01_2026-01-29.parquet
        matches = sorted(glob.glob(str(DATA / 'cache' / f'{sym}_ohlcv_2019-01-01_*.parquet')))
        if not matches:
            print(f"  [smoke] {sym}: NO full-range cache file -> skip")
            continue
        df = pd.read_parquet(matches[-1])
        if 'returns' in df.columns:
            rd[sym] = df['returns'].dropna()
            print(f"  [smoke] {sym}: {len(rd[sym])} returns (cache)")
    return rd


def load_reclassified_neg_events():
    import json
    d = json.load(open(DATA / 'events_reclassified.json'))
    by_type = {}
    for e in d['events']:
        if not e.get('include_in_reanalysis', True):
            continue
        if not e.get('meets_impact_threshold', False):
            continue
        if not e.get('has_sufficient_estimation_data', True):
            continue
        et = e.get('type_detailed', e['type'])
        by_type.setdefault(et, []).append(e)
    return by_type


def run_smoke():
    print("\n" + "=" * 74)
    print("SMOKE TEST -- reproduce published headline on ORIGINAL sample")
    print("  (4 assets BTC/ETH/SOL/ADA from cache; Infra_Negative/Reg_Negative)")
    print("=" * 74)

    symbols = config.TIER1_ASSETS + config.TIER2_ASSETS[:2]   # BTC,ETH,SOL,ADA
    rd = load_cache_returns(symbols)
    if not rd:
        print("  [smoke] Binance parquet cache not found under data/cache/.")
        print("  [smoke] Rebuild it with:  python code/fetch_binance_cache.py")
        print("  [smoke] Skipping smoke test; gate runs (A/B) below use only the")
        print("  [smoke] committed CoinGecko CSVs and are unaffected.")
        return None
    by_type = load_reclassified_neg_events()
    infra_ev = by_type.get('Infra_Negative', [])
    reg_ev = by_type.get('Reg_Negative', [])
    print(f"  Infra_Negative events: {len(infra_ev)} | Reg_Negative events: {len(reg_ev)}")

    infra_el = event_level_cars(rd, infra_ev)
    reg_el = event_level_cars(rd, reg_ev)
    infra_means = [e['mean_car'] for e in infra_el]
    reg_means = [e['mean_car'] for e in reg_el]
    print(f"  Events with valid CARs: infra={len(infra_means)}, reg={len(reg_means)}")

    # event-equal-weighted block bootstrap (the 'corrected' / IM-consistent run)
    bb = block_bootstrap_diff(infra_means, reg_means)
    im = im_test(infra_means, reg_means)

    # observation-weighted pooled bootstrap (the ORIGINAL -7.6/-11.1/0.81 headline)
    infra_obs, reg_obs = [], []
    for ev in infra_ev:
        for sym, ret in rd.items():
            r = MODEL.compute_abnormal_returns(ret, ev['date'], WINDOW)
            if 'error' not in r:
                infra_obs.append(r['car'])
    for ev in reg_ev:
        for sym, ret in rd.items():
            r = MODEL.compute_abnormal_returns(ret, ev['date'], WINDOW)
            if 'error' not in r:
                reg_obs.append(r['car'])
    obs = pooled_obs_bootstrap_diff(infra_obs, reg_obs)

    print("\n  --- OBSERVATION-WEIGHTED pooled bootstrap (PUBLISHED HEADLINE) ---")
    print(f"    CAR_infra = {obs['mean_infra']*100:+.1f}%   CAR_reg = {obs['mean_reg']*100:+.1f}%")
    print(f"    diff = {obs['diff']*100:+.1f}pp   p(two)={obs['p_two']:.3f}   "
          f"CI=[{obs['ci_low']*100:+.1f}%, {obs['ci_high']*100:+.1f}%]")
    print(f"    [paper says: -7.6% / -11.1% / +3.6pp / p=0.81 / CI [-25.3,+30.9]]")

    print("\n  --- EVENT-EQUAL-WEIGHTED block bootstrap (paper robustness) ---")
    print(f"    CAR_infra = {im['mean_infra']*100:+.1f}%   CAR_reg = {im['mean_reg']*100:+.1f}%")
    print(f"    diff = {bb['diff']*100:+.1f}pp   p(two)={bb['p_two']:.3f}   "
          f"CI=[{bb['ci_low']*100:+.1f}%, {bb['ci_high']*100:+.1f}%]")
    print(f"    [paper says: -7.9% / -9.4% / +1.5pp / p=0.93]")

    print("\n  --- IBRAGIMOV-MUELLER few-cluster test (paper robustness) ---")
    print(f"    diff = {im['diff']*100:+.1f}pp   t={im['t']:.2f}   df={im['df']:.1f}   "
          f"p={im['p']:.3f}   CI=[{im['ci_low']*100:+.1f}%, {im['ci_high']*100:+.1f}%]")
    print(f"    [paper says: +1.5pp / t=0.09 / p=0.93 / CI [-32.5,+35.4]]")

    return {
        'obs': obs, 'bb': bb, 'im': im,
        'n_infra': len(infra_means), 'n_reg': len(reg_means),
    }


# ============================================================================
# GATE RUN -- unified variance basis (50 events, 6 or 5 assets, CoinGecko CSV)
# ============================================================================
def load_csv_returns(symbols):
    """Load returns from the committed CoinGecko price CSVs (shared with the
    variance paper; byte-identical across both repos)."""
    rd = {}
    for sym in symbols:
        df = pd.read_csv(DATA / f'{sym.lower()}.csv')
        df['date'] = pd.to_datetime(df['snapped_at'].str.replace(' UTC', '', regex=False))
        df = df.sort_values('date').set_index('date')
        ret = df['price'].pct_change().dropna()
        rd[sym] = ret
    return rd


def load_unified_events():
    ev = pd.read_csv(DATA / 'events.csv')
    infra = ev[ev['type'] == 'Infrastructure'].to_dict('records')
    reg = ev[ev['type'] == 'Regulatory'].to_dict('records')
    return infra, reg


def run_gate(label, symbols):
    print("\n" + "=" * 74)
    print(f"GATE BASIS [{label}] -- assets: {symbols}")
    print("  50 events from events.csv (binary Infrastructure/Regulatory)")
    print("=" * 74)

    rd = load_csv_returns(symbols)
    for s in symbols:
        print(f"  {s}: {len(rd[s])} returns ({rd[s].index.min().date()} -> {rd[s].index.max().date()})")
    infra_ev, reg_ev = load_unified_events()
    print(f"  events.csv: {len(infra_ev)} infra, {len(reg_ev)} reg")

    infra_el = event_level_cars(rd, infra_ev)
    reg_el = event_level_cars(rd, reg_ev)
    infra_means = [e['mean_car'] for e in infra_el]
    reg_means = [e['mean_car'] for e in reg_el]
    print(f"  events with valid CARs: infra={len(infra_means)}, reg={len(reg_means)}")

    bb = block_bootstrap_diff(infra_means, reg_means)
    im = im_test(infra_means, reg_means)
    mde = mde_note(infra_means, reg_means)

    print(f"\n  CAR_infra = {im['mean_infra']*100:+.2f}%   CAR_reg = {im['mean_reg']*100:+.2f}%")
    print(f"  diff (infra - reg) = {bb['diff']*100:+.2f}pp")
    print(f"  block-bootstrap p: two-sided={bb['p_two']:.3f}  one-sided={bb['p_one']:.3f}")
    print(f"  block-bootstrap 95% CI: [{bb['ci_low']*100:+.2f}%, {bb['ci_high']*100:+.2f}%]")
    print(f"  Ibragimov-Mueller: t={im['t']:.2f}  df={im['df']:.1f}  p={im['p']:.3f}  "
          f"CI=[{im['ci_low']*100:+.2f}%, {im['ci_high']*100:+.2f}%]")
    print(f"  Cohen's d (observed) = {mde['cohens_d_obs']:+.3f}   "
          f"pooled SD = {mde['pooled_sd']*100:.1f}pp")
    print(f"  MDE @ 80% power, a=.05: d={mde['cohens_d_mde']:.2f}  "
          f"=> {mde['mde_car']*100:.1f}pp (much larger than observed effect)")

    return {
        'basis': label,
        'assets': '/'.join(symbols),
        'n_infra': len(infra_means),
        'n_reg': len(reg_means),
        'car_infra_pct': im['mean_infra'] * 100,
        'car_reg_pct': im['mean_reg'] * 100,
        'diff_pp': bb['diff'] * 100,
        'block_p_two': bb['p_two'],
        'block_p_one': bb['p_one'],
        'block_ci_low_pct': bb['ci_low'] * 100,
        'block_ci_high_pct': bb['ci_high'] * 100,
        'im_t': im['t'],
        'im_df': im['df'],
        'im_p': im['p'],
        'im_ci_low_pct': im['ci_low'] * 100,
        'im_ci_high_pct': im['ci_high'] * 100,
        'cohens_d_obs': mde['cohens_d_obs'],
        'pooled_sd_pp': mde['pooled_sd'] * 100,
        'mde_car_pp': mde['mde_car'] * 100,
    }


def main():
    print("#" * 74)
    print("# GATE: returns event study on the UNIFIED variance basis")
    print(f"# window={WINDOW}  est={ESTIMATION_WINDOW}d  gap={GAP_WINDOW}d  "
          f"boot={N_BOOTSTRAP}  seed={SEED}")
    print("#" * 74)

    smoke = run_smoke()
    rowA = run_gate("A: 6-asset (incl XRP)", ['BTC', 'ETH', 'XRP', 'BNB', 'LTC', 'ADA'])
    rowB = run_gate("B: 5-asset (ex XRP)", ['BTC', 'ETH', 'BNB', 'LTC', 'ADA'])

    out = pd.DataFrame([rowA, rowB])
    out_path = OUT_DIR / 'c-gate-returns-unified-results.csv'
    out.to_csv(out_path, index=False)
    print("\n" + "=" * 74)
    print(f"Saved results CSV: {out_path}")
    print("=" * 74)

    print("\nGATE VERDICT")
    print("-" * 74)
    for r in (rowA, rowB):
        sig = "NON-significant (p>0.10) -> clean dual-null" if r['block_p_two'] > 0.10 \
              else "MOVED toward/into significance -> cracks the dual-null"
        print(f"  [{r['basis']}] diff={r['diff_pp']:+.2f}pp  "
              f"block-p={r['block_p_two']:.3f}  IM-p={r['im_p']:.3f}  => {sig}")
    print("-" * 74)


if __name__ == '__main__':
    main()
