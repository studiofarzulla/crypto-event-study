# Critical Fixes - Must Apply Before Running

## Fix #1: Make dotenv optional (config.py)

**File**: `event_study/code/config.py`
**Line**: 8
**Replace**:
```python
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
```

**With**:
```python
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Continue without .env file - will use defaults
    pass
```

---

## Fix #2: Half-life calculation (event_impact_analysis.py)

**File**: `event_study/code/event_impact_analysis.py`
**Line**: 514
**Replace**:
```python
half_life = np.log(0.5) / np.log(persistence)
```

**With**:
```python
half_life = -np.log(0.5) / np.log(persistence)
```

---

## Fix #3: Half-life calculation #2 (event_impact_analysis.py)

**File**: `event_study/code/event_impact_analysis.py`
**Line**: 747
**Replace**:
```python
return -np.log(0.5) / np.log(persistence)
```

**With**: (This one is already correct, but verify sign)
```python
return -np.log(0.5) / np.log(persistence)  # Correct ✓
```

---

## Fix #4: Timezone handling (robustness_checks.py)

**File**: `event_study/code/robustness_checks.py`
**Line**: 176
**Replace**:
```python
events_df['date'] = pd.to_datetime(events_df['date'])
```

**With**:
```python
events_df['date'] = pd.to_datetime(events_df['date'], utc=True)
```

---

## Fix #5: Safe dictionary access (publication_outputs.py)

**File**: `event_study/code/publication_outputs.py`
**Lines**: 66-73

**Replace**:
```python
garch_aic = models.get('GARCH(1,1)', {}).aic if 'GARCH(1,1)' in models and models['GARCH(1,1)'].convergence else np.nan
garch_bic = models.get('GARCH(1,1)', {}).bic if 'GARCH(1,1)' in models and models['GARCH(1,1)'].convergence else np.nan

tarch_aic = models.get('TARCH(1,1)', {}).aic if 'TARCH(1,1)' in models and models['TARCH(1,1)'].convergence else np.nan
tarch_bic = models.get('TARCH(1,1)', {}).bic if 'TARCH(1,1)' in models and models['TARCH(1,1)'].convergence else np.nan

tarchx_aic = models.get('TARCH-X', {}).aic if 'TARCH-X' in models and models['TARCH-X'].convergence else np.nan
tarchx_bic = models.get('TARCH-X', {}).bic if 'TARCH-X' in models and models['TARCH-X'].convergence else np.nan
```

**With**:
```python
def safe_get_aic_bic(models, model_name):
    if model_name in models and models[model_name].convergence:
        return models[model_name].aic, models[model_name].bic
    return np.nan, np.nan

garch_aic, garch_bic = safe_get_aic_bic(models, 'GARCH(1,1)')
tarch_aic, tarch_bic = safe_get_aic_bic(models, 'TARCH(1,1)')
tarchx_aic, tarchx_bic = safe_get_aic_bic(models, 'TARCH-X)')
```

---

## Fix #6: Remove redundant rename (coingecko_fetcher.py)

**File**: `event_study/code/coingecko_fetcher.py`
**Line**: 150
**Delete** (or comment out):
```python
daily = daily.rename(columns={'volume': 'volume', 'market_cap': 'market_cap'})
```

---

## Fix #7: Add missing positional check (robustness_checks.py)

**File**: `event_study/code/robustness_checks.py`
**Line**: 225
**Add before line 225**:
```python
# Ensure event_day has timezone info
if event_day.tz is None:
    event_day = event_day.tz_localize('UTC')
```

---

## Quick Fix Script

Save this as `apply_critical_fixes.sh`:

```bash
#!/bin/bash

echo "Applying critical fixes to event-study codebase..."

cd /home/kawaiikali/event-study/event_study/code/

# Fix 1: config.py - Make dotenv optional
sed -i '8,11d' config.py
sed -i '7a\
try:\
    from dotenv import load_dotenv\
    load_dotenv()\
except ImportError:\
    pass  # Continue without .env file' config.py

echo "✓ Fix 1 applied: config.py"

# Fix 2: event_impact_analysis.py line 514
sed -i '514s/half_life = np.log(0.5)/half_life = -np.log(0.5)/' event_impact_analysis.py

echo "✓ Fix 2 applied: event_impact_analysis.py (line 514)"

# Fix 3: robustness_checks.py line 176
sed -i "176s/pd.to_datetime(events_df\['date'\])/pd.to_datetime(events_df['date'], utc=True)/" robustness_checks.py

echo "✓ Fix 3 applied: robustness_checks.py"

# Fix 4: Remove redundant rename
sed -i '150d' coingecko_fetcher.py

echo "✓ Fix 4 applied: coingecko_fetcher.py"

echo ""
echo "All critical fixes applied!"
echo "Note: publication_outputs.py requires manual refactoring (see CRITICAL_FIXES.md)"
```

---

## Manual Fixes Required

### publication_outputs.py (lines 66-73)
This requires adding a helper function at the class level. Too complex for sed.

**Add at line 52** (after `__init__`):
```python
def _safe_get_model_stats(self, models: Dict, model_name: str) -> Tuple[float, float]:
    """Safely extract AIC and BIC from model results."""
    if model_name in models and models[model_name].convergence:
        return models[model_name].aic, models[model_name].bic
    return np.nan, np.nan
```

**Then replace lines 66-73** with:
```python
garch_aic, garch_bic = self._safe_get_model_stats(models, 'GARCH(1,1)')
tarch_aic, tarch_bic = self._safe_get_model_stats(models, 'TARCH(1,1)')
tarchx_aic, tarchx_bic = self._safe_get_model_stats(models, 'TARCH-X)')
```

---

## Installation Requirements

Before running, install dependencies:

```bash
pip install pandas numpy scipy arch matplotlib seaborn statsmodels python-dotenv requests tqdm pytest
```

Or create `requirements.txt`:
```
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.11.0
arch>=6.2.0
matplotlib>=3.7.0
seaborn>=0.12.0
statsmodels>=0.14.0
python-dotenv>=1.0.0
requests>=2.31.0
tqdm>=4.66.0
pytest>=7.4.0
```

Then:
```bash
pip install -r requirements.txt
```

---

## Verification Steps

After applying fixes:

1. **Test imports**:
```bash
cd /home/kawaiikali/event-study/event_study/code/
python -c "import config; import data_preparation; import garch_models; print('All imports OK')"
```

2. **Run unit tests**:
```bash
cd /home/kawaiikali/event-study/
pytest tests_backup/test_data_preparation.py -v
```

3. **Test data loading**:
```python
from data_preparation import DataPreparation
dp = DataPreparation()
btc = dp.prepare_crypto_data('btc')
print(btc.shape)  # Should print (n_days, n_columns)
```

4. **Test GARCH estimation** (small test):
```python
from data_preparation import DataPreparation
from garch_models import GARCHModels

dp = DataPreparation()
btc = dp.prepare_crypto_data('btc', include_events=False)
gm = GARCHModels(btc, 'btc')
result = gm.estimate_garch_11()
print(f"Converged: {result.convergence}, AIC: {result.aic}")
```

---

## Expected Behavior After Fixes

- ✅ No import errors
- ✅ Positive half-life values
- ✅ No timezone crashes
- ✅ No AttributeError on model results
- ✅ All tests in test_data_preparation.py pass

---

## Still Need to Address (Non-Critical)

These can be fixed later but should be on the roadmap:

1. **Logging instead of print statements** (all files)
2. **Input validation** (all public methods)
3. **Type hints** (many functions)
4. **Code duplication** (robustness_checks.py correlation code)
5. **Long methods** (event_impact_analysis.py)
6. **Magic numbers** (tarch_x_manual.py starting values)

---

## Questions for User

1. **Data sources**: Are all CSV files up-to-date?
2. **API key**: Is COINGECKO_API_KEY required or optional?
3. **Overlap adjustment**: Should overlapping events be 0.5+0.5 or 1+1? (methodology question)
4. **Persistence adjustment**: Is adding event coefficients to persistence theoretically justified? (line 741)
5. **Testing**: Should I restore tests/ directory?

---

End of Critical Fixes
