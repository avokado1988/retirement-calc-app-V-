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
        .styled-table th { background-color: #f3f4f6; color: #1f2937; text-align: right !important; padding: 10px !important; font-weight: bold; border-bottom: 2px solid #e5e7eb; }
        .styled-table td { padding: 8px !important; text-align: right !important; border-bottom: 1px solid #f3f4f6; }
        .styled-table thead { display: none; }
        </style>
    """, unsafe_allow_html=True)

    df_full = results["df_full"]
    timeline = user_inputs.get("timeline", {})
    wealth = user_inputs.get("wealth", {})
    real_tax_25 = user_inputs.get("real_tax_25", {})

    start_age = float(timeline.get("start_age", 65.5))
    check_age = float(timeline.get("check_age", 87.0))
    retire_age = float(timeline.get("retirement_age", start_age))

    baseline_capital = float(real_tax_25.get("net_for_real_pathway") or 3340000)
    emergency_fund = float(wealth.get("emergency_fund", 0))
    property_value_start = float(wealth.get("new_apartment_cost", 0))
    appreciation_rate = float(wealth.get("property_appreciation", 0))

    # -------------------------------------------------------
    # Helper: get row at target age
    # -------------------------------------------------------
    def get_row(target_age):
        sub = df_full[df_full["גיל"] >= target_age]
        return sub.iloc[0] if not sub.empty else df_full.iloc[-1]

    row_retire = get_row(retire_age)
    row_check = get_row(check_age)

    # Read property value directly from engine column
    property_value_retire = float(row_retire.get("שווי נדלן", property_value_start))
    property_value_check = float(row_check.get("שווי נדלן", property_value_start))

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
    tw_rent_r = br_r + float(row_retire.get("שווי נדלן מסלול 4", property_value_retire)) + emergency_fund

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
    tw_rent_c = br_c + float(row_check.get("שווי נדלן מסלול 4", property_value_check)) + emergency_fund

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
            "name": "מסלול 1 — תיקון 190",
            "pro1": "קצבה מובטחת לכל החיים — גם בגיל 105 הכסף לא נגמר. ביטוח אריכות ימים.",
            "pro2": "מיסוי נמוך — 15% נומינלי בלבד",
            "con1": "פחות גמיש — לא ניתן לשבור את הקצבה לצורך הוצאה גדולה",
            "con2": "דורש הון גדול — צריך לפחות ₪1M+ לקצבה משמעותית",
        },
        2: {
            "name": "מסלול 2 — 25% ריאלי",
            "pro1": "כל הכסף נזיל — ניתן למשוך כל סכום בכל עת, ירושה מקסימלית",
            "pro2": "כל ההון עובד בשוק — ללא כיסוח לקצבה",
            "con1": "אין גיבוי לאריכות ימים — אם הכסף ייגמר בגיל 92 אין עוד מקורות",
            "con2": "תלוי לחלוטין בביצועי השוק",
        },
        3: {
            "name": "מסלול 3 — היברידי",
            "pro1": "שילוב קצבה קטנה + נזילות — רצפת ביטחון עם יכולת תמרון",
            "pro2": "מאזן בין ביטחון וגמישות",
            "con1": "מורכב — טעות במקדם ההמרה גוררת הפסד שקשה להחזיר",
            "con2": "הון נזיל קטן יותר ממסלול 2 — פחות ירושה",
        },
        4: {
            "name": "מסלול 4 — שכירות",
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
    st.subheader("🧭 סיכום מנהלים — השוואת מסלולים")

    cols = st.columns(4)
    for col_idx, (track_id, score, empty_age, portfolio_95, husn) in enumerate(tracks_exec):
        pc = track_pros_cons[track_id]
        health = get_health_label(score)
        score_color = get_score_color(score)
        _, border_color = get_card_colors(score)
        res_label = resiliency_label_for_card(empty_age)
        res_color = "#1a7a1a" if empty_age >= 105.0 else ("#b84c00" if empty_age >= 90 else "#cc0000")

        # Short track name for header
        track_short = pc["name"].split("—")[1].strip() if "—" in pc["name"] else pc["name"]
        track_num = pc["name"].split("—")[0].strip()

        with cols[col_idx]:
            st.markdown(f"""
<div style='border-top: 4px solid {border_color}; border-radius: 8px; padding: 14px 16px 16px 16px; background: #ffffff; box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: right; direction: rtl; font-family: sans-serif;'>

  <div style='font-size: 0.75em; color: #888; margin-bottom: 2px;'>{track_num}</div>
  <div style='font-size: 1em; font-weight: 700; color: #1f2937; margin-bottom: 12px;'>{track_short}</div>

  <div style='display: flex; align-items: baseline; gap: 6px; margin-bottom: 4px; direction: ltr; justify-content: flex-end;'>
    <span style='font-size: 2.2em; font-weight: 800; color: {score_color}; line-height: 1;'>{score}</span>
    <span style='font-size: 1em; color: #888;'>/100</span>
  </div>
  <div style='font-size: 1em; margin-bottom: 14px;'>{health}</div>

  <div style='border-top: 1px solid #e5e7eb; padding-top: 10px; margin-bottom: 10px;'>
    <div style='font-size: 0.7em; font-weight: 700; color: #555; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;'>יתרונות</div>
    <div style='font-size: 0.82em; color: #1a7a1a; margin-bottom: 4px;'>✅ {pc["pro1"]}</div>
    <div style='font-size: 0.82em; color: #1a7a1a;'>✅ {pc["pro2"]}</div>
  </div>

  <div style='border-top: 1px solid #e5e7eb; padding-top: 10px; margin-bottom: 10px;'>
    <div style='font-size: 0.7em; font-weight: 700; color: #555; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;'>סיכונים</div>
    <div style='font-size: 0.82em; color: #cc5500; margin-bottom: 4px;'>⚠️ {pc["con1"]}</div>
    <div style='font-size: 0.82em; color: #cc5500;'>⚠️ {pc["con2"]}</div>
  </div>

  <div style='border-top: 1px solid #e5e7eb; padding-top: 10px; display: flex; flex-direction: column; gap: 4px;'>
    <div style='font-size: 0.82em; color: {res_color}; font-weight: 600;'>📅 {res_label}</div>
    <div style='font-size: 0.82em; color: #1f2937;'>💰 בגיל 95: <b>{format_shekel(portfolio_95)}</b></div>
  </div>

</div>
""", unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # -------------------------------------------------------
    # Table 1: At retirement
    # -------------------------------------------------------
    st.subheader(f"📊 מצב ביום הפרישה (גיל {retire_age:.1f})")
    t1 = pd.DataFrame({
        "שאלה": [
            "גודל תיק נזיל בגיל פרישה",
            "שווי ירושה (תיק + הבטחת קצבה)",
            "שווי הנדל\"ן בפרישה",
            "קצבאות בפרישה (ב\"ל + פנסיה)",
            "משיכה חודשית נטו מהתיק",
            "חוק ה-400 (יחס חסינות)",
            "שנות כיסוי מקרן חירום",
            "קצב משיכה שנתי",
            "סך כלל הנכסים"
        ],
        "מסלול 1 — תיקון 190": [
            format_shekel(b190_r),
            format_shekel(inherit_190_r),
            format_shekel(property_value_retire),
            format_shekel(base_income_retire + pension_retire),
            format_shekel(nn_190_r),
            wrap_html_style(rule400(b190_r, nn_190_r), get_400_rule_style(rule400(b190_r, nn_190_r))),
            wrap_html_style(emer(nn_190_r), get_emergency_style(emer(nn_190_r))),
            wrap_html_style(f"{pct_190_r:.2f}%", get_withdrawal_style(pct_190_r)),
            format_shekel(tw_190_r)
        ],
        "מסלול 2 — 25% ריאלי": [
            format_shekel(b25_r),
            "—",
            format_shekel(property_value_retire),
            format_shekel(base_income_retire),
            format_shekel(nn_25_r),
            wrap_html_style(rule400(b25_r, nn_25_r), get_400_rule_style(rule400(b25_r, nn_25_r))),
            wrap_html_style(emer(nn_25_r), get_emergency_style(emer(nn_25_r))),
            wrap_html_style(f"{pct_25_r:.2f}%", get_withdrawal_style(pct_25_r)),
            format_shekel(tw_25_r)
        ],
        "מסלול 3 — קצבה + 25% ריאלי": [
            format_shekel(bh_r),
            format_shekel(inherit_h_r),
            format_shekel(property_value_retire),
            format_shekel(base_income_retire + pension_retire),
            format_shekel(nn_h_r),
            wrap_html_style(rule400(bh_r, nn_h_r), get_400_rule_style(rule400(bh_r, nn_h_r))),
            wrap_html_style(emer(nn_h_r), get_emergency_style(emer(nn_h_r))),
            wrap_html_style(f"{pct_h_r:.2f}%", get_withdrawal_style(pct_h_r)),
            format_shekel(tw_h_r)
        ],
        "מסלול 4 — שכירות": [
            format_shekel(br_r),
            "—",
            format_shekel(float(row_retire.get("שווי נדלן מסלול 4", property_value_retire))),
            format_shekel(base_income_retire),
            format_shekel(nn_rent_r),
            "לא רלוונטי",
            "לא רלוונטי",
            "לא רלוונטי",
            format_shekel(tw_rent_r)
        ]
    })
    st.markdown(t1.set_index("שאלה").to_html(escape=False, classes="styled-table"), unsafe_allow_html=True)

    # -------------------------------------------------------
    # Table 2: At check_age
    # -------------------------------------------------------
    st.subheader(f"🔮 מצב בגיל נבדק (גיל {check_age:.1f})")

    # Preservation at age 95 (not check_age)
    bool_preserve_95_190 = "✅ כן" if b190_95 >= baseline_capital else "❌ לא"
    bool_preserve_95_25 = "✅ כן" if b25_95 >= baseline_capital else "❌ לא"
    bool_preserve_95_h = "✅ כן" if bh_95 >= baseline_capital else "❌ לא"
    bool_preserve_95_r = "✅ כן" if br_95 > 0 else "❌ לא"  # Track 4: חסכונות > 0?

    t2 = pd.DataFrame({
        "שאלה": [
            "תיק נזיל שיישאר",
            "שווי ירושה (תיק + הבטחת קצבה)",
            "משיכה חודשית נטו מהתיק",
            "קצב משיכה בגיל הנבדק",
            "האם נשמר ההון ההתחלתי? (גיל 95)",
            "גיל שבו עובר את ההון ההתחלתי",
            "סך כלל הנכסים"
        ],
        "מסלול 1 — תיקון 190": [
            wrap_html_style(format_shekel(b190_c), get_larger_portfolio_style(b190_c > b25_c)),
            format_shekel(inherit_190_c),
            format_shekel(nn_190_c),
            wrap_html_style(f"{pct_190_c:.2f}%", get_withdrawal_style(pct_190_c)),
            wrap_html_style(bool_preserve_95_190, get_boolean_style(bool_preserve_95_190)),
            recovery_190,
            format_shekel(tw_190_c)
        ],
        "מסלול 2 — 25% ריאלי": [
            wrap_html_style(format_shekel(b25_c), get_larger_portfolio_style(b25_c > b190_c)),
            "—",
            format_shekel(nn_25_c),
            wrap_html_style(f"{pct_25_c:.2f}%", get_withdrawal_style(pct_25_c)),
            wrap_html_style(bool_preserve_95_25, get_boolean_style(bool_preserve_95_25)),
            recovery_25,
            format_shekel(tw_25_c)
        ],
        "מסלול 3 — קצבה + 25% ריאלי": [
            wrap_html_style(format_shekel(bh_c), get_larger_portfolio_style(bh_c > b25_c)),
            format_shekel(inherit_h_c),
            format_shekel(nn_h_c),
            wrap_html_style(f"{pct_h_c:.2f}%", get_withdrawal_style(pct_h_c)),
            wrap_html_style(bool_preserve_95_h, get_boolean_style(bool_preserve_95_h)),
            recovery_h,
            format_shekel(tw_h_c)
        ],
        "מסלול 4 — שכירות": [
            wrap_html_style(format_shekel(br_c), get_larger_portfolio_style(br_c > b25_c)),
            "—",
            format_shekel(nn_rent_c),
            wrap_html_style(f"{pct_rent_c:.2f}%", get_withdrawal_style(pct_rent_c)),
            wrap_html_style(bool_preserve_95_r, get_boolean_style(bool_preserve_95_r)),
            recovery_r,
            format_shekel(tw_rent_c)
        ]
    })
    st.markdown(t2.set_index("שאלה").to_html(escape=False, classes="styled-table"), unsafe_allow_html=True)

    # -------------------------------------------------------
    # Table 3: Resiliency
    # -------------------------------------------------------
    st.subheader("🏁 שורה תחתונה וחסינות אקטוארית")
    t3 = pd.DataFrame({
        "שורה תחתונה": [
            "עד איזה גיל הכסף יחזיק?",
            "אחוז ההון ההתחלתי שנשמר בגיל 97"
        ],
        "מסלול 1 — תיקון 190": [
            wrap_html_style(fmt_empty(empty_190), get_resiliency_style(fmt_empty(empty_190))),
            wrap_html_style(ratio_190_str, get_preservation_pct_style(ratio_190_pct))
        ],
        "מסלול 2 — 25% ריאלי": [
            wrap_html_style(fmt_empty(empty_25), get_resiliency_style(fmt_empty(empty_25))),
            wrap_html_style(ratio_25_str, get_preservation_pct_style(ratio_25_pct))
        ],
        "מסלול 3 — קצבה + 25% ריאלי": [
            wrap_html_style(fmt_empty(empty_h), get_resiliency_style(fmt_empty(empty_h))),
            wrap_html_style(ratio_h_str, get_preservation_pct_style(ratio_h_pct))
        ],
        "מסלול 4 — שכירות": [
            wrap_html_style(fmt_empty(empty_r), get_resiliency_style(fmt_empty(empty_r))),
            wrap_html_style(ratio_r_str, get_preservation_pct_style(ratio_r_pct))
        ]
    })
    st.markdown(t3.set_index("שורה תחתונה").to_html(escape=False, classes="styled-table"), unsafe_allow_html=True)
