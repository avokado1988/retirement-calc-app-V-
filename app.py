# ==============================================================================
# 🪄 מנגנון שמירה אוטומטית בדפדפן בזמן אמת (URL Query Parameters)
# ==============================================================================
if "initialized" not in st.session_state:
    for k in list(st.query_params.keys()):
        if k.startswith("saved_"):
            val_str = st.query_params[k]
            try:
                if '.' in val_str: st.session_state[k] = float(val_str)
                else: st.session_state[k] = int(val_str)
            except ValueError: st.session_state[k] = val_str
    st.session_state["initialized"] = True

# 🟢 נעילת הרקורסיה: שומרים את הפונקציות המקוריות של סטרימליט פעם אחת בלבד תחת שמות ייחודיים
if "original_funcs_cached" not in st.session_state:
    st.session_state["_raw_streamlit_slider"] = st.slider
    st.session_state["_raw_streamlit_number_input"] = st.number_input
    st.session_state["original_funcs_cached"] = True

def patched_slider(label, *args, **kwargs):
    widget_key = f"saved_slider_{label}"
    kwargs["key"] = widget_key
    if widget_key in st.session_state:
        kwargs["value"] = st.session_state[widget_key]
        
    val = st.session_state["_raw_streamlit_slider"](label, *args, **kwargs)
    st.query_params[widget_key] = str(val)
    return val

def patched_number_input(label, *args, **kwargs):
    widget_key = f"saved_num_{label}"
    kwargs["key"] = widget_key
    if widget_key in st.session_state:
        kwargs["value"] = st.session_state[widget_key]
        
    val = st.session_state["_raw_streamlit_number_input"](label, *args, **kwargs)
    st.query_params[widget_key] = str(val)
    return val

# הזרקת הפונקציות המוגנות למנוע של סטרימליט
st.slider = patched_slider
st.number_input = patched_number_input
# ==============================================================================
