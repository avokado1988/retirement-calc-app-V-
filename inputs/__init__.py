import streamlit as st
from .timeline import render_timeline_inputs
from .wealth import render_wealth_inputs
from .expenses import render_expenses_inputs
from .amendment_190 import render_190_inputs
from .real_tax_25 import render_25_inputs

def render_all_sidebar_inputs():
    """מנהל את תפריט הצד ומחזיר אובייקט קלטים מאוחד"""
    st.sidebar.title("⚙️ פרמטרים ומחשבון פרישה")
    
    inputs_dict = {}
    
    # 1. קריאה לסליידרים של זמנים וגילאים
    with st.sidebar.expander("1. נתוני זמנים ופרישה", expanded=True):
        inputs_dict["timeline"] = render_timeline_inputs()
    
    # 2. קריאה לסליידרים של נתוני הון ונדל"ן
    with st.sidebar.expander("2. נתוני הון ונדל\"ן", expanded=False):
        inputs_dict["wealth"] = render_wealth_inputs()
        
    # שמירת נתון ההון ההתחלתי המחושב לשימוש במסלולים השונים
    remaining_wealth = inputs_dict["wealth"]["remaining_for_gimel"]
        
    # 3. קריאה לסליידרים של תקציב והוצאות
    with st.sidebar.expander("3. תקציב והוצאות", expanded=False):
        inputs_dict["expenses"] = render_expenses_inputs()
        
    # 4. קריאה לסליידרים של מסלול תיקון 190 (מעבירים את ההון)
    with st.sidebar.expander("4. מסלול תיקון 190", expanded=False):
        inputs_dict["amendment_190"] = render_190_inputs(remaining_wealth)
        
    # 5. קריאה לסליידרים של מסלול 25% מס ריאלי (התיקון: מעבירים את ההון גם כאן!)
    with st.sidebar.expander("5. מסלול 25% מס ריאלי", expanded=False):
        inputs_dict["real_tax_25"] = render_25_inputs(remaining_wealth)
        
    return inputs_dict
