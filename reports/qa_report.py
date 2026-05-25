import streamlit as st
import pandas as pd
from inputs.ui_components import format_shekel

def render_qa_section(results, user_inputs):
    df_history = results["df"]
    df_full = results.get("df_full", df_history)
    
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
    
    row_start = df_history.iloc[0]
    exp_start = row_start["הוצאה נומינלית"]
    inc_start = row_start["הכנסה נומינלית"]
    pension_190_start = user_inputs["amendment_190"]["desired_pension"]
    
    filtered_df = df_history[df_history["גיל"] >= check_age]
    if not filtered_df.empty:
        row_check = filtered_df.iloc[0]
    else:
        row_check = df_history.iloc[-1]
    
    exp_check = row_check["הוצאה נומינלית"]
    inc_check = row_check["הכנסה נומינלית"]
    inflation_factor_check = row_check["inflation_factor"]
    balance_190_check = row_check["צבירה תיקון 190"]
    balance_25_check = row_check["צבירה מסלול ריאלי"]
    
    years_passed = check_age - start_age
    property_value_check = property_value_start * ((1 + appreciation_rate) ** years_passed)
    
    burn_age_190 = 99.0
    burn_age_25 = 83.0
    empty_age_190 = 120.0
    empty_age_25 = 120.0
    
    for idx in range(1, len(df_full)):
        if df_full.iloc[idx]["צבירה תיקון 190"] < df_full.iloc[idx-1]["צבירה תיקון 190"]:
            burn_age_190 = float(df_full.iloc[idx]["גיל"])
            break
    for idx in range(1, len(df_full)):
        if df_full.iloc[idx]["צבירה מסלול ריאלי"] < df_full.iloc[idx-1]["צבירה מסלול ריאלי"]:
            burn_age_25 = float(df_full.iloc[idx]["גיל"])
            break
            
    for idx in range(len(df_full)):
        if df_full.iloc[idx]["צבירה תיקון 190"] <= 0:
            empty_age_190 = float(df_full.iloc[idx]["גיל"])
            break
    for idx in range(len(df_full)):
        if df_full.iloc[idx]["צבירה מסלול ריאלי"] <= 0:
            empty_age_25 = float(df_full.iloc[idx]["גיל"])
            break

    ratio_190_97 = float(results.get("ratio_190_97", 0.0))
    ratio_25_97 = float(results.get("ratio_25_97", 0.0))

    # ==========================================
    # הכנת משתנים נקיים לחלוטין למניעת שגיאות Syntax
    # ==========================================
    
    # טבלה 1
    net_needed_190_start = max(0, exp_start - inc_start - pension_190_start)
    net_needed_25_start = max(0, exp_start - inc_start)
    
    val_w_190_start = (net_needed_190_start * 12) / max(1, initial_capital_190) * 100
    val_w_25_start = (net_needed_25_start * 12) / max(1, initial_capital_25) * 100
    pct_w_190_start = f"{val_w_190_start:.2f}%"
    pct_w_25_start = f"{val_w_25_start:.2f}%"
    
    if net_needed_190_start > 0:
        rule400_190_start = f"{(initial_capital_190 / max(1, net_needed_190_start * 12 * 25)):.1f}"
        emer_190 = f"{(emergency_fund / max(1, net_needed_190_start * 12)):.1f}"
    else:
        rule400_190_start = "∞"
        emer_190 = "∞"
        
    if net_needed_25_start > 0:
        rule400_25_start = f"{(initial_capital_25 / max(1, net_needed_25_start * 12 * 25)):.1f}"
        emer_25 = f"{(emergency_fund / max(1, net_needed_25_start * 12)):.1f}"
    else:
        rule400_2
