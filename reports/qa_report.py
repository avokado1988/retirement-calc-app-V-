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
        .styled-table { width: 100% !important; direction: rtl !important; text-align: right !important; border-collapse: collapse; margin: 15px 0; font-family: sans-serif; }
        .styled-table th { background-color: #2a2a3e; color: #e0e0e0; text-align: right !important; padding: 10px !important; font-weight: bold; border-bottom: 2px solid #444; }
        .styled-table td { padding: 8px !important; text-align: right !important; border-bottom: 1px solid #333; }
        .styled-table tbody th { background-color: #1e1e2e; color: #c0c0c0; font-weight: 600; padding: 8px !important; text-align: right !important; border-bottom: 1px solid #333; border-left: 2px solid #444; }
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
    # Track 4: use user-defined current property value (the retained apartment)
    rental_property_start = float(rental_inputs.get("current_property_value", wealth.get("net_sale", property_value_start)))

    # -------------------------------------------------------
    # Helper: get row at target age
    # -------------------------------------------------------
    def get_row(target_age):
        sub = df_full[df_full["גיל"] >= target_age]
        return sub.iloc[0] if not sub.empty else df_full.iloc[-1]

    row_retire = get_row(retire_age)
    row_check = get_row(check_age)

    # Read property value directly from engine column (tracks 1-3: new apartment)
    property_value_retire = float(row_retire.get("שווי נדלן", property_value_start))
    property_value_check = float(row_check.get("שווי נדלן", property_value_start))
    # Track 4: retained apartment, valued independently from user input
    years_to_retire = retire_age - start_age
    years_to_check = check_age - start_age
    rental_prop_retire = rental_property_start * ((1 + appreciation_rate) ** years_to_retire)
    rental_prop_check = rental_property_start * ((1 + appreciation_rate) ** years_to_check)

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

    nn_190_r = max(0.0, exp_retire - (base_income_retire + pension_retire))
    nn_25_r = max(0.0, exp_retire - base_income_retire)
    nn_h_r = nn_190_r
    nn_rent_r = max(0.0, (exp_retire + rent_paid_r) - (base_income_retire + net_rental_r))

    def rule400(bal, nn): return f"{bal / (nn * 400):.2f}" if nn > 0 else "∞"
    def emer(nn): return f"{emergency_fund / (nn * 12):.1f}" if nn > 0 else "∞"
    def wpct(nn, bal): return (nn * 12) / bal * 100 if bal > 0 else 0.0
    def fmt_withdrawal(nn):
        return wrap_html_style(f"−{format_shekel(int(nn))}", "color: #ff6666; font-weight: bold;") if nn > 0 else format_shekel(0)
    def fmt_with_delta(val, baseline, pension_component=None):
        if baseline <= 0: return format_shekel(int(val))
        delta_pct = (val - baseline) / baseline * 100
        arrow = "↑" if delta_pct >= 0 else "↓"
        if delta_pct > 20:
            color = "#00e676"
        elif delta_pct >= 0:
            color = "#2ecc71"
        else:
            color = "#ff5555"
        sign = "+" if delta_pct >= 0 else ""
        pension_note = ""
        if pension_component is not None:
            pension_note = f"<br/><span style='color:#aaa; font-size:0.78em;'>מתוכם {format_shekel(int(pension_component))} ערך קצבה</span>"
        return f"{format_shekel(int(val))}<br/><span style='color:{color}; font-size:0.85em;'>({arrow}{sign}{delta_pct:.1f}%)</span>{pension_note}"

    def fmt_with_pension_note(val, pension_component=None):
        base = format_shekel(int(val))
        if pension_component is not None:
            note = f"<br/><span style='color:#aaa; font-size:0.78em;'>מתוכם {format_shekel(int(pension_component))} ערך קצבה</span>"
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

    tw_190_r = b190_r + pension_asset_retire + property_value_retire + emergency_fund
    tw_25_r = b25_r + property_value_retire + emergency_fund
    tw_h_r = bh_r + pension_asset_retire + property_value_retire + emergency_fund
    tw_rent_r = br_r + rental_prop_retire + emergency_fund

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
    nn_rent_c = max(0.0, (exp_check + rent_paid_c) - (base_income_check + net_rental_c))

    pct_190_c = wpct(nn_190_c, b190_c)
    pct_25_c = wpct(nn_25_c, b25_c)
    pct_h_c = wpct(nn_h_c, bh_c)
    pct_rent_c = wpct(nn_rent_c, br_c)

    inherit_190_c = b190_c + pension_asset_check
    inherit_h_c = bh_c + pension_asset_check

    tw_190_c = b190_c + pension_asset_check + property_value_check + emergency_fund
    tw_25_c = b25_c + property_value_check + emergency_fund
    tw_h_c = bh_c + pension_asset_check + property_value_check + emergency_fund
    tw_rent_c = br_c + rental_prop_check + emergency_fund

    bool_preserve = lambda bal: "✅ כן" if bal > baseline_capital else "❌ לא"

    # -------------------------------------------------------
    # Extract values at age 95 (for preservation check)
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

    empty_190 = find_empty_age("צבירה תיקון 190")
    empty_25 = find_empty_age("צבירה מסלול ריאלי")
    empty_h = find_empty_age("צבירה מסלול היברידי")
    empty_r = find_empty_age("צבירה מסלול שכירות")

    fmt_empty = lambda a: "105+ (חסין)" if a >= 105.0 else f"גיל {a:.1f}"

    recovery_190 = find_recovery_age("צבירה תיקון 190")
    recovery_25 = find_recovery_age("צבירה מסלול ריאלי")
    recovery_h = find_recovery_age("צבירה מסלול היברידי")
    recovery_r = find_recovery_age("צבירה מסלול שכירות")

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
    # Executive Summary: compute scores per track
    # -------------------------------------------------------
    def compute_score(track_id, empty_age, ratio_at_95, withdrawal_rate, rule400_val_str, is_track4=False):
        """
        track_id: 1-4
        empty_age: age portfolio empties (120 = never)
        ratio_at_95: portfolio_at_95 / baseline_capital (float ratio, not pct)
        withdrawal_rate: annual withdrawal % (float)
        rule400_val_str: rule400 string value
        is_track4: True for track 4 (no rule400)
        """
        score = 0

        # 40 pts: resiliency to 105
        husn_105 = empty_age >= 105.0
        if husn_105:
            score += 40

        # 30 pts: preservation at 95
        ratio_95_pct = ratio_at_95 * 100
        if ratio_95_pct >= 100.0:
            score += 30
        elif ratio_95_pct >= 75.0:
            score += 15
        else:
            score += 0

        # 20 pts: withdrawal rate (use thresholds)
        r = float(withdrawal_rate)
        if r < 3.0:
            score += 20
        elif r <= 4.0:
            score += 12
        elif r <= 6.0:
            score += 5
        else:
            score += 0

        # 10 pts: rule400 (skip for track 4, redistribute to שימור)
        if is_track4:
            # redistribute 10 pts to preservation (add bonus if ratio >= 100%)
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
                    else:
                        score += 0
                except:
                    score += 0

        return score, husn_105

    def get_health_label(score):
        if score >= 80:
            return "🟢 חסין"
        elif score >= 60:
            return "🟡 יציב"
        elif score >= 40:
            return "🟠 מוגבל"
        else:
            return "🔴 בסיכון"

    def get_score_color(score):
        if score >= 80:
            return "#006600"
        elif score >= 60:
            return "#856400"
        elif score >= 40:
            return "#c45c00"
        else:
            return "#990000"

    def get_card_colors(score):
        if score >= 80:
            return "#e6f9e6", "#006600"
        elif score >= 60:
            return "#fffbe6", "#856400"
        elif score >= 40:
            return "#fff3e6", "#c45c00"
        else:
            return "#fce8e8", "#990000"

    # Ratio at 95 for each track (as fraction, not pct)
    ratio_190_95 = b190_95 / max(1.0, baseline_capital)
    ratio_25_95 = b25_95 / max(1.0, baseline_capital)
    ratio_h_95 = bh_95 / max(1.0, baseline_capital)
    ratio_r_95 = br_95 / max(1.0, baseline_capital)  # for track4: positive = solvent

    score_190, husn_190 = compute_score(1, empty_190, ratio_190_95, pct_190_r, rule400_190_r)
    score_25, husn_25 = compute_score(2, empty_25, ratio_25_95, pct_25_r, rule400_25_r)
    score_h, husn_h = compute_score(3, empty_h, ratio_h_95, pct_h_r, rule400_h_r)
    score_r, husn_r = compute_score(4, empty_r, ratio_r_95, pct_rent_r, "N/A", is_track4=True)

    # Pros/cons per track (hardcoded Hebrew)
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

    def resiliency_label_for_card(empty_age):
        return "105+ (חסין)" if empty_age >= 105.0 else f"גיל {empty_age:.1f}"

    tracks_exec = [
        (1, score_190, empty_190, b190_95, husn_190),
        (2, score_25, empty_25, b25_95, husn_25),
        (3, score_h, empty_h, bh_95, husn_h),
        (4, score_r, empty_r, br_95, husn_r),
    ]

    # -------------------------------------------------------
    # Render Executive Summary
    # -------------------------------------------------------
    st.markdown("<h3 style='text-align: center;'>🧭 סיכום מנהלים — השוואת מסלולים</h3>", unsafe_allow_html=True)

    best_score = max(score for _, score, _, _, _ in tracks_exec)
    # Single winner: lowest track_id among those with best score
    winner_id = min(tid for tid, sc, _, _, _ in tracks_exec if sc == best_score)

    # Build ordered list (reversed = RTL: track4, track3, track2, track1)
    ordered_tracks = list(reversed(tracks_exec))

    # Equal columns — winner distinguished by styling, not width
    cols = st.columns(4)

    for col_idx, (track_id, score, empty_age, portfolio_95, husn) in enumerate(ordered_tracks):
        pc = track_pros_cons[track_id]
        health = get_health_label(score)
        score_color = get_score_color(score)
        _, border_color = get_card_colors(score)
        res_label = resiliency_label_for_card(empty_age)
        is_winner = track_id == winner_id
        res_color = "#4dbb4d" if empty_age >= 105.0 else ("#ff8c42" if empty_age >= 90 else "#ff4444")

        score_font = "2.8em" if is_winner else "2.2em"
        border_width = "4px" if is_winner else "3px"
        glow = "box-shadow:0 0 20px rgba(240,192,64,0.25),0 2px 10px rgba(0,0,0,0.4);" if is_winner else "box-shadow:0 2px 8px rgba(0,0,0,0.3);"
        winner_badge = "<div style='display:inline-block;background:rgba(240,192,64,0.15);color:#f0c040;font-size:0.68em;padding:2px 10px;border-radius:10px;font-weight:700;letter-spacing:0.03em;'>🏆 המומלץ</div><div style='height:6px;'></div>" if is_winner else "<div style='height:24px;'></div>"

        delta_95 = portfolio_95 - baseline_capital
        delta_pct_95 = (delta_95 / baseline_capital * 100) if baseline_capital > 0 else 0
        arrow = "↑" if delta_95 >= 0 else "↓"
        delta_color = "#4dbb4d" if delta_95 >= 0 else "#ff6666"
        sign = "+" if delta_95 >= 0 else "−"
        abs_delta = abs(int(delta_95))
        abs_pct = abs(delta_pct_95)

        card_html = (
            f"<div style='border-top:{border_width} solid {border_color};border-radius:10px;padding:16px 16px 18px 16px;"
            f"background:#1a1a2e;{glow}text-align:center;direction:rtl;font-family:sans-serif;color:#e0e0e0;"
            f"min-height:260px;display:flex;flex-direction:column;justify-content:space-between;'>"
            f"<div>"
            f"{winner_badge}"
            f"<div style='font-size:0.95em;font-weight:700;color:#f0f0f0;line-height:1.3;margin-bottom:12px;'>{pc['name']}</div>"
            f"<div style='font-size:{score_font};font-weight:900;color:{score_color};line-height:1;'>{score}"
            f"<span style='font-size:0.38em;color:#666;font-weight:400;'>/100</span></div>"
            f"<div style='font-size:0.85em;color:#ccc;margin-top:6px;margin-bottom:16px;'>{health}</div>"
            f"</div>"
            f"<div style='border-top:1px solid #2a2a40;padding-top:12px;text-align:right;'>"
            f"<div style='font-size:0.68em;color:#666;margin-bottom:2px;'>⏳ הכסף מחזיק עד</div>"
            f"<div style='font-size:0.88em;color:{res_color};font-weight:700;margin-bottom:12px;'>{res_label}</div>"
            f"<div style='font-size:0.68em;color:#666;margin-bottom:2px;'>💰 תיק בגיל 95</div>"
            f"<div style='font-size:0.92em;color:#f0f0f0;font-weight:700;'>{format_shekel(int(portfolio_95))}</div>"
            f"<div style='font-size:0.72em;color:{delta_color};margin-top:3px;'>{arrow} {sign}{format_shekel(abs_delta)}"
            f"<span style='color:#555;'> | </span>"
            f"<span style='color:{delta_color};'>{sign}{abs_pct:.1f}%</span></div>"
            f"<div style='font-size:0.65em;color:#555;margin-top:1px;'>מ-{format_shekel(int(baseline_capital))}</div>"
            f"</div></div>"
        )

        with cols[col_idx]:
            st.markdown(card_html, unsafe_allow_html=True)
            with st.expander("יתרונות וסיכונים"):
                st.markdown(f"<span style='color:#4dbb4d;'>✅ {pc['pro1']}</span>", unsafe_allow_html=True)
                st.markdown(f"<span style='color:#4dbb4d;'>✅ {pc['pro2']}</span>", unsafe_allow_html=True)
                st.markdown(f"<span style='color:#ff8c42;'>⚠️ {pc['con1']}</span>", unsafe_allow_html=True)
                st.markdown(f"<span style='color:#ff8c42;'>⚠️ {pc['con2']}</span>", unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # -------------------------------------------------------
    # Table 1: At retirement — collapsible, 4 key rows + expander
    # -------------------------------------------------------

    # All data pre-built per column
    t1_cols = {
        "190 + קצבה מזערית": {
            "הון כולל":        fmt_with_pension_note(inherit_190_r, pension_asset_retire),
            "משיכה חודשית":    fmt_withdrawal(nn_190_r),
            "קצב משיכה":       wrap_html_style(f"{pct_190_r:.2f}%", get_withdrawal_style(pct_190_r)),
            "סך נכסים":        format_shekel(tw_190_r),
            "תיק נזיל":        format_shekel(b190_r),
            "שווי נדלן":       format_shekel(property_value_retire),
            "קצבאות חודשיות":  format_shekel(base_income_retire + pension_retire),
            "חוק 400":         wrap_html_style(rule400(b190_r, nn_190_r), get_400_rule_style(rule400(b190_r, nn_190_r))),
            "קרן חירום":       wrap_html_style(emer(nn_190_r), get_emergency_style(emer(nn_190_r))),
        },
        "25% ריאלי (ללא קצבה)": {
            "הון כולל":        format_shekel(b25_r),
            "משיכה חודשית":    fmt_withdrawal(nn_25_r),
            "קצב משיכה":       wrap_html_style(f"{pct_25_r:.2f}%", get_withdrawal_style(pct_25_r)),
            "סך נכסים":        format_shekel(tw_25_r),
            "תיק נזיל":        format_shekel(b25_r),
            "שווי נדלן":       format_shekel(property_value_retire),
            "קצבאות חודשיות":  format_shekel(base_income_retire),
            "חוק 400":         wrap_html_style(rule400(b25_r, nn_25_r), get_400_rule_style(rule400(b25_r, nn_25_r))),
            "קרן חירום":       wrap_html_style(emer(nn_25_r), get_emergency_style(emer(nn_25_r))),
        },
        "25% ריאלי + קצבה מזערית": {
            "הון כולל":        fmt_with_pension_note(inherit_h_r, pension_asset_retire),
            "משיכה חודשית":    fmt_withdrawal(nn_h_r),
            "קצב משיכה":       wrap_html_style(f"{pct_h_r:.2f}%", get_withdrawal_style(pct_h_r)),
            "סך נכסים":        format_shekel(tw_h_r),
            "תיק נזיל":        format_shekel(bh_r),
            "שווי נדלן":       format_shekel(property_value_retire),
            "קצבאות חודשיות":  format_shekel(base_income_retire + pension_retire),
            "חוק 400":         wrap_html_style(rule400(bh_r, nn_h_r), get_400_rule_style(rule400(bh_r, nn_h_r))),
            "קרן חירום":       wrap_html_style(emer(nn_h_r), get_emergency_style(emer(nn_h_r))),
        },
        "שכירות": {
            "הון כולל":        format_shekel(br_r),
            "משיכה חודשית":    fmt_withdrawal(nn_rent_r),
            "קצב משיכה":       'ל"ר',
            "סך נכסים":        format_shekel(tw_rent_r),
            "תיק נזיל":        format_shekel(br_r),
            "שווי נדלן":       format_shekel(rental_prop_retire),
            "קצבאות חודשיות":  format_shekel(base_income_retire),
            "חוק 400":         'ל"ר',
            "קרן חירום":       'ל"ר',
        },
    }

    KEY_ROWS_1 = [
        ("מה שווי ההון הכולל כולל הקצבה?",   "הון כולל"),
        ("כמה אצטרך למשוך מהתיק כל חודש?",   "משיכה חודשית"),
        ("מה קצב המשיכה השנתי מהתיק?",       "קצב משיכה"),
        ("מה סך כלל הנכסים שלי?",             "סך נכסים"),
    ]
    DETAIL_ROWS_1 = [
        ("מה גובה התיק הנזיל ביום הפרישה?",   "תיק נזיל"),
        ("מה שווי הנדל\"ן שלי בפרישה?",       "שווי נדלן"),
        ("מה סך הקצבאות החודשיות שלי?",       "קצבאות חודשיות"),
        ("מה מדד החסינות של התיק (חוק 400)?", "חוק 400"),
        ("כמה שנים קרן החירום מכסה?",          "קרן חירום"),
    ]

    def build_df(row_list, data_dict):
        track_keys = list(data_dict.keys())
        rows = {"שאלה": [r[0] for r in row_list]}
        for tk in track_keys:
            rows[tk] = [data_dict[tk][r[1]] for r in row_list]
        return pd.DataFrame(rows)

    with st.expander(f"📊 מצב ביום הפרישה — גיל {retire_age:.1f}", expanded=True):
        st.markdown(
            build_df(KEY_ROWS_1, t1_cols).set_index("שאלה").rename_axis(None).to_html(escape=False, classes="styled-table"),
            unsafe_allow_html=True
        )
        with st.expander("פרטים נוספים"):
            st.markdown(
                build_df(DETAIL_ROWS_1, t1_cols).set_index("שאלה").rename_axis(None).to_html(escape=False, classes="styled-table"),
                unsafe_allow_html=True
            )

    # -------------------------------------------------------
    # Table 2: At check_age — collapsible, 4 key rows + expander
    # -------------------------------------------------------
    bool_preserve_95_190 = "✅ כן" if b190_95 >= baseline_capital else "❌ לא"
    bool_preserve_95_25  = "✅ כן" if b25_95  >= baseline_capital else "❌ לא"
    bool_preserve_95_h   = "✅ כן" if bh_95   >= baseline_capital else "❌ לא"
    bool_preserve_95_r   = "✅ כן" if br_95 > 0 else "❌ לא"

    t2_cols = {
        "190 + קצבה מזערית": {
            "הון כולל":     fmt_with_delta(inherit_190_c, baseline_capital, pension_component=int(pension_asset_check)),
            "משיכה חודשית": fmt_withdrawal(nn_190_c),
            "קצב משיכה":    wrap_html_style(f"{pct_190_c:.2f}%", get_withdrawal_style(pct_190_c)),
            "סך נכסים":     format_shekel(tw_190_c),
            "שימור הון":    wrap_html_style(bool_preserve_95_190, get_boolean_style(bool_preserve_95_190)),
            "גיל התאוששות": recovery_190,
        },
        "25% ריאלי (ללא קצבה)": {
            "הון כולל":     fmt_with_delta(b25_c, baseline_capital),
            "משיכה חודשית": fmt_withdrawal(nn_25_c),
            "קצב משיכה":    wrap_html_style(f"{pct_25_c:.2f}%", get_withdrawal_style(pct_25_c)),
            "סך נכסים":     format_shekel(tw_25_c),
            "שימור הון":    wrap_html_style(bool_preserve_95_25, get_boolean_style(bool_preserve_95_25)),
            "גיל התאוששות": recovery_25,
        },
        "25% ריאלי + קצבה מזערית": {
            "הון כולל":     fmt_with_delta(inherit_h_c, baseline_capital, pension_component=int(pension_asset_check)),
            "משיכה חודשית": fmt_withdrawal(nn_h_c),
            "קצב משיכה":    wrap_html_style(f"{pct_h_c:.2f}%", get_withdrawal_style(pct_h_c)),
            "סך נכסים":     format_shekel(tw_h_c),
            "שימור הון":    wrap_html_style(bool_preserve_95_h, get_boolean_style(bool_preserve_95_h)),
            "גיל התאוששות": recovery_h,
        },
        "שכירות": {
            "הון כולל":     fmt_with_delta(br_c, baseline_capital),
            "משיכה חודשית": fmt_withdrawal(nn_rent_c),
            "קצב משיכה":    wrap_html_style(f"{pct_rent_c:.2f}%", get_withdrawal_style(pct_rent_c)),
            "סך נכסים":     format_shekel(tw_rent_c),
            "שימור הון":    wrap_html_style(bool_preserve_95_r, get_boolean_style(bool_preserve_95_r)),
            "גיל התאוששות": recovery_r,
        },
    }

    KEY_ROWS_2 = [
        ("מה שווי ההון הכולל כולל הקצבה?",  "הון כולל"),
        ("כמה אמשוך מהתיק כל חודש?",         "משיכה חודשית"),
        ("מה קצב המשיכה בגיל זה?",           "קצב משיכה"),
        ("מה סך כלל הנכסים שלי?",             "סך נכסים"),
    ]
    DETAIL_ROWS_2 = [
        ("האם נשמר ההון ההתחלתי עד גיל 95?",          "שימור הון"),
        ("מאיזה גיל התיק עולה מעל ההון הראשוני?",     "גיל התאוששות"),
    ]

    with st.expander(f"🔮 מצב בגיל נבדק — גיל {check_age:.1f}", expanded=True):
        st.markdown(
            build_df(KEY_ROWS_2, t2_cols).set_index("שאלה").rename_axis(None).to_html(escape=False, classes="styled-table"),
            unsafe_allow_html=True
        )
        with st.expander("פרטים נוספים"):
            st.markdown(
                build_df(DETAIL_ROWS_2, t2_cols).set_index("שאלה").rename_axis(None).to_html(escape=False, classes="styled-table"),
                unsafe_allow_html=True
            )

