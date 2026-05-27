import streamlit as st
import pandas as pd
from inputs.ui_components import format_shekel, wrap_html_style

# 🚥 פונקציות הרמזור והצבע (ייעודיות רק לדו"ח)
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

# 🟢 מזרק כיווניות קשיח לטבלאות פנדס
def _render_rtl_table(df, index_col):
    raw_html = df.set_index(index_col).to_html(escape=False, classes='styled-table')
    rtl_html = raw_html.replace('<table', '<table dir="rtl"')
    st.markdown(f"<div dir='rtl' style='width: 100%; text-align: right;'>{rtl_html}</div>", unsafe_allow_html=True)

def render_qa_section(results, user_inputs):
    # 🎨 עיצוב מבודד לטבלאות הדו"ח בלבד
    st.markdown("""
        <style>
        table.styled-table { 
            width: 100% !important; 
            border-collapse: collapse !important; 
            margin: 25px 0 !important; 
            font-family: sans-serif; 
            background-color: #1e293b !important; 
            border: 1px solid #334155 !important;
            border-radius: 8px !important;
            overflow: hidden !important;
            direction: rtl !important;
        }
        table.styled-table th { 
            background-color: #334155 !important; 
            color: #ffffff !important; 
            padding: 14px 16px !important; 
            font-weight: bold !important; 
            border-bottom: 3px solid #475569 !important; 
            font-size: 14.5px !important;
            text-align: right !important;
        }
        table.styled-table td { 
            padding: 12px 16px !important; 
            border-bottom: 1px solid #334155 !important; 
            color: #ffffff; /* ללא important כדי שהרמזור יעבוד! */
            font-size: 14px !important;
            text-align: right !important;
        }
        </style>
    """, unsafe_allow_html=True)

    df_history = results["df"]
    df_full = results["df_full"]
    baseline_capital = results.get("baseline_capital", 1.0)
    
    timeline = user_inputs.get("timeline", {})
    wealth = user_inputs.get("wealth", {})
    
    start_age = float(timeline.get("start_age", 65.5))
    check_age = float(timeline.get("check_age", 87.0))
    retire_age = float(timeline.get("retirement_age", start_age))
    
    emergency_fund = float(wealth.get("emergency_fund", 0))
    property_value_start = float(wealth.get("new_apartment_cost", 0))
    appreciation_rate = float(wealth.get("property_appreciation", 0))

    # --- 1. ביום הפרישה (הנתונים נשאבים ישירות מהמנוע) ---
    row_retire = df_full[df_full["גיל"] >= retire_age].iloc[0] if not df_full[df_full["גיל"] >= retire_age].empty else df_history.iloc[-1]
    
    ni_retire = float(row_retire["קצבת ביטוח לאומי"])
    pension_190_retire = float(row_retire["קצבה מזערית 190"])
    balance_190_retire = float(row_retire["צבירה תיקון 190"])
    balance_25_retire = float(row_retire["צבירה מסלול ריאלי"])
    
    years_to_retire = retire_age - start_age
    property_value_retire = property_value_start * ((1 + appreciation_rate) ** years_to_retire)

    # שאיבה ישירה של הנטו שהמנוע חישב
    net_needed_190_retire = float(row_retire.get("נטו למשיכה 190", 0.0))
    net_needed_25_retire = float(row_retire.get("נטו למשיכה 25", 0.0))
    
    pct_190_retire = (net_needed_190_retire * 12) / balance_190_retire * 100 if balance_190_retire > 0 else 0.0
    pct_25_retire = (net_needed_25_retire * 12) / balance_25_retire * 100 if balance_25_retire > 0 else 0.0
        
    rule400_190_retire = f"{balance_190_retire / (net_needed_190_retire * 400):.2f}" if net_needed_190_retire > 0 else "∞"
    emer_190_retire = f"{emergency_fund / (net_needed_190_retire * 12):.1f}" if net_needed_190_retire > 0 else "∞"
    rule400_25_retire = f"{balance_25_retire / (net_needed_25_retire * 400):.2f}" if net_needed_25_retire > 0 else "∞"
    emer_25_retire = f"{emergency_fund / (net_needed_25_retire * 12):.1f}" if net_needed_25_retire > 0 else "∞"

    total_wealth_190_retire = balance_190_retire + property_value_retire + emergency_fund
    total_wealth_25_retire = balance_25_retire + property_value_retire + emergency_fund

    # --- 2. בגיל הנבדק (הנתונים נשאבים ישירות מהמנוע) ---
    row_check = df_full[df_full["גיל"] >= check_age].iloc[0] if not df_full[df_full["גיל"] >= check_age].empty else df_history.iloc[-1]
    
    balance_190_check = float(row_check["צבירה תיקון 190"])
    balance_25_check = float(row_check["צבירה מסלול ריאלי"])
    
    years_passed_check = check_age - start_age
    property_value_check = property_value_start * ((1 + appreciation_rate) ** years_passed_check)

    # שאיבה ישירה של הנטו שהמנוע חישב
    net_needed_190_check = float(row_check.get("נטו למשיכה 190", 0.0))
    net_needed_25_check = float(row_check.get("נטו למשיכה 25", 0.0))
    
    pct_190_check = (net_needed_190_check * 12) / balance_190_check * 100 if balance_190_check > 0 else 0.0
    pct_25_check = (net_needed_25_check * 12) / balance_25_check * 100 if balance_25_check > 0 else 0.0
        
    rule400_190_check = f"{balance_190_check / (net_needed_190_check * 400):.2f}" if net_needed_190_check > 0 else "∞"
    rule400_25_check = f"{balance_25_check / (net_needed_25_check * 400):.2f}" if net_needed_25_check > 0 else "∞"
        
    bool_preserve_190 = "✅ כן" if balance_190_check > baseline_capital else "❌ לא"
    bool_preserve_25 = "✅ כן" if balance_25_check > baseline_capital else "❌ לא"
    
    total_wealth_190_check = balance_190_check + property_value_check + emergency_fund
    total_wealth_25_check = balance_25_check + property_value_check + emergency_fund

    # --- 3. סריקות מתקדמות ---
    intersection_age = "לא משתווים"
    for idx in range(len(df_full)):
        if df_full.iloc[idx]["צבירה תיקון 190"] >= df_full.iloc[idx]["צבירה מסלול ריאלי"] and df_full.iloc[idx]["גיל"] > retire_age + 2:
            intersection_age = f"{df_full.iloc[idx]['גיל']:.1f}"
            break

    recovery_age_190 = "לא עובר"
    for idx in range(len(df_full)):
        if df_full.iloc[idx]["צבירה תיקון 190"] > baseline_capital and df_full.iloc[idx]["גיל"] > start_age:
            recovery_age_190 = f"{df_full.iloc[idx]['גיל']:.1f}"
            break
            
    recovery_age_25 = "לא עובר"
    for idx in range(len(df_full)):
        if df_full.iloc[idx]["צבירה מסלול ריאלי"] > baseline_capital and df_full.iloc[idx]["גיל"] > start_age:
            recovery_age_25 = f"{df_full.iloc[idx]['גיל']:.1f}"
            break

    empty_age_190 = 120.0
    empty_age_25 = 120.0
    for idx in range(len(df_full)):
        if float(df_full.iloc[idx]["צבירה תיקון 190"]) <= 0:
            empty_age_190 = float(df_full.iloc[idx]["גיל"])
            break
    for idx in range(len(df_full)):
        if float(df_full.iloc[idx]["צבירה מסלול ריאלי"]) <= 0:
            empty_age_25 = float(df_full.iloc[idx]["גיל"])
            break

    empty_190_str = "105+ (חסין)" if empty_age_190 >= 105.0 else f"גיל {empty_age_190:.1f}"
    empty_25_str = "105+ (חסין)" if empty_age_25 >= 105.0 else f"גיל {empty_age_25:.1f}"

    df_97 = df_full[df_full["גיל"] >= 97.0]
    row_97 = df_97.iloc[0] if not df_97.empty else df_full.iloc[-1]
    balance_at_97_190 = float(row_97["צבירה תיקון 190"])
    balance_at_97_25 = float(row_97["צבירה מסלול ריאלי"])
    
    ratio_190_str = f"{(balance_at_97_190 / max(1.0, baseline_capital)) * 100:.2f}%"
    ratio_25_str = f"{(balance_at_97_25 / max(1.0, baseline_capital)) * 100:.2f}%"

    ratio_190_pct = (balance_at_97_190 / max(1.0, baseline_capital)) * 100
    ratio_25_pct = (balance_at_97_25 / max(1.0, baseline_capital)) * 100

    is_190_larger = balance_190_check > balance_25_check

    # טבלאות תצוגה
    st.subheader(f"📊 מצב ביום הפרישה (גיל {retire_age:.1f})")
    df_start_table = pd.DataFrame({
        "שאלה": [
            "מה גודל התיק שלי בגיל פרישה?",
            "מה שווי הנדלן שלי בפרישה?",
            'גובה קצבאות בפרישה (ב"ל + פנסיה מ-190)',
            "כמה כסף נטו אצטרך למשוך מהתיק בכל חודש?",
            "פי כמה גדול ההון ממה שצריך (חוק ה-400)?",
            "כמה שנים ניתן לחיות מקרן החירום?",
            "קצב המשיכה באחוזים בפרישה?",
            "מה שווי כלל הנכסים שלי (הון + נדלן + חירום)?"
        ],
        "מסלול תיקון 190": [
            format_shekel(balance_190_retire),
            format_shekel(property_value_retire),
            format_shekel(ni_retire + pension_190_retire),
            format_shekel(net_needed_190_retire),
            wrap_html_style(rule400_190_retire, get_400_rule_style(rule400_190_retire)),
            wrap_html_style(emer_190_retire, get_emergency_style(emer_190_retire)),
            wrap_html_style(f"{pct_190_retire:.2f}%", get_withdrawal_style(pct_190_retire)),
            format_shekel(total_wealth_190_retire)
        ],
        "מסלול 25% מס ריאלי": [
            format_shekel(balance_25_retire),
            format_shekel(property_value_retire),
            format_shekel(ni_retire),
            format_shekel(net_needed_25_retire),
            wrap_html_style(rule400_25_retire, get_400_rule_style(rule400_25_retire)),
            wrap_html_style(emer_25_retire, get_emergency_style(emer_25_retire)),
            wrap_html_style(f"{pct_25_retire:.2f}%", get_withdrawal_style(pct_25_retire)),
            format_shekel(total_wealth_25_retire)
        ]
    })
    _render_rtl_table(df_start_table, "שאלה")

    st.subheader(f"🔮 מצב בגיל נבדק בסימולציה (גיל {check_age:.1f})")
    df_check_table = pd.DataFrame({
        "שאלה": [
            "כמה כסף נזיל יישאר לי בתיק?",
            "כמה כסף נטו אצטרך למשוך מהתיק בכל חודש?",
            "מה שיעור המשיכה בגיל הנבדק?",
            "האם ישאר לי יותר כסף ממה שהתחלתי איתו?",
            "גיל שבו התיקים משתווים",
            "גיל שבו התיקים עוברים את ההון ההתחלתי",
            "מה שווי כלל הנכסים שלי (הון + נדלן + חירום)?"
        ],
        "מסלול תיקון 190": [
            wrap_html_style(format_shekel(balance_190_check), get_larger_portfolio_style(is_190_larger)),
            format_shekel(net_needed_190_check),
            wrap_html_style(f"{pct_190_check:.2f}%", get_withdrawal_style(pct_190_check)),
            wrap_html_style(bool_preserve_190, get_boolean_style(bool_preserve_190)),
            intersection_age,
            recovery_age_190,
            format_shekel(total_wealth_190_check)
        ],
        "מסלול 25% מס ריאלי": [
            wrap_html_style(format_shekel(balance_25_check), get_larger_portfolio_style(not is_190_larger)),
            format_shekel(net_needed_25_check),
            wrap_html_style(f"{pct_25_check:.2f}%", get_withdrawal_style(pct_25_check)),
            wrap_html_style(bool_preserve_25, get_boolean_style(bool_preserve_25)),
            intersection_age,
            recovery_age_25,
            format_shekel(total_wealth_25_check)
        ]
    })
    _render_rtl_table(df_check_table, "שאלה")

    st.subheader("🏁 שורה תחתונה וחסינות אקטוארית")
    df_bottom_table = pd.DataFrame({
        "שורה תחתונה": [
            "עד איזה גיל הכסף יחזיק (חסינות)?",
            "כמה אחוז מההון ההתחלתי נשמר בגיל 97??"
        ],
        "מסלול תיקון 190": [
            wrap_html_style(empty_190_str, get_resiliency_style(empty_190_str)),
            wrap_html_style(f"{ratio_190_str}", get_preservation_pct_style(ratio_190_pct))
        ],
        "מסלול 25% מס ריאלי": [
            wrap_html_style(empty_25_str, get_resiliency_style(empty_25_str)),
            wrap_html_style(f"{ratio_25_str}", get_preservation_pct_style(ratio_25_pct))
        ]
    })
    _render_rtl_table(df_bottom_table, "שורה תחתונה")
