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
    # Chart B: Total including pension value + guarantee line
    # =========================================================
    st.subheader("ב) הון כולל ערך הקצבה — כולל ה'בור' בסיום תקופת ההבטחה")
    st.markdown(
        "קו מלא = הון נזיל + ערך הקצבה הנותר. "
        "קו מקווקו = הון נזיל בלבד. "
        "השטח הצבוע = כסף הכלוא בקצבה שנעלם עם סיום ההבטחה."
    )
    active_b = _track_selector("b")

    fig_b = go.Figure()
    for tid in active_b:
        liq_col = COL_MAP[tid]
        has_pension = tid in ("190", "hybrid")
        if has_pension:
            total = df[liq_col] + pension_asset
            r, g, b = int(COLORS[tid][1:3], 16), int(COLORS[tid][3:5], 16), int(COLORS[tid][5:7], 16)
            fig_b.add_trace(go.Scatter(
                x=df["גיל"], y=total,
                mode='lines', name=f'{TRACK_NAMES[tid]} — סה"כ',
                line=dict(color=COLORS[tid], width=2.5)
            ))
            fig_b.add_trace(go.Scatter(
                x=df["גיל"], y=df[liq_col],
                mode='lines', name=f'{TRACK_NAMES[tid]} — נזיל',
                line=dict(color=COLORS[tid], width=1.5, dash='dash'),
                fill='tonexty', fillcolor=f'rgba({r},{g},{b},0.18)'
            ))
        else:
            fig_b.add_trace(go.Scatter(
                x=df["גיל"], y=df[liq_col],
                mode='lines', name=TRACK_NAMES[tid],
                line=dict(color=COLORS[tid], width=2.5)
            ))

    if guarantee_end_age:
        fig_b.add_vline(
            x=guarantee_end_age, line_dash="dot", line_color="gray",
            annotation_text=f"סיום הבטחה (גיל {guarantee_end_age:.0f})",
            annotation_position="top right"
        )

    fig_b.update_layout(
        xaxis_title="גיל", yaxis_title="הון (₪)",
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
