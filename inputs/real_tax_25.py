import streamlit as st

def render_25_inputs():
    st.subheader("📊 מסלול 25% מס ריאלי (פוליסת חיסכון / תיק מנוהל)")
    
    st.markdown("##### ⚙️ פרמטרים כלכליים למסלול")
    
    annual_return_25 = st.slider("תשואה שנתית צפויה במסלול 25% (%)", min_value=0.0, max_value=15.0, value=5.0, step=0.1) / 100
    management_fee_25 = st.slider("דמי ניהול שנתיים מהצבירה (%)", min_value=0.0, max_value=2.0, value=0.6, step=0.05) / 100
    
    st.divider()
    st.markdown("##### 📊 סיכום הון במסלול:")
    
    # הצגת הודעה ירוקה בדיוק כמו בתיקון 190, שמראה שכל ההון נשאר נזיל
    st.success("💰 **יתרת הון נטו פנויה למשיכה למסלול הריאלי:** (מלוא ההון ההתחלתי הפנוי נשאר נזיל)")
    
    # אריזת הנתונים למילון
    strategy_data = {
        "annual_return_25": annual_return_25,
        "management_fee_25": management_fee_25
    }
    
    return strategy_data
