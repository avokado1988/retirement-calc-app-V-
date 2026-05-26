import streamlit as st
import pandas as pd
from inputs.ui_components import format_shekel

def render_qa_section(results, user_inputs):
    # CSS ליישור מימין לשמאל בלבד, ללא שבירת שורות מסוכנת
    st.markdown("<style>.stTable, table { direction: rtl !important; text-align: right !important; } th, td { text-align: right !important; direction: rtl !important; }</style>", unsafe_allow_html=True)

    df_history = results["df"]
    df_full = results.get("df_full", df_history)
    
    timeline = user_inputs["timeline"]
    wealth = user_inputs["wealth"]
    
    start_age = float(timeline["start_age"])
    check_age = float(timeline["check_age"])
    retire_age = float(timeline.get("retirement_age", start_age))
    
    initial_capital_190 = float(user_inputs["amendment_190"]["net_for_190"] or 0)
    initial_capital_25 = float(user_inputs["real_tax_25"]["net_for_real_pathway"] or 0)
    
    # הבייסליין האקטוארי לכל חישובי ההתאוששות (תפוחים לתפוחים לפי הוראות)
    baseline_capital = initial_capital_25
    
    property_value_start = float(wealth["new_apartment_cost"] or 0)
    appreciation_rate = float(wealth["property_appreciation"] or 0)
    emergency_fund = float(wealth["emergency_fund"] or 0)
    pension_190_start = float(user_inputs["amendment_190"]["desired_pension"] or 0)
    
    # --- 1. נקודת הפרישה (Table 1) ---
    df_retire = df_history[df_history["גיל"] >= retire_age]
    row_retire = df_retire.iloc[0] if not df_retire.empty else df_history.iloc[-1]
    
    exp_retire = float(row_retire["הוצאה נומינלית"])
    inc_retire = float(row_retire["הכנסה נומינלית"])
    balance_190_retire = float(row_retire["צבירה תיקון 190"])
    balance_25_retire = float(row_retire["צבירה מסלול ריאלי"])
    
    years_to_retire = retire_age - start_age
    property_value_retire = property_value_start * ((1 + appreciation_rate) ** years_to_retire)
    
    net_needed_190_retire = max(0.0, exp_retire - inc_retire - pension_190_start)
    net_needed_25_retire = max(0.0, exp_retire - inc_retire)
    
    pct_190_retire = (net
