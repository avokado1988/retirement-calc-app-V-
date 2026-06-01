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

st.markdown("<h1 style='text-align: center;'>📊 סימולטור פרישה השוואתי</h1>", unsafe_allow_html=True)
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
    # מחיקת הפרמטרים מזיכרון ה-Session
    for k in list(st.session_state.keys()):
        if k.startswith("saved_"):
            del st.session_state[k]
    st.sidebar.success("הדפדפן אופס בהצלחה!")
    st.rerun()

st.sidebar.divider()
# ==============================================================================

# 2. טעינת תפריט הצד המבוזר וקבלת מילון הנתונים המאוחד
# (חייב לרוץ תמיד — כדי לשמור ערכים ב-URL)
user_inputs = inputs.render_all_sidebar_inputs()

# 3. כפתור הפעלה — הסימולציה רצה רק בלחיצה (לא על כל שינוי)
st.sidebar.divider()

# אזהרה אם יש שינויים שטרם חושבו
if "last_inputs" in st.session_state:
    import json
    try:
        current_str = json.dumps(user_inputs, default=str, sort_keys=True)
        last_str = json.dumps(st.session_state["last_inputs"], default=str, sort_keys=True)
        if current_str != last_str:
            st.sidebar.warning("⚠️ יש שינויים שלא חושבו — לחץ עדכן")
    except Exception:
        pass

run_clicked = st.sidebar.button("▶️ עדכן סימולציה", use_container_width=True, type="primary")

import json, os
_DEFAULTS_FILE = os.path.join(os.path.dirname(__file__), "user_defaults.json")
if st.sidebar.button("💾 שמור נתונים אלו כברירת מחדל", use_container_width=True):
    try:
        with open(_DEFAULTS_FILE, "w", encoding="utf-8") as f:
            json.dump(user_inputs, f, default=str, ensure_ascii=False, indent=2)
        st.sidebar.success("✅ נשמר בהצלחה!")
    except Exception as e:
        st.sidebar.error(f"שגיאה: {e}")

if run_clicked or "sim_results" not in st.session_state:
    st.session_state["sim_results"] = run_simulation(user_inputs)
    st.session_state["last_inputs"] = user_inputs

sim_results = st.session_state["sim_results"]
display_inputs = st.session_state["last_inputs"]

# 4. חלוקת המסך המרכזי ללשוניות תצוגה מקצועיות
# בדיקה אם יש מסלולים בסיכון (אוזלים לפני 105) לשם אינדיקטור ב-QA
try:
    df_full = sim_results["df_full"]
    def _track_runs_out(col):
        return any(float(v) <= 0 for v in df_full[col])
    tracks_at_risk = any([
        _track_runs_out("צבירה תיקון 190"),
        _track_runs_out("צבירה מסלול ריאלי"),
        _track_runs_out("צבירה מסלול היברידי"),
        _track_runs_out("צבירה מסלול שכירות"),
    ])
    qa_tab_label = "🔴 QA — ניתוח מסלולים" if tracks_at_risk else "🟢 QA — ניתוח מסלולים"
except Exception:
    qa_tab_label = "🔬 QA — ניתוח מסלולים"

tab4, tab3, tab2, tab1 = st.tabs(["📋 העתקה מהירה לבדיקות", "📋 טבלת נתונים מלאה", "📈 גרפים השוואתיים", qa_tab_label])

with tab1:
    render_qa_section(sim_results, display_inputs)

with tab2:
    render_charts(sim_results["df_full"], display_inputs)

with tab3:
    st.subheader("🔍 גיליון סימולציה חודשי מלא (חודש-בחודשו)")
    st.markdown("ניתן לסקור כאן את כל שלבי החישוב, גילום המס וההצמדות כפי שבוצעו במנוע:")

    df_display = sim_results["df"]

    COMMON_COLS = ["גיל", "הוצאה נומינלית", "הכנסה נומינלית"]
    COMMON_FMT  = {"גיל": "{:.2f}", "הוצאה נומינלית": "{:,.0f} ₪", "הכנסה נומינלית": "{:,.0f} ₪"}

    track_tabs = st.tabs(["📘 מסלול 1 — תיקון 190", "📗 מסלול 2 — 25% ריאלי", "📙 מסלול 3 — היברידי", "📕 מסלול 4 — שכירות"])

    with track_tabs[0]:
        cols = COMMON_COLS + ["הכנסה מקצבה מזערית", "צבירה תיקון 190", "מס ששולם 190", "ערך קצבה נותר", "שווי ירושה 190", "שווי נדלן"]
        fmt  = {**COMMON_FMT, "הכנסה מקצבה מזערית": "{:,.0f} ₪", "צבירה תיקון 190": "{:,.0f} ₪",
                "מס ששולם 190": "{:,.0f} ₪", "ערך קצבה נותר": "{:,.0f} ₪",
                "שווי ירושה 190": "{:,.0f} ₪", "שווי נדלן": "{:,.0f} ₪"}
        st.dataframe(df_display[[c for c in cols if c in df_display.columns]].style.format(fmt), use_container_width=True)

    with track_tabs[1]:
        cols = COMMON_COLS + ["צבירה מסלול ריאלי", "מס ששולם 25", "שווי נדלן"]
        fmt  = {**COMMON_FMT, "צבירה מסלול ריאלי": "{:,.0f} ₪", "מס ששולם 25": "{:,.0f} ₪", "שווי נדלן": "{:,.0f} ₪"}
        st.dataframe(df_display[[c for c in cols if c in df_display.columns]].style.format(fmt), use_container_width=True)

    with track_tabs[2]:
        cols = COMMON_COLS + ["הכנסה מקצבה מזערית", "צבירה מסלול היברידי", "מס ששולם היברידי", "ערך קצבה נותר", "שווי ירושה היברידי", "שווי נדלן"]
        fmt  = {**COMMON_FMT, "הכנסה מקצבה מזערית": "{:,.0f} ₪", "צבירה מסלול היברידי": "{:,.0f} ₪",
                "מס ששולם היברידי": "{:,.0f} ₪", "ערך קצבה נותר": "{:,.0f} ₪",
                "שווי ירושה היברידי": "{:,.0f} ₪", "שווי נדלן": "{:,.0f} ₪"}
        st.dataframe(df_display[[c for c in cols if c in df_display.columns]].style.format(fmt), use_container_width=True)

    with track_tabs[3]:
        cols = COMMON_COLS + ["הכנסת שכירות נטו", "הוצאת שכירות", "צבירה מסלול שכירות", "משיכה מתיק שכירות", "מס רווח הון — משיכה מתיק", "שווי נדלן מסלול 4"]
        fmt  = {**COMMON_FMT, "הכנסת שכירות נטו": "{:,.0f} ₪", "הוצאת שכירות": "{:,.0f} ₪",
                "צבירה מסלול שכירות": "{:,.0f} ₪", "משיכה מתיק שכירות": "{:,.0f} ₪",
                "מס רווח הון — משיכה מתיק": "{:,.0f} ₪", "שווי נדלן מסלול 4": "{:,.0f} ₪"}
        st.dataframe(df_display[[c for c in cols if c in df_display.columns]].style.format(fmt), use_container_width=True)

with tab4:
    render_qa_summary_page(sim_results, display_inputs)
