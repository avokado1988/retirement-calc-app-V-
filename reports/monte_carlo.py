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
    st.subheader("🎲 ניתוח סיכון — מונטה קרלו למסלול המינוף")
    st.markdown(
        "המודל הרגיל מניח תשואה קבועה, ולכן לעולם לא יראה מפולת. כאן מריצים אלפי "
        "תרחישי שוק אקראיים, ובודקים לכל גודל הלוואה מה ההסתברות שתהיה דרישת ביטחונות "
        "(מכירת התיק בהפסד), וכמה שווה הירושה בתרחיש גרוע, חציוני וטוב."
    )

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

    c1, c2 = st.columns(2)
    with c1:
        std_ret = st.slider("תנודתיות שנתית של התיק (סטיית תקן %)",
                            min_value=6.0, max_value=25.0, value=12.0, step=0.5,
                            help="תיק סולידי מפוזר סביב 10-12%. מנייתי טהור 18%+.") / 100
    with c2:
        call_ltv = st.slider("סף מכירה (LTV שבו הבנק מוכר %)",
                             min_value=70.0, max_value=95.0, value=85.0, step=1.0,
                             help="מעל שיעור המימון המקסימלי (75%). כשהיחס חוצה אותו — מכירה כפויה.") / 100

    home_price = home0
    loan_steps = [0, int(home_price*0.2), int(home_price*0.4), int(home_price*0.6),
                  int(home_price*0.8), int(home_price)]

    rows = []
    for loan in loan_steps:
        P0 = net_for_190 + loan
        ltv0 = (loan / P0 * 100) if P0 > 0 else 0
        res = _simulate(P0, loan, loan_rate, mean_ret, std_ret, years, annual_wd, inflation,
                        home0, home_appr, buffer_cash, 0.02, call_ltv)
        rows.append((loan, ltv0, res))

    def _f(x):
        return f"₪{x:,.0f}"

    header = (
        "<tr style='background:#eef0f7;'>"
        "<th style='padding:6px 10px;text-align:right;'>הלוואה</th>"
        "<th style='padding:6px 10px;'>מינוף התחלתי</th>"
        "<th style='padding:6px 10px;'>סיכון דרישת ביטחונות</th>"
        "<th style='padding:6px 10px;'>ירושה — תרחיש גרוע (10%)</th>"
        "<th style='padding:6px 10px;'>ירושה — חציון</th>"
        "<th style='padding:6px 10px;'>ירושה — תרחיש טוב (90%)</th></tr>"
    )
    body = ""
    for loan, ltv0, res in rows:
        p = res["p_margin_call"]
        risk_color = "#1a7a3a" if p < 0.05 else ("#b07800" if p < 0.15 else "#a83232")
        risk_label = "נמוך" if p < 0.05 else ("בינוני" if p < 0.15 else "גבוה")
        loan_lbl = "ללא מינוף (מסלול 1)" if loan == 0 else _f(loan)
        body += (
            f"<tr style='border-bottom:1px solid #eee;'>"
            f"<td style='padding:6px 10px;text-align:right;font-weight:600;'>{loan_lbl}</td>"
            f"<td style='padding:6px 10px;text-align:center;'>{ltv0:.0f}%</td>"
            f"<td style='padding:6px 10px;text-align:center;color:{risk_color};font-weight:700;'>{p*100:.0f}% ({risk_label})</td>"
            f"<td style='padding:6px 10px;text-align:center;color:#a83232;'>{_f(res['nw_p10'])}</td>"
            f"<td style='padding:6px 10px;text-align:center;font-weight:700;'>{_f(res['nw_p50'])}</td>"
            f"<td style='padding:6px 10px;text-align:center;color:#1a7a3a;'>{_f(res['nw_p90'])}</td></tr>"
        )

    st.markdown(
        f"<div style='direction:rtl;font-family:sans-serif;'>"
        f"<table style='width:100%;border-collapse:collapse;font-size:0.85em;'>"
        f"<thead>{header}</thead><tbody>{body}</tbody></table></div>",
        unsafe_allow_html=True
    )

    st.caption(
        f"על בסיס {years} שנים, תשואה ממוצעת {mean_ret*100:.1f}%, ריבית הלוואה {loan_rate*100:.2f}%, "
        f"וכרית מזומן {_f(buffer_cash)}. סיכון דרישת ביטחונות = אחוז התרחישים שבהם השוק צנח מספיק "
        f"כדי לחצות את סף המכירה ולאלץ מכירת התיק."
    )
    st.info(
        "💡 איך קוראים את זה: חפש את שורת ההלוואה הגבוהה ביותר שבה הסיכון עדיין נמוך (ירוק). "
        "זו רמת המינוף ההגיונית. מעליה, הירושה הצפויה גדלה אך הסיכון למכירה כפויה בהפסד קופץ."
    )
