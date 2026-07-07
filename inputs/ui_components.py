import streamlit as st

# ==============================================================================
# ⚙️ קבועים וערכי ברירת מחדל מרוכזים (System Defaults)
# ==============================================================================
DEFAULTS = {
    "start_age": 65.0,
    "retirement_age": 65.0,
    "check_age": 95.0,
    "expected_inflation": 0.023,
    "current_expenses": 11000,
    "caregiver_cost": 2500,
    "one_time_expense": 80000,
    "one_time_frequency": 8,
    "age_75_85_increase": 0.0,
    "age_85_plus_increase": 0.0,
    "work_income": 0,
    "national_insurance": 2500,
    "desired_pension": 5306,
    "securing_years": 20,
    "base_coefficient": 200.0,
    "annual_return": 0.07,
    "management_fee": 0.006,
    "management_fee_190": 0.005,
    "net_sale": 9200000,
    "existing_savings": 440000,
    "new_apartment_cost": 5500000,
    "kids_help": 1000000,
    "kids_help_growth": 0.05,
    "emergency_fund": 50000,
    "property_appreciation": 0.03,
    "rental_property_value": 10800000,
    "rental_property_appreciation": 0.023,
    "rental_income_monthly": 25000,
    "rental_income_growth_rate": 0.03,
    "rent_paid_monthly": 12500,
    "rent_paid_growth_rate": 0.035,
    "rental_tax_rate": 0.1,
    "maintenance_early_pct": 0.05,
    "maintenance_late_pct": 0.1,
    "rm_annual_rate": 0.06,
    "rm_savings_floor": 100000,
    "loan_amount": 2000000,
    "loan_annual_rate": 0.0525,
    "visible_tracks": [1, 4, 5],
}

# ==============================================================================
# 📊 1. פונקציות פירמוט והצגה בסיסיות
# ==============================================================================

# טולטיפ משותף לשדות התשואה — תשואה משוקללת של תיק דליים
RETURN_HELP = (
    "התשואה היא תשואה משוקללת של תיק דליים (מזומן, אג\"ח ומניות), "
    "נומינלית ולפני דמי ניהול (כלומר לפני אינפלציה). "
    "תמהילים מקובלים: שמרני (25% מניות) כ-5%, מאוזן (50% מניות) כ-6%, "
    "צומח (75% מניות) כ-7%, מנייתי (90%+) כ-8%. "
    "ככל שהמשיכה החודשית מהתיק קטנה יותר, אפשר להרשות הטיה מנייתית גבוהה יותר."
)


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
        if r < 3.0: color = "#2ecc71"
        elif r <= 4.0: color = "#FFCC99"
        elif r <= 6.0: color = "#FFB347"
        else: color = "#FF9999"
        return f"color: {color}; font-weight: bold;"
    except: return ""

def get_400_rule_style(multiplier_str):
    if str(multiplier_str) == "∞": return "color: #2ecc71; font-weight: bold;"
    try:
        val = float(multiplier_str)
        if val < 1.0: color = "#FF9999"
        elif val <= 1.3: color = "#FFCC99"
        else: color = "#2ecc71"
        return f"color: {color}; font-weight: bold;"
    except: return ""

def get_emergency_style(years_str):
    if str(years_str) == "∞": return "color: #2ecc71; font-weight: bold;"
    try:
        val = float(str(years_str).replace(" שנים", "").replace(" שנה", ""))
        if val < 1.0: color = "#FF9999"
        elif val < 3.0: color = "#FFCC99"
        else: color = "#2ecc71"
        return f"color: {color}; font-weight: bold;"
    except: return ""

def get_larger_portfolio_style(is_larger):
    if is_larger: return "color: #2ecc71; font-weight: bold;"
    return ""

def get_resiliency_style(age_str):
    if "105+" in str(age_str) or "חסין" in str(age_str): color = "#2ecc71"
    else:
        try:
            age = float(str(age_str).replace("גיל ", ""))
            if age >= 100: color = "#FFCC99"
            elif age >= 90: color = "#FFB347"
            else: color = "#FF9999"
        except: color = "#FF9999"
    return f"color: {color}; font-weight: bold;"

def get_preservation_pct_style(ratio_pct):
    try:
        val = float(ratio_pct)
        if val < 75.0: color = "#FF9999"
        elif val < 100.0: color = "#FFCC99"
        else: color = "#2ecc71"
        return f"color: {color}; font-weight: bold;"
    except: return ""

def get_boolean_style(val_str):
    if "כן" in str(val_str): return "color: #4dbb4d; font-weight: bold;"
    else: return "color: #FF9999; font-weight: bold;"

def wrap_html_style(val_str, style_str):
    if not style_str: return str(val_str)
    return f"<span style='{style_str}'>{val_str}</span>"


# ==============================================================================
# 💎 3. רכיבי ממשק משופרים והיברידיים (UX קומפקטי, דינמי ומוגן מפני קריסות)
# ==============================================================================

COLOR_RED    = "#d62728"   # הוצאות
COLOR_GREEN  = "#2ca02c"   # הכנסות
COLOR_BLUE   = "#1565c0"   # פרמטרים אקטואריים / זמנים
COLOR_ORANGE = "#e67e22"   # קרן חירום

def compact_number_input(label, value, min_value=None, max_value=None, step=1, help_text=None, unit="₪", color=COLOR_GREEN):
    col1, col2 = st.columns([2.5, 1.5])
    with col1:
        v = st.number_input(label, value=value, min_value=min_value, max_value=max_value, step=step, help=help_text)

    with col2:
        if unit == "₪":
            formatted = format_shekel(v)
        elif unit == "%":
            formatted = f"{float(v):.1f}%"
        elif unit:
            formatted = f"{float(v):.1f} {unit}" if isinstance(v, float) else f"{v} {unit}"
        else:
            formatted = f"{float(v):.1f}" if isinstance(v, float) else f"{v}"

        st.markdown(f"<div id='num_{v}' style='padding-top: 28px; font-weight: bold; color: {color}; text-align: left; direction: ltr;'>{formatted}</div>", unsafe_allow_html=True)
    return v


def labeled_slider_with_value(key_label, min_value, max_value, value, step, format=None, help_text=None, unit=None):
    col1, col2 = st.columns([2.5, 1.5])
    with col1:
        val = st.slider(key_label, min_value=min_value, max_value=max_value, value=value, step=step, format=format, help=help_text)
    
    with col2:
        # פירמוט עשרוני מוגן מפני Floating Point Bug
        if unit == "₪": 
            formatted = format_shekel(val)
        elif unit == "%": 
            formatted = f"{float(val):.1f}%"
        elif unit: 
            formatted = f"{float(val):.1f} {unit}" if isinstance(val, float) else f"{val} {unit}"
        else: 
            formatted = f"{float(val):.1f}" if isinstance(val, float) else f"{val}"
        
        # ID דינמי (id='slider_{val}') מכריח את הדפדפן לרנדר את הטקסט מחדש ומונע קיפאון!
        st.markdown(f"<div id='slider_{val}' style='padding-top: 28px; font-weight: bold; color: #1f77b4; text-align: left; direction: ltr;'>{formatted}</div>", unsafe_allow_html=True)
    return val
