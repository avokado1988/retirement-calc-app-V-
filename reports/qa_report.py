import streamlit as st
import pandas as pd
from inputs.ui_components import format_shekel

def render_qa_section(results, user_inputs):
    # --- הזרקת CSS בטוחה לחלוטין ליישור מימין לשמאל (RTL) ---
    st.markdown(
        """
        <style>
        .stTable, table {
            direction: rtl !important;
            text-align: right !important;
        }
        th, td {
            text-align: right !important;
            direction: rtl !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    df_history = results["df"]
    
    timeline = user_inputs["timeline"]
    wealth = user_inputs["wealth"]
    
    start_age = timeline["start_age"]
    check_age = timeline["check_age"]
    
    initial_capital_190 = user_inputs["amendment_190"]["net_for_190"]
    initial_capital_25 = user_inputs["real_tax_25"]["net_for_real_pathway"]
    
    property_value_start = wealth["new_apartment_cost"]
    appreciation_rate = wealth["property_appreciation"]
    emergency_fund = wealth["emergency_fund"]
    
    row_start = df_history.iloc[0]
    exp_start = row_start["הוצאה נומינלית"]
    inc_start = row_start["הכנסה נומינלית"]
    pension_190_start = user_inputs["amendment_190"]["desired_pension"]
    
    df_filtered = df_history[df_history["גיל"] >= check_age]
    if not df_filtered.empty:
        row_check = df_filtered.iloc[0]
    else:
        row_check = df_history.iloc[-1]
        
    exp_check = row_check["הוצאה נומינלית"]
    inc_check = row_check["הכנסה נומינלית"]
    balance_190_check = row_check["צבירה תיקון 190"]
    balance_25_check = row_check["צבירה מסלול ריאלי"]
    
    years_passed = check_age - start_age
    property_value_check = property_value_start * ((1 + appreciation_rate) ** years_passed)
    
    # חישובי טבלה 1
    net_needed_190_start = max(0, exp_start - inc_start - pension_190_start)
    net_needed_25_start = max(0, exp_start - inc_start)
    
    pct_190_start = (net_needed_190_start * 12) / max(1, initial_capital_190) * 100
    pct_25_start = (net_needed_25_start * 12) / max(1, initial_capital_25) * 100
    
    total_wealth_190_start = initial_capital_190 + property_value_start + emergency_fund
    total_wealth_25_start = initial_capital_25 + property_value_start + emergency_fund

    # חישובי טבלה 2
    net_needed_190_check = max(0, exp_check - inc_check - pension_190_start)
    net_needed_25_check = max(0, exp_check - inc_check)
    
    pct_190_check = (net_needed_190_check * 12) / max(1, balance_190_check) * 100 if balance_190_check > 0 else 0
    pct_25_check = (net_needed_25_check * 12) / max(1, balance_25_check) * 100 if balance_25_check > 0 else 0
    
    total_wealth_190_check = balance_190_check + property_value_check
    total_wealth_25_check = balance_25_check + property_value_check

    # חישובי טבלה 3
    ratio_190_97 = results.get("ratio_190_97", 0.0) * 100
    ratio_25_97 = results.get("ratio_25_97", 0.0) * 100

    # בניית טבלאות
    st.subheader(f"📊 מצב בגיל פרישה (גיל {start_age})")
    df_start_table = pd.DataFrame({
        "שאלה": [
            "עם כמה כסף אני מתחיל פרישה בתיק?",
            "מה שווי הנדלן שלי?",
            "גובה קצבאות",
            "כמה כסף נטו אצטרך למשוך מהתיק בכל חודש?",
            "קצב המשיכה באחוזים בפרישה?",
            "מה שווי כלל הנכסים שלי (הון + נדלן)?"
        ],
        "מסלול תיקון 190": [
            format_shekel(initial_capital_190),
            format_shekel(property_value_start),
            format_shekel(inc_start + pension_190_start),
            "-" + format_shekel(net_needed_190_start),
            str(round(pct_190_start, 2)) + "%",
            format_shekel(total_wealth_1
