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
# 🎨 מנוע העיצוב הגלובלי - יישור, מרווחים אסתטיים וצבעים קשיחים
# ==============================================================================
def inject_design_system():
    st.markdown("""
    <style>
        /* ביטול מרווחים בין עמודות בסרגל הצד ושמירה על שורה אחידה */
        [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
            gap: 2px !important;
            flex-wrap: nowrap !important;
            align-items: center !important; 
            direction: rtl !important; 
            margin-bottom: 12px !important; 
        }

        /* תווית לבנה מימין */
        .custom-sidebar-label {
            font-size: 14px !important;
            font-weight: 500 !important;
            color: #ffffff !important;
            white-space: nowrap !important;
            text-align: right !important;
            padding-left: 4px !important;
        }

        /* ערך צבעוני משמאל - מוצמד הדוק לחלונית בזכות יישור ימין מדויק */
        .custom-sidebar-badge {
            font-size: 14.5px !important;
            font-weight: 700 !important;
            direction: rtl !important;
            text-align: right !important; 
            white-space: nowrap !important;
            margin-right: 6px !important;
        }

        .custom-sidebar-badge p {
            margin: 0 !important;
            padding: 0 !important;
        }

        /* 🟢 עיצוב חלונית ההזנה - מותאם למסך כהה וקריא לחלוטין */
        [data-testid="stSidebar"] .stNumberInput {
            width: 100% !important;
        }
        [data-testid="stSidebar"] .stNumberInput div[data-baseweb="input"] {
            height: 28px !important;
            border-radius: 4px !important;
            background-color: #334155 !important;
            border: 1px solid #475569 !important;
        }
        [data-testid="stSidebar"] .stNumberInput input {
            color: #ffffff !important;
            padding: 2px !important;
            font-size: 13.5px !important;
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
# 🚥 פונקציות הרמזור לדו"ח המרכזי
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

# ==============================================================================
# 🚥 לוגיקת צבעי סרגל הצד - עכשיו עם נתונים אקטואריים בכחול!
# ==============================================================================
def _get_dynamic_color_by_label(label):
    lbl = label.lower()
    # כתום: קרן חירום
    if "חירום" in lbl or "מזומן" in lbl: return "#fb923c" 
    # כחול: נתונים אקטואריים
    if any(x in lbl for x in ["גיל", "שנים", "מקדם", "אבטחה", "תקופת", "יעד"]): return "#60a5fa" 
    # אדום: הוצאות, אינפלציה, מס, עלויות
    if any(x in lbl for x in ["הוצאה", "הוצאות", "אינפלציה", "עזרה", "ניהול", "עלות", "מס", "דירה", "רכישה", "ילדים"]): return "#f87171" 
    # ירוק: הכנסות, קצבאות, תשואה, נדל"ן
    if any(x in lbl for x in ["הכנסה", "קצבה", "חיסכון", "חסכונות", "תשואה", "מכירה", "נדלן", "נדל\"ן", "הון", "פנסיה", "ביטוח"]): return "#4ade80" 
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
# 🧱 מנוע ההזנה המאוחד - חלוניות בלבד
# ==============================================================================
def compact_number_input(label, value, min_value=0, max_value=None, step=1, unit="₪", is_pct=False):
    widget_key = f"saved_v4_{label.replace(' ', '_')}"
    is_float = isinstance(value, float) or isinstance(step, float) or (min_value is not None and isinstance(min_value, float)) or is_pct
    
    if widget_key in st.query_params:
        try:
            stored_val = float(st.query_params[widget_key])
            value = stored_val * 100.0 if is_pct else stored_val
            if not is_float: value = int(value)
        except: pass

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

    # 🎯 פרופורציות אסתטיות ומדויקות: [תגית ימין 5.2] [הזנה 2.2] [ערך 2.6]
    col1, col2, col3 = st.columns([5.2, 2.2, 2.6])
    with col1:
        st.markdown(f"<div class='custom-sidebar-label'>{label}</div>", unsafe_allow_html=True)
    with col2:
        res = st.number_input(label, min_value=min_to_use, max_value=max_to_use, value=val_to_use, step=step_to_use, label_visibility="collapsed", key=temp_key)
    with col3:
        formatted_display = _format_compact_value(res, "%" if is_pct else unit)
        # הזרקת פקודת הצבע ישירות לספאן חוסמת כל סיכוי לדריסה של סטרימליט!
        st.markdown(f"<div class='custom-sidebar-badge'><span style='color: {text_color} !important;'>{formatted_display}</span></div>", unsafe_allow_html=True)
    
    final_val = float(res) / 100.0 if is_pct else res
    st.query_params[widget_key] = str(final_val)
    return final_val

def labeled_slider_with_value(label, min_value, max_value, value, step=1.0, format=None, unit=None):
    is_pct = format is not None and "%" in format
    display_unit = "%" if is_pct else (unit if unit else "")
    return compact_number_input(label, value, min_value, max_value, step, unit=display_unit, is_pct=is_pct)
