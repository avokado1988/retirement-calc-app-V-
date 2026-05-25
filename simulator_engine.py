import pandas as pd
import numpy as np

def calculate_inflation_factor(months, annual_inflation):
    """מחזיר את מקדם האינפלציה החודשי המצטבר"""
    monthly_inflation = (1 + annual_inflation) ** (1 / 12) - 1
    return (1 + monthly_inflation) ** months

def get_monthly_expense(current_age, months_passed, expenses_data, timeline_data):
    """
    מחשב את ההוצאה הריאלית לחודש ספציפי, כולל:
    1. גידול לפי גיל (75-85, 85 ומעלה)
    2. עלות מטפלת סיעודית מגיל 85
    3. הוצאות חד-פעמיות מחזוריות (למשל כל 8 שנים)
    4. הפחתת הכנסה זמנית מעבודה (כל עוד לא הגיע לגיל פרישה)
    """
    # הוצאת בסיס
    base_expense = expenses_data["current_expenses"]
    
    # 1. גידול דינמי בהוצאות לפי גיל (מעל גיל פרישה)
    if current_age > timeline_data["retirement_age"]:
        # חישוב השנים שעברו מגיל הפרישה
        years_since_retire = max(0, current_age - timeline_data["retirement_age"])
        
        # אפקט גיל 75 עד 85
        years_in_phase1 = min(10.0, max(0.0, current_age - 75.0)) if current_age > 75 else 0.0
        # אפקט גיל 85 ומעלה
        years_in_phase2 = max(0.0, current_age - 85.0) if current_age > 85 else 0.0
        
        # החלת אחוזי הגידול מהאינפוטים
        base_expense *= (1 + expenses_data["age_75_85_increase"]) ** years_in_phase1
        base_expense *= (1 + expenses_data["age_85_plus_increase"]) ** years_in_phase2

    # 2. תוספת עלות מטפלת סיעודית מגיל 85
    if current_age >= 85.0:
        base_expense += expenses_data["caregiver_cost"]
        
    # 3. הוספת הוצאה חד-פעמית מחזורית (נבדק ברמת חודשים)
    frequency_months = expenses_data["one_time_frequency"] * 12
    if months_passed > 0 and months_passed % frequency_months == 0:
        base_expense += (expenses_data["one_time_expense"] / 12) # פריסה חודשית או הוספה ישירה (באקסל זה בד"כ שנתי, כאן הוספנו לחודש הספציפי)

    # 4. קיזום הכנסה מעבודה (רק אם הוא מתחת לגיל פרישה ובחר לעבוד)
    if current_age < timeline_data["retirement_age"]:
        base_expense = max(0, base_expense - expenses_data["work_income"])
        
    return base_expense

def run_simulation(user_inputs):
    """
    הפונקציה המרכזית שמריצה את הסימולציות חודש אחר חודש
    ומחזירה נתונים מסוכמים וטבלאות מלאות
    """
    # שליפת נתוני הזמנים של הלולאה
    start_age = user_inputs["timeline"]["start_age"]
    check_age = user_inputs["timeline"]["check_age"]
    
    total_months = int((check_age - start_age) * 12)
    
    # --- כאן נבנה בשלב הבא את הלולאות של המסלולים ---
    
    # כרגע נחזיר ערך זמני לבדיקה שהמנוע מחובר
    return {"status": "Engine is ready", "total_months_simulated": total_months}
