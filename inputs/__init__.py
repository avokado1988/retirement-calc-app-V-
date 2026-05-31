import streamlit as st
from .timeline import render_timeline_inputs
from .wealth import render_wealth_inputs
from .expenses import render_expenses_inputs
from .incomes import render_incomes_inputs
from .amendment_190 import render_190_inputs
from .real_tax_25 import render_25_inputs
from .rental import render_rental_inputs

def render_all_sidebar_inputs():
    """מנהל את תפריט הצד ומחזיר אובייקט קלטים מאוחד"""
    st.sidebar.title("⚙️ פרמטרים ומחשבון פרישה")

    inputs_dict = {}

    st.sidebar.markdown("#### 🎯 הגדרות בסיס")

    with st.sidebar.expander("1. נתוני זמנים ופרישה", expanded=True):
        inputs_dict["timeline"] = render_timeline_inputs()

    with st.sidebar.expander("2. נתוני הון ונדל\"ן", expanded=False):
        inputs_dict["wealth"] = render_wealth_inputs()

    remaining_wealth = inputs_dict["wealth"]["remaining_for_gimel"]

    with st.sidebar.expander("3. מקורות הכנסה וקצבה", expanded=False):
        incomes_ui = render_incomes_inputs(remaining_wealth)

    with st.sidebar.expander("4. תקציב והוצאות", expanded=False):
        expenses_ui = render_expenses_inputs()

    # Wire incomes back into the unified inputs dict
    inputs_dict["wealth"]["national_insurance"] = incomes_ui["national_insurance"]
    expenses_ui["work_income"] = incomes_ui["work_income"]
    expenses_ui["work_end_age"] = incomes_ui["work_end_age"]
    inputs_dict["expenses"] = expenses_ui

    st.sidebar.divider()
    st.sidebar.markdown("#### 🔧 הגדרות מתקדמות — מסלולים")

    capital_for_pension = incomes_ui.get("capital_for_pension", 0)

    with st.sidebar.expander("5. מסלול 1 — תיקון 190", expanded=False):
        a190 = render_190_inputs(remaining_wealth, capital_for_pension)
        # Inject pension data from incomes
        a190["desired_pension"]      = incomes_ui["desired_pension"]
        a190["securing_years"]       = incomes_ui["securing_years"]
        a190["base_coefficient"]     = incomes_ui["base_coefficient"]
        a190["adjusted_coefficient"] = incomes_ui["adjusted_coefficient"]
        a190["capital_for_pension"]  = capital_for_pension
        inputs_dict["amendment_190"] = a190

    with st.sidebar.expander("6. מסלולים 2 ו-3 — 25% מס ריאלי", expanded=False):
        inputs_dict["real_tax_25"] = render_25_inputs(remaining_wealth)

    # net_for_hybrid = same capital as track 1 after pension purchase
    inputs_dict["real_tax_25"]["net_for_hybrid"] = inputs_dict["amendment_190"].get("net_for_190", 0)

    with st.sidebar.expander("7. מסלול 4 — השכרת הנכס", expanded=False):
        inputs_dict["rental"] = render_rental_inputs(inputs_dict["wealth"])

    return inputs_dict
