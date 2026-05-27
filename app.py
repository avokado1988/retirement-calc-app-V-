import streamlit as st

# 1. הגדרת תצורת דף אחידה - חובה ראשון!
st.set_page_config(page_title="מחשבון פרישה אקטוארי חכם", page_icon="📊", layout="wide")

import inputs
from simulator_engine import run_simulation
from reports.graphs import render_charts
from reports.qa_report import render_qa_section
from reports.qa_summary import render_qa_summary_page

st.title("📊 סימולטור פרישה השוואתי - Gold Standard")
st.markdown("המערכת מנתחת את עוגת ההון ומציגה השוואה אקטוארית בין מסלול תיקון 190 למסלול 25% מס ריאלי.")
st.divider()

# ==============================================================================
# 🗑️ כפתור איפוס נתונים בדפדפן (כדי להתחיל לקוח חדש מאפס)
# ==============================================================================
st.sidebar.title("🧹 ניהול זיכרון דפדפן")
if st.sidebar.button("🗑️ נקה נתונים וחזור לברירת מחדל", use_container_width=True):
    for k in list(st.query_params.keys()):
        if k.startswith("saved_"):
            del st.query_params[k]
    for k in list(st.session_state.keys()):
        if k.startswith("saved_"):
            del st.session_state[k]
    st.sidebar.success("הדפדפן אופס בהצלחה!")
    st.rerun()

st.sidebar.divider()
# ==============================================================================

# 2. טעינת תפריט הצד המבוזר וקבלת מילון הנתונים המאוחד
user_inputs = inputs.render_all_sidebar_inputs()

# 3. הפעלת מנוע החישובים בזמן אמת על בסיס נתוני המשתמש
sim_results = run_simulation(user_inputs)

# 4. חלוקת המסך המרכזי ללשוניות תצוגה מקצועיות
tab1, tab2, tab3, tab4 = st.tabs(["❓ שאלות ותשובות", "📈 גרפים השוואתיים", "📋 טבלת נתונים מלאה", "📋 העתקה מהירה לבדיקות"])

with tab1:
    render_qa_section(sim_results, user_inputs)

with tab2:
    render_charts(sim_results["df"])

with tab3:
    st.subheader("🔍 גיליון סימולציה חודשי מלא (חודש-בחודשו)")
    st.markdown("ניתן לסקור כאן את כל שלבי החישוב, גילום המס וההצמדות כפי שבוצעו במנוע:")
    
    st.dataframe(sim_results["df"].style.format({
        "גיל": "{:.2f}",
        "הוצאה נומינלית": "{:,.0f} ₪",
        "הכנסה מעבודה": "{:,.0f} ₪",
        "קצבת ביטוח לאומי": "{:,.0f} ₪",
        "קצבה מזערית 190": "{:,.0f} ₪",
        "צבירה תיקון 190": "{:,.0f} ₪",
        "צבירה מסלול ריאלי": "{:,.0f} ₪",
        "מס ששולם 190": "{:,.0f} ₪",
        "מס ששולם 25": "{:,.0f} ₪"
    }), use_container_width=True)

with tab4:
    render_qa_summary_page(sim_results, user_inputs)
