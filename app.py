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

def _build_defaults_dict(ui):
    """Map the current inputs back to the DEFAULTS keys (single source of truth)."""
    tl = ui.get("timeline", {}); ex = ui.get("expenses", {}); w = ui.get("wealth", {})
    a190 = ui.get("amendment_190", {}); rt = ui.get("real_tax_25", {}); rn = ui.get("rental", {})
    return {
        "start_age": tl.get("start_age", 65.0),
        "retirement_age": tl.get("retirement_age", 65.0),
        "check_age": tl.get("check_age", 95.0),
        "expected_inflation": ex.get("expected_inflation", 0.023),
        "current_expenses": int(ex.get("current_expenses", 11000)),
        "caregiver_cost": int(ex.get("caregiver_cost", 2500)),
        "one_time_expense": int(ex.get("one_time_expense", 80000)),
        "one_time_frequency": int(ex.get("one_time_frequency", 8)),
        "age_75_85_increase": ex.get("age_75_85_increase", 0.0),
        "age_85_plus_increase": ex.get("age_85_plus_increase", 0.0),
        "work_income": int(ex.get("work_income", 0)),
        "national_insurance": int(w.get("national_insurance", 2500)),
        "desired_pension": int(a190.get("desired_pension", 5306)),
        "securing_years": int(a190.get("securing_years", 20)),
        "base_coefficient": a190.get("base_coefficient", 200.0),
        "annual_return": rt.get("annual_return_25", 0.07),
        "management_fee": rt.get("management_fee_25", 0.006),
        "management_fee_190": a190.get("management_fee_190", 0.0055),
        "net_sale": int(w.get("net_sale", 9200000)),
        "existing_savings": int(w.get("existing_savings", 440000)),
        "new_apartment_cost": int(w.get("new_apartment_cost", 5600000)),
        "kids_help": int(w.get("kids_help", 1000000)),
        "emergency_fund": int(w.get("emergency_fund", 250000)),
        "property_appreciation": w.get("property_appreciation", 0.03),
        "rental_property_value": int(rn.get("current_property_value", 10800000)),
        "rental_property_appreciation": rn.get("rental_property_appreciation", 0.023),
        "rental_income_monthly": int(rn.get("rental_income_monthly", 25000)),
        "rental_income_growth_rate": rn.get("rental_income_growth_rate", 0.035),
        "rent_paid_monthly": int(rn.get("rent_paid_monthly", 12000)),
        "rent_paid_growth_rate": rn.get("rent_paid_growth_rate", 0.035),
        "rental_tax_rate": rn.get("rental_tax_rate", 0.1),
        "maintenance_early_pct": rn.get("maintenance_early_pct", 0.06),
        "maintenance_late_pct": rn.get("maintenance_late_pct", 0.1),
        "rm_annual_rate": 0.06,
        "rm_savings_floor": 100000,
    }

def _render_defaults_block(d):
    def fmt(v):
        return repr(round(v, 6)) if isinstance(v, float) else repr(v)
    lines = ",\n".join(f'    "{k}": {fmt(v)}' for k, v in d.items())
    return "DEFAULTS = {\n" + lines + ",\n}"

def _save_defaults_to_github(ui):
    """Write the current values into DEFAULTS in inputs/ui_components.py on GitHub."""
    import base64, re, requests
    try:
        token = st.secrets.get("github_token", "")
    except Exception:
        token = ""
    if not token:
        return False, "לא הוגדר טוקן. הוסף github_token תחת Settings ← Secrets של האפליקציה."
    owner  = st.secrets.get("github_owner", "avokado1988")
    repo   = st.secrets.get("github_repo", "retirement-calc-app-V-")
    branch = st.secrets.get("github_branch", "BugFix-July-5-V5")
    path = "inputs/ui_components.py"
    api = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    r = requests.get(api, headers=headers, params={"ref": branch}, timeout=20)
    if r.status_code != 200:
        return False, f"קריאת הקובץ מגיטהאב נכשלה ({r.status_code})."
    sha = r.json()["sha"]
    content = base64.b64decode(r.json()["content"]).decode("utf-8")
    new_block = _render_defaults_block(_build_defaults_dict(ui))
    new_content, n = re.subn(r"DEFAULTS\s*=\s*\{.*?\n\}", new_block, content, count=1, flags=re.DOTALL)
    if n == 0:
        return False, "לא נמצא בלוק DEFAULTS בקובץ."
    if new_content == content:
        return True, "אין שינוי — הערכים כבר שמורים בקוד."
    put = requests.put(api, headers=headers, timeout=20, json={
        "message": "chore: update DEFAULTS from app save",
        "content": base64.b64encode(new_content.encode("utf-8")).decode("ascii"),
        "sha": sha, "branch": branch,
    })
    if put.status_code in (200, 201):
        return True, "נשמר לקוד ונדחף לגיטהאב. האפליקציה תתעדכן אוטומטית תוך כדקה."
    return False, f"הדחיפה נכשלה ({put.status_code})."

if st.sidebar.button("💾 שמור נתונים אלו כברירת מחדל", use_container_width=True):
    _ok, _msg = _save_defaults_to_github(user_inputs)
    (st.sidebar.success if _ok else st.sidebar.error)(("✅ " if _ok else "⚠️ ") + _msg)

if run_clicked or "sim_results" not in st.session_state:
    with st.spinner("⏳ מחשב סימולציה אקטוארית — חודש בחודשו עד גיל 105..."):
        st.session_state["sim_results"] = run_simulation(user_inputs)
        st.session_state["last_inputs"] = user_inputs
    if run_clicked:
        st.toast("✅ הסימולציה עודכנה בהצלחה!", icon="✅")

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
        cols = COMMON_COLS + ["הכנסת שכירות נטו", "הוצאת שכירות", "הוצאת תחזוקה", "הוצאות מטפלת", "תזרים נטו שכירות", "צבירה מסלול שכירות", "משיכה מתיק שכירות", "מס רווח הון — משיכה מתיק", "שווי נדלן מסלול 4"]
        fmt  = {**COMMON_FMT, "הכנסת שכירות נטו": "{:,.0f} ₪", "הוצאת שכירות": "{:,.0f} ₪",
                "הוצאת תחזוקה": "{:,.0f} ₪", "הוצאות מטפלת": "{:,.0f} ₪",
                "תזרים נטו שכירות": "{:,.0f} ₪", "צבירה מסלול שכירות": "{:,.0f} ₪",
                "משיכה מתיק שכירות": "{:,.0f} ₪",
                "מס רווח הון — משיכה מתיק": "{:,.0f} ₪", "שווי נדלן מסלול 4": "{:,.0f} ₪"}
        if "משכנתה הפוכה — יתרת חוב" in df_display.columns and (df_display["משכנתה הפוכה — יתרת חוב"] > 0).any():
            cols += ["משכנתה הפוכה — משיכה חודשית", "משכנתה הפוכה — יתרת חוב", "משכנתה הפוכה — הון עצמי", "משכנתה הפוכה — LTV"]
            fmt.update({
                "משכנתה הפוכה — משיכה חודשית": "{:,.0f} ₪",
                "משכנתה הפוכה — יתרת חוב": "{:,.0f} ₪",
                "משכנתה הפוכה — הון עצמי": "{:,.0f} ₪",
                "משכנתה הפוכה — LTV": "{:.1%}",
            })
        st.dataframe(df_display[[c for c in cols if c in df_display.columns]].style.format(fmt), use_container_width=True)

with tab4:
    render_qa_summary_page(sim_results, display_inputs)
