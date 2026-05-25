import streamlit as st

def render_timeline_inputs():
    st.subheader("⏳ נתוני זמנים וגילאים")
    
    start_age = st.slider("גיל התחלת השקעה (תחילת סימולציה)", min_value=55.0, max_value=80.0, value=65.5, step=0.5)
    retirement_age = st.slider("גיל פרישה (הפסקת עבודה)", min_value=60.0, max_value=80.0, value=67.0, step=0.5)
    check_age = st.slider("גיל יעד לבדיקת סימולציה", min_value=70.0, max_value=120.0, value=87.0, step=1.0)
    
    retirement_years = check_age - retirement_age
    st.info(f"משך שנות הפרישה הנבדקות בסימולציה: {retirement_years} שנים.")
    
    timeline_data = {
        "start_age": start_age,
        "retirement_age": retirement_age,
        "check_age": check_age,
        "retirement_years": retirement_years
    }
    return timeline_data
