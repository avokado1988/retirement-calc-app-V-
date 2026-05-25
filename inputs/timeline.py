import streamlit as st

def render_timeline_inputs():
    st.subheader("⏳ נתוני זמנים וגילאים")
    
    timeline_data = {
        "start_age": st.slider("גיל התחלת השקעה (תחילת סימולציה)", min_value=55.0, max_value=80.0, value=65.5, step=0.5),
        "retirement_age": st.slider("גיל פרישה (הפסקת עבודה)", min_value=60.0, max_value=80.0, value=67.0, step=0.5),
        "check_age": st.slider("גיל יעד לבדיקת סימולציה (עבור שאלות ותשובות)", min_value=70.0, max_value=120.0, value=87.0, step=1.0)
    }
    
    # חישוב אוטומטי של שנות הפרישה (מהפרישה ועד גיל הבדיקה)
    timeline_data["retirement_years"] = timeline_data["check_age"] - timeline_data["retirement_age"]
    
    st.info(f"משך שנות הפרישה הנבדקות בסימולציה: {timeline_data['retirement_years']} שנים.")
    
    return timeline_data
