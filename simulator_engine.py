import pandas as pd
import numpy as np

def run_simulation(user_inputs):
    """
    מנוע סימולציה אקטוארי תקני ומיושר מול משתני ה-UI (Gold Standard).
    מפריד בין תקופת צבירה לתקופת משיכה ומבצע התאמה מלאה של מפתחות המילון.
    """
    timeline = user_inputs.get("timeline", {})
    wealth = user_inputs.get("wealth", {})
    expenses = user_inputs.get("expenses", {})
    amendment_190 = user_inputs.get("amendment_190", {})
    real_tax_25 = user_inputs.get("real_tax_25", {})
    
    # 1. שליפת גילאים מתוזמנים
    start_age = float(timeline.get("start_age", 65.5))
    retirement_age = float(timeline.get("retirement_age", 67.0))
    check_age = float(timeline.get("check_age", 99.0))
    
    # 2. נרמול ומיפוי משתני שוק חודשיים (פתרון באג ה-Key Mismatch)
    inflation_rate = float(expenses.get("expected_inflation", 0.03))
    
    yield_190 = float(amendment_190.get("annual_return_190") or amendment_190.get("yield", 0.05))
    fees_190 = float(amendment_190.get("management_fee_190") or amendment_190.get("fees", 0.005))
    
    yield_25 = float(real_tax_25.get("annual_return_25") or real_tax_25.get("yield", 0.05))
    fees_25 = float(real_tax_25.get("management_fee_25") or real_tax_25.get("fees", 0.005))
    
    r_monthly_190 = (1 + yield_190) ** (1/12) - 1
    r_monthly_25 = (1 + yield_25) ** (1/12) - 1
    f_monthly_190 = fees_190 / 12
    f_monthly_25 = fees_25 / 12
    inf_monthly = (1 + inflation_rate) ** (1/12) - 1
    
    # 3. הון התחלתי ובסיס מס במקור לקופות
    balance_190 = float(amendment_190.get("net_for_190", 2240000) or 0)
    balance_25 = float(real_tax_25.get("net_for_real_pathway", 3340000) or 0)
    
    basis_190 = balance_190
    basis_25 = balance_25
    
    # 4. תזרים מזומנים חודשי (פתרון באג מילון general)
    base_expense = float(expenses.get("current_expenses", 15000))
    work_income = float(expenses.get("work_income", 0))
    national_insurance = float(wealth.get("national_insurance", 2591))
    pension_190_start = float(amendment_190.get("desired_pension", 5000))
    
    # 5. רכיבים סיעודיים
    care_age = float(wealth.get("care_age", 85.0))
    care_cost = float(expenses.get("caregiver_cost", 3500)) # תוקן משתנה עלות המטפלת מה-UI
    
    history = []
    total_months = int((105 - start_age) * 12) + 1
    inflation_factor = 1.0
    
    for m in range(total_months):
        current_age = start_age + (m / 12.0)
        
        if m > 0:
            inflation_factor *= (1 + inf_monthly)
            
        # הוצאות שוטפות מוצמדות (כולל הוספה אקטוארית בגיל 85)
        current_expense = base_expense * inflation_factor
        if current_age >= care_age:
            current_expense += care_cost * inflation_factor
            
        # ניהול הכנסות שוטפות לפי שלב בחיים (עבודה לפני פרישה, קצבאות אחרי פרישה)
        if current_age < retirement_age:
            current_income = work_income * inflation_factor
            pension_190_indexed = 0.0
            # 🛑 פתרון באג פרישה: לפני גיל פרישה אין משיכות מהתיק לצרכי מחיה!
            net_needed_190 = 0.0
            net_needed_25 = 0.0
        else:
            current_income = national_insurance * inflation_factor
            pension_190_indexed = pension_190_start * inflation_factor
            net_needed_190 = max(0.0, current_expense - current_income - pension_190_indexed)
            net_needed_25 = max(0.0, current_expense - current_income)
            
        # --- לוגיקת מסלול תיקון 190 + מעקב מס ---
        tax_paid_month_190 = 0.0
        if net_needed_190 > 0 and balance_190 > 0:
            profit_ratio_190 = max(0.0, (balance_190 - basis_190) / balance_190)
            eff_tax_190 = profit_ratio_190 * 0.15
            gross_withdrawn_190 = net_needed_190 / (1 - eff_tax_190) if eff_tax_190 < 1 else net_needed_190
            
            if gross_withdrawn_190 > balance_190:
                tax_paid_month_190 = balance_190 * profit_ratio_190 * 0.15
                balance_190 = 0.0
            else:
                tax_paid_month_190 = gross_withdrawn_190 - net_needed_190
                balance_190 -= gross_withdrawn_190
                if balance_190 + gross_withdrawn_190 > 0:
                    basis_190 *= (balance_190 / (balance_190 + gross_withdrawn_190))
                    
        # --- לוגיקת מסלול 25% מס ריאלי + מעקב מס ---
        tax_paid_month_25 = 0.0
        basis_25 *= (1 + inf_monthly) # הצמדת קרן פטורה למדד חודשי
        
        if net_needed_25 > 0 and balance_25 > 0:
            real_profit_ratio = max(0.0, (balance_25 - basis_25) / balance_25)
            eff_tax_25 = real_profit_ratio * 0.25
            gross_withdrawn_25 = net_needed_25 / (1 - eff_tax_25) if eff_tax_25 < 1 else net_needed_25
            
            if gross_withdrawn_25 > balance_25:
                tax_paid_month_25 = balance_25 * real_profit_ratio * 0.25
                balance_25 = 0.0
            else:
                tax_paid_month_25 = gross_withdrawn_25 - net_needed_25
                balance_25 -= gross_withdrawn_25
                if balance_25 + gross_withdrawn_25 > 0:
                    basis_25 *= (balance_25 / (balance_25 + gross_withdrawn_25))
                    
        # קרדיט תשואה וניכוי דמי ניהול (משיכה בתחילת חודש - גישה שמרנית)
        if balance_190 > 0:
            balance_190 *= (1 + r_monthly_190)
            balance_190 *= (1 - f_monthly_190)
        if balance_25 > 0:
            balance_25 *= (1 + r_monthly_25)
            balance_25 *= (1 - f_monthly_25)
            
        history.append({
            "גיל": current_age,
            "חודש": m,
            "הוצאה נומינלית": current_expense,
            "הכנסה נומינלית": current_income,
            "הכנסה מקצבה מזערית": pension_190_indexed,
            "צבירה תיקון 190": balance_190,
            "צבירה מסלול ריאלי": balance_25,
            "מס ששולם 190": tax_paid_month_190,
            "מס ששולם 25": tax_paid_month_25,
            "inflation_factor": inflation_factor
        })
        
    df_full = pd.DataFrame(history)
    df_check = df_full[df_full["גיל"] <= check_age]
    
    # בייסליין להשוואה (הון מסלול ריאלי התחלתי)
    baseline_capital = float(real_tax_25.get("net_for_real_pathway", 3340000) or 1)
    df_97 = df_full[df_full["גיל"] >= 97.0]
    row_97 = df_97.iloc[0] if not df_97.empty else df_full.iloc[-1]
    
    ratio_190_97 = float(row_97["צבירה תיקון 190"]) / max(1.0, baseline_capital)
    ratio_25_97 = float(row_97["צבירה מסלול ריאלי"]) / max(1.0, baseline_capital)
    
    return {
        "df": df_check,
        "df_full": df_full,
        "ratio_190_97": ratio_190_97,
        "ratio_25_97": ratio_25_97
    }
