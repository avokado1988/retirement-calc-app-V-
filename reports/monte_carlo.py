"""
מונטה קרלו למסלול המינוף (מסלול 5).

מודל דטרמיניסטי מניח תשואה קבועה ולכן לא יכול להראות את הסיכון האמיתי של המינוף,
דרישת ביטחונות בעקבות מפולת. מונטה קרלו מריץ אלפי רצפי תשואה אקראיים ומדווח על
ההסתברות לדרישת ביטחונות ועל התפלגות שווי הירושה, לכל גודל הלוואה.

מודל ישראלי. הכסף נשאר מושקע (מסלול כללי) וההלוואה קונה את הבית, כך שהתיק המושקע
והממושכן = הצבירה + ההלוואה. דרישת השלמה מתרחשת כשהחוב עובר את סף המימון משווי התיק.
"""
import numpy as np
import streamlit as st


def _simulate(P0, loan0, loan_rate, mean_ret, std_ret, years, annual_wd, wd_growth,
              home0, home_appr, buffer_cash, buffer_rate, call_ltv, side0=0.0,
              n_sims=4000, seed=12345):
    """P0 = התיק המושקע והממושכן (צבירה + הלוואה). דרישת השלמה כשהחוב עובר call_ltv
    משווי התיק. side0 שמור להרחבות (כסף שאול המושקע בנפרד), ברירת מחדל 0."""
    rng = np.random.default_rng(seed)
    rets = rng.normal(mean_ret, std_ret, size=(n_sims, years))

    P = np.full(n_sims, float(P0))
    S = np.full(n_sims, float(side0))
    D = np.full(n_sims, float(loan0))
    buf = np.full(n_sims, float(buffer_cash))
    margin_called = np.zeros(n_sims, dtype=bool)
    wd = float(annual_wd)

    for y in range(years):
        # ריבית משולמת שוטף (הלוואת בלון סטנדרטית) — החוב נשאר קבוע, הריבית נמשכת מהתיק
        total_wd = wd + D * loan_rate
        from_buf = np.minimum(buf, total_wd)
        buf = (buf - from_buf) * (1 + buffer_rate)
        P = P - (total_wd - from_buf)
        P = P * (1 + rets[:, y])
        S = S * (1 + rets[:, y])
        with np.errstate(divide="ignore", invalid="ignore"):
            ltv = np.where(P > 0, D / np.maximum(P, 1.0), 999.0)
        breach = (~margin_called) & (ltv > call_ltv)
        margin_called |= (ltv > call_ltv)
        pooled = np.maximum(0.0, P + S - D)
        P = np.where(breach, pooled, P)
        S = np.where(breach, 0.0, S)
        D = np.where(breach, 0.0, D)
        wd *= (1 + wd_growth)

    home = home0 * (1 + home_appr) ** years
    networth = P + S + home - D
    return {
        "p_margin_call": float(margin_called.mean()),
        "nw_p10": float(np.percentile(networth, 10)),
        "nw_p50": float(np.percentile(networth, 50)),
        "nw_p90": float(np.percentile(networth, 90)),
    }


GEN_RETURN = 0.06    # תשואת מסלול כללי, בסיס צופה פני עתיד (עבר 6.5-7.5%, תכנון 4-6%)
GEN_VOL    = 0.08    # תנודתיות מסלול כללי
CALL_LTV_IL = 0.90   # דרישת השלמה כשהחוב עובר 90% מהתיק (גבוה משיעור המימון 80%, זו הכרית)


def margin_call_probability(user_inputs, std_ret=GEN_VOL, call_ltv=CALL_LTV_IL, n_sims=2000):
    """Single Monte Carlo run for the CURRENT loan — probability of a margin call."""
    tl = user_inputs.get("timeline", {}); ex = user_inputs.get("expenses", {})
    w = user_inputs.get("wealth", {}); a190 = user_inputs.get("amendment_190", {})
    lev = user_inputs.get("leverage", {})
    years = max(1, int(round(float(tl.get("check_age", 95)) - float(tl.get("start_age", 65)))))
    net_for_190 = float(a190.get("net_for_190", 0))
    home = float(w.get("new_apartment_cost", 5500000))
    loan = min(float(lev.get("loan_amount", 0)), home, 4.0 * net_for_190)
    if loan <= 0 or net_for_190 <= 0:
        return 0.0
    mean_ret = GEN_RETURN - float(a190.get("management_fee_190", 0.005))
    monthly_deficit = max(0.0, float(ex.get("current_expenses", 11000))
                          - float(w.get("national_insurance", 2500))
                          - float(a190.get("desired_pension", 5306)))
    res = _simulate(net_for_190 + loan, loan, float(lev.get("loan_annual_rate", 0.0525)), mean_ret, std_ret, years,
                    monthly_deficit * 12, float(ex.get("expected_inflation", 0.023)),
                    home, float(w.get("property_appreciation", 0.03)),
                    float(w.get("emergency_fund", 250000)), 0.02, call_ltv, n_sims=n_sims)
    return res["p_margin_call"]


def _rtl(html):
    st.markdown(f"<div style='direction:rtl;text-align:right;'>{html}</div>", unsafe_allow_html=True)


def render_monte_carlo(user_inputs):
    import plotly.graph_objects as go

    def _f(x):
        return f"₪{x:,.0f}"

    def _sec(txt):
        st.markdown(
            f"<div style='direction:rtl;text-align:right;font-weight:800;font-size:1.05em;"
            f"color:#1a1a2e;margin:14px 0 6px;'>{txt}</div>", unsafe_allow_html=True)

    # ============ כותרת והסבר ============
    _rtl(
        "<p style='line-height:1.7;'>המודל הרגיל מניח שהשוק עולה בקצב קבוע כל שנה. במציאות "
        "יש שנים טובות ורעות. כאן מריצים אלפי תרחישי שוק אקראיים כדי לראות עד כמה המינוף "
        "מסוכן בפועל.</p>"
        "<p style='line-height:1.7;color:#555;font-size:0.92em;'>המודל לפי חוקי הקופות בישראל, "
        "מסלול כללי. הכסף נשאר מושקע וההלוואה קונה את הבית, כך שהתיק המושקע והממושכן = "
        "הצבירה + ההלוואה, בתשואת מסלול כללי (כ-6%). המימון עד 80% מהתיק, ודרישת השלמה "
        "מתרחשת רק כשהחוב מטפס מעל כ-90% משווי התיק. הרווח בין השניים הוא הכרית.</p>")
    st.markdown(
        "<div style='direction:rtl;text-align:right;background:#e7f0fb;border:1px solid #a9c9ef;"
        "border-right:4px solid #1565c0;border-radius:8px;padding:10px 14px;margin:6px 0;"
        "color:#173a5e;line-height:1.7;'><b>מה הסיכון במינוף?</b> אם השוק יורד חזק, התיק "
        "מצטמק אבל החוב לא, והמלווה דורש להשלים כסף. אם אין נזילות, מוכרים לך מהתיק "
        "<b>בשפל</b> ומקבעים הפסד. זה מה שאנחנו מודדים כאן.</div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='direction:rtl;text-align:right;background:#f5f3fa;border:1px solid #cbc0e6;"
        "border-right:4px solid #7e57c2;border-radius:8px;padding:10px 14px;margin:6px 0;"
        "color:#3d2b66;line-height:1.8;'><b>איך עובד סף המכירה, בקצרה</b><br/>"
        "1. אתה לווה עד 80% מהתיק. ההלוואה קבועה.<br/>"
        "2. כשהשוק יורד, התיק מצטמק, אבל ההלוואה נשארת אותו דבר, אז היא תופסת אחוז גדל והולך מהתיק.<br/>"
        "3. כשההלוואה מגיעה ל-90% מהתיק, הבנק דורש השלמה או מוכר. הוא לא מחכה שההלוואה תגיע ל-100%.<br/>"
        "4. הרווח בין מה שלקחת (למשל 75%) לבין הסף (90%) הוא הכרית, וזה כמה התיק יכול לרדת לפני מכירה.</div>",
        unsafe_allow_html=True)

    # ============ נתונים ============
    tl = user_inputs.get("timeline", {}); ex = user_inputs.get("expenses", {})
    w = user_inputs.get("wealth", {}); a190 = user_inputs.get("amendment_190", {})
    lev = user_inputs.get("leverage", {})

    years = max(1, int(round(float(tl.get("check_age", 95.0)) - float(tl.get("start_age", 65.0)))))
    net_for_190 = float(a190.get("net_for_190", 0))
    home0 = float(w.get("new_apartment_cost", 5500000))
    home_appr = float(w.get("property_appreciation", 0.03))
    buffer_cash = float(w.get("emergency_fund", 250000))
    loan_rate = float(lev.get("loan_annual_rate", 0.0525))
    mean_ret = GEN_RETURN - float(a190.get("management_fee_190", 0.005))
    inflation = float(ex.get("expected_inflation", 0.023))
    annual_wd = max(0.0, float(ex.get("current_expenses", 11000))
                    - float(w.get("national_insurance", 2500))
                    - float(a190.get("desired_pension", 5306))) * 12

    # ============ ⚙️ הנחות המודל ============
    _sec("⚙️ הנחות המודל")
    c1, c2 = st.columns(2)
    with c1:
        std_ret = st.slider("תנודתיות שנתית של התיק, מסלול כללי (סטיית תקן %)",
                            min_value=5.0, max_value=20.0, value=GEN_VOL * 100, step=0.5,
                            help="מסלול כללי סביב 7-9%. מנייתי טהור 15%+.") / 100
    with c2:
        call_ltv = st.slider("סף דרישת השלמה למכירה (% מהתיק)",
                             min_value=80.0, max_value=100.0, value=CALL_LTV_IL * 100, step=1.0,
                             help="גבוה משיעור המימון (80%). הרווח בין מה שלקחת לסף הוא הכרית. מקובל כ-90%.") / 100
    _rtl(
        f"<div style='color:#555;font-size:0.84em;line-height:1.6;margin-top:2px;'>"
        f"📌 <b>תשואת התיק המונחת:</b> {GEN_RETURN*100:.0f}% ברוטו מסלול כללי, "
        f"כ-{mean_ret*100:.1f}% נטו אחרי דמי ניהול &nbsp;·&nbsp; "
        f"<b>ריבית ההלוואה:</b> {loan_rate*100:.2f}%. הסיכון תלוי גם ביחס החוב לתיק וגם "
        f"בפער בין התשואה לריבית לאורך השנים.</div>")

    # ============ חישובים ============
    loan_cap = min(home0, 4.0 * net_for_190)  # מימון עד 80% מהתיק => הלוואה עד פי 4 מהצבירה

    def _drop_for_loan(ln):
        if ln <= 0:
            return 1.0
        return max(0.0, 1 - (ln / (net_for_190 + ln)) / call_ltv)

    cur_loan = max(0.0, min(float(lev.get("loan_amount", 0)), loan_cap))
    P0_cur = net_for_190 + cur_loan
    cur = _simulate(P0_cur, cur_loan, loan_rate, mean_ret, std_ret, years,
                    annual_wd, inflation, home0, home_appr, buffer_cash, 0.02, call_ltv)
    p_cur = cur["p_margin_call"]
    _ltv0 = cur_loan / P0_cur if P0_cur > 0 else 0.0
    threshold_val = cur_loan / call_ltv if call_ltv > 0 else P0_cur
    green_margin = max(0.0, P0_cur - threshold_val)
    orange_cushion = max(0.0, threshold_val - cur_loan)
    drop_needed = max(0.0, 1 - _ltv0 / call_ltv)
    loss_impact = max(0.0, cur["nw_p50"] - cur["nw_p10"])
    verdict = "נמוך 🟢" if p_cur < 0.05 else ("בינוני 🟡" if p_cur < 0.15 else "גבוה 🔴")
    _bg = "#eafaf0" if p_cur < 0.05 else ("#fff7e0" if p_cur < 0.15 else "#fdecea")
    _bd = "#8fd3a8" if p_cur < 0.05 else ("#f0c86a" if p_cur < 0.15 else "#e0a099")

    # כל קשת ההלוואה, מ-0 ועד התקרה (מחיר הבית), בקפיצות של 10%
    loan_steps = sorted(set(int(loan_cap * i / 10) for i in range(11)))
    rows = []
    for loan in loan_steps:
        P0 = net_for_190 + loan
        ltv0 = (loan / P0 * 100) if P0 > 0 else 0
        res = _simulate(P0, loan, loan_rate, mean_ret, std_ret, years, annual_wd, inflation,
                        home0, home_appr, buffer_cash, 0.02, call_ltv, n_sims=2500)
        rows.append((loan, ltv0, res))

    # ============ 1. המצב שלך ============
    _sec("1️⃣ המצב שלך — ההלוואה שבחרת")
    _bcol = st.columns([1, 2, 1])[1]  # ממורכז, לא רחב מדי
    with _bcol:
        _BW = 0.32
        bar = go.Figure()
        bar.add_trace(go.Bar(
            x=["התיק"], y=[cur_loan], name="הלוואה", marker_color="#c0392b", width=_BW,
            text=[f"הלוואה<br>{_f(cur_loan)}"], textposition="inside", insidetextanchor="middle",
            textfont=dict(color="white", size=11), hoverinfo="text",
            hovertext=[f"הלוואה: {_f(cur_loan)}"]))
        bar.add_trace(go.Bar(
            x=["התיק"], y=[orange_cushion], name="כרית נדרשת", marker_color="#e6a800", width=_BW,
            hoverinfo="text", hovertext=[f"כרית נדרשת מעל ההלוואה: {_f(orange_cushion)}"]))
        bar.add_trace(go.Bar(
            x=["התיק"], y=[green_margin], name=f"מרווח — התיק יכול לרדת {drop_needed*100:.0f}%",
            marker_color="#27ae60", width=_BW, hoverinfo="text",
            hovertext=[f"התיק יכול לרדת {_f(green_margin)} ({drop_needed*100:.0f}%) לפני דרישת השלמה"]))
        bar.add_hline(
            y=threshold_val, line=dict(color="#c0392b", width=2.5, dash="dash"),
            annotation_text=f"רף השלמה {_f(threshold_val)}",
            annotation_position="top left", annotation_font=dict(color="#c0392b", size=11))
        bar.add_annotation(
            x="התיק", y=P0_cur, yshift=18, showarrow=False,
            text=f"💼 סך התיק {_f(P0_cur)}",
            font=dict(color="#1a1a2e", size=15, family="sans-serif"), bgcolor="rgba(255,255,255,0.9)")
        bar.update_layout(
            barmode="stack", height=300, template="plotly_white", bargap=0.6,
            title={"text": "הרכב התיק ורף דרישת השלמה", "font": {"size": 13}, "x": 0.5},
            margin=dict(t=70, b=10, l=10, r=10), font=dict(family="sans-serif"),
            xaxis=dict(showticklabels=False),
            yaxis=dict(title="₪", tickformat=",.0f", range=[0, max(P0_cur, 1) * 1.12]),
            legend=dict(orientation="h", y=-0.08, x=0.5, xanchor="center", font=dict(size=9)),
            showlegend=True)
        st.plotly_chart(bar, use_container_width=True)

    if cur_loan <= 0:
        st.markdown(
            f"<div style='direction:rtl;text-align:right;background:#eafaf0;border:1px solid #8fd3a8;"
            f"border-right:4px solid #1a7a3a;border-radius:8px;padding:12px 16px;color:#14532d;"
            f"line-height:1.7;'>✅ ללא מינוף (הלוואה ₪0), אין סיכון של דרישת השלמה. "
            f"הירושה הצפויה {_f(cur['nw_p50'])}.</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            f"<div style='direction:rtl;text-align:right;font-size:0.86em;color:#333;line-height:1.9;"
            f"background:#f8f9fc;border:1px solid #e6e8f0;border-radius:8px;padding:10px 14px;margin:6px 0;'>"
            f"💼 <b>סך התיק היום:</b> {_f(P0_cur)} "
            f"<span style='color:#777;'>(הצבירה שלך {_f(net_for_190)} + הלוואה {_f(cur_loan)})</span><br/>"
            f"📊 <b>שיעור מימון היום:</b> {_ltv0*100:.0f}% — ההלוואה חלקי התיק (מתוך תקרה של 80%).<br/>"
            f"🔴 <b>רף דרישת השלמה:</b> {_f(threshold_val)} — <span style='color:#555;'>שווי התיק שאם יורדים אליו, ההלוואה הופכת ל-{call_ltv*100:.0f}% מהתיק, ואז הבנק דורש השלמה או מוכר.</span><br/>"
            f"🟢 <b>מרחק מהרף:</b> <span style='color:#555;'>כדי להגיע לרף, <u>התיק</u> צריך לרדת בכ-</span><b>{drop_needed*100:.0f}%</b> <span style='color:#555;'>(מ-{_f(P0_cur)} ל-{_f(threshold_val)}). שים לב, זו ירידה של התיק הכללי, לא של שוק המניות.</span>"
            f"</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='direction:rtl;text-align:right;background:{_bg};border:1px solid {_bd};"
            f"border-radius:8px;padding:12px 16px;font-size:0.92em;line-height:1.9;'>"
            f"<div>🎯 <b>מה צריך שיקרה:</b> ירידה של כ-<b>{drop_needed*100:.0f}%</b> בתיק הכללי (לא בשוק המניות).</div>"
            f"<div>💥 <b>ההשפעה:</b> מוכרים בשפל ומקבעים הפסד — הירושה יורדת מ-<b>{_f(cur['nw_p50'])}</b> (צפוי) לכ-<b>{_f(cur['nw_p10'])}</b> (תרחיש גרוע), פגיעה של כ-{_f(loss_impact)}.</div>"
            f"<div>🎲 <b>הסיכוי שזה יקרה:</b> <b>{p_cur*100:.0f}%</b> מהתרחישים לאורך הפרישה.</div>"
            f"<div>⚖️ <b>מסקנה:</b> סיכון <b>{verdict}</b>.</div>"
            f"</div>", unsafe_allow_html=True)

    # ============ 2. כמה אפשר ללוות ============
    st.divider()
    _sec("2️⃣ הסיכון לפי גודל ההלוואה — כל הקשת")
    _rows_html = ""
    for loan, ltv0, res in rows:
        p = res["p_margin_call"]
        rc, rl = (("#1a7a3a", "🟢 נמוך") if p < 0.10 else
                  ("#b07800", "🟡 בינוני") if p < 0.25 else ("#a83232", "🔴 גבוה"))
        loan_lbl = "ללא מינוף" if loan == 0 else _f(loan)
        _rows_html += (
            f"<tr style='border-bottom:1px solid #eee;'>"
            f"<td style='padding:7px 12px;text-align:right;font-weight:800;'>{loan_lbl}</td>"
            f"<td style='padding:7px 12px;text-align:center;'>{ltv0:.0f}%</td>"
            f"<td style='padding:7px 12px;text-align:center;font-weight:700;color:{rc};'>{p*100:.0f}%</td>"
            f"<td style='padding:7px 12px;text-align:center;font-weight:700;color:{rc};'>{rl}</td>"
            f"<td style='padding:7px 12px;text-align:center;color:#555;'>{_drop_for_loan(loan)*100:.0f}%</td></tr>")
    with st.expander("📊 טבלת הסיכון לכל גודל הלוואה (0 עד המקסימום)", expanded=True):
        st.markdown(
            f"<div style='direction:rtl;text-align:right;font-family:sans-serif;'>"
            f"<table dir='rtl' style='width:100%;border-collapse:collapse;font-size:0.9em;'>"
            f"<thead><tr style='background:#eef0f7;'>"
            f"<th style='padding:7px 12px;text-align:right;'>סכום ההלוואה</th>"
            f"<th style='padding:7px 12px;'>שיעור מימון</th>"
            f"<th style='padding:7px 12px;'>סיכוי דרישת השלמה</th>"
            f"<th style='padding:7px 12px;'>רמת סיכון</th>"
            f"<th style='padding:7px 12px;'>בכמה התיק יכול לרדת</th></tr></thead>"
            f"<tbody>{_rows_html}</tbody></table></div>", unsafe_allow_html=True)
        _rtl(
            "<div style='color:#777;font-size:0.8em;line-height:1.6;margin-top:6px;'>"
            "העמודה בכמה התיק יכול לרדת מתייחסת לירידת התיק הכללי, לא לשוק המניות. "
            "מכיוון שמסלול כללי הוא כמחצית מניות, ירידה בתיק שקולה בערך לירידה כפולה בשוק המניות. "
            "כלומר ירידה של 30% בתיק דורשת מפולת של כ-60% בשוק המניות, אירוע נדיר מאוד.</div>")

    _cur_col = "#1a7a3a" if p_cur <= 0.10 else ("#b07800" if p_cur <= 0.25 else "#a83232")
    _cur_lbl = "שמרנית" if p_cur <= 0.10 else ("מתונה" if p_cur <= 0.25 else "אגרסיבית")
    _rtl(
        f"<div style='color:#444;font-size:0.9em;line-height:1.7;margin-top:8px;'>"
        f"ההלוואה שבחרת ({_f(cur_loan)}) נמצאת ברמת סיכון "
        f"<b style='color:{_cur_col};'>{_cur_lbl}</b>, עם סיכוי דרישת השלמה של כ-{p_cur*100:.0f}%.</div>"
        f"<div style='color:#777;font-size:0.82em;line-height:1.6;margin-top:4px;'>"
        f"מינוף הוא תמיד לקיחת סיכון, אין סכום חסר סיכון. המודל מניח שהריבית משולמת "
        f"שוטף מהתיק וקרן ההלוואה נשארת קבועה, כמו בהלוואת בלון סטנדרטית.</div>")

    # ============ 3. סיכון מול תשואה ============
    st.divider()
    _sec("3️⃣ סיכון מול תשואה — לפי גודל ההלוואה")
    rr = go.Figure()
    rr.add_trace(go.Scatter(x=[r[0] for r in rows], y=[r[2]["nw_p50"] / 1e6 for r in rows],
                            name="ירושה חציונית (₪ מיליון)", mode="lines+markers",
                            line=dict(color="#1a7a3a", width=3), yaxis="y1"))
    rr.add_trace(go.Scatter(x=[r[0] for r in rows], y=[r[2]["p_margin_call"] * 100 for r in rows],
                            name="סיכון דרישת השלמה (%)", mode="lines+markers",
                            line=dict(color="#c0392b", width=3, dash="dot"), yaxis="y2"))
    rr.update_layout(
        height=340, template="plotly_white", font=dict(family="sans-serif"),
        margin=dict(t=20, b=40, l=10, r=10),
        xaxis=dict(title="סכום ההלוואה (₪)"),
        yaxis=dict(title="ירושה (₪ מיליון)", side="left"),
        yaxis2=dict(title="סיכון %", overlaying="y", side="right", range=[0, 100]),
        legend=dict(orientation="h", y=1.18, x=0, xanchor="left"))
    st.plotly_chart(rr, use_container_width=True)
    _rtl(
        f"<div style='color:#777;font-size:0.82em;line-height:1.6;'>"
        f"ככל שההלוואה גדלה, הקו הירוק (ירושה) עולה, אבל גם הקו האדום (סיכון) עולה. "
        f"על בסיס {years} שנים, תשואה ממוצעת {mean_ret*100:.1f}%, וריבית הלוואה {loan_rate*100:.2f}%.</div>")
