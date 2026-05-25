import streamlit as st
import pandas as pd
from inputs.ui_components import format_shekel

def render_qa_section(results, user_inputs):
    # CSS ליישור מימין לשמאל
    st.markdown("<style>.stTable, table { direction: rtl !important; text-align: right !important; } th, td { text-align: right !important; direction: rtl !important; }</style>", unsafe_allow_html=True)

    df_history = results["df"]
    timeline = user_inputs["timeline"]
    wealth = user_inputs["wealth"]
    
    start_age = float(timeline["start_age"])
    check_age = float(timeline["check_age"])
    
    initial_capital_190 = float(user_inputs["amendment_190"]["net_for_190"] or 0)
    initial_capital_25 = float(user_inputs["real_tax_25"]["net_for_real_pathway"] or 0)
    
    property_value_start = float(wealth["new_apartment_cost"] or 0)
    appreciation_rate = float(wealth["property_appreciation"] or 0)
    emergency_fund = float(wealth["emergency_fund"] or 0)
    pension_190_start = float(user_inputs["amendment_190"]["desired_pension"] or 0)
    
    row_start = df_history.iloc[0]
    exp_start = float(row_start["הוצאה נומינלית"])
    inc_start = float(row_start["הכנסה נומינלית"])
    
    df_filtered = df_history[df_history["גיל"] >= check_age]
    row_check = df_filtered.iloc[0] if not df_filtered.empty else df_history.iloc[-1]
        
    exp_check = float(row_check["הוצאה נומינלית"])
    inc_check = float(row_check["הכנסה נומינלית"])
    balance_190_check = float(row_check["צבירה תיקון 190"])
    balance_25_check = float(row_check["צבירה מסלול ריאלי"])
    
    years_passed = check_age - start_age
    property_value_check = property_value_start * ((1 + appreciation_rate) ** years_passed)
    
    net_needed_190_start = max(0.0, exp_start - inc_start - pension_190_start)
    net_needed_25_start = max(0.0, exp_start - inc_start)
    
    pct_190_start = (net_needed_190_start * 12) / max(1.0, initial_capital_190) * 100
    pct_25_start = (net_needed_25_start * 12) / max(1.0, initial_capital_25) * 100
    
    total_wealth_190_start = initial_capital_190 + property_value_start + emergency_fund
    total_wealth_25_start = initial_capital_25 + property_value_start + emergency_fund

    net_needed_190_check = max(0.0, exp_check - inc_check - pension_190_start)
    net_needed_25_check = max(0.0, exp_check - inc_check)
    
    pct_190_check = (net_needed_190_check * 12) / max(1.0, balance_190_check) * 100 if balance_190_check > 0 else 0
    pct_25_check = (net_needed_25_check * 12) / max(1.0, balance_25_check) * 100 if balance_25_check > 0 else 0
    
    total_wealth_190_check = balance_190_check + property_value_check
    total_wealth_25_check = balance_25_check + property_value_check

    ratio_190_97 = float(results.get("ratio_190_97", 0.0)) * 100
    ratio_25_97 = float(results.get("ratio_25_97", 0.0)) * 100

    # --- חישוב אקטוארי: מציאת הגיל המדויק שבו התיק מתרוקן ל-0 ---
    df_full = results["df_full"] if "df_full" in results else df_history
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

    # הפיכת גיל ההתרוקנות למחרוזת ברורה ללקוח
    if empty_age_190 >= 105.0:
        empty_190_str = "105+ (חסין)"
    else:
        empty_190_str = f"גיל {empty_age_190:.1f}"

    if empty_age_25 >= 105.0:
        empty_25_str = "105+ (חסין)"
    else:
        empty_25_str = f"גיל {empty_age_25:.1f}"

    # --- טבלה 1 ---
    st.subheader(f"📊 מצב בגיל פרישה (גיל {start_age})")
    df_start_table = pd.DataFrame({
        "שאלה": ["עם כמה כסף אני מתחיל פרישה בתיק?", "מה שווי הנדלן שלי?", "גובה קצבאות", "כמה כסף נטו אצטרך למשוך מהתיק בכל חודש?", "קצב המשיכה באחוזים בפרישה?", "מה שווי כלל הנכסים שלי (הון + נדלן)?"],
        "מסלול תיקון 190": [format_shekel(initial_capital_190), format_shekel(property_value_start), format_shekel(inc_start + pension_190_start), f"-{format_shekel(net_needed_190_start)}", f"{pct_190_start:.2f}%", format_shekel(total_wealth_190_start)],
        "מסלול 25% מס ריאלי": [format_shekel(initial_capital_25), format_shekel(property_value_start), format_shekel(inc_start), f"-{format_shekel(net_needed_25_start)}", f"{pct_25_start:.2f}%", format_shekel(total_wealth_25_start)]
    })
    st.table(df_start_table.set_index("שאלה"))

    # --- טבלה 2 ---
    st.subheader(f"🔮 מצב בגיל נבדק בסימולציה (גיל {check_age})")
    df_check_table = pd.DataFrame({
        "שאלה": ["כמה כסף נטו אצטרך למשוך מהתיק בכל חודש?", "מה שיעור המשיכה בגיל הנבדק?", "כמה כסף נזיל יישאר לי בתיק?", "מה שווי כלל הנכסים שלי (הון + נדלן)?"],
        "מסלול תיקון 190": [f"-{format_shekel(net_needed_190_check)}", f"{pct_190_check:.2f}%", format_shekel(balance_190_check), format_shekel(total_wealth_190_check)],
        "מסלול 25% מס ריאלי": [f"-{format_shekel(net_needed_25_check)}", f"{pct_25_check:.2f}%", format_shekel(balance_25_check), format_shekel(total_wealth_25_check)]
    })
    st.table(df_check_table.set_index("שאלה"))

    # --- טבלה 3 ---
    st.subheader("🏁 שורה תחתונה וחסינות אקטוארית")
    df_bottom_table = pd.DataFrame({
        "שורה תחתונה": ["עד איזה גיל הכסף יחזיק (חסינות)?", "כמה אחוז מההון ההתחלתי נשמר בגיל 97 עם מטפלת?"],
        "מסלול תיקון 190": [empty_190_str, f"{ratio_190_97:.2f}%"],
        "מסלול 25% מס ריאלי": [empty_25_str, f"{ratio_25_97:.2f}%"]
    })
    st.table(df_bottom_table.set_index("שורה תחתונה"))
