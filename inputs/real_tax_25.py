import streamlit as st
from inputs.ui_components import labeled_slider_with_value, show_net_summary, format_shekel, DEFAULTS

def render_25_inputs(remaining_for_gimel):
    st.subheader("📉 מסלול 25% מס ריאלי")
    st.caption(f"הון התחלתי מועבר למסלול ריאלי: {format_shekel(remaining_for_gimel)}")
    
    net_for_real_pathway = remaining_for_gimel
    show_net_summary(title="סך הון נטו פנוי במסלול 25% מס ריאלי", amount=net_for_real_pathway)
    
    st.divider()
    st.markdown("##### 📈 תשואה ודמי ניהול לתיק")
    
    annual_return_25 = labeled_slider_with_value(
        "תשואה שנתית צפויה במסלול ריאלי (%)", 
        min_value=0.0, max_value=15.0, value=DEFAULTS["annual_return"] * 100, step=0.1, 
        format="%.1f%%", unit="%"
    ) / 100
    
    management_fee_25 = labeled_slider_with_value(
        "דמי ניהול שנתיים מהצבירה במסלול ריאלי (%)", 
        min_value=0.0, max_value=2.0, value=DEFAULTS["management_fee"] * 100, step=0.05, 
        format="%.2f%%", unit="%"
    ) / 100
    
    return {
        "net_for_real_pathway": net_for_real_pathway,
        "annual_return_25": annual_return_25,
        "management_fee_25": management_fee_25
    }
