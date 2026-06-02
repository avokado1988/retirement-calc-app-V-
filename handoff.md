# 📋 Handoff/Onboarding Document: Retirement Calculator App (משכנתה הפוכה)

---

## 1. App Objectives

**Primary Goal:** Interactive Israeli retirement planning simulator comparing 4 investment/asset strategies side-by-side, with focus on inheritance, tax optimization, and late-life liquidity management.

**Core Functionality:**
- Simulate lifetime cashflows (age 18 to 120) under 4 distinct strategies
- Compare strategies on inheritance, taxes, portfolio depletion timeline, and net wealth
- Support Hebrew RTL interface with real Israeli tax rules (תיקון 190, מס 25% ריאלי, הצמדה למדד)
- Real-time browser persistence via URL query parameters
- Reverse mortgage (משכנתה הפוכה) as emergency liquidity tool for Track 4 (rental strategy)

**Key User Problem:** Retirees struggle to compare pension vs. investment returns vs. property rental, especially when facing savings depletion. The app lets them stress-test scenarios and quantify trade-offs (e.g., "If I keep the apartment and rent it, when do I run out of savings? Could RM help?").

---

## 2. Codebase Architecture & Tech Stack

**Stack:**
- **Framework:** Streamlit (Python 3.10+) — RTL-aware
- **UI:** Sidebar expanders (collapsible sections), HTML markdown for tables/tooltips, CSS custom classes
- **Core:** Pure Python — no external simulation engine, all logic inline
- **Locale:** Hebrew (RTL) — text direction, money format (₪), date handling

**Directory Structure:**
```
retirement-calc-app-V-/
├── app.py                        # Main Streamlit entry point
├── simulator_engine.py           # Core monthly cashflow loop (age 18–120)
├── inputs/                       # Input widgets & data collection
│   ├── __init__.py              # Orchestrator — combines all input modules
│   ├── ui_components.py         # Reusable widgets (compact_number_input, tooltips)
│   ├── timeline.py              # Retirement age, check age, inflation
│   ├── wealth.py                # Property, savings, inheritance splits
│   ├── incomes.py               # Pension, work income, national insurance
│   ├── expenses.py              # Annual budget, cost of living
│   ├── amendment_190.py         # Track 1 inputs (pension-based strategy)
│   ├── real_tax_25.py           # Tracks 2 & 3 inputs (investment strategies)
│   └── rental.py                # Track 4 inputs (property rental + RM)
├── reports/                      # Output & visualization
│   ├── graphs.py                # Comparative charts (4-track side-by-side)
│   ├── qa_report.py             # QA card: risk metrics, ranked summary
│   └── qa_summary.py            # Detailed narrative comparison (text blocks)
└── user_defaults.json           # Optional persistent user preferences

**Key File Sizes/Complexity:**
- `simulator_engine.py`: ~450 lines (core logic, all RM calculations)
- `reports/qa_report.py`: ~700 lines (metric calculations, CSS tooltips)
- `inputs/rental.py`: ~200 lines (RM UI, danger table, annuity preview)
- `app.py`: ~195 lines (orchestration, URL persistence, tabs)

---

## 3. Data Models & State

### Session State (Streamlit `st.session_state`)
**Initialized on first page load by `app.py`:**
- `initialized`: Boolean flag — True after first load (prevents re-parsing URL params)
- `sim_results`: Full simulation output (DataFrame + metadata) — WITH RM enabled if user chose
- `sim_results_no_rm`: Parallel simulation with RM disabled — used ONLY for danger table planning
- `last_inputs`: Last set of user inputs that triggered simulation (for change detection)

**Why two simulations?** When RM is active, `sim_results` includes RM cashflows, biasing the depletion hint. `sim_results_no_rm` is a clean baseline.

### URL Query Parameters (Browser Persistence)
- Keys: `saved_slider_*`, `saved_num_*` (auto-prefixed by patched widgets)
- On reload: loaded into `st.session_state` before any UI renders
- User can share a URL with all their settings pre-filled
- Clear button in sidebar resets both URL params and session state

### Core Data: Simulation Output (`sim_results` dict)

**`sim_results["df"]`** — DataFrame (monthly rows, age 18–120)
Each row = one calendar month, columns include:
- `"גיל"` (age, float)
- `"הוצאה נומינלית"`, `"הכנסה נומינלית"` (costs, income in nominal ₪)
- **Track 1 (תיקון 190):** `"צבירה תיקון 190"`, `"מס ששולם 190"`, `"שווי ירושה 190"`
- **Track 2 (25% מס ריאלי):** `"צבירה מסלול ריאלי"`, `"מס ששולם 25"`
- **Track 3 (היברידי):** `"צבירה מסלול היברידי"`, `"מס ששולם היברידי"`
- **Track 4 (שכירות):** `"צבירה מסלול שכירות"`, `"תזרים נטו שכירות"`, `"משיכה מתיק שכירות"`, `"מס רווח הון — משיכה מתיק"`
- **RM columns (if enabled):** `"משכנתה הפוכה — משיכה חודשית"`, `"משכנתה הפוכה — יתרת חוב"`, `"משכנתה הפוכה — הון עצמי"`, `"משכנתה הפוכה — LTV"`

**`sim_results["df_full"]`** — Same as `df`, used in charts and danger-table calculations.

**`sim_results[...]` metadata:**
- Other keys vary by analysis; see `reports/qa_report.py` for full list (ranking scores, P95 ages, etc.)

### Inputs Dictionary (nested structure from `inputs/__init__.py`)
```python
user_inputs = {
    "timeline": {
        "retirement_age": 67,
        "check_age": 90,
        "inflation_rate": 2.0,  # % annual
    },
    "wealth": {
        "existing_savings": 440000,      # ₪ current liquid
        "net_sale": 10000000,            # ₪ property value (if sold)
        "remaining_for_gimel": 5000000,  # ₪ available for pension
        "national_insurance": {...},     # from incomes
    },
    "expenses": {
        "annual_expense_nominal": 250000, # ₪/year today
        "work_income": 0,
        "work_end_age": 67,
    },
    "amendment_190": {
        "desired_pension": 30000,        # ₪/month target
        "securing_years": 20,
        "capital_for_pension": 3000000,
        "net_for_190": 2000000,          # after distributions
        ...
    },
    "real_tax_25": {
        "capital_for_track_2": 4000000,
        "real_annual_return": 5.0,       # % real (inflation-adjusted)
        ...
    },
    "rental": {
        "current_property_value": 10000000,
        "rental_income_monthly": 8000,
        "rental_income_growth_rate": 0.03,
        "rent_paid_monthly": 6000,
        "rent_paid_growth_rate": 0.03,
        "maintenance_early_pct": 0.07,   # % of rental income, first 10 years
        "maintenance_late_pct": 0.12,    # % of rental income, after 10 years
        "rm_enabled": True/False,
        "rm_loan_amount_ils": 500000,    # ₪ user selects upfront
        "rm_annual_rate": 0.055,         # 5.5% fixed
        "rm_start_age": 72,              # when annuity begins
        "rm_life_expectancy_age": 90,    # horizon for annuity calc
        "rm_origination_fee": 0.02,      # 2% one-time on loan
        ...
    },
    "visible_tracks": [1, 2, 3, 4],  # filtered by per-track checkboxes
}
```

### Reverse Mortgage (RM) Model — Key Concepts

**When activated:**
1. User enters desired loan amount (`rm_loan_amount_ils`)
2. At `rm_start_age`, bank calculates fixed monthly annuity:
   ```
   r_m = (1 + annual_rate) ^ (1/12) - 1
   n_m = (life_expectancy - start_age) * 12
   net_loan = loan_amount * (1 - origination_fee)
   annuity = net_loan * r_m / ((1 + r_m)^n_m - 1)
   ```
3. Each month from activation onward:
   - Annuity credited to rental savings
   - Loan balance grows: `balance = (balance + annuity) * (1 + r_m)`
   - Interest accrued = amount needed to reach new balance
4. **Non-recourse:** Equity can go negative; annuity continues (bank absorbs)
5. **No phantom tax:** Gain from RM surplus is not capital gains; basis adjusted downward

**Key constraint:** Maintenance costs are **% of rental income**, not fixed ₪, so they grow naturally with rent.

---

## 4. Coding Standards & Preferences

**Hebrew UI:**
- All strings in Hebrew (RTL)
- Currency: ₪ with format `₪{value:,.0f}`
- Direction: `direction:rtl` in HTML divs
- Emojis: Use sparingly, for section icons (🏦 RM, 🏠 rental, etc.)

**Naming Conventions:**
- Snake case: `rental_income_monthly`, `rm_loan_balance`
- Hebrew column names: stored as-is in DataFrames (e.g., `"צבירה תיקון 190"`)
- Private/internal: prefix with `_` (e.g., `_sim_no_rm`, `_find_threshold_age`)

**Functions & Modularity:**
- Keep input renderers (`render_*_inputs()`) self-contained; return single dict
- Simulators are loops, not recursive — easy to debug month-by-month
- Reports compute metrics on-demand; avoid storing intermediate state in session

**Comments:**
- Only document WHY, not WHAT (code should be self-documenting)
- Flag hidden constraints (e.g., "maintenance is % of income, not fixed ₪")
- Workarounds for bugs warrant comments (e.g., Streamlit RTL quirks)

**No External Libraries Beyond:**
- `streamlit` (UI)
- `pandas` (DataFrames)
- Standard library (json, os, datetime, math)

**Error Handling:**
- Validate at boundaries (user inputs, external data)
- Trust internal code — no defensive try/except for impossible states
- If a field should exist, KeyError is acceptable; use `.get(..., default)` for optional fields

**Testing:**
- No unit tests yet; validation is manual (run app, check charts/tables)
- Use `st.write()` / `st.dataframe()` to inspect intermediate results during dev

---

## 5. Environment & Commands

**Python Version:** 3.10+ (f-strings, walrus operator, dict merge)

**Installation:**
```bash
pip install streamlit pandas
```

**Run the app:**
```bash
streamlit run app.py
```
Opens at `http://localhost:8501` by default.

**Optional: User Defaults**
Create `user_defaults.json` in project root to set baseline inputs:
```json
{
  "timeline": {"retirement_age": 67, "check_age": 90},
  "wealth": {"existing_savings": 440000, ...},
  ...
}
```
Loaded on startup if present.

**Browser Persistence:**
- All inputs auto-saved to URL query params on every change
- Reload URL → all values restored (no manual save needed)
- Share URL with others → they see your exact scenario

**Environment Variables:**
- None required currently
- For production: could add `STREAMLIT_LOGGER_LEVEL=warning` to reduce console noise

**Git Workflow (see "Branching & Versioning" below)**

---

## 6. Branching & Versioning

**Main Branch:** `main` (production-ready)

**Feature Branch:** `claude/reverse-mortgage-track4` (current work)
- Started from main, contains full RM implementation + danger table
- Ready to merge once verified

**Commit Message Format:**
```
Short imperative summary (50 chars max)

Longer explanation if needed (wrapped at ~72 chars).
Explain WHY, not WHAT.

https://claude.ai/code/session_<ID>
```

**No Versioning Tags Yet** — app is internal/experimental.

**Git Workflow:**
1. All changes → feature branch
2. Commit locally, push with `-u origin <branch>`
3. No force-push to main; squash-merge when ready
4. PR review recommended before merging (or manual diff review)

---

## 7. Current State & Next Steps

### ✅ Completed (as of this handoff)
- **RM core logic** (simulator_engine.py):
  - Actuarial annuity calculation
  - Monthly loan balance compounding
  - Interest tracking, equity calculation, LTV display
  - Non-recourse (equity can hit 0, annuity continues)
  - Maintenance as % of rental income (not fixed)
  - Basis adjustment for RM surplus (no phantom tax)

- **RM UI** (inputs/rental.py):
  - Checkbox to enable/disable RM
  - Input fields: loan amount, annual rate, start age, life expectancy, origination fee
  - Live annuity preview & loan summary table
  - **NEW:** Danger table (always visible, before checkbox)
    - Shows savings depletion ages (₪80K, ₪40K, ₪20K) from no-RM simulation
    - Shows cumulative deficit from each threshold to check_age
    - Helps user decide when to activate RM and how large a loan to request

- **Parallel simulations** (app.py):
  - `sim_results` = WITH RM (if enabled)
  - `sim_results_no_rm` = WITHOUT RM (for planning only)
  - Avoids polluting danger table with RM effects

- **Track visibility checkboxes** (inputs/__init__.py):
  - Per-track show/hide buttons
  - Filtered ranking in qa_report.py

- **QA Report enhancements** (reports/qa_report.py):
  - Ranked comparison of visible tracks only
  - CSS tooltip class (`.qa-tip` / `.qa-tiptext`) for hover descriptions
  - RM-aware equity calculations (property - loan balance)

- **QA Summary narrative** (reports/qa_summary.py):
  - Includes RM loan amount and activation age if enabled

### 🔄 In Progress / Considerations
- **Verification:** Run app locally, verify danger table displays correct ages/deficits
- **Edge cases:** What if savings never hit a threshold? (Handled: shows "לא מגיע עד גיל X")
- **Tax interaction:** RM surplus credited to basis — double-check this doesn't cause phantom gains elsewhere

### 📌 Known Limitations / Future Ideas
1. **RM model simplifications:**
   - No variable-rate RM (always fixed)
   - No RM cancellation mid-stream (once activated, runs to life expectancy)
   - No prepayment penalties modeled
   - Assumes non-recourse (Israeli law may vary)

2. **Missing features (out of scope for now):**
   - Google Sheets export (user asked; complex to auto-create sheets)
   - Mobile-optimized layout (Streamlit default is tablet-friendly)
   - Multi-scenario comparison (batch run A vs. B)
   - Historical backtesting (data not available)

3. **UI/UX:**
   - Tooltip `title=` attribute doesn't work in Streamlit — workaround: CSS `.qa-tip` class
   - Hebrew RTL in table headers can be cramped — may need responsive widths

---

## 8. Known Issues & Crucial Context

### ✅ Resolved (from development)
1. **Deficit calculation used wrong simulation** → Fixed: now uses `sim_results_no_rm`
2. **Maintenance costs were % of gross rental, not net** → Fixed: now % of rental income
3. **Phantom capital gains tax on RM** → Fixed: basis adjusted downward when RM surplus credited
4. **Annuity cutoff when equity = 0** → Fixed: removed condition, annuity runs to life expectancy
5. **UnboundLocalError in qa_report.py** → Fixed: pre-compute rental cashflow values from dataframe row
6. **Tooltip hover broken** → Fixed: use CSS `.qa-tip` class instead of `title=` attribute

### 🟡 Current Gotchas / Constraints
1. **Two simulations run on every update** → Doubles computation time; acceptable for ~100-month lifespan
2. **Maintenance early/late split happens at rental_start_age + 10 years** → Not age 75 or absolute, but relative to when rental income begins
3. **Inflation applied to ALL nominal values** → Means maintenance costs grow both from CPI and rental income growth
4. **RM interest is compounding monthly** → Not paid out, so loan balance accelerates over time
5. **Property value fixed** → Appreciation rate applies to `property_rental_value` column in DF, but loan balance is separate (equity = property_value - balance)
6. **Non-recourse assumption** → Israeli law may require heir to cover shortfall; model assumes bank eats it

### ⚠️ Testing Checklist (Before Production)
- [ ] Danger table shows correct ages for each threshold (₪80K, ₪40K, ₪20K)
- [ ] Cumulative deficit matches sum of negative cashflow rows
- [ ] RM annuity calculates correctly (use online Israeli RM calculator for spot-check)
- [ ] Equity never exceeds property value (LTV capped at 100%)
- [ ] Loan balance compounds correctly (monthly interest accumulates)
- [ ] Maintenance switches from early to late % on schedule
- [ ] No NaN or inf values in output (watch for division by zero)
- [ ] Disabling RM removes all RM columns from track 4 table
- [ ] Hiding a track updates ranking correctly

### 🔐 Security / Sensitive Data
- All inputs stored in URL → user can bookmark/share, but **no server-side persistence**
- No user authentication; no backend database
- Safe to run locally or on secure intranet
- No API keys or secrets in code

---

## Summary for Next Session

**What to do first:**
1. Run `streamlit run app.py`
2. Fill in inputs (use defaults or load `user_defaults.json`)
3. Go to Track 4 (rental) section
4. Verify **danger table** shows before the "הפעל משכנתה הפוכה" checkbox
5. Verify table shows ages at ₪80K, ₪40K, ₪20K (or "לא מגיע" if savings never deplete)
6. Enable RM, set loan amount, run simulation
7. Check Track 4 table for new RM columns (annuity, balance, equity, LTV)
8. Review QA report — verify RM activates at correct age and doesn't break ranking

**If issues arise:**
- Check `sim_results_no_rm` exists in session state (run at least one simulation)
- Verify `df_full` has all expected columns (especially `"תזרים נטו שכירות"`)
- Inspect monthly interest calculation: `interest = balance - balance/(1+r_m)`
- Search code for `TODO` / `FIXME` comments (none expected, but check)

**How to extend:**
- Add new track? Create `inputs/new_track.py`, wire in `__init__.py`, add columns to simulator loop
- Add new chart? Create `reports/new_chart.py`, import in `app.py`, add to tabs
- Change RM model? Update `simulator_engine.py` section "Reverse Mortgage (RM)" (lines ~64–220)
- Change RM UI? Update `inputs/rental.py` (lines ~71–195)

---

**Last Updated:** June 2, 2026  
**Branch:** `claude/reverse-mortgage-track4`  
**Commit:** `bd63464` (danger table added)

