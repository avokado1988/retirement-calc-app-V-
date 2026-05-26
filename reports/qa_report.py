import streamlit as st
import pandas as pd
from inputs.ui_components import (
    format_shekel,
    wrap_html_style,
    get_withdrawal_style,
    get_400_rule_style,
    get_emergency_style,
    get_larger_portfolio_style,
    get_resiliency_style,
    get_preservation_pct_style,
    get_boolean_style
)

def render_qa_section(results, user_inputs):
    # CSS ליישור מימין לשמאל ועיצוב רשת טבלה אחידה ומקצועית לרינדור HTML
    st.markdown("""
        <style>
        .styled-table { width: 100% !important; direction: rtl !important; text-align: right !important; border-collapse: collapse; margin: 15px 0; font-family: sans-serif; }
        .styled-table th { background-color: #f3f4f6; color: #1f2937; text-align: right !important; padding: 10px !important; font-weight: bold; border-bottom: 2px solid #e5e7eb; }
        .styled-table td { padding: 8px !important; text-align: right !important; border-bottom: 1px solid #f3f4f6; }
        </style>
    """, unsafe_allow_html=True)

    df_history = results["df"]
    df_full = results.get("df_full", df_history)
    
    timeline = user_inputs.get("timeline", {})
    wealth = user_inputs.get("wealth", {})
    expenses = user_inputs.get("expenses", {})
    
    start_age = float(timeline.get("start_age", 65.5))
    check_age = float(timeline.get("check_age", 87.0))
    retire_age = float(timeline.get("retirement_age", start_age))
    
    amendment_190 = user_inputs.get("amendment_190", {})
    real_tax_25 = user_inputs.get("real_tax_25", {})
    
    initial_capital_190 = float(amendment_190.get("net_for_190") or 0)
    initial_capital_25 = float(real_tax_25.get("net_for_real_pathway") or 0)
    
    baseline_capital = initial_capital_25
    
    property_value_start = float(wealth.get("new_apartment_cost") or 0)
    appreciation_rate = float(wealth.get("property_appreciation") or 0)
    emergency_fund = float(wealth.get("emergency_fund") or 0)
    pension_190_start = float(amendment_190.get("desired_pension") or 0)
    
    # --- 1. נקודת הפרישה ---
    df_retire = df_history[df_history["גיל"] >= retire_age]
    row_retire = df_retire.iloc[0] if not df_retire.empty else df_history.iloc[-1]
        
    exp_retire = float(row_retire["הוצאה נומינלית"])
    inc_retire = float(row_retire["הכנסה נומינלית"])
    balance_190_retire = float(row_retire["צבירה תיקון 190"])
    balance_25_retire = float(row_retire["צבירה מסלול ריאלי"])
    
    years_to_retire = retire_age - start_age
    property_value_retire = property_value_start * ((1 + appreciation_rate) ** years_to_retire)
    
    if "הכנסה מקצבה מזערית" in row_retire:
        pension_190_indexed_retire = float(row_retire["הכנסה מקצבה מזערית"])
    else:
        inf_factor_retire = float(row_retire.get("inflation_factor", 1.0))
        pension_190_indexed_retire = pension_190_start * inf_factor_retire

    net_needed_190_retire = max(0.0, exp_retire - inc_retire - pension_190_indexed_retire)
    net_needed_25_retire = max(0.0, exp_retire - inc_retire)
    
    pct_190_retire = (net_needed_190_retire * 12) / balance_190_retire * 100 if balance_190_retire > 0 else 0.0
    pct_25_retire = (net_needed_25_retire * 12) / balance_25_retire * 100 if balance_25_retire > 0 else 0.0
        
    rule400_190_retire = f"{balance_190_retire / (net_needed_190_retire * 400):.2f}" if net_needed_190_retire > 0 else "∞"
    emer_190_retire = f"{emergency_fund / (net_needed_190_retire * 12):.1f}" if net_needed_190_retire > 0 else "∞"
        
    rule400_25_retire = f"{balance_25_retire / (net_needed_25_retire * 400):.2f}" if net_needed_25_retire > 0 else "∞"
    emer_25
