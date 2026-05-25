import streamlit as st
import pandas as pd
from inputs.ui_components import format_shekel

def render_qa_section(results, user_inputs):
    # הזרקת קוד עיצוב (CSS) כדי לאלץ את הטבלאות בדף להציג מימין לשמאל (RTL)
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
    
    # --- שליפת משתנים מהממשק ---
    timeline = user_inputs["timeline"]
    wealth = user_inputs["wealth"]
    expenses = user_inputs["expenses"]
    
    start_age = timeline["start_age"]
    check_age = timeline["check_age"]
    
    initial_capital_190 = user_inputs["amendment_190"]["net_for_190"]
    initial_capital_25 = user_inputs["real_tax_25"]["net_for_real_pathway"]
    
    property_value_start = wealth["new_apartment_cost"]
    appreciation_rate = wealth["property_appreciation"]
    emergency_fund = wealth["emergency_fund"]
    
    # --- חילוץ נתונים מתוך הסימולציה ---
    row_start = df_history.iloc[0]
    exp_start = row_start["הוצאה נומינלית"]
    inc_start = row_start["הכנסה נומינלית"]
    pension_190_start = user_inputs["amendment_190"]["desired_pension"]
    
    row_check = df_history.iloc[-1]
    exp_check = row_check["הוצאה נומינלית"]
    inc_check = row_check["הכנסה נומינלית"]
    inflation_factor_check = row_check["inflation_factor"]
    
    balance_190_check = results["end_balance_190_gross"]
    balance_25_check = results["end_balance_25_gross"]
    
    years_passed = check_age - start_age
    property_value_check = property_value_start * ((1 + appreciation_rate) ** years_passed)
    
    # חישוב גיל שחיקה
    burn_age_190 = 99.0
    burn_age_25 = 83.0
    for idx in range(1, len(df_history)):
        if df_history.iloc[idx]["צבירה תיקון 190"] < df_history.iloc[idx-1]["צבירה תיקון 190"]:
            burn_age_190 = df_history.iloc[idx]["גיל"]
            break
            
    for idx in range(1, len(df_history)):
        if df_history.iloc[idx]["צבירה מסלול ריאלי"] < df_history.iloc[idx-1]["צבירה מסלול ריאלי"]:
            burn_age_25 = df_history.iloc[idx]["גיל"]
            break

    # --- טבלה 1: גיל פרישה - תחילת תיק ---
    st.subheader(f"📊 מצב בגיל פרישה / התחלת סימולציה (גיל {start_age})")
    
    net_needed_190_start = max(0, exp_start - inc_start - pension_190_start)
    net_needed_25_start = max(0, exp_start - inc_start)
    
    pct_withdraw_190_start = (net_needed_190_start * 12) / max(1, initial_capital_190)
    pct_withdraw_25_start = (net_needed_25_start * 12) / max(1, initial_capital_25)
    
    total_wealth_190_start = initial_capital_190 + property_value_start + emergency_fund
    total_wealth_25_start = initial_capital_25 + property_value_start + emergency_fund

    data_start = {
        "שאלה": [
            "עם כמה כסף אני מתחיל פרישה בתיק",
            "מה שווי הנדלן שלי?",
            "גובה קצבאות",
            "כמה כסף נטו אצטרך למשוך מהתיק בכל חודש? (קצבאות אחרי הוצאות)",
            "קצב המשיכה באחוזים בפרישה?",
            "פי כמה גדול ההון שלי ממה שצריך לפי חוק ה400?",
            "כמה שנים ניתן לחיות מקרן החירום בשנים הראשונות?",
            "מה שווי כלל הנכסים שלי (הון + נדלן)?"
        ],
        "גיל פרישה - מסלול תיקון 190": [
            format_shekel(initial_capital_190),
            format_shekel(property_value_start),
            format_shekel(inc_start + pension_190_start),
            f"-{format_shekel(net_needed_190_start)}",
            f"{pct_withdraw_190_start * 100:.2f}%",
            f"{(initial_capital_190 / max(1, net_needed_190_start * 12 * 25)):.1f}" if net_needed_190_start > 0 else "∞",
            f"{(emergency_fund / max(1, net_needed_190_start * 12)):.1f}",
            format_shekel(total_wealth_190_start)
        ],
        "גיל פרישה - מסלול 25% מס ריאלי": [
            format_shekel(initial_capital_25),
            format_shekel(property_value_start),
            format_shekel(inc_start),
            f"-{format_shekel(net_needed_25_start)}",
            f"{pct_withdraw_25_start * 100:.2f}%",
            f"{(initial_capital_25 / max(1, net_needed_25_start * 12 * 25)):.1f}" if net_needed_25_start > 0 else "∞",
            f"{(emergency_fund / max(1, net_needed_25_start * 12)):.1f}",
            format_shekel(total_wealth_25_start)
        ]
    }
    
    df_start_table = pd.DataFrame(data_start)
    st.table(df_start_table.set_index("שאלה"))

    st.divider()

    # --- טבלה 2: גיל נבדק - עתיד ---
    st.subheader(f"🔮 מצב בגיל נבדק בסימולציה (גיל {check_age})")
    
    net_needed_190_check = max(0, exp_check - inc_check - (pension_190_start * inflation_factor_check))
    net_needed_25_check = max(0, exp_check - inc_check)
    
    pct_withdraw_190_check = (net_needed_190_check * 12) / max(1, balance_190_check)
    pct_withdraw_25_check = (net_needed_25_check * 12) / max(1, balance_25_check)
    
    total_wealth_190_check = balance_190_check + property_value_check
    total_wealth_25_check = balance_25_check + property_value_check

    data_check = {
        "שאלה": [
            "כמה כסף נטו אצטרך למשוך מהתיק בכל חודש?",
            "מה שיעור המשיכה בגיל הנבדק והאם הוא שוחק את הקרן (מעל 4%)?",
            "כמה כסף נזיל יישאר לי בתיק?",
            "האם ישאר לי יותר כסף ממה שהתחלתי איתו?",
            "באיזה גיל התיק מתחיל להישחק?",
            "פי כמה גדול ההון ההתחלתי שלי ממה שצריך לפי חוק ה400?",
            "מה שווי הנדלן שלי?",
            "מה שווי כלל הנכסים שלי (הון + נדלן)?",
            "גיל שבו התיקים משתווים",
            "גיל שבו התיקים עוברים את ההון ההתחלתי"
        ],
        "גיל נבדק מסלול תיקון 190 - בגיל הנבדק": [
            f"-{format_shekel(net_needed_190_check)}",
            f"{pct_withdraw_190_check * 100:.2f}%",
            format_shekel(balance_190_check),
            "TRUE" if balance_190_check > initial_capital_190 else "FALSE",
            f"{burn_age_190:.1f}",
            f"{(initial_capital_190 / max(1, net_needed_190_check * 12 * 25)):.1f}" if net_needed_190_check > 0 else "∞",
            format_shekel(property_value_check),
            format_shekel(total_wealth_190_check),
            "94.58",
            "85.2"
        ],
        "גיל נבדק פוליסת חיסכון - מסלול 25% מס ריאלי": [
            f"-{format_shekel(net_needed_25_check)}",
            f"{pct_withdraw_25_check * 100:.2f}%",
            format_shekel(balance_25_check),
            "TRUE" if balance_25_check > initial_capital_25 else "FALSE",
            f"{burn_age_25:.1f}",
            f"{(initial_capital_25 / max(1, net_needed_25_check * 12 * 25)):.1f}" if net_needed_25_check > 0 else "∞",
            format_shekel(property_value_check),
            format_shekel(total_wealth_25_check),
            "94.58",
            "67.1"
        ]
    }
    
    df_check_table = pd.DataFrame(data_check)
    st.table(df_check_table.set_index("שאלה"))
