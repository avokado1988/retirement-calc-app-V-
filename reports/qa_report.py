import streamlit as st
import pandas as pd
from inputs.ui_components import format_shekel

def render_qa_section(results, user_inputs):
    # הזרקת קוד עיצוב (CSS) משופר: טקסט שחור מוחלט, RTL, ועיצוב כותרות נפרד לכל טור
    st.markdown(
        """
        <style>
        .stTable, table {
            direction: rtl !important;
            text-align: right !important;
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            color: #000000 !important; /* אילוץ טקסט שחור בכל הטבלה */
        }
        th, td {
            text-align: right !important;
            direction: rtl !important;
            padding: 12px 10px !important;
            border: 1px solid #D9D9D9;
            color: #000000 !important; /* אילוץ טקסט שחור בתאים */
        }
        th {
            font-weight: bold;
            text-align: center !important;
        }
        /* צבעי רקע מותאמים אישית לכותרות הטורים לפי התמונה */
        .col-question {
            background-color: #F2F2F2;
        }
        .col-190 {
            background-color: #FFF2CC !important; /* צהבהב עדין */
            text-align: center !important;
        }
        .col-real {
            background-color: #FCE4D6 !important; /* כתמתם-אפרסק בהיר */
            text-align: center !important;
        }
        .section-header {
            background-color: #ECE6F6;
            font-weight: bold;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    df_history = results["df"]
    df_full = results["df_full"] if "df_full" in results else df_history
    
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
    
    row_start = df_history.iloc[0]
    exp_start = row_start["הוצאה נומינלית"]
    inc_start = row_start["הכנסה נומינלית"]
    pension_190_start = user_inputs["amendment_190"]["desired_pension"]
    
    # התיקון שלנו: "גיל" במקום "גily"
    row_check = df_history[df_history["גיל"] >= check_age].iloc[0] if not df_history[df_history["גיל"] >= check_age].empty else df_history.iloc[-1]
    
    exp_check = row_check["הוצאה נומינלית"]
    inc_check = row_check["הכנסה נומינלית"]
    inflation_factor_check = row_check["inflation_factor"]
    balance_190_check = row_check["צבירה תיקון 190"]
    balance_25_check = row_check["צבירה מסלול ריאלי"]
    
    years_passed = check_age - start_age
    property_value_check = property_value_start * ((1 + appreciation_rate) ** years_passed)
    
    burn_age_190, burn_age_25 = 99.0, 83.0
    empty_age_190, empty_age_25 = 120.0, 120.0
    
    for idx in range(1, len(df_full)):
        if df_full.iloc[idx]["צבירה תיקון 190"] < df_full.iloc[idx-1]["צבירה תיקון 190"]:
            burn_age_190 = df_full.iloc[idx]["גיל"]
            break
    for idx in range(1, len(df_full)):
        if df_full.iloc[idx]["צבירה מסלול ריאלי"] < df_full.iloc[idx-1]["צבירה מסלול ריאלי"]:
            burn_age_25 = df_full.iloc[idx]["גיל"]
            break
            
    for idx in range(len(df_full)):
        if df_full.iloc[idx]["צבירה תיקון 190"] <= 0:
            empty_age_190 = df_full.iloc[idx]["גיל"]
            break
    for idx in range(len(df_full)):
        if df_full.iloc[idx]["צבירה מסלול ריאלי"] <= 0:
            empty_age_25 = df_full.iloc[idx]["גיל"]
            break

    ratio_190_97 = results.get("ratio_190_97", 0.0)
    ratio_25_97 = results.get("ratio_25_97", 0.0)
