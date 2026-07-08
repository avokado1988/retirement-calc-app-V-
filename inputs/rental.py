import streamlit as st
from inputs.ui_components import compact_number_input, show_net_summary, format_shekel, COLOR_GREEN, COLOR_RED, COLOR_BLUE, DEFAULTS

def render_rental_inputs(wealth_data, check_age=DEFAULTS["check_age"], start_age=67.0):
    existing_savings = float(wealth_data.get("existing_savings", 440000))
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
        value=DEFAULTS["rental_property_value"], min_value=0, step=100000, unit="₪", color=COLOR_GREEN
    )
    rental_appreciation_pct = compact_number_input(
        "עליית ערך שנתית — דירה מושכרת (%)",
        value=DEFAULTS["rental_property_appreciation"] * 100, min_value=0.0, max_value=10.0, step=0.1, unit="%", color=COLOR_BLUE
    )
    st.caption("2.3%. פנטהאוס יוקרה מתייקר לאט יותר באחוזים, ובעוד 30 שנה גם מתיישן, לכן בערך אינפלציה בלבד.")

    st.divider()
    st.markdown("##### 📥 הכנסה מהשכרת הנכס")
    rental_income_monthly = compact_number_input(
        "שכר דירה חודשי — גביה (₪)",
        value=DEFAULTS["rental_income_monthly"], min_value=0, step=500, unit="₪", color=COLOR_GREEN
    )
    rental_income_growth_pct = compact_number_input(
        "עלייה שנתית בדמי שכירות גביה (%)",
        value=DEFAULTS["rental_income_growth_rate"] * 100, min_value=0.0, max_value=10.0, step=0.1, unit="%", color=COLOR_BLUE
    )

    st.divider()
    st.markdown("##### 📤 הוצאה על שכירות למגורים")
    rent_paid_monthly = compact_number_input(
        "שכר דירה חודשי — תשלום (₪)",
        value=DEFAULTS["rent_paid_monthly"], min_value=0, step=500, unit="₪", color=COLOR_RED
    )
    rent_paid_growth_pct = compact_number_input(
        "עלייה שנתית בדמי שכירות תשלום (%)",
        value=DEFAULTS["rent_paid_growth_rate"] * 100, min_value=0.0, max_value=10.0, step=0.1, unit="%", color=COLOR_BLUE
    )

    st.divider()
    st.markdown("##### 🧾 מיסוי והוצאות על הכנסת שכירות")
    rental_tax_pct = compact_number_input(
        "שיעור מס אפקטיבי על שכירות (%)",
        value=DEFAULTS["rental_tax_rate"] * 100, min_value=0.0, max_value=50.0, step=0.5, unit="%", color=COLOR_RED
    )
    st.caption("ברירת מחדל 10% — מסלול סעיף 122 (ללא ניכוי הוצאות). ניתן להתאים.")

    st.markdown("**הוצאות תחזוקה — % מדמי השכירות (מגיל ההשכרה, גיל 66)**")
    maintenance_early_pct = compact_number_input(
        "תחזוקה — 10 שנים ראשונות (% מהשכירות)",
        value=DEFAULTS["maintenance_early_pct"] * 100, min_value=0.0, max_value=30.0, step=0.5, unit="%", color=COLOR_RED
    )
    st.caption("10%. סך ההוצאות בשוק, ריקנות ותיקונים וועד וביטוח, הוא 15-25% מהשכירות. 10% בעשור הראשון מגלם גם חודש ריק בשנה.")
    maintenance_late_pct = compact_number_input(
        "תחזוקה — מ-10 שנים ואילך (% מהשכירות)",
        value=DEFAULTS["maintenance_late_pct"] * 100, min_value=0.0, max_value=30.0, step=0.5, unit="%", color=COLOR_RED
    )
    st.caption("15%. אחרי עשור הבניין מתיישן, תיקונים גדולים ושיפוצים, אז ההוצאה עולה לקצה הגבוה של הטווח.")

    st.divider()
    st.caption(
        f"🏦 משכנתה הפוכה — אוטומטית. אם החסכונות יורדים ל-₪{int(DEFAULTS['rm_savings_floor']):,} "
        f"ועדיין יש גרעון, המערכת לוקחת משכנתה הפוכה שמכסה את הגרעון עד הגיל הנבדק "
        f"(ריבית {DEFAULTS['rm_annual_rate']*100:.1f}%). החוב יורד מסך הנכסים בכרטיס מסלול 4."
    )

    return {
        "net_for_rental": net_for_rental,
        "rental_income_monthly": rental_income_monthly,
        "rental_income_growth_rate": rental_income_growth_pct / 100,
        "rent_paid_monthly": rent_paid_monthly,
        "rent_paid_growth_rate": rent_paid_growth_pct / 100,
        "rental_tax_rate": rental_tax_pct / 100,
        "maintenance_early_pct": maintenance_early_pct / 100,
        "maintenance_late_pct": maintenance_late_pct / 100,
        "current_property_value": current_property_value,
        "rental_property_appreciation": rental_appreciation_pct / 100,
    }
