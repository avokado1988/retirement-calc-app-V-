import streamlit as st
from inputs.ui_components import show_net_summary, format_shekel

def render_wealth_inputs():
    st.subheader("💰 נתוני הון")
    
    st.markdown("#### 📈 חישוב הון לטובת מסלולים")
    net_sale = st.slider("נטו ממכירה מוערך", min_value=0, max_value=20_000_000, value=10_000_000, step=100_000, format="%d")
    st.caption(f"בחרת: **{net_sale/1_000_000:.1f} מיליון ₪** ({format_shekel(net_sale)})")
    
    existing_savings = st.slider("חסכונות קיימים", min_value=0, max_value=5_000_000, value=440_000, step=10_000, format="%d")
    st.caption(f"בחרת: **{format_shekel(existing_savings)}**")
    
    new_apartment_cost = st.slider("עלות דירה חדשה (כולל הכל)", min_value=0, max_value=15_000_000, value=5_800_000, step=100_000, format="%d")
    st.caption(f"בחרת: **{new_apartment_cost/1_000_000:.1f} מיליון ₪** ({format_shekel(new_apartment_cost)})")
    
    kids_help = st.slider("עזרה לילדים", min_value=0, max_value=5_000_000, value=1_000_000, step=50_000, format="%d")
    st.caption(f"בחרת: **{kids_help/1_000_000:.1f} מיליון ₪** ({format_shekel(kids_help)})")
    
    emergency_fund = st.slider("קרן חירום / מזומן", min_value=0, max_value=2_000_000, value=300_000, step=50_000, format="%d")
    st.caption(f"בחרת: **{format_shekel(emergency_fund)}**")
    
    remaining_for_gimel = net_sale + existing_savings - new_apartment_cost - kids_help - emergency_fund
    
    show_net_summary(title="סך הון פנוי לטובת מסלולים", amount=remaining_for_gimel)
    
    st.divider()
    st.markdown("#### ➕ נכסים נוספים")
    national_insurance = st.number_input("קצבת ביטוח לאומי (₪ חודשי)", min_value=0, value=2591, step=50)
    property_appreciation_pct = st.slider("עליה ערך נדלן שנתית (%)", min_value=0.0, max_value=10.0, value=2.3, step=0.1)
    
    wealth_data = {
        "net_sale": net_sale,
        "existing_savings": existing_savings,
        "new_apartment_cost": new_apartment_cost,
        "kids_help": kids_help,
        "emergency_fund": emergency_fund,
        "remaining_for_gimel": remaining_for_gimel,
        "national_insurance": national_insurance,
        "property_appreciation": property_appreciation_pct / 100
    }
    return wealth_data
