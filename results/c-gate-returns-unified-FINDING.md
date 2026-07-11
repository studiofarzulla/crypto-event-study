# GATE — Returns (first moment) on the UNIFIED variance basis

**Date:** 2026-06-18
**Runner:** `code/c11_returns_block_bootstrap.py` (committed here under its pipeline
name; originally written as `c_gate_returns_unified.py` on the paper side — identical
analysis code)
**Results:** `results/c-gate-returns-unified-results.csv`
**Question:** Does the infrastructure-vs-regulatory **returns** null hold when re-estimated on the
**same sample basis as the variance analysis** (6 assets, 50 events)? This is the make-or-break
number for merging the no-structure (returns) and event-study/infra (variance) papers into one
"null at both moments" paper.

**Methodology:** UNCHANGED from the published returns paper. Same CAR engine
(`ConstantMeanModel`, window (−5,+30), 250d estimation, 30d gap, constant-mean expected return),
same within-event averaging (average per-asset CARs inside each event FIRST), same event-level
**block bootstrap** (resample whole events with replacement, preserving cross-sectional
correlation; 5000 reps, seed 42), same **Ibragimov–Müller** few-cluster test (Welch t on
event-level mean CARs). **Only the sample changed.**

---

## 1. Smoke test — engine is faithful (CONFIRMED, bit-exact)

Reran the original sample (4 assets BTC/ETH/SOL/ADA from the Binance parquet cache —
not committed; rebuild via `code/fetch_binance_cache.py`; `Infra_Negative` / `Reg_Negative`
events from `data/events_reclassified.json`, 8 vs 7 with valid CARs).

| Quantity | This run | Paper | Match |
|---|---|---|---|
| Event-equal CAR_infra / CAR_reg | −7.9% / −9.4% | −7.9% / −9.4% | ✅ exact |
| Event-equal block-bootstrap diff / p | +1.5pp / 0.916 | +1.5pp / 0.93 | ✅ (seed-level) |
| Ibragimov–Müller diff / t / df / p / CI | +1.5pp / 0.09 / 12.0 / **0.927** / [−32.5,+35.4] | +1.5pp / 0.09 / **0.93** / [−32.5,+35.4] | ✅ exact |
| Obs-weighted CAR_infra / CAR_reg (headline point) | −7.5% / −11.1% | −7.6% / −11.1% | ✅ |

**Per-event CARs match the stored `corrected_bootstrap_summary.json` to 0.00e+00** on all 15
events — the engine reproduces the exact numbers behind the paper's robustness table.

**Reconciliation of the recon flag (0.81 vs 0.927):** there is no contradiction. The paper carries
TWO inference schemes and reports both:
- **Headline p = 0.81** = the *original observation-weighted* DiD bootstrap (`bootstrap_summary.json`,
  pools all asset-level CARs, wider event-resampled CI [−25.3,+30.9]).
- **p = 0.927 (IM) / 0.93 (corrected)** = the *event-equal-weighted* block bootstrap + IM few-cluster
  test, reported in the paper as the robustness/triangulation row (§ "Few-Cluster Inference" and
  Table note). The JSONs the recon saw (0.927 IM / 0.93 corrected) are those robustness numbers,
  not a competing headline.

My simple obs-pooled reimplementation gives the same point estimate (+3.6pp) but a tighter CI
(p=0.69) because the published headline bootstrap resamples at the event block level, not the raw
observation level — a dispersion difference, not a point difference. **The decision-relevant engine
for the merge is the event-block bootstrap + IM, and those reproduce exactly.** Engine validated.

---

## 2. Gate result — returns on the unified basis (50 events, binary infra/reg)

Both bases use the shared `events.csv` (26 Infrastructure / 24 Regulatory; byte-identical to the
variance paper's copy) and the committed CoinGecko price CSVs (byte-identical across both repos;
returns = `price.pct_change()`). **All 50 events produce valid CARs on both bases** (every asset has
≥120 estimation days for every event), so n = 26 vs 24 throughout — no silent dropping.

| | CAR_infra | CAR_reg | diff (pp) | block-p (2s) | block-p (1s) | block 95% CI | IM t | IM df | IM-p | IM 95% CI | n infra/reg |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **(A) 6-asset (incl XRP)** | −0.23% | −7.42% | **+7.19** | **0.283** | 0.141 | [−5.97%, +20.48%] | 1.06 | 48 | **0.295** | [−6.46%, +20.83%] | 26 / 24 |
| **(B) 5-asset (ex XRP)** | +0.91% | −5.15% | **+6.06** | **0.400** | 0.200 | [−7.89%, +20.25%] | 0.84 | 48 | **0.405** | [−8.44%, +20.56%] | 26 / 24 |

**Power / MDE** (two-sample, 80% power, α=.05, on event-level CARs):
- (A) pooled SD = 24.1pp, observed Cohen's d = **+0.30**, MDE = d≈0.79 ≈ **19.1pp**.
- (B) pooled SD = 25.6pp, observed Cohen's d = **+0.24**, MDE ≈ **20.3pp**.

The observed difference (~6–7pp) is well below the ~19–20pp detectable threshold at this N. The
study remains **exploratory / underpowered** on the unified basis — same honest caveat as the
original paper, on a now-larger event count (50 vs 15) but a noisier full-valence sample.

---

## 3. VERDICT (gates the merge)

**The returns difference stays NON-significant on the unified variance basis. Clean dual-null holds.**

- Both bases: block-bootstrap p ≈ **0.28–0.40**, IM p ≈ **0.30–0.41**, 95% CIs comfortably cross
  zero. Nowhere near the p<0.10 line. **The merge is NOT cracked.**
- The point estimate **flips sign relative to the original paper**: on the negative-valence subset
  infra was *less* negative than reg by +3.6pp; on the full 50-event binary basis infra is again
  *less* negative (≈0% vs −5 to −7%), diff ≈ **+6–7pp**. So the directional story is consistent
  (infra returns hold up slightly better than regulatory), just bigger and still insignificant.

**Honest caveats to carry into the merge:**
1. **Directionally suggestive, not null-flat.** +6–7pp with d≈0.3 and one-sided p≈0.14 is a
   non-trivial point estimate that the sample is simply too small to resolve. Frame it as
   "no significant difference; wide CIs; underpowered (MDE ≈ 19–20pp)", NOT "returns are identical."
   This is the same posture the original paper takes, and it is the truthful one.
2. **Interesting asymmetry with the variance side.** On the unified basis the **returns** point
   estimate runs in the *same direction* the variance result runs (infra distinct from reg) but
   stays insignificant, while variance is also directional-but-insignificant under proper
   cross-asset inference (t-copula bootstrap p=0.322; see infra memory). So the cleanest honest
   framing is **"both moments directional, neither significant on the shared basis"** — a symmetric
   dual-(insignificant) result, not "null returns + significant variance." If the merge prose still
   leans on a *significant* variance asymmetry, that overclaim has to be fixed on the variance side
   too (already flagged in memory: pseudoreplication + 2-asset reframe).
3. **Valence is no longer controlled.** The original returns design compared negative-valence
   events only; the 50-event binary split mixes positive and negative events. That is exactly the
   variance basis, which is the point of the gate, but it means CAR magnitudes here are not
   directly comparable to the −7.6%/−11.1% negative-only headline. Report the 50-event binary
   numbers as the unified basis and keep the negative-only result as a valence-controlled robustness
   row if desired.

**Bottom line for the PI:** the gate passes. Returns are insignificant (p≈0.28–0.41) on the exact
6-asset/50-event basis the variance paper uses, and also on the ex-XRP 5-asset variant. The "null at
both moments" thesis survives the unification — provided the variance side is described as
directional-not-significant too (which the honest infra reframe already does).
