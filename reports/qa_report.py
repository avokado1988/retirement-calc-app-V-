import streamlit as st
import pandas as pd
from inputs.ui_components import format_shekel

def render_qa_section(results, user_inputs):
    # CSS ליישור מימין לשמאל בלבד
    st.markdown("<style>.stTable, table { direction: rtl !important; text-align: right !important; } th, td { text-align: right !important; direction: rtl !important; }</style>", unsafe_allow_html=True)

    df_history = results["df"]
    df_full = results.get("df_full", df_history)
    
    timeline = user_inputs.get("timeline", {})
    wealth = user_inputs.get("wealth", {})
    
    start_age = float(timeline.get("start_age", 60))
    check_age = float(timeline.get("check_age", 80))
    retire_age = float(timeline.get("retirement_age", start_age))
    
    amendment_190 = user_inputs.get("amendment_190", {})
    real_tax_25 = user_inputs.get("real_tax_25", {})
    
    initial_capital_190 = float(amendment_190.get("net_for_190") or 0)
    initial_capital_25 = float(real_tax_25.get("net_for_real_pathway") or 0)
    
    # הבייסליין האקטוארי לכל חישובי ההתאוששות (תפוחים לתפוחים לפי הדרישה)
    baseline_capital = initial_capital_25
    
    property_value_start = float(wealth.get("new_apartment_cost") or 0)
    appreciation_rate = float(wealth.get("property_appreciation") or 0)
    emergency_fund = float(wealth.get("emergency_fund") or 0)
    pension_190_start = float(amendment_190.get("desired_pension") or 0)
    
    # --- 1. נקודת הפרישה ---
    df_retire = df_history[df_history["גיל"] >= retire_age]
    if not df_retire.empty:
        row_retire = df_retire.iloc[0]
    else:
        row_retire = df_history.iloc[-1]
        
    exp_retire = float(row_retire["הוצאה נומינלית"])
    inc_retire = float(row_retire["הכנסה נומינלית"])
    balance_190_retire = float(row_retire["צבירה תיקון 190"])
    balance_25_retire = float(row_retire["צבירה מסלול ריאלי"])
    
    years_to_retire = retire_age - start_age
    property_value_retire = property_value_start * ((1 + appreciation_rate) ** years_to_retire)
    
    net_needed_190_retire = max(0.0, exp_retire - inc_retire - pension_190_start)
    net_needed_25_retire = max(0.0, exp_retire - inc_retire)
    
    pct_190_retire = 0.0
    if balance_190_retire > 0:
        pct_190_retire = (net_needed_190_retire * 12) / balance_190_retire * 100
        
    pct_25_retire = 0.0
    if balance_25_retire > 0:
        pct_25_retire = (net_needed_25_retire * 12) / balance_25_retire * 100
        
    rule400_190_retire = "∞"
    emer_190_retire = "∞"
    if net_needed_190_retire > 0:
        v_rule = balance_190_retire / (net_needed_190_retire * 400)
        rule400_190_retire = f"{v_rule:.2f}"
        v_emer = emergency_fund / (net_needed_190_retire * 12)
        emer_190_retire = f"{v_emer:.1f}"
        
    rule400_25_retire = "∞"
    emer_25_retire = "∞"
    if net_needed_25_retire > 0:
        v_rule2 = balance_25_retire /
