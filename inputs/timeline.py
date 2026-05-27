import streamlit as st
from inputs.ui_components import DEFAULTS

def render_timeline_inputs():
    st.subheader("⏳ נתוני זמנים וגילאים")
    
    start_age = st.number_input(
        "גיל התחלת השקעה (תחילת סימולציה)", 
        min_value=50.0, max_value=100.0, 
        value=float(DEFAULTS["start_age"]), step=0.5, format="%.1f"
    )
    
    retirement_age = st.number_input(
        "גיל פרישה (הפסקת עבודה)", 
        min_value=50.0, max_value=100.0, 
        value=float(DEFAULTS["retirement_age"]), step=0.5, format="%.1f"
    )
    
    check_age = st.number_input(
        "גיל יעד לבדיקת סימולציה", 
        min_value=70.0, max_value=120.0, 
        value=float(DEFAULTS["check_age"]), step=1.0, format="%.1f"
    )
    
    retirement_years = check_age - retirement_age
    st.info(f"משך שנות הפרישה הנבדקות בסימולציה: {retirement_years:.1f} שנים.")
    
    return {
        "start_age": start_age,
        "retirement_age": retirement_age,
        "check_age": check_age,
        "retirement_years": retirement_years
    }
