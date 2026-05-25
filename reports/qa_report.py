import streamlit as st
import pandas as pd
from inputs.ui_components import format_shekel

def render_qa_section(results, user_inputs):
    # הזרקת קוד עיצוב (CSS) לתמיכה ב-RTL, אילוץ יישור לימין ועיצוב אחיד לטבלאות
    st.markdown(
        """
        <style>
        .stTable, table {
            direction: rtl !important;
            text-align: right !important;
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        th, td {
            text-align: right !important;
            direction: rtl !important;
            padding: 12px 10px !important;
            border: 1px solid #E0E0E0;
        }
        thead tr {
            background-color: #ECE6F6;
        }
        th {
            font-weight: bold;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    df_history = results["df"]
    
    # --- שליפת משתנים מהממשק ---
    timeline = user_inputs["timeline"]
    wealth = user_inputs["wealth"]
    expenses = user_inputs["expenses"]
    
    start_age = timeline["start_age"]
    check_age = timeline["check_age"]
    
    initial_capital_190 = user_inputs["amendment_190"]["net_for_190"]
    initial_capital_25 = user_inputs["real_tax_25"]["net_for_real_pathway"]
    base_initial_capital = wealth["remaining_for_gimel"]
    
    property_value_start = wealth["new_apartment_cost"]
    appreciation_rate = wealth["property_appreciation"]
    emergency_fund = wealth["emergency_fund"]
    
    # --- חילוץ נתונים מתוך הסימולציה ---
    row_start = df_history.iloc[0]
    exp_start = row_start["הוצאה נומינלית"]
    inc_start = row_start["הכנסה נומינלית"]
    pension_190_start = user_inputs["amendment_190"]["desired_pension"]
    
    row_check = df_history[df_history["גיל"] >= check_age].iloc[0] if not df_history[df_history["גיל"] >= check_age].empty else df_history.iloc[-1]
    exp_check = row_check["הוצאה נומינלית"]
    inc_check = row_check["הכנסה נומינלית"]
    inflation_factor_check = row_check["inflation_factor"]
    balance_190_check = row_check["צבירה תיקון 190"]
    balance_25_check = row_check["צבירה מסלול ריאלי"]
    
    years_passed = check_age - start_age
    property_value_check = property_value_start * ((1 + appreciation_rate) ** years_passed)
    
    # חישוב גילאי שחיקה והתרוקנות
    burn_age_190, burn_age_25 = 99.0, 83.0
    empty_age_190, empty_age_25 = 120.0, 120.0
    
    for idx in range(1, len(df_history)):
        if df_history.iloc[idx]["צבירה תיקון 190"] < df_history.iloc[idx-1]["צבירה תיקון 190"]:
            burn_age_190 = df_history.iloc[idx]["גיל"]
            break
    for idx in range(1, len(df_history)):
        if df_history.iloc[idx]["צבירה מסלול ריאלי"] < df_history.iloc[idx-1]["צבירה מסלול ריאלי"]:
            burn_age_25 = df_history.iloc[idx]["גיל"]
            break
            
    for idx in range(len(df_history)):
        if df_history.iloc[idx]["צבירה תיקון 190"] <= 0:
            empty_age_190 = df_history.iloc[idx]["גיל"]
            break
    for idx in range(len(df_history)):
        if df_history.iloc[idx]["צבירה מסלול ריאלי"] <= 0:
            empty_age_25 = df_history.iloc[idx]["גיל"]
            break

    # חילוץ ההון המדויק בגיל 97 לצורך שורה 75
    row_97 = df_history[df_history["גיל"] >= 97.0]
    balance_190_97 = row_97.iloc[0]["צבירה תיקון 190"] if not row_97.empty else 0.0
    balance_25_97 = row_97.iloc[0]["צבירה מסלול ריאלי"] if not row_97.empty else 0.0
    
    ratio_190_97 = balance_190_97 / max(1, base_initial_capital)
    ratio_25_97 = balance_25_97 / max(1, base_initial_capital)

    # --- פונקציות עזר לצבעי רמזור (Conditional Formatting) ---
    def color_withdraw_rate(rate):
        return "#99FF99" if rate <= 0.04 else "#FF9999"  # ירוק בטוח או אדום סיכון

    def color_boolean(val_bool):
        return "#99FF99" if val_bool else "#FF9999"  # ירוק ל-TRUE, אדום ל-FALSE

    def color_rule_400(val_factor):
        return "#99FF99" if val_factor >= 1.0 else "#FF9999"  # ירוק לחסין, אדום לשברירי

    def get_color_for_ratio(ratio):
        if ratio >= 0.90: return "#99FF99"   # ירוק עז
        if ratio >= 0.75: return "#FFCC99"   # כתום/צהוב בהיר
        return "#FF9999"                     # אדום בהיר

    # --- טבלה 1: גיל פרישה ---
    st.subheader(f"📊 מצב בגיל פרישה / התחלת סימולציה (גיל {start_age})")
    net_needed_190_start = max(0, exp_start - inc_start - pension_190_start)
    net_needed_25_start = max(0, exp_start - inc_start)
    pct_withdraw_190_start = (net_needed_190_start * 12) / max(1, initial_capital_190)
    pct_withdraw_25_start = (net_needed_25_start * 12) / max(1, initial_capital_25)
    total_wealth_190_start = initial_capital_190 + property_value_start + emergency_fund
    total_wealth_25_start = initial_capital_25 + property_value_start + emergency_fund

    data_start = {
        "שאלה": ["עם כמה כסף אני מתחיל פרישה בתיק", "מה שווי הנדלן שלי?", "גובה קצבאות", "כמה כסף נטו אצטרך למשוך מהתיק בכל חודש? (קצבאות אחרי הוצאות)", "קצב המשיכה באחוזים בפרישה?", "פי כמה גדול ההון שלי ממה שצריך לפי חוק ה400?", "כמה שנים ניתן לחיות מקרן החירום בשנים הראשונות?", "מה שווי כלל הנכסים שלי (הון + נדלן)?"],
        "גיל פרישה - מסלול תיקון 190": [format_shekel(initial_capital_190), format_shekel(property_value_start), format_shekel(inc_start + pension_190_start), f"-{format_shekel(net_needed_190_start)}", f"{pct_withdraw_190_start * 100:.2f}%", f"{(initial_capital_190 / max(1, net_needed_190_start * 12 * 25)):.1f}" if net_needed_190_start > 0 else "∞", f"{(emergency_fund / max(1, net_needed_190_start * 12)):.1f}", format_shekel(total_wealth_190_start)],
        "גיל פרישה - מסלול 25% מס ריאלי": [format_shekel(initial_capital_25), format_shekel(property_value_start), format_shekel(inc_start), f"-{format_shekel(net_needed_25_start)}", f"{pct_withdraw_25_start * 100:.2f}%", f"{(initial_capital_25 / max(1, net_needed_25_start * 12 * 25)):.1f}" if net_needed_25_start > 0 else "∞", f"{(emergency_fund / max(1, net_needed_25_start * 12)):.1f}", format_shekel(total_wealth_25_start)]
    }
    st.table(pd.DataFrame(data_start).set_index("שאלה"))

    # --- טבלה 2: גיל נבדק עם מערכת רמזורים מלאה (HTML) ---
    st.subheader(f"🔮 מצב בגיל נבדק בסימולציה (גיל {check_age})")
    
    net_needed_190_check = max(0, exp_check - inc_check - (pension_190_start * inflation_factor_check))
    net_needed_25_check = max(0, exp_check - inc_check)
    
    pct_withdraw_190_check = (net_needed_190_check * 12) / max(1, balance_190_check) if balance_190_check > 0 else 1.0
    pct_withdraw_25_check = (net_needed_25_check * 12) / max(1, balance_25_check) if balance_25_check > 0 else 1.0
    
    bool_preserve_190 = balance_190_check > initial_capital_190
    bool_preserve_25 = balance_25_check > initial_capital_25
    
    rule_400_190 = (initial_capital_190 / max
