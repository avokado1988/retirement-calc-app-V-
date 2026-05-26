import streamlit as st

# ==============================================================================
# 📊 1. פונקציות פירמוט והצגה בסיסיות
# ==============================================================================

def format_shekel(val):
    """מפרמט מספר לשקלים עם פסיקים: ₪1,000,000"""
    try:
        return f"₪{int(val):,}"
    except:
        return f"₪{val}"

def format_percent(val_decimal):
    """מפרמט שבר עשרוני לאחוז: 2.3%"""
    try:
        return f"{float(val_decimal) * 100:.1f}%"
    except:
        return val_decimal

def show_net_summary(title, amount):
    """מציג את קוביית הסיכום הירוקה האחידה בכל המסלולים"""
    st.success(f"💰 **{title}:** {format_shekel(amount)}")


# ==============================================================================
# 🎨 2. לוגיקת עיצוב מותנה (Conditional Styling) ורמזורים - תואם חוקי קצה
# ==============================================================================

def get_withdrawal_style(rate):
    """
    לוגיקת קצב/שיעור משיכה:
    מתחת ל-3%: ירוק בהיר | בין 3% ל-4%: כתום בהיר | מעל 4%: אדום בהיר
    """
    try:
        r = float(rate)
        if r < 3.0:
            color = "#99FF99"  # ירוק בהיר
        elif r <= 4.0:
            color = "#FFCC99"  # כתום בהיר
        else:
            color = "#FF9999"  # אדום בהיר
        return f"background-color: {color}; font-weight: bold; color: #1f2937;"
    except:
        return ""

def get_400_rule_style(multiplier_str):
    """
    לוגיקת חוק ה-400:
    קטן מ-1: אדום בהיר | בין 1 ל-1.3: כתום בהיר | מעל 1.3: ירוק בהיר
    """
    if str(multiplier_str) == "∞":
        return "background-color: #99FF99; font-weight: bold; color: #1f2937;"
        
    try:
        val = float(multiplier_str)
        if val < 1.0:
            color = "#FF9999"  # אדום בהיר
        elif val <= 1.3:
            color = "#FFCC99"  # כתום בהיר
        else:
            color = "#99FF99"  # ירוק בהיר
        return f"background-color: {color}; font-weight: bold; color: #1f2937;"
    except:
        return ""

def get_emergency_style(years_str):
    """
    לוגיקת קרן חירום (שנות מחיה):
    מתחת ל-2 שנים: אדום בהיר | בין 2 ל-3.5 שנים: כתום בהיר | מעל 3.5 שנים: ירוק בהיר
    """
    if str(years_str) == "∞":
        return "background-color: #99FF99; font-weight: bold; color: #1f2937;"
        
    try:
        val = float(years_str)
        if val < 2.0:
            color = "#FF9999"  # אדום בהיר
        elif val <= 3.5:
            color = "#FFCC99"  # כתום בהיר
        else:
            color = "#99FF99"  # ירוק בהיר
        return f"background-color: {color}; font-weight: bold; color: #1f2937;"
    except:
        return ""

def get_larger_portfolio_style(is_larger):
    """
    לוגיקת השוואת תיקים נזילים:
    צובעת בירוק בהיר את התיק ששוויו גדול יותר באותה נקודת זמן
    """
    if is_larger:
        return "background-color: #99FF99; font-weight: bold; color: #1f2937;"
    return ""

def get_resiliency_style(age_str):
    """
    לוגיקת חסינות אקטוארית:
    חסין (105+): ירוק בהיר | לא חסין: אדום בהיר
    """
    if "105+" in str(age_str) or "חסין" in str(age_str):
        color = "#99FF99"  # ירוק בהיר
    else:
        color = "#FF9999"  # אדום בהיר
    return f"background-color: {color}; font-weight: bold; color: #1f2937;"

def get_preservation_pct_style(ratio_pct):
    """
    לוגיקת שימור הון בגיל 97 (עומק ירושה):
    עד 75%: אדום בהיר | בין 75% ל-90%: כתום בהיר | מעל 90%: ירוק בהיר
    """
    try:
        val = float(ratio_pct)
        if val < 75.0:
            color = "#FF9999"  # אדום בהיר
        elif val <= 90.0:
            color = "#FFCC99"  # כתום בהיר
        else:
            color = "#99FF99"  # ירוק בהיר
        return f"background-color: {color}; font-weight: bold; border: 1px solid #c5c5c5; color: #1f2937;"
    except:
        return ""

def get_boolean_style(val_str):
    """עיצוב בסיסי לערכים בוליאניים"""
    if "כן" in str(val_str):
        return "color: #006600; font-weight: bold;"
    else:
        return "color: #990000; font-weight: bold;"


# ==============================================================================
# 🪄 3. מנוע עטיפת HTML לרינדור בטבלאות
# ==============================================================================

def wrap_html_style(val_str, style_str):
    """עוטף ערך ב-HTML מעוצב לרינדור אחיד ומקצועי בתוך רשת הטבלאות"""
    if not style_str:
        return str(val_str)
    # פאדינג ויישור יציב לימין בשביל התצוגה הויזואלית
    full_style = f"padding: 6px 10px; border-radius: 4px; display: block; text-align: right; {style_str}"
    return f"<div style='{full_style}'>{val_str}</div>"
