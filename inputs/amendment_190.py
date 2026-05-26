import streamlit as st
from inputs.ui_components import compact_number_input, labeled_slider_with_value, show_net_summary, format_shekel, DEFAULTS

def render_190_inputs(remaining_for_gimel):
    st.subheader("📑 מסלול תיקון 190 וחישוב קצבה")
    st.caption(f"הון התחלתי זמין לקופת גמל: {format_shekel(remaining_for_gimel)}")
    
    st.markdown("##### 🎯 הגדרת קצבה רצויה לרכישה")
    desired_pension = compact_number_input(
        "קצבה רצויה לרכישה (₪ חודשי)", 
        value=DEFAULTS["desired_pension"], min_value=0, step=50, unit="₪"
    )
    
    st.divider()
    st.markdown("##### 🎲 תנאים אקטואריים (מודל שוק ריאלי)")
    securing_years = labeled_slider_with_value(
        "תקופת אבטחה בשנים (חודשי הבטחה ליורשים)", 
        min_value=0, max_value=35, value=20, step=1, unit="שנים"
    )
    base_coefficient = labeled_slider_with_value(
        "מקדם המרה בסיסי לקצבה (ללא אבטחה)", 
        min_value=150.0, max_value=300.0, value=200.0, step=1.0, format="%.1f", unit=None
    )
    
    adjusted_coefficient = base_coefficient + (securing_years * 1.0)
    capital_for_pension = int(desired_pension * adjusted_coefficient)
    
    st.divider()
    st.markdown("##### 📊 חישובים אקטואריים אוטומטיים:")
    col1, col2 = st.columns(2)
    with col1: st.metric(label="מקדם המרה משוקלל", value=f"{adjusted_coefficient:.1f}")
    with col2: st.metric(label="הון נדרש שינוכה", value=format_shekel(capital_for_pension))
    
    net_for_190 = max(0, remaining_for_gimel - capital_for_pension)
    if remaining_for_gimel < capital_for_pension:
        st.error(f"⚠️ אזהרה: ההון הנדרש לקצבה גבוה מסך ההון הזמין!")
    else:
        show_net_summary(title="יתרת הון נטו פנויה בתיקון 190", amount=net_for_190)
    
    st.divider()
    st.markdown("##### 📈 תשואה ודמי ניהול ליתרת ההון")
    annual_return_190 = labeled_slider_with_value(
        "תשואה שנתית צפויה במסלול 190 (%)", 
        min_value=0.0, max_value=15.0, value=DEFAULTS["annual_return"] * 100, step=0.1, 
        format="%.1f%%", unit="%"
    ) / 100
    management_fee_190 = labeled_slider_with_value(
        "דמי ניהול שנתיים מהצבירה במסלול 190 (%)", 
        min_value=0.0, max_value=2.0, value=DEFAULTS["management_fee"] * 100, step=0.05, 
        format="%.2f%%", unit="%"
    ) / 100
    
    return {
        "desired_pension": desired_pension, "securing_years": securing_years,
        "base_coefficient": base_coefficient, "adjusted_coefficient": adjusted_coefficient,
        "capital_for_pension": capital_for_pension, "net_for_190": net_for_190,
        "annual_return_190": annual_return_190, "management_fee_190": management_fee_190
    }
