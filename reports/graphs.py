import streamlit as st
import plotly.graph_objects as go

def render_charts(df_history):
    st.subheader("📊 סימולציית הון לאורך השנים")
    st.markdown("הגרף מציג את התפתחות ההון (ברוטו) בכל אחד מהמסלולים מחודש לחודש:")
    
    # יצירת גרף אינטראקטיבי מקצועי ב-Plotly
    fig = go.Figure()
    
    # קו מסלול 190
    fig.add_trace(go.Scatter(
        x=df_history["גיל"],
        y=df_history["צבירה תיקון 190"],
        mode='lines',
        name='תיקון 190',
        line=dict(color='#2ca02c', width=3)
    ))
    
    # קו מסלול 25% ריאלי
    fig.add_trace(go.Scatter(
        x=df_history["גיל"],
        y=df_history["צבירה מסלול ריאלי"],
        mode='lines',
        name='מסלול 25% ריאלי',
        line=dict(color='#1f77b4', width=3)
    ))
    
    fig.update_layout(
        title="השוואת קצב דעיכת/צמיחת ההון בפועל",
        xaxis_title="גיל",
        yaxis_title="סך הון בקופה (₪)",
        legend_title="מסלולים",
        template="plotly_white",
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, use_container_width=True)
