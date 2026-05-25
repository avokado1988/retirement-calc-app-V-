import pandas as pd
import numpy as np

def calculate_inflation_factor(months, annual_inflation):
    monthly_inflation = (1 + annual_inflation) ** (1 / 12) - 1
    return (1 + monthly_inflation) ** months

def run_simulation(user_inputs):
    timeline = user_inputs["timeline"]
    wealth = user_inputs["wealth"]
    expenses = user_inputs["expenses"]
    amendment_190 = user_inputs["amendment_190"]
    real_tax_25 = user_inputs["real_tax_25"]
    
    start_age = float(timeline["start_age"])
    check_age = float(timeline["check_age"])
    total_months = 480  # 40 שנה קבוע ומאובטח
    
    r_190 = (1 + (amendment_190["annual_return_190"] - amendment_190["management_fee_190"])) ** (1/12) - 1
    r_25 = (1 + (real_tax_25["annual_return_25"] - real_tax_25["management_fee_25"])) ** (1/12) - 1
    
    annual_inflation_base = expenses["expected_inflation"]
    
    balance_190 = amendment_190["net_for_190"]
    invested_capital_190 = balance_190
    pension_received = amendment_190["desired_pension"]
    
    balance_25 = real_tax_25["net_for_real_pathway"]
    basis_25 = balance_25
    base_initial_capital = wealth["remaining_for_gimel"]
    
    history = []
    balance_190_97 = 0.0
    balance_25_97 = 0.0
    
    for m in range(total_months):
        current_age = start_age + (m / 12)
        
        current_annual_inflation = annual_inflation_base
        if current_age >= 85.0:
            current_annual_inflation += 0.015
        elif current_age >= 75.0:
            current_annual_inflation += 0.005
            
        i_monthly = (1 + current_annual_inflation) ** (1/12) - 1
        
        if m == 0:
            inflation_factor = 1.0
        else:
            inflation_factor = history[-1]["inflation_factor"] * (1 + i_monthly)
            
        base_expense = expenses["current_expenses"]
        if current_age >= 85.0:
            base_expense += expenses["caregiver_cost"]
            
        frequency_months = expenses["one_time_frequency"] * 12
        if m > 0 and m % frequency_months == 0:
            base_expense += expenses["one_time_expense"]
            
        if current_age < timeline["retirement_age"]:
            base_expense = max(0, base_expense - expenses["work_income"])
            
        nominal_expense = base_expense * inflation_factor
        nominal_income = wealth["national_insurance"] * inflation_factor
        net_needed_base = max(0, nominal_expense - nominal_income)
        
        # --- תיקון 190 ---
        net_needed_190 = max(0, net_needed_base - (pension_received * inflation_factor))
        gross_withdrawn_190 = 0.0
        tax_paid_month_190 = 0.0
        
        if balance_190 > 0 and net_needed_190 > 0:
            current_net_target = min(net_needed_190, balance_190)
            profit_ratio_190 = max(0.0, (balance_190 - invested_capital_190) / balance_190) if balance_190 > 0 else 0.0
            gross_withdrawn_190 = current_net_target / (1 - (profit_ratio_190 * 0.15))
            
            if gross_withdrawn_190 > balance_190:
                gross_withdrawn_190 = balance_190
                tax_paid_month_190 = gross_withdrawn_190 * profit_ratio_190 * 0.15
            else:
                tax_paid_month_190 = gross_withdrawn_190 - current_net_target
                
            balance_190 -= gross_withdrawn_190
            invested_capital_190 *= (1 - (gross_withdrawn_190 / (balance_190 + gross_withdrawn_190)))
            
        if balance_190 > 0:
            balance_190 *= (1 + r_190)
            
        # --- מסלול 25% ---
        basis_25 *= (1 + i_monthly)
        gross_withdrawn_25 = 0.0
        tax_paid_month_25 = 0.0
        
        if balance_25 > 0 and net_needed_base > 0:
            current_net_target_25 = min(net_needed_base, balance_25)
            real_profit_total = max(0.0, balance_25 - basis_25)
            real_profit_ratio = real_profit_total / balance_25 if balance_25 > 0 else 0.0
            gross_withdrawn_25 = current_net_target_25 / (1 - (real_profit_ratio * 0.25))
            
            if gross_withdrawn_25 > balance_25:
                gross_withdrawn_25 = balance_25
                tax_paid_month_25 = max(0.0, balance_25 - basis_25) * 0.25
            else:
                tax_paid_month_25 = gross_withdrawn_25 - current_net_target_25
                
            balance_25 -= gross_withdrawn_25
            principal_portion = gross_withdrawn_25 * (1 - real_profit_ratio)
            basis_25 = max(0.0, basis_25 - principal_portion)
            
        if balance_25 > 0:
            balance_25 *= (1 + r_25)

        if current_age >= 97.0 and balance_190_97 == 0.0:
            balance_190_97 = balance_190
            balance_25_97 = balance_25

        history.append({
            "חודש": m + 1,
            "גיל": round(current_age, 2),
            "הוצאה נומינלית": int(nominal_expense),
            "הכנסה נומינלית": int(nominal_income),
            "צבירה תיקון 190": int(balance_190),
            "צבירה מסלול ריאלי": int(balance_25),
            "מס ששולם 190": tax_paid_month_190,
            "מס ששולם 25": tax_paid_month_25,
            "inflation_factor": inflation_factor
        })

    df_full = pd.DataFrame(history)
    df_user_view = df_full[df_full["גיל"] <= check_age]
    if df_user_view.empty:
        df_user_view = df_full
        
    row_user_end = df_user_view.iloc[-1]
    
    if balance_190_97 == 0.0:
        row_97_fallback = df_full[df_full["גיל"] >= 97.0]
        balance_190_97 = row_97_fallback.iloc[0]["צבירה תיקון 190"] if not row_97_fallback.empty else 0.0
        balance_25_97 = row_97_fallback.iloc[0]["צבירה מסלול ריאלי"] if not row_97_fallback.empty else 0.0

    return {
        "df": df_user_view,
        "end_balance_190_gross": int(row_user_end["צבירה תיקון 190"]),
        "end_balance_190_net": int(row_user_end["צבירה תיקון 190"] * 0.95), 
        "total_tax_paid_190": int(df_user_view["מס ששולם 190"].sum()),
        "end_balance_25_gross": int(row_user_end["צבירה מסלול ריאלי"]),
        "end_balance_25_net": int(row_user_end["צבירה מסלול ריאלי"] * 0.93),
        "total_tax_paid_25": int(df_user_view["מס ששולם 25"].sum()),
        "ratio_190_97": float(balance_190_97 / max(1, base_initial_capital)),
        "ratio_25_97": float(balance_25_97 / max(1, base_initial_capital)),
        "df_full": df_full
    }
