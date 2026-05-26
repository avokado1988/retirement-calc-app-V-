import streamlit as st
import pandas as pd
from inputs.ui_components import format_shekel

def render_qa_summary_page(results, user_inputs):
    """
    קובץ בדיקות (QA) עצמאי לחלוטין - ריכוז אינפוטים ושורות סיכום להעתקה מהירה
    """
    df_history = results["df"]
    df_full = results.get("df_full", df_history)
    
    timeline = user_inputs.get("timeline", {})
    wealth = user_inputs.get("wealth", {})
    general = user_inputs.get("general", {})
    amendment_190 = user_inputs.get("amendment_190", {})
    real_tax_25 = user_inputs.get("real_tax_25", {})
    
    start_age = float(timeline.get("start_age", 60))
    check_age = float(timeline.get("check_age", 80))
    retire_age = float(timeline.get("retirement_age", start_age))
    
    initial_capital_190 = float(amendment_190.get("net_for_190") or 0)
    initial_capital_25 = float(real_tax_25.get("net_for_real_pathway") or 0)
    
    property_value_start = float(wealth.get("new_apartment_cost") or 0)
    appreciation_rate = float(wealth.get("property_appreciation") or 0)
    emergency_fund = float(wealth.get("emergency_fund") or 0)
    pension_190_start = float(amendment_190.get("desired_pension") or 0)

    # 1. שליפת שווי תיק נזיל בגיל פרישה
    df_retire = df_history[df_history["גיל"] >= retire_age]
    row_retire = df_retire.iloc[0] if not df_retire.empty else df_history.iloc[-1]
    balance_190_retire = float(row_retire["צבירה תיקון 190"])
    balance_25_retire = float(row_retire["צבירה מסלול ריאלי"])

    # 2. שליפת שווי תיק נזיל בגיל 100
    df_100 = df_full[df_full["גיל"] >= 100.0]
    row_100 = df_100.iloc[0] if not df_100.empty else df_full.iloc[-1]
    balance_190_at_100 = float(row_100["צבירה תיקון 190"])
    balance_25_at_100 = float(row_100["צבירה מסלול ריאלי"])

    # הצגה ויזואלית בממשק
    st.subheader("📋 כלי סיכום נתונים להעתקה מהירה (QA)")
    
    # בניית גוש הטקסט המרוכז להעתקה
    copy_text = f"""=== סימולציית פרישה אקטוארית - דוח QA מהיר ===

[פרמטרים ואינפוטים שנבחרו]
- גיל התחלה: {start_age}
- גיל פרישה: {retire_age}
- גיל בדיקה: {check_age}
- אינפלציה שנתית: {float(general.get('inflation_rate', 0.03))*100:.1f}%
- תשואה תיקון 190: {float(amendment_190.get('yield', 0.05))*100:.1f}% (דמי ניהול: {float(amendment_190.get('fees', 0.005))*100:.2f}%)
- תשואה מסלול ריאלי: {float(real_tax_25.get('yield', 0.05))*100:.1f}% (דמי ניהול: {float(real_tax_25.get('fees', 0.005))*100:.2f}%)
- הון התחלה תיקון 190: {initial_capital_190:,.0f} ש"ח
- הון התחלה מסלול ריאלי: {initial_capital_25:,.0f} ש"ח
- הוצאת בסיס חודשית: {float(general.get('base_expense', 15000)):,.0f} ש"ח
- הכנסת בסיס (קצבאות): {float(general.get('base_income', 5000)):,.0f} ש"ח
- קצבה מבוקשת ל-190: {pension_190_start:,.0f} ש"ח
- קרן חירום: {emergency_fund:,.0f} ש"ח
- שווי נדל"ן התחלתי: {property_value_start:,.0f} ש"ח

[תוצאות שווי התיק הנזיל - נקודות מפתח]
- מסלול תיקון 190 בגיל פרישה ({retire_age:.1f}): {balance_190_retire:,.0f} ש"ח
- מסלול 25% מס ריאלי בגיל פרישה ({retire_age:.1f}): {balance_25_retire:,.0f} ש"ח
- מסלול תיקון 190 בגיל 100: {balance_190_at_100:,.0f} ש"ח
- מסלול 25% מס ריאלי בגיל 100: {balance_25_at_100:,.0f} ש"ח
============================================"""

    # הצגת קופסת קוד נוחה להעתקה מיידית (לחיצה על האייקון בצד ימין למעלה של התיבה מעתיקה הכל)
    st.code(copy_text, language="text")
    
    # הצגת שורת סיכום מהירה בטבלה קטנה מתחת, סתם כדי שיהיה לך מול העיניים בלי להעתיק
    st.write("---")
    st.markdown("**🔍 מבט מהיר על תוצאות התיק הנזיל:**")
    df_summary_row = pd.DataFrame({
        "נקודת זמן בסימולציה": [f"גיל פרישה ({retire_age:.1f})", "גיל 100.0"],
        "תיקון 190": [format_shekel(balance_190_retire), format_shekel(balance_190_at_100)],
        "מסלול 25% מס ריאלי": [format_shekel(balance_25_retire), format_shekel(balance_25_at_100)]
    })
    st.table(df_summary_row.set_index("נקודת זמן בסימולציה"))
