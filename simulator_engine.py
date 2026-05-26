import pandas as pd
import numpy as np

def run_simulation(user_inputs):
    """
    מנוע סימולציה אקטוארי היברידי (Gold Standard) - גרסה סופית ומאושרת.
    מנהל תזרים מזומנים חודשי מבוסס עודף/חוסר, הצמדות ריאליות מול נומינליות,
    ומעקב יחסי אחרי בסיס המס במקור.
    """
    # 1. שליפת קלטים מוגנת מהממשק (UI Keys Synchronization)
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
    
    # תשואות חודשיות נטו (בניכוי דמי ניהול ישיר)
    r_monthly_190 = (1 + (float(amendment_190.get("annual_return_190", 0.05)) - float(amendment_190.get("management_fee_190", 0.006)))) ** (1/12) - 1
    r_monthly_25 = (1 + (float(real_tax_25.get("annual_return_25", 0.05)) - float(real_tax_25.get("management_fee_25", 0.006)))) ** (1/12) - 1

    # הון התחלתי ובסיס מס במקור
    balance_190 = float(amendment_190.get("net_for_190", 0))
    basis_190 = balance_190
    balance_25 = float(real_tax_25.get("net_for_real_pathway", 0))
    basis_25 = balance_25
    baseline_capital = balance_25 if balance_25 > 0 else 1.0

    # נתוני בסיס לתזרים
    base_monthly_expense = float(expenses.get("current_expenses", 11000))
    work_income_static = float(expenses.get("work_income", 0))  # הכנסה מעבודה - סטטית/נומינלית
    work_end_age = float(expenses.get("work_end_age", retirement_age))
    ni_base = float(wealth.get("national_insurance", 2500))
    pension_base = float(amendment_190.get("desired_pension", 5000))
    caregiver_cost_base = float(expenses.get("caregiver_cost", 3500))
    
    # נדל"ן (מעקב חיוני לסנכרון מול קובצי הדו"חות והגרפים)
    property_value = float(wealth.get("new_apartment_cost", 5800000))
    prop_appreciation_monthly = (1 + float(wealth.get("property_appreciation", 0.023))) ** (1/12) - 1
    
    history = []
    inflation_factor = 1.0
    total_months = int((105 - start_age) * 12) + 1

    for m in range(total_months):
        current_age = start_age + (m / 12.0)
        
        # --- שלב א': עדכון מדד ואינפלציה (כולל מדרגות שמרנות) ---
        current_ann_inf = annual_inflation_base
        if current_age >= 85.0: 
            current_ann_inf += float(expenses.get("age_85_plus_increase", 0.015))
        elif current_age >= 75.0: 
            current_ann_inf += float(expenses.get("age_75_85_increase", 0.005))
        
        i_monthly = (1 + current_ann_inf) ** (1/12) - 1
        if m > 0: 
            inflation_factor *= (1 + i_monthly)

        # --- שלב ב': חישוב הוצאות נומינליות (רכיבים צמודים) ---
        curr_base_exp = base_monthly_expense
        if current_age >= 85.0: 
            curr_base_exp += caregiver_cost_base
        
        # הזרקת הוצאות מחזוריות (צמודות מדד) כל X שנים
        freq = int(expenses.get("one_time_frequency", 8) * 12)
        if m > 0 and m % freq == 0:
            curr_base_exp += float(expenses.get("one_time_expense", 80000))
            
        nominal_expense = curr_base_exp * inflation_factor

        # --- שלב ג': חישוב הכנסות נומינליות (צמודות מול סטטיות) ---
        curr_work_inc = work_income_static if current_age < work_end_age else 0.0
        
        if current_age < retirement_age:
            pension_indexed = 0.0
            ni_indexed = 0.0
        else:
            pension_indexed = pension_base * inflation_factor
            ni_indexed = ni_base * inflation_factor
            
        # בסיס ההכנסה המשותף לשני המסלולים (עבודה + ביטוח לאומי)
        base_shared_income = curr_work_inc + ni_indexed

        # --- שלב ד': לוגיקת עודף/חוסר ומשיכה מהקרנות (Net Needed) ---
        # מסלול תיקון 190 נהנה בנוסף מהקצבה המזערית הצמודה
        net_needed_190 = max(0.0, nominal_expense - (base_shared_income + pension_indexed))
        # מסלול 25% מס ריאלי נשען על הכנסות בסיס בלבד
        net_needed_25 = max(0.0, nominal_expense - base_shared_income)

        # --- שלב ה': ביצוע משיכה ומס במסלול תיקון 190 ---
        tax_190 = 0.0
        if net_needed_190 > 0 and balance_190 > 0:
            pr = max(0.0, (balance_190 - basis_190) / balance_190)
            gross = net_needed_190 / (1 - (pr * 0.15))
            pull = min(gross, balance_190)
            tax_190 = pull * pr * 0.15
            # עדכון יחסי של בסיס המס (הקרן הפטורה)
            basis_190 *= (1 - (pull / balance_190))
            balance_190 -= pull

        # --- שלב ו': ביצוע משיכה ומס במסלול 25% מס ריאלי ---
        tax_25 = 0.0
        basis_25 *= (1 + i_monthly)  # הצמדת בסיס המס החוקי למדד מדי חודש
        if net_needed_25 > 0 and balance_25 > 0:
            rpr = max(0.0, (balance_25 - basis_25) / balance_25)
            gross25 = net_needed_25 / (1 - (rpr * 0.25))
            pull25 = min(gross25, balance_25)
            tax_25 = pull25 * rpr * 0.25
            # עדכון יחסי של בסיס המס (הקרן הפטורה)
            basis_25 *= (1 - (pull25 / balance_25))
            balance_25 -= pull25

        # --- שלב ז': צבירת תשואה חודשית ועדכון נכסי נדל"ן ---
        if balance_190 > 0: 
            balance_190 *= (1 + r_monthly_190)
        if balance_25 > 0: 
            balance_25 *= (1 + r_monthly_25)
            
        property_value *= (1 + prop_appreciation_monthly)

        # רישום היסטורי מדויק ומלא (שומר על מבנה הדוחות והגרפים)
        history.append({
            "גיל": current_age, 
            "חודש": m, 
            "הוצאה נומינלית": nominal_expense,
            "הכנסה נומינלית": base_shared_income,
            "הכנסה מקצבה מזערית": pension_indexed,
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
