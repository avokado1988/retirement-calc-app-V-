import streamlit as st
# ייבוא הפונקציות מכל ארבעת הקבצים שיצרת בתיקייה
from inputs.wealth import render_wealth_inputs
from inputs.expenses import render_expenses_inputs
from inputs.amendment_190 import render_190_inputs
from inputs.real_tax_25 import render_25_inputs

def render_all_sidebar_inputs():
    """מנהל את תפריט הצד ומחזיר אובייקט קלטים מאוחד"""
    st.sidebar.title("⚙️ פרמטרים ומחשבון פרישה")
    
    inputs_dict = {}
    
    # 1. קריאה לסליידרים של נתוני הון ונדל"ן
    with st.sidebar.expander("1. נתוני הון ונדל\"ן", expanded=True):
        inputs_dict["wealth"] = render_wealth_inputs()
        
    # 2. קריאה לסליידרים של תקציב והוצאות
    with st.sidebar.expander("2. תקציב והוצאות", expanded=False):
        inputs_dict["expenses"] = render_expenses_inputs()
        
    # 3. קריאה לסליידרים של מסלול תיקון 190 (מקבל את ההון הנותר מהשלב הראשון)
    with st.sidebar.expander("3. מסלול תיקון 190", expanded=False):
        remaining_wealth = inputs_dict["wealth"]["remaining_for_gimel"]
        inputs_dict["amendment_190"] = render_190_inputs(remaining_wealth)
        
    # 4. קריאה לסליידרים של מסלול 25% מס ריאלי
    with st.sidebar.expander("4. מסלול 25% מס ריאלי", expanded=False):
        inputs_dict["real_tax_25"] = render_25_inputs()
        
    return inputs_dict
