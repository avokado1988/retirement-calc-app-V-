import streamlit as st
import pandas as pd
from inputs.ui_components import (
    format_shekel, wrap_html_style,
    get_withdrawal_style, get_400_rule_style, get_emergency_style,
    get_larger_portfolio_style, get_resiliency_style,
    get_preservation_pct_style, get_boolean_style
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
    check_age = float(timeline.get("check_age", 87.0))
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
    _cf_retire_raw = float(row_retire.get("תזרים נטו שכירות", 0.0))
    _cf_check_raw  = float(row_check.get("תזרים נטו שכירות", 0.0))

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

    rent_paid_c = float(row_check.get("הוצאת שכירות", 0.0))
    net_rental_c = float(row_check.get("הכנסת שכירות נטו", 0.0))

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
    # Extract values at age 95
    # -------------------------------------------------------
    df_95 = df_full[df_full["גיל"] >= 95.0]
    row_95 = df_95.iloc[0] if not df_95.empty else df_full.iloc[-1]
    b190_95 = float(row_95["צבירה תיקון 190"])
    b25_95 = float(row_95["צבירה מסלול ריאלי"])
    bh_95 = float(row_95["צבירה מסלול היברידי"])
    br_95 = float(row_95["צבירה מסלול שכירות"])

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
    empty_r = find_empty_age("צבירה מסלול שכירות")

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
    df_full["rental_cashflow"] = df_full["תזרים נטו שכירות"]

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
    # Reverse mortgage metrics (track 4, optional)
    # -------------------------------------------------------
    rm_enabled_flag = bool(user_inputs.get("rental", {}).get("rm_enabled", False))
    rm_activation_age = None
    rm_equity_at_check = None
    rm_total_interest = None
    rm_underwater_age = None

    if rm_enabled_flag and "משכנתה הפוכה — יתרת חוב" in df_full.columns:
        rm_active_rows = df_full[df_full["משכנתה הפוכה — יתרת חוב"] > 0]
        if not rm_active_rows.empty:
            rm_activation_age = float(rm_active_rows.iloc[0]["גיל"])
        row_check_rm = df_full[df_full["גיל"] >= check_age].iloc[0] if not df_full[df_full["גיל"] >= check_age].empty else df_full.iloc[-1]
        rm_equity_at_check = float(row_check_rm.get("משכנתה הפוכה — הון עצמי", 0.0))
        rm_total_interest = float(df_full["משכנתה הפוכה — ריבית חודשית"].sum())
        underwater_rows = df_full[(df_full["גיל"] >= retire_age) & (df_full["משכנתה הפוכה — הון עצמי"] <= 0)]
        if not underwater_rows.empty:
            rm_underwater_age = float(underwater_rows.iloc[0]["גיל"])

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
    cum_deficit_r = float(df_r_neg["תזרים נטו שכירות"].clip(upper=0).abs().sum())
    months_deficit_r = len(df_r_neg)

    def fmt_cum_deficit(total, months):
        if total <= 0 or months == 0:
            return "<span style='color:#1a7a3a;font-weight:700;'>✅ אין גירעון</span>"
        monthly_avg = total / months
        yrs = months / 12
        return (f"<span style='color:#c0392b;font-weight:700;'>{format_shekel(int(total))}</span>"
                f"<br/><span style='color:#888;font-size:0.75em;'>על פני {yrs:.1f} שנים</span>"
                f"<br/><span style='color:#c0392b;font-size:0.78em;'>≈ {format_shekel(int(monthly_avg))}/חודש</span>")

    df_97 = df_full[df_full["גיל"] >= 97.0]
    row_97 = df_97.iloc[0] if not df_97.empty else df_full.iloc[-1]

    def ratio_at_97(col):
        val = float(row_97[col])
        pct = (val / max(1.0, baseline_capital)) * 100
        return pct, f"{pct:.2f}%"

    ratio_190_pct, ratio_190_str = ratio_at_97("צבירה תיקון 190")
    ratio_25_pct, ratio_25_str = ratio_at_97("צבירה מסלול ריאלי")
    ratio_h_pct, ratio_h_str = ratio_at_97("צבירה מסלול היברידי")
    ratio_r_pct, ratio_r_str = ratio_at_97("צבירה מסלול שכירות")

    # -------------------------------------------------------
    # Balanced Stress-Test: Track 4 vs Track 1 at check_age
    # S4   = portfolio_rental + (property_rental × 0.85 − 500K) − rm_debt
    # S190 = portfolio_190 + pension_asset + property × 1.05 + emergency
    # Δ > 0 → track 4 wins even under stress
    # -------------------------------------------------------
    rm_debt_check_st = float(row_check.get("משכנתה הפוכה — יתרת חוב", 0.0))
    S4_stress   = br_c + (rental_prop_check * 0.85 - 500_000) - rm_debt_check_st
    S190_stress = b190_c + pension_asset_check + property_value_check * 1.05 + emergency_fund
    delta_stress = S4_stress - S190_stress
    track4_wins_stress = delta_stress > 0

    # -------------------------------------------------------
    # Compute scores per track
    # -------------------------------------------------------
    def compute_score(track_id, empty_age, ratio_at_95, withdrawal_rate, rule400_val_str, is_track4=False):
        score = 0
        husn_105 = empty_age >= 105.0
        if husn_105:
            score += 40
        ratio_95_pct = ratio_at_95 * 100
        if ratio_95_pct >= 100.0:
            score += 30
        elif ratio_95_pct >= 75.0:
            score += 15
        r = float(withdrawal_rate)
        if r < 3.0:
            score += 20
        elif r <= 4.0:
            score += 12
        elif r <= 6.0:
            score += 5
        if is_track4:
            if ratio_95_pct >= 100.0:
                score += 10
            elif ratio_95_pct >= 75.0:
                score += 5
        else:
            if rule400_val_str == "∞":
                score += 10
            else:
                try:
                    r400 = float(rule400_val_str)
                    if r400 > 1.3:
                        score += 10
                    elif r400 >= 1.0:
                        score += 5
                except:
                    score += 0
        return score, husn_105

    # =======================================================================
    # Wealth at 95 — two distinct concepts, kept separate on purpose:
    #   (a) LIQUID portfolio  → drives health/resilience (can it fund life?)
    #   (b) TOTAL net worth    → the bottom line shown on cards (what am I worth?)
    #   (c) STRESS-adjusted    → risk-aware total used for scoring the winner
    # -----------------------------------------------------------------------
    prop_95_rental = float(row_95.get("שווי נדלן מסלול 4", rental_property_start))
    rm_debt_95 = float(row_95.get("משכנתה הפוכה — יתרת חוב", 0.0))
    prop_95_own = float(row_95.get("שווי נדלן", property_value_start))
    pension_asset_95 = float(row_95.get("ערך קצבה נותר", 0.0))

    # (b) Total net worth at 95 — liquid + real estate (− RM debt for track 4)
    total_net_95_190 = b190_95 + prop_95_own
    total_net_95_25  = b25_95  + prop_95_own
    total_net_95_h   = bh_95   + prop_95_own
    total_net_95_rental = br_95 + prop_95_rental - rm_debt_95

    liquid_95_by_track = {1: b190_95, 2: b25_95, 3: bh_95, 4: br_95}
    total_95_by_track  = {1: total_net_95_190, 2: total_net_95_25,
                          3: total_net_95_h, 4: total_net_95_rental}

    # Per-track breakdown dicts (used in card display)
    _fin_port_95 = {1: b190_95, 2: b25_95,  3: bh_95,  4: br_95}
    _prop_net_95 = {
        1: prop_95_own, 2: prop_95_own, 3: prop_95_own,
        4: max(0.0, prop_95_rental - rm_debt_95),
    }

    # Starting total net worth per track — the apples-to-apples baseline for
    # the "vs starting capital" comparison (each track vs where IT began).
    net_for_rental_start = float(rental_inputs.get("net_for_rental", 0.0))
    start_total_123 = baseline_capital + property_value_start + emergency_fund
    start_total_4   = net_for_rental_start + rental_property_start
    start_total_by_track = {1: start_total_123, 2: start_total_123,
                            3: start_total_123, 4: start_total_4}

    # (c) Stress-adjusted net worth at 95 — same philosophy as the stress-test
    # panel, applied uniformly so the score is risk-aware AND apples-to-apples:
    #   • liquid portfolio + emergency fund: full value (truly available)
    #   • pension asset: full value (guaranteed, but illiquid)
    #   • residence (tracks 1-3): full value (stable, you live in it)
    #   • rental property (track 4): 15% haircut − 500K liquidity penalty − RM debt
    sa_95 = {
        1: b190_95 + pension_asset_95 + prop_95_own + emergency_fund,
        2: b25_95  + prop_95_own + emergency_fund,
        3: bh_95   + pension_asset_95 + prop_95_own + emergency_fund,
        4: br_95   + max(0.0, prop_95_rental * 0.85 - 500_000 - rm_debt_95),
    }
    ratio_190_95 = sa_95[1] / max(1.0, start_total_by_track[1])
    ratio_25_95  = sa_95[2] / max(1.0, start_total_by_track[2])
    ratio_h_95   = sa_95[3] / max(1.0, start_total_by_track[3])
    ratio_r_95   = sa_95[4] / max(1.0, start_total_by_track[4])

    score_190, husn_190 = compute_score(1, empty_190, ratio_190_95, pct_190_r, rule400_190_r)
    score_25, husn_25 = compute_score(2, empty_25, ratio_25_95, pct_25_r, rule400_25_r)
    score_h, husn_h = compute_score(3, empty_h, ratio_h_95, pct_h_r, rule400_h_r)
    score_r, husn_r = compute_score(4, empty_r, ratio_r_95, pct_rent_r, "N/A", is_track4=True)


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
    }

    visible_tracks = set(user_inputs.get("visible_tracks", [1, 2, 3, 4]))
    if not visible_tracks:  # safety: show all if none selected
        visible_tracks = {1, 2, 3, 4}

    # p95 carried here = LIQUID portfolio (drives health/preservation badge).
    # Total net worth for display/comparison comes from total_95_by_track.
    tracks_exec = [
        (1, score_190, empty_190, b190_95, husn_190),
        (2, score_25,  empty_25,  b25_95,  husn_25),
        (3, score_h,   empty_h,   bh_95,   husn_h),
        (4, score_r,   empty_r,   br_95,   husn_r),
    ]

    # -------------------------------------------------------
    # Rank: sort by score desc, lower track_id wins ties; filter hidden tracks
    # -------------------------------------------------------
    sorted_by_score = sorted(tracks_exec, key=lambda x: (-x[1], x[0]))
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
    }

    # -------------------------------------------------------
    # Health model: a track is "healthy" only if it lasts past 105
    # AND preserves at least 90% of its starting capital at age 95.
    # Preservation proves resilience — enough buffer if life or
    # markets change, not just leftover for inheritance.
    # -------------------------------------------------------
    def track_health(empty_age, portfolio_95):
        is_resilient = empty_age >= 105.0
        preservation = (portfolio_95 / baseline_capital) if baseline_capital > 0 else 0.0
        is_preserving = preservation >= 0.90
        is_healthy = is_resilient and is_preserving
        return is_resilient, is_preserving, is_healthy

    # Winner declared only if the top track is genuinely healthy —
    # lasts past 105 AND preserves >=90% of starting capital at 95.
    # A real depletion risk means no track wins.
    _top_empty = sorted_by_score[0][2]
    _top_p95 = sorted_by_score[0][3]
    _top_resilient, _top_preserving, _top_healthy = track_health(_top_empty, _top_p95)
    has_winner = _top_healthy

    RANK_CFG = {
        1: {"bg": "#FFFDF0" if has_winner else "#F8F8F8",
            "border": "#E8A000" if has_winner else "#999",
            "th_bg": "#FFF8D6" if has_winner else "#EFEFEF",
            "col_bg": "#FFFDF0" if has_winner else "#F8F8F8",
            "badge": "🏆" if has_winner else "1️⃣",
            "label": "המסלול המומלץ" if has_winner else "מקום ראשון",
            "rank_color": "#c07800" if has_winner else "#555",
            "health_bg": "#e8f8ee", "health_color": "#1a7a3a"},
        2: {"bg": "#F7F8FA", "border": "#607D8B", "th_bg": "#EEF1F5", "col_bg": "#F7F8FA",
            "badge": "🥈", "label": "מקום שני", "rank_color": "#607D8B",
            "health_bg": "#e8f8ee", "health_color": "#1a7a3a"},
        3: {"bg": "#FDF7F3", "border": "#A0522D", "th_bg": "#F5EDE6", "col_bg": "#FDF7F3",
            "badge": "🥉", "label": "מקום שלישי", "rank_color": "#8b4513",
            "health_bg": "#fffbe6", "health_color": "#856400"},
        4: {"bg": "#FFF5F5", "border": "#E53935", "th_bg": "#FFE8E8", "col_bg": "#FFF5F5",
            "badge": "4️⃣", "label": "מקום רביעי", "rank_color": "#c0392b",
            "health_bg": "#fde8e8", "health_color": "#b71c1c"},
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
        st.warning("⚠️ אין מסלול מומלץ — אף מסלול אינו שומר על עצמו עד גיל 105. בכל המסלולים התיק נשחק בצורה מסוכנת. מומלץ לבחון מחדש את ההכנסות וההוצאות.")

    # Reference TOTAL net worth for relative comparison (apples-to-apples:
    # every card compares total wealth, not liquid portfolio).
    winner_total = total_95_by_track[ranked_order[0][1]]
    winner_name = TRACK_NAMES[ranked_order[0][1]]
    second_total = total_95_by_track[ranked_order[1][1]] if len(ranked_order) > 1 else winner_total
    second_name = TRACK_NAMES[ranked_order[1][1]] if len(ranked_order) > 1 else ""

    def delta_block(label, val, ref):
        """Build a comparison line: amount + percent vs a reference."""
        if ref is None or ref == 0:
            return ""
        d = val - ref
        pct = d / abs(ref) * 100
        arr = "↑" if d >= 0 else "↓"
        sgn = "+" if d >= 0 else "−"
        col = "#1a7a3a" if d >= 0 else "#c0392b"
        return (
            f"<div style='font-size:0.62em;color:#999;margin-top:6px;'>{label}</div>"
            f"<div style='font-size:0.74em;color:{col};font-weight:600;'>"
            f"{arr} {format_shekel(abs(int(d)))}{sgn} | {abs(pct):.1f}%{sgn}</div>"
        )

    def build_why_line(is_winner, is_resilient, is_preserving, empty_age, has_pension):
        """Short plain-language reason, tailored to the scenario."""
        if is_winner:
            base = "נשאר איתן עד גיל 105 ומעבר, שומר על ההון שלך גם אם החיים יתארכו או השוק ישתנה"
            if has_pension:
                base += ", ומבטיח לך קצבה חודשית לכל החיים"
            return "✓ " + base
        if not is_resilient:
            reason = "בלי קצבה מובטחת התיק " if not has_pension else "התיק "
            return f"✗ {reason}מתחיל להישחק ועלול להיגמר סביב גיל {empty_age:.0f} — חסר רשת ביטחון לאריכות ימים"
        if not is_preserving:
            return "△ מחזיק עד 105, אך ההון נשחק משמעותית — פחות טווח ביטחון אם דברים ישתנו"
        return "△ מסלול בריא, אך משאיר פחות הון מהמסלול המומלץ"

    # Tracks that include a guaranteed pension (190 and hybrid)
    PENSION_TRACKS = {1, 3}

    # -------------------------------------------------------
    # Rental card bottom — cash flow test
    # -------------------------------------------------------
    def _build_rental_card_bottom(cf, flip_age, always_positive, starts_negative, why_line, why_color, wealth_breakdown_html):
        cf_color = "#1a7a3a" if cf >= 0 else "#c0392b"
        cf_sign  = "+" if cf >= 0 else ""

        if starts_negative:
            flip_html = "<div style='font-size:0.72em;color:#c0392b;font-weight:700;margin-top:4px;'>⚠️ מתחיל בגירעון מיום הפרישה</div>"
        elif always_positive:
            flip_html = "<div style='font-size:0.72em;color:#1a7a3a;font-weight:700;margin-top:4px;'>✅ תזרים חיובי לכל האורך</div>"
        else:
            flip_html = f"<div style='font-size:0.72em;color:#b84c00;font-weight:700;margin-top:4px;'>⚠️ הופך שלילי בגיל {flip_age:.0f}</div>"

        return (
            f"<div style='font-size:0.65em;color:#999;margin-bottom:2px;'>💸 תזרים חודשי נטו בפרישה</div>"
            f"<div style='font-size:1.0em;font-weight:800;color:{cf_color};margin-bottom:0;'>{cf_sign}{format_shekel(int(cf))}</div>"
            f"{flip_html}"
            f"<div style='border-top:1px solid #e8e8e8;margin-top:8px;padding-top:8px;'>"
            f"{wealth_breakdown_html}"
            f"</div>"
            f"<div style='font-size:0.72em;color:{why_color};font-weight:600;margin-top:10px;line-height:1.4;"
            f"border-top:1px dashed #ddd;padding-top:8px;'>{why_line}</div>"
        )

    # Cards: render in reverse rank order so rank1 is rightmost (Streamlit LTR columns)
    n_visible = max(1, len(ranked_order))
    cols = st.columns(n_visible)
    for col_idx, (rank, track_id, score, empty_age, portfolio_95, husn) in enumerate(reversed(ranked_order)):
        pc = track_pros_cons[track_id]
        rc = RANK_CFG[rank]
        is_winner = rank == 1 and has_winner
        is_resilient, is_preserving, is_healthy = track_health(empty_age, portfolio_95)
        health = get_health_label(is_resilient, is_preserving)
        health_bg, health_color = get_health_style(is_resilient, is_preserving)
        res_color = "#1a7a3a" if empty_age >= 105.0 else ("#b84c00" if empty_age >= 90 else "#c0392b")
        res_label = "105+" if empty_age >= 105.0 else f"גיל {empty_age:.0f}"

        # Total net worth at 95 — the bottom-line figure shown & compared on cards.
        total_95 = total_95_by_track[track_id]

        # Comparison 1: vs the leading alternative (total wealth)
        if is_winner:
            cmp_label = f"מול הבא בתור ({second_name})"
            cmp_html = delta_block(cmp_label, total_95, second_total)
        else:
            cmp_label = "מול המסלול המומלץ" if has_winner else "מול המסלול המוביל"
            cmp_html = delta_block(cmp_label, total_95, winner_total)

        # Comparison 2: vs this track's own starting net worth
        base_html = delta_block("מול ההון ההתחלתי", total_95, start_total_by_track[track_id])

        why_line = build_why_line(is_winner, is_resilient, is_preserving, empty_age, track_id in PENSION_TRACKS)
        why_color = "#1a7a3a" if (is_winner or is_healthy) else ("#856400" if is_resilient else "#b71c1c")

        if is_winner:
            shadow = "0 12px 40px rgba(232,160,0,0.30), 0 4px 16px rgba(0,0,0,0.12)"
            border_top = "5px solid #E8A000"
            outline = "outline: 2px solid #E8A000; outline-offset: 2px;"
            winner_ribbon = (
                f"<div style='text-align:center;margin-bottom:10px;'>"
                f"<span style='display:inline-block;background:linear-gradient(135deg,#E8A000,#f5c842);"
                f"color:#fff;padding:4px 18px;border-radius:20px;font-size:0.72em;font-weight:800;"
                f"white-space:nowrap;box-shadow:0 3px 10px rgba(232,160,0,0.4);letter-spacing:0.05em;'>"
                f"⭐ המסלול המומלץ</span></div>"
            )
        else:
            shadow = "0 2px 10px rgba(0,0,0,0.07)"
            border_top = f"4px solid {rc['border']}"
            outline = ""
            winner_ribbon = "<div style='height:30px;'></div>"

        fin_port = _fin_port_95[track_id]
        prop_net = _prop_net_95[track_id]
        prop_label = "🏠 הון עצמי בנדל\"ן בגיל 95" if track_id == 4 else "🏠 שווי נדלן בגיל 95"

        wealth_breakdown_html = (
            f"<div style='font-size:0.62em;color:#999;margin-bottom:1px;'>💰 תיק פיננסי בגיל 95</div>"
            f"<div style='font-size:0.85em;font-weight:600;color:#444;margin-bottom:4px;'>{format_shekel(int(fin_port))}</div>"
            f"<div style='font-size:0.62em;color:#999;margin-bottom:1px;'>{prop_label}</div>"
            f"<div style='font-size:0.85em;font-weight:600;color:#444;margin-bottom:6px;'>{format_shekel(int(prop_net))}</div>"
            f"<div style='font-size:0.62em;color:#555;margin-bottom:1px;font-weight:600;'>📊 סך נכסים בגיל 95</div>"
            f"<div style='font-size:1.05em;font-weight:800;color:#1a1a2e;'>{format_shekel(int(total_95))}</div>"
        )

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
            f"🟢 חסין = התיק הנזיל מחזיק מעל גיל 105 ושומר על 90%+ מההון בגיל 95. "
            f"🟡 מחזיק = מחזיק מעל 105 אך נשחק מתחת ל-90%. "
            f"🔴 נשחק = התיק הנזיל עלול להיגמר לפני גיל 105."
            f"</span></span></span></div>"
            f"<div style='text-align:center;font-size:0.74em;color:{res_color};font-weight:700;margin-bottom:4px;'>"
            f"⏳ מחזיק עד {res_label}</div>"
            f"</div>"
            f"<div style='border-top:1px solid #e8e8e8;padding-top:10px;'>"
            + (
                # Track 4: cashflow headline + shared wealth breakdown
                _build_rental_card_bottom(rental_cashflow_at_retire, rental_flip_age,
                                          rental_always_positive, rental_starts_negative,
                                          why_line, why_color, wealth_breakdown_html)
                if track_id == 4 else
                wealth_breakdown_html
                + cmp_html
                + base_html
                + f"<div style='font-size:0.72em;color:{why_color};font-weight:600;margin-top:10px;line-height:1.4;"
                f"border-top:1px dashed #ddd;padding-top:8px;'>{why_line}</div>"
            )
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
    bool_preserve_95_190 = "✅ כן" if b190_95 >= baseline_capital else "❌ לא"
    bool_preserve_95_25  = "✅ כן" if b25_95  >= baseline_capital else "❌ לא"
    bool_preserve_95_h   = "✅ כן" if bh_95   >= baseline_capital else "❌ לא"
    bool_preserve_95_r   = "✅ כן" if br_95 > 0 else "❌ לא"

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
            "הוצאות חודשיות":  format_shekel(int(exp_retire + rent_paid_r)),
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
        "הוצאות חודשיות": f"הוצאות חודשיות נומינליות (מוצמדות לאינפלציה) בגיל {retire_age:.1f}. מסלול 4: כולל גם שכ\"ד שמשולם על הדירה הנוכחית.",
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

    # Preservation % at age 95 (the core health metric, shown numerically)
    def fmt_preservation(portfolio_95):
        pct = (portfolio_95 / baseline_capital * 100) if baseline_capital > 0 else 0
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
            "שימור הון":    fmt_preservation(b190_95),
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
            "שימור הון":    fmt_preservation(b25_95),
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
            "שימור הון":    fmt_preservation(bh_95),
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
            "הוצאות חודשיות": format_shekel(int(exp_check + rent_paid_c)),
            "משיכה / תזרים": fmt_cashflow(nn_rent_c, cashflow=rental_cashflow_at_check, withdrawal_pct=pct_rent_c),
            "גירעון מצטבר":  fmt_cum_deficit(cum_deficit_r, months_deficit_r),
            "עד איזה גיל הכסף מחזיק?": fmt_lifespan(empty_r),
            "שימור הון":    fmt_preservation(br_95),
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
        ("כמה מההון ההתחלתי נשמר בגיל 95?",         "שימור הון"),
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
        "הוצאות חודשיות": f"הוצאות חודשיות בגיל {check_age:.1f} לאחר הצמדה לאינפלציה. כולל תוספת מטפל מגיל 85 אם הוגדרה.",
        "משיכה / תזרים":  f"כמה יש להוציא מהתיק בגיל {check_age:.1f} = הוצאות פחות הכנסות. אם התיק אזל — הגירעון מופיע בשורת הגירעון המצטבר.",
        "גירעון מצטבר":   f"סכום כל החסרים החודשיים לאחר שהתיק הגיע לאפס, עד גיל {check_age:.0f}. מייצג כמה כסף חיצוני (ילדים, עזרה) נדרש לכיסוי. אפס = אין גירעון.",
    }
    TOOLTIPS_ACTUARIAL_2 = {
        "עד איזה גיל הכסף מחזיק?": "גיל מיצוי חסכונות: הגיל שבו יתרת התיק הנזיל מגיעה לאפס לחלוטין. מסלול 4: החסכונות אזלו — הדירה ממשיכה לייצר הכנסה אבל אין יותר כרית נזילה. אם לא נגמר עד 105 — מסומן ✅ לא נשחק.",
        "שימור הון":    f"אחוז מההון ההתחלתי ({format_shekel(int(baseline_capital))}) שנשאר בתיק בגיל 95. מעל 90% = מצוין. 75-90% = טוב. מתחת ל-75% = שחיקה משמעותית.",
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

    # -------------------------------------------------------
    # Balanced Stress-Test display (track 4 visible only)
    # -------------------------------------------------------
    if 4 in visible_tracks and 1 in visible_tracks:
        st.markdown("<br/>", unsafe_allow_html=True)
        with st.expander("⚖️ מבחן עמידות — מסלול 4 מול מסלול 190", expanded=True):
            verdict_color  = "#1a7a3a" if track4_wins_stress else "#1a3a7a"
            verdict_icon   = "✅" if track4_wins_stress else "🔵"
            verdict_label  = "מסלול 4 מנצח גם תחת לחץ" if track4_wins_stress else "מסלול 190 שומר על עדיפות"
            delta_fmt      = format_shekel(int(abs(delta_stress)))
            direction_txt  = f"יתרון {delta_fmt} למסלול 4" if track4_wins_stress else f"יתרון {delta_fmt} למסלול 190"

            st.markdown(
                f"<div style='background:#f8f9fc;border:1px solid #d0d4e8;border-radius:8px;"
                f"padding:16px 20px;direction:rtl;font-family:sans-serif;'>"
                f"<div style='font-size:1.05em;font-weight:700;color:{verdict_color};margin-bottom:12px;'>"
                f"{verdict_icon} {verdict_label} — {direction_txt}"
                f"</div>"
                f"<table style='width:100%;border-collapse:collapse;font-size:0.88em;'>"
                f"<tr style='border-bottom:1px solid #dde;'>"
                f"<td style='padding:5px 8px;color:#555;'>S₄ (מסלול 4 תחת לחץ)</td>"
                f"<td style='padding:5px 8px;font-weight:700;'>{format_shekel(int(S4_stress))}</td>"
                f"<td style='padding:5px 8px;color:#888;font-size:0.82em;'>תיק + נדל\"ן×0.85 − 500K − חוב</td>"
                f"</tr>"
                f"<tr style='border-bottom:1px solid #dde;'>"
                f"<td style='padding:5px 8px;color:#555;'>S₁₉₀ (מסלול 190 עם בונוס)</td>"
                f"<td style='padding:5px 8px;font-weight:700;'>{format_shekel(int(S190_stress))}</td>"
                f"<td style='padding:5px 8px;color:#888;font-size:0.82em;'>תיק + קצבה + נדל\"ן×1.05 + חירום</td>"
                f"</tr>"
                f"<tr>"
                f"<td style='padding:5px 8px;font-weight:700;'>Δ (הפרש)</td>"
                f"<td style='padding:5px 8px;font-weight:700;color:{verdict_color};'>"
                f"{'+ ' if delta_stress >= 0 else ''}{format_shekel(int(delta_stress))}</td>"
                f"<td style='padding:5px 8px;color:#888;font-size:0.82em;'>"
                f"{'מסלול 4 עדיף' if delta_stress >= 0 else 'מסלול 190 עדיף'}</td>"
                f"</tr>"
                f"</table>"
                f"<div style='margin-top:10px;font-size:0.78em;color:#888;'>"
                f"הלחץ: נדל\"ן מסלול 4 מוזל ב-15% + קנס 500K. מסלול 190 מוגבה ב-5% + קרן חירום."
                f" אם Δ חיובי — מסלול 4 ניצח גם בתרחיש שמרני."
                f"</div></div>",
                unsafe_allow_html=True
            )
