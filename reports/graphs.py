import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def render_charts(df_history):
    st.markdown("### 📈 ניתוח אקטוארי ויזואלי")
    st.markdown("גלול מטה כדי לראות את התנהגות התיק מכמה זוויות שונות: התפתחות ההון, פערי תזרים, מיסוי ושווי נקי.")
    st.divider()
    
    # === גרף 1 ===
    st.subheader("💰 1. התפתחות ההון הנזיל (קופות ופוליסות)")
    st.markdown("הגרף מציג את התפתחות ההון הנזיל נטו בכל אחד מהמסלולים לאורך שנות הפרישה.")
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=df_history["גיל"], y=df_history["צבירה תיקון 190"],
        mode='lines', name='תיקון 190',
        line=dict(color='#2ca02c', width=3),
        fill='tozeroy', fillcolor='rgba(44, 160, 44, 0.1)'
    ))
    fig1.add_trace(go.Scatter(
        x=df_history["גיל"], y=df_history["צבירה מסלול ריאלי"],
        mode='lines', name='מסלול 25% ריאלי',
        line=dict(color='#1f77b4', width=3),
        fill='tozeroy', fillcolor='rgba(31, 119, 180, 0.1)'
    ))
    fig1.update_layout(xaxis_title="גיל", yaxis_title="סך הון בקופה (₪)", hovermode="x unified", template="plotly_white", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig1.update_traces(hovertemplate="%{y:,.0f} ₪")
    st.plotly_chart(fig1, use_container_width=True)

    st.divider()

    # === גרף 2 ===
    st.subheader("⚖️ 2. פאזל מימון המחיה (מאיפה מגיע הכסף?)")
    st.markdown("הגרף מראה כיצד ממומנות ההוצאות השוטפות שלך: ההכנסות הקבועות (ירוק/כחול), ו**הגירעון (באדום) אותו אתה נאלץ למשוך מהחסכונות**.")
    fig2 = go.Figure()
    
    base_income_series = df_history["הכנסה מעבודה"] + df_history["קצבת ביטוח לאומי"]
    
    fig2.add_trace(go.Scatter(
        x=df_history["גיל"], y=base_income_series,
        mode='none', name='הכנסה קבועה (ב"ל/עבודה)',
        fill='tozeroy', stackgroup='one', fillcolor='rgba(44, 160, 44, 0.6)'
    ))
    fig2.add_trace(go.Scatter(
        x=df_history["גיל"], y=df_history["קצבה מזערית 190"], # 🟢 מותאם למפתח החדש
        mode='none', name='קצבת תיקון 190',
        fill='tonexty', stackgroup='one', fillcolor='rgba(31, 119, 180, 0.6)'
    ))
    
    gap = df_history["הוצאה נומינלית"] - (base_income_series + df_history["קצבה מזערית 190"])
    gap = gap.clip(lower=0) 
    
    fig2.add_trace(go.Scatter(
        x=df_history["גיל"], y=gap,
        mode='none', name='משיכה מהחסכונות (גירעון)',
        fill='tonexty', stackgroup='one', fillcolor='rgba(214, 39, 40, 0.5)'
    ))
    fig2.add_trace(go.Scatter(
        x=df_history["גיל"], y=df_history["הוצאה נומינלית"],
        mode='lines', name='סך ההוצאות בפועל',
        line=dict(color='black', width=2, dash='dot')
    ))

    max_y_view = df_history["הוצאה נומינלית"].quantile(0.95) * 1.3
    fig2.update_layout(xaxis_title="גיל", yaxis_title="סכום חודשי (₪)", yaxis=dict(range=[0, max_y_view]), hovermode="x unified", template="plotly_white", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig2.update_traces(hovertemplate="%{y:,.0f} ₪")
    st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # === גרף 3 ===
    st.subheader("🛡️ 3. סך מס רווחי הון ששולם בפועל (מצטבר)")
    df_history_tax = df_history.copy()
    df_history_tax['cum_tax_190'] = df_history_tax['מס ששולם 190'].cumsum()
    df_history_tax['cum_tax_25'] = df_history_tax['מס ששולם 25'].cumsum()
    
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=df_history_tax["גיל"], y=df_history_tax["cum_tax_190"], mode='lines', name='מס מצטבר - תיקון 190', line=dict(color='#2ca02c', width=3)))
    fig3.add_trace(go.Scatter(x=df_history_tax["גיל"], y=df_history_tax["cum_tax_25"], mode='lines', name='מס מצטבר - 25% ריאלי', line=dict(color='#1f77b4', width=3)))
    fig3.update_layout(xaxis_title="גיל", yaxis_title="סך מס ששולם (₪)", hovermode="x unified", template="plotly_white", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig3.update_traces(hovertemplate="%{y:,.0f} ₪")
    st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    # === גרף 4 ===
    st.subheader("🏢 4. שווי נקי כולל (הון נזיל + נדל\"ן)")
    df_history_nw = df_history.copy()
    df_history_nw['total_nw_190'] = df_history_nw['צבירה תיקון 190'] + df_history_nw['שווי נדלן']
    df_history_nw['total_nw_25'] = df_history_nw['צבירה מסלול ריאלי'] + df_history_nw['שווי נדלן']
    
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=df_history_nw["גיל"], y=df_history_nw["total_nw_190"], mode='lines', name='שווי כולל - תיקון 190', line=dict(color='#2ca02c', width=3, dash='dot')))
    fig4.add_trace(go.Scatter(x=df_history_nw["גיל"], y=df_history_nw["total_nw_25"], mode='lines', name='שווי כולל - 25% ריאלי', line=dict(color='#1f77b4', width=3, dash='dot')))
    fig4.update_layout(xaxis_title="גיל", yaxis_title="שווי נכסים כולל (₪)", hovermode="x unified", template="plotly_white", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig4.update_traces(hovertemplate="%{y:,.0f} ₪")
    st.plotly_chart(fig4, use_container_width=True)
