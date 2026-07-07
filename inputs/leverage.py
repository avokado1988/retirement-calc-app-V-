import streamlit as st
from inputs.ui_components import compact_number_input, show_net_summary, format_shekel, COLOR_GREEN, COLOR_RED, COLOR_BLUE, DEFAULTS


def render_leverage_inputs(net_for_190, new_apartment_cost):
    """Track 5 — leverage via a balloon loan against the investment portfolio.

    The home is bought with a loan instead of cash, so the home-money stays
    invested. Portfolio = track-1 liquid (net_for_190) + loan. The loan is the
    single dial: 0 = identical to track 1, up to the home price = full leverage.
    """
    st.subheader("🏦 מסלול 5 — מינוף (הלוואת בלון)")
    st.caption("הלוואה כנגד הצבירה (מסלול כללי) לפי חוקי הקופות בישראל, והכסף השאול מושקע.")
    st.caption("תשואת מסלול כללי (כ-5.5%). הבטוחה היא הצבירה בלבד, והמימון עד 80% ממנה.")

    # חוקי הקופות בישראל: ההלוואה נלקחת כנגד הצבירה (מסלול כללי), עד 80% ממנה.
    # הבטוחה היא הצבירה בלבד, ולכן התקרה היא 80% מהחלק הנזיל, לא יחס על סך התיק.
    MAX_ADVANCE = 0.80
    loan_cap = int((MAX_ADVANCE * net_for_190) // 100000 * 100000)
    default_loan = min(int(DEFAULTS["loan_amount"]), loan_cap)

    loan_amount = compact_number_input(
        "סכום ההלוואה (₪)",
        value=default_loan, min_value=0, max_value=loan_cap,
        step=100000, unit="₪", color=COLOR_RED
    )
    st.caption(f"מ-0 (ללא מינוף) ועד 80% מהצבירה ({format_shekel(loan_cap)}). זו תקרת המימון המקובלת בקופות בישראל.")

    loan_annual_rate = compact_number_input(
        "ריבית שנתית על ההלוואה (%)",
        value=DEFAULTS["loan_annual_rate"] * 100, min_value=1.0, max_value=12.0,
        step=0.05, unit="%", color=COLOR_RED
    )
    st.caption("בערך פריים פחות 0.75. הריבית מצטברת לחוב, בלי תשלום חודשי, ונפרעת מהעיזבון.")

    # יחס המימון מחושב כנגד הצבירה (הבטוחה), לא כנגד סך התיק
    portfolio = net_for_190 + loan_amount
    ltv = (loan_amount / net_for_190 * 100) if net_for_190 > 0 else 0.0
    show_net_summary("תיק מושקע במסלול 5 (צבירה + הלוואה)", portfolio)
    _icon = "🟢" if ltv <= 40 else ("🟡" if ltv <= 65 else "🔴")
    st.caption(f"{_icon} שיעור מימון: {ltv:.0f}% מהצבירה. חסום ב-80%, תקרת הקופות. ככל שקרוב לתקרה, פחות כרית עד דרישת השלמה.")

    return {
        "loan_amount": loan_amount,
        "loan_annual_rate": loan_annual_rate / 100,
    }
