import streamlit as st
from inputs.ui_components import labeled_slider_with_value, DEFAULTS

def render_timeline_inputs():
    st.subheader("⏳ נתוני זמנים וגילאים")
    
    start_age = labeled_slider_with_value(
        "גיל התחלת השקעה (תחילת סימולציה)", 
        min_value=55.0, max_value=80.0, 
        value=DEFAULTS["start_age"], step=0.5, format="%.1f", unit=None
    )
    
    retirement_age = labeled_slider_with_value(
        "גיל פרישה (הפסקת עבודה)", 
        min_value=60.0, max_value=80.0, 
        value=DEFAULTS["retirement_age"], step=0.5, format="%.1f", unit=None
    )
    
    check_age = labeled_slider_with_value(
        "גיל יעד לבדיקת סימולציה", 
        min_value=70.0, max_value=120.0, 
        value=DEFAULTS["check_age"], step=1.0, unit="שנים"
    )
    
    retirement_years = check_age - retirement_age
    st.info(f"משך שנות הפרישה הנבדקות בסימולציה: {retirement_years:.1f} שנים.")
    
    return {
        "start_age": start_age,
        "retirement_age": retirement_age,
        "check_age": check_age,
        "retirement_years": retirement_years
    }
