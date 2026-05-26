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
# 🎨 2. לוגיקת עיצוב מותנה (Conditional Styling) ורמזורים - תואם Sheets
# ==============================================================================

def get_withdrawal_style(rate):
    """לוגיקת חוק ה-4%: ירוק עד 4%, אדום מעל"""
    try:
        r = float(rate)
        color = "#99FF99" if r <= 4.0 else "#FF9999"
        return f"background-color: {color}; font-weight: bold;"
    except:
        return ""

def get_resiliency_style(age_str):
    """לוגיקת חסינות: ✅ מעל גיל 105, ❌ מתחת"""
    if "105+" in str(age_str):
        return "background-color: #99FF99; font-weight: bold; color: #006600;" # ירוק כהה
    else:
        return "background-color: #FF9999; font-weight: bold; color: #990000;" # אדום כהה

def get_preservation_pct_style(ratio_pct):
    """לוגיקת שימור הון בגיל 97:
    >= 90%: ירוק | 75%-90%: כתום בהיר | < 75%: אדום בהיר
    """
    try:
        val = float(ratio_pct)
        if val >= 90.0:
            color = "#99FF99" # ירוק
        elif val >= 75.0:
            color = "#FFCC99" # כתום בהיר
        else:
            color = "#FF9999" # אדום בהיר
        return f"background-color: {color}; font-weight: bold; border: 1px solid #c5c5c5;"
    except:
        return ""

def get_400_rule_style(multiplier_str):
    """לוגיקת חוק ה-400: ירוק מעל 1.0, אדום מתחת"""
    try:
        val = float(multiplier_str)
        color = "#99FF99" if val >= 1.0 else "#FF9999"
        return f"background-color: {color}; font-weight: bold;"
    except:
        return ""

def get_boolean_style(val_str):
    """עיצוב ירוק ל'כן' ואדום ל'לא'"""
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
