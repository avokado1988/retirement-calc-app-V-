import streamlit as st

# ==============================================================================
# ⚙️ קבועים וערכי ברירת מחדל מרוכזים (System Defaults)
# ==============================================================================
DEFAULTS = {
    "start_age": 65.5,
    "retirement_age": 67.0,
    "check_age": 87.0,
    "expected_inflation": 0.023,
    "current_expenses": 11000,
    "caregiver_cost": 3500,
    "one_time_expense": 80000,
    "one_time_frequency": 8,
    "work_income": 0,
    "desired_pension": 5000,
    "national_insurance": 2500,
    "annual_return": 0.05,
    "management_fee": 0.006,
    "net_sale": 10000000,
    "existing_savings": 440000,
    "new_apartment_cost": 5800000,
    "kids_help": 1000000,
    "emergency_fund": 300000,
    "property_appreciation": 0.023,
    "age_75_85_increase": 0.005,
    "age_85_plus_increase": 0.015
}

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
# 🎨 2. לוגיקת עיצוב מותנה (Conditional Styling) ורמזורים - טבלאות
# ==============================================================================

def get_withdrawal_style(rate):
    try:
        r = float(rate)
        if r < 3.0: color = "#99FF99"
        elif r <= 4.0: color = "#FFCC99"
        else: color = "#FF9999"
        return f"background-color: {color}; font-weight: bold; color: #1f2937;"
    except: return ""

def get_400_rule_style(multiplier_str):
    if str(multiplier_str) == "∞": return "background-color: #99FF99; font-weight: bold; color: #1f2937;"
    try:
        val = float(multiplier_str)
        if val < 1.0: color = "#FF9999"
        elif val <= 1.3: color = "#FFCC99"
        else: color = "#99FF99"
        return f"background-color: {color}; font-weight: bold; color: #1f2937;"
    except: return ""

def get_emergency_style(years_str):
    if str(years_str) == "∞": return "background-color: #99FF99; font-weight: bold; color: #1f2937;"
    try:
        val = float(years_str)
        if val < 2.0: color = "#FF9999"
        elif val <= 3.5: color = "#FFCC99"
        else: color = "#99FF99"
        return f"background-color: {color}; font-weight: bold; color: #1f2937;"
    except: return ""

def get_larger_portfolio_style(is_larger):
    if is_larger: return "background-color: #99FF99; font-weight: bold; color: #1f2937;"
    return ""

def get_resiliency_style(age_str):
    if "105+" in str(age_str) or "חסין" in str(age_str): color = "#99FF99"
    else: color = "#FF9999"
    return f"background-color: {color}; font-weight: bold; color: #1f2937;"

def get_preservation_pct_style(ratio_pct):
    try:
        val = float(ratio_pct)
        if val < 75.0: color = "#FF9999"
        elif val <= 90.0: color = "#FFCC99"
        else: color = "#99FF99"
        return f"background-color: {color}; font-weight: bold; border: 1px solid #c5c5c5; color: #1f2937;"
    except: return ""

def get_boolean_style(val_str):
    if "כן" in str(val_str): return "color: #006600; font-weight: bold;"
    else: return "color: #990000; font-weight: bold;"

def wrap_html_style(val_str, style_str):
    if not style_str: return str(val_str)
    full_style = f"padding: 6px 10px; border-radius: 4px; display: block; text-align: right; {style_str}"
    return f"<div style='{full_style}'>{val_str}</div>"


# ==============================================================================
# 💎 3. רכיבי ממשק משופרים והיברידיים (UX קומפקטי ומיושר בזמן אמת)
# ==============================================================================

def compact_number_input(label, value, min_value=None, max_value=None, step=1, help_text=None, unit="₪"):
    col1, col2 = st.columns([2.5, 1.5])
    with col1:
        v = st.number_input(label, value=value, min_value=min_value, max_value=max_value, step=step, help=help_text)
    
    # 🟢 חומת אש: המרה בטוחה למספר כדי למנוע קריסות (TypeError) ממחרוזות שנתקעו ב-URL
    try:
        v = float(v) if '.' in str(step) else int(v)
    except:
        pass

    with col2:
        if unit == "₪": formatted = format_shekel(v)
        elif unit == "%": formatted = f"{v:.1f}%"
        else: formatted = f"{v} {unit}" if unit else f"{v}"
        st.markdown(f"<div style='padding-top: 28px; font-weight: bold; color: #2ca02c; text-align: left; direction: ltr;'>{formatted}</div>", unsafe_allow_html=True)
    return v

def labeled_slider_with_value(key_label, min_value, max_value, value, step, format=None, help_text=None, unit=None):
    col1, col2 = st.columns([2.5, 1.5])
    with col1:
        val = st.slider(key_label, min_value=min_value, max_value=max_value, value=value, step=step, format=format, help=help_text)
    
    # 🟢 חומת אש: המרה ודאית למספר עשרוני למקרה שהדפדפן דחף לנו טקסט
    try:
        val = float(val)
    except:
        pass

    with col2:
        if unit == "₪": formatted = format_shekel(val)
        elif unit == "%": formatted = f"{val:.1f}%"
        elif unit: formatted = f"{val} {unit}"
        else: formatted = f"{val:.1f}" if isinstance(val, float) else f"{val}"
        st.markdown(f"<div style='padding-top: 28px; font-weight: bold; color: #1f77b4; text-align: left; direction: ltr;'>{formatted}</div>", unsafe_allow_html=True)
    return val
