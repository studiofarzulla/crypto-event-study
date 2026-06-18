# C2b — The missing like-for-like 2-asset point (BLOCKING finding)

**Date:** 17 Jun 2026. **Trigger:** external review (Opus 4.8) flagged that Table 7's
event counts cannot be nested screens on one pool (S1=50 < S4=77). Confirmed in code:
`c2_relaxed_threshold_sensitivity.py` uses `events.csv` (legacy curated 50) for S1 and
`stage2_{relaxed,nofilter,strict}_pass` for S2–S4, but **never uses `stage2_std_pass`**
(the genuine 2-asset screen on the 135 pool, n=93). Recomputed via `code/c2b_two_asset_point.py`
under the identical global-clip pipeline as S2–S4.

## Corrected, properly-nested sweep on the reconstructed 135 pool

| Screen | n | δ̄ infra | δ̄ reg | Multiplier | Welch p |
|---|---|---|---|---|---|
| No filter | 135 | 0.209 | 0.364 | **0.58×** | 0.446 |
| 1-asset (relaxed) | 115 | 1.403 | 0.944 | **1.49×** | 0.321 |
| **2-asset (std)** | **93** | **2.889** | **1.793** | **1.61×** | **0.164** |
| 3-asset (strict) | 77 | 3.834 | 2.924 | **1.31×** | 0.403 |

Legacy curated sample (separate selection process — full 4-stage protocol, not a mechanical screen):

| Legacy 50 (global clip) | 50 | 1.978 | 0.405 | **4.88×** | 0.0015 |
| Legacy 50 (rolling ±5SD winsor = canonical) | 50 | 2.385 | 0.419 | **5.7×** | 0.0008 |

## What this means
- The 5.7×/4.88× headline is a property of the **curated 50-event sample**, NOT of the
  2-asset impact threshold. The genuine 2-asset screen on the broad pool gives **1.61×**.
- On the reconstructed pool, the multiplier is **modest (1.3–1.6×) and non-significant at
  every threshold** (all p > 0.16). There is at most a weak, non-significant rise toward the
  2-asset screen — it does NOT pass through 4.88×.
- **The "multiplier peaks at the 2-asset threshold, at 5.7×" claim in §4.8 / abstract is false
  as stated** and must be removed. Submitting it knowing this = the "prose ahead of code" trap.

## Honest reframe (recommended)
The strong, significant asymmetry holds for **carefully-identified, high-salience events**
(the curated sample); under **purely mechanical impact screening** of a broad candidate pool it
attenuates to a modest, non-significant 1.3–1.6×. This is a **scope condition** — the asymmetry
is real for well-identified events but is not a universal function of multi-asset impact — and it
*concedes* R2's selection-bias point honestly rather than manufacturing a peak. Add the 93-event
row to Table 7; relabel S1 as the curated sample (not "2-asset baseline"); rewrite the abstract's
"peaks at the two-asset screen" line.

## Reproduce
`cd code && python3 c2b_two_asset_point.py`  (≈3–4 min, 6 GJR-GARCH-X SLSQP fits)
