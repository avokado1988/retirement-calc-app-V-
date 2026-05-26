import pandas as pd
import numpy as np

def run_simulation(user_inputs):
    """
    מנוע סימולציה אקטוארי בכיר (Gold Standard) - גרסה סופית ומאושרת.
    כולל מדרגות שמרנות לפי גיל, הוצאות מחזוריות, הצמדות נדל"ן וניהול בסיס מס במקור.
    """
    # 1. שליפת קלטים מוגנת
    timeline = user_inputs.get("timeline", {})
    wealth = user_inputs.get("wealth", {})
    expenses = user_inputs.get("expenses", {})
    amendment_190 = user_inputs.get("amendment_190", {})
    real_tax_25 = user_inputs.get("real_tax_25", {})

    # גילאים
    start_age = float(timeline.get("start_age", 65.5))
    retirement_age = float(timeline.get("retirement_age", 67.0))
    check_age = float(timeline.get("check_age", 87.0))
    
    # פרמטרים כלכליים בסיסיים
    annual_inflation_base = float(expenses.get("expected_inflation", 0.023))
    
    # חישוב תשואות נטו חודשיות (ניכוי דמי ניהול ישיר וקריאה מאובטחת מה-UI)
    return_190 = float(amendment_190.get("annual_return_190", 0.05))
    fee_190 = float(amendment_190.get("management_fee_190", 0.003))
    r_monthly_190 = (1 + (return_190 - fee_190)) ** (1/12) - 1

    return_25 = float(real_tax_25.get("annual_return_25", 0.05))
    fee_25 = float(real_tax_25.get("management_fee_25", 0.003))
    r_monthly_25 = (1 + (return_25 - fee_25)) ** (1/12) - 1

    # הון התחלתי ובסיס מס במקור
    balance_190 = float(amendment_190.get("net_for_190", 2240000))
    basis_190 = balance_190
    balance_25 = float(real_tax_25.get("net_for_real_pathway", 3340000))
    basis_25 = balance_25
    
    baseline_capital = balance_25  # בייסליין להשוואת תפוחים לתפוחים

    # תזרימי בסיס מהממשק
    base_expense = float(expenses.get("current_expenses", 11000))
    work_income = float(expenses.get("work_income", 0))
    work_end_age = float(expenses.get("work_end_age", retirement_age))
    national_insurance = float(wealth.get("national_insurance", 2591))
    pension_190_start = float(amendment_190.get("desired_pension", 5000))
    caregiver_cost = float(expenses.get("caregiver_cost", 3500))
    
    # נכסי נדל"ן
    property_value = float(wealth.get("new_apartment_cost", 5800000))
    prop_appreciation_monthly = (1 + float(wealth.get("property_appreciation", 0.023))) ** (1/12) - 1

    history = []
    inflation_factor = 1.0
    total_months = int((105 - start_age) * 12) + 1

    for m in range(total_months):
        current_age = start_age + (m / 12.0)
        
        # לוגיקת מדרגות שמרנות דינמיות (Age Jumps לאינפלציה)
        current_ann_inf = annual_inflation_base
        if current_age >= 85.0:
            current_ann_inf += float(expenses.get("age_85_plus_increase", 0.015))
        elif current_age >= 75.0:
            current_ann_inf += float(expenses.get("age_75_85_increase", 0.005))
        
        i_monthly = (1 + current_ann_inf) ** (1/12) - 1
        if m > 0:
            inflation_factor *= (1 + i_monthly)

        # חישוב הוצאה חודשית נומינלית (כולל קפיצה סיעודית והוצאות מחזוריות)
        current_month_expense = base_expense
        if current_age >= 85.0:
            current_month_expense += caregiver_cost
            
        # הזרקת "מכות" של הוצאה חד פעמית כל X שנים (שוקי אקטוארי)
        one_time_freq = int(expenses.get("one_time_frequency", 8) * 12)
        if m > 0 and m % one_time_freq == 0:
            current_month_expense += float(expenses.get("one_time_expense", 80000))
            
        nominal_expense = current_month_expense * inflation_factor
        
        # חישוב הכנסות שוטפות לפי שלבי חיים
        current_work_inc = (work_income * inflation_factor) if current_age < work_end_age else 0.0
        if current_age < retirement_age:
            pension_190_indexed = 0.0
            nominal_passive_inc = 0.0
        else:
            pension_190_indexed = pension_190_start * inflation_factor
            nominal_passive_inc = national_insurance * inflation_factor
            
        current_total_income = current_work_inc + nominal_passive_inc
        
        # חוסר חודשי למשיכה מהקופות
        net_needed_190 = max(0.0, nominal_expense - current_total_income - pension_190_indexed)
        net_needed_25 = max(0.0, nominal_expense - current_total_income)

        # --- משיכה ומס: מסלול תיקון 190 ---
        tax_190 = 0.0
        if net_needed_190 > 0 and balance_190 > 0:
            profit_ratio = max(0.0, (balance_190 - basis_190) / balance_190)
            gross = net_needed_190 / (1 - (profit_ratio * 0.15))
            actual_pull = min(gross, balance_190)
            tax_190 = actual_pull * profit_ratio * 0.15
            basis_190 *= (1 - (actual_pull / balance_190))
            balance_190 -= actual_pull

        # --- משיכה ומס: מסלול 25% מס ריאלי ---
        tax_25 = 0.0
        basis_25 *= (1 + i_monthly)  # הצמדת בסיס המס (קרן פטורה) למדד הדינמי
        if net_needed_25 > 0 and balance_25 > 0:
            real_profit_ratio = max(0.0, (balance_25 - basis_25) / balance_25)
            gross_25 = net_needed_25 / (1 - (real_profit_ratio * 0.25))
            actual_pull_25 = min(gross_25, balance_25)
            tax_25 = actual_pull_25 * real_profit_ratio * 0.25
            basis_25 *= (1 - (actual_pull_25 / balance_25))
            balance_25 -= actual_pull_25

        # ריבית דריבית חודשית וצמיחת שווי נדל"ן
        if balance_190 > 0: 
            balance_190 *= (1 + r_monthly_190)
        if balance_25 > 0: 
            balance_25 *= (1 + r_monthly_25)
            
        property_value *= (1 + prop_appreciation_monthly)

        history.append({
            "גיל": current_age,
            "חודש": m,
            "הוצאה נומינלית": nominal_expense,
            "הכנסה נומינלית": current_total_income,
            "הכנסה מקצבה מזערית": pension_190_indexed,
            "צבירה תיקון 190": balance_190,
            "צבירה מסלול ריאלי": balance_25,
            "מס ששולם 190": tax_190,
            "מס ששולם 25": tax_25,
            "שווי נדלן": property_value,
            "inflation_factor": inflation_factor
        })

    df_full = pd.DataFrame(history)
    row_97 = df_full[df_full["גיל"] >= 97.0].iloc[0] if not df_full[df_full["גיל"] >= 97.0].empty else df_full.iloc[-1]

    return {
        "df": df_full[df_full["גיל"] <= check_age],
        "df_full": df_full,
        "ratio_190_97": float(row_97["צבירה תיקון 190"] / baseline_capital),
        "ratio_25_97": float(row_97["צבירה מסלול ריאלי"] / baseline_capital)
    }
