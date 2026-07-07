"""
מונטה קרלו למסלול המינוף (מסלול 5).

מודל דטרמיניסטי מניח תשואה קבועה ולכן לא יכול להראות את הסיכון האמיתי של המינוף,
דרישת ביטחונות בעקבות מפולת. מונטה קרלו מריץ אלפי רצפי תשואה אקראיים ומדווח על
ההסתברות לדרישת ביטחונות ועל התפלגות שווי הירושה, לכל גודל הלוואה.

השיטה שנתית ומווקטרת ב-numpy. כשהיחס חוב/תיק חוצה את סף המכירה, מדומה מכירה כפויה,
התיק מחוסל לכיסוי החוב וההון שנותר ממשיך ללא מינוף.
"""
import numpy as np
import streamlit as st


def _simulate(P0, loan0, loan_rate, mean_ret, std_ret, years, annual_wd, wd_growth,
              home0, home_appr, buffer_cash, buffer_rate, call_ltv, n_sims=4000, seed=12345):
    rng = np.random.default_rng(seed)
    rets = rng.normal(mean_ret, std_ret, size=(n_sims, years))

    P = np.full(n_sims, float(P0))
    D = np.full(n_sims, float(loan0))
    buf = np.full(n_sims, float(buffer_cash))
    margin_called = np.zeros(n_sims, dtype=bool)
    wd = float(annual_wd)

    for y in range(years):
        # Live off the cash buffer first, then the portfolio
        from_buf = np.minimum(buf, wd)
        buf = (buf - from_buf) * (1 + buffer_rate)
        P = P - (wd - from_buf)
        # Market return + loan interest accrual
        P = P * (1 + rets[:, y])
        D = D * (1 + loan_rate)
        # Margin call when debt/portfolio crosses the liquidation threshold
        with np.errstate(divide="ignore", invalid="ignore"):
            ltv = np.where(P > 0, D / np.maximum(P, 1.0), 999.0)
        breach = (~margin_called) & (ltv > call_ltv)
        margin_called |= (ltv > call_ltv)
        # Forced liquidation: sell to repay the debt; remaining equity continues unlevered
        P = np.where(breach, np.maximum(0.0, P - D), P)
        D = np.where(breach, 0.0, D)
        wd *= (1 + wd_growth)

    home = home0 * (1 + home_appr) ** years
    networth = P + home - D
    return {
        "p_margin_call": float(margin_called.mean()),
        "nw_p10": float(np.percentile(networth, 10)),
        "nw_p50": float(np.percentile(networth, 50)),
        "nw_p90": float(np.percentile(networth, 90)),
    }


def margin_call_probability(user_inputs, std_ret=0.12, call_ltv=0.85, n_sims=2000):
    """Single Monte Carlo run for the CURRENT loan — probability of a margin call.
    Used to surface a risk figure on the leverage card."""
    tl = user_inputs.get("timeline", {}); ex = user_inputs.get("expenses", {})
    w = user_inputs.get("wealth", {}); a190 = user_inputs.get("amendment_190", {})
    lev = user_inputs.get("leverage", {})
    years = max(1, int(round(float(tl.get("check_age", 95)) - float(tl.get("start_age", 65)))))
    loan = float(lev.get("loan_amount", 0))
    if loan <= 0:
        return 0.0
    P0 = float(a190.get("net_for_190", 0)) + loan
    mean_ret = float(a190.get("annual_return_190", 0.07)) - float(a190.get("management_fee_190", 0.005))
    monthly_deficit = max(0.0, float(ex.get("current_expenses", 11000))
                          - float(w.get("national_insurance", 2500))
                          - float(a190.get("desired_pension", 5306)))
    res = _simulate(P0, loan, float(lev.get("loan_annual_rate", 0.0525)), mean_ret, std_ret, years,
                    monthly_deficit * 12, float(ex.get("expected_inflation", 0.023)),
                    float(w.get("new_apartment_cost", 5500000)), float(w.get("property_appreciation", 0.03)),
                    float(w.get("emergency_fund", 250000)), 0.02, call_ltv, n_sims=n_sims)
    return res["p_margin_call"]


def render_monte_carlo(user_inputs):
    st.markdown(
        "<div style='direction:rtl;text-align:right;'>"
        "<h4 style='color:#1a1a2e;'>🎲 ניתוח סיכון — מונטה קרלו למסלול המינוף</h4>"
        "<p style='line-height:1.7;'>המודל הרגיל מניח שהשוק עולה בקצב קבוע כל שנה. במציאות "
        "יש שנים טובות ורעות. כאן מריצים אלפי תרחישי שוק אקראיים כדי לראות עד כמה המינוף "
        "מסוכן בפועל.</p></div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='direction:rtl;text-align:right;background:#e7f0fb;border:1px solid #a9c9ef;"
        "border-right:4px solid #1565c0;border-radius:8px;padding:10px 14px;margin:6px 0;"
        "color:#173a5e;line-height:1.7;'><b>מה הסיכון במינוף?</b> לקחת הלוואה כנגד תיק "
        "ההשקעות. אם השוק יורד חזק, התיק מצטמק אבל החוב לא, והבנק דורש להחזיר חלק מההלוואה. "
        "אם אין מזומן, הבנק <b>מוכר לך מניות בשפל</b> ומקבע הפסד כבד. זה בדיוק מה שאנחנו "
        "מודדים כאן, מה הסבירות שזה יקרה לאורך שנות הפרישה.</div>", unsafe_allow_html=True)

    tl = user_inputs.get("timeline", {})
    ex = user_inputs.get("expenses", {})
    w = user_inputs.get("wealth", {})
    a190 = user_inputs.get("amendment_190", {})
    lev = user_inputs.get("leverage", {})

    start_age = float(tl.get("start_age", 65.0))
    check_age = float(tl.get("check_age", 95.0))
    years = max(1, int(round(check_age - start_age)))

    net_for_190 = float(a190.get("net_for_190", 0))
    home0 = float(w.get("new_apartment_cost", 5500000))
    home_appr = float(w.get("property_appreciation", 0.03))
    buffer_cash = float(w.get("emergency_fund", 250000))
    loan_rate = float(lev.get("loan_annual_rate", 0.0525))

    mean_ret = float(a190.get("annual_return_190", 0.07)) - float(a190.get("management_fee_190", 0.005))
    inflation = float(ex.get("expected_inflation", 0.023))
    # Deficit funded from the portfolio: expenses − (NI + pension), monthly → annual
    monthly_deficit = max(0.0, float(ex.get("current_expenses", 11000))
                          - float(w.get("national_insurance", 2500))
                          - float(a190.get("desired_pension", 5306)))
    annual_wd = monthly_deficit * 12

    def _f(x):
        return f"₪{x:,.0f}"

    c1, c2 = st.columns(2)
    with c1:
        std_ret = st.slider("תנודתיות שנתית של התיק (סטיית תקן %)",
                            min_value=6.0, max_value=25.0, value=12.0, step=0.5,
                            help="תיק סולידי מפוזר סביב 10-12%. מנייתי טהור 18%+.") / 100
    with c2:
        call_ltv = st.slider("סף מכירה (LTV שבו הבנק מוכר %)",
                             min_value=70.0, max_value=95.0, value=85.0, step=1.0,
                             help="מעל שיעור המימון המקסימלי (75%). כשהיחס חוצה אותו — מכירה כפויה.") / 100

    # --- כמה אפשר ללוות לפי רמת הסיכון שמוכנים לקחת ---
    # מינוף הוא בהגדרה סיכון, ולכן במקום "סכום בטוח" יחיד מציגים כמה אפשר ללוות
    # בכל רמת סיכון. הסתברות המכירה הכפויה עולה באופן מונוטוני עם ההלוואה.
    loan_cap = min(home0, 3 * net_for_190)  # תקרת מימון 75% (loan <= 3 × החלק הנזיל)
    _N = 40
    _grid = []
    for _i in range(_N + 1):
        _loan = loan_cap * _i / _N
        _pr = _simulate(net_for_190 + _loan, _loan, loan_rate, mean_ret, std_ret, years,
                        annual_wd, inflation, home0, home_appr, buffer_cash, 0.02, call_ltv,
                        n_sims=1500)["p_margin_call"]
        _grid.append((_loan, _pr))

    def _max_loan_under(thr):
        ok = [ln for ln, pr in _grid if pr <= thr]
        return max(ok) if ok else 0.0

    _cur_loan_disp = max(0.0, min(float(lev.get("loan_amount", 0)), loan_cap))
    _cur_pr = next((pr for ln, pr in _grid if ln >= _cur_loan_disp), _grid[-1][1])

    def _drop_for_loan(ml):
        # כמה השוק יכול לרדת עכשיו עד שהיחס חוצה את סף המכירה
        if ml <= 0:
            return 1.0
        ltv0 = ml / (net_for_190 + ml)
        return max(0.0, 1 - ltv0 / call_ltv)

    _tiers = [("🟢 שמרני מאוד", 0.05, "#127a3a"),
              ("🟢 שמרני", 0.10, "#1a7a3a"),
              ("🟡 מתון", 0.20, "#b07800"),
              ("🟠 אגרסיבי", 0.35, "#c9700f"),
              ("🔴 אגרסיבי מאוד", 0.50, "#a83232")]
    _rows_html = ""
    for lbl, thr, c in _tiers:
        _ml = _max_loan_under(thr)
        _rows_html += (
            f"<tr style='border-bottom:1px solid #eee;'>"
            f"<td style='padding:7px 12px;text-align:right;font-weight:700;color:{c};'>{lbl}</td>"
            f"<td style='padding:7px 12px;text-align:center;'>עד {int(thr*100)}%</td>"
            f"<td style='padding:7px 12px;text-align:center;font-weight:800;'>{_f(_ml)}</td>"
            f"<td style='padding:7px 12px;text-align:center;color:#555;'>{_drop_for_loan(_ml)*100:.0f}%</td></tr>")
    st.markdown(
        f"<div style='direction:rtl;text-align:right;font-family:sans-serif;'>"
        f"<div style='font-weight:800;font-size:1.02em;margin-bottom:4px;'>💰 כמה אפשר ללוות, לפי רמת הסיכון</div>"
        f"<table dir='rtl' style='width:100%;border-collapse:collapse;font-size:0.9em;'>"
        f"<thead><tr style='background:#eef0f7;'>"
        f"<th style='padding:7px 12px;text-align:right;'>רמת סיכון</th>"
        f"<th style='padding:7px 12px;'>סיכוי מכירה כפויה</th>"
        f"<th style='padding:7px 12px;'>סכום הלוואה מקסימלי</th>"
        f"<th style='padding:7px 12px;'>כמה השוק יכול לרדת</th></tr></thead>"
        f"<tbody>{_rows_html}</tbody></table></div>", unsafe_allow_html=True)

    # השוואה להלוואה הנוכחית
    _cur_col = "#1a7a3a" if _cur_pr <= 0.10 else ("#b07800" if _cur_pr <= 0.25 else "#a83232")
    _cur_lbl = "שמרנית" if _cur_pr <= 0.10 else ("מתונה" if _cur_pr <= 0.25 else "אגרסיבית")
    st.markdown(
        f"<div style='direction:rtl;text-align:right;color:#444;font-size:0.9em;line-height:1.7;margin-top:8px;'>"
        f"ההלוואה הנוכחית ({_f(_cur_loan_disp)}) נמצאת ברמת סיכון "
        f"<b style='color:{_cur_col};'>{_cur_lbl}</b>, עם סיכוי מכירה כפויה של כ-{_cur_pr*100:.0f}%.</div>",
        unsafe_allow_html=True)
    st.markdown(
        "<div style='direction:rtl;text-align:right;color:#777;font-size:0.82em;line-height:1.6;margin-top:4px;'>"
        "מינוף הוא תמיד לקיחת סיכון, אין סכום חסר סיכון לחלוטין. הטבלה מניחה שריבית "
        "ההלוואה מצטברת לאורך כל התקופה בלי שמשלמים אותה, וזו ההנחה השמרנית.</div>",
        unsafe_allow_html=True)

    home_price = home0
    loan_steps = [0, int(loan_cap*0.2), int(loan_cap*0.4), int(loan_cap*0.6),
                  int(loan_cap*0.8), int(loan_cap)]

    rows = []
    for loan in loan_steps:
        P0 = net_for_190 + loan
        ltv0 = (loan / P0 * 100) if P0 > 0 else 0
        res = _simulate(P0, loan, loan_rate, mean_ret, std_ret, years, annual_wd, inflation,
                        home0, home_appr, buffer_cash, 0.02, call_ltv)
        rows.append((loan, ltv0, res))

    import plotly.graph_objects as go

    # --- Current chosen loan → gauge + one-sentence verdict ---
    cur_loan = max(0.0, min(float(lev.get("loan_amount", 0)), home0))
    cur = _simulate(net_for_190 + cur_loan, cur_loan, loan_rate, mean_ret, std_ret, years,
                    annual_wd, inflation, home0, home_appr, buffer_cash, 0.02, call_ltv)
    p_cur = cur["p_margin_call"]

    # Composition today: portfolio, loan, and the forced-sale threshold
    P0_cur = net_for_190 + cur_loan
    _ltv0 = cur_loan / P0_cur if P0_cur > 0 else 0.0
    threshold_val = cur_loan / call_ltv if call_ltv > 0 else P0_cur  # portfolio value that triggers a call
    green_margin = max(0.0, P0_cur - threshold_val)   # how much the portfolio can fall before a call
    orange_cushion = max(0.0, threshold_val - cur_loan)  # the bank's required cushion above the loan
    drop_needed = max(0.0, 1 - _ltv0 / call_ltv)  # = green_margin / P0_cur
    loss_impact = max(0.0, cur["nw_p50"] - cur["nw_p10"])

    verdict = "נמוך 🟢" if p_cur < 0.05 else ("בינוני 🟡" if p_cur < 0.15 else "גבוה 🔴")
    _bg = "#eafaf0" if p_cur < 0.05 else ("#fff7e0" if p_cur < 0.15 else "#fdecea")
    _bd = "#8fd3a8" if p_cur < 0.05 else ("#f0c86a" if p_cur < 0.15 else "#e0a099")

    g1, g2 = st.columns([1, 1])

    with g1:
        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=round(p_cur * 100),
            number={"suffix": "%", "font": {"size": 42}},
            title={"text": f"סיכוי שתיאלץ למכור את התיק בהפסד<br>(הלוואה {_f(cur_loan)})", "font": {"size": 14}},
            gauge={
                "axis": {"range": [0, 100], "ticksuffix": "%"},
                "bar": {"color": "#2c3e50", "thickness": 0.25},
                "steps": [
                    {"range": [0, 5], "color": "#c8f0d0"},
                    {"range": [5, 15], "color": "#ffe7a3"},
                    {"range": [15, 100], "color": "#f5b3b3"},
                ],
            },
        ))
        gauge.update_layout(height=300, margin=dict(t=70, b=10, l=30, r=30), font=dict(family="sans-serif"))
        st.plotly_chart(gauge, use_container_width=True)

    with g2:
        # Stacked bar: loan (bottom) → bank's required cushion → your safety margin (top).
        # The red dashed line marks the forced-sale threshold; the green part is how far it can fall.
        _BW = 0.32  # narrow bar — the default fills the whole slot and looks too thick
        bar = go.Figure()
        bar.add_trace(go.Bar(
            x=["התיק שלך"], y=[cur_loan], name="הלוואה", marker_color="#c0392b", width=_BW,
            text=[f"הלוואה<br>{_f(cur_loan)}"], textposition="inside", insidetextanchor="middle",
            textfont=dict(color="white", size=12), hoverinfo="text",
            hovertext=[f"הלוואה שנלקחה: {_f(cur_loan)}"]))
        bar.add_trace(go.Bar(
            x=["התיק שלך"], y=[orange_cushion], name="כרית נדרשת לבנק", marker_color="#e6a800", width=_BW,
            text=[_f(orange_cushion)], textposition="inside", insidetextanchor="middle",
            textfont=dict(color="white", size=10), hoverinfo="text",
            hovertext=[f"כרית ביטחון שהבנק דורש מעל ההלוואה: {_f(orange_cushion)}"]))
        bar.add_trace(go.Bar(
            x=["התיק שלך"], y=[green_margin], name="מרווח ביטחון שלך", marker_color="#27ae60", width=_BW,
            text=[_f(green_margin)], textposition="inside", insidetextanchor="middle",
            textfont=dict(color="white", size=10), hoverinfo="text",
            hovertext=[f"כמה התיק יכול לרדת לפני מכירה כפויה: {_f(green_margin)} ({drop_needed*100:.0f}%)"]))
        bar.add_hline(
            y=threshold_val, line=dict(color="#c0392b", width=2.5, dash="dash"),
            annotation_text=f"סף מכירה {_f(threshold_val)}",
            annotation_position="bottom right", annotation_font=dict(color="#c0392b", size=11))
        # Clear label of the TOTAL portfolio value, right above the top of the bar
        bar.add_annotation(
            x="התיק שלך", y=P0_cur, yshift=16, showarrow=False,
            text=f"💼 שווי התיק {_f(P0_cur)}",
            font=dict(color="#1a1a2e", size=13, family="sans-serif"),
            bgcolor="rgba(255,255,255,0.85)")
        bar.update_layout(
            barmode="stack", height=300, template="plotly_white", bargap=0.6,
            title={"text": f"הרכב התיק היום — סה\"כ {_f(P0_cur)}", "font": {"size": 14}, "x": 0.5},
            margin=dict(t=70, b=10, l=10, r=10), font=dict(family="sans-serif"),
            xaxis=dict(showticklabels=False),
            yaxis=dict(title="₪", tickformat=",.0f", range=[0, P0_cur * 1.12]),
            legend=dict(orientation="h", y=-0.08, x=0.5, xanchor="center", font=dict(size=10)),
            showlegend=True)
        st.plotly_chart(bar, use_container_width=True)

    if cur_loan <= 0:
        st.markdown(
            f"<div style='direction:rtl;text-align:right;background:#eafaf0;border:1px solid #8fd3a8;"
            f"border-right:4px solid #1a7a3a;border-radius:8px;padding:12px 16px;color:#14532d;"
            f"line-height:1.7;'>✅ ללא מינוף (הלוואה ₪0), אין סיכון של מכירה כפויה. "
            f"הירושה הצפויה {_f(cur['nw_p50'])}.</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            f"<div style='direction:rtl;text-align:right;background:{_bg};border:1px solid {_bd};"
            f"border-radius:8px;padding:12px 16px;font-size:0.92em;line-height:1.9;'>"
            f"<div>🎯 <b>מה צריך שיקרה:</b> ירידה של כ-<b>{drop_needed*100:.0f}%</b> בתיק — "
            f"מ-<b>{_f(P0_cur)}</b> היום לכ-<b>{_f(threshold_val)}</b>. ברגע שהתיק חוצה את הרף הזה, "
            f"יחס החוב מגיע ל-{call_ltv*100:.0f}% והבנק מוכר.</div>"
            f"<div>💥 <b>ההשפעה אם זה קורה:</b> הבנק מוכר לך מניות בשפל ומקבע הפסד — הירושה יורדת מ-<b>{_f(cur['nw_p50'])}</b> (צפוי) לכ-<b>{_f(cur['nw_p10'])}</b> (תרחיש גרוע). פגיעה של כ-{_f(loss_impact)}.</div>"
            f"<div>🎲 <b>הסיכוי שזה יקרה:</b> <b>{p_cur*100:.0f}%</b> מהתרחישים לאורך הפרישה.</div>"
            f"<div>⚖️ <b>מסקנה:</b> סיכון <b>{verdict}</b>.</div>"
            f"</div>", unsafe_allow_html=True)

    st.divider()

    # --- Risk vs reward across loan sizes ---
    st.markdown("<div style='direction:rtl;text-align:right;font-weight:700;font-size:1.0em;'>📈 סיכון מול תשואה — לפי גודל ההלוואה</div>", unsafe_allow_html=True)
    loans   = [r[0] for r in rows]
    risks   = [r[2]["p_margin_call"] * 100 for r in rows]
    medians = [r[2]["nw_p50"] / 1e6 for r in rows]
    rr = go.Figure()
    rr.add_trace(go.Scatter(x=loans, y=medians, name="ירושה חציונית (₪ מיליון)", mode="lines+markers",
                            line=dict(color="#1a7a3a", width=3), yaxis="y1"))
    rr.add_trace(go.Scatter(x=loans, y=risks, name="סיכון מכירה כפויה (%)", mode="lines+markers",
                            line=dict(color="#c0392b", width=3, dash="dot"), yaxis="y2"))
    rr.update_layout(
        height=340, template="plotly_white", font=dict(family="sans-serif"),
        margin=dict(t=20, b=40, l=10, r=10),
        xaxis=dict(title="סכום ההלוואה (₪)"),
        yaxis=dict(title="ירושה (₪ מיליון)", side="left"),
        yaxis2=dict(title="סיכון %", overlaying="y", side="right", range=[0, 100]),
        legend=dict(orientation="h", y=1.18, x=0, xanchor="left"),
    )
    st.plotly_chart(rr, use_container_width=True)
    st.markdown(
        "<div style='direction:rtl;text-align:right;color:#777;font-size:0.82em;line-height:1.6;'>"
        "ככל שההלוואה גדלה, הקו הירוק (ירושה) עולה, אבל גם הקו האדום (סיכון) עולה. "
        "רמת המינוף ההגיונית היא הגבוהה ביותר שבה הקו האדום עדיין נמוך.</div>",
        unsafe_allow_html=True)

    # --- Full numeric table (collapsed) ---
    header = (
        "<tr style='background:#eef0f7;'>"
        "<th style='padding:6px 10px;text-align:right;'>הלוואה</th>"
        "<th style='padding:6px 10px;'>מינוף התחלתי</th>"
        "<th style='padding:6px 10px;'>סיכון דרישת ביטחונות</th>"
        "<th style='padding:6px 10px;'>ירושה — גרוע (10%)</th>"
        "<th style='padding:6px 10px;'>ירושה — חציון</th>"
        "<th style='padding:6px 10px;'>ירושה — טוב (90%)</th></tr>"
    )
    body = ""
    for loan, ltv0, res in rows:
        p = res["p_margin_call"]
        rc = "#1a7a3a" if p < 0.05 else ("#b07800" if p < 0.15 else "#a83232")
        rl = "נמוך" if p < 0.05 else ("בינוני" if p < 0.15 else "גבוה")
        loan_lbl = "ללא מינוף (מסלול 1)" if loan == 0 else _f(loan)
        body += (
            f"<tr style='border-bottom:1px solid #eee;'>"
            f"<td style='padding:6px 10px;text-align:right;font-weight:600;'>{loan_lbl}</td>"
            f"<td style='padding:6px 10px;text-align:center;'>{ltv0:.0f}%</td>"
            f"<td style='padding:6px 10px;text-align:center;color:{rc};font-weight:700;'>{p*100:.0f}% ({rl})</td>"
            f"<td style='padding:6px 10px;text-align:center;color:#a83232;'>{_f(res['nw_p10'])}</td>"
            f"<td style='padding:6px 10px;text-align:center;font-weight:700;'>{_f(res['nw_p50'])}</td>"
            f"<td style='padding:6px 10px;text-align:center;color:#1a7a3a;'>{_f(res['nw_p90'])}</td></tr>"
        )
    with st.expander("📋 פירוט מספרי מלא"):
        st.markdown(
            f"<div style='direction:rtl;font-family:sans-serif;text-align:right;'>"
            f"<table dir='rtl' style='width:100%;border-collapse:collapse;font-size:0.85em;direction:rtl;text-align:right;'>"
            f"<thead>{header}</thead><tbody>{body}</tbody></table></div>",
            unsafe_allow_html=True)
        st.markdown(
            f"<div style='direction:rtl;text-align:right;color:#777;font-size:0.82em;line-height:1.6;'>"
            f"על בסיס {years} שנים, תשואה ממוצעת {mean_ret*100:.1f}%, ריבית הלוואה {loan_rate*100:.2f}%, "
            f"וכרית מזומן {_f(buffer_cash)}. סיכון דרישת ביטחונות = אחוז התרחישים שבהם השוק צנח מספיק "
            f"כדי לחצות את סף המכירה ולאלץ מכירת התיק.</div>", unsafe_allow_html=True)
