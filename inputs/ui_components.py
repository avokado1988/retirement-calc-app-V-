import streamlit as st

# ==============================================================================
# 🎯 מילון ערכי ברירת המחדל
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
# 🎨 מנוע העיצוב המדויק - צבעים, יישור וצמצום רווחים
# ==============================================================================
def inject_design_system():
    st.markdown("""
    <style>
        /* ביטול מרווחים בין עמודות בסרגל הצד */
        [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
            gap: 0px !important;
            align-items: center !important; 
            direction: rtl !important; 
            margin-bottom: 10px !important; 
        }

        /* תווית לבנה מימין */
        .custom-sidebar-label {
            font-size: 14px !important;
            font-weight: 500 !important;
            color: #ffffff !important;
            white-space: nowrap !important;
            text-align: right !important;
            padding-left: 5px;
        }

        /* ערך צבעוני משמאל - מוצמד לחלונית */
        .custom-sidebar-badge {
            font-size: 14px !important;
            font-weight: 700 !important;
            direction: rtl !important;
            text-align: right !important; /* יישור לימין בתוך העמודה השמאלית להצמדה */
            white-space: nowrap !important;
            margin-right: 2px !important;
        }

        /* כפיית צבע על הילדים של ה-badge */
        .custom-sidebar-badge * {
            color: inherit !important;
        }

        /* עיצוב חלונית ההזנה */
        [data-testid="stSidebar"] .stNumberInput {
            width: 75px !important;
        }
        [data-testid="stSidebar"] .stNumberInput div[data-baseweb="input"] {
            height: 28px !important;
            border-radius: 4px !important;
            background-color: #ffffff !important;
        }
        [data-testid="stSidebar"] .stNumberInput input {
            color: #000000 !important;
            padding: 2px !important;
            font-size: 13px !important;
            text-align: center !important;
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
# 🚥 לוגיקת הצבעים שסיכמנו
# ==============================================================================
def _get_dynamic_color_by_label(label):
    lbl = label.lower()
    # כתום: קרן חירום
    if "חירום" in lbl or "מזומן" in lbl: return "#fb923c" 
    # אדום: הוצאות, אינפלציה, עזרה לילדים, דמי ניהול, מס
    if any(x in lbl for x in ["הוצאה", "הוצאות", "אינפלציה", "עזרה", "ניהול", "עלות", "מס"]): return "#f87171" 
    # ירוק: הכנסות, קצבאות, חסכונות, תשואה, נטו ממכירה, שווי נדל"ן
    if any(x in lbl for x in ["הכנסה", "קצבה", "חיסכון", "חסכונות", "תשואה", "מכירה", "נדלן", "נדל\"ן", "הון"]): return "#4ade80" 
    # לבן: גילאים וזמנים
    return "#ffffff" 

def _format_compact_value(val, unit):
    val = float(val)
    rtl_mark = "\u200f"
    if unit in ["₪", "שח", "ש\"ח"]:
        if val >= 1_000_000 or val <= -1_000_000: return f"{rtl_mark}{val / 1_000_000:.2f} מ׳ ₪"
        if val >= 100_000 or val <= -100_000: return f"{rtl_mark}{val / 1_000:.0f} א׳ ₪"
        return f"{rtl_mark}{int(val):,} ₪" 
    if unit == "שנים": return f"{rtl_mark}{val:.1f} שנים" if val % 1 != 0 else f"{rtl_mark}{int(val)} שנים"
    if unit == "%": return f"{rtl_mark}{val:.1f}%"
    return f"{rtl_mark}{val} {unit}" if unit else f"{rtl_mark}{val}"

# ==============================================================================
# 🧱 רכיבי ההזנה - מבנה 3 עמודות צפוף ללא סליידר
# ==============================================================================
def compact_number_input(label, value, min_value=0, max_value=None, step=1, unit="₪"):
    widget_key = f"saved_v3_{label.replace(' ', '_')}"
    is_float = isinstance(value, float) or isinstance(step, float) or (min_value is not None and isinstance(min_value, float))
    
    if widget_key in st.query_params:
        try:
            stored_val = st.query_params[widget_key]
            value = float(stored_val) if is_float else int(float(stored_val))
        except: pass

    val_to_use = float(value) if is_float else int(value)
    min_to_use = float(min_value) if min_value is not None else (0.0 if is_float else 0)
    step_to_use = float(step) if is_float else int(step)

    temp_key = widget_key + "_v7_holder"
    text_color = _get_dynamic_color_by_label(label)

    # יחס עמודות חדש וצפוף: [ערך צבעוני] [חלונית] [תגית]
    col1, col2, col3 = st.columns([5.5, 1.8, 2.7])
    with col3:
        st.markdown(f"<div class='custom-sidebar-label'>{label}</div>", unsafe_allow_html=True)
    with col2:
        res = st.number_input(label, min_value=min_to_use, max_value=max_to_use, value=val_to_use, step=step_to_use, label_visibility="collapsed", key=temp_key)
    with col1:
        formatted_display = _format_compact_value(res, unit)
        st.markdown(f"<div class='custom-sidebar-badge' style='color: {text_color} !important;'>{formatted_display}</div>", unsafe_allow_html=True)
    
    st.query_params[widget_key] = str(res)
    return res

def labeled_slider_with_value(label, min_value, max_value, value, step=1.0, format=None, unit=None):
    # הסבה של פונקציית ה"סליידר" להזנה בלבד כדי לשמור על אחידות המערכת
    is_pct = format is not None and "%" in format
    display_unit = "%" if is_pct else (unit if unit else "")
    
    # שימוש ב-compact_number_input לביצוע ההזנה בפועל
    return compact_number_input(label, value, min_value, max_value, step, unit=display_unit)
