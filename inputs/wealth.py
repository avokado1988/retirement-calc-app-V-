import streamlit as st

def render_wealth_inputs():
    st.subheader("💰 נתוני הון, נדל\"ן והכנסות יסוד")
    
    # 1. נדל"ן והון נזיל
    st.markdown("##### 🏠 נכסים ונדל\"ן")
    net_sale = st.slider("נטו ממכירת נכס מוערך (₪)", min_value=0, max_value=20_000_000, value=10_000_000, step=100_000)
    new_apartment_cost = st.slider("עלות דירה חדשה - כולל הכל (₪)", min_value=0, max_value=15_000_000, value=5_800_000, step=100_000)
    
    # האינפוט החדש שביקשת - עליית ערך הדירה החדשה
    property_appreciation = st.slider("עליית ערך שנתית צפויה של הדירה החדשה (%)", min_value=0.0, max_value=10.0, value=2.3, step=0.1) / 100
    
    st.divider()
    
    st.markdown("##### 💸 חסכונות והתחייבויות ראשוניות")
    existing_savings = st.slider("חסכונות קיימים נזילים (₪)", min_value=0, max_value=5_000_000, value=440_000, step=10_000)
    kids_help = st.slider("עזרה לילדים (₪)", min_value=0, max_value=5_000_000, value=1_000_000, step=50_000)
    emergency_fund = st.slider("קרן חירום / מזומן בקרן כספית (₪)", min_value=0, max_value=2_000_000, value=300_000, step=50_000)
    
    st.divider()
    
    # האינפוט השני שביקשת - ביטוח לאומי
    st.markdown("##### 🏛️ קצבאות ממשלתיות קבועות")
    national_insurance = st.number_input("קצבת אזרח ותיק חודשית צפויה - ביטוח לאומי (₪)", min_value=0, value=2591, step=50)
    
    # אריזת כל הנתונים למילון
    wealth_data = {
        "net_sale": net_sale,
        "new_apartment_cost": new_apartment_cost,
        "property_appreciation": property_appreciation,
        "existing_savings": existing_savings,
        "kids_help": kids_help,
        "emergency_fund": emergency_fund,
        "national_insurance": national_insurance
    }
    
    # חישוב אוטומטי של ההון שנותר לגמל/פוליסה
    wealth_data["remaining_for_gimel"] = (
        wealth_data["net_sale"] + 
        wealth_data["existing_savings"] - 
        wealth_data["new_apartment_cost"] - 
        wealth_data["kids_help"] - 
        wealth_data["emergency_fund"]
    )
    
    st.info(f"הון נותר לטובת קופת גמל לקצבה (למסלול 190): ₪{wealth_data['remaining_for_gimel']:,}")
    
    return wealth_data
