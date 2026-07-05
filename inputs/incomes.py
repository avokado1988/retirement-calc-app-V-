import streamlit as st
from inputs.ui_components import compact_number_input, format_shekel, COLOR_GREEN, COLOR_BLUE, DEFAULTS

def render_incomes_inputs(remaining_for_gimel=0):
    st.subheader("💼 מקורות הכנסה")

    st.markdown("##### 🏛️ הכנסות קבועות מפרישה")
    national_insurance = compact_number_input(
        "קצבת ביטוח לאומי (₪ חודשי)",
        value=DEFAULTS["national_insurance"], min_value=0, step=50, unit="₪", color=COLOR_GREEN
    )

    st.divider()
    st.markdown("##### 🎯 קצבה מזערית מובטחת (מסלולים 1 ו-3)")
    st.caption(
        "חלק מההון יומר לקצבה חודשית מובטחת לכל החיים. "
        "הקצבה מוגנת גם לאחר תקופת ההבטחה — ביטוח אריכות ימים מלא."
    )

    desired_pension = compact_number_input(
        "קצבה רצויה לרכישה (₪ חודשי)",
        value=DEFAULTS["desired_pension"], min_value=0, step=50, unit="₪", color=COLOR_GREEN
    )

    securing_years = compact_number_input(
        "תקופת אבטחה לירושה (שנים)",
        value=DEFAULTS["securing_years"], min_value=0, max_value=35, step=1, unit="שנים", color=COLOR_BLUE
    )
    base_coefficient = compact_number_input(
        "מקדם המרה בסיסי (ללא אבטחה)",
        value=DEFAULTS["base_coefficient"], min_value=150.0, max_value=300.0, step=1.0, unit=None, color=COLOR_BLUE
    )

    adjusted_coefficient = base_coefficient + (securing_years * 1.0)
    capital_for_pension = int(desired_pension * adjusted_coefficient)

    # Compact display of computed actuarial values
    col1, col2 = st.columns(2)
    with col1:
        val_m = capital_for_pension / 1_000_000
        st.markdown(
            f"<div style='font-size:0.72em;color:#666;'>הון נדרש לקצבה</div>"
            f"<div style='font-size:0.95em;font-weight:700;color:#c0392b;'>{val_m:.2f}M ₪</div>",
            unsafe_allow_html=True
        )
    with col2:
        remaining_after = max(0, remaining_for_gimel - capital_for_pension)
        rem_m = remaining_after / 1_000_000
        st.markdown(
            f"<div style='font-size:0.72em;color:#666;'>מקדם משוקלל | יתרה</div>"
            f"<div style='font-size:0.95em;font-weight:700;color:#1a7a3a;'>{adjusted_coefficient:.0f} | {rem_m:.2f}M ₪</div>",
            unsafe_allow_html=True
        )

    st.divider()
    st.markdown("##### 💼 הכנסה זמנית מעבודה/גישור")
    work_income = compact_number_input(
        "הכנסה חודשית ממוצעת מעבודה כיום (₪)",
        value=DEFAULTS["work_income"], min_value=0, step=500, unit="₪", color=COLOR_GREEN
    )
    work_end_age = compact_number_input(
        "גיל הפסקת עבודה בפועל",
        value=DEFAULTS["retirement_age"], min_value=55.0, max_value=85.0, step=0.5, unit=None, color=COLOR_BLUE
    )

    return {
        "national_insurance": national_insurance,
        "work_income": work_income,
        "work_end_age": work_end_age,
        "desired_pension": desired_pension,
        "securing_years": securing_years,
        "base_coefficient": base_coefficient,
        "adjusted_coefficient": adjusted_coefficient,
        "capital_for_pension": capital_for_pension,
    }
