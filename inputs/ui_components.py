import streamlit as st

# ==============================================================================
# 🎯 מילון ערכי ברירת המחדל המעודכנים והמדויקים של המערכת
# ==============================================================================
DEFAULTS = {
    "start_age": 65.5,
    "retirement_age": 67.0,
    "check_age": 95.0,
    "desired_pension": 5306,
    "current_expenses": 11000,
    "expected_inflation": 0.023,
    "age_75_85_increase": 0.005,         
    "age_85_plus_increase": 0.015,
    "one_time_expense": 80000,
    "one_time_frequency": 8,
    "caregiver_cost": 0,
    "national_insurance": 2500,         
    "work_income": 0,
    "net_sale": 10000000,
    "existing_savings": 440000,          
    "new_apartment_cost": 5800000,
    "property_appreciation": 0.023,
    "kids_help": 1000000,
    "emergency_fund": 300000,
    "annual_return": 0.055,              
    "management_fee": 0.006              
}

# ==============================================================================
# 🎨 הזרקת העיצוב הגלובלית האוטומטית - מחזירה את תפריט הצד לחיים!
# ==============================================================================
st.markdown("""
<style>
    /* יישור אלמנטים בסרגל הצד לימין ולמרכזם אנכית */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
        align-items: center !important; 
        direction: rtl !important; 
        margin-bottom: 12px !important; 
    }

    /* תוויות וערכים בסרגל הצד */
    .custom-sidebar-label {
        font-size: 14px !important;
        font-weight: 500 !important;
        color: #ffffff !important;
        line-height: 1.2 !important;
    }

    .custom-sidebar-badge {
        font-size: 14.5px !important;
        font-weight: 700 !important;
        direction: rtl !important;
        text-align: left !important;
        white-space: nowrap !important;
    }

    /* עיצוב שדות הזנת מספר - קומפקטיים */
    [data-testid="stSidebar"] .stNumberInput div[data-baseweb="input"] {
        height: 32px !important;
        border-radius: 6px !important;
    }
    [data-testid="stSidebar"] .stNumberInput input {
        padding: 2px 4px !important;
        font-size: 13.5px !important;
        text-align: center !important;
    }
    
    /* הסתרת מרווחים מיותרים מסליידרים */
    [data-testid="stSidebar"] .stSlider {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
</style>
""", unsafe_allow_html=True)


def format_shekel(amount):
    return f"{int(amount):,} ₪" if amount is not None else "0 ₪"

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
# 🚥 פונקציות הרמזור האקטואריות לטבלאות
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

def get_larger_portfolio_style(is_larger):
    if is_larger: return "color: #4ade80 !important; font-weight: 700 !important;"
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

def _format_compact_value(val, unit):
    val = float(val)
    rtl_mark = "\u200f"
    
    if unit in ["₪", "שח", "ש\"ח"]:
        if val >= 1_000_000 or val <= -1_000_000:
            formatted = f"{val / 1_000_000:.2f}"
            return f"{rtl_mark}{formatted} מ׳ ₪"
        if val >= 100_000 or val <= -100_000:
            return f"{rtl_mark}{val / 1_000:.0f} א׳ ₪"
        return f"{rtl_mark}{int(val):,} ₪" 
        
    if unit == "שנים":
        return f"{rtl_mark}{val:.1f} שנים" if val % 1 != 0 else f"{rtl_mark}{int(val)} שנים"
        
    if unit == "%":
        return f"{rtl_mark}{val:.1f}%"
        
    return f"{rtl_mark}{val} {unit}" if unit else f"{rtl_mark}{val}"

# ==============================================================================
# 🧱 רכיבי הזנה חסינים בסרגל הצד (עם נעילת סוגים אבסולוטית)
# ==============================================================================
def compact_number_input(label, value, min_value=0, max_value=None, step=1, unit="₪"):
    widget_key = f"saved_v3_{label.replace(' ', '_')}"
    is_float = isinstance(value, float) or isinstance(step, float) or (min_value is not None and isinstance(min_value, float)) or (max_value is not None and isinstance(max_value, float))

    if widget_key in st.query_params:
        try:
            stored_val = st.query_params[widget_key]
            value = float(stored_val) if is_float else int(float(stored_val))
        except:
            pass

    if is_float:
        val_to_use = float(value) if value is not None else 0.0
        min_to_use = float(min_value) if min_value is not None else 0.0
        max_to_use = float(max_value) if max_value is not None else None
        step_to_use = float(step) if step is not None else 1.0
    else:
        val_to_use = int(value) if value is not None else 0
        min_to_use = int(min_value) if min_value is not None else 0
        max_to_use = int(max_value) if max_value is not None else None
        step_to_use = int(step) if step is not None else 1

    temp_key = widget_key + "_v7_holder"
    text_color = _get_dynamic_color_by_label(label)

    # 🟢 יחס עמודות מותאם למספרים
    col1, col2, col3 = st.columns([5, 2.5, 2.5])
    with col1:
        st.markdown(f"<div class='custom-sidebar-label'>{label}</div>", unsafe_allow_html=True)
        
    with col2:
        res = st.number_input(
            label, min_value=min_to_use, max_value=max_to_use, 
            value=val_to_use, step=step_to_use, label_visibility="collapsed", key=temp_key
        )
    with col3:
        formatted_display = _format_compact_value(res, unit)
        # 🟢 התיקון הקריטי: הוספת !important לצבע הדינמי כדי לדרוס הגדרות ברירת מחדל
        st.markdown(f"<div class='custom-sidebar-badge' style='color: {text_color} !important;'>{formatted_display}</div>", unsafe_allow_html=True)
    
    st.query_params[widget_key] = str(res)
    return res

def labeled_slider_with_value(label, min_value, max_value, value, step=1.0, format=None, unit=None):
    widget_key = f"saved_v3_{label.replace(' ', '_')}"
    is_percentage_fraction = format is not None and "%" in format and float(value) <= 1.0
    
    if widget_key in st.query_params:
        try:
            stored_val = float(st.query_params[widget_key])
            value = stored_val
        except:
            pass

    if is_percentage_fraction:
        val_to_use = float(value) * 100.0 if float(value) <= 1.0 else float(value)
        min_to_use = float(min_value) * 100.0
        max_to_use = float(max_value) * 100.0
        step_to_use = float(step) * 100.0 if step is not None else 1.0
        display_unit = "%"
    else:
        display_unit = unit if unit else ""
        is_float = isinstance(value, float) or isinstance(step, float) or (min_value is not None and isinstance(min_value, float)) or (max_value is not None and isinstance(max_value, float))
        if is_float:
            val_to_use = float(value)
            min_to_use = float(min_value) if min_value is not None else 0.0
            max_to_use = float(max_value) if max_value is not None else None
            step_to_use = float(step) if step is not None else 1.0
        else:
            val_to_use = int(value)
            min_to_use = int(min_value) if min_value is not None else 0
            max_to_use = int(max_value) if max_value is not None else None
            step_to_use = int(step) if step is not None else 1

    temp_key = widget_key + "_v7_holder"
    text_color = _get_dynamic_color_by_label(label)
    
    # 🟢 יחס עמודות שנותן סוף סוף מקום ראוי לסליידר
    col1, col2, col3 = st.columns([4, 4, 2])
    with col1:
        st.markdown(f"<div class='custom-sidebar-label'>{label}</div>", unsafe_allow_html=True)

    with col2:
        # 🟢 התיקון הקריטי 2: החזרת הפקודה st.slider שהעלמתי בטעות!
        raw_input = st.slider(
            label, min_value=min_to_use, max_value=max_to_use, 
            value=val_to_use, step=step_to_use, label_visibility="collapsed", key=temp_key
        )
    with col3:
        formatted_display = _format_compact_value(raw_input, display_unit)
        # 🟢 התיקון הקריטי: הוספת !important לצבע 
        st.markdown(f"<div class='custom-sidebar-badge' style='color: {text_color} !important;'>{formatted_display}</div>", unsafe_allow_html=True)
        
    res = float(raw_input) / 100.0 if is_percentage_fraction else raw_input
    st.query_params[widget_key] = str(res)
    return res
