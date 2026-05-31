import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def render_charts(df_history):
    st.markdown("### 📈 ניתוח ויזואלי — התפתחות ההון לאורך הפרישה")
    st.divider()

    df = df_history.copy()

    COLORS = {
        "190":    "#2ca02c",
        "25":     "#1f77b4",
        "hybrid": "#ff7f0e",
        "rental": "#9467bd",
    }

    # =========================================================
    # Section 1: Liquid + Pension — two tabs
    # =========================================================
    tab1, tab2 = st.tabs(["💰 הון נזיל בלבד", "💎 הון כולל ערך קצבה"])

    with tab1:
        st.markdown("השוואת ההון הנזיל הגולמי — ללא ערך הקצבה — בכל מסלול לאורך השנים.")
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=df["גיל"], y=df["צבירה תיקון 190"],
            mode='lines', name='190 + קצבה מזערית',
            line=dict(color=COLORS["190"], width=2.5)
        ))
        fig1.add_trace(go.Scatter(
            x=df["גיל"], y=df["צבירה מסלול היברידי"],
            mode='lines', name='25% ריאלי + קצבה מזערית',
            line=dict(color=COLORS["hybrid"], width=2.5, dash='dash')
        ))
        fig1.add_trace(go.Scatter(
            x=df["גיל"], y=df["צבירה מסלול ריאלי"],
            mode='lines', name='25% ריאלי (ללא קצבה)',
            line=dict(color=COLORS["25"], width=2.5)
        ))
        fig1.update_layout(
            xaxis_title="גיל", yaxis_title="הון נזיל (₪)",
            hovermode="x unified", template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig1.update_traces(hovertemplate="%{y:,.0f} ₪")
        st.plotly_chart(fig1, use_container_width=True)

    with tab2:
        pension_asset = df["ערך קצבה נותר"] if "ערך קצבה נותר" in df.columns else pd.Series(0, index=df.index)

        st.markdown(
            "הקו המלא = הון נזיל + ערך הקצבה הנותר. "
            "הקו המקווקו = הון נזיל בלבד. "
            "השטח הצבוע בין השניים = כסף הכלוא בקצבה — **'הבור' נעלם עם סיום תקופת ההבטחה.**"
        )
        fig2 = go.Figure()

        # Track 1 — 190: solid line = total, dashed = liquid, shaded gap = pension
        total_190 = df["צבירה תיקון 190"] + pension_asset
        fig2.add_trace(go.Scatter(
            x=df["גיל"], y=total_190,
            mode='lines', name='190 + קצבה — סה"כ',
            line=dict(color=COLORS["190"], width=2.5)
        ))
        fig2.add_trace(go.Scatter(
            x=df["גיל"], y=df["צבירה תיקון 190"],
            mode='lines', name='190 — הון נזיל',
            line=dict(color=COLORS["190"], width=1.5, dash='dash'),
            fill='tonexty', fillcolor='rgba(44,160,44,0.18)'
        ))

        # Track 3 — hybrid: solid = total, dashed = liquid, shaded gap = pension
        total_hybrid = df["צבירה מסלול היברידי"] + pension_asset
        fig2.add_trace(go.Scatter(
            x=df["גיל"], y=total_hybrid,
            mode='lines', name='25% ריאלי + קצבה — סה"כ',
            line=dict(color=COLORS["hybrid"], width=2.5)
        ))
        fig2.add_trace(go.Scatter(
            x=df["גיל"], y=df["צבירה מסלול היברידי"],
            mode='lines', name='25% ריאלי + קצבה — נזיל',
            line=dict(color=COLORS["hybrid"], width=1.5, dash='dash'),
            fill='tonexty', fillcolor='rgba(255,127,14,0.18)'
        ))

        # Track 2 — no pension, just liquid line
        fig2.add_trace(go.Scatter(
            x=df["גיל"], y=df["צבירה מסלול ריאלי"],
            mode='lines', name='25% ריאלי (ללא קצבה)',
            line=dict(color=COLORS["25"], width=2.5)
        ))

        fig2.update_layout(
            xaxis_title="גיל", yaxis_title="הון (₪)",
            hovermode="x unified", template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig2.update_traces(hovertemplate="%{y:,.0f} ₪")
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # =========================================================
    # Section 2: Annual tax paid per track (aggregate monthly → yearly)
    # =========================================================
    st.subheader("🧾 מס שנתי ששולם — השוואת מסלולים")
    st.markdown("סך המס ששולם בכל שנת גיל — אפקט מגן המס של תיקון 190 אל מול 25% ריאלי.")

    df_annual = (
        df.assign(age_floor=df["גיל"].astype(int))
          .groupby("age_floor", as_index=False)
          .agg({
              "מס ששולם 190":     "sum",
              "מס ששולם 25":      "sum",
              "מס ששולם היברידי": "sum",
          })
          .rename(columns={"age_floor": "גיל"})
    )

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=df_annual["גיל"], y=df_annual["מס ששולם 190"],    mode='lines', name='190 + קצבה מזערית',       line=dict(color=COLORS["190"],    width=2.5)))
    fig3.add_trace(go.Scatter(x=df_annual["גיל"], y=df_annual["מס ששולם היברידי"], mode='lines', name='25% ריאלי + קצבה מזערית', line=dict(color=COLORS["hybrid"], width=2.5, dash='dash')))
    fig3.add_trace(go.Scatter(x=df_annual["גיל"], y=df_annual["מס ששולם 25"],     mode='lines', name='25% ריאלי (ללא קצבה)',    line=dict(color=COLORS["25"],     width=2.5)))
    fig3.update_layout(
        xaxis_title="גיל", yaxis_title="מס שנתי (₪)",
        hovermode="x unified", template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig3.update_traces(hovertemplate="%{y:,.0f} ₪")
    st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    # =========================================================
    # Section 3: Total net worth including real estate
    # =========================================================
    st.subheader("🏢 שווי כולל נכסים — הון נזיל + נדל\"ן")
    st.markdown("מבט הוליסטי: תיק נזיל + שווי הנכס הנדל\"ני של כל מסלול.")

    df_nw = df.copy()
    df_nw["nw_190"]    = df_nw["צבירה תיקון 190"]      + df_nw["שווי נדלן"]
    df_nw["nw_25"]     = df_nw["צבירה מסלול ריאלי"]    + df_nw["שווי נדלן"]
    df_nw["nw_hybrid"] = df_nw["צבירה מסלול היברידי"]  + df_nw["שווי נדלן"]

    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(
        x=df_nw["גיל"], y=df_nw["nw_190"],
        mode='lines', name='190 + קצבה מזערית',
        line=dict(color=COLORS["190"], width=3)
    ))
    fig4.add_trace(go.Scatter(
        x=df_nw["גיל"], y=df_nw["nw_hybrid"],
        mode='lines', name='25% ריאלי + קצבה מזערית',
        line=dict(color=COLORS["hybrid"], width=3, dash='dash')
    ))
    fig4.add_trace(go.Scatter(
        x=df_nw["גיל"], y=df_nw["nw_25"],
        mode='lines', name='25% ריאלי (ללא קצבה)',
        line=dict(color=COLORS["25"], width=3)
    ))
    fig4.update_layout(
        xaxis_title="גיל", yaxis_title="שווי נכסים כולל (₪)",
        hovermode="x unified", template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig4.update_traces(hovertemplate="%{y:,.0f} ₪")
    st.plotly_chart(fig4, use_container_width=True)
