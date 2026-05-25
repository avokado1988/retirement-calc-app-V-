import streamlit as st

def format_with_commas(val):
    """פונקציית עזר להצגת מספר עם פסיקים וסימן שח"""
    return f"₪{val:,}"

def render_wealth_inputs():
    st.subheader("💰 נתוני הון")
    
    # חלק 1: חישוב הון לטובת מסלולים
    st.markdown("#### 📈 חישוב הון לטובת מסלולים")
    
    # הוספנו את הפרמטר format="%,d" שיוצר פסיקים אוטומטיים בתוך הסליידר עצמו!
    net_sale = st.slider("נטו ממכירה מוערך", min_value=0, max_value=20_000_000, value=10_000_000, step=100_000, format="%d")
    st.caption(f"בחרת: **{net_sale/1_000_000:.1f} מיליון ₪** ({format_with_commas(net_sale)})")
    
    existing_savings = st.slider("חסכונות קיימים", min_value=0, max_value=5_000_000, value=440_000, step=10_000, format="%d")
    st.caption(f"בחרת: **{existing_savings:,} ₪**")
    
    new_apartment_cost = st.slider("עלות דירה חדשה (כולל הכל)", min_value=0, max_value=15_000_000, value=5_800_000, step=100_000, format="%d")
    st.caption(f"בחרת: **{new_apartment_cost/1_000_000:.1f} מיליון ₪** ({format_with_commas(new_apartment_cost)})")
    
    kids_help = st.slider("עזרה לילדים", min_value=0, max_value=5_000_000, value=1_000_000, step=50_000, format="%d")
    st.caption(f"בחרת: **{kids_help/1_000_000:.1f} מיליון ₪** ({format_with_commas(kids_help)})")
    
    emergency_fund = st.slider("קרן חירום / מזומן", min_value=0, max_value=2_000_000, value=300_000, step=50_000, format="%d")
    st.caption(f"בחרת: **{emergency_fund:,} ₪**")
    
    # חישוב אוטומטי של סך ההון הפנוי לטובת מסלולי ההשקעה
    remaining_for_gimel = net_sale + existing_savings - new_apartment_cost - kids_help - emergency_fund
    
    # הצגת תוצאת החישוב בצורה הכי ברורה ומודגשת
    if remaining_for_gimel >= 1_000_000:
        text_summary = f"{remaining_for_gimel/1_000_000:.3f} מיליון ₪"
    else:
        text_summary = f"{remaining_for_gimel:,} ₪"
        
    st.info(f"📊 **סך הון פנוי לטובת מסלולים:** {text_summary} *(מדויק: {format_with_commas(remaining_for_gimel)})*")
    
    st.divider()
    
    # חלק 2: נכסים נוספים
    st.markdown("#### ➕ נכסים נוספים")
    
    national_insurance = st.number_input("קצבת ביטוח לאומי (₪ חודשי)", min_value=0, value=2591, step=50)
    property_appreciation_pct = st.slider("עליה ערך נדלן שנתית (%)", min_value=0.0, max_value=10.0, value=2.3, step=0.1)
    
    # שמירה במילון הנתונים
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
