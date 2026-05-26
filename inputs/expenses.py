import streamlit as st
from inputs.ui_components import compact_number_input, labeled_slider_with_value, DEFAULTS

def render_expenses_inputs():
    st.subheader("📉 תקציב והוצאות")
    
    st.markdown("##### 🛒 הוצאות שוטפות ואינפלציה")
    current_expenses = compact_number_input(
        "הוצאות חודשיות נוכחיות (₪)", 
        value=DEFAULTS["current_expenses"], min_value=0, step=500, unit="₪"
    )
    
    expected_inflation = labeled_slider_with_value(
        "אינפלציה שנתית צפויה (%)", 
        min_value=0.0, max_value=10.0, 
        value=DEFAULTS["expected_inflation"] * 100, step=0.1, 
        format="%.1f%%", unit="%"
    )
    
    st.divider()
    st.markdown("##### 👵 תוספת הוצאות לפי גיל")
    age_75_85_increase = labeled_slider_with_value(
        "תוספת הוצאות שנתית בגילאי 75-85 (%)", 
        min_value=0.0, max_value=5.0, 
        value=DEFAULTS["age_75_85_increase"] * 100, step=0.1, 
        format="%.1f%%", unit="%"
    )
    
    age_85_plus_increase = labeled_slider_with_value(
        "תוספת הוצאות שנתית מגיל 85 ואילך (%)", 
        min_value=0.0, max_value=5.0, 
        value=DEFAULTS["age_85_plus_increase"] * 100, step=0.1, 
        format="%.1f%%", unit="%"
    )
    
    st.divider()
    st.markdown("##### 🚗 הוצאות חד פעמיות")
    one_time_expense = compact_number_input(
        "גובה הוצאה חד-פעמית ממוצעת (₪)", 
        value=DEFAULTS["one_time_expense"], min_value=0, step=5000, unit="₪"
    )
    
    one_time_frequency = labeled_slider_with_value(
        "תדירות ההוצאה החד-פעמית (כל כמה שנים)", 
        min_value=1, max_value=20, 
        value=DEFAULTS["one_time_frequency"], step=1, unit="שנים"
    )

    st.divider()
    st.markdown("##### 👩‍⚕️ הוצאות מטפלת")
    caregiver_cost = compact_number_input(
        "תוספת עלות מטפלת סיעודית מגיל 85 (₪)", 
        value=DEFAULTS["caregiver_cost"], min_value=0, step=500, unit="₪"
    )
    
    return {
        "current_expenses": current_expenses,
        "expected_inflation": expected_inflation / 100,
        "age_75_85_increase": age_75_85_increase / 100,
        "age_85_plus_increase": age_85_plus_increase / 100,
        "caregiver_cost": caregiver_cost,
        "one_time_expense": one_time_expense,
        "one_time_frequency": one_time_frequency
    }
