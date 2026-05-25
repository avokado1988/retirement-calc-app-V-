import streamlit as st
# ייבוא רכיבי העיצוב המרכזיים מקובץ העיצוב החדש
from inputs.ui_components import show_net_summary, format_shekel

def render_25_inputs(remaining_for_real):
    st.subheader("📊 מסלול 25% מס ריאלי (פוליסת חיסכון / תיק מנוהל)")
    st.caption(f"הון התחלתי זמין למסלול ריאלי: {format_shekel(remaining_for_real)}")
    
    st.markdown("##### ⚙️ :פרמטרים כלכליים למסלול")
    annual_return_25 = st.slider("תשואה שנתית צפויה במסלול 25% (%)", min_value=0.0, max_value=15.0, value=5.0, step=0.1) / 100
    management_fee_25 = st.slider("דמי ניהול שנתיים מהצבירה (%)", min_value=0.0, max_value=2.0, value=0.6, step=0.05) / 100
    
    st.divider()
    st.markdown("##### 📊 סיכום הון במסלול:")
    
    # שימוש ברכיב המרכזי - ידפיס אוטומטית מספר מדויק עם פסיקים וצבע ירוק!
    show_net_summary(title="יתרת הון נטו פנויה למשיכה למסלול הריאלי", amount=remaining_for_real)
    
    strategy_data = {
        "annual_return_25": annual_return_25,
        "management_fee_25": management_fee_25
    }
    
    return strategy_data
