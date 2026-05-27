import streamlit as st
from inputs.ui_components import compact_number_input, labeled_slider_with_value, DEFAULTS

def render_incomes_inputs():
    st.subheader("💼 מקורות הכנסה")
    
    st.markdown("##### 🏛️ הכנסות קבועות מפרישה")
    national_insurance = compact_number_input(
        "קצבת ביטוח לאומי (₪ חודשי)", 
        value=DEFAULTS.get("national_insurance", 2500), min_value=0, step=50, unit="₪"
    )
    
    st.divider()
    st.markdown("##### 💼 הכנסה זמנית מעבודה/גישור")
    work_income = compact_number_input(
        "הכנסה חודשית ממוצעת מעבודה כיום (₪)", 
        value=DEFAULTS.get("work_income", 0), min_value=0, step=500, unit="₪"
    )
    
    work_end_age = labeled_slider_with_value(
        "גיל הפסקת עבודה בפועל", 
        min_value=55.0, max_value=85.0, 
        value=DEFAULTS.get("retirement_age", 67.0), step=0.5, format="%.1f", unit=None
    )
    
    return {
        "national_insurance": national_insurance,
        "work_income": work_income,
        "work_end_age": work_end_age
    }
