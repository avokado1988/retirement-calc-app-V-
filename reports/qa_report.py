import streamlit as st
import pandas as pd
from inputs.ui_components import format_shekel

def render_qa_section(results, user_inputs):
    # CSS ליישור מימין לשמאל בלבד
    st.markdown("<style>.stTable, table { direction: rtl !important; text-align: right !important; } th, td { text-align: right !important; direction: rtl !important; }</style>", unsafe_allow_html=True)

    df_history = results["df"]
    df_full = results.get("df_full", df_history)
    
    timeline = user_inputs.get("timeline", {})
    wealth = user_inputs.get("wealth", {})
    
    start_age = float(timeline.get("start_age", 60))
    check_age = float(timeline.get("check_age", 80))
    retire_age = float(timeline.get("retirement_age", start_age))
    
    amendment_190 = user_inputs.get("amendment_190", {})
    real_tax_25 = user_inputs.get("real_tax_25", {})
    
    initial_capital_190 = float(amendment_190.get("net_for_190") or 0)
    initial_capital_25 = float(real_tax_25.get("net_for_real_pathway") or 0)
    
    # הבייסליין האקטוארי לכל חישובי ההתאוששות (תפוחים לתפוחים לפי הדרישה)
    baseline_capital = initial_capital_25
    
    property_value_start = float(wealth.get("new_apartment_cost") or 0)
    appreciation_rate = float(wealth.get("property_appreciation") or 0)
    emergency_fund = float(wealth.get("emergency_fund") or 0)
    pension_190_start = float(amendment_190.get("desired_pension") or 0)
    
    # --- 1. נקודת הפרישה ---
    df_retire = df_history[df_history["גיל"] >= retire_age]
    if not df_retire.empty:
        row_retire = df_retire.iloc[0]
    else:
        row_retire = df_history.iloc[-1]
        
    exp_retire = float(row_retire["הוצאה נומינלית"])
    inc_retire = float(row_retire["הכנסה נומינלית"])
    balance_190_retire = float(row_retire["צבירה תיקון 190"])
    balance_25_retire = float(row_retire["צבירה מסלול ריאלי"])
    
    years_to_retire = retire_age - start_age
    property_value_retire = property_value_start * ((1 + appreciation_rate) ** years_to_retire)
    
    net_needed_190_retire = max(0.0, exp_retire - inc_retire - pension_190_start)
    net_needed_25_retire = max(0.0, exp_retire - inc_retire)
    
    pct_190_retire = 0.0
    if balance_190_retire > 0:
        pct_190_retire = (net_needed_190_retire * 12) / balance_190_retire * 100
        
    pct_25_retire = 0.0
    if balance_25_retire > 0:
        pct_25_retire = (net_needed_25_retire * 12) / balance_25_retire * 100
        
    rule400_190_retire = "∞"
    emer_190_retire = "∞"
    if net_needed_190_retire > 0:
        v_rule = balance_190_retire / (net_needed_190_retire * 400)
        rule400_190_retire = f"{v_rule:.2f}"
        v_emer = emergency_fund / (net_needed_190_retire * 12)
        emer_190_retire = f"{v_emer:.1f}"
        
    rule400_25_retire = "∞"
    emer_25_retire = "∞"
    if net_needed_25_retire > 0:
        v_rule2 = balance_25_retire / (net_needed_25_retire * 400)
        rule400_25_retire = f"{v_rule2:.2f}"
        v_emer2 = emergency_fund / (net_needed_25_retire * 12)
        emer_25_retire = f"{v_emer2:.1f}"

    total_wealth_190_retire = balance_190_retire + property_value_retire + emergency_fund
    total_wealth_25_retire = balance_25_retire + property_value_retire + emergency_fund

    # --- 2. נקודת הגיל הנבדק ---
    df_filtered = df_history[df_history["גיל"] >= check_age]
    if not df_filtered.empty:
        row_check = df_filtered.iloc[0]
    else:
        row_check = df_history.iloc[-1]
        
    exp_check = float(row_check["הוצאה נומינלית"])
    inc_check = float(row_check["הכנסה נומינלית"])
    balance_190_check = float(row_check["צבירה תיקון 190"])
    balance_25_check = float(row_check["צבירה מסלול ריאלי"])
    
    years_passed_check = check_age - start_age
    property_value_check = property_value_start * ((1 + appreciation_rate) ** years_passed_check)
    
    net_needed_190_check = max(0.0, exp_check - inc_check - pension_190_start)
    net_needed_25_check = max(0.0, exp_check - inc_check)
    
    pct_190_check = 0.0
    if balance_190_check > 0:
        pct_190_check = (net_needed_190_check * 12) / balance_190_check * 100
        
    pct_25_check = 0.0
    if balance_25_check > 0:
        pct_25_check = (net_needed_25_check * 12) / balance_25_check * 100
        
    rule400_190_check = "∞"
    if net_needed_190_check > 0:
        v_chk1 = balance_190_check / (net_needed_190_check * 400)
        rule400_190_check = f"{v_chk1:.2f}"
        
    rule400_25_check = "∞"
    if net_needed_25_check > 0:
        v_chk2 = balance_25_check / (net_needed_25_check * 400)
        rule400_25_check = f"{v_chk2:.2f}"
        
    bool_preserve_190 = "✅ כן" if balance_190_check > baseline_capital else "❌ לא"
    bool_preserve_25 = "✅ כן" if balance_25_check > baseline_capital else "❌ לא"
    
    total_wealth_190_check = balance_190_check + property_value_check
    total_wealth_25_check = balance_25_check + property_value_check

    # --- 3. סריקות מערך לגילאים מתקדמים ---
    intersection_age = "לא משתווים"
    has_been_lower = False
    for idx in range(len(df_full)):
        b190 = float(df_full.iloc[idx]["צבירה תיקון 190"])
        b25 = float(df_full.iloc[idx]["צבירה מסלול ריאלי"])
        curr_age = float(df_full.iloc[idx]["גיל"])
        if b190 < b25:
            has_been_lower = True
        if has_been_lower and b190 >= b25 and curr_age > start_age:
            intersection_age = f"{curr_age:.1f}"
            break

    recovery_age_190 = "לא עובר"
    for idx in range(len(df_full)):
        if float(df_full.iloc[idx]["צבירה תיקון 190"]) > baseline_capital and float(df_full.iloc[idx]["גיל"]) > start_age:
            recovery_age_190 = f"{float(df_full.iloc[idx]['גיל']):.1f}"
            break

    recovery_age_25 = "לא עובר"
    for idx in range(len(df_full)):
        if float(df_full.iloc[idx]["צבירה מסלול ריאלי"]) > baseline_capital and float(df_full.iloc[idx]["גיל"]) > start_age:
            recovery_age_25 = f"{float(df_full.iloc[idx]['גיל']):.1f}"
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

    ratio_190_97 = float(results.get("ratio_190_97", 0.0)) * 100
    ratio_25_97 = float(results.get("ratio_25_97", 0.0)) * 100

    # --- מחרוזות מעוצבות למניעת שגיאות ---
    pct_190_retire_str = f"{pct_190_retire:.2f}%"
    pct_25_retire_str = f"{pct_25_retire:.2f}%"
    pct_190_check_str = f"{pct_190_check:.2f}%"
    pct_25_check_str = f"{pct_25_check:.2f}%"
    ratio_190_str = f"{ratio_190_97:.2f}%"
    ratio_25_str = f"{ratio_25_97:.2f}%"

    # ===============================================
    # הרכבת הטבלאות למסך
    # ===============================================

    st.subheader(f"📊 מצב ביום הפרישה (גיל {retire_age:.1f})")
    df_start_table = pd.DataFrame({
        "שאלה": [
            "עם כמה כסף אני מגיע לגיל פרישה בתיק?",
            "מה שווי הנדלן שלי בפרישה?",
            "גובה קצבאות בפרישה",
            "כמה כסף נטו אצטרך למשוך מהתיק בכל חודש?",
            "פי כמה גדול ההון שלי ממה שצריך לפי חוק ה-400?",
            "כמה שנים ניתן לחיות מקרן החירום בשנים הראשונות?",
            "קצב המשיכה באחוזים בפרישה?",
            "מה שווי כלל הנכסים שלי (הון + נדלן)?"
        ],
        "מסלול תיקון 190": [
            format_shekel(balance_190_retire),
            format_shekel(property_value_retire),
            format_shekel(inc_retire + pension_190_start),
            f"-{format_shekel(net_needed_190_retire)}",
            rule400_190_retire,
            emer_190_retire,
            pct_190_retire_str,
            format_shekel(total_wealth_190_retire)
        ],
        "מסלול 25% מס ריאלי": [
            format_shekel(balance_25_retire),
            format_shekel(property_value_retire),
            format_shekel(inc_retire),
            f"-{format_shekel(net_needed_25_retire)}",
            rule400_25_retire,
            emer_25_retire,
            pct_25_retire_str,
            format_shekel(total_wealth_25_retire)
        ]
    })
    st.table(df_start_table.set_index("שאלה"))

    st.subheader(f"🔮 מצב בגיל נבדק בסימולציה (גיל {check_age:.1f})")
    df_check_table = pd.DataFrame({
        "שאלה": [
            "כמה כסף נטו אצטרך למשוך מהתיק בכל חודש?",
            "מה שיעור המשיכה בגיל הנבדק?",
            "פי כמה גדול ההון שלי ממה שצריך לפי חוק ה-400?",
            "כמה כסף נזיל יישאר לי בתיק?",
            "האם ישאר לי יותר כסף ממה שהתחלתי איתו?",
            "גיל שבו התיקים משתווים",
            "גיל שבו התיקים עוברים את ההון ההתחלתי",
            "מה שווי כלל הנכסים שלי (הון + נדלן)?"
        ],
        "מסלול תיקון 190": [
            f"-{format_shekel(net_needed_190_check)}",
            pct_190_check_str,
            rule400_190_check,
            format_shekel(balance_190_check),
            bool_preserve_190,
            intersection_age,
            recovery_age_190,
            format_shekel(total_wealth_190_check)
        ],
        "מסלול 25% מס ריאלי": [
            f"-{format_shekel(net_needed_25_check)}",
            pct_25_check_str,
            rule400_25_check,
            format_shekel(balance_25_check),
            bool_preserve_25,
            intersection_age,
            recovery_age_25,
            format_shekel(total_wealth_25_check)
        ]
    })
    st.table(df_check_table.set_index("שאלה"))

    st.subheader("🏁 שורה תחתונה וחסינות אקטוארית")
    df_bottom_table = pd.DataFrame({
        "שורה תחתונה": [
            "עד איזה גיל הכסף יחזיק (חסינות)?",
            "כמה אחוז מההון ההתחלתי נשמר בגיל 97 עם מטפלת?"
        ],
        "מסלול תיקון 190": [
            empty_190_str,
            ratio_190_str
        ],
        "מסלול 25% מס ריאלי": [
            empty_25_str,
            ratio_25_str
        ]
    })
    st.table(df_bottom_table.set_index("שורה תחתונה"))
