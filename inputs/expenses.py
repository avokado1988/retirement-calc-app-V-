import streamlit as st
from inputs.ui_components import format_shekel

def render_expenses_inputs():
    st.subheader("📉 תקציב, הוצאות ואינפלציה")
    
    st.markdown("##### 🛒 הוצאות שוטפות")
    current_expenses = st.slider("הוצאות חודשיות נוכחיות", min_value=0, max_value=50_000, value=11_000, step=500, format="%d")
    st.caption(f"בחרת: **{format_shekel(current_expenses)}**")
    
    expected_inflation = st.slider("אינפלציה שנתית צפויה (%)", min_value=0.0, max_value=10.0, value=2.3, step=0.1) / 100
    
    st.divider()
    st.markdown("##### 👵 גידול דינמי בהוצאות לפי גיל")
    age_75_85_increase = st.slider("תוספת הוצאות שנתית בגילאי 75-85 (%)", min_value=0.0, max_value=5.0, value=0.5, step=0.1) / 100
    age_85_plus_increase = st.slider("תוספת הוצאות שנתית מגיל 85 ואילך (%)", min_value=0.0, max_value=5.0, value=1.5, step=0.1) / 100
    
    caregiver_cost = st.slider("תוספת עלות מטפלת סיעודית מגיל 85", min_value=0, max_value=15_000, value=3_500, step=500, format="%d")
    st.caption(f"בחרת: **{format_shekel(caregiver_cost)} לחודש**")
    
    st.divider()
    st.markdown("##### 🚗 הוצאות חד-פעמיות מחזוריות")
    one_time_expense = st.slider("גובה הוצאה חד-פעמית ממוצעת", min_value=0, max_value=500_000, value=80_000, step=5_000, format="%d")
    st.caption(f"בחרת: **{format_shekel(one_time_expense)}**")
    one_time_frequency = st.slider("תדירות ההוצאה החד-פעמית (כל כמה שנים)", min_value=1, max_value=20, value=8, step=1)
    
    st.divider()
    st.markdown("##### 💼 הכנסה זמנית מעבודה/גישור")
    work_income = st.slider("הכנסה חודשית ממוצעת מעבודה כיום", min_value=0, max_value=30_000, value=0, step=500, format="%d")
    st.caption(f"בחרת: **{format_shekel(work_income)}**")
    
    # 🟢 הסליידר החדש והקריטי:
    work_end_age = st.slider("גיל הפסקת עבודה בפועל (סיום הכנסה מעבודה)", min_value=55.0, max_value=85.0, value=67.0, step=0.5)
    st.caption(f"ההכנסה מעבודה תיפסק לחלוטין בגיל: **{work_end_age:.1f}**")
    
    expenses_data = {
        "current_expenses": current_expenses,
        "expected_inflation": expected_inflation,
        "age_75_85_increase": age_75_85_increase,
        "age_85_plus_increase": age_85_plus_increase,
        "caregiver_cost": caregiver_cost,
        "one_time_expense": one_time_expense,
        "one_time_frequency": one_time_frequency,
        "work_income": work_income,
        "work_end_age": work_end_age  # נשמר במילון
    }
    return expenses_data
