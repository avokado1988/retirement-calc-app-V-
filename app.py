import streamlit as st
import inputs
from simulator_engine import run_simulation
from reports.graphs import render_charts
from reports.qa_report import render_qa_section

# 1. הגדרת תצורת דף אחידה
st.set_page_config(page_title="מחשבון פרישה אקטוארי חכם", page_icon="📊", layout="wide")

st.title("📊 סימולטור פרישה השוואתי - Gold Standard")
st.markdown("המערכת מנתחת את עוגת ההון ומציגה השוואה אקטוארית בין מסלול תיקון 190 למסלול 25% מס ריאלי.")
st.divider()

# 2. טעינת תפריט הצד המבוזר וקבלת מילון הנתונים המאוחד
user_inputs = inputs.render_all_sidebar_inputs()

# 3. הפעלת מנוע החישובים ("המוח") בזמן אמת על בסיס נתוני המשתמש
sim_results = run_simulation(user_inputs)

# 4. חלוקת המסך המרכזי ללשוניות תצוגה מקצועיות
tab1, tab2, tab3 = st.tabs(["❓ שאלות ותשובות", "📈 גרפים השוואתיים", "📋 טבלת נתונים מלאה"])

with tab1:
    # הצגת דוח שאלות ותשובות
    render_qa_section(sim_results, user_inputs)

with tab2:
    # הצגת הגרפים הדינמיים
    render_charts(sim_results["df"])

with tab3:
    # הצגת האקסל החי והמלא לבדיקת המספרים חודש-אחר-חודש
    st.subheader("🔍 גיליון סימולציה חודשי מלא (חודש-בחודשו)")
    st.markdown("ניתן לסקור כאן את כל שלבי החישוב, גילום המס וההצמדות כפי שבוצעו במנוע:")
    
    # מציג את הטבלה בצורה נקייה, מיושרת לימין וקריאה
    st.dataframe(sim_results["df"].style.format({
        "גיל": "{:.2f}",
        "הוצאה נומינלית": "{:,.0f} ₪",
        "הכנסה נומינלית": "{:,.0f} ₪",
        "צבירה תיקון 190": "{:,.0f} ₪",
        "צבירה מסלול ריאלי": "{:,.0f} ₪",
        "מס ששולם 190": "{:,.0f} ₪",
        "מס ששולם 25": "{:,.0f} ₪"
    }), use_container_width=True)
