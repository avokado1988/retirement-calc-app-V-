import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

COLORS = {
    "190":    "#2ca02c",
    "25":     "#1f77b4",
    "hybrid": "#ff7f0e",
    "rental": "#9467bd",
}

TRACK_NAMES = {
    "190":    "190 + קצבה מזערית",
    "25":     "25% ריאלי (ללא קצבה)",
    "hybrid": "25% ריאלי + קצבה מזערית",
    "rental": "מסלול נדל\"ן (שכירות)",
}

COL_MAP = {
    "190":    "צבירה תיקון 190",
    "25":     "צבירה מסלול ריאלי",
    "hybrid": "צבירה מסלול היברידי",
    "rental": "צבירה מסלול שכירות",
}

TAX_COL = {
    "190":    "מס ששולם 190",
    "25":     "מס ששולם 25",
    "hybrid": "מס ששולם היברידי",
    "rental": "מס רווח הון — משיכה מתיק",
}

EXPENSE_COL = "הוצאה נומינלית"
INCOME_COL  = "הכנסה נומינלית"
PENSION_COL = "הכנסה מקצבה מזערית"


def _track_selector(key_prefix):
    st.markdown("**בחר מסלולים להצגה:**")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        show_190    = st.checkbox(TRACK_NAMES["190"],    value=True,  key=f"{key_prefix}_190")
    with c2:
        show_25     = st.checkbox(TRACK_NAMES["25"],     value=True,  key=f"{key_prefix}_25")
    with c3:
        show_h      = st.checkbox(TRACK_NAMES["hybrid"], value=True,  key=f"{key_prefix}_hybrid")
    with c4:
        show_rental = st.checkbox(TRACK_NAMES["rental"], value=False, key=f"{key_prefix}_rental")
    active = []
    if show_190:    active.append("190")
    if show_25:     active.append("25")
    if show_h:      active.append("hybrid")
    if show_rental: active.append("rental")
    return active


def render_charts(df_history, user_inputs):
    st.markdown("### 📈 ניתוח ויזואלי — התפתחות ההון לאורך הפרישה")
    st.divider()

    df = df_history.copy()

    # Guarantee end age for vertical line
    try:
        timeline = user_inputs.get("timeline", {})
        amendment = user_inputs.get("amendment_190", {})
        retirement_age = float(timeline.get("retirement_age", 67.0))
        securing_years = float(amendment.get("securing_years", 20))
        guarantee_end_age = retirement_age + securing_years
    except Exception:
        guarantee_end_age = None

    pension_asset = df["ערך קצבה נותר"] if "ערך קצבה נותר" in df.columns else pd.Series(0, index=df.index)

    # =========================================================
    # Chart A: Liquid portfolio comparison
    # =========================================================
    st.subheader("א) השוואת תיקים — הון נזיל בלבד")
    st.markdown("ההון הנזיל הגולמי של כל מסלול ללא ערך הקצבה.")
    active_a = _track_selector("a")

    fig_a = go.Figure()
    for tid in active_a:
        fig_a.add_trace(go.Scatter(
            x=df["גיל"], y=df[COL_MAP[tid]],
            mode='lines', name=TRACK_NAMES[tid],
            line=dict(color=COLORS[tid], width=2.5,
                      dash='dash' if tid == "hybrid" else 'solid')
        ))
    fig_a.update_layout(
        xaxis_title="גיל", yaxis_title="הון נזיל (₪)",
        hovermode="x unified", template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig_a.update_traces(hovertemplate="%{y:,.0f} ₪")
    st.plotly_chart(fig_a, use_container_width=True)

    st.divider()

    # =========================================================
    # Chart B: Total net worth — liquid portfolio + real estate (− RM debt)
    # =========================================================
    st.subheader("ב) סך השווי הנקי — תיק נזיל + נדל\"ן (השורה התחתונה)")
    st.markdown(
        "כמה אתה שווה בסך הכל בכל גיל: התיק הנזיל **בתוספת** שווי הנדל\"ן. "
        "במסלול 4 מנוכה חוב המשכנתה ההפוכה (הון עצמי נטו). "
        "זו ההשוואה ההוגנת — תפוחים מול תפוחים."
    )
    st.caption(
        "💡 השוואת קצבה: מסלול 2 (ללא קצבה — הכל נזיל) מול מסלול 3 (חלק הומר לקצבה) "
        "מראה כיצד המרת הון לקצבה משפיעה על סך השווי."
    )
    active_b = _track_selector("b")

    # Per-track total net worth series
    own_property = df["שווי נדלן"] if "שווי נדלן" in df.columns else pd.Series(0, index=df.index)
    rental_property = df["שווי נדלן מסלול 4"] if "שווי נדלן מסלול 4" in df.columns else pd.Series(0, index=df.index)
    rm_debt = df["משכנתה הפוכה — יתרת חוב"] if "משכנתה הפוכה — יתרת חוב" in df.columns else pd.Series(0, index=df.index)

    def total_networth(tid):
        liq = df[COL_MAP[tid]]
        if tid == "rental":
            return liq + (rental_property - rm_debt).clip(lower=0)
        return liq + own_property

    fig_b = go.Figure()
    for tid in active_b:
        fig_b.add_trace(go.Scatter(
            x=df["גיל"], y=total_networth(tid),
            mode='lines', name=TRACK_NAMES[tid],
            line=dict(color=COLORS[tid], width=2.5,
                      dash='dash' if tid == "hybrid" else 'solid')
        ))

    fig_b.update_layout(
        xaxis_title="גיל", yaxis_title="סך שווי נקי (₪)",
        hovermode="x unified", template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig_b.update_traces(hovertemplate="%{y:,.0f} ₪")
    st.plotly_chart(fig_b, use_container_width=True)

    st.divider()

    # =========================================================
    # Chart C: Annual tax paid
    # =========================================================
    st.subheader("ג) מס שנתי ששולם — השוואת מסלולים")
    st.markdown("סך המס ששולם בכל שנת גיל — אפקט מגן המס של תיקון 190 אל מול 25% ריאלי.")
    active_c = _track_selector("c")

    agg_dict = {TAX_COL[tid]: "sum" for tid in ["190", "25", "hybrid", "rental"]}
    df_annual = (
        df.assign(age_floor=df["גיל"].astype(int))
          .groupby("age_floor", as_index=False)
          .agg(agg_dict)
          .rename(columns={"age_floor": "גיל"})
    )

    fig_c = go.Figure()
    for tid in active_c:
        fig_c.add_trace(go.Scatter(
            x=df_annual["גיל"], y=df_annual[TAX_COL[tid]],
            mode='lines', name=TRACK_NAMES[tid],
            line=dict(color=COLORS[tid], width=2.5,
                      dash='dash' if tid == "hybrid" else 'solid')
        ))
    fig_c.update_layout(
        xaxis_title="גיל", yaxis_title="מס שנתי (₪)",
        hovermode="x unified", template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig_c.update_traces(hovertemplate="%{y:,.0f} ₪")
    st.plotly_chart(fig_c, use_container_width=True)

    st.divider()

    # =========================================================
    # Chart D: Portfolio pressure — annual withdrawal needed
    # =========================================================
    st.subheader("ד) לחץ על התיק — כמה צריך להשלים מהחיסכון מדי שנה")
    st.markdown(
        "כמה כסף כל מסלול נאלץ למשוך מהחיסכון בכל שנה כדי לכסות את הגירעון בין הוצאות להכנסות. "
        "ככל שהעמודה גבוהה יותר — כך התיק נשחק מהר יותר."
    )
    active_d = _track_selector("d")

    df_press = df.copy()
    pension_income  = df_press[PENSION_COL] if PENSION_COL in df_press.columns else 0
    rental_net_col  = "הכנסת שכירות נטו" if "הכנסת שכירות נטו" in df_press.columns else None
    rent_paid_col   = "הוצאת שכירות"      if "הוצאת שכירות"      in df_press.columns else None
    rental_income   = df_press[rental_net_col] if rental_net_col else 0
    rent_paid       = df_press[rent_paid_col]   if rent_paid_col   else 0
    df_press["withdrawal_190"]    = (df_press[EXPENSE_COL] - (df_press[INCOME_COL] + pension_income)).clip(lower=0)
    df_press["withdrawal_25"]     = (df_press[EXPENSE_COL] - df_press[INCOME_COL]).clip(lower=0)
    df_press["withdrawal_hybrid"] = (df_press[EXPENSE_COL] - (df_press[INCOME_COL] + pension_income)).clip(lower=0)
    df_press["withdrawal_rental"] = (df_press[EXPENSE_COL] + rent_paid - (df_press[INCOME_COL] + rental_income)).clip(lower=0)

    df_press_annual = (
        df_press.assign(age_floor=df_press["גיל"].astype(int))
        .groupby("age_floor", as_index=False)
        .agg({"withdrawal_190": "sum", "withdrawal_25": "sum", "withdrawal_hybrid": "sum", "withdrawal_rental": "sum"})
        .rename(columns={"age_floor": "גיל"})
    )

    WITHDRAWAL_COL = {"190": "withdrawal_190", "25": "withdrawal_25", "hybrid": "withdrawal_hybrid", "rental": "withdrawal_rental"}

    fig_d = go.Figure()
    for tid in active_d:
        fig_d.add_trace(go.Scatter(
            x=df_press_annual["גיל"],
            y=df_press_annual[WITHDRAWAL_COL[tid]],
            mode='lines', name=TRACK_NAMES[tid],
            line=dict(color=COLORS[tid], width=2.5,
                      dash='dash' if tid == "hybrid" else 'solid')
        ))
    fig_d.update_layout(
        xaxis_title="גיל", yaxis_title="משיכה שנתית נדרשת (₪)",
        hovermode="x unified", template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig_d.update_traces(hovertemplate="%{y:,.0f} ₪")
    st.plotly_chart(fig_d, use_container_width=True)

    # =========================================================
    # Chart E: Track 4 dedicated — monthly cashflow renter/landlord,
    # with an optional reverse-mortgage overlay (toggle on/off).
    # =========================================================
    if "תזרים נטו שכירות" in df.columns:
        st.divider()
        st.subheader("ה) מסלול 4 — תזרים חודשי: שוכר ומשכיר, עם/בלי משכנתה הפוכה")
        st.markdown(
            "התזרים החודשי נטו: הכנסות (שכ\"ד שאתה גובה + ביטוח לאומי) פחות הוצאות "
            "(מחיה + שכ\"ד שאתה משלם + תחזוקה). מעל הקו = עודף, מתחת לקו = גירעון שנמשך מהחיסכון."
        )

        rental_cfg = user_inputs.get("rental", {})
        add_rm = st.checkbox(
            "➕ הצג גם תזרים עם משכנתה הפוכה",
            value=bool(rental_cfg.get("rm_enabled", False)),
            key="chart_e_add_rm"
        )

        base_cf = df["תזרים נטו שכירות"]

        fig_e = go.Figure()
        # Zero reference line
        fig_e.add_hline(y=0, line_dash="dot", line_color="#aaa")
        fig_e.add_trace(go.Scatter(
            x=df["גיל"], y=base_cf,
            mode='lines', name="ללא משכנתה",
            line=dict(color="#9467bd", width=2.5)
        ))

        if add_rm:
            # Compute the reverse-mortgage annuity inline (same formula as the
            # input preview): M = net_loan / n_months, paid start_age → life_exp.
            rm_loan = float(rental_cfg.get("rm_loan_amount_ils", 0) or 0)
            rm_fee = float(rental_cfg.get("rm_origination_fee", 0.02))
            rm_start = float(rental_cfg.get("rm_start_age", 72))
            rm_life = float(rental_cfg.get("rm_life_expectancy_age", 92))
            net_loan = rm_loan * (1 - rm_fee)
            n_months = max(1.0, (rm_life - rm_start) * 12)
            monthly_annuity = net_loan / n_months if rm_loan > 0 else 0.0

            ages = df["גיל"]
            annuity_series = ages.apply(
                lambda a: monthly_annuity if (rm_start <= a < rm_life) else 0.0
            )
            cf_with_rm = base_cf + annuity_series

            fig_e.add_trace(go.Scatter(
                x=ages, y=cf_with_rm,
                mode='lines', name="עם משכנתה הפוכה",
                line=dict(color="#2ca02c", width=2.5)
            ))
            # Mark the payment window
            fig_e.add_vline(x=rm_start, line_dash="dot", line_color="#2ca02c",
                            annotation_text=f"תחילת קצבה (גיל {rm_start:.0f})",
                            annotation_position="top left")
            fig_e.add_vline(x=rm_life, line_dash="dot", line_color="#c0392b",
                            annotation_text=f"תום תקופה (גיל {rm_life:.0f})",
                            annotation_position="top right")
            if rm_loan > 0:
                st.caption(
                    f"💰 קצבה חודשית מהמשכנתה: ₪{monthly_annuity:,.0f} "
                    f"(מגיל {rm_start:.0f} עד {rm_life:.0f}). "
                    f"שים לב לקפיצת התזרים כלפי מעלה בתקופה זו, ולחזרה לרמה הקודמת בתום התקופה."
                )
            else:
                st.caption("⚠️ לא הוגדר סכום הלוואה — הזן סכום בקלט מסלול 4 כדי לראות את ההשפעה.")

        fig_e.update_layout(
            xaxis_title="גיל", yaxis_title="תזרים חודשי נטו (₪)",
            hovermode="x unified", template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig_e.update_traces(hovertemplate="%{y:,.0f} ₪")
        st.plotly_chart(fig_e, use_container_width=True)
