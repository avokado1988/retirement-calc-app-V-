import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def render_charts(df_history):
    st.markdown("### 📈 ניתוח אקטוארי ויזואלי")
    st.markdown("גלול מטה כדי לראות את התנהגות התיק מכמה זוויות שונות.")
    st.divider()

    # =========================================================
    # Graph 1: Capital development — all 4 tracks
    # =========================================================
    st.subheader("💰 1. התפתחות ההון הנזיל — 4 מסלולים")
    st.markdown("השוואת יתרת ההון הנזיל בכל אחד מ-4 המסלולים לאורך שנות הפרישה.")
    fig1 = go.Figure()

    fig1.add_trace(go.Scatter(
        x=df_history["גיל"], y=df_history["צבירה תיקון 190"],
        mode='lines', name='מסלול 1 — תיקון 190',
        line=dict(color='#2ca02c', width=3),
        fill='tozeroy', fillcolor='rgba(44, 160, 44, 0.08)'
    ))
    fig1.add_trace(go.Scatter(
        x=df_history["גיל"], y=df_history["צבירה מסלול ריאלי"],
        mode='lines', name='מסלול 2 — 25% ריאלי',
        line=dict(color='#1f77b4', width=3),
        fill='tozeroy', fillcolor='rgba(31, 119, 180, 0.08)'
    ))
    fig1.add_trace(go.Scatter(
        x=df_history["גיל"], y=df_history["צבירה מסלול היברידי"],
        mode='lines', name='מסלול 3 — קצבה + 25% ריאלי',
        line=dict(color='#ff7f0e', width=3, dash='dash'),
        fill='tozeroy', fillcolor='rgba(255, 127, 14, 0.08)'
    ))
    fig1.add_trace(go.Scatter(
        x=df_history["גיל"], y=df_history["צבירה מסלול שכירות"],
        mode='lines', name='מסלול 4 — שכירות',
        line=dict(color='#9467bd', width=3, dash='dot'),
        fill='tozeroy', fillcolor='rgba(148, 103, 189, 0.08)'
    ))

    fig1.update_layout(
        xaxis_title="גיל", yaxis_title="הון נזיל (₪)",
        hovermode="x unified", template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig1.update_traces(hovertemplate="%{y:,.0f} ₪")
    st.plotly_chart(fig1, use_container_width=True)

    st.divider()

    # =========================================================
    # Graph 2: Cash flow puzzle (tracks 1 and 3 — pension-based)
    # =========================================================
    st.subheader("⚖️ 2. פאזל מימון המחיה — השוואת מסלולים")

    tab_c1, tab_c2 = st.tabs(["מסלולים 1 ו-3 (קצבה)", "מסלול 4 (שכירות)"])

    with tab_c1:
        st.markdown("הכנסות קבועות (ירוק), קצבה (כחול), **גירעון שנמשך מחסכונות (אדום)**.")
        fig2a = go.Figure()
        fig2a.add_trace(go.Scatter(x=df_history["גיל"], y=df_history["הכנסה נומינלית"],
            mode='none', name='הכנסה קבועה (ב"ל / עבודה)',
            fill='tozeroy', stackgroup='one', fillcolor='rgba(44, 160, 44, 0.6)'))
        fig2a.add_trace(go.Scatter(x=df_history["גיל"], y=df_history["הכנסה מקצבה מזערית"],
            mode='none', name='קצבת תיקון 190 / היברידי',
            fill='tonexty', stackgroup='one', fillcolor='rgba(31, 119, 180, 0.6)'))
        gap1 = (df_history["הוצאה נומינלית"] - (df_history["הכנסה נומינלית"] + df_history["הכנסה מקצבה מזערית"])).clip(lower=0)
        fig2a.add_trace(go.Scatter(x=df_history["גיל"], y=gap1,
            mode='none', name='משיכה מחסכונות (גירעון)',
            fill='tonexty', stackgroup='one', fillcolor='rgba(214, 39, 40, 0.5)'))
        fig2a.add_trace(go.Scatter(x=df_history["גיל"], y=df_history["הוצאה נומינלית"],
            mode='lines', name='סך הוצאות', line=dict(color='black', width=2, dash='dot')))
        max_y1 = df_history["הוצאה נומינלית"].quantile(0.95) * 1.3
        fig2a.update_layout(xaxis_title="גיל", yaxis_title="סכום חודשי (₪)",
            yaxis=dict(range=[0, max_y1]), hovermode="x unified", template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        fig2a.update_traces(hovertemplate="%{y:,.0f} ₪")
        st.plotly_chart(fig2a, use_container_width=True)

    with tab_c2:
        st.markdown("הכנסות (ירוק = ב\"ל + שכירות נטו), **גירעון (אדום) = הוצאות מחיה + שכירות תשלום פחות הכנסות**.")
        fig2b = go.Figure()
        total_income_4 = df_history["הכנסה נומינלית"] + df_history.get("הכנסת שכירות נטו", 0)
        total_expense_4 = df_history["הוצאה נומינלית"] + df_history.get("הוצאת שכירות", 0)
        fig2b.add_trace(go.Scatter(x=df_history["גיל"], y=total_income_4,
            mode='none', name='סך הכנסות (ב"ל + שכירות נטו)',
            fill='tozeroy', stackgroup='one', fillcolor='rgba(44, 160, 44, 0.6)'))
        gap4 = (total_expense_4 - total_income_4).clip(lower=0)
        fig2b.add_trace(go.Scatter(x=df_history["גיל"], y=gap4,
            mode='none', name='גירעון — משיכה מחסכונות',
            fill='tonexty', stackgroup='one', fillcolor='rgba(214, 39, 40, 0.5)'))
        fig2b.add_trace(go.Scatter(x=df_history["גיל"], y=total_expense_4,
            mode='lines', name='סך הוצאות (מחיה + שכירות)', line=dict(color='black', width=2, dash='dot')))
        max_y2 = total_expense_4.quantile(0.95) * 1.3
        fig2b.update_layout(xaxis_title="גיל", yaxis_title="סכום חודשי (₪)",
            yaxis=dict(range=[0, max_y2]), hovermode="x unified", template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        fig2b.update_traces(hovertemplate="%{y:,.0f} ₪")
        st.plotly_chart(fig2b, use_container_width=True)

    st.divider()

    # =========================================================
    # Graph 3: Cumulative tax — all 4 tracks
    # =========================================================
    st.subheader("🛡️ 3. סך מס רווחי הון ששולם (מצטבר) — 4 מסלולים")
    st.markdown("אפקט מגן המס של תיקון 190 אל מול גביית 25% ריאלי במסלולים האחרים.")

    df_tax = df_history.copy()
    df_tax['cum_190'] = df_tax['מס ששולם 190'].cumsum()
    df_tax['cum_25'] = df_tax['מס ששולם 25'].cumsum()
    df_tax['cum_hybrid'] = df_tax['מס ששולם היברידי'].cumsum()
    df_tax['cum_rental'] = df_tax['מס ששולם שכירות'].cumsum()

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=df_tax["גיל"], y=df_tax["cum_190"], mode='lines', name='מסלול 1 — 190', line=dict(color='#2ca02c', width=3)))
    fig3.add_trace(go.Scatter(x=df_tax["גיל"], y=df_tax["cum_25"], mode='lines', name='מסלול 2 — 25% ריאלי', line=dict(color='#1f77b4', width=3)))
    fig3.add_trace(go.Scatter(x=df_tax["גיל"], y=df_tax["cum_hybrid"], mode='lines', name='מסלול 3 — היברידי', line=dict(color='#ff7f0e', width=3, dash='dash')))
    fig3.add_trace(go.Scatter(x=df_tax["גיל"], y=df_tax["cum_rental"], mode='lines', name='מסלול 4 — שכירות', line=dict(color='#9467bd', width=3, dash='dot')))

    fig3.update_layout(
        xaxis_title="גיל", yaxis_title="סך מס ששולם (₪)",
        hovermode="x unified", template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig3.update_traces(hovertemplate="%{y:,.0f} ₪")
    st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    # =========================================================
    # Graph 4: Net worth — liquid + real estate
    # =========================================================
    st.subheader("🏢 4. שווי נקי כולל — הון נזיל + נדל\"ן")
    st.markdown("מבט הוליסטי: מסלול 4 מציג גם את הנכס המושכר, לעומת מסלולים 1-3 שמציגים את הדירה הנרכשת.")

    df_nw = df_history.copy()
    df_nw['nw_190'] = df_nw['צבירה תיקון 190'] + df_nw['שווי נדלן']
    df_nw['nw_25'] = df_nw['צבירה מסלול ריאלי'] + df_nw['שווי נדלן']
    df_nw['nw_hybrid'] = df_nw['צבירה מסלול היברידי'] + df_nw['שווי נדלן']
    df_nw['nw_rental'] = df_nw['צבירה מסלול שכירות'] + df_nw['שווי נדלן מסלול 4']

    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=df_nw["גיל"], y=df_nw["nw_190"], mode='lines', name='מסלול 1 — 190', line=dict(color='#2ca02c', width=3, dash='dot')))
    fig4.add_trace(go.Scatter(x=df_nw["גיל"], y=df_nw["nw_25"], mode='lines', name='מסלול 2 — 25% ריאלי', line=dict(color='#1f77b4', width=3, dash='dot')))
    fig4.add_trace(go.Scatter(x=df_nw["גיל"], y=df_nw["nw_hybrid"], mode='lines', name='מסלול 3 — היברידי', line=dict(color='#ff7f0e', width=3, dash='dash')))
    fig4.add_trace(go.Scatter(x=df_nw["גיל"], y=df_nw["nw_rental"], mode='lines', name='מסלול 4 — שכירות (כולל נכס)', line=dict(color='#9467bd', width=3)))

    fig4.update_layout(
        xaxis_title="גיל", yaxis_title="שווי נכסים כולל (₪)",
        hovermode="x unified", template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig4.update_traces(hovertemplate="%{y:,.0f} ₪")
    st.plotly_chart(fig4, use_container_width=True)

    st.divider()

    # =========================================================
    # Graph 5: Inheritance value — liquid + pension guarantee
    # =========================================================
    st.subheader("🏆 5. שווי ירושה כולל — תיק נזיל + ערך הבטחת הקצבה")
    st.markdown("מסלולים 1 ו-3 כוללים את ערך הבטחת הקצבה לירושה (נשחק לאפס בסיום תקופת ההבטחה).")

    fig5 = go.Figure()
    fig5.add_trace(go.Scatter(
        x=df_history["גיל"], y=df_history["שווי ירושה 190"],
        mode='lines', name='שווי ירושה — מסלול 1 (190)',
        line=dict(color='#2ca02c', width=3),
        fill='tozeroy', fillcolor='rgba(44, 160, 44, 0.08)'
    ))
    fig5.add_trace(go.Scatter(
        x=df_history["גיל"], y=df_history["שווי ירושה היברידי"],
        mode='lines', name='שווי ירושה — מסלול 3 (היברידי)',
        line=dict(color='#ff7f0e', width=3, dash='dash'),
        fill='tozeroy', fillcolor='rgba(255, 127, 14, 0.08)'
    ))
    fig5.add_trace(go.Scatter(
        x=df_history["גיל"], y=df_history["צבירה מסלול ריאלי"],
        mode='lines', name='הון נזיל — מסלול 2 (25% ריאלי)',
        line=dict(color='#1f77b4', width=2, dash='dot')
    ))
    fig5.add_trace(go.Scatter(
        x=df_history["גיל"], y=df_history["ערך קצבה נותר"],
        mode='lines', name='ערך הבטחת קצבה בלבד',
        line=dict(color='#d62728', width=1, dash='dash')
    ))

    fig5.update_layout(
        xaxis_title="גיל", yaxis_title="שווי ירושה (₪)",
        hovermode="x unified", template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig5.update_traces(hovertemplate="%{y:,.0f} ₪")
    st.plotly_chart(fig5, use_container_width=True)
