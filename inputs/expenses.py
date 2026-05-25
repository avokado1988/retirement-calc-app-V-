import streamlit as st

def render_expenses_inputs():
    st.subheader("📉 תקציב, הוצאות ואינפלציה")
    
    # כרטיסייה פנימית ראשונה: הוצאות שוטפות ואינפלציה
    st.markdown("##### 🛒 הוצאות שוטפות")
    expenses_data = {
        "current_expenses": st.slider("הוצאות חודשיות נוכחיות (₪)", min_value=0, max_value=50_000, value=11_000, step=500),
        "expected_inflation": st.slider("אינפלציה שנתית צפויה (%)", min_value=0.0, max_value=10.0, value=2.3, step=0.1) / 100
    }
    
    st.divider()
    
    # כרטיסייה פנימית שנייה: גידול בהוצאות לפי גיל
    st.markdown("##### 👵 גידול דינמי בהוצאות לפי גיל")
    expenses_data["age_75_85_increase"] = st.slider("תוספת הוצאות שנתית בגילאי 75-85 (%)", min_value=0.0, max_value=5.0, value=0.5, step=0.1) / 100
    expenses_data["age_85_plus_increase"] = st.slider("תוספת הוצאות שנתית מגיל 85 ואילך (%)", min_value=0.0, max_value=5.0, value=1.5, step=0.1) / 100
    expenses_data["caregiver_cost"] = st.slider("תוספת עלות מטפלת סיעודית מגיל 85 (₪ לחודש)", min_value=0, max_value=15_000, value=3_500, step=500)
    
    st.divider()
    
    # כרטיסייה פנימית שלישית: הוצאות חד פעמיות משתנות
    st.markdown("##### 🚗 הוצאות חד-פעמיות מחזוריות (שיפוץ, רכב וכו')")
    expenses_data["one_time_expense"] = st.slider("גובה הוצאה חד-פעמית ממוצעת (₪)", min_value=0, max_value=500_000, value=80_000, step=5_000)
    expenses_data["one_time_frequency"] = st.slider("תדירות ההוצאה החד-פעמית (כל כמה שנים)", min_value=1, max_value=20, value=8, step=1)
    
    st.divider()
    
    # כרטיסייה פנימית רביעית: הכנסה מעבודה (אם קיימת עד הפרישה המלאה)
    st.markdown("##### 💼 הכנסה זמנית מעבודה/גישור")
    expenses_data["work_income"] = st.slider("הכנסה חודשית ממוצעת מעבודה כיום (₪)", min_value=0, max_value=30_000, value=0, step=500)
    expenses_data["retirement_age"] = st.slider("גיל הפסקת עבודה מלאה", min_value=60, max_value=80, value=70, step=1)
    
    return expenses_data
