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
    st.caption("תשואת מסלול כללי (כ-6%). מימון עד 80% מהתיק (הצבירה + ההלוואה).")

    # מודל עמית: הכסף נשאר מושקע וההלוואה קונה את הבית. התיק המושקע והממושכן =
    # הצבירה + ההלוואה. מימון עד 80% מהתיק => הלוואה עד פי 4 מהצבירה, וגם עד מחיר הבית.
    loan_cap = int(min(new_apartment_cost, 4.0 * net_for_190) // 100000 * 100000)
    default_loan = min(int(DEFAULTS["loan_amount"]), loan_cap)

    loan_amount = compact_number_input(
        "סכום ההלוואה (₪)",
        value=default_loan, min_value=0, max_value=loan_cap,
        step=100000, unit="₪", color=COLOR_RED
    )
    st.caption(f"מ-0 (ללא מינוף, קניית הבית במזומן) ועד {format_shekel(loan_cap)}. תקרת מימון 80% מהתיק (הצבירה + ההלוואה), כמקובל בקופות בישראל.")

    loan_annual_rate = compact_number_input(
        "ריבית שנתית על ההלוואה (%)",
        value=DEFAULTS["loan_annual_rate"] * 100, min_value=1.0, max_value=12.0,
        step=0.05, unit="%", color=COLOR_RED
    )
    st.caption("בערך פריים פחות 0.75. הריבית מצטברת לחוב, בלי תשלום חודשי, ונפרעת מהעיזבון.")

    # יחס המימון מחושב כנגד התיק המושקע והממושכן (הצבירה + ההלוואה)
    portfolio = net_for_190 + loan_amount
    ltv = (loan_amount / portfolio * 100) if portfolio > 0 else 0.0
    show_net_summary("תיק מושקע וממושכן במסלול 5 (צבירה + הלוואה)", portfolio)
    _icon = "🟢" if ltv <= 50 else ("🟡" if ltv <= 70 else "🔴")
    st.caption(f"{_icon} שיעור מימון: {ltv:.0f}% מהתיק. חסום ב-80%, תקרת הקופות. ככל שקרוב לתקרה, פחות כרית עד דרישת השלמה.")

    return {
        "loan_amount": loan_amount,
        "loan_annual_rate": loan_annual_rate / 100,
    }
