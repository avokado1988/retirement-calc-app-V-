import streamlit as st
import pandas as pd
from inputs.ui_components import (
    format_shekel, wrap_html_style,
    get_withdrawal_style, get_400_rule_style, get_emergency_style,
    get_larger_portfolio_style, get_resiliency_style,
    get_preservation_pct_style, get_boolean_style,
    DEFAULTS
)

def render_qa_section(results, user_inputs):
    st.markdown("""
        <style>
        .styled-table { width: 100% !important; direction: rtl !important; text-align: right !important; border-collapse: collapse; margin: 8px 0; font-family: sans-serif; }
        .styled-table thead th { background-color: #eef0f7; color: #1a1a2e; text-align: right !important; padding: 10px 12px !important; font-weight: 700; border-bottom: 2px solid #d0d4e8; font-size: 0.9em; }
        .styled-table td { padding: 8px 12px !important; text-align: right !important; border-bottom: 1px solid #eef; color: #1a1a2e; }
        .styled-table tbody th { background-color: #f8f9fc; color: #555; font-weight: 600; padding: 8px 12px !important; text-align: right !important; border-bottom: 1px solid #eef; border-left: 2px solid #d0d4e8; font-size: 0.88em; }
        [data-testid="stExpander"] summary { direction: rtl !important; text-align: right !important; }
        [data-testid="stExpander"] summary p { direction: rtl !important; text-align: right !important; }
        .qa-tip { position: relative; display: inline-block; cursor: help; color: #7a9cc8; font-size: 0.85em; vertical-align: middle; }
        .qa-tip .qa-tiptext { visibility: hidden; opacity: 0; background: #2c3e50; color: #fff; font-size: 0.8em; font-weight: 400; border-radius: 6px; padding: 6px 10px; position: absolute; z-index: 9999; bottom: 130%; right: 0; width: 240px; text-align: right; direction: rtl; transition: opacity 0.15s; pointer-events: none; box-shadow: 0 2px 8px rgba(0,0,0,0.25); line-height: 1.4; }
        .qa-tip:hover .qa-tiptext { visibility: visible; opacity: 1; }
        </style>
    """, unsafe_allow_html=True)

    df_full = results["df_full"]
    timeline = user_inputs.get("timeline", {})
    wealth = user_inputs.get("wealth", {})
    real_tax_25 = user_inputs.get("real_tax_25", {})

    start_age = float(timeline.get("start_age", 65.5))
    check_age = float(timeline.get("check_age", DEFAULTS["check_age"]))
    retire_age = float(timeline.get("retirement_age", start_age))

    rental_inputs = user_inputs.get("rental", {})
    baseline_capital = float(real_tax_25.get("net_for_real_pathway") or 3340000)
    emergency_fund = float(wealth.get("emergency_fund", 0))
    property_value_start = float(wealth.get("new_apartment_cost", 0))
    appreciation_rate = float(wealth.get("property_appreciation", 0))
    rental_property_start = float(rental_inputs.get("current_property_value", wealth.get("net_sale", property_value_start)))
    # Rented property uses its own (lower) appreciation rate — pricey homes climb slower
    rental_appreciation_rate = float(rental_inputs.get("rental_property_appreciation", 0.015))

    def get_row(target_age):
        sub = df_full[df_full["גיל"] >= target_age]
        return sub.iloc[0] if not sub.empty else df_full.iloc[-1]

    row_retire = get_row(retire_age)
    row_check = get_row(check_age)

    property_value_retire = float(row_retire.get("שווי נדלן", property_value_start))
    property_value_check = float(row_check.get("שווי נדלן", property_value_start))
    # Read rental property value from engine (monthly-compounded) instead of recalculating with annual rate
    rental_prop_retire = float(row_retire.get("שווי נדלן מסלול 4", rental_property_start))
    rental_prop_check = float(row_check.get("שווי נדלן מסלול 4", rental_property_start))

    # -------------------------------------------------------
    # Extract values at retirement
    # -------------------------------------------------------
    exp_retire = float(row_retire["הוצאה נומינלית"])
    base_income_retire = float(row_retire["הכנסה נומינלית"])
    pension_retire = float(row_retire.get("הכנסה מקצבה מזערית", 0.0))
    pension_asset_retire = float(row_retire.get("ערך קצבה נותר", 0.0))

    b190_r = float(row_retire["צבירה תיקון 190"])
    b25_r = float(row_retire["צבירה מסלול ריאלי"])
    bh_r = float(row_retire["צבירה מסלול היברידי"])
    br_r = float(row_retire["צבירה מסלול שכירות"])

    rent_paid_r = float(row_retire.get("הוצאת שכירות", 0.0))
    net_rental_r = float(row_retire.get("הכנסת שכירות נטו", 0.0))
    maintenance_r = float(row_retire.get("הוצאת תחזוקה", 0.0))
    # Include RM annuity in cashflow — the engine uses cashflow_with_rm for actual decisions;
    # rental_cashflow_net alone understates income when RM is active.
    _cf_retire_raw = float(row_retire.get("תזרים נטו שכירות", 0.0)) + float(row_retire.get("משכנתה הפוכה — משיכה חודשית", 0.0))
    _cf_check_raw  = float(row_check.get("תזרים נטו שכירות", 0.0))  + float(row_check.get("משכנתה הפוכה — משיכה חודשית", 0.0))

    nn_190_r = max(0.0, exp_retire - (base_income_retire + pension_retire))
    nn_25_r = max(0.0, exp_retire - base_income_retire)
    nn_h_r = nn_190_r
    nn_rent_r = max(0.0, -_cf_retire_raw)  # full cashflow incl. maintenance

    def rule400(bal, nn): return f"{bal / (nn * 400):.2f}" if nn > 0 else "∞"
    def emer(nn): return f"{emergency_fund / (nn * 12):.1f}" if nn > 0 else "∞"
    def wpct(nn, bal): return (nn * 12) / bal * 100 if bal > 0 else 0.0
    def fmt_withdrawal(nn):
        return format_shekel(int(nn)) if nn == 0 else f"{format_shekel(int(nn))}−"
    def fmt_with_delta(val, baseline, pension_component=None):
        if baseline <= 0: return format_shekel(int(val))
        delta_pct = (val - baseline) / baseline * 100
        arrow = "↑" if delta_pct >= 0 else "↓"
        if delta_pct > 20:
            color = "#1a7a3a"
        elif delta_pct >= 0:
            color = "#2e7d32"
        else:
            color = "#c0392b"
        sign = "+" if delta_pct >= 0 else ""
        pension_note = ""
        if pension_component is not None:
            pension_note = f"<br/><span style='color:#999; font-size:0.78em;'>מתוכם {format_shekel(int(pension_component))} ערך קצבה</span>"
        return f"{format_shekel(int(val))}<br/><span style='color:{color}; font-size:0.85em;'>({arrow}{sign}{delta_pct:.1f}%)</span>{pension_note}"

    def fmt_with_pension_note(val, pension_component=None):
        base = format_shekel(int(val))
        if pension_component is not None:
            note = f"<br/><span style='color:#999; font-size:0.78em;'>מתוכם {format_shekel(int(pension_component))} ערך קצבה</span>"
            return base + note
        return base

    pct_190_r = wpct(nn_190_r, b190_r)
    pct_25_r = wpct(nn_25_r, b25_r)
    pct_h_r = wpct(nn_h_r, bh_r)
    pct_rent_r = wpct(nn_rent_r, br_r)

    rule400_190_r = rule400(b190_r, nn_190_r)
    rule400_25_r = rule400(b25_r, nn_25_r)
    rule400_h_r = rule400(bh_r, nn_h_r)

    inherit_190_r = b190_r + pension_asset_retire
    inherit_h_r = bh_r + pension_asset_retire

    # Track 4: property equity = property value minus RM loan (0 when RM not active)
    rm_equity_retire = float(row_retire.get("משכנתה הפוכה — הון עצמי", rental_prop_retire))
    rm_equity_check  = float(row_check.get("משכנתה הפוכה — הון עצמי", rental_prop_check))

    tw_190_r = b190_r + pension_asset_retire + property_value_retire + emergency_fund
    tw_25_r = b25_r + property_value_retire + emergency_fund
    tw_h_r = bh_r + pension_asset_retire + property_value_retire + emergency_fund
    tw_rent_r = br_r + rm_equity_retire  # net equity, not gross property value

    # -------------------------------------------------------
    # Extract values at check_age
    # -------------------------------------------------------
    exp_check = float(row_check["הוצאה נומינלית"])
    base_income_check = float(row_check["הכנסה נומינלית"])
    pension_check = float(row_check.get("הכנסה מקצבה מזערית", 0.0))
    pension_asset_check = float(row_check.get("ערך קצבה נותר", 0.0))

    b190_c = float(row_check["צבירה תיקון 190"])
    b25_c = float(row_check["צבירה מסלול ריאלי"])
    bh_c = float(row_check["צבירה מסלול היברידי"])
    br_c = float(row_check["צבירה מסלול שכירות"])
    blev_c = float(row_check.get("צבירה מסלול מינוף", 0.0))
    loan_debt_c = float(row_check.get("הלוואת בלון — יתרת חוב", 0.0))

    rent_paid_c = float(row_check.get("הוצאת שכירות", 0.0))
    net_rental_c = float(row_check.get("הכנסת שכירות נטו", 0.0))
    maintenance_c = float(row_check.get("הוצאת תחזוקה", 0.0))

    nn_190_c = max(0.0, exp_check - (base_income_check + pension_check))
    nn_25_c = max(0.0, exp_check - base_income_check)
    nn_h_c = nn_190_c
    nn_rent_c = max(0.0, -_cf_check_raw)  # full cashflow incl. maintenance

    pct_190_c = wpct(nn_190_c, b190_c)
    pct_25_c = wpct(nn_25_c, b25_c)
    pct_h_c = wpct(nn_h_c, bh_c)
    pct_rent_c = wpct(nn_rent_c, br_c)

    inherit_190_c = b190_c + pension_asset_check
    inherit_h_c = bh_c + pension_asset_check

    tw_190_c = b190_c + pension_asset_check + property_value_check + emergency_fund
    tw_25_c = b25_c + property_value_check + emergency_fund
    tw_h_c = bh_c + pension_asset_check + property_value_check + emergency_fund
    tw_rent_c = br_c + rm_equity_check  # net equity, not gross property value

    # -------------------------------------------------------
    # Extract values at age 102
    # -------------------------------------------------------
    df_102 = df_full[df_full["גיל"] >= 102.0]
    row_102 = df_102.iloc[0] if not df_102.empty else df_full.iloc[-1]
    b190_102 = float(row_102["צבירה תיקון 190"])
    b25_102 = float(row_102["צבירה מסלול ריאלי"])
    bh_102 = float(row_102["צבירה מסלול היברידי"])
    br_102 = float(row_102["צבירה מסלול שכירות"])

    # -------------------------------------------------------
    # Extract values at age 100 (ranking / contest reference age)
    # -------------------------------------------------------
    df_100 = df_full[df_full["גיל"] >= 100.0]
    row_100 = df_100.iloc[0] if not df_100.empty else df_full.iloc[-1]
    b190_100 = float(row_100["צבירה תיקון 190"])
    b25_100  = float(row_100["צבירה מסלול ריאלי"])
    bh_100   = float(row_100["צבירה מסלול היברידי"])
    br_100   = float(row_100["צבירה מסלול שכירות"])
    blev_100 = float(row_100.get("צבירה מסלול מינוף", 0.0))
    loan_debt_100 = float(row_100.get("הלוואת בלון — יתרת חוב", 0.0))

    # -------------------------------------------------------
    # Scans: resiliency and recovery ages
    # -------------------------------------------------------
    def find_empty_age(col):
        for idx in range(len(df_full)):
            if float(df_full.iloc[idx][col]) <= 0:
                return float(df_full.iloc[idx]["גיל"])
        return 120.0

    def find_recovery_age(col):
        for idx in range(len(df_full)):
            if df_full.iloc[idx][col] > baseline_capital and df_full.iloc[idx]["גיל"] > start_age:
                return f"{df_full.iloc[idx]['גיל']:.1f}"
        return "לא עובר"

    def find_peak_age(col):
        """Age at which the portfolio reaches its maximum — after this it only declines."""
        peak_idx = df_full[col].idxmax()
        peak_age = float(df_full.loc[peak_idx, "גיל"])
        # If peak is within 1 year of end of simulation → portfolio never erodes
        if peak_age >= 104.0:
            return "<span style='color:#1a7a3a;font-weight:700;'>✅ לא נשחק (צומח לאורך כל החיים)</span>"
        if peak_age <= retire_age + 0.5:
            return f"<span style='color:#888;'>גיל {retire_age:.0f} (יורד מהרגע הראשון)</span>"
        color = "#1a7a3a" if peak_age >= 85 else ("#b84c00" if peak_age >= 75 else "#b71c1c")
        return f"<span style='color:{color};font-weight:700;'>גיל {peak_age:.0f}</span>"

    empty_190 = find_empty_age("צבירה תיקון 190")
    empty_25 = find_empty_age("צבירה מסלול ריאלי")
    empty_h = find_empty_age("צבירה מסלול היברידי")
    empty_lev = find_empty_age("צבירה מסלול מינוף") if "צבירה מסלול מינוף" in df_full.columns else 120.0
    # Track 4: the automatic RM floors the liquid portfolio, so it "never empties"
    # by balance alone. Its true failure point is the first month the RM could
    # NOT cover the deficit (LTV cap hit) — that is when the plan actually breaks.
    empty_r = find_empty_age("צבירה מסלול שכירות")
    if "משכנתה הפוכה — גרעון לא מכוסה" in df_full.columns:
        _unc_rows = df_full[df_full["משכנתה הפוכה — גרעון לא מכוסה"] > 1.0]
        if not _unc_rows.empty:
            empty_r = float(_unc_rows.iloc[0]["גיל"])

    recovery_190 = find_recovery_age("צבירה תיקון 190")
    recovery_25 = find_recovery_age("צבירה מסלול ריאלי")
    recovery_h = find_recovery_age("צבירה מסלול היברידי")
    recovery_r = find_recovery_age("צבירה מסלול שכירות")

    peak_190 = find_peak_age("צבירה תיקון 190")
    peak_25 = find_peak_age("צבירה מסלול ריאלי")
    peak_h = find_peak_age("צבירה מסלול היברידי")
    peak_r = find_peak_age("צבירה מסלול שכירות")

    # -------------------------------------------------------
    # Rental cash flow analysis
    # -------------------------------------------------------
    # Monthly surplus pre-computed by engine; alias for compatibility
    # True cashflow = net rental + RM annuity (mirrors cashflow_with_rm in the engine)
    _rm_annuity_col = df_full["משכנתה הפוכה — משיכה חודשית"] if "משכנתה הפוכה — משיכה חודשית" in df_full.columns else 0
    df_full["rental_cashflow"] = df_full["תזרים נטו שכירות"] + _rm_annuity_col

    row_ret_r = df_full[df_full["גיל"] >= retire_age].iloc[0] if not df_full[df_full["גיל"] >= retire_age].empty else df_full.iloc[0]
    rental_cashflow_at_retire = float(row_ret_r["rental_cashflow"])

    # Cash flow at the checked age (גיל נבדק) — so the deficit is visible there too
    row_check_r = df_full[df_full["גיל"] >= check_age].iloc[0] if not df_full[df_full["גיל"] >= check_age].empty else df_full.iloc[-1]
    rental_cashflow_at_check = float(row_check_r["rental_cashflow"])

    # Find age cash flow first turns negative (after retirement)
    df_after_retire = df_full[df_full["גיל"] >= retire_age]
    negative_rows = df_after_retire[df_after_retire["rental_cashflow"] < 0]
    rental_flip_age = float(negative_rows.iloc[0]["גיל"]) if not negative_rows.empty else None

    rental_always_positive = rental_flip_age is None
    rental_starts_negative = rental_cashflow_at_retire < 0

    # -------------------------------------------------------
    # Reverse mortgage metrics (track 4) — fully automatic.
    # RM "activates" whenever the sim actually took on debt (portfolio hit the
    # cash floor with a remaining deficit).
    # -------------------------------------------------------
    _rm_debt_col = "משכנתה הפוכה — יתרת חוב"
    rm_activated = (_rm_debt_col in df_full.columns) and bool((df_full[_rm_debt_col] > 0).any())
    rm_activation_age = None
    rm_debt_at_check = 0.0
    rm_equity_at_check = None
    rm_total_interest = None
    rm_underwater_age = None
    rm_uncovered_total = 0.0
    rm_track4_not_viable = False

    if rm_activated:
        rm_active_rows = df_full[df_full[_rm_debt_col] > 0]
        rm_activation_age = float(rm_active_rows.iloc[0]["גיל"])
        row_check_rm = df_full[df_full["גיל"] >= check_age].iloc[0] if not df_full[df_full["גיל"] >= check_age].empty else df_full.iloc[-1]
        rm_debt_at_check = float(row_check_rm.get(_rm_debt_col, 0.0))
        rm_equity_at_check = float(row_check_rm.get("משכנתה הפוכה — הון עצמי", 0.0))
        rm_total_interest = float(df_full["משכנתה הפוכה — ריבית חודשית"].sum())
        underwater_rows = df_full[(df_full["גיל"] >= retire_age) & (df_full["משכנתה הפוכה — הון עצמי"] <= 0)]
        if not underwater_rows.empty:
            rm_underwater_age = float(underwater_rows.iloc[0]["גיל"])

    # Track 4 not viable if the RM couldn't cover the deficit up to check_age (LTV cap hit)
    if "משכנתה הפוכה — גרעון לא מכוסה" in df_full.columns:
        rm_uncovered_total = float(df_full[df_full["גיל"] <= check_age]["משכנתה הפוכה — גרעון לא מכוסה"].sum())
        rm_track4_not_viable = rm_uncovered_total > 1.0

    # Legacy aliases still referenced downstream
    rm_enabled_flag = rm_activated
    _rm_start_age_val = rm_activation_age if rm_activation_age is not None else retire_age
    _rental_flip_is_pre_rm = False
    _flip_recovers_with_rm = False

    # -------------------------------------------------------
    # Cumulative deficit — how much external support needed
    # -------------------------------------------------------
    # Tracks 1-3: sum of monthly shortfalls AFTER portfolio hits zero, up to check_age
    df_190_empty = df_full[(df_full["צבירה תיקון 190"] <= 0) & (df_full["גיל"] <= check_age)]
    cum_deficit_190 = float((df_190_empty["הוצאה נומינלית"] - df_190_empty["הכנסה נומינלית"] - df_190_empty["הכנסה מקצבה מזערית"]).clip(lower=0).sum())
    months_deficit_190 = len(df_190_empty)

    df_25_empty = df_full[(df_full["צבירה מסלול ריאלי"] <= 0) & (df_full["גיל"] <= check_age)]
    cum_deficit_25 = float((df_25_empty["הוצאה נומינלית"] - df_25_empty["הכנסה נומינלית"]).clip(lower=0).sum())
    months_deficit_25 = len(df_25_empty)

    df_h_empty = df_full[(df_full["צבירה מסלול היברידי"] <= 0) & (df_full["גיל"] <= check_age)]
    cum_deficit_h = float((df_h_empty["הוצאה נומינלית"] - df_h_empty["הכנסה נומינלית"] - df_h_empty["הכנסה מקצבה מזערית"]).clip(lower=0).sum())
    months_deficit_h = len(df_h_empty)

    # Track 4: only count deficit after savings are depleted; cashflow column already includes maintenance
    df_r_neg = df_full[(df_full["צבירה מסלול שכירות"] <= 0) & (df_full["גיל"] >= retire_age) & (df_full["גיל"] <= check_age)]
    cum_deficit_r = float(df_r_neg["rental_cashflow"].clip(upper=0).abs().sum())
    months_deficit_r = len(df_r_neg)

    def fmt_cum_deficit(total, months):
        if total <= 0 or months == 0:
            return "<span style='color:#1a7a3a;font-weight:700;'>✅ אין גירעון</span>"
        monthly_avg = total / months
        yrs = months / 12
        return (f"<span style='color:#c0392b;font-weight:700;'>{format_shekel(int(total))}</span>"
                f"<br/><span style='color:#888;font-size:0.75em;'>על פני {yrs:.1f} שנים</span>"
                f"<br/><span style='color:#c0392b;font-size:0.78em;'>≈ {format_shekel(int(monthly_avg))}/חודש</span>")


    # -------------------------------------------------------
    # Balanced Stress-Test: Track 4 vs Track 1 at age 100 (ranking reference)
    # S4   = portfolio_rental + (property_rental × 0.85 − 500K) − rm_debt
    # S190 = portfolio_190 + pension_asset + property × 1.05 + emergency
    # Δ > 0 → track 4 wins even under stress
    # -------------------------------------------------------
    _rm_debt_100_st   = float(row_100.get("משכנתה הפוכה — יתרת חוב", 0.0))
    _prop_100_r_st    = float(row_100.get("שווי נדלן מסלול 4", rental_property_start))
    _prop_100_own_st  = float(row_100.get("שווי נדלן", property_value_start))
    _pension_100_st   = float(row_100.get("ערך קצבה נותר", 0.0))

    # --- Future betterment tax (מס שבח) on the kept property — track 4 only ---
    # Behind-the-scenes estimate, no user fields. Calibrated to the owner's
    # tax-advisor figure: base ₪2M bought 2006, linear pre-2014 exemption, 25%
    # on the real (inflation-indexed) gain, with a calibration factor so that
    # today's tax equals the ~₪900k the advisor quoted at today's value.
    import datetime as _dt
    _TAX_BASE, _TAX_YEAR, _TAX_ANCHOR, _TAX_RATE, _LINEAR_YEAR = 2_000_000, 2006, 900_000, 0.25, 2014
    _tax_infl = float(user_inputs.get("expenses", {}).get("expected_inflation", 0.023))
    _now_year = _dt.datetime.now().year

    def _betterment_raw(value, sale_year):
        yh = max(1, sale_year - _TAX_YEAR)
        base_idx = _TAX_BASE * (1 + _tax_infl) ** yh
        real_gain = max(0.0, value - base_idx)
        taxable_frac = max(0.0, yh - max(0, _LINEAR_YEAR - _TAX_YEAR)) / yh
        return _TAX_RATE * real_gain * taxable_frac

    _raw_today = _betterment_raw(rental_property_start, _now_year)
    _tax_k = (_TAX_ANCHOR / _raw_today) if _raw_today > 0 else 0.0
    property_tax_100   = _tax_k * _betterment_raw(_prop_100_r_st, _now_year + max(0, int(round(100 - start_age))))
    property_tax_check = _tax_k * _betterment_raw(rental_prop_check, _now_year + int(round(check_age - start_age)))

    S4_stress   = br_100 + (_prop_100_r_st - property_tax_100) - _rm_debt_100_st
    S190_stress = b190_100 + _pension_100_st + _prop_100_own_st * 1.05 + emergency_fund
    delta_stress = S4_stress - S190_stress
    track4_wins_stress = delta_stress > 0

    # -------------------------------------------------------
    # Resilience flags — does each track's liquid portfolio last through check_age?
    # -------------------------------------------------------

    # =======================================================================
    # Wealth at 100 — two distinct concepts, kept separate on purpose:
    #   (a) LIQUID portfolio  → drives health/resilience (can it fund life?)
    #   (b) TOTAL net worth    → the bottom line shown on cards (what am I worth?)
    #   (c) STRESS-adjusted    → risk-aware total used for scoring the winner
    # -----------------------------------------------------------------------
    prop_100_rental   = _prop_100_r_st
    rm_debt_100       = _rm_debt_100_st
    prop_100_own      = _prop_100_own_st
    pension_asset_100 = _pension_100_st

    # (b) Total net worth at 100 — liquid + real estate (− RM debt for track 4)
    total_net_100_190    = b190_100 + prop_100_own
    total_net_100_25     = b25_100  + prop_100_own
    total_net_100_h      = bh_100   + prop_100_own
    total_net_100_rental = br_100   + prop_100_rental - rm_debt_100

    liquid_100_by_track = {1: b190_100, 2: b25_100, 3: bh_100, 4: br_100}
    total_100_by_track  = {1: total_net_100_190, 2: total_net_100_25,
                           3: total_net_100_h,   4: total_net_100_rental}

    # Per-track breakdown dicts (used in card display)
    _fin_port_100 = {1: b190_100, 2: b25_100, 3: bh_100, 4: br_100}
    _prop_net_100 = {
        1: prop_100_own, 2: prop_100_own, 3: prop_100_own,
        4: max(0.0, prop_100_rental - rm_debt_100),
    }

    # Starting total net worth per track — the apples-to-apples baseline for
    # the "vs starting capital" comparison (each track vs where IT began).
    net_for_rental_start = float(rental_inputs.get("net_for_rental", 0.0))
    start_total_123 = baseline_capital + property_value_start + emergency_fund
    start_total_4   = net_for_rental_start + rental_property_start
    start_total_by_track = {1: start_total_123, 2: start_total_123,
                            3: start_total_123, 4: start_total_4}

    # sa_100: stress-adjusted net worth at age 100 — primary ranking metric
    # Kids-help returns as a growing family asset in the sell-and-invest tracks
    # (1-3), where the gift is actually made and compounds in the children's
    # hands. It is counted both in the ranking metric below and in the cards.
    _kids_help = float(wealth.get("kids_help", 0.0))
    _kids_growth = float(wealth.get("kids_help_growth", 0.05))
    _kids_grown = _kids_help * (1 + _kids_growth) ** max(0.0, check_age - start_age)
    kids_asset_check = {1: _kids_grown, 2: _kids_grown, 3: _kids_grown, 4: 0.0, 5: _kids_grown}

    sa_100 = {
        1: b190_100 + _pension_100_st + _prop_100_own_st + emergency_fund + kids_asset_check[1],
        2: b25_100  + _prop_100_own_st + emergency_fund + kids_asset_check[2],
        3: bh_100   + _pension_100_st + _prop_100_own_st + emergency_fund + kids_asset_check[3],
        4: br_100   + max(0.0, _prop_100_r_st - _rm_debt_100_st - property_tax_100) + kids_asset_check[4],
        5: blev_100 + _pension_100_st + _prop_100_own_st + emergency_fund - loan_debt_100 + kids_asset_check[5],
    }

    husn_190 = empty_190 >= check_age
    husn_25  = empty_25  >= check_age
    husn_h   = empty_h   >= check_age
    husn_r   = empty_r   >= check_age
    husn_lev = empty_lev >= check_age

    # Ranking metric: stress-adjusted net worth at age 100 (contest reference age).
    # Pension tracks (1, 3) get a +1 tie-break — guaranteed income continues past 100.
    _sa_rank = {
        1: sa_100[1] + 1,
        2: sa_100[2],
        3: sa_100[3] + 1,
        4: sa_100[4],
        5: sa_100[5] + 1,
    }


    track_pros_cons = {
        1: {
            "name": "190 + קצבה מזערית",
            "pro1": "קצבה מובטחת לכל החיים — גם בגיל 105 הכסף לא נגמר. ביטוח אריכות ימים.",
            "pro2": "מיסוי נמוך — 15% נומינלי בלבד",
            "con1": "פחות גמיש — לא ניתן לשבור את הקצבה לצורך הוצאה גדולה",
            "con2": "דורש הון גדול — צריך לפחות ₪1M+ לקצבה משמעותית",
        },
        2: {
            "name": "25% ריאלי (ללא קצבה)",
            "pro1": "כל הכסף נזיל — ניתן למשוך כל סכום בכל עת, ירושה מקסימלית",
            "pro2": "כל ההון עובד בשוק — ללא כיסוח לקצבה",
            "con1": "אין גיבוי לאריכות ימים — אם הכסף ייגמר בגיל 92 אין עוד מקורות",
            "con2": "תלוי לחלוטין בביצועי השוק",
        },
        3: {
            "name": "25% ריאלי + קצבה מזערית",
            "pro1": "שילוב קצבה קטנה ונזילות — רצפת ביטחון עם יכולת תמרון",
            "pro2": "מאזן בין ביטחון וגמישות",
            "con1": "מורכב — טעות במקדם ההמרה גוררת הפסד שקשה להחזיר",
            "con2": "הון נזיל קטן יותר ממסלול ריאלי — פחות ירושה",
        },
        4: {
            "name": "שכירות",
            "pro1": "הדירה נשמרת ועולה בערכה עם הזמן",
            "pro2": 'שכ"ד מכסה חלק מהוצאות — פחות תלות בתיק',
            "con1": 'הון נזיל קטן מאוד — כמעט כל הכסף כלוא בנדל"ן',
            "con2": "שוכר לא תמיד מגיע — תיקונים, ריקנות, ועד בית בגיל מבוגר",
        },
        5: {
            "name": "מינוף (הלוואת בלון)",
            "pro1": "התיק מתחיל גדול — כל כסף הדירה נשאר מושקע ועובד בשוק",
            "pro2": "ארביטראז׳ — התיק צומח מהר יותר מריבית ההלוואה",
            "con1": "מסוכן — מפולת עלולה להפעיל דרישת ביטחונות ומכירה בהפסד",
            "con2": "החוב תופח בריבית דריבית ונפרע מהעיזבון",
        },
    }

    visible_tracks = set(user_inputs.get("visible_tracks", [1, 2, 3, 4, 5]))
    if not visible_tracks:  # safety: show all if none selected
        visible_tracks = {1, 2, 3, 4, 5}

    # Preservation measured at the checked age and fair to pension tracks:
    # each track keeps its remaining annuity value (pension tracks) and is
    # compared to its OWN starting capital — not track 2's full liquid pot.
    _start_cap = {
        1: baseline_capital, 2: baseline_capital, 3: baseline_capital,
        4: (net_for_rental_start if net_for_rental_start > 0 else baseline_capital),
        5: baseline_capital,
    }
    # Track 5 economic value is net of the loan debt (leverage nets to zero at start)
    _econ_check = {1: inherit_190_c, 2: b25_c, 3: inherit_h_c, 4: br_c,
                   5: blev_c + pension_asset_check - loan_debt_c}
    preservation_ratio = {
        t: (_econ_check[t] / _start_cap[t]) if _start_cap[t] > 0 else 0.0
        for t in (1, 2, 3, 4, 5)
    }

    # 4th field = preservation ratio at check_age (drives the health badge).
    tracks_exec = [
        (1, _sa_rank[1], empty_190, preservation_ratio[1], husn_190),
        (2, _sa_rank[2], empty_25,  preservation_ratio[2], husn_25),
        (3, _sa_rank[3], empty_h,   preservation_ratio[3], husn_h),
        (4, _sa_rank[4], empty_r,   preservation_ratio[4], husn_r),
        (5, _sa_rank[5], empty_lev, preservation_ratio[5], husn_lev),
    ]

    # -------------------------------------------------------
    # Rank: sort by score desc, lower track_id wins ties; filter hidden tracks
    # -------------------------------------------------------
    sorted_by_score = sorted(tracks_exec, key=lambda x: (-x[1], x[0]))

    # When both track 1 (190) and track 4 (rental) are visible, the stress test
    # decides their relative rank — not the score.  All other tracks stay sorted by score.
    if 1 in visible_tracks and 4 in visible_tracks:
        idx1 = next((i for i, t in enumerate(sorted_by_score) if t[0] == 1), None)
        idx4 = next((i for i, t in enumerate(sorted_by_score) if t[0] == 4), None)
        if idx1 is not None and idx4 is not None:
            stress_says_4_first = track4_wins_stress
            currently_4_first   = idx4 < idx1
            if stress_says_4_first != currently_4_first:
                lst = list(sorted_by_score)
                lst[idx1], lst[idx4] = lst[idx4], lst[idx1]
                sorted_by_score = lst

    ranked_order = [
        (i + 1, tid, sc, ea, p95, husn)
        for i, (tid, sc, ea, p95, husn) in enumerate(sorted_by_score)
        if tid in visible_tracks
    ]
    rank_for_track = {tid: rank for rank, tid, *_ in ranked_order}

    TRACK_NAMES = {
        1: "190 + קצבה מזערית",
        2: "25% ריאלי (ללא קצבה)",
        3: "25% ריאלי + קצבה מזערית",
        4: "שכירות",
        5: "מינוף (הלוואת בלון)",
    }

    # -------------------------------------------------------
    # Health model, judged against the user's checked age (check_age):
    #   • resilient  = the liquid portfolio funds life through check_age
    #   • preserving = keeps >=90% of its OWN starting capital (pension
    #     tracks count their remaining annuity value) at check_age
    # A track is "recommended" if it is resilient — funding life through
    # the horizon you chose. Preservation only upgrades the badge to 🟢.
    # -------------------------------------------------------
    def track_health(empty_age, preservation):
        is_resilient = empty_age >= check_age
        is_preserving = preservation >= 0.90
        is_healthy = is_resilient and is_preserving
        return is_resilient, is_preserving, is_healthy

    # A recommended track exists if the top track is resilient — i.e. its
    # money lasts through check_age. Depleting before then = no winner.
    _top_empty = sorted_by_score[0][2]
    _top_pres = sorted_by_score[0][3]
    _top_resilient, _top_preserving, _top_healthy = track_health(_top_empty, _top_pres)
    has_winner = _top_resilient

    RANK_CFG = {
        1: {"bg": "#FFFCE8",
            "border": "#D4A800",
            "th_bg": "#FFF3B0",
            "col_bg": "#FFFCE8",
            "badge": "🏆",
            "label": "המסלול המומלץ" if has_winner else "מקום ראשון",
            "rank_color": "#B8860B",
            "health_bg": "#e8f8ee", "health_color": "#1a7a3a"},
        2: {"bg": "#F6F7F8", "border": "#8A9BA8", "th_bg": "#E8ECF0", "col_bg": "#F6F7F8",
            "badge": "🥈", "label": "מקום שני", "rank_color": "#5A6E7A",
            "health_bg": "#e8f8ee", "health_color": "#1a7a3a"},
        3: {"bg": "#FBF5EE", "border": "#A0693A", "th_bg": "#F2E4D4", "col_bg": "#FBF5EE",
            "badge": "🥉", "label": "מקום שלישי", "rank_color": "#7D4E28",
            "health_bg": "#fffbe6", "health_color": "#856400"},
        4: {"bg": "#FFF5F5", "border": "#E53935", "th_bg": "#FFE0E0", "col_bg": "#FFF5F5",
            "badge": "4️⃣", "label": "מקום רביעי", "rank_color": "#c0392b",
            "health_bg": "#fde8e8", "health_color": "#b71c1c"},
        5: {"bg": "#F5F3FA", "border": "#7E57C2", "th_bg": "#E9E3F5", "col_bg": "#F5F3FA",
            "badge": "5️⃣", "label": "מקום חמישי", "rank_color": "#5E35B1",
            "health_bg": "#eee8f7", "health_color": "#5E35B1"},
    }

    def get_health_label(is_resilient, is_preserving):
        if is_resilient and is_preserving: return "🟢 חסין"
        elif is_resilient: return "🟡 מחזיק מעמד"
        else: return "🔴 נשחק"

    def get_health_style(is_resilient, is_preserving):
        if is_resilient and is_preserving: return "#e8f8ee", "#1a7a3a"
        elif is_resilient: return "#fffbe6", "#856400"
        else: return "#fde8e8", "#b71c1c"

    # -------------------------------------------------------
    # Render Executive Summary
    # -------------------------------------------------------
    st.markdown("""
        <style>
        [data-testid="stHorizontalBlock"] { align-items: stretch !important; }
        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] > div { height: 100%; }
        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] > div > div { height: 100%; }
        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] > div > div > div:first-child { height: 100%; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='text-align: center; color: #1a1a2e;'>🧭 סיכום מנהלים — השוואת מסלולים</h3>", unsafe_allow_html=True)

    if not has_winner:
        st.warning(f"⚠️ אין מסלול מומלץ — אף מסלול אינו מחזיק את התיק עד גיל {check_age:.0f}. בכל המסלולים החיסכון עלול להיגמר לפני כן. מומלץ לבחון מחדש את ההכנסות וההוצאות, או להוריד את גיל הבדיקה אם הוא גבוה מהמתוכנן.")

    # Tracks that include a guaranteed pension (190 and hybrid)
    PENSION_TRACKS = {1, 3, 5}

    def build_winner_tooltip(track_id, is_resilient, total_100_val, stress_passed):
        reasons = []
        if is_resilient:
            reasons.append(f"✓ מחזיק עד גיל {check_age:.0f} — כיסוי לאופק התכנון שהגדרת")
        if track_id in PENSION_TRACKS:
            reasons.append("✓ קצבה מובטחת לכל החיים — הכנסה שלא תלויה בשוק")
        if track_id == 4 and stress_passed:
            reasons.append("✓ עמד במבחן סטרס נדל\"ן — נדל\"ן בהנחה 15% + קנס ₪500K")
        elif track_id == 4 and not stress_passed:
            reasons.append("△ ניצח על בסיס שווי כולל — בתרחיש לחץ מסלול 190 קרוב")
        reasons.append(f"✓ הכי הרבה נכסים בגיל {check_age:.0f} — {format_shekel(int(total_100_val))}")
        return "<br/>".join(reasons)

    # -------------------------------------------------------
    # Per-track figures for the unified executive cards
    # -------------------------------------------------------
    _exp_col, _inc_col, _pen_col = "הוצאה נומינלית", "הכנסה נומינלית", "הכנסה מקצבה מזערית"
    _cf_series = {
        1: df_full[_inc_col] + df_full[_pen_col] - df_full[_exp_col],
        2: df_full[_inc_col] - df_full[_exp_col],
        3: df_full[_inc_col] + df_full[_pen_col] - df_full[_exp_col],
        4: df_full["תזרים נטו שכירות"],
        5: df_full[_inc_col] + df_full[_pen_col] - df_full[_exp_col],
    }
    _post_ret = df_full[df_full["גיל"] >= retire_age]
    def _cf_at_retire(s):
        return float(s.loc[_post_ret.index[0]]) if not _post_ret.empty else float(s.iloc[0])
    def _cf_flip(s):
        neg = _post_ret.index[(s.loc[_post_ret.index] < 0).values]
        if len(neg) == 0:
            return None, 0.0
        return float(df_full.loc[neg[0], "גיל"]), float(s.loc[neg[0]])
    cf_retire = {t: _cf_at_retire(_cf_series[t]) for t in (1, 2, 3, 4, 5)}
    cf_flip = {t: _cf_flip(_cf_series[t]) for t in (1, 2, 3, 4, 5)}

    # Sustainability per track: monthly draw at retirement, erosion-start age, life-of-portfolio
    _bal_col = {1: "צבירה תיקון 190", 2: "צבירה מסלול ריאלי",
                3: "צבירה מסלול היברידי", 4: "צבירה מסלול שכירות",
                5: "צבירה מסלול מינוף"}
    _sim_end_age = float(df_full["גיל"].max())
    def _erosion_age(t):
        """Age the portfolio balance peaks and starts declining. None = grows for life."""
        post = df_full[df_full["גיל"] >= retire_age]
        if post.empty:
            return None
        pk_age = float(df_full.loc[post[_bal_col[t]].idxmax(), "גיל"])
        return None if pk_age >= _sim_end_age - 0.5 else pk_age
    draw_retire = {t: max(0.0, -cf_retire[t]) for t in (1, 2, 3, 4, 5)}
    erosion_age = {t: _erosion_age(t) for t in (1, 2, 3, 4, 5)}
    # Age the liquid portfolio stops sufficing: depletion for 1-3/5, RM activation for 4
    portfolio_lasts = {1: empty_190, 2: empty_25, 3: empty_h,
                       4: (rm_activation_age if rm_activation_age is not None else 120.0),
                       5: empty_lev}

    # Wealth at the checked age — liquid portfolio, property (gross), liabilities
    fin_check   = {1: b190_c, 2: b25_c, 3: bh_c, 4: br_c, 5: blev_c}
    prop_check  = {1: property_value_check, 2: property_value_check,
                   3: property_value_check, 4: rental_prop_check, 5: property_value_check}
    liab_check  = {1: 0.0, 2: 0.0, 3: 0.0, 4: rm_debt_at_check, 5: loan_debt_c}

    # Future betterment tax on the kept property — a real liability, track 4 only
    # (track 5 sold the old property, tax already paid via net_sale)
    tax_check = {1: 0.0, 2: 0.0, 3: 0.0, 4: property_tax_check, 5: 0.0}

    # kids_asset_check was computed above (also feeds the ranking metric sa_100)
    total_check = {t: fin_check[t] + prop_check[t] - liab_check[t] - tax_check[t] + kids_asset_check[t]
                   for t in (1, 2, 3, 4, 5)}

    # --- Track 5 leverage risk gauge: LTV, margin-call cushion, cash buffer ---
    _CALL_LTV = 0.85  # lender liquidates when loan/portfolio crosses this
    _ltv_col = df_full[df_full["גיל"] >= retire_age]["מינוף — LTV"] if "מינוף — LTV" in df_full.columns else None
    lev_ltv_max = float(_ltv_col.max()) if _ltv_col is not None and not _ltv_col.empty else 0.0
    lev_drop_tol = max(0.0, 1 - lev_ltv_max / _CALL_LTV) if lev_ltv_max > 0 else 1.0
    _lev_draw_year = draw_retire.get(5, 0.0) * 12
    lev_buffer_years = (emergency_fund / _lev_draw_year) if _lev_draw_year > 100 else None

    def _card_row(label, value_html, strong=False, top_border=False):
        bt = "border-top:1px solid #e0e0e0;" if top_border else ""
        val_size = "1.02em" if strong else "0.9em"
        val_weight = "800" if strong else "700"
        return (
            f"<div style='display:flex;justify-content:space-between;align-items:center;"
            f"min-height:32px;padding:3px 0;border-bottom:1px solid #f2f2f2;{bt}'>"
            f"<span style='font-size:0.7em;color:#777;'>{label}</span>"
            f"<span style='font-size:{val_size};font-weight:{val_weight};'>{value_html}</span></div>"
        )

    def _val(text, color="#1a1a2e"):
        return f"<span style='color:{color};'>{text}</span>"

    def _section_title(text):
        return (f"<div style='font-size:0.66em;font-weight:800;color:#8a8a8a;"
                f"letter-spacing:0.03em;margin:10px 0 2px;'>{text}</div>")

    # Cards: render in reverse rank order so rank1 is rightmost (Streamlit LTR columns)
    n_visible = max(1, len(ranked_order))
    cols = st.columns(n_visible)
    for col_idx, (rank, track_id, score, empty_age, preservation, husn) in enumerate(reversed(ranked_order)):
        pc = track_pros_cons[track_id]
        rc = RANK_CFG[rank]
        is_winner = rank == 1 and has_winner
        is_resilient, is_preserving, is_healthy = track_health(empty_age, preservation)
        health = get_health_label(is_resilient, is_preserving)
        health_bg, health_color = get_health_style(is_resilient, is_preserving)
        res_color = "#1a7a3a" if empty_age >= check_age else ("#b84c00" if empty_age >= 90 else "#c0392b")
        res_label = f"גיל {check_age:.0f}+" if empty_age >= check_age else f"גיל {empty_age:.0f}"

        if rank == 1:
            shadow = "0 16px 48px rgba(212,168,0,0.35), 0 4px 16px rgba(0,0,0,0.14)"
            border_top = "5px solid #D4A800"
            outline = "outline: 3px solid #D4A800; outline-offset: 3px;"
            if is_winner:
                _why_tooltip = build_winner_tooltip(
                    track_id, is_resilient, total_check[track_id], track4_wins_stress
                )
                winner_ribbon = (
                    f"<div style='text-align:center;margin-bottom:10px;'>"
                    f"<span style='display:inline-block;"
                    f"background:linear-gradient(135deg,#C8960C,#F0C93A,#C8960C);"
                    f"color:#fff;padding:5px 20px;border-radius:20px;font-size:0.72em;font-weight:800;"
                    f"white-space:nowrap;box-shadow:0 4px 12px rgba(200,150,12,0.5);letter-spacing:0.05em;'>"
                    f"⭐ המסלול המומלץ</span>"
                    f"<span class='qa-tip' style='color:#B8860B;margin-right:6px;'>ⓘ"
                    f"<span class='qa-tiptext' style='width:280px;font-size:0.82em;line-height:1.5;'>"
                    f"<b>למה ניצח?</b><br/>{_why_tooltip}</span></span>"
                    f"</div>"
                )
            else:
                winner_ribbon = (
                    f"<div style='text-align:center;margin-bottom:10px;'>"
                    f"<span style='display:inline-block;background:#B8860B;"
                    f"color:#fff;padding:4px 18px;border-radius:20px;font-size:0.72em;font-weight:800;"
                    f"white-space:nowrap;letter-spacing:0.04em;'>"
                    f"🏆 מקום ראשון</span></div>"
                )
        else:
            shadow = "0 2px 10px rgba(0,0,0,0.07)"
            border_top = f"4px solid {rc['border']}"
            outline = ""
            winner_ribbon = "<div style='height:30px;'></div>"

        # --- Unified card body: sustainability section + wealth section (same rows for every track) ---
        # Row 1: monthly supplement drawn from the portfolio at retirement
        draw0 = draw_retire[track_id]
        if draw0 <= 1:
            draw_txt = _val("אין צורך", "#1a7a3a")
        else:
            draw_txt = _val(f"−{format_shekel(int(draw0))}", "#c0392b")

        # Row 2: age the portfolio starts to erode (peak then decline); None = grows for life
        er = erosion_age[track_id]
        if er is None:
            erode_txt = _val("צומח תמיד", "#1a7a3a")
        else:
            erode_txt = _val(f"גיל {er:.0f}", "#b84c00" if er >= 80 else "#c0392b")

        # Row 3: until what age the liquid portfolio suffices, with a track-specific hint
        pl = portfolio_lasts[track_id]
        if pl >= 105:
            lasts_txt = _val("מספיק לכל החיים", "#1a7a3a")
        else:
            if track_id == 4:
                hint = "נכנסת משכנתה הפוכה"
            elif track_id in (1, 3, 5):
                hint = "נשארת רק הקצבה"
            else:
                hint = "נגמר הכסף, אין קצבה"
            lasts_txt = _val(f"גיל {pl:.0f} · {hint}", "#c0392b")

        liab = liab_check[track_id]
        liab_txt = _val(f"−{format_shekel(int(liab))}", "#c0392b") if liab > 0 else _val("—", "#aaa")
        tax_c = tax_check[track_id]
        tax_txt = _val(f"−{format_shekel(int(tax_c))}", "#c0392b") if tax_c > 0 else _val("—", "#aaa")
        kids_a = kids_asset_check[track_id]
        kids_txt = _val(f"+{format_shekel(int(kids_a))}", "#1a7a3a") if kids_a > 0 else _val("—", "#aaa")

        body = (
            _section_title("💸 קיימות התיק")
            + _card_row("השלמה חודשית מהתיק בפרישה", draw_txt)
            + _card_row("גיל תחילת שחיקת התיק", erode_txt)
            + _card_row("עד איזה גיל התיק מספיק", lasts_txt)
            + _section_title(f"🏦 הון בגיל {check_age:.0f}")
            + _card_row("💰 תיק פיננסי", _val(format_shekel(int(fin_check[track_id]))))
            + _card_row("🏠 שווי נדל\"ן", _val(format_shekel(int(prop_check[track_id]))))
            + _card_row("➖ הלוואות והתחייבויות", liab_txt)
            + _card_row("🧾 מס שבח עתידי", tax_txt)
            + _card_row("🎁 עזרה לילדים (נכס משפחתי)", kids_txt)
            + _card_row("📊 סך נכסים", _val(format_shekel(int(total_check[track_id]))), strong=True, top_border=True)
        )
        if track_id == 4 and rm_track4_not_viable:
            body = (
                "<div style='background:#fdecea;border:1px solid #e0a099;border-radius:6px;"
                "padding:6px 8px;margin-bottom:6px;color:#a83232;font-weight:700;font-size:0.72em;text-align:center;'>"
                "🚫 מסלול לא קביל — אין מספיק כסף לכסות את הגרעון</div>"
            ) + body

        # Leverage risk gauge — only on the leverage card
        if track_id == 5 and lev_ltv_max > 0:
            if lev_drop_tol >= 0.40:
                _rk_bg, _rk_fg, _rk_label = "#e8f8ee", "#1a7a3a", "סביר"
            elif lev_drop_tol >= 0.25:
                _rk_bg, _rk_fg, _rk_label = "#fff8e1", "#b07800", "זהירות"
            else:
                _rk_bg, _rk_fg, _rk_label = "#fdecea", "#a83232", "משחק באש"
            _buf = f"{lev_buffer_years:.0f} שנים" if lev_buffer_years else "—"
            gauge = (
                f"<div style='background:{_rk_bg};border-radius:6px;padding:6px 8px;margin-bottom:6px;"
                f"color:{_rk_fg};font-size:0.68em;text-align:center;line-height:1.5;'>"
                f"<b>⚖️ מד סיכון מינוף · {_rk_label}</b><br/>"
                f"מינוף {lev_ltv_max*100:.0f}% מהתיק · השוק יכול ליפול {lev_drop_tol*100:.0f}% "
                f"לפני דרישת ביטחונות · כרית מזומן {_buf}</div>"
            )
            body = gauge + body

        inner_card = (
            f"<div style='background:{rc['bg']};border-top:{border_top};border-radius:12px;"
            f"padding:14px 14px 14px 14px;box-shadow:{shadow};{outline}font-family:sans-serif;"
            f"direction:rtl;text-align:right;height:100%;display:flex;flex-direction:column;justify-content:space-between;'>"
            f"<div>"
            f"{winner_ribbon}"
            f"<div style='text-align:center;margin-bottom:6px;font-size:1.7em;line-height:1;'>{rc['badge']}</div>"
            f"<div style='text-align:center;font-size:0.72em;font-weight:700;color:{rc['rank_color']};margin-bottom:8px;letter-spacing:0.04em;'>{rc['label']}</div>"
            f"<div style='text-align:center;font-size:0.92em;font-weight:700;color:#1a1a2e;margin-bottom:10px;line-height:1.35;'>{pc['name']}</div>"
            f"<div style='text-align:center;margin-bottom:10px;'>"
            f"<span style='display:inline-block;font-size:0.78em;font-weight:600;padding:2px 10px;border-radius:20px;"
            f"background:{health_bg};color:{health_color};'>{health}"
            f" <span class='qa-tip'>ⓘ<span class='qa-tiptext'>"
            f"🟢 חסין = התיק מחזיק עד גיל {check_age:.0f} ושומר על 90%+ מההון (כולל ערך קצבה). "
            f"🟡 מחזיק = מחזיק עד גיל {check_age:.0f} אך נשחק מתחת ל-90%. "
            f"🔴 נשחק = התיק הנזיל עלול להיגמר לפני גיל {check_age:.0f}."
            f"</span></span></span></div>"
            f"<div style='text-align:center;font-size:0.74em;color:{res_color};font-weight:700;margin-bottom:4px;'>"
            f"⏳ מחזיק עד {res_label}</div>"
            f"</div>"
            f"<div style='border-top:1px solid #e8e8e8;padding-top:6px;'>"
            + body
            + f"</div></div>"
        )

        card_html = (
            f"<div style='height:100%;'>"
            f"{inner_card}"
            f"</div>"
        )

        with cols[col_idx]:
            st.markdown(card_html, unsafe_allow_html=True)
            with st.expander("יתרונות וסיכונים"):
                st.markdown(f"<span style='color:#1a7a3a;'>✅ {pc['pro1']}</span>", unsafe_allow_html=True)
                st.markdown(f"<span style='color:#1a7a3a;'>✅ {pc['pro2']}</span>", unsafe_allow_html=True)
                st.markdown(f"<span style='color:#b84c00;'>⚠️ {pc['con1']}</span>", unsafe_allow_html=True)
                st.markdown(f"<span style='color:#b84c00;'>⚠️ {pc['con2']}</span>", unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # -------------------------------------------------------
    # Table helper — st.columns(4) aligned under cards
    # -------------------------------------------------------
    def render_metric_columns(rows, data_dict, show_header=True, tooltips=None):
        tooltips = tooltips or {}
        # Render as single HTML block — each row is one flex div so all cells align perfectly.
        # RTL flex: first child = rightmost visually → label first, then rank1..rank4.
        html_parts = []

        if show_header:
            hp = ["<div style='display:flex;direction:rtl;gap:4px;margin-bottom:4px;'>",
                  "<div style='flex:1.5;'></div>"]
            for rank, track_id, *_ in ranked_order:
                rc = RANK_CFG[rank]
                hp.append(
                    f"<div style='flex:1;background:{rc['th_bg']};border-bottom:2px solid {rc['border']};"
                    f"padding:4px 6px;border-radius:6px 6px 0 0;text-align:center;"
                    f"font-size:0.72em;font-weight:700;color:{rc['rank_color']};'>"
                    f"{rc['badge']} {TRACK_NAMES[track_id]}</div>"
                )
            hp.append("</div>")
            html_parts.append("".join(hp))

        for question, key in rows:
            tip = tooltips.get(key, "")
            tip_html = (
                f" <span class='qa-tip'>ⓘ<span class='qa-tiptext'>{tip}</span></span>"
                if tip else ""
            )
            rp = [
                "<div style='display:flex;direction:rtl;gap:4px;margin-bottom:4px;align-items:stretch;'>",
                f"<div style='flex:1.5;padding:6px 10px;border-radius:5px;background:#f8f9fc;"
                f"border:1px solid #eee;border-right:3px solid #d0d4e8;direction:rtl;text-align:right;"
                f"font-size:0.82em;font-weight:600;color:#333;"
                f"display:flex;align-items:center;'>{question}{tip_html}</div>",
            ]
            for rank, track_id, *_ in ranked_order:
                rc = RANK_CFG[rank]
                val = data_dict.get(TRACK_NAMES[track_id], {}).get(key, "—")
                rp.append(
                    f"<div style='flex:1;background:{rc['col_bg']};padding:6px 8px;border-radius:5px;"
                    f"border:1px solid #eee;font-size:0.88em;font-weight:600;line-height:1.35;"
                    f"display:flex;flex-direction:column;align-items:center;justify-content:center;"
                    f"text-align:center;'>{val}</div>"
                )
            rp.append("</div>")
            html_parts.append("".join(rp))

        st.markdown("\n".join(html_parts), unsafe_allow_html=True)

    # -------------------------------------------------------
    # Table 1: At retirement
    # -------------------------------------------------------
    bool_preserve_95_190 = "✅ כן" if b190_100 >= baseline_capital else "❌ לא"
    bool_preserve_95_25  = "✅ כן" if b25_100  >= baseline_capital else "❌ לא"
    bool_preserve_95_h   = "✅ כן" if bh_100   >= baseline_capital else "❌ לא"
    bool_preserve_95_r   = "✅ כן" if br_100 > 0 else "❌ לא"

    # Unified cashflow / withdrawal cell.
    #  Tracks 1-3: nn is the monthly deficit pulled from the portfolio.
    #  Track 4 (rental): pass cashflow (positive=surplus, negative=deficit) + withdrawal_pct for the note.
    def fmt_cashflow(nn, cashflow=None, withdrawal_pct=0.0):
        if cashflow is None:
            return fmt_withdrawal(nn)
        if cashflow >= 0:
            return (f"<span style='color:#1a7a3a;font-weight:700;'>+{format_shekel(int(cashflow))}</span>"
                    f"<br/><span style='color:#1a7a3a;font-size:0.72em;'>עודף תזרימי משכירות</span>")
        return (f"<span style='color:#c0392b;font-weight:700;'>{format_shekel(int(abs(cashflow)))}−</span>"
                f"<br/><span style='color:#c0392b;font-size:0.72em;'>גירעון תזרימי משכירות<br/>"
                f"({withdrawal_pct:.1f}% שיעור משיכה מהתיק)</span>")

    # Track 5 (leverage) figures for the detail tables
    blev_r = float(row_retire.get("צבירה מסלול מינוף", 0.0))
    loan_debt_r = float(row_retire.get("הלוואת בלון — יתרת חוב", 0.0))
    nn_lev_r, nn_lev_c = nn_190_r, nn_190_c
    pct_lev_r = wpct(nn_lev_r, blev_r)
    pct_lev_c = wpct(nn_lev_c, blev_c)
    tw_lev_r = blev_r + pension_asset_retire + property_value_retire + emergency_fund - loan_debt_r
    tw_lev_c = blev_c + pension_asset_check + property_value_check + emergency_fund - loan_debt_c
    inherit_lev_r = blev_r + pension_asset_retire - loan_debt_r
    inherit_lev_c = blev_c + pension_asset_check - loan_debt_c
    recovery_lev = find_recovery_age("צבירה מסלול מינוף") if "צבירה מסלול מינוף" in df_full.columns else "—"
    peak_lev = find_peak_age("צבירה מסלול מינוף") if "צבירה מסלול מינוף" in df_full.columns else "—"
    _df_lev_empty = df_full[(df_full.get("צבירה מסלול מינוף", 1) <= 0) & (df_full["גיל"] <= check_age)] if "צבירה מסלול מינוף" in df_full.columns else df_full.iloc[0:0]
    cum_deficit_lev = float((_df_lev_empty["הוצאה נומינלית"] - _df_lev_empty["הכנסה נומינלית"] - _df_lev_empty["הכנסה מקצבה מזערית"]).clip(lower=0).sum())
    months_deficit_lev = len(_df_lev_empty)

    t1_cols = {
        "190 + קצבה מזערית": {
            "הכנסות חודשיות":  format_shekel(int(base_income_retire + pension_retire)),
            "הוצאות חודשיות":  format_shekel(int(exp_retire)),
            "הון כולל":        fmt_with_pension_note(inherit_190_r, pension_asset_retire),
            "משיכה / תזרים":   fmt_cashflow(nn_190_r),
            "קצב משיכה":       wrap_html_style(f"{pct_190_r:.2f}%", get_withdrawal_style(pct_190_r)),
            "סך נכסים":        format_shekel(tw_190_r),
            "תיק נזיל":        format_shekel(b190_r),
            "שווי נדלן":       format_shekel(property_value_retire),
            "חוק 400":         wrap_html_style(rule400(b190_r, nn_190_r), get_400_rule_style(rule400(b190_r, nn_190_r))),
            "קרן חירום":       wrap_html_style(emer(nn_190_r), get_emergency_style(emer(nn_190_r))),
        },
        "25% ריאלי (ללא קצבה)": {
            "הכנסות חודשיות":  format_shekel(int(base_income_retire)),
            "הוצאות חודשיות":  format_shekel(int(exp_retire)),
            "הון כולל":        format_shekel(b25_r),
            "משיכה / תזרים":   fmt_cashflow(nn_25_r),
            "קצב משיכה":       wrap_html_style(f"{pct_25_r:.2f}%", get_withdrawal_style(pct_25_r)),
            "סך נכסים":        format_shekel(tw_25_r),
            "תיק נזיל":        format_shekel(b25_r),
            "שווי נדלן":       format_shekel(property_value_retire),
            "חוק 400":         wrap_html_style(rule400(b25_r, nn_25_r), get_400_rule_style(rule400(b25_r, nn_25_r))),
            "קרן חירום":       wrap_html_style(emer(nn_25_r), get_emergency_style(emer(nn_25_r))),
        },
        "25% ריאלי + קצבה מזערית": {
            "הכנסות חודשיות":  format_shekel(int(base_income_retire + pension_retire)),
            "הוצאות חודשיות":  format_shekel(int(exp_retire)),
            "הון כולל":        fmt_with_pension_note(inherit_h_r, pension_asset_retire),
            "משיכה / תזרים":   fmt_cashflow(nn_h_r),
            "קצב משיכה":       wrap_html_style(f"{pct_h_r:.2f}%", get_withdrawal_style(pct_h_r)),
            "סך נכסים":        format_shekel(tw_h_r),
            "תיק נזיל":        format_shekel(bh_r),
            "שווי נדלן":       format_shekel(property_value_retire),
            "חוק 400":         wrap_html_style(rule400(bh_r, nn_h_r), get_400_rule_style(rule400(bh_r, nn_h_r))),
            "קרן חירום":       wrap_html_style(emer(nn_h_r), get_emergency_style(emer(nn_h_r))),
        },
        "שכירות": {
            "הכנסות חודשיות":  format_shekel(int(base_income_retire + net_rental_r)),
            "הוצאות חודשיות":  format_shekel(int(exp_retire + rent_paid_r + maintenance_r)),
            "הון כולל":        format_shekel(br_r),
            "משיכה / תזרים":   fmt_cashflow(nn_rent_r, cashflow=rental_cashflow_at_retire, withdrawal_pct=pct_rent_r),
            "קצב משיכה":       (
                "<span style='color:#1a7a3a;'>✅ לא נדרש</span>"
                if rental_cashflow_at_retire >= 0 else
                wrap_html_style(f"{pct_rent_r:.2f}%", get_withdrawal_style(pct_rent_r))
            ),
            "סך נכסים":        format_shekel(tw_rent_r),
            "תיק נזיל":        format_shekel(br_r),
            "שווי נדלן":       format_shekel(rm_equity_retire),  # net equity (property minus RM loan)
            "חוק 400":         "<span style='color:#888;'>לא רלוונטי<br/>(מבחן תזרים)</span>",
            "קרן חירום":       wrap_html_style(emer(nn_rent_r), get_emergency_style(emer(nn_rent_r))) if nn_rent_r > 0 else "<span style='color:#1a7a3a;'>לא נדרש</span>",
        },
        "מינוף (הלוואת בלון)": {
            "הכנסות חודשיות":  format_shekel(int(base_income_retire + pension_retire)),
            "הוצאות חודשיות":  format_shekel(int(exp_retire)),
            "הון כולל":        fmt_with_pension_note(inherit_lev_r, pension_asset_retire),
            "משיכה / תזרים":   fmt_cashflow(nn_lev_r),
            "קצב משיכה":       wrap_html_style(f"{pct_lev_r:.2f}%", get_withdrawal_style(pct_lev_r)),
            "סך נכסים":        format_shekel(tw_lev_r),
            "תיק נזיל":        format_shekel(blev_r),
            "שווי נדלן":       format_shekel(property_value_retire),
            "חוק 400":         wrap_html_style(rule400(blev_r, nn_lev_r), get_400_rule_style(rule400(blev_r, nn_lev_r))),
            "קרן חירום":       wrap_html_style(emer(nn_lev_r), get_emergency_style(emer(nn_lev_r))),
        },
    }

    ASSETS_ROWS_1 = [
        ("מה גובה התיק הנזיל ביום הפרישה?",   "תיק נזיל"),
        ("שווי הון כולל כולל קצבה",            "הון כולל"),
        ("מה שווי הנדל\"ן שלי בפרישה?",        "שווי נדלן"),
        ("מה סך כלל הנכסים שלי?",              "סך נכסים"),
    ]
    CASHFLOW_ROWS_1 = [
        ("הכנסות (קצבאות / שכירות)",            "הכנסות חודשיות"),
        ("הוצאות (קבועות / שכירות)",            "הוצאות חודשיות"),
        ("כמה אצטרך להשלים מהתיק (תזרים)",      "משיכה / תזרים"),
    ]
    ACTUARIAL_ROWS_1 = [
        ("מה קצב המשיכה השנתי מהתיק?",         "קצב משיכה"),
        ("מה מדד החסינות של התיק (חוק 400)?",  "חוק 400"),
        ("כמה שנים קרן החירום מכסה?",           "קרן חירום"),
    ]

    TOOLTIPS_ASSETS_1 = {
        "תיק נזיל":   f"סך הצבירה הנזילה בתיק ההשקעות ביום הפרישה (גיל {retire_age:.1f}). לא כולל נדל\"ן ולא כולל ערך הקצבה.",
        "הון כולל":   f"תיק נזיל + ערך נוכחי של הקצבה המובטחת (מסלולים 1 ו-3) — כלומר כמה שווה בפועל הנכס הפנסיוני כולו. במסלול 4: רק חסכונות נזילים.",
        "שווי נדלן":  f"שווי הדירה ביום הפרישה (גיל {retire_age:.1f}), לפי עליית ערך שנתית שהוגדרה בקלט. מסלולים 1-3: דירה למגורים. מסלול 4: דירה להשקעה.",
        "סך נכסים":   f"סכום כולל: תיק נזיל + ערך קצבה + שווי נדל\"ן + קרן חירום. מבטא את שווי הנכס נטו של הלקוח ביום הפרישה.",
    }
    TOOLTIPS_CASHFLOW_1 = {
        "הכנסות חודשיות": f"סך ההכנסות החודשיות הצפויות בגיל {retire_age:.1f}: ביטוח לאומי + פנסיה (מסלולים 1/3) או שכ\"ד נטו אחרי מס (מסלול 4). לא כולל משיכות מהתיק.",
        "הוצאות חודשיות": f"הוצאות חודשיות נומינליות (מוצמדות לאינפלציה) בגיל {retire_age:.1f}. מסלול 4: כולל שכ\"ד שמשולם + תחזוקת הנכס המושכר (7–12% מהשכירות). הכנסות - הוצאות = תזרים.",
        "משיכה / תזרים":  f"הפרש בין הוצאות להכנסות — כמה יש להוציא מהתיק כל חודש. מסלול 4: מראה תזרים כולל (חיובי = עודף, שלילי = חסר).",
    }
    TOOLTIPS_ACTUARIAL_1 = {
        "קצב משיכה":  f"משיכה שנתית מהתיק חלקי ערך התיק, באחוזים. מתחת ל-3%: בטוח מאוד. 3-4%: מקובל. מעל 4%: מסוכן. חוק ה-4% מבוסס על מחקר Trinity.",
        "חוק 400":    f"יחס בטיחות: ערך התיק חלקי (משיכה חודשית × 400). מעל 1.3 = בטוח. מעל 1.0 = עומד בחוק 4%. מתחת ל-1.0 = מסוכן.",
        "קרן חירום":  f"קרן החירום שהוגדרה (₪ {format_shekel(int(emergency_fund))}) חלקי (משיכה × 12). כמה שנים ניתן לחיות מקרן החירום בלבד אם התיק יפגע.",
    }

    st.markdown(f"### 📊 מצב ביום הפרישה — גיל {retire_age:.1f}")
    with st.expander("💰 סיכום שווי נכסים", expanded=True):
        render_metric_columns(ASSETS_ROWS_1, t1_cols, show_header=True, tooltips=TOOLTIPS_ASSETS_1)
    with st.expander("💸 סיכום תזרים", expanded=True):
        render_metric_columns(CASHFLOW_ROWS_1, t1_cols, show_header=True, tooltips=TOOLTIPS_CASHFLOW_1)
    with st.expander("📊 ניתוח אקטוארי", expanded=False):
        render_metric_columns(ACTUARIAL_ROWS_1, t1_cols, show_header=True, tooltips=TOOLTIPS_ACTUARIAL_1)

    # -------------------------------------------------------
    # Table 2: At check_age
    # -------------------------------------------------------
    # Resilience formatter for the table: highlight the lifespan of the portfolio
    def fmt_lifespan(empty_age):
        if empty_age >= 105.0:
            return "<span style='color:#1a7a3a; font-weight:bold;'>✅ לא נשחק</span>"
        color = "#b84c00" if empty_age >= 90 else "#b71c1c"
        return f"<span style='color:{color}; font-weight:bold;'>גיל {empty_age:.0f}</span>"

    # Preservation % at check_age (the core health metric, shown numerically) —
    # fair to pension tracks: counts remaining annuity value, vs own starting capital.
    def fmt_preservation(ratio):
        pct = ratio * 100
        if pct >= 90: color = "#1a7a3a"
        elif pct >= 75: color = "#b84c00"
        else: color = "#b71c1c"
        return f"<span style='color:{color}; font-weight:bold;'>{pct:.0f}%</span>"

    t2_cols = {
        "190 + קצבה מזערית": {
            "הכנסות חודשיות": format_shekel(int(base_income_check + pension_check)),
            "הוצאות חודשיות": format_shekel(int(exp_check)),
            "משיכה / תזרים": fmt_cashflow(nn_190_c),
            "גירעון מצטבר":  fmt_cum_deficit(cum_deficit_190, months_deficit_190),
            "עד איזה גיל הכסף מחזיק?": fmt_lifespan(empty_190),
            "שימור הון":    fmt_preservation(preservation_ratio[1]),
            "הון כולל":     fmt_with_delta(inherit_190_c, baseline_capital, pension_component=int(pension_asset_check)),
            "תיק נזיל":     format_shekel(b190_c),
            "שווי נדלן":    format_shekel(property_value_check),
            "סך נכסים":     format_shekel(tw_190_c),
            "קצב משיכה":    wrap_html_style(f"{pct_190_c:.2f}%", get_withdrawal_style(pct_190_c)),
            "גיל התאוששות": recovery_190,
            "גיל היפוך":    peak_190,
        },
        "25% ריאלי (ללא קצבה)": {
            "הכנסות חודשיות": format_shekel(int(base_income_check)),
            "הוצאות חודשיות": format_shekel(int(exp_check)),
            "משיכה / תזרים": fmt_cashflow(nn_25_c),
            "גירעון מצטבר":  fmt_cum_deficit(cum_deficit_25, months_deficit_25),
            "עד איזה גיל הכסף מחזיק?": fmt_lifespan(empty_25),
            "שימור הון":    fmt_preservation(preservation_ratio[2]),
            "הון כולל":     fmt_with_delta(b25_c, baseline_capital),
            "תיק נזיל":     format_shekel(b25_c),
            "שווי נדלן":    format_shekel(property_value_check),
            "סך נכסים":     format_shekel(tw_25_c),
            "קצב משיכה":    wrap_html_style(f"{pct_25_c:.2f}%", get_withdrawal_style(pct_25_c)),
            "גיל התאוששות": recovery_25,
            "גיל היפוך":    peak_25,
        },
        "25% ריאלי + קצבה מזערית": {
            "הכנסות חודשיות": format_shekel(int(base_income_check + pension_check)),
            "הוצאות חודשיות": format_shekel(int(exp_check)),
            "משיכה / תזרים": fmt_cashflow(nn_h_c),
            "גירעון מצטבר":  fmt_cum_deficit(cum_deficit_h, months_deficit_h),
            "עד איזה גיל הכסף מחזיק?": fmt_lifespan(empty_h),
            "שימור הון":    fmt_preservation(preservation_ratio[3]),
            "הון כולל":     fmt_with_delta(inherit_h_c, baseline_capital, pension_component=int(pension_asset_check)),
            "תיק נזיל":     format_shekel(bh_c),
            "שווי נדלן":    format_shekel(property_value_check),
            "סך נכסים":     format_shekel(tw_h_c),
            "קצב משיכה":    wrap_html_style(f"{pct_h_c:.2f}%", get_withdrawal_style(pct_h_c)),
            "גיל התאוששות": recovery_h,
            "גיל היפוך":    peak_h,
        },
        "שכירות": {
            "הכנסות חודשיות": format_shekel(int(base_income_check + net_rental_c)),
            "הוצאות חודשיות": format_shekel(int(exp_check + rent_paid_c + maintenance_c)),
            "משיכה / תזרים": fmt_cashflow(nn_rent_c, cashflow=rental_cashflow_at_check, withdrawal_pct=pct_rent_c),
            "גירעון מצטבר":  fmt_cum_deficit(cum_deficit_r, months_deficit_r),
            "עד איזה גיל הכסף מחזיק?": fmt_lifespan(empty_r),
            "שימור הון":    fmt_preservation(preservation_ratio[4]),
            "הון כולל":     format_shekel(br_c),
            "תיק נזיל":     format_shekel(br_c),
            "שווי נדלן":    format_shekel(rm_equity_check),  # net equity (property minus RM loan)
            "סך נכסים":     format_shekel(tw_rent_c),
            "קצב משיכה":    (
                "<span style='color:#1a7a3a;'>✅ לא נדרש</span>"
                if rental_cashflow_at_check >= 0 else
                wrap_html_style(f"{pct_rent_c:.2f}%", get_withdrawal_style(pct_rent_c))
            ),
            "גיל התאוששות": recovery_r,
            "גיל היפוך":    (
                "<span style='color:#1a7a3a;'>✅ תזרים חיובי לאורך כל הדרך</span>" if rental_always_positive
                else f"<span style='color:#b84c00;font-weight:700;'>גיל {rental_flip_age:.0f}</span>"
                if rental_flip_age else "<span style='color:#c0392b;'>מתחיל שלילי מהרגע הראשון</span>"
            ),
            "משכנתה הפוכה": (
                (
                    f"<span style='color:#856400;font-weight:700;'>מגיל {rm_activation_age:.0f}</span>"
                    if rm_activation_age else
                    "<span style='color:#1a7a3a;'>✅ לא הופעלה</span>"
                ) if rm_enabled_flag else
                "<span style='color:#aaa;'>—</span>"
            ),
            "הון עצמי RM בגיל נבדק": (
                (format_shekel(int(rm_equity_at_check)) if rm_equity_at_check is not None and rm_equity_at_check > 0
                 else "<span style='color:#c0392b;font-weight:700;'>⚠️ נכס מתחת למים</span>")
                if rm_enabled_flag else "<span style='color:#aaa;'>—</span>"
            ),
            "סה\"כ ריבית RM": (
                format_shekel(int(rm_total_interest)) if rm_enabled_flag and rm_total_interest
                else "<span style='color:#aaa;'>—</span>"
            ),
        },
        "מינוף (הלוואת בלון)": {
            "הכנסות חודשיות": format_shekel(int(base_income_check + pension_check)),
            "הוצאות חודשיות": format_shekel(int(exp_check)),
            "משיכה / תזרים": fmt_cashflow(nn_lev_c),
            "גירעון מצטבר":  fmt_cum_deficit(cum_deficit_lev, months_deficit_lev),
            "עד איזה גיל הכסף מחזיק?": fmt_lifespan(empty_lev),
            "שימור הון":    fmt_preservation(preservation_ratio[5]),
            "הון כולל":     fmt_with_delta(inherit_lev_c, baseline_capital, pension_component=int(pension_asset_check)),
            "תיק נזיל":     format_shekel(blev_c),
            "שווי נדלן":    format_shekel(property_value_check),
            "סך נכסים":     format_shekel(tw_lev_c),
            "קצב משיכה":    wrap_html_style(f"{pct_lev_c:.2f}%", get_withdrawal_style(pct_lev_c)),
            "גיל התאוששות": recovery_lev,
            "גיל היפוך":    peak_lev,
            "משכנתה הפוכה": "<span style='color:#aaa;'>—</span>",
            "הון עצמי RM בגיל נבדק": "<span style='color:#aaa;'>—</span>",
            "סה\"כ ריבית RM": "<span style='color:#aaa;'>—</span>",
        },
    }

    ASSETS_ROWS_2 = [
        ("מה גובה התיק הנזיל בגיל זה?",        "תיק נזיל"),
        ("שווי הון כולל כולל קצבה",            "הון כולל"),
        ("מה שווי הנדל\"ן שלי בגיל זה?",       "שווי נדלן"),
        ("מה סך כלל הנכסים שלי?",              "סך נכסים"),
    ]
    CASHFLOW_ROWS_2 = [
        ("הכנסות (קצבאות / שכירות)",                        "הכנסות חודשיות"),
        ("הוצאות (קבועות / שכירות)",                        "הוצאות חודשיות"),
        ("כמה אצטרך להשלים מהתיק (תזרים)",                  "משיכה / תזרים"),
        (f"גירעון לכיסוי חיצוני (עד גיל {check_age:.0f})", "גירעון מצטבר"),
    ]
    ACTUARIAL_ROWS_2 = [
        ("גיל מיצוי חסכונות — עד מתי הכסף מחזיק?", "עד איזה גיל הכסף מחזיק?"),
        ("כמה מההון ההתחלתי נשמר בגיל הנבדק?",       "שימור הון"),
        ("מה קצב המשיכה בגיל זה?",                  "קצב משיכה"),
        ("מאיזה גיל התיק עולה מעל ההון הראשוני?",    "גיל התאוששות"),
        ("גיל גרעון שכירות / גיל היפוך תיק",         "גיל היפוך"),
        ("משכנתה הפוכה — גיל הפעלה",                 "משכנתה הפוכה"),
        (f"הון עצמי נטו בנכס בגיל {check_age:.0f}", "הון עצמי RM בגיל נבדק"),
        ("סה\"כ ריבית שנצברה על RM",                  "סה\"כ ריבית RM"),
    ]

    TOOLTIPS_ASSETS_2 = {
        "תיק נזיל":   f"יתרת חסכונות נזילים בתיק ההשקעות בגיל {check_age:.1f}. אפס = הכסף אזל לפני גיל זה.",
        "הון כולל":   f"תיק נזיל + ערך קצבה נותר בגיל {check_age:.1f}. ערך הקצבה = חודשים שנותרו בתקופת הבטחה × קצבה חודשית.",
        "שווי נדלן":  f"שווי הדירה בגיל {check_age:.1f} לפי הצמדה שנתית. מסלול 4: דירת השקעה לפי {rental_appreciation_rate*100:.1f}% עלייה שנתית.",
        "סך נכסים":   f"סך כלל הנכסים: תיק + קצבה + נדל\"ן + קרן חירום. הסכום הכולל שניתן להוריש או לממש בגיל {check_age:.1f}.",
    }
    TOOLTIPS_CASHFLOW_2 = {
        "הכנסות חודשיות": f"הכנסות חודשיות צפויות בגיל {check_age:.1f}: ב\"ל מוצמד + פנסיה מוצמדת / שכ\"ד נטו. כל ההכנסות מוצמדות לאינפלציה.",
        "הוצאות חודשיות": f"הוצאות חודשיות בגיל {check_age:.1f} לאחר הצמדה לאינפלציה. כולל תוספת מטפל מגיל 85 אם הוגדרה. מסלול 4: כולל שכ\"ד + תחזוקת הנכס.",
        "משיכה / תזרים":  f"כמה יש להוציא מהתיק בגיל {check_age:.1f} = הוצאות פחות הכנסות. אם התיק אזל — הגירעון מופיע בשורת הגירעון המצטבר.",
        "גירעון מצטבר":   f"סכום כל החסרים החודשיים לאחר שהתיק הגיע לאפס, עד גיל {check_age:.0f}. מייצג כמה כסף חיצוני (ילדים, עזרה) נדרש לכיסוי. אפס = אין גירעון.",
    }
    TOOLTIPS_ACTUARIAL_2 = {
        "עד איזה גיל הכסף מחזיק?": "גיל מיצוי חסכונות: הגיל שבו יתרת התיק הנזיל מגיעה לאפס לחלוטין. מסלול 4: החסכונות אזלו — הדירה ממשיכה לייצר הכנסה אבל אין יותר כרית נזילה. אם לא נגמר עד 105 — מסומן ✅ לא נשחק.",
        "שימור הון":    f"אחוז מההון ההתחלתי של המסלול עצמו שנשמר בגיל {check_age:.0f} (במסלולי קצבה נספר גם ערך הקצבה שנותר, לא רק הנזיל). מעל 90% = מצוין. 75-90% = טוב. מתחת ל-75% = שחיקה משמעותית.",
        "קצב משיכה":    f"קצב המשיכה השנתי בגיל {check_age:.1f}. נמוך מ-3% = בטוח. 3-4% = מקובל. מעל 4% = לחץ על התיק.",
        "גיל התאוששות": f"הגיל שבו ערך התיק עולה מעל ההון ההתחלתי ({format_shekel(int(baseline_capital))}) בפעם הראשונה — מוכיח שהתיק גדל ולא רק נשמר.",
        "גיל היפוך":    "מסלולים 1-3: הגיל שבו התיק מגיע לשיאו ומתחיל להישחק (משיכות > תשואה חודשית). מסלול 4 — גיל גרעון שכירות: הגיל הראשון שבו ההכנסות (שכ\"ד + ב\"ל) לא מכסות את ההוצאות ומתחילים למשוך מהחסכונות.",
    }

    st.markdown(f"### 🔮 מצב בגיל {check_age:.1f}")
    with st.expander("💰 סיכום שווי נכסים", expanded=True):
        render_metric_columns(ASSETS_ROWS_2, t2_cols, show_header=True, tooltips=TOOLTIPS_ASSETS_2)
    with st.expander("💸 סיכום תזרים", expanded=True):
        render_metric_columns(CASHFLOW_ROWS_2, t2_cols, show_header=True, tooltips=TOOLTIPS_CASHFLOW_2)
    with st.expander("📊 ניתוח אקטוארי", expanded=False):
        render_metric_columns(ACTUARIAL_ROWS_2, t2_cols, show_header=True, tooltips=TOOLTIPS_ACTUARIAL_2)

