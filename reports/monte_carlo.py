"""
מונטה קרלו למסלול המינוף (מסלול 5).

לפי מה שהמלווה מסר: אין מכירה כפויה, ההלוואה מסוג בלון שנפרעת מהעיזבון (הריבית
מצטברת לחוב), מסלול כללי, וניתן למחזר. לכן השאלה הנבדקת כאן היא לא סיכון מכירה
כפויה, אלא כמה יהיה שווה התיק בסוף, עם מינוף מול בלי מינוף, והאם המינוף שווה את זה.

השיטה מווקטרת ב-numpy, אלפי רצפי תשואה אקראיים, ומדווחת התפלגות שווי נטו (עיזבון).
"""
import numpy as np
import streamlit as st


def _simulate(P0, loan0, loan_rate, mean_ret, std_ret, years, annual_wd, wd_growth,
              home0, home_appr, buffer_cash, buffer_rate, call_ltv, side0=0.0,
              n_sims=4000, seed=12345):
    """P0 = התיק המושקע (צבירה + הלוואה). הריבית מצטברת לחוב (בלון). אם call_ltv גבוה
    מאוד, אין מכירה כפויה. מחזיר התפלגות שווי נטו = תיק + דירה − חוב."""
    rng = np.random.default_rng(seed)
    rets = rng.normal(mean_ret, std_ret, size=(n_sims, years))

    P = np.full(n_sims, float(P0))
    S = np.full(n_sims, float(side0))
    D = np.full(n_sims, float(loan0))
    buf = np.full(n_sims, float(buffer_cash))
    margin_called = np.zeros(n_sims, dtype=bool)
    wd = float(annual_wd)

    for y in range(years):
        from_buf = np.minimum(buf, wd)
        buf = (buf - from_buf) * (1 + buffer_rate)
        P = P - (wd - from_buf)
        P = P * (1 + rets[:, y])
        S = S * (1 + rets[:, y])
        D = D * (1 + loan_rate)
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
NO_FORCED_SALE = 99.0  # אין מכירה כפויה — לפי מה שהמלווה מסר


def margin_call_probability(user_inputs, std_ret=GEN_VOL, call_ltv=0.90, n_sims=2000):
    """נשמר לתאימות עם דוח ההשוואה. מחזיר הסתברות מכירה כפויה בהנחת סף (למקרה שכן קיים)."""
    tl = user_inputs.get("timeline", {}); ex = user_inputs.get("expenses", {})
    w = user_inputs.get("wealth", {}); a190 = user_inputs.get("amendment_190", {})
    lev = user_inputs.get("leverage", {})
    years = max(1, int(round(float(tl.get("check_age", 95)) - float(tl.get("start_age", 65)))))
    net_for_190 = float(a190.get("net_for_190", 0))
    home = float(w.get("new_apartment_cost", 5500000))
    loan = min(float(lev.get("loan_amount", 0)), home, 4.0 * net_for_190)
    if loan <= 0 or net_for_190 <= 0:
        return 0.0
    mean_ret = float(lev.get("annual_return_lev", GEN_RETURN)) - float(a190.get("management_fee_190", 0.005))
    monthly_deficit = max(0.0, float(ex.get("current_expenses", 11000))
                          - float(w.get("national_insurance", 2500))
                          - float(a190.get("desired_pension", 5306)))
    res = _simulate(net_for_190 + loan, loan, float(lev.get("loan_annual_rate", 0.045)), mean_ret, std_ret, years,
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

    def _m(x):
        return f"{x/1e6:.1f}מ"

    def _sec(txt):
        st.markdown(
            f"<div style='direction:rtl;text-align:right;font-weight:800;font-size:1.05em;"
            f"color:#1a1a2e;margin:14px 0 6px;'>{txt}</div>", unsafe_allow_html=True)

    # ============ כותרת והסבר ============
    _rtl(
        "<p style='line-height:1.7;'>המודל הרגיל מניח שהשוק עולה בקצב קבוע. כאן מריצים אלפי "
        "תרחישי שוק אקראיים כדי לראות את טווח התוצאות האמיתי.</p>"
        "<p style='line-height:1.7;color:#555;font-size:0.92em;'>לפי מה שהמלווה מסר, אין מכירה "
        "כפויה, ההלוואה מסוג בלון שנפרעת מהעיזבון (הריבית מצטברת לחוב), מסלול כללי, וניתן "
        "למחזר. לכן השאלה כאן היא לא סיכון מכירה, אלא <b>כמה יהיה שווה התיק בסוף</b>, עם "
        "מינוף מול בלי מינוף, והאם המינוף שווה את זה.</p>")

    # ============ נתונים ============
    tl = user_inputs.get("timeline", {}); ex = user_inputs.get("expenses", {})
    w = user_inputs.get("wealth", {}); a190 = user_inputs.get("amendment_190", {})
    lev = user_inputs.get("leverage", {})

    years = max(1, int(round(float(tl.get("check_age", 95.0)) - float(tl.get("start_age", 65.0)))))
    net_for_190 = float(a190.get("net_for_190", 0))
    home0 = float(w.get("new_apartment_cost", 5500000))
    home_appr = float(w.get("property_appreciation", 0.03))
    buffer_cash = float(w.get("emergency_fund", 250000))
    loan_rate = float(lev.get("loan_annual_rate", 0.045))
    gen_return = float(lev.get("annual_return_lev", GEN_RETURN))  # שדה תשואת מסלול כללי
    mean_ret = gen_return - float(a190.get("management_fee_190", 0.005))
    inflation = float(ex.get("expected_inflation", 0.023))
    annual_wd = max(0.0, float(ex.get("current_expenses", 11000))
                    - float(w.get("national_insurance", 2500))
                    - float(a190.get("desired_pension", 5306))) * 12

    # ============ ⚙️ הנחות המודל ============
    _sec("⚙️ הנחות המודל")
    std_ret = st.slider("תנודתיות שנתית של התיק, מסלול כללי (סטיית תקן %)",
                        min_value=5.0, max_value=20.0, value=GEN_VOL * 100, step=0.5,
                        help="מסלול כללי סביב 7-9%. מנייתי טהור 15%+.") / 100
    _rtl(
        f"<div style='color:#555;font-size:0.84em;line-height:1.6;margin-top:2px;'>"
        f"📌 תשואת התיק {gen_return*100:.1f}% ברוטו (כ-{mean_ret*100:.1f}% נטו) &nbsp;·&nbsp; "
        f"ריבית ההלוואה {loan_rate*100:.2f}% &nbsp;·&nbsp; אופק {years} שנים &nbsp;·&nbsp; "
        f"<b>ללא מכירה כפויה</b>, החוב מצטבר ונפרע מהעיזבון.</div>")

    # ============ חישובים — ללא מכירה כפויה ============
    loan_cap = min(home0, 3.0 * net_for_190)  # מימון עד 75% מהתיק (מסלול כללי, לפי המלווה)
    loan_steps = sorted(set(int(loan_cap * i / 10) for i in range(11)))
    rows = []
    for loan in loan_steps:
        res = _simulate(net_for_190 + loan, loan, loan_rate, mean_ret, std_ret, years, annual_wd,
                        inflation, home0, home_appr, buffer_cash, 0.02, NO_FORCED_SALE, n_sims=2500)
        rows.append((loan, res))
    base = rows[0][1]  # ללא מינוף
    b10, b50, b90 = base["nw_p10"], base["nw_p50"], base["nw_p90"]

    cur_loan = max(0.0, min(float(lev.get("loan_amount", 0)), loan_cap))
    cur = _simulate(net_for_190 + cur_loan, cur_loan, loan_rate, mean_ret, std_ret, years, annual_wd,
                    inflation, home0, home_appr, buffer_cash, 0.02, NO_FORCED_SALE, n_sims=4000)
    up50 = cur["nw_p50"] - b50
    up10 = cur["nw_p10"] - b10

    # ============ 1. כמה יהיה שווה התיק, ההלוואה שבחרת ============
    _sec("1️⃣ שווי התיק בסוף — ההלוואה שבחרת")
    _c1, _c2, _c3 = st.columns(3)
    _c1.metric("תרחיש גרוע (10%)", _m(cur["nw_p10"]), _m(up10))
    _c2.metric("חציון (אמצעי)", _m(cur["nw_p50"]), _m(up50))
    _c3.metric("תרחיש טוב (90%)", _m(cur["nw_p90"]), _m(cur["nw_p90"] - b90))

    if cur_loan <= 0:
        _rtl("<div style='background:#eafaf0;border:1px solid #8fd3a8;border-right:4px solid #1a7a3a;"
             "border-radius:8px;padding:12px 16px;color:#14532d;line-height:1.7;margin-top:6px;'>"
             f"ללא מינוף. שווי התיק הצפוי בגיל {tl.get('check_age',95):.0f}, חציון {_f(b50)}.</div>")
    else:
        _worth = up50 > 0 and up10 >= -0.15 * b10  # תוספת חיובית וללא פגיעה חריפה בתרחיש הגרוע
        _bg, _bd, _cl = (("#eafaf0", "#8fd3a8", "#14532d") if _worth else ("#fff8e1", "#f0c86a", "#5a4a1a"))
        _verdict = ("המינוף מוסיף בממוצע ולא פוגע קשה בתרחיש הגרוע, אז שווה לשקול אותו."
                    if _worth else
                    "המינוף מוסיף בממוצע, אבל פוגע בתרחיש הגרוע. זו פשרה, לא ארוחת חינם.")
        _rtl(
            f"<div style='background:{_bg};border:1px solid {_bd};border-right:4px solid {_bd};"
            f"border-radius:8px;padding:12px 16px;color:{_cl};line-height:1.9;margin-top:6px;'>"
            f"עם הלוואה של <b>{_f(cur_loan)}</b>, לעומת בלי מינוף:<br/>"
            f"💰 בתרחיש האמצעי, הירושה <b>{_f(cur['nw_p50'])}</b> במקום {_f(b50)}, "
            f"תוספת של <b>{'+' if up50>=0 else ''}{_f(up50)}</b>.<br/>"
            f"⚠️ בתרחיש הגרוע, <b>{_f(cur['nw_p10'])}</b> במקום {_f(b10)}, "
            f"שינוי של <b>{'+' if up10>=0 else ''}{_f(up10)}</b>.<br/>"
            f"⚖️ {_verdict}</div>")

    # ============ 2. שווי התיק לפי גודל ההלוואה ============
    st.divider()
    _sec("2️⃣ שווי התיק לפי גודל ההלוואה — כל הקשת")
    _rows_html = ""
    for loan, res in rows:
        d50 = res["nw_p50"] - b50
        dcol = "#1a7a3a" if d50 >= 0 else "#a83232"
        loan_lbl = "ללא מינוף" if loan == 0 else _f(loan)
        _rows_html += (
            f"<tr style='border-bottom:1px solid #eee;'>"
            f"<td style='padding:7px 12px;text-align:right;font-weight:800;'>{loan_lbl}</td>"
            f"<td style='padding:7px 12px;text-align:center;color:#a83232;'>{_m(res['nw_p10'])}</td>"
            f"<td style='padding:7px 12px;text-align:center;font-weight:700;'>{_m(res['nw_p50'])}</td>"
            f"<td style='padding:7px 12px;text-align:center;color:#1a7a3a;'>{_m(res['nw_p90'])}</td>"
            f"<td style='padding:7px 12px;text-align:center;font-weight:700;color:{dcol};'>{'+' if d50>=0 else ''}{_m(d50)}</td></tr>")
    with st.expander("📊 שווי התיק לכל גודל הלוואה (0 עד המקסימום)", expanded=True):
        st.markdown(
            f"<div style='direction:rtl;text-align:right;font-family:sans-serif;'>"
            f"<table dir='rtl' style='width:100%;border-collapse:collapse;font-size:0.9em;'>"
            f"<thead><tr style='background:#eef0f7;'>"
            f"<th style='padding:7px 12px;text-align:right;'>הלוואה</th>"
            f"<th style='padding:7px 12px;'>ירושה — גרוע (10%)</th>"
            f"<th style='padding:7px 12px;'>ירושה — חציון</th>"
            f"<th style='padding:7px 12px;'>ירושה — טוב (90%)</th>"
            f"<th style='padding:7px 12px;'>תוספת לחציון מול בלי מינוף</th></tr></thead>"
            f"<tbody>{_rows_html}</tbody></table></div>", unsafe_allow_html=True)
        _rtl(
            "<div style='color:#777;font-size:0.8em;line-height:1.6;margin-top:6px;'>"
            "כל הסכומים הם שווי נטו, תיק + דירה פחות החוב שהצטבר, בגיל הנבדק. תוספת חיובית "
            "לחציון פירושה שהמינוף הגדיל את הירושה הצפויה. שים לב לתרחיש הגרוע, שם רואים אם "
            "המינוף פוגע כשהתשואה מאכזבת.</div>")

    # ============ 3. גרף — שווי התיק מול גודל ההלוואה ============
    st.divider()
    _sec("3️⃣ שווי התיק מול גודל ההלוואה")
    rr = go.Figure()
    rr.add_trace(go.Scatter(x=[r[0] for r in rows], y=[r[1]["nw_p50"] / 1e6 for r in rows],
                            name="חציון (אמצעי)", mode="lines+markers",
                            line=dict(color="#1a7a3a", width=3)))
    rr.add_trace(go.Scatter(x=[r[0] for r in rows], y=[r[1]["nw_p10"] / 1e6 for r in rows],
                            name="תרחיש גרוע (10%)", mode="lines+markers",
                            line=dict(color="#c0392b", width=3, dash="dot")))
    rr.add_trace(go.Scatter(x=[r[0] for r in rows], y=[r[1]["nw_p90"] / 1e6 for r in rows],
                            name="תרחיש טוב (90%)", mode="lines+markers",
                            line=dict(color="#8a9ba8", width=2, dash="dot")))
    rr.update_layout(
        height=360, template="plotly_white", font=dict(family="sans-serif"),
        margin=dict(t=20, b=40, l=10, r=10),
        xaxis=dict(title="סכום ההלוואה (₪)"),
        yaxis=dict(title="שווי נטו (₪ מיליון)"),
        legend=dict(orientation="h", y=1.15, x=0, xanchor="left"))
    st.plotly_chart(rr, use_container_width=True)
    _rtl(
        "<div style='color:#777;font-size:0.82em;line-height:1.6;'>"
        "הקו הירוק הוא הירושה הצפויה. הקו האדום הוא התרחיש הגרוע. אם המינוף מגדיל את "
        "שניהם, הוא שווה. אם הוא מגדיל את הירוק אבל מוריד את האדום, זו פשרה בין ירושה גדולה "
        "יותר בממוצע לבין סיכון להשאיר פחות כשהתשואה מאכזבת.</div>")
