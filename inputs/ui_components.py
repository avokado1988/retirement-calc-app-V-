import streamlit as st

# מילון ערכי ברירת המחדל המדויקים של האפליקציה
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
    return f"{int(amount):,} ₪" if amount is not None else "0 ₪"

def show_net_summary(title, amount):
    st.markdown(
        f"<div style='padding:10px; background-color:#f1f5f9; border-radius:5px; margin:10px 0; border-right:4px solid #1e3a8a;'>"
        f"<span style='font-weight:600; color:#1e3a8a;'>{title}:</span> "
        f"<span style='font-weight:700; color:#0f172a;'>{format_shekel(amount)}</span>"
        f"</div>", 
        unsafe_allow_html=True
    )

def wrap_html_style(text, style_str):
    return f"<span style='{style_str}'>{text}</span>"

# פונקציות הסטייל האקטואריות
def get_withdrawal_style(pct):
    val = float(pct)
    if val <= 3.5: return "color: #16a34a; font-weight: bold;"
    if val <= 5.0: return "color: #d97706; font-weight: bold;"
    return "color: #dc2626; font-weight: bold;"

def get_400_rule_style(val_str):
    if val_str == "∞": return "color: #16a34a; font-weight: bold;"
    try: return "color: #16a34a; font-weight: bold;" if float(val_str) >= 1.0 else "color: #dc2626; font-weight: bold;"
    except: return ""

def get_emergency_style(val_str):
    if val_str == "∞": return "color: #16a34a; font-weight: bold;"
    try: return "color: #16a34a; font-weight: bold;" if float(val_str) >= 1.0 else "color: #dc2626; font-weight: bold;"
    except: return ""

def get_larger_portfolio_style(is_larger):
    return "color: #16a34a; font-weight: 700; background-color: #f0fdf4; padding: 2px 5px; border-radius: 3px;" if is_larger else "color: #4b5563;"

def get_resiliency_style(val_str):
    return "color: #16a34a; font-weight: bold;" if "חסין" in val_str or "105" in val_str else "color: #dc2626; font-weight: bold;"

def get_preservation_pct_style(pct):
    return "color: #16a34a; font-weight: bold;" if float(pct) >= 100.0 else "color: #dc2626; font-weight: bold;"

def get_boolean_style(val_str):
    return "color: #16a34a; font-weight: bold;" if "✅" in val_str else "color: #dc2626; font-weight: bold;"

# ==============================================================================
# 🧱 רכיבי הזנה מעוצבים - שילוב הערכים והיחידות ישירות בטקסט הימני
# ==============================================================================
def compact_number_input(label, value, min_value=0, max_value=None, step=1, unit="₪"):
    widget_key = f"saved_v3_{label.replace(' ', '_')}"
    
    if widget_key in st.query_params:
        try:
            stored_val = st.query_params[widget_key]
            value = float(stored_val) if isinstance(step, float) or isinstance(value, float) else int(stored_val)
        except: pass

    if isinstance(step, float) or isinstance(value, float):
        val_to_use = float(value)
        min_to_use = float(min_value) if min_value is not None else None
        max_to_use = float(max_value) if max_value is not None else None
        step_to_use = float(step)
    else:
        val_to_use = int(value)
        min_to_use = int(min_value) if min_value is not None else None
        max_to_use = int(max_value) if max_value is not None else None
        step_to_use = int(step)

    # 🟢 שלב 1: מייצרים את הקלט קודם (בצורה נסתרת זמנית) כדי לדעת מה הערך הנוכחי בזמן אמת
    # אנחנו מייצרים קוד ייחודי זמני כדי למנוע כפל רכיבים
    temp_key = widget_key + "_v4_holder"
    current_val = st.session_state.get(temp_key, val_to_use)

    col1, col2 = st.columns([3.2, 1.8])
    with col1:
        # 🟢 שלב 2: הדפסת הטקסט המשולב בלבן בוהק: "כותרת: 1,000 שח"
        if unit == "₪":
            formatted_display = f"{int(current_val):,} {unit}"
        elif unit == "שנים":
            formatted_display = f"{current_val:.1f} {unit}" if isinstance(step, float) else f"{int(current_val)} {unit}"
        else:
            formatted_display = f"{current_val} {unit}" if unit else f"{current_val}"
            
        st.markdown(f"<div style='line-height: 2.6; font-weight: 500; color: #ffffff;'>{label}: <span style='color: #38bdf8; font-weight: 700;'>{formatted_display}</span></div>", unsafe_allow_html=True)
        
    with col2:
        res = st.number_input(
            label, min_value=min_to_use, max_value=max_to_use, 
            value=val_to_use, step=step_to_use, label_visibility="collapsed", key=temp_key
        )
    
    st.query_params[widget_key] = str(res)
    return res

def labeled_slider_with_value(label, min_value, max_value, value, step=1.0, format=None, unit=None):
    widget_key = f"saved_v3_{label.replace(' ', '_')}"
    is_percentage_fraction = format is not None and "%" in format and float(value) <= 1.0
    
    if widget_key in st.query_params:
        try:
            stored_val = float(st.query_params[widget_key])
            value = stored_val if is_percentage_fraction else (float(stored_val) if isinstance(step, float) else int(stored_val))
        except: pass

    if is_percentage_fraction:
        val_to_use = float(value) * 100.0 if float(value) <= 1.0 else float(value)
        min_to_use = float(min_value) * 100.0
        max_to_use = float(max_value) * 100.0
        step_to_use = float(step) * 100.0 if float(step) <= 1.0 else float(step)
        display_unit = "%"
    else:
        if isinstance(step, float) or '.' in str(value) or isinstance(value, float):
            val_to_use = float(value)
            min_to_use = float(min_value)
            max_to_use = float(max_value)
            step_to_use = float(step)
        else:
            val_to_use = int(value)
            min_to_use = int(min_value)
            max_to_use = int(max_value)
            step_to_use = int(step)
        display_unit = unit if unit else ""

    temp_key = widget_key + "_v4_holder"
    current_val = st.session_state.get(temp_key, val_to_use)

    col1, col2 = st.columns([3.2, 1.8])
    with col1:
        # 🟢 שלב 2: הדפסת הטקסט המשולב לאחוזים או יחידות אחרות: "תשואה: 4.5%"
        if display_unit == "%":
            formatted_display = f"{current_val:.1f}%"
        elif display_unit == "שנים":
            formatted_display = f"{current_val:.1f} שנים" if isinstance(step, float) else f"{int(current_val)} שנים"
        elif display_unit == "₪":
            formatted_display = f"{int(current_val):,} ₪"
        else:
            formatted_display = f"{current_val} {display_unit}" if display_unit else f"{current_val}"
            
        st.markdown(f"<div style='line-height: 2.6; font-weight: 500; color: #ffffff;'>{label}: <span style='color: #38bdf8; font-weight: 700;'>{formatted_display}</span></div>", unsafe_allow_html=True)

    with col2:
        raw_input = st.number_input(
            label, min_value=min_to_use, max_value=max_to_use, 
            value=val_to_use, step=step_to_use, label_visibility="collapsed", key=temp_key
        )
        
    res = float(raw_input) / 100.0 if is_percentage_fraction else raw_input
    st.query_params[widget_key] = str(res)
    return res
