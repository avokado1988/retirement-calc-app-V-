import streamlit as st
from inputs.ui_components import compact_number_input, show_net_summary, DEFAULTS

def render_wealth_inputs():
    st.subheader("💰 נתוני הון ונדל\"ן")
    
    st.markdown("#### 📈 נכסים ומשיכות")
    net_sale = compact_number_input(
        "נטו ממכירה מוערך (₪)", 
        value=DEFAULTS["net_sale"], min_value=0, step=100000, unit="₪"
    )
    
    existing_savings = compact_number_input(
        "חסכונות קיימים (₪)", 
        value=DEFAULTS["existing_savings"], min_value=0, step=10000, unit="₪"
    )
    
    st.divider()
    st.markdown("#### 🏠 נדל\"ן ורכישות")
    new_apartment_cost = compact_number_input(
        "עלות דירה חדשה (כולל הכל) (₪)", 
        value=DEFAULTS["new_apartment_cost"], min_value=0, step=100000, unit="₪"
    )
    
    property_appreciation_pct = compact_number_input(
        "עליה ערך נדלן שנתית (%)",
        value=DEFAULTS["property_appreciation"] * 100, min_value=0.0, max_value=10.0, step=0.1, unit="%"
    )
    
    st.divider()
    st.markdown("#### 🎁 התחייבויות וחירום")
    kids_help = compact_number_input(
        "עזרה לילדים (₪)", 
        value=DEFAULTS["kids_help"], min_value=0, step=50000, unit="₪"
    )
    
    emergency_fund = compact_number_input(
        "קרן חירום / מזומן (₪)", 
        value=DEFAULTS["emergency_fund"], min_value=0, step=10000, unit="₪"
    )
    
    st.divider()
    remaining_for_gimel = net_sale + existing_savings - new_apartment_cost - kids_help - emergency_fund
    show_net_summary(title="סך הון פנוי לטובת מסלולים", amount=remaining_for_gimel)
    
    return {
        "net_sale": net_sale,
        "existing_savings": existing_savings,
        "new_apartment_cost": new_apartment_cost,
        "property_appreciation": property_appreciation_pct / 100,
        "kids_help": kids_help,
        "emergency_fund": emergency_fund,
        "remaining_for_gimel": remaining_for_gimel
    }
