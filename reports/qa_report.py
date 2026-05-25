import streamlit as st
import pandas as pd
from inputs.ui_components import format_shekel

def render_qa_section(results, user_inputs):
    df_history = results["df"]
    
    # שליפת משתנים מהממשק
    timeline = user_inputs["timeline"]
    wealth = user_inputs["wealth"]
    expenses = user_inputs["expenses"]
    
    start_age = timeline["start_age"]
    check_age = timeline["check_age"]
    
    initial_capital_190 = user_inputs["amendment_190"]["net_for_190"]
    initial_capital_25 = user_inputs["real_tax_25"]["net_for_real_pathway"]
    
    property_value_start = wealth["new_apartment_cost"]
    appreciation_rate = wealth["property_appreciation"]
    emergency_fund = wealth["emergency_fund"]
    
    # חילוץ נתונים לתחילת פרישה
    row_start = df_history.iloc[0]
    exp_start = row_start["הוצאה נומינלית"]
    inc_start = row_start["הכנסה נומינלית"]
    pension_190_start = user_inputs["amendment_190"]["desired_pension"]
    
    # חילוץ נתונים לגיל הנבדק בצורה בטוחה
    df_check_filter = df_history[df_history["גיל"] >= check_age]
    if len(df_check_filter) > 0:
        row_check = df_check_filter.iloc[0]
    else:
        row_check = df_history.iloc[-1]
        
    exp_check = row_check["הוצאה נומינלית"]
    inc_check = row_check["הכנסה נומינלית"]
    inflation_factor_check = row_check["inflation_factor"]
    balance_190_check = row_check["צבירה תיקון 190"]
    balance_25_check = row_check["צבירה מסלול ריאלי"]
    
    years_passed = check_age - start_age
    property_value_check = property_value_start * ((1 + appreciation_rate) ** years_passed)
    
    # מציאת גיל שחיקה מתוך הטבלה המלאה (עד גיל 105)
    df_full = results["df_full"] if "df_full" in results else df_history
    burn_age_190 = 99.0
    burn_age_25 = 83.0
    
    for idx in range(1, len(df_full)):
        if df_full.iloc[idx]["צבירה תיקון 190"] < df_full.iloc[idx-1]["צבירה תיקון 190"]:
            burn_age_190 = df_full.iloc[idx]["גיל"]
            break
            
    for idx in range(1, len(df_full)):
        if df_full.iloc[idx]["צבירה מסלול ריאלי"] < df_full.iloc[idx-1]["צבירה מסלול ריאלי"]:
            burn_age_25 = df_full.iloc[idx]["גיל"]
            break

    # --- חישובים לטבלה 1 ---
    net_needed_190_start = max(0, exp_start - inc_start - pension_190_start)
    net_needed_25_start = max(0, exp_start - inc_start)
    
    pct_withdraw_190_start = (net_needed_190_start * 12) / max(1, initial_capital_190)
    pct_withdraw_25_start = (net_needed_25_start * 12) / max(1, initial_capital_25)
    
    total_wealth_190_start = initial_capital_190 + property_value_start + emergency_fund
    total_wealth_25_start = initial_capital_25 + property_value_start + emergency_fund

    # --- חישובים לטבלה 2 ---
    net_needed_190_check = max(0, exp_check - inc_check - (pension_190_start * inflation_factor_check))
    net_needed_25_check = max(0, exp_check - inc_check)
    
    pct_withdraw_190_check = (net_needed_190_check * 12) / max(1, balance_190_check)
    pct_withdraw_25_check = (net_needed_25_check * 12) / max(1, balance_25_check)
    
    total_wealth_190_check = balance_190_check + property_value_check
    total_wealth_25_check = balance_25_check + property_value_check

    # --- חישובים לטבלה 3 ---
    ratio_190_97 = results["ratio_190_97"] if "ratio_190_97" in results else 0.0
    ratio_25_97 = results["ratio_25_97"] if "ratio_25_97" in results else 0.0

    # ===============================================
    # הדפסת הטבלאות למסך (באמצעות DataFrame נקי)
    # ===============================================

    st.subheader(f"📊 מצב בגיל פרישה / התחלת סימולציה (גיל {start_age})")
    df_start_table = pd.DataFrame({
        "שאלה": [
            "עם כמה כסף אני מתחיל פרישה בתיק",
            "מה שווי הנדלן שלי?",
            "גובה קצבאות",
            "כמה כסף נטו אצטרך למשוך מהתיק בכל חודש
