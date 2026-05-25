import streamlit as st
import pandas as pd
from inputs.ui_components import format_shekel

def render_qa_section(results, user_inputs):
    # CSS בטוח שחל אך ורק על המחלקה custom-table ולא שובר את האתר
    st.markdown(
        """
        <style>
        .custom-table {
            direction: rtl !important;
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 25px;
            font-size: 16px;
        }
        .custom-table th, .custom-table td {
            border: 1px solid #C0C0C0 !important;
            padding: 10px !important;
            text-align: right !important;
            direction: rtl !important;
            color: #000000 !important; /* טקסט שחור מובטח */
        }
        .custom-table th {
            font-weight: bold;
            text-align: center !important;
        }
        /* צבעי הטורים */
        .bg-question { background-color: #F2F2F2 !important; }
        .bg-190 { background-color: #FFF2CC !important; text-align: center !important; }
        .bg-real { background-color: #FCE4D6 !important; text-align: center !important; }
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
    
    # חיפוש בטוח של השורה לגיל הנבדק
    filtered_df = df_
