# Is 0.97pp Spread Actually Meaningful?

**Date:** October 28, 2025
**Question:** Is the 0.974 percentage point spread in event sensitivity actually a big deal or disappointingly small?
**Answer:** **IT DEPENDS ON WHAT IT'S MEASURING**

---

## The Confusion

You're measuring **RETURNS** (price changes), NOT volatility changes!

### What the Coefficients Actually Mean:

**BNB: 0.947%** = When an event happens, BNB's price changes by +0.947% on average
**LTC: -0.027%** = When an event happens, LTC's price barely budges (-0.027%)

**Spread: 0.974pp** = BNB moves nearly 1 percentage point more than LTC during events

---

## Is 0.97pp Big or Small?

### For Crypto DAILY Returns:

**Typical context:**
- Normal daily crypto volatility: ±3-5%
- Big news day: ±10-20%
- Major crash/pump: ±30-50%

**Your event effects:**
- BNB: +0.947% (modest but measurable)
- LTC: -0.027% (basically noise)

### The Issue: These are AVERAGES across 18 events

If you're averaging across:
- Infrastructure events (some positive, some negative)
- Regulatory events (some positive, some negative)
- Different market conditions

Then averaging out to 0.947% means individual events could be MUCH larger!

---

## What Does This Actually Show?

### The Finding is NOT:
❌ "Events cause massive price movements"

### The Finding IS:
✅ "BNB is consistently more sensitive to events than LTC"

**The heterogeneity is the story**, not the absolute magnitude!

- BNB responds to events (0.947% average effect, significant)
- LTC doesn't respond to events (-0.027%, not significant)
- This pattern is STABLE across different event types
- The 0.97pp spread is ROBUST across placebo tests, temporal periods, etc.

---

## Let Me Check: What Are Individual Event Magnitudes?

The coefficients you have are **pooled across all events** within each type:
- `D_infrastructure` = average effect of ALL infrastructure events combined
- `D_regulatory` = average effect of ALL regulatory events combined

**Question:** Do you have data on INDIVIDUAL events (e.g., FTX collapse, Ethereum Merge)?

If individual events show ±5-10% price impacts, then a 0.97pp difference in **average sensitivity** is actually substantial!

---

## The Real Question

**What matters more:**

1. **Absolute magnitude?**
   - 0.97pp sounds small
   - But it's an AVERAGE across diverse events
   - Individual events likely have much larger impacts

2. **Cross-sectional pattern?**
   - BNB responds, LTC doesn't ← This is robust
   - Pattern holds across placebo tests ← Real finding
   - Cohen's d = 5.19 ← HUGE effect size
   - Rankings stable across time periods ← Structural

---

## Finance Context

### Traditional finance benchmarks:

**Beta (stock market sensitivity):**
- High-beta stock: 1.5-2.0 (moves 50-100% more than market)
- Low-beta stock: 0.5-0.8 (moves 50-20% less than market)
- Spread: ~1.0-1.5x difference

**Your finding:**
- BNB event sensitivity: 0.947%
- LTC event sensitivity: -0.027%
- **Relative difference: BNB responds infinitely more than LTC** (LTC is basically zero!)

---

## Hypothesis: Averaging is Hiding the Signal

If you have:
- 9 infrastructure events (some +5%, some -5%)
- 9 regulatory events (some +3%, some -3%)

And BNB responds to ALL of them while LTC responds to NONE...

Then averaging could wash out to:
- BNB: 0.947% (average across +5% and -5% cancels out)
- LTC: -0.027% (no response = noise)

**The 0.97pp spread is NOT the individual event magnitude!**
**It's the difference in AVERAGE SENSITIVITY across mixed positive/negative events!**

---

## What You Should Check

1. **Individual event magnitudes:**
   - What was BNB's response to FTX collapse specifically?
   - What was LTC's response to the same event?
   - Are individual effects ±5-10% but averaging cancels them out?

2. **Event direction:**
   - How many events were positive shocks vs negative?
   - Is the 0.947% an average of +10% and -8%?

3. **Absolute vs relative:**
   - Focus on the RATIO or DIFFERENCE, not just absolute magnitude
   - BNB being 35x more sensitive is the story (even if both are small in absolute terms)

---

## My Educated Guess

**The 0.97pp spread seems small because:**

1. **It's an AVERAGE** across positive and negative shocks that cancel out
2. **Individual events** likely have ±5-15% impacts for BNB
3. **LTC barely responds** to any events (hence near-zero average)
4. **The heterogeneity is the finding**, not the absolute magnitude

**This is like saying:**
- "Stock A has beta of 1.5, Stock B has beta of 0.0"
- The absolute numbers seem boring
- But Stock B literally doesn't respond to market movements AT ALL!
- That's interesting even if the effect sizes are modest

---

## Verdict

**Is 0.97pp meaningful?**
- In isolation: Seems small
- As an AVERAGE across 18 mixed events: Probably hiding larger individual effects
- As a measure of HETEROGENEITY: Yes! BNB responds, LTC doesn't!

**The story is:**
> "Some cryptos (BNB, XRP) are event-sensitive. Others (LTC, ETH) are event-immune. The 0.97pp spread in average sensitivity reflects a fundamental structural difference in how tokens respond to macro shocks."

**Not clickbait-worthy, but academically solid!**
