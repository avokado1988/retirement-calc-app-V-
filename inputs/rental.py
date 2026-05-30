import streamlit as st
from inputs.ui_components import compact_number_input, show_net_summary, format_shekel

def render_rental_inputs(wealth_data):
    existing_savings = float(wealth_data.get("existing_savings", 440000))
    kids_help = float(wealth_data.get("kids_help", 1000000))
    emergency_fund = float(wealth_data.get("emergency_fund", 300000))
    property_value = float(wealth_data.get("new_apartment_cost", 5800000))

    net_for_rental = existing_savings - kids_help - emergency_fund

    st.subheader("🏠 מסלול 4 — אסטרטגיית שכירות")
    st.caption("במסלול זה הדירה לא נמכרת. ההון הנזיל מגיע מחסכונות קיימים בלבד.")
    st.caption(f"שווי הדירה הנשמרת כנכס מניב: {format_shekel(property_value)}")
    st.caption("תשואה ודמי ניהול על החסכונות — נלקחים ממסלול 25% ריאלי.")
    show_net_summary("הון נזיל פנוי (חסכונות בלבד)", net_for_rental)

    st.divider()
    st.markdown("##### 📥 הכנסה מהשכרת הנכס")
    rental_income_monthly = compact_number_input(
        "שכר דירה חודשי — גביה (₪)",
        value=8000, min_value=0, step=500, unit="₪"
    )
    rental_income_growth_pct = compact_number_input(
        "עלייה שנתית בדמי שכירות גביה (%)",
        value=3.0, min_value=0.0, max_value=10.0, step=0.1, unit="%"
    )

    st.divider()
    st.markdown("##### 📤 הוצאה על שכירות למגורים")
    rent_paid_monthly = compact_number_input(
        "שכר דירה חודשי — תשלום (₪)",
        value=6000, min_value=0, step=500, unit="₪"
    )
    rent_paid_growth_pct = compact_number_input(
        "עלייה שנתית בדמי שכירות תשלום (%)",
        value=3.0, min_value=0.0, max_value=10.0, step=0.1, unit="%"
    )

    st.divider()
    st.markdown("##### 🧾 מיסוי על הכנסת שכירות")
    rental_tax_pct = compact_number_input(
        "שיעור מס אפקטיבי על שכירות (%)",
        value=10.0, min_value=0.0, max_value=50.0, step=0.5, unit="%"
    )
    st.caption("ברירת מחדל 10% — מסלול סעיף 122 (ללא ניכוי הוצאות). ניתן להתאים.")

    return {
        "net_for_rental": net_for_rental,
        "rental_income_monthly": rental_income_monthly,
        "rental_income_growth_rate": rental_income_growth_pct / 100,
        "rent_paid_monthly": rent_paid_monthly,
        "rent_paid_growth_rate": rent_paid_growth_pct / 100,
        "rental_tax_rate": rental_tax_pct / 100,
        "property_value_retained": property_value
    }
