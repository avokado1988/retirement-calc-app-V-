import streamlit as st

def format_shekel(val):
    """מפרמט מספר לשקלים עם פסיקים: ₪1,000,000"""
    return f"₪{int(val):,}"

def format_percent(val_decimal):
    """מפרמט שבר עשרוני לאחוז: 2.3%"""
    return f"{val_decimal * 100:.1f}%"

def show_net_summary(title, amount):
    """מציג את קוביית הסיכום הירוקה האחידה בכל המסלולים"""
    st.success(f"💰 **{title}:** {format_shekel(amount)}")
