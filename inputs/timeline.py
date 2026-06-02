import streamlit as st
from inputs.ui_components import compact_number_input, COLOR_BLUE, DEFAULTS

def render_timeline_inputs():
    st.subheader("⏳ נתוני זמנים וגילאים")

    start_age = compact_number_input(
        "גיל התחלת השקעה (תחילת סימולציה)",
        value=DEFAULTS["start_age"], min_value=55.0, max_value=80.0, step=0.5, unit=None, color=COLOR_BLUE
    )

    retirement_age = compact_number_input(
        "גיל פרישה (הפסקת עבודה)",
        value=DEFAULTS["retirement_age"], min_value=60.0, max_value=80.0, step=0.5, unit=None, color=COLOR_BLUE
    )

    check_age = compact_number_input(
        "גיל יעד לבדיקת סימולציה",
        value=DEFAULTS["check_age"], min_value=70.0, max_value=120.0, step=1.0, unit="שנים", color=COLOR_BLUE
    )

    retirement_years = check_age - retirement_age
    st.info(f"משך שנות הפרישה הנבדקות בסימולציה: {retirement_years:.1f} שנים.")

    return {
        "start_age": start_age,
        "retirement_age": retirement_age,
        "check_age": check_age,
        "retirement_years": retirement_years
    }
