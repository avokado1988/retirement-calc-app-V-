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
    /* 1. הגדרת השורה כולה כמכלול אופקי קשיח ללא יכולת קיפול או שבירה */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important; /* חוסם לחלוטין נפילת שורות */
        align-items: center !important; /* מירכוז אנכי מושלם */
        direction: rtl !important; 
        margin-bottom: 14px !important; 
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

    .custom-sidebar-badge, .custom-sidebar-badge * {
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
    if val_str == "∞": return "color
