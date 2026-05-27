import streamlit as st

# מילון ערכי ברירת המחדל המדויקים והמיושרים של האפליקציה
DEFAULTS = {
    "start_age": 65.5,
    "retirement_age": 67.0,
    "check_age": 87.0,
    "desired_pension": 5000,
    "current_expenses": 11000,
    "expected_inflation": 0.023,
    "age_75_85_increase": 0.005,
    "age_85_plus_increase": 0.015,
    "one_time_expense": 80000,
    "one_time_frequency": 8,
    "caregiver_cost": 0,
    "national_insurance": 2500,
    "work_income": 0,
    "net_sale": 0,
    "existing_savings": 0,
    "new_apartment_cost": 5800000,
    "property_appreciation": 0.023,
    "kids_help": 0,
    "emergency_fund": 0,
    "annual_return": 0.05,
    "management_fee": 0.006
}

def format_shekel(amount):
    """פונקציית עזר גלובלית לעיצוב מטבע שקלי"""
    return f"{int(amount):,} ₪" if amount is not None else "0 ₪"

def show_net_summary(title, amount):
    """מציג תיבת סיכום מעוצבת להון נטו"""
    st.markdown(
        f"<div style='padding:10px; background-color:#f1f5f9; border-radius:5px; margin:10px 0; border-right:4px solid #1e3a8a;'>"
        f"<span style='font-weight:600; color:#1e3a8a;'>{title}:</span> "
        f"<span style='font-weight:700; color:#0f172a;'>{format_shekel(amount)}</span>"
        f"</div>", 
        unsafe_allow_html=True
    )

def wrap_html_style(text, style_str):
    """פונקציית עזר להזרקת סטייל לתוך HTML בטבלאות"""
    return f"<span style='{style_str}'>{text}</span>"

# ==============================================================================
# 🎨 פונקציות הסטייל והצבעים האקטואריים שדוחות ה-QA מחפשים (שחזור החוסר)
# ==============================================================================
def get_withdrawal_style(pct):
    val = float(pct)
    if val <= 3.5: return "color: #16a34a; font-weight: bold;" # ירוק בטוח
    if val <= 5.0: return "color: #d97706; font-weight: bold;" # צהוב גבולי
    return "color: #dc2626; font-weight: bold;" # אדום מסוכן

def get_400_rule_style(val_str):
    if val_str == "∞": return "color: #16a34a; font-weight: bold;"
    try:
        val = float(val_str)
        return "color: #16a34a; font-weight: bold;" if val >= 1.0 else "color: #dc2626; font-weight: bold;"
    except: return ""

def get_emergency_style(val_str):
    if val_str == "∞": return "color: #16a34a; font-weight: bold;"
    try:
        val = float(val_str)
        return "color: #16a34a; font-weight: bold;" if val >= 1.0 else "color: #dc2626; font-weight: bold;"
    except: return ""

def get_larger_portfolio_style(is_larger):
    return "color: #16a34a; font-weight: 700; background-color: #f0fdf4; padding: 2px 5px; border-radius: 3px;" if is_larger else "color: #4b5563;"

def get_resiliency_style(val_str):
    return "color: #16a34a; font-weight: bold;" if "حסין" in val_str or "105" in val_str else "color: #dc2626; font-weight: bold;"

def get_preservation_pct_style(pct):
    return "color: #16a34a; font-weight: bold;" if float(pct) >= 100.0 else "color: #dc2626; font-weight: bold;"

def get_boolean_style(val_str):
    return "color: #16a34a; font-weight: bold;" if "✅" in val_str else "color: #dc2626; font-weight: bold;"

# ==============================================================================
# 🧱 רכיבי הזנת נתונים (UI Components) - מבוססי הקלדה בלבד
# ==============================================================================
def compact_number_input(label, value, min_value=0, max_value=None, step=1, unit="₪"):
    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown(f"<div style='line-height: 2.5; font-weight: 500;'>{label}</div>", unsafe_allow_html=True)
    with col2:
        val_to_use = float(value) if isinstance(value, float) or isinstance(step, float) else int(value)
        min_to_use = float(min_value) if min_value is not None else None
        max_to_use = float(max_value) if max_value is not None else None
        
        res = st.number_input(
            label,
            min_value=min_to_use, 
            max_value=max_to_use, 
            value=val_to_use, 
            step=step,
            label_visibility="collapsed"
        )
        if unit:
            st.caption(f"יחידות: {unit}")
    return res

def labeled_slider_with_value(label, min_value, max_value, value, step=1.0, format=None, unit=None):
    """
    🔄 הוסב להזנת מספרים (הקלדה) תוך הצגת סימונים אסתטיים (%, שנים, ₪) באותה השורה!
    """
    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown(f"<div style='line-height: 2.5; font-weight: 500;'>{label}</div>", unsafe_allow_html=True)
    with col2:
        # טיפול חכם בשברי אחוזים (למשל: הפיכת 0.023 ל-2.3% לצורך הקלדה נוחה)
        is_percentage_fraction = format is not None and "%" in format and float(value) <= 1.0
        
        if is_percentage_fraction:
            val_to_use = float(value) * 100.0
            min_to_use = float(min_value) * 100.0
            max_to_use = float(max_value) * 100.0
            step_to_use = float(step) * 100.0 if float(step) <= 1.0 else float(step)
        else:
            val_to_use = float(value) if isinstance(step, float) or '.' in str(value) else int(value)
            min_to_use = float(min_value) if isinstance(min_value, float) else int(min_value)
            max_to_use = float(max_value) if isinstance(max_value, float) else int(max_value)
            step_to_use = step

        # ציור שדה הקלט וסימן היחידה יחד באותו הגובה
        sub_col1, sub_col2 = st.columns([3, 1])
        with sub_col1:
            raw_input = st.number_input(
                label,
                min_value=min_to_use,
                max_value=max_to_use,
                value=val_to_use,
                step=step_to_use,
                label_visibility="collapsed"
            )
        with sub_col2:
            display_unit = "%" if (format and "%" in format) or unit == "%" else (unit if unit else "")
            st.markdown(f"<div style='line-height: 2.5; font-weight: 600; color: #4b5563;'>{display_unit}</div>", unsafe_allow_html=True)
            
        res = float(raw_input) / 100.0 if is_percentage_fraction else raw_input
        
    return res
