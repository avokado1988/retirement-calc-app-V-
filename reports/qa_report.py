import streamlit as st
import pandas as pd
from inputs.ui_components import format_shekel

def render_qa_section(results, user_inputs):
    # --- הזרקת CSS בטוחה ליישור מימין לשמאל (RTL) ---
    st.markdown("<style>.stTable, table { direction: rtl !important; text-align: right !important; } th, td { text-align: right !important; direction: rtl !important; }</style>", unsafe_allow_html=True)

    df_history = results["df"]
    
    timeline = user_inputs["timeline"]
    wealth = user_inputs["wealth"]
    
    start_age = float(timeline["start_age"])
    check_age = float(timeline["check_age"])
    
    # --- הגנת TypeError: הכרחת כל הנתונים להיות מספרים (float) ---
    initial_capital_190 = float(user_inputs["amendment_190"]["net_for_190"] or 0)
    initial_capital_25 = float(user_inputs["real_tax_25"]["net_for_real_pathway"] or 0)
    
    property_value_start = float(wealth["new_apartment_cost"] or 0)
    appreciation_rate = float(wealth["property_appreciation"] or 0)
    emergency_fund = float(wealth["emergency_fund"] or 0)
    pension_190_start = float(user_inputs["amendment_190"]["desired_pension"] or 0)
    
    row_start = df_history.iloc[0]
    exp_start = float(row_start["הוצאה נומינלית"])
    inc_start = float(row_start["הכנסה נומינלית"])
    
    df_filtered = df_history[df_history["גיל"] >= check_age]
    if not df_filtered.empty:
        row_check = df_filtered.iloc[0]
    else:
        row_check = df_history.iloc[-1]
        
    exp_check = float(row_check["הוצאה נומינלית"])
    inc_check = float(row_check["הכנסה נומינלית"])
    balance_190_check = float(row_check["צבירה תיקון 190"])
    balance_25_check = float(row_check["צבירה מסלול ריאלי"])
    
    years_passed = check_age - start_age
    property_value_check = property_value_start * ((1 + appreciation_rate) ** years_passed)
    
    # --- חישובי טבלה 1 ---
    net_needed_190_start = max(0.0, exp_start - inc_start - pension_190_start)
    net_needed_25_start = max(0.0, exp_start - inc_start)
    
    pct_190_start = (net_needed_190_start * 12) / max(1.0, initial_capital_190) * 100
    pct_25_start = (net_needed_25_start * 12) / max(1.0, initial_capital_25) * 100
    
    total_wealth_190_start = initial_capital_190 + property_value_start + emergency_fund
    total_wealth_25_start = initial_capital_25 + property_value_start + emergency_fund

    # --- חישובי טבלה 2 ---
    net_needed_190_check = max(0.0, exp_check - inc_check - pension_190_start)
    net_needed_25_check = max(0.0, exp_check - inc_check)
    
    pct_190_check = (net_needed_190_check * 12) / max(1.0, balance_190_check) * 100 if balance_190_check > 0 else 0
    pct_25_check = (net_
