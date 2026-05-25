import streamlit as st

def render_wealth_inputs():
    st.subheader("💰 נתוני הון ונדל\"ן")
    
    wealth_data = {
        "net_sale": st.slider("נטו ממכירת נכס מוערך (₪)", min_value=0, max_value=20_000_000, value=10_000_000, step=100_000),
        "existing_savings": st.slider("חסכונות קיימים (₪)", min_value=0, max_value=5_000_000, value=440_000, step=10_000),
        "new_apartment_cost": st.slider("עלות דירה חדשה - כולל הכל (₪)", min_value=0, max_value=15_000_000, value=5_800_000, step=100_000),
        "kids_help": st.slider("עזרה לילדים (₪)", min_value=0, max_value=5_000_000, value=1_000_000, step=50_000),
        "emergency_fund": st.slider("קרן חירום / מזומן בקרן כספית (₪)", min_value=0, max_value=2_000_000, value=300_000, step=50_000)
    }
    
    wealth_data["remaining_for_gimel"] = (
        wealth_data["net_sale"] + 
        wealth_data["existing_savings"] - 
        wealth_data["new_apartment_cost"] - 
        wealth_data["kids_help"] - 
        wealth_data["emergency_fund"]
    )
    
    st.info(f"הון נותר לטובת קופת גמל לקצבה (למסלול 190): ₪{wealth_data['remaining_for_gimel']:,}")
    
    return wealth_data
