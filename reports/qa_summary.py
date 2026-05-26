import streamlit as st
import pandas as pd
from inputs.ui_components import format_shekel

def render_qa_summary_page(results, user_inputs):
    """
    קובץ בדיקות (QA) עצמאי לחלוטין - ריכוז אינפוטים ושורות סיכום להעתקה מהירה
    """
    df_history = results["df"]
    df_full = results.get("df_full", df_history)
    
    # מיפוי המילונים הקיימים באפליקציה
    timeline = user_inputs.get("timeline", {})
    wealth = user_inputs.get("wealth", {})
    expenses = user_inputs.get("expenses", {})
    amendment_190 = user_inputs.get("amendment_190", {})
    real_tax_25 = user_inputs.get("real_tax_25", {})
    
    start_age = float(timeline.get("start_age", 65.5))
    check_age = float(timeline.get("check_age", 87.0))
    retire_age = float(timeline.get("retirement_age", start_age))
    
    # שליפת הערכים המדויקים מהסליידרים
    inflation = float(expenses.get("expected_inflation", 0.023))
    yield_190 = float(amendment_190.get("annual_return_190", 0.05))
    fee_190 = float(amendment_190.get("management_fee_190", 0.005))
    
    yield_25 = float(real_tax_25.get("annual_return_25", 0.05))
    fee_25 = float(real_tax_25.get("management_fee_25", 0.005))
    
    initial_capital_190 = float(amendment_190.get("net_for_190") or 0)
    initial_capital_25 = float(real_tax_25.get("net_for_real_pathway") or 0)
    
    base_exp = float(expenses.get("current_expenses", 11000))
    work_inc = float(expenses.get("work_income", 0))
    work_end_age = float(expenses.get("work_end_age", retire_age)) # 🟢 השליפה של גיל סיום עבודה בפועל
    base_inc_ni = float(wealth.get("national_insurance", 2591))
    
    property_value_start = float(wealth.get("new_apartment_cost") or 0)
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
    
    # בניית גוש הטקסט המרוכז להעתקה - כולל גיל הפסקת העבודה הדינמי
    copy_text = f"""=== סימולציית פרישה אקטוארית - דוח QA מהיר ===

[פרמטרים ואינפוטים שנבחרו]
- גיל התחלה: {start_age}
- גיל פרישה (קבלת פנסיה): {
