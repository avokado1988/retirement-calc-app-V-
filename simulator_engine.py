import pandas as pd
import numpy as np

def run_simulation(user_inputs):
    timeline = user_inputs.get("timeline", {})
    wealth = user_inputs.get("wealth", {})
    expenses = user_inputs.get("expenses", {})
    amendment_190 = user_inputs.get("amendment_190", {})
    real_tax_25 = user_inputs.get("real_tax_25", {})

    start_age = float(timeline.get("start_age", 65.5))
    retirement_age = float(timeline.get("retirement_age", 67.0))
    check_age = float(timeline.get("check_age", 87.0))
    
    annual_inflation_base = float(expenses.get("expected_inflation", 0.023))
    
    r_monthly_190 = (1 + (float(amendment_190.get("annual_return_190", 0.05)) - float(amendment_190.get("management_fee_190", 0.006)))) ** (1/12) - 1
    r_monthly_25 = (1 + (float(real_tax_25.get("annual_return_25", 0.05)) - float(real_tax_25.get("management_fee_25", 0.006)))) ** (1/12) - 1

    balance_190 = float(amendment_190.get("net_for_190", 0))
    basis_190 = balance_190
    balance_25 = float(real_tax_25.get("net_for_real_pathway", 0))
    basis_25 = balance_25
    baseline_capital = balance_25 if balance_25 > 0 else 1.0

    base_monthly_expense = float(expenses.get("current_expenses", 11000))
    work_income_static = float(expenses.get("work_income", 0)) 
    work_end_age = float(expenses.get("work_end_age", retirement_age))
    ni_base = float(wealth.get("national_insurance", 2500))
    pension_base = float(amendment_190.get("desired_pension", 5000))
    caregiver_cost_base = float(expenses.get("caregiver_cost", 0))
    
    property_value = float(wealth.get("new_apartment_cost", 5800000))
    prop_appreciation_monthly = (1 + float(wealth.get("property_appreciation", 0.023))) ** (1/12) - 1

    history = []
    inflation_factor = 1.0
    retirement_inflation_factor = 1.0  
    total_months = int((105 - start_age) * 12) + 1

    for m in range(total_months):
        current_age = start_age + (m / 12.0)
        
        current_ann_inf = annual_inflation_base
        if current_age >= 85.0: current_ann_inf += float(expenses.get("age_85_plus_increase", 0.015))
        elif current_age >= 75.0: current_ann_inf += float(expenses.get("age_75_85_increase", 0.005))
        
        i_monthly = (1 + current_ann_inf) ** (1/12) - 1
        
        if m > 0: 
            inflation_factor *= (1 + i_monthly)
        
        # המדד של הפנסיה מתחיל לעלות רק בחודש *שאחרי* הפרישה
        if current_age > retirement_age:
            retirement_inflation_factor *= (1 + i_monthly)

        curr_base_exp = base_monthly_expense
        if current_age >= 85.0: curr_base_exp += caregiver_cost_base
        
        freq = int(expenses.get("one_time_frequency", 8) * 12)
        if freq > 0 and m > 0 and m % freq == 0:
            curr_base_exp += float(expenses.get("one_time_expense", 80000))
            
        nominal_expense = curr_base_exp * inflation_factor

        curr_work_inc = work_income_static if current_age < work_end_age else 0.0
        
        ni_indexed = ni_base * inflation_factor
        if current_age >= retirement_age:
            p_indexed = pension_base * retirement_inflation_factor
        else:
            p_indexed = 0.0
            
        # 🟢 הכנסת בסיס בלבד (עבודה + ב"ל)
        base_income = curr_work_inc + ni_indexed
        
        net_needed_190 = max(0.0, nominal_expense - (base_income + p_indexed))
        net_needed_25 = max(0.0, nominal_expense - base_income)

        # 🛑 חסימה מוחלטת: אין משיכות מהתיק לפני פרישה
        if current_age < retirement_age:
            net_needed_190 = 0.0
            net_needed_25 = 0.0

        # --- משיכה 190 ---
        tax_190 = 0.0
        if net_needed_190 > 0 and balance_190 > 0:
            pr = max(0.0, (balance_190 - basis_190) / balance_190)
            gross = net_needed_190 / (1 - (pr * 0.15))
            pull = min(gross, balance_190)
            tax_190 = pull * pr * 0.15
            basis_190 *= (1 - (pull / balance_190))
            balance_190 -= pull

        # --- משיכה 25% ---
        tax_25 = 0.0
        if net_needed_25 > 0 and balance_25 > 0:
            rpr = max(0.0, (balance_25 - basis_25) / balance_25)
            gross25 = net_needed_25 / (1 - (rpr * 0.25))
            pull25 = min(gross25, balance_25)
            tax_25 = pull25 * rpr * 0.25
            basis_25 *= (1 - (pull25 / balance_25))
            balance_25 -= pull25
        if m > 0: basis_25 *= (1 + i_monthly)

        if balance_190 > 0: balance_190 *= (1 + r_monthly_190)
        if balance_25 > 0: balance_25 *= (1 + r_monthly_25)
        property_value *= (1 + prop_appreciation_monthly)

        history.append({
            "גיל": current_age, "חודש": m, "הוצאה נומינלית": nominal_expense,
            "הכנסה נומינלית": base_income, # 🟢 כאן נכנס רק ביטוח לאומי (2500)
            "הכנסה מקצבה מזערית": p_indexed, # 🟢 כאן נכנסת הפנסיה (5000)
            "צבירה תיקון 190": balance_190, "צבירה מסלול ריאלי": balance_25,
            "מס ששולם 190": tax_190, "מס ששולם 25": tax_25,
            "שווי נדלן": property_value, "inflation_factor": inflation_factor
        })

    df_full = pd.DataFrame(history)
    row_97 = df_full[df_full["גיל"] >= 97.0].iloc[0] if not df_full[df_full["גיל"] >= 97.0].empty else df_full.iloc[-1]
    
    return {
        "df": df_full[df_full["גיל"] <= check_age], "df_full": df_full,
        "ratio_190_97": float(row_97["צבירה תיקון 190"] / baseline_capital),
        "ratio_25_97": float(row_97["צבירה מסלול ריאלי"] / baseline_capital)
    }
