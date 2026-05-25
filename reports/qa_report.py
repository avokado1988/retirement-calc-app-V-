import streamlit as st
import pandas as pd
from inputs.ui_components import format_shekel

def render_qa_section(results, user_inputs):
    try:
        # --- 1. חילוץ משתנים בצורה בטוחה ---
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
        
        # --- 2. נתוני התחלה ---
        row_start = df_history.iloc[0]
        exp_start = float(row_start["הוצאה נומינלית"])
        inc_start = float(row_start["הכנסה נומינלית"])
        pension_190_start = float(user_inputs["amendment_190"]["desired_pension"])
        
        # --- 3. נתוני גיל נבדק ---
        filtered_df = df_history[df_history["גיל"] >= check_age]
        if len(filtered_df) > 0:
            row_check = filtered_df.iloc[0]
        else:
            row_check = df_history.iloc[-1]
            
        exp_check = float(row_check["הוצאה נומינלית"])
        inc_check = float(row_check["הכנסה נומינלית"])
        inflation_factor_check = float(row_check["inflation_factor"])
        balance_190_check = float(row_check["צבירה תיקון 190"])
        balance_25_check = float(row_check["צבירה מסלול ריאלי"])
        
        years_passed = check_age - start_age
        property_value_check = property_value_start * ((1 + appreciation_rate) ** years_passed)
        
        # --- 4. מציאת גיל שחיקה ---
        burn_age_190 = 99.0
        burn_age_25 = 83.0
        empty_age_190 = 120.0
        empty_age_25 = 120.0
        
        for idx in range(1, len(df_full)):
            if float(df_full.iloc[idx]["צבירה תיקון 190"]) < float(df_full.iloc[idx-1]["צבירה תיקון 190"]):
                burn_age_190 = float(df_full.iloc[idx]["גיל"])
                break
                
        for idx in range(1, len(df_full)):
            if float(df_full.iloc[idx]["צבירה מסלול ריאלי"]) < float(df_full.iloc[idx-1]["צבירה מסלול ריאלי"]):
                burn_age_25 = float(df_full.iloc[idx]["גיל"])
                break
                
        for idx in range(len(df_full)):
            if float(df_full.iloc[idx]["צבירה תיקון 190"]) <= 0:
                empty_age_190 = float(df_full.iloc[idx]["גיל"])
                break
                
        for idx in range(len(df_full)):
            if float(df_full.iloc[idx]["צבירה מסלול ריאלי"]) <= 0:
                empty_age_25 = float(df_full.iloc[idx]["גיל"])
                break

        ratio_190_97 = float(results.get("ratio_190_97", 0.0))
        ratio_25_97 = float(results.get("ratio_25_97", 0.0))

        # --- 5. חישובים לטבלה 1 ---
        net_needed_190_start = max(0.0, exp_start - inc_start - pension_190_start)
        net_needed_25_start = max(0.0, exp_start - inc_start)
        
        pct_w_190_start = (net_needed_190_start * 12) / max(1.0, initial_capital_190) * 100
        pct_w_25_start = (net_needed_25_start * 12) / max(1.0, initial_capital_25) * 100
        
        if net_needed_190_start > 0:
            val_400_190_st = initial_capital_190 / (net_needed_190_start * 12 * 25)
            rule_190_str = f"{val_400_190_st:.1f}"
            val_emer_190 = emergency_fund / (net_needed_190_start * 12)
            emer_190_str = f"{val_emer_190:.1f}"
        else:
            rule_190_str = "∞"
            emer_190_str = "∞"
            
        if net_needed_25_start > 0:
            val_400_25_st = initial_capital_25 / (net_needed_25_start * 12 * 25)
            rule_25_str = f"{val_400_25_st:.1f}"
            val_emer_25 = emergency_fund / (net_needed_25_start * 12)
            emer_25_str = f"{val_emer_25:.1f}"
        else:
            rule_25_str = "∞"
            emer_25_str = "∞"
            
        total_wealth_190_start = initial_capital_190 + property_value_start + emergency_fund
        total_wealth_25_start = initial_capital_25 + property_value_start + emergency_fund

        t1_1_190 = format_shekel(initial_capital_190)
        t1_1_25 = format_shekel(initial_capital_25)
        t1_2 = format_shekel(property_value_start)
        t1_3_190 = format_shekel(inc_start + pension_190_start)
        t1_3_25 = format_shekel(inc_start)
        t1_4_190 = f"-{format_shekel(net_needed_190_start)}"
        t1_4_25 = f"-{format_shekel(net_needed_25_start)}"
        t1_5_190 = f"{pct_w_190_start
