import streamlit as st
from inputs.ui_components import compact_number_input, labeled_slider_with_value, show_net_summary, DEFAULTS

def render_wealth_inputs():
    st.subheader("💰 נתוני הון")
    st.markdown("#### 📈 חישוב הון לטובת מסלולים")
    
    net_sale = compact_number_input(
        "נטו ממכירה מוערך (₪)", 
        value=DEFAULTS["net_sale"], min_value=0, step=100000,
        help_text="סך התמורה נטו ממכירת הנכס/חברה"
    )
    
    existing_savings = compact_number_input(
        "חסכונות קיימים (₪)", 
        value=DEFAULTS["existing_savings"], min_value=0, step=10000
    )
    
    new_apartment_cost = compact_number_input(
        "עלות דירה חדשה (כולל הכל) (₪)", 
        value=DEFAULTS["new_apartment_cost"], min_value=0, step=100000
    )
    
    kids_help = compact_number_input(
        "עזרה לילדים (₪)", 
        value=DEFAULTS["kids_help"], min_value=0, step=50000
    )
    
    emergency_fund = compact_number_input(
        "קרן חירום / מזומן (₪)", 
        value=DEFAULTS["emergency_fund"], min_value=0, step=10000
    )
    
    remaining_for_gimel = net_sale + existing_savings - new_apartment_cost - kids_help - emergency_fund
    show_net_summary(title="סך הון פנוי לטובת מסלולים", amount=remaining_for_gimel)
    
    st.divider()
    st.markdown("#### ➕ נכסים נוספים")
    
    # שימוש בתיבה קומפקטית לביטוח לאומי
    national_insurance = st.number_input("קצבת ביטוח לאומי (₪ חודשי)", min_value=0, value=DEFAULTS["national_insurance"], step=50)
    
    property_appreciation_pct = labeled_slider_with_value(
        "עליה ערך נדלן שנתית (%)", 
        min_value=0.0, max_value=10.0, 
        value=DEFAULTS["property_appreciation"] * 100, step=0.1, 
        format="%.1f%%", is_percent=True
    )
    
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
