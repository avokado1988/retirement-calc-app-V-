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

    years_to_retire = retire_age - start_age
    years_to_check = check_age - start_age
    property_value_retire = property_value_start * ((1 + appreciation_rate) ** years_to_retire)
    property_value_check = property_value_start * ((1 + appreciation_rate) ** years_to_check)

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

    inherit_190_r = b190_r + pension_asset_retire
    inherit_h_r = bh_r + pension_asset_retire

    tw_190_r = b190_r + property_value_retire + emergency_fund
    tw_25_r = b25_r + property_value_retire + emergency_fund
    tw_h_r = bh_r + property_value_retire + emergency_fund
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

    tw_190_c = b190_c + property_value_check + emergency_fund
    tw_25_c = b25_c + property_value_check + emergency_fund
    tw_h_c = bh_c + property_value_check + emergency_fund
    tw_rent_c = br_c + float(row_check.get("שווי נדלן מסלול 4", property_value_check)) + emergency_fund

    bool_preserve = lambda bal: "✅ כן" if bal > baseline_capital else "❌ לא"

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
            wrap_html_style(rule400(br_r, nn_rent_r), get_400_rule_style(rule400(br_r, nn_rent_r))),
            wrap_html_style(emer(nn_rent_r), get_emergency_style(emer(nn_rent_r))),
            wrap_html_style(f"{pct_rent_r:.2f}%", get_withdrawal_style(pct_rent_r)),
            format_shekel(tw_rent_r)
        ]
    })
    st.markdown(t1.set_index("שאלה").to_html(escape=False, classes="styled-table"), unsafe_allow_html=True)

    # -------------------------------------------------------
    # Table 2: At check_age
    # -------------------------------------------------------
    st.subheader(f"🔮 מצב בגיל נבדק (גיל {check_age:.1f})")
    t2 = pd.DataFrame({
        "שאלה": [
            "תיק נזיל שיישאר",
            "שווי ירושה (תיק + הבטחת קצבה)",
            "משיכה חודשית נטו מהתיק",
            "קצב משיכה בגיל הנבדק",
            "האם נשמר ההון ההתחלתי?",
            "גיל שבו עובר את ההון ההתחלתי",
            "סך כלל הנכסים"
        ],
        "מסלול 1 — תיקון 190": [
            wrap_html_style(format_shekel(b190_c), get_larger_portfolio_style(b190_c > b25_c)),
            format_shekel(inherit_190_c),
            format_shekel(nn_190_c),
            wrap_html_style(f"{pct_190_c:.2f}%", get_withdrawal_style(pct_190_c)),
            wrap_html_style(bool_preserve(b190_c), get_boolean_style(bool_preserve(b190_c))),
            recovery_190,
            format_shekel(tw_190_c)
        ],
        "מסלול 2 — 25% ריאלי": [
            wrap_html_style(format_shekel(b25_c), get_larger_portfolio_style(b25_c > b190_c)),
            "—",
            format_shekel(nn_25_c),
            wrap_html_style(f"{pct_25_c:.2f}%", get_withdrawal_style(pct_25_c)),
            wrap_html_style(bool_preserve(b25_c), get_boolean_style(bool_preserve(b25_c))),
            recovery_25,
            format_shekel(tw_25_c)
        ],
        "מסלול 3 — קצבה + 25% ריאלי": [
            wrap_html_style(format_shekel(bh_c), get_larger_portfolio_style(bh_c > b25_c)),
            format_shekel(inherit_h_c),
            format_shekel(nn_h_c),
            wrap_html_style(f"{pct_h_c:.2f}%", get_withdrawal_style(pct_h_c)),
            wrap_html_style(bool_preserve(bh_c), get_boolean_style(bool_preserve(bh_c))),
            recovery_h,
            format_shekel(tw_h_c)
        ],
        "מסלול 4 — שכירות": [
            wrap_html_style(format_shekel(br_c), get_larger_portfolio_style(br_c > b25_c)),
            "—",
            format_shekel(nn_rent_c),
            wrap_html_style(f"{pct_rent_c:.2f}%", get_withdrawal_style(pct_rent_c)),
            wrap_html_style(bool_preserve(br_c), get_boolean_style(bool_preserve(br_c))),
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
