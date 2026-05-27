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

# ==============================================================================
# 🎨 מנוע עיצוב ברזל - חסימת שבירת שורות מוחלטת ( foolproof Nowrap Layout )
# ==============================================================================
st.markdown("""
<style>
    /* 1. נעילת השורה כולה כחץ אופקי אחד קשיח ללא יכולת קיפול */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important; /* חוסם לחלוטין נפילת עמודות למטה */
        align-items: center !important; /* מירכוז אנכי מושלם של כל הרכיבים */
        gap: 6px !important; /* מרחק קומפקטי קבוע בין חלקי השורה */
        margin-bottom: 12px !important; /* מרווח אסתטי נקי בין שורה לשורה */
        padding: 0 !important;
    }

    /* ניקוי שוליים מובנים של עמודות סטרימליט כדי למנוע פיזור */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
        padding: 0 !important;
        margin: 0 !important;
    }

    /* 2. ביטול התנהגות הפסקה המובנית של מרקדאון שמאלצת שבירת שורות */
    [data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p,
    .custom-sidebar-label p, 
    .custom-sidebar-badge p {
        display: inline !important; /* הופך את הטקסט לרצף אחד חלק */
        white-space: nowrap !important; /* חוסם שבירת שורות אופקית */
        word-break: keep-all !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* 3. עיצוב טקסט הכותרת הלבנה מימין */
    .custom-sidebar-label {
        font-size: 13.5px !important;
        font-weight: 500 !important;
        color: #ffffff !important;
        white-space: nowrap !important; /* הגנה כפולה מפני שבירה */
        text-align: right !important;
    }

    /* 4. קיבוע גודל חלון ההזנה הלבן/שחור באמצע השורה */
    [data-testid="stSidebar"] .stNumberInput {
        width: 75px !important; /* רוחב מיושר ומהודק */
        margin: 0 !important;
    }
    [data-testid="stSidebar"] .stNumberInput div[data-baseweb="input"] {
        height: 28px !important;
        border-radius: 4px !important;
    }
    [data-testid="stSidebar"] .stNumberInput input {
        padding: 2px 4px !important;
        font-size: 13px !important;
        text-align: center !important;
    }

    /* 5. עיצוב הערך הפיננסי הצבעוני משמאל */
    .custom-sidebar-badge {
        font-size: 13.5px !important;
        font-weight: 700 !important;
        white-space: nowrap !important; /* הגנה כפולה מפני שבירה */
        direction: rtl !important;
        text-align: right !important;
    }
</style>
""", unsafe_allow_html=True)


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

# פונקציות הסטייל האקטואריות לטבלאות
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

def _get_dynamic_color_by_label(label):
    lbl = label.lower()
    if "חירום" in lbl: return "#fb923c" 
    if any(x in lbl for x in ["הוצאה", "הוצאות", "מס", "עלות", "אינפלציה", "עזרה", "ניהול", "גירעון"]): return "#f87171" 
    if any(x in lbl for x in ["הכנסה", "הכנסות", "קצבה", "קצבת", "חיסכון", "חסכונות", "תשואה", "מכירה", "עליה ערך"]): return "#4ade80" 
    return "#38bdf8" 

def _format_compact_value(val, unit):
    val = float(val)
    rtl_mark = "\u200f"
    
    if unit in ["₪", "שח", "ש\"ח"]:
        if val >= 1_000_000:
            # 🟢 שתי ספרות קבועות אחרי הנקודה תמיד (למשל: 1.62 מ׳ ₪, 10.00 מ׳ ₪)
            formatted = f"{val / 1_000_000:.2f}"
            return f"{rtl_mark}{formatted} מ׳ ₪"
        if val >= 1_000:
            return f"{rtl_mark}{val / 1_000:.0f} א׳ ₪"
        return f"{rtl_mark}{int(val):,} ₪"
        
    if unit == "שנים":
        return f"{rtl_mark}{val:.1f} שנים" if val % 1 != 0 else f"{rtl_mark}{int(val)} שנים"
        
    if unit == "%":
        return f"{rtl_mark}{val:.1f}%"
        
    return f"{rtl_mark}{val} {unit}" if unit else f"{rtl_mark}{val}"

# ==============================================================================
# 🧱 רכיבי הזנה - יחס עמודות פרופורציונלי ומאוזן למניעת שבירות
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

    temp_key = widget_key + "_v7_holder"
    text_color = _get_dynamic_color_by_label(label)

    # 🟢 תיקון יחס עמודות פרופורציונלי: הכותרת מקבלת את רוב המקום כדי למנוע שבירה אופקית!
    col1, col2, col3 = st.columns([5.4, 2.0, 2.6])
    with col1:
        st.markdown(f"<div class='custom-sidebar-label'>{label}</div>", unsafe_allow_html=True)
        
    with col2:
        res = st.number_input(
            label, min_value=min_to_use, max_value=max_to_use, 
            value=val_to_use, step=step_to_use, label_visibility="collapsed", key=temp_key
        )
    with col3:
        formatted_display = _format_compact_value(res, unit)
        st.markdown(f"<div class='custom-sidebar-badge' style='color: {text_color};'>{formatted_display}</div>", unsafe_allow_html=True)
    
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

    temp_key = widget_key + "_v7_holder"
    text_color = _get_dynamic_color_by_label(label)
    
    # 🟢 תיקון יחס עמודות פרופורציונלי
    col1, col2, col3 = st.columns([5.4, 2.0, 2.6])
    with col1:
        st.markdown(f"<div class='custom-sidebar-label'>{label}</div>", unsafe_allow_html=True)

    with col2:
        raw_input = st.number_input(
            label, min_value=min_to_use, max_value=max_to_use, 
            value=val_to_use, step=step_to_use, label_visibility="collapsed", key=temp_key
        )
    with col3:
        formatted_display = _format_compact_value(raw_input, display_unit)
        st.markdown(f"<div class='custom-sidebar-badge' style='color: {text_color};'>{formatted_display}</div>", unsafe_allow_html=True)
        
    res = float(raw_input) / 100.0 if is_percentage_fraction else raw_input
    st.query_params[widget_key] = str(res)
    return res
