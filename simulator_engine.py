import pandas as pd
import numpy as np

def run_simulation(user_inputs):
    """
    מנוע סימולציה פיננסי אקטוארי בסטנדרט Gold Standard.
    חישוב חודשי הכולל גילום מס (Gross-Up), ניהול בסיס מס מוצמד ושינויי אינפלציה דינמיים.
    """
    # --- 1. שליפת פרמטרים ונתוני בסיס ---
    timeline = user_inputs["timeline"]
    wealth = user_inputs["wealth"]
    expenses = user_inputs["expenses"]
    amendment_190 = user_inputs["amendment_190"]
    real_tax_25 = user_inputs["real_tax_25"]
    
    start_age = timeline["start_age"]
    check_age = timeline["check_age"]
    total_months = int((check_age - start_age) * 12)
    
    # פרמטרי תשואה חודשית נטו (לאחר הפחתת דמי ניהול - ריבית דריבית)
    r_190 = (1 + (amendment_190["annual_return_190"] - amendment_190["management_fee_190"])) ** (1/12) - 1
    r_25 = (1 + (real_tax_25["annual_return_25"] - real_tax_25["management_fee_25"])) ** (1/12) - 1
    
    # פרמטרי אינפלציה בסיסיים
    annual_inflation_base = expenses["expected_inflation"]
    
    # קביעת הון התחלתי ובסיס מס התחלתי
    balance_190 = amendment_190["net_for_190"]
    invested_capital_190 = balance_190  # בסיס מס נומינלי ל-190
    pension_received = amendment_190["desired_pension"]
    
    balance_25 = real_tax_25["net_for_real_pathway"]
    basis_25 = balance_25  # בסיס מס מוצמד התחלתי ל-25%
    
    history = []
    
    # --- 2. הלולאה החודשית המרכזית (The Monthly Loop) ---
    for m in range(total_months):
        current_age = start_age + (m / 12)
        
        # א. מדרגות השמרנות - עדכון קצב האינפלציה הדינמי לפי הגיל
        current_annual_inflation = annual_inflation_base
        if current_age >= 85.0:
            current_annual_inflation += 0.015
        elif current_age >= 75.0:
            current_annual_inflation += 0.005
            
        i_monthly = (1 + current_annual_inflation) ** (1/12) - 1
        
        # ב. עדכון מדד מצטבר פנימי לחודש הנוכחי (ביחס לחודש אפס)
        if m == 0:
            inflation_factor = 1.0
        else:
            inflation_factor = history[-1]["inflation_factor"] * (1 + i_monthly)
            
        # ג. חישוב הוצאה בסיסית ריאלית באותו חודש
        base_expense = expenses["current_expenses"]
        if current_age >= 85.0:
            base_expense += expenses["caregiver_cost"]
            
        # הוצאות מחזוריות
        frequency_months = expenses["one_time_frequency"] * 12
        if m > 0 and m % frequency_months == 0:
            base_expense += expenses["one_time_expense"]
            
        # קיזוז הכנסה זמנית מעבודה (רק מתחת לגיל פרישה)
        if current_age < timeline["retirement_age"]:
            base_expense = max(0, base_expense - expenses["work_income"])
            
        # הפיכה לנומינלי (הצמדה למדד)
        nominal_expense = base_expense * inflation_factor
        
        # ד. חישוב הכנסות צמודות (ביטוח לאומי)
        nominal_income = wealth["national_insurance"] * inflation_factor
        
        # ה. חישוב הסכום החסר למחיה (Net Needed)
        net_needed_base = max(0, nominal_expense - nominal_income)
        
        # ----------------------------------------------------
        # מסלול א': תיקון 190 (הקצבה שקנינו מקטינה את הנטו הדרוש מההון ההוני)
        # ----------------------------------------------------
        net_needed_190 = max(0, net_needed_base - (pension_received * inflation_factor))
        gross_withdrawn_190 = 0.0
        tax_paid_month_190 = 0.0
        
        if balance_190 > 0 and net_needed_190 > 0:
            # אם צריך למשוך יותר ממה שיש, נמשוך את כל הקופה
            current_net_target = min(net_needed_190, balance_190)
            
            # קביעת יחס רווח (Profit Ratio)
            profit_ratio_190 = max(0.0, (balance_190 - invested_capital_190) / balance_190) if balance_190 > 0 else 0.0
            
            # מנגנון גילום המס (Gross-Up Mechanism)
            gross_withdrawn_190 = current_net_target / (1 - (profit_ratio_190 * 0.15))
            
            # הגנה מפני משיכת יתר על גבול יתרת הקופה
            if gross_withdrawn_190 > balance_190:
                gross_withdrawn_190 = balance_190
                tax_paid_month_190 = gross_withdrawn_190 * profit_ratio_190 * 0.15
            else:
                tax_paid_month_190 = gross_withdrawn_190 - current_net_target
                
            # גריעת הברוטו מהקופה
            balance_190 -= gross_withdrawn_190
            # עדכון בסיס הקרן הנומינלית שנשארה (פרופורציונלית למשיכה)
            invested_capital_190 *= (1 - (gross_withdrawn_190 / (balance_190 + gross_withdrawn_190)))
            
        # החלת תשואה חודשית על היתרה
        if balance_190 > 0:
            balance_190 *= (1 + r_190)
            
        # ----------------------------------------------------
        # מסלול ב': מסלול ריאלי 25%
        # ----------------------------------------------------
        # הצמדת בסיס המס למדד בתחילת הצעד
        basis_25 *= (1 + i_monthly)
        
        gross_withdrawn_25 = 0.0
        tax_paid_month_25 = 0.0
        
        if balance_25 > 0 and net_needed_base > 0:
            current_net_target_25 = min(net_needed_base, balance_25)
            
            # חישוב רווח ריאלי חיובי בקופה ברגע זה
            real_profit_total = max(0.0, balance_25 - basis_25)
            real_profit_ratio = real_profit_total / balance_25 if balance_25 > 0 else 0.0
            
            # מנגנון גילום המס (Gross-Up Mechanism) ל-25% ריאלי
            gross_withdrawn_25 = current_net_target_25 / (1 - (real_profit_ratio * 0.25))
            
            if gross_withdrawn_25 > balance_25:
                gross_withdrawn_25 = balance_25
                tax_paid_month_25 = max(0.0, balance_25 - basis_25) * 0.25
            else:
                tax_paid_month_25 = gross_withdrawn_25 - current_net_target_25
                
            # גריעת הברוטו מהקופה
            balance_25 -= gross_withdrawn_25
            # עדכון בסיס המס המוצמד (הפחתת חלק הקרן שנמשך)
            # חלק הקרן שנמשך הוא סך המשיכה פחות הרווח הריאלי היחסי שבתוכה
            principal_portion = gross_withdrawn_25 * (1 - real_profit_ratio)
            basis_25 = max(0.0, basis_25 - principal_portion)
            
        # החלת תשואה חודשית על היתרה
        if balance_25 > 0:
            balance_25 *= (1 + r_25)

        # תיעוד המצב לחודש הנוכחי
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

    # --- 3. סיכומי נטו סופיים בגיל היעד (פדיון הוני מוחלט) ---
    df_history = pd.DataFrame(history)
    
    # חישוב מס סופי על היתרה שנותרה בקופה אם נפדה הכל בגיל היעד
    # תיקון 190
    final_profit_ratio_190 = max(0.0, (balance_190 - invested_capital_190) / balance_190) if balance_190 > 0 else 0.0
    final_tax_190 = balance_190 * final_profit_ratio_190 * 0.15
    net_final_190 = balance_190 - final_tax_190
    
    # מסלול 25%
    final_real_profit = max(0.0, balance_25 - basis_25)
    final_tax_25 = final_real_profit * 0.25
    net_final_25 = balance_25 - final_tax_25
    
    total_tax_paid_inside_190 = df_history["מס ששולם 190"].sum()
    total_tax_paid_inside_25 = df_history["מס ששולם 25"].sum()

    return {
        "df": df_history,
        "end_balance_190_gross": int(balance_190),
        "end_balance_190_net": int(net_final_190),
        "total_tax_paid_190": int(total_tax_paid_inside_190 + final_tax_190),
        
        "end_balance_25_gross": int(balance_25),
        "end_balance_25_net": int(net_final_25),
        "total_tax_paid_25": int(total_tax_paid_inside_25 + final_tax_25)
    }
