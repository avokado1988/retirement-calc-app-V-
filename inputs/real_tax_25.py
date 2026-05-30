import streamlit as st
from inputs.ui_components import compact_number_input, show_net_summary, format_shekel, COLOR_BLUE, COLOR_RED, DEFAULTS

def render_25_inputs(remaining_for_gimel):
    st.subheader("📉 מסלול 25% מס ריאלי")
    st.caption(f"הון התחלתי מועבר למסלול ריאלי: {format_shekel(remaining_for_gimel)}")

    net_for_real_pathway = remaining_for_gimel
    show_net_summary(title="סך הון נטו פנוי במסלול 25% מס ריאלי", amount=net_for_real_pathway)

    st.divider()
    st.markdown("##### 📈 תשואה ודמי ניהול לתיק")

    annual_return_25 = compact_number_input(
        "תשואה שנתית צפויה במסלול ריאלי (%)",
        value=DEFAULTS["annual_return"] * 100, min_value=0.0, max_value=15.0, step=0.1, unit="%", color=COLOR_BLUE
    ) / 100

    management_fee_25 = compact_number_input(
        "דמי ניהול שנתיים מהצבירה במסלול ריאלי (%)",
        value=DEFAULTS["management_fee"] * 100, min_value=0.0, max_value=2.0, step=0.05, unit="%", color=COLOR_RED
    ) / 100

    st.divider()
    st.subheader("📊 מסלול 3 — קצבה + 25% מס ריאלי (היברידי)")
    st.caption("🔗 נתוני הקצבה (גובה, מקדם, הון שנוכה) נלקחים אוטומטית ממסלול תיקון 190.")
    st.caption("ההון הנותר לאחר רכישת הקצבה מנוהל כאן בשיטת 25% מס ריאלי.")

    annual_return_hybrid = compact_number_input(
        "תשואה שנתית — מסלול היברידי (%)",
        value=DEFAULTS["annual_return"] * 100, min_value=0.0, max_value=15.0, step=0.1, unit="%", color=COLOR_BLUE
    ) / 100
    management_fee_hybrid = compact_number_input(
        "דמי ניהול — מסלול היברידי (%)",
        value=DEFAULTS["management_fee"] * 100, min_value=0.0, max_value=2.0, step=0.05, unit="%", color=COLOR_RED
    ) / 100

    return {
        "net_for_real_pathway": net_for_real_pathway,
        "annual_return_25": annual_return_25,
        "management_fee_25": management_fee_25,
        "annual_return_hybrid": annual_return_hybrid,
        "management_fee_hybrid": management_fee_hybrid
    }
