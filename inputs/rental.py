import streamlit as st
from inputs.ui_components import compact_number_input, show_net_summary, format_shekel, COLOR_GREEN, COLOR_RED, COLOR_BLUE

def render_rental_inputs(wealth_data):
    existing_savings = float(wealth_data.get("existing_savings", 440000))
    kids_help = float(wealth_data.get("kids_help", 1000000))
    emergency_fund = float(wealth_data.get("emergency_fund", 300000))
    net_sale = float(wealth_data.get("net_sale", 10000000))

    net_for_rental = existing_savings

    st.subheader("🏠 מסלול 4 — אסטרטגיית שכירות")
    st.caption("במסלול זה הדירה לא נמכרת. ההון הנזיל מגיע מחסכונות קיימים בלבד.")
    st.caption("עזרה לילדים וקרן חירום — לא מנוכות במסלול זה. הדירה היא הירושה, והחסכונות הם כרית הביטחון.")
    st.caption("תשואה ודמי ניהול על החסכונות — נלקחים ממסלול 25% ריאלי.")
    show_net_summary("הון נזיל פנוי (חסכונות בלבד)", net_for_rental)

    st.divider()
    st.markdown("##### 🏡 שווי הנכס המושכר")
    current_property_value = compact_number_input(
        "שווי הדירה הנוכחית (₪)",
        value=int(net_sale), min_value=0, step=100000, unit="₪", color=COLOR_GREEN
    )
    rental_appreciation_pct = compact_number_input(
        "עליית ערך שנתית — דירה מושכרת (%)",
        value=1.5, min_value=0.0, max_value=10.0, step=0.1, unit="%", color=COLOR_BLUE
    )
    st.caption("דירות יקרות מתייקרות לאט יותר באחוזים — מומלץ 1–2% לדירה מעל ₪5M.")

    st.divider()
    st.markdown("##### 📥 הכנסה מהשכרת הנכס")
    rental_income_monthly = compact_number_input(
        "שכר דירה חודשי — גביה (₪)",
        value=8000, min_value=0, step=500, unit="₪", color=COLOR_GREEN
    )
    rental_income_growth_pct = compact_number_input(
        "עלייה שנתית בדמי שכירות גביה (%)",
        value=3.0, min_value=0.0, max_value=10.0, step=0.1, unit="%", color=COLOR_BLUE
    )

    st.divider()
    st.markdown("##### 📤 הוצאה על שכירות למגורים")
    rent_paid_monthly = compact_number_input(
        "שכר דירה חודשי — תשלום (₪)",
        value=6000, min_value=0, step=500, unit="₪", color=COLOR_RED
    )
    rent_paid_growth_pct = compact_number_input(
        "עלייה שנתית בדמי שכירות תשלום (%)",
        value=3.0, min_value=0.0, max_value=10.0, step=0.1, unit="%", color=COLOR_BLUE
    )

    st.divider()
    st.markdown("##### 🧾 מיסוי והוצאות על הכנסת שכירות")
    rental_tax_pct = compact_number_input(
        "שיעור מס אפקטיבי על שכירות (%)",
        value=10.0, min_value=0.0, max_value=50.0, step=0.5, unit="%", color=COLOR_RED
    )
    st.caption("ברירת מחדל 10% — מסלול סעיף 122 (ללא ניכוי הוצאות). ניתן להתאים.")

    st.markdown("**הוצאות תחזוקה חודשיות — מגיל ההשכרה (גיל 66)**")
    maintenance_early_monthly = compact_number_input(
        "תחזוקה — 10 שנים ראשונות (₪/חודש)",
        value=500, min_value=0, step=100, unit="₪", color=COLOR_RED
    )
    st.caption("תיקונים שוטפים, ועד בית, ביטוח — בעשור הראשון להשכרה.")
    maintenance_late_monthly = compact_number_input(
        "תחזוקה — מ-10 שנים ואילך (₪/חודש)",
        value=1000, min_value=0, step=100, unit="₪", color=COLOR_RED
    )
    st.caption("עלייה בהוצאות תחזוקה עם גיל הדירה — תיקונים גדולים יותר.")

    st.divider()
    st.markdown("##### 🏦 משכנתה הפוכה — קצבה חודשית קבועה מהנכס")
    st.caption("הבנק מחשב קצבה חודשית קבועה לכל החיים לפי שווי הנכס, גיל ההפעלה וריבית. החיסכון נשאר נזיל כקרן חירום.")
    enable_rm = st.checkbox("הפעל משכנתה הפוכה", value=False, key="enable_rm")

    if enable_rm:
        rm_annual_rate_pct = compact_number_input(
            "ריבית שנתית ממוצעת (%)",
            value=5.5, min_value=1.0, max_value=12.0, step=0.1, unit="%", color=COLOR_RED
        )
        rm_start_age = compact_number_input(
            "גיל התחלת קצבה מהמשכנתה",
            value=72, min_value=60, max_value=90, step=1, unit="גיל", color=COLOR_BLUE
        )
        rm_life_expectancy_age = compact_number_input(
            "גיל תוחלת חיים (לחישוב הקצבה)",
            value=90, min_value=70, max_value=105, step=1, unit="גיל", color=COLOR_BLUE
        )
        st.caption("הבנק מחלק את ההלוואה על פני שנות החיים הצפויות. ככל שמפעיל מוקדם יותר — הקצבה גבוהה יותר.")
        rm_max_ltv_pct = compact_number_input(
            "LTV — תקרת הלוואה מול שווי נכס (%)",
            value=55.0, min_value=10.0, max_value=80.0, step=5.0, unit="%", color=COLOR_BLUE
        )
        st.caption("בישראל: ~45% לגיל 60, ~55% לגיל 65–70, ~65% לגיל 75+.")
        rm_origination_fee_pct = compact_number_input(
            "עמלת פתיחת תיק — חד פעמית (%)",
            value=2.0, min_value=0.0, max_value=5.0, step=0.5, unit="%", color=COLOR_RED
        )
    else:
        rm_annual_rate_pct = 5.5
        rm_start_age = 72
        rm_life_expectancy_age = 90
        rm_max_ltv_pct = 55.0
        rm_origination_fee_pct = 2.0

    return {
        "net_for_rental": net_for_rental,
        "rental_income_monthly": rental_income_monthly,
        "rental_income_growth_rate": rental_income_growth_pct / 100,
        "rent_paid_monthly": rent_paid_monthly,
        "rent_paid_growth_rate": rent_paid_growth_pct / 100,
        "rental_tax_rate": rental_tax_pct / 100,
        "maintenance_early_monthly": maintenance_early_monthly,
        "maintenance_late_monthly": maintenance_late_monthly,
        "current_property_value": current_property_value,
        "rental_property_appreciation": rental_appreciation_pct / 100,
        "rm_enabled": enable_rm,
        "rm_annual_rate": rm_annual_rate_pct / 100,
        "rm_start_age": rm_start_age,
        "rm_life_expectancy_age": rm_life_expectancy_age,
        "rm_max_ltv": rm_max_ltv_pct / 100,
        "rm_origination_fee": rm_origination_fee_pct / 100,
    }
