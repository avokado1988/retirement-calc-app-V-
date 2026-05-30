import streamlit as st
from inputs.ui_components import compact_number_input, DEFAULTS

def render_incomes_inputs():
    st.subheader("💼 מקורות הכנסה")
    
    st.markdown("##### 🏛️ הכנסות קבועות מפרישה")
    national_insurance = compact_number_input(
        "קצבת ביטוח לאומי (₪ חודשי)", 
        value=DEFAULTS["national_insurance"], min_value=0, step=50, unit="₪"
    )
    
    st.divider()
    st.markdown("##### 💼 הכנסה זמנית מעבודה/גישור")
    work_income = compact_number_input(
        "הכנסה חודשית ממוצעת מעבודה כיום (₪)", 
        value=DEFAULTS["work_income"], min_value=0, step=500, unit="₪"
    )
    
    work_end_age = compact_number_input(
        "גיל הפסקת עבודה בפועל",
        value=DEFAULTS["retirement_age"], min_value=55.0, max_value=85.0, step=0.5, unit=None
    )
    
    return {
        "national_insurance": national_insurance,
        "work_income": work_income,
        "work_end_age": work_end_age
    }
