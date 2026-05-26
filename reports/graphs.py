import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def render_charts(df_history):
    st.markdown("### 📈 ניתוח אקטוארי ויזואלי")
    st.markdown("כאן ניתן לראות את התנהגות התיק מכמה זוויות שונות: התפתחות ההון, פערי תזרים, מיסוי ושווי כולל.")
    
    # יצירת טאבים לסידור נקי של הגרפים במסך
    tab1, tab2, tab3, tab4 = st.tabs([
        "💰 הון נזיל (קופות)", 
        "⚖️ תזרים מזומנים", 
        "🛡️ נטל מס מצטבר", 
        "🏢 שווי נקי כולל (Net Worth)"
    ])
    
    # ---------------------------------------------------------
    # גרף 1: התפתחות ההון הנזיל (הגרף המקורי המשופר)
    # ---------------------------------------------------------
    with tab1:
        st.subheader("השוואת התפתחות ההון הנזיל בפועל")
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
        
        fig1.update_layout(
            xaxis_title="גיל", yaxis_title="סך הון בקופה (₪)",
            hovermode="x unified", template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig1.update_traces(hovertemplate="%{y:,.0f} ₪")
        st.plotly_chart(fig1, use_container_width=True)

    # ---------------------------------------------------------
    # גרף 2: תזרים מזומנים (הוצאות מול הכנסות)
    # ---------------------------------------------------------
    with tab2:
        st.subheader("ניתוח פער תזרימי (Cash Flow Gap)")
        st.markdown("הגרף מציג את סך ההוצאות הצמודות מול מקורות ההכנסה הקבועים. הפער (השטח הלבן) הוא הסכום שמושכים מהתיק.")
        fig2 = go.Figure()
        
        # קו הוצאות כולל
        fig2.add_trace(go.Scatter(
            x=df_history["גיל"], y=df_history["הוצאה נומינלית"],
            mode='lines', name='סך הוצאות מחיה',
            line=dict(color='#d62728', width=2, dash='dash')
        ))
        
        # הכנסה בסיסית (עבודה + ב"ל)
        fig2.add_trace(go.Scatter(
            x=df_history["גיל"], y=df_history["הכנסה נומינלית"],
            mode='lines', name='הכנסה קבועה (ב"ל/עבודה)',
            line=dict(color='#ff7f0e', width=2),
            stackgroup='one'
        ))
        
        # תוספת קצבת 190
        fig2.add_trace(go.Scatter(
            x=df_history["גיל"], y=df_history["הכנסה מקצבה מזערית"],
            mode='lines', name='קצבת תיקון 190',
            line=dict(color='#2ca02c', width=2),
            stackgroup='one'
        ))

        fig2.update_layout(
            xaxis_title="גיל", yaxis_title="סכום חודשי (₪)",
            hovermode="x unified", template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig2.update_traces(hovertemplate="%{y:,.0f} ₪")
        st.plotly_chart(fig2, use_container_width=True)

    # ---------------------------------------------------------
    # גרף 3: נטל מס מצטבר במשיכות
    # ---------------------------------------------------------
    with tab3:
        st.subheader("סך מס רווחי הון ששולם בפועל לאורך השנים")
        st.markdown("ממחיש את אפקט 'המגן ממס' של תיקון 190 אל מול שחיקת מס רווחי הון ריאלי במשיכות שוטפות.")
        
        # חישוב מס מצטבר
        df_history = df_history.copy()
        df_history['cum_tax_190'] = df_history['מס ששולם 190'].cumsum()
        df_history['cum_tax_25'] = df_history['מס ששולם 25'].cumsum()
        
        fig3 = go.Figure()
        
        fig3.add_trace(go.Scatter(
            x=df_history["גיל"], y=df_history["cum_tax_190"],
            mode='lines', name='מס מצטבר - תיקון 190',
            line=dict(color='#2ca02c', width=3)
        ))
        
        fig3.add_trace(go.Scatter(
            x=df_history["גיל"], y=df_history["cum_tax_25"],
            mode='lines', name='מס מצטבר - 25% ריאלי',
            line=dict(color='#1f77b4', width=3)
        ))
        
        fig3.update_layout(
            xaxis_title="גיל", yaxis_title="סך מס ששולם (₪)",
            hovermode="x unified", template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig3.update_traces(hovertemplate="%{y:,.0f} ₪")
        st.plotly_chart(fig3, use_container_width=True)

    # ---------------------------------------------------------
    # גרף 4: שווי נקי כולל (Net Worth)
    # ---------------------------------------------------------
    with tab4:
        st.subheader("שווי נקי כולל (הון נזיל + נדל\"ן)")
        st.markdown("מבט הוליסטי על סך הנכסים של התא המשפחתי, המציג את תמונת הירושה הכוללת בכל נקודת זמן.")
        
        df_history['total_nw_190'] = df_history['צבירה תיקון 190'] + df_history['שווי נדלן']
        df_history['total_nw_25'] = df_history['צבירה מסלול ריאלי'] + df_history['שווי נדלן']
        
        fig4 = go.Figure()
        
        fig4.add_trace(go.Scatter(
            x=df_history["גיל"], y=df_history["total_nw_190"],
            mode='lines', name='שווי כולל - תיקון 190',
            line=dict(color='#2ca02c', width=3, dash='dot')
        ))
        
        fig4.add_trace(go.Scatter(
            x=df_history["גיל"], y=df_history["total_nw_25"],
            mode='lines', name='שווי כולל - 25% ריאלי',
            line=dict(color='#1f77b4', width=3, dash='dot')
        ))
        
        fig4.update_layout(
            xaxis_title="גיל", yaxis_title="שווי נכסים כולל (₪)",
            hovermode="x unified", template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig4.update_traces(hovertemplate="%{y:,.0f} ₪")
        st.plotly_chart(fig4, use_container_width=True)
