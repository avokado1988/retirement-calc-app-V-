import streamlit as st
from .timeline import render_timeline_inputs
from .wealth import render_wealth_inputs
from .expenses import render_expenses_inputs
from .incomes import render_incomes_inputs
from .amendment_190 import render_190_inputs
from .real_tax_25 import render_25_inputs

def render_all_sidebar_inputs():
    """מנהל את תפריט הצד ומחזיר אובייקט קלטים מאוחד"""
    st.sidebar.title("⚙️ פרמטרים ומחשבון פרישה")
    
    inputs_dict = {}
    
    with st.sidebar.expander("1. נתוני זמנים ופרישה", expanded=True):
        inputs_dict["timeline"] = render_timeline_inputs()
    
    with st.sidebar.expander("2. נתוני הון ונדל\"ן", expanded=False):
        inputs_dict["wealth"] = render_wealth_inputs()
        
    remaining_wealth = inputs_dict["wealth"]["remaining_for_gimel"]
    
    with st.sidebar.expander("3. מקורות הכנסה", expanded=False):
        incomes_ui = render_incomes_inputs()
        
    with st.sidebar.expander("4. תקציב והוצאות", expanded=False):
        expenses_ui = render_expenses_inputs()
        
    # --- הזרקת ההכנסות למקומן עבור המנוע ---
    inputs_dict["wealth"]["national_insurance"] = incomes_ui["national_insurance"]
    expenses_ui["work_income"] = incomes_ui["work_income"]
    expenses_ui["work_end_age"] = incomes_ui["work_end_age"]
    inputs_dict["expenses"] = expenses_ui
    
    with st.sidebar.expander("5. מסלול תיקון 190", expanded=False):
        inputs_dict["amendment_190"] = render_190_inputs(remaining_wealth)
        
    with st.sidebar.expander("6. מסלול 25% מס ריאלי", expanded=False):
        inputs_dict["real_tax_25"] = render_25_inputs(remaining_wealth)
        
    return inputs_dict
