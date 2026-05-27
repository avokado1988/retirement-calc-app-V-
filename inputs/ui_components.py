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
# 🎨 מנוע עיצוב ברזל - חסינות שורות, מרווחים אסתטיים וביטול דריסות
# ==============================================================================
st.markdown("""
<style>
    /* 1. הגדרת השורה כולה כמכלול אופקי קשיח ללא יכולת קיפול או שבירה */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important; /* חוסם לחלוטין נפילת שורות */
        align-items: center !important; /* מירכוז אנכי מושלם */
        direction: rtl !important; 
        margin-bottom: 14px !important; /* מרווח אסתטי ונקי בין שורה לשורה */
        padding: 0 !important;
        width: 100% !important;
    }

    /* ניקוי שוליים ופדינגים כפולים של עמודות סטרימליט */
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

    /* עמודה 3: הערך הפיננסי הצבעוני משמאל - מוצמד הדוק לחלונית */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(3) {
        flex: 0 0 auto !important;
        min-width: max-content !important;
        text-align: right !important;
        margin-right: 8px !important;
    }

    /* ביטול מוחלט של שבירת פסקאות מרקדאון */
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

    /* קיבוע חלון ההזנה הלבן/שחור */
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

# 🎯 תיקון כרטיס הסיכום: המסגרת הירוקה הצידית נמחקה לצמיתות (border-right רגיל ללא צבע זרחני)
def show_net_summary(title, amount):
    st.markdown(
        f"<div style='padding:12px; background-color:#1e293b; border:1px solid #334155; border-radius:6px; margin:14px 0; direction: rtl; text-align: right;'> "
        f"<span style='font-weight:600; color:#ffffff; font-size:15px;'>{title}:</span> "
        f"<span style='font-weight:700; color:#4ade80; font-size:16px; margin-right:6px;'>{format_shekel(amount)}</span>"
        f"</div>", 
        unsafe_allow_html=True
    )

def wrap_html_style(text, style_str):
    return f"<span style='{style_str}'>{text}</span>"

# ==============================================================================
# 🚥 פונקציות הרמזור האקטואריות לטבלאות - הזרקת !important למניעת דריסה
# ==============================================================================
def get_withdrawal_style(pct):
    val = float(pct)
    if val <= 3.5: return "color: #4ade80 !important; font-weight: bold !important;"
    if val <= 5.0: return "color: #fb923c !important; font-weight: bold !important;"
    return "color: #f87171 !important; font-weight: bold !important;"

def get_400_rule_style(val_str):
    if val_str == "∞": return "color: #4ade80 !important; font-weight: bold !important;"
    try: return "color: #4ade80 !important; font-weight: bold !important;" if float(val_str) >= 1.0 else "color: #f87171 !important; font-weight: bold !important;"
    except: return ""

def get_emergency_style(val_str):
    if val_str == "∞": return "color: #4ade80 !important; font-weight: bold !important;"
    try: return "color: #4ade80 !important; font-weight: bold !important;" if float(val_str) >= 1.0 else "color: #f87171 !important; font-weight: bold !important;"
    except: return ""

# 🎯 תיקון המסגרת המכוערת: הוסרו לחלוטין כל הגבולות והרקעים, מעכשיו זה טקסט ירוק/לבן נקי!
def get_larger_portfolio_style(is_larger):
    if is_larger: 
        return "color: #4ade80 !important; font-weight: 700 !important;"
    return "color: #ffffff !important; font-weight: 500 !important;"

def get_resiliency_style(val_str):
    return "color: #4ade80 !important; font-weight: bold !important;" if "חסין" in val_str or "105" in val_str else "color: #f87171 !important; font-weight: bold !important;"

def get_preservation_pct_style(pct):
    return "color: #4ade80 !important; font-weight: bold !important;" if float(pct) >= 100.0 else "color: #f87171 !important; font-weight: bold !important;"

def get_boolean_style(val_str):
    return "color: #4ade80 !important; font-weight: bold !important;" if "✅" in val_str else "color: #f87171 !important; font-weight: bold !important;"

def _get_dynamic_color_by_label(label):
    lbl = label.lower()
    if "חירום" in lbl: return "#fb923c" 
    if any(x in lbl for x in ["הוצאה", "הוצאות", "מס", "עלות", "אינפלציה", "עזרה", "ניהול", "גירעון"]): return "#f87171" 
    if any(x in lbl for x in ["הכנסה", "הכנסות", "קצבה", "קצבת", "חיסכון", "חסכונות", "תשואה", "מכירה", "עליה ערך", "נזיל", "תיק", "יישאר"]): return "#4ade80" 
    return "#ffffff" 

# 🎯 תיקון מנוע הקיצורים: סכומים קטנים מ-100,000 ₪ מוצגים במלואם (למשל: 2,500 ₪ ולא 2 א׳)
def _format_compact_value(val, unit):
    val = float(val)
    rtl_mark = "\u200f"
    
    if unit in ["₪", "שח", "ש\"ח"]:
        if val >= 1_000_000 or val <= -1_000_000:
            formatted = f"{val / 1_000_000:.2f}"
            return f"{rtl_mark}{formatted} מ׳ ₪"
        if val >= 100_000 or val <= -100_000:
            return f"{rtl_mark}{val / 1_000:.0f} א׳ ₪"
        return f"{rtl_mark}{int(val):,} ₪" # תצוגה מלאה ומפורטת לאלפים קטנים
        
    if unit == "שנים":
        return f"{rtl_mark}{val:.1f} שנים" if val % 1 != 0 else f"{rtl_mark}{int(val)} שנים"
        
    if unit == "%":
        return f"{rtl_mark}{val:.1f}%"
        
    return f"{rtl_mark}{val} {unit}" if unit else f"{rtl_mark}{val}"

# ==============================================================================
# 🧱 רכיבי הזנה מבוססי ארכיטקטורת 3 עמודות מאוזנות
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
