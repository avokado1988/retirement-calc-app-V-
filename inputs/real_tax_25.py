import streamlit as st
from inputs.ui_components import compact_number_input, show_net_summary, format_shekel, COLOR_BLUE, COLOR_RED, DEFAULTS


def render_track2_inputs(remaining_for_gimel):
    st.caption(f"הון זמין: {format_shekel(remaining_for_gimel)}")
    st.info(
        "כל ההון נשאר נזיל ועובד בשוק. משלמים מס רק על הרווח הריאלי (מעל האינפלציה). "
        "גמישות מרבית — ניתן למשוך כל סכום בכל עת. **סיכון:** אין רשת ביטחון לאריכות ימים — "
        "אם התיק ייגמר, אין קצבה שתחליף."
    )
    show_net_summary(title="סך הון נטו פנוי במסלול 2", amount=remaining_for_gimel)

    annual_return_25 = compact_number_input(
        "תשואה שנתית צפויה — מסלול 2 (%)",
        value=DEFAULTS["annual_return"] * 100, min_value=0.0, max_value=15.0, step=0.1, unit="%", color=COLOR_BLUE
    ) / 100
    management_fee_25 = compact_number_input(
        "דמי ניהול שנתיים — מסלול 2 (%)",
        value=DEFAULTS["management_fee"] * 100, min_value=0.0, max_value=2.0, step=0.05, unit="%", color=COLOR_RED
    ) / 100

    return {
        "net_for_real_pathway": remaining_for_gimel,
        "annual_return_25": annual_return_25,
        "management_fee_25": management_fee_25,
    }


def render_track3_inputs(net_for_hybrid):
    st.caption("🔗 הון נזיל זהה למסלול 1 אחרי ניכוי רכישת הקצבה.")
    st.info(
        "שילוב: חלק מההון הומר לקצבה חודשית מובטחת (כרית ביטחון), והשאר מנוהל ב-25% ריאלי. "
        "מאזן בין ביטחון לגמישות. **סיכון:** מורכב — טעות במקדם ההמרה קשה לתיקון, "
        "וההון הנזיל קטן יותר מבמסלול 2."
    )
    show_net_summary(title="סך הון נטו פנוי במסלול 3", amount=net_for_hybrid)

    annual_return_hybrid = compact_number_input(
        "תשואה שנתית צפויה — מסלול 3 (%)",
        value=DEFAULTS["annual_return"] * 100, min_value=0.0, max_value=15.0, step=0.1, unit="%", color=COLOR_BLUE
    ) / 100
    management_fee_hybrid = compact_number_input(
        "דמי ניהול שנתיים — מסלול 3 (%)",
        value=DEFAULTS["management_fee"] * 100, min_value=0.0, max_value=2.0, step=0.05, unit="%", color=COLOR_RED
    ) / 100

    return {
        "annual_return_hybrid": annual_return_hybrid,
        "management_fee_hybrid": management_fee_hybrid,
    }


def render_25_inputs(remaining_for_gimel):
    """Legacy combined function — still works if called directly."""
    t2 = render_track2_inputs(remaining_for_gimel)
    t3 = render_track3_inputs(remaining_for_gimel)
    return {**t2, **t3}
