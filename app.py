import streamlit as st

# ==============================================================================
# 🪄 מנגנון שמירה אוטומטית בדפדפן בזמן אמת (URL Query Parameters)
# ==============================================================================
# טעינה ראשונית מהדפדפן לתוך הזיכרון של האפליקציה (קורה רק בטעינת הדף)
if "initialized" not in st.session_state:
    for k in list(st.query_params.keys()):
        if k.startswith("saved_"):
            val_str = st.query_params[k]
            try:
                if '.' in val_str:
                    st.session_state[k] = float(val_str)
                else:
                    st.session_state[k] = int(val_str)
            except ValueError:
                st.session_state[k] = val_str
    st.session_state["initialized"] = True

_orig_slider = st.slider
_orig_number_input = st.number_input

def patched_slider(label, *args, **kwargs):
    widget_key = f"saved_slider_{label}"
    kwargs["key"] = widget_key
    if widget_key in st.session_state:
        kwargs["value"] = st.session_state[widget_key]
        
    val = _orig_slider(label, *args, **kwargs)
    # הזרקה ישירה לכתובת הדפדפן בזמן אמת
    st.query_params[widget_key] = str(val)
    return val

def patched_number_input(label, *args, **kwargs):
    widget_key = f"saved_num_{label}"
    kwargs["key"] = widget_key
    if widget_key in st.session_state:
        kwargs["value"] = st.session_state[widget_key]
        
    val = _orig_number_input(label, *args, **kwargs)
    # הזרקה ישירה לכתובת הדפדפן בזמן אמת
    st.query_params[widget_key] = str(val)
    return val

# חטיפת הרכיבים הגלובלית
st.slider = patched_slider
st.number_input = patched_number_input
# ==============================================================================

import inputs
from simulator_engine import run_simulation
from reports.graphs import render_charts
from reports.qa_report import render_qa_section
from reports.qa_summary import render_qa_summary_page

# 1. הגדרת תצורת דף אחידה
st.set_page_config(page_title="מחשבון פרישה אקטוארי חכם", page_icon="📊", layout="wide")

st.title("📊 סימולטור פרישה השוואתי - Gold Standard")
st.markdown("המערכת מנתחת את עוגת ההון ומציגה השוואה אקטוארית בין מסלול תיקון 190 למסלול 25% מס ריאלי.")
st.divider()

# ==============================================================================
# 🗑️ כפתור איפוס נתונים בדפדפן (כדי להתחיל לקוח חדש מאפס)
# ==============================================================================
st.sidebar.title("🧹 ניהול זיכרון דפדפן")
if st.sidebar.button("🗑️ נקה נתונים וחזור לברירת מחדל", use_container_width=True):
    # מחיקת הפרמטרים מכתובת הדפדפן
    for k in list(st.query_params.keys()):
        if k.startswith("saved_"):
            del st.query_params[k]
    # מחיקת הפרמטרים מזיכרון
