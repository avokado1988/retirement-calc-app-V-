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
# 🎨 מנוע עיצוב מתקדם - קביעת מרווחים אופטימליים לתפריט הצד
# ==============================================================================
st.markdown("""
<style>
    /* 1. הגדרת השורה כולה כמכלול אופקי ממורכז בכיווניות עברית מלאה */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important; /* חוסם לחלוטינ נפילת שורות */
        align-items: center !important; 
        direction: rtl !important; 
        margin-bottom: 14px !important; 
        padding: 0 !important;
        width: 100% !important;
    }

    /* ניקוי שוליים ופדינגים של עמודות סטרימליט */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
        padding: 0 !important;
        margin: 0 !important;
    }

    /* עמודה 1: הכותרת הלבנה מימין */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(1) {
        flex: 1 1 auto !important;
        min-width: 0 !important;
        text-align: right !important;
        margin-left: 10px !important;
    }

    /* עמודה 2: חלון ההזנה הלבן באמצע */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) {
        flex: 0 0 80px !important;
        width: 80px !important;
        min-width: 80px !important;
    }

    /* עמודה 3: הערך הפיננסי הצבעוני משמאל */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(3) {
        flex: 0 0 auto !important;
        min-width: max-content !important;
        text-align: right !important;
        margin-right: 8px !important;
    }

    /* ביטול שבירת פסקאות מרקדאון */
    [data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p,
    .custom-sidebar-label p, 
    .custom-sidebar-badge p {
        display: inline !important;
        white-space: nowrap !important;
        word-break: keep-all !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    .custom-sidebar-label {
        font-size: 14px !important;
        font-weight: 500 !important;
        color: #ffffff !important;
        white-space: nowrap !important;
    }

    .custom-sidebar-badge {
        font-size: 14px !important;
        font-weight: 700 !important;
        white-space: nowrap !important;
        direction: rtl !important;
    }

    .custom-sidebar-badge,
    .custom-sidebar-badge * {
        color: inherit !important;
    }

    /* קיבוע חלון ההזנה הלבן */
    [data-testid="stSidebar"] .stNumberInput {
        width: 80px !important;
        margin: 0 !important;
    }
    [data-testid="stSidebar"] .stNumberInput div[data-baseweb="input"] {
        height: 30px !important;
        border-radius: 4px !important;
    }
    [data-testid="stSidebar"] .stNumberInput input {
        padding: 2px 4px !important;
        font-size: 13.5px !important;
        text-align: center !important;
    }
</style>
""", unsafe_allow_html=True)


def format_shekel(amount):
    return f"{int(amount):,} ₪" if amount is not None else "0 ₪"

def show_net_summary(title, amount):
    st.markdown(
        f"<div style='padding:12px; background-color:#1e293b; border:1px solid #334155; border-radius:6px; margin:14px 0; border-right:5px solid #4ade80; direction: rtl; text-align: right;'> "
        f"<span style='font-weight:600; color:#ffffff; font-size:15px;'>{title}:</span> "
        f"<span style='font-weight:700; color:#4ade80; font-size:16px; margin-right:6px;'>{format_shekel(amount)}</span>"
        f"</div>", 
        unsafe_allow_html=True
    )

def wrap_html_style(text, style_str):
    return f"<span style='{style_str}'>{text}</span>"

# פונקציות הסטייל האקטואריות לטבלאות
def get_withdrawal_style(pct):
    val = float(pct)
    if val <= 3.5: return "color: #4ade80; font-weight: bold;"
    if val <= 5.0: return "color: #fb923c; font-weight: bold;"
    return "color: #f87171; font-weight: bold;"

def get_400_rule_style(val_str):
    if val_str == "∞": return "color: #4ade80; font-weight: bold;"
    try: return "color: #4ade80; font-weight: bold;" if float(val_str) >= 1.0 else "color: #f87171; font-weight: bold;"
    except: return ""

def get_emergency_style(val_str):
    if val_str == "∞": return "color: #4ade80; font-weight: bold;"
    try: return "color: #4ade80; font-weight: bold;" if float(val_str) >= 1.0 else "color: #f87171; font-weight: bold;"
    except: return ""

# 🎯 תיקון המסגרת המכוערת: הסרנו את הקופסה, הרקע והגבולות. מעכשיו זה טקסט נקי ויפה!
def get_larger_portfolio_style(is_larger):
    if is_larger:
        return "color: #4ade80; font-weight: 700;"
    return "color: #ffffff; font-weight: 500;"

def get_resiliency_style(val_str):
    return "color: #4ade80; font-weight: bold;" if "חסין" in val_str or "105" in val_str else "color: #f87171; font-weight: bold;"

def get_preservation_pct_style(pct):
    return "color: #4ade80; font-weight: bold;" if float(pct) >= 100.0 else "color: #f87171; font-weight: bold;"

def get_boolean_style(val_str):
    return "color: #4ade80; font-weight: bold;" if "✅" in val_str else "color: #f87171; font-weight: bold;"

def _get_dynamic_color_by_label(label):
    lbl = label.lower()
    if "חירום" in lbl: return "#fb923c" 
    if any(x in lbl for x in ["הוצאה", "הוצאות", "מס", "עלות", "אינפלציה", "עזרה", "ניהול", "גירעון"]): return "#f87171" 
    if any(x in lbl for x in ["הכנסה", "הכנסות", "קצבה", "קצבת", "חיסכון", "חסכונות", "תשואה", "מכירה", "עליה ערך", "נזיל", "תיק", "יישאר"]): return "#4ade80" 
    return "#ffffff" 

# 🎯 תיקון הקיצורים באלפים: מעכשיו סכומים מתחת ל-100 אלף מוצגים מלאים (כמו 2,500 ₪) ולא מקוצרים!
def _format_compact_value(val, unit):
    val = float(val)
    rtl_mark = "\u200f"
    
    if unit in ["₪", "שח", "ש\"ח"]:
        if val >= 1_000_000 or val <= -1_000_000:
            formatted = f"{val / 1_000_000:.2f}"
            return f"{rtl_mark}{formatted} מ׳ ₪"
        if val >= 100_000 or val <= -100_000:
            return f"{rtl_mark}{val / 1_000:.0f} א׳ ₪"
        return f"{rtl_mark}{int(val):,} ₪" # סכומים רגילים באלפים מוצגים מלא
        
    if unit == "שנים":
        return f"{rtl_mark}{val:.1f} שנים" if val % 1 != 0 else f"{rtl_mark}{int(val)} שנים"
        
    if unit == "%":
        return f"{rtl_mark}{val:.1f}%"
        
    return f"{rtl_mark}{val} {unit}" if unit else f"{rtl_mark}{val}"

# ==============================================================================
# 🧱 רכיבי הזנה
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
