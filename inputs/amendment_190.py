import streamlit as st
from inputs.ui_components import compact_number_input, show_net_summary, format_shekel, COLOR_GREEN, COLOR_BLUE, COLOR_RED, DEFAULTS, RETURN_HELP

def render_190_inputs(remaining_for_gimel, capital_for_pension=0):
    net_for_190 = max(0, remaining_for_gimel - capital_for_pension)

    st.markdown("##### 📑 מסלול 1 — תיקון 190 + קצבה מזערית")
    st.info(
        "ההון מוחזק בקופת גמל ומשלמים **15% מס נומינלי בלבד** (לא ריאלי) בעת המשיכה. "
        "חלק מההון נמיר לקצבה חודשית מובטחת לכל החיים — ביטוח אריכות ימים. "
        "**יתרון:** מגן מס אפקטיבי בתנאי אינפלציה גבוהה ודמי ניהול נמוכים בשוק."
    )

    if capital_for_pension > 0:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                f"<div style='font-size:0.78em;color:#666;'>הון לקצבה</div>"
                f"<div style='font-size:1em;font-weight:700;color:#c0392b;'>{format_shekel(capital_for_pension)}</div>",
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                f"<div style='font-size:0.78em;color:#666;'>יתרה נזילה לתיק</div>"
                f"<div style='font-size:1em;font-weight:700;color:#1a7a3a;'>{format_shekel(net_for_190)}</div>",
                unsafe_allow_html=True
            )
        if remaining_for_gimel < capital_for_pension:
            st.error("⚠️ ההון הנדרש לקצבה גבוה מסך ההון הזמין!")

    st.divider()
    st.markdown("##### 📈 תשואה ודמי ניהול")
    annual_return_190 = compact_number_input(
        "תשואה שנתית צפויה — מסלול 190 (%)",
        value=DEFAULTS["annual_return"] * 100, min_value=0.0, max_value=15.0, step=0.1, unit="%", color=COLOR_BLUE,
        help_text=RETURN_HELP
    ) / 100
    from reports.allocation import implied_vol
    st.caption(f"סטיית תקן למונטה קרלו כ-{implied_vol(annual_return_190)*100:.0f}%, נגזרת מהתשואה לפי חלק המניות. משנה תשואה, משנה גם את הסטייה.")
    management_fee_190 = compact_number_input(
        "דמי ניהול שנתיים — מסלול 190 (%)",
        value=DEFAULTS["management_fee_190"] * 100, min_value=0.0, max_value=2.0, step=0.05, unit="%", color=COLOR_RED
    ) / 100

    return {
        "desired_pension": 0,  # set from incomes
        "securing_years": 0,   # set from incomes
        "base_coefficient": 0, # set from incomes
        "adjusted_coefficient": 0, # set from incomes
        "capital_for_pension": capital_for_pension,
        "net_for_190": net_for_190,
        "annual_return_190": annual_return_190,
        "management_fee_190": management_fee_190
    }
