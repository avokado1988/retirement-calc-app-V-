"""
המלצת תמהיל דליים ותשואה לכל מסלול, מגובה במונטה קרלו.

הרעיון. במקום שהמשתמש ינחש תשואה, אנחנו גוזרים אותה מהנתונים. לכל מסלול
מחשבים כמה מושכים מהתיק (ההוצאה פחות ההכנסה המובטחת), בונים דלי סולידי בגודל
שבע שנות משבר, והשאר מניות עד תקרה. מריצים מונטה קרלו על התמהיל ומאשרים שהוא
עומד ברף הצלחה. אם לא, מורידים סיכון עד שעובר, או מכריזים שהתכנית בסיכון.

מכיוון שהקצבה המובטחת מקטינה את המשיכה מהתיק, מסלול עם קצבה יכול להחזיק יותר
מניות ולקחת תשואה גבוהה יותר. כך המנוע חושף את היתרון המבני של הקצבה.
"""
import numpy as np

# הנחות אפיקים לפי נורמות תכנון פרישה בישראל — נומינלי, לפני דמי ניהול
CASH_RET, CASH_VOL = 0.025, 0.00
BOND_RET, BOND_VOL = 0.040, 0.05
EQ_RET,   EQ_VOL   = 0.080, 0.17

EQUITY_CAP = 0.85   # תקרת מניות שפויה לפורש
BAD_YEARS  = 7      # הדלי הסולידי מכסה שבע שנות משבר
CASH_YEARS = 2      # מתוכן, שנתיים ראשונות במזומן
GREEN      = 0.90   # רף ההצלחה לרמזור ירוק
DEFAULT_FEE = 0.005 # דמי ניהול טיפוסיים, לניכוי בבדיקת השרידות

TRACK_NAMES = {
    1: "190 + קצבה",
    2: "25% ריאלי",
    3: "היברידי",
}


def _blend(mix):
    c, b, e = mix
    ret = c * CASH_RET + b * BOND_RET + e * EQ_RET
    vol = e * EQ_VOL + b * BOND_VOL  # לינארי ושמרני (בלי הטבת פיזור), מזומן אפס
    return ret, vol


def implied_vol(gross_return):
    """גוזר סטיית תקן שנתית מהתשואה, לפי חלק המניות שנדרש כדי להשיג אותה.
    כך שהתנודתיות זזה יחד עם התשואה שהמשתמש בוחר, ולא נשארת קבועה."""
    e = (gross_return - BOND_RET) / (EQ_RET - BOND_RET)
    e = max(0.0, min(1.0, e))
    return e * EQ_VOL + (1 - e) * BOND_VOL


def _survival(P0, annual_wd, wd_growth, years, mean_ret, std_ret, n_sims=2500, seed=7):
    """מחזיר את הסתברות השרידות (התיק לא אזל עד סוף התקופה) ואת אחוזוני היתרה."""
    rng = np.random.default_rng(seed)
    rets = rng.normal(mean_ret, std_ret, size=(n_sims, years))
    P = np.full(n_sims, float(P0))
    alive = np.ones(n_sims, dtype=bool)
    wd = float(annual_wd)
    for y in range(years):
        P = P - wd
        alive &= (P > 0)
        P = np.maximum(P, 0.0) * (1 + rets[:, y])
        wd *= (1 + wd_growth)
    P_final = np.where(alive, P, 0.0)
    return (float(alive.mean()),
            float(np.percentile(P_final, 10)),
            float(np.percentile(P_final, 50)),
            float(np.percentile(P_final, 90)))


def _recommend_for_track(P0, annual_wd, wd_growth, years, fee=DEFAULT_FEE):
    if P0 <= 0 or years <= 0:
        return None

    def cum(n):
        return sum(annual_wd * (1 + wd_growth) ** k for k in range(int(n)))

    safe_need = cum(BAD_YEARS)
    cash_need = cum(CASH_YEARS)
    cash_pct = min(1.0, cash_need / P0) if P0 > 0 else 1.0
    safe_pct = min(1.0, safe_need / P0) if P0 > 0 else 1.0

    # סורקים את מלוא טווח המניות, מאפס ועד התקרה. לכל רמת מניות שומרים דלי מזומן
    # של שנתיים, והשאר אג"ח. חשוב לסרוק גם מעלה, כי במשיכה גבוהה דווקא יותר מניות
    # מעלות את סיכוי ההצלחה (צמיחה שמנצחת את המשיכה), לא רק מורידות סיכון.
    candidates = []
    eq = 0.0
    while eq <= EQUITY_CAP + 1e-9:
        e = round(min(EQUITY_CAP, eq), 4)
        c = min(cash_pct, 1.0 - e)
        b = max(0.0, 1.0 - e - c)
        mix = (c, b, e)
        ret, vol = _blend(mix)
        succ, p10, p50, p90 = _survival(P0, annual_wd, wd_growth, years, ret - fee, vol)
        candidates.append({"mix": mix, "ret": ret, "vol": vol,
                           "success": succ, "p10": p10, "p50": p50, "p90": p90})
        eq += 0.05

    # מבין התמהילים שעוברים את רף ההצלחה, בוחרים את זה שמשאיר הכי הרבה ליורשים
    # (חציון הירושה). אם אף אחד לא עובר — התכנית בסיכון, ומציגים את הטוב ביותר.
    passing = [c for c in candidates if c["success"] >= GREEN]
    if passing:
        chosen = max(passing, key=lambda c: c["p50"])
        at_risk = False
    else:
        chosen = max(candidates, key=lambda c: c["success"])
        at_risk = True

    result = dict(chosen)
    result["at_risk"] = at_risk
    result["safe_need"] = safe_need
    result["safe_pct"] = safe_pct
    result["annual_wd"] = annual_wd
    result["P0"] = P0
    result["best_success"] = max(c["success"] for c in candidates)
    return result


def compute_recommendations(user_inputs):
    """מריץ המלצה לכל מסלול הון (1,2,3,5) לפי הנתונים שהוזנו."""
    tl = user_inputs.get("timeline", {})
    ex = user_inputs.get("expenses", {})
    w = user_inputs.get("wealth", {})
    a190 = user_inputs.get("amendment_190", {})
    rt = user_inputs.get("real_tax_25", {})
    lev = user_inputs.get("leverage", {})

    start_age = float(tl.get("start_age", 67.0))
    check_age = float(tl.get("check_age", 95.0))
    years = max(1, int(round(check_age - start_age)))
    inflation = float(ex.get("expected_inflation", 0.023))
    expenses_m = float(ex.get("current_expenses", 11000))
    ni = float(w.get("national_insurance", 2500))
    pension = float(a190.get("desired_pension", 5306))

    net_190 = float(a190.get("net_for_190", 0))
    net_real = float(rt.get("net_for_real_pathway", 0))
    net_hybrid = float(rt.get("net_for_hybrid", 0))

    # משיכה חודשית מהתיק = הוצאה פחות הכנסה מובטחת (קצבה רק במסלולים עם קצבה)
    deficit_pension = max(0.0, expenses_m - ni - pension) * 12
    deficit_no_pension = max(0.0, expenses_m - ni) * 12

    # רק מסלולי ההון (1,2,3) — בהם בוחרים תמהיל דליים. מסלול 5 (מינוף) הוא מסלול
    # כללי בתשואה מקובעת ואינו בחירת תמהיל, ולכן אינו כלול בהמלצת התמהיל.
    specs = {
        1: (net_190, deficit_pension),
        2: (net_real, deficit_no_pension),
        3: (net_hybrid, deficit_pension),
    }
    out = {}
    for tid, (P0, wd) in specs.items():
        out[tid] = _recommend_for_track(P0, wd, inflation, years)
    return out, years


# ------------------------------------------------------------------
# תצוגה — כפתור, טבלת המלצה עם רמזור, וכפתור החל שממלא את שדות התשואה
# ------------------------------------------------------------------
_RETURN_FIELD_KEY = {
    1: "saved_num_תשואה שנתית צפויה — מסלול 190 (%)",
    2: "saved_num_תשואה שנתית צפויה — מסלול 2 (%)",
    3: "saved_num_תשואה שנתית צפויה — מסלול 3 (%)",
}


def _fmt(x):
    return f"₪{x:,.0f}"


def _light(rec):
    if rec.get("at_risk"):
        return "#a83232", "🔴 בסיכון"
    if rec["success"] >= GREEN:
        return "#1a7a3a", "🟢 בטוח"
    return "#b07800", "🟡 סביר"


def render_allocation_recommender(user_inputs):
    import streamlit as st

    st.markdown(
        "<div style='direction:rtl;text-align:right;'>"
        "<h3 style='color:#1a1a2e;'>🎯 המלצת תמהיל ותשואה — לפי הנתונים שלך</h3>"
        "<p style='font-size:0.95em;line-height:1.7;'>במקום לנחש תשואה, המנוע גוזר אותה "
        "מהנתונים. לכל מסלול הוא מחשב כמה מושכים מהתיק, בונה דלי סולידי שמכסה שבע שנות "
        "משבר, ומקצה את השאר למניות עד תקרה. ואז מריץ מונטה קרלו ומאשר שהתמהיל עומד "
        "במבחן המציאות.</p></div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='direction:rtl;text-align:right;background:#e7f0fb;border:1px solid #a9c9ef;"
        "border-right:4px solid #1565c0;border-radius:8px;padding:10px 14px;margin:6px 0;"
        "color:#173a5e;line-height:1.7;'>💡 ככל שהמשיכה מהתיק קטנה יותר, אפשר להחזיק יותר "
        "מניות. לכן מסלול עם קצבה מובטחת יכול לקחת תשואה גבוהה יותר ממסלול בלי קצבה, "
        "זה היתרון של הקצבה.</div>", unsafe_allow_html=True)

    if st.button("🎯 חשב תמהיל מומלץ", use_container_width=True, type="primary", key="alloc_compute_btn"):
        st.session_state["alloc_run"] = True

    if not st.session_state.get("alloc_run"):
        st.markdown(
            "<div style='direction:rtl;text-align:right;color:#777;font-size:0.9em;'>"
            "לחץ על הכפתור כדי לחשב המלצת תמהיל, תשואה וסיכוי הצלחה לכל מסלול.</div>",
            unsafe_allow_html=True)
        return

    with st.spinner("מריץ מונטה קרלו על תמהילים..."):
        recs, years = compute_recommendations(user_inputs)

    visible = set(user_inputs.get("visible_tracks", [1, 2, 3, 4, 5]))
    order = [t for t in (1, 2, 3) if t in visible and recs.get(t)]
    if not order:
        st.markdown(
            "<div style='direction:rtl;text-align:right;background:#fff8e1;border:1px solid #f0c86a;"
            "border-right:4px solid #e0a800;border-radius:8px;padding:10px 14px;color:#5a4a1a;'>"
            "אין מסלול הון פעיל להמלצה (מסלול שכירות מבוסס נדל\"ן ואינו כלול).</div>",
            unsafe_allow_html=True)
        return

    header = (
        "<tr style='background:#eef0f7;'>"
        "<th style='padding:7px 10px;text-align:right;'>מסלול</th>"
        "<th style='padding:7px 10px;'>משיכה שנתית מהתיק</th>"
        "<th style='padding:7px 10px;'>תמהיל מומלץ</th>"
        "<th style='padding:7px 10px;'>תשואה</th>"
        "<th style='padding:7px 10px;'>סטיית תקן</th>"
        "<th style='padding:7px 10px;'>טווח ירושה (גרוע→אמצעי)</th>"
        "<th style='padding:7px 10px;'>סיכוי הצלחה</th></tr>"
    )
    body = ""
    for tid in order:
        r = recs[tid]
        c, b, e = r["mix"]
        col, lbl = _light(r)
        mix_txt = f"מזומן {c*100:.0f}% · אג\"ח {b*100:.0f}% · מניות {e*100:.0f}%"
        body += (
            f"<tr style='border-bottom:1px solid #eee;'>"
            f"<td style='padding:7px 10px;text-align:right;font-weight:700;'>{TRACK_NAMES[tid]}</td>"
            f"<td style='padding:7px 10px;text-align:center;'>{_fmt(r['annual_wd'])}</td>"
            f"<td style='padding:7px 10px;text-align:center;'>{mix_txt}</td>"
            f"<td style='padding:7px 10px;text-align:center;font-weight:800;color:#1565c0;'>{r['ret']*100:.1f}%</td>"
            f"<td style='padding:7px 10px;text-align:center;color:#7e57c2;'>{r['vol']*100:.0f}%</td>"
            f"<td style='padding:7px 10px;text-align:center;color:#555;'>{_fmt(r['p10'])} → {_fmt(r['p50'])}</td>"
            f"<td style='padding:7px 10px;text-align:center;font-weight:800;color:{col};'>{r['success']*100:.0f}% {lbl}</td></tr>"
        )
    st.markdown(
        f"<div style='direction:rtl;font-family:sans-serif;text-align:right;'>"
        f"<table dir='rtl' style='width:100%;border-collapse:collapse;font-size:0.86em;direction:rtl;'>"
        f"<thead>{header}</thead><tbody>{body}</tbody></table></div>",
        unsafe_allow_html=True)
    st.markdown(
        f"<div style='direction:rtl;text-align:right;color:#777;font-size:0.82em;line-height:1.6;'>"
        f"על בסיס {years} שנים. התשואה נומינלית ולפני דמי ניהול. סיכוי ההצלחה = אחוז "
        f"התרחישים שבהם הכסף החזיק עד הגיל הנבדק. טווח הירושה מציג תרחיש גרוע (10%) "
        f"מול אמצעי (חציון).</div>", unsafe_allow_html=True)

    risky = [t for t in order if recs[t].get("at_risk")]
    if risky:
        _best = max(recs[t]["best_success"] for t in risky) * 100
        st.markdown(
            "<div style='direction:rtl;text-align:right;background:#fff8e1;border:1px solid #f0c86a;"
            "border-right:4px solid #e0a800;border-radius:8px;padding:10px 14px;margin:6px 0;"
            f"color:#5a4a1a;line-height:1.7;'>⚠️ במסלול שסומן בסיכון בדקנו את כל טווח התמהילים, "
            f"ממאה אחוז סולידי ועד תקרת המניות, והסיכוי הגבוה ביותר שהצלחנו להגיע אליו הוא "
            f"כ-{_best:.0f}%, מתחת לרף התשעים אחוז. זה לא בעיה של תמהיל אלא של המשיכה עצמה, "
            f"שגבוהה מדי ביחס לתיק. שום תערובת לא תפתור זאת, צריך לבחון מחדש הוצאות, הכנסות "
            f"או גיל בדיקה.</div>", unsafe_allow_html=True)

    st.divider()
    st.markdown(
        "<div style='direction:rtl;text-align:right;font-weight:700;'>להחיל את התשואות "
        "המומלצות על המסלולים? <span style='font-weight:400;color:#777;'>(השדה הידני יישאר "
        "וניתן לעקוף)</span></div>", unsafe_allow_html=True)
    if st.button("✅ החל תשואות מומלצות", use_container_width=True, key="alloc_apply_btn"):
        # אי אפשר לשנות שדה widget אחרי שנוצר בריצה זו, לכן שומרים בקשה שתוחל
        # בראש app.py לפני יצירת השדות.
        pending = {}
        for tid in (1, 2, 3):
            if recs.get(tid) and tid in visible:
                pending[_RETURN_FIELD_KEY[tid]] = round(recs[tid]["ret"] * 100, 1)
        st.session_state["alloc_pending"] = pending
        st.session_state["alloc_run"] = True
        st.rerun()
