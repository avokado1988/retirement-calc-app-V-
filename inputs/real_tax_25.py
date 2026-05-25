import streamlit as st

def render_25_inputs(remaining_for_real):
    st.subheader("📊 מסלול 25% מס ריאלי (פוליסת חיסכון / תיק מנוהל)")
    
    # הצגת ההון ההתחלתי שהגיע למסלול זה כקפשן עליון (אופציונלי, לאחידות עם 190)
    st.caption(f"הון התחלתי זמין למסלול ריאלי: ₪{remaining_for_real:,}")
    
    st.markdown("##### ⚙️ פרמטרים כלכליים למסלול")
    
    annual_return_25 = st.slider("תשואה שנתית צפויה במסלול 25% (%)", min_value=0.0, max_value=15.0, value=5.0, step=0.1) / 100
    management_fee_25 = st.slider("דמי ניהול שנתיים מהצבירה (%)", min_value=0.0, max_value=2.0, value=0.6, step=0.05) / 100
    
    st.divider()
    st.markdown("##### 📊 סיכום הון במסלול:")
    
    # חישוב היתרה - במסלול זה אין ניכויים לקצבה, ולכן היתרה שווה למלוא ההון
    net_for_real_pathway = remaining_for_real
    
    # הצגת הודעה ירוקה עם המספר המדויק והדינמי של היתרה!
    st.success(f"💰 **יתרת הון נטו פנויה למשיכה למסלול הריאלי:** ₪{net_for_real_pathway:,}")
    
    # אריזת הנתונים למילון
    strategy_data = {
        "net_for_real_pathway": net_for_real_pathway,
        "annual_return_25": annual_return_25,
        "management_fee_25": management_fee_25
    }
    
    return strategy_data
