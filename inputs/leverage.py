import streamlit as st
from inputs.ui_components import compact_number_input, show_net_summary, format_shekel, COLOR_GREEN, COLOR_RED, COLOR_BLUE, DEFAULTS


def render_leverage_inputs(net_for_190, new_apartment_cost):
    """Track 5 — leverage via a balloon loan against the investment portfolio.

    The home is bought with a loan instead of cash, so the home-money stays
    invested. Portfolio = track-1 liquid (net_for_190) + loan. The loan is the
    single dial: 0 = identical to track 1, up to the home price = full leverage.
    """
    st.subheader("🏦 מסלול 5 — מינוף (הלוואת בלון)")
    st.caption("קונים את הדירה בהלוואת בלון כנגד תיק ההשקעות במקום במזומן, כך שכסף הדירה נשאר מושקע.")
    st.caption("מיסוי ותשואה כמו תיקון 190. מחיר הדירה ועליית הערך נלקחים משדה הדירה החדשה.")

    # תקרת מימון 75%. יחס חוב לשווי 75% פירושו שההלוואה לא עוברת פי שלושה מהחלק
    # הנזיל של התיק (loan / (net_for_190 + loan) <= 0.75  =>  loan <= 3 * net_for_190).
    # מגבילים גם למחיר הדירה, כי אין צורך ללוות מעבר לעלות הרכישה.
    MAX_LTV = 0.75
    cap_by_ltv = MAX_LTV / (1 - MAX_LTV) * net_for_190  # = 3 * net_for_190
    loan_cap = int(min(new_apartment_cost, cap_by_ltv) // 100000 * 100000)
    default_loan = min(int(DEFAULTS["loan_amount"]), loan_cap)

    loan_amount = compact_number_input(
        "סכום ההלוואה (₪)",
        value=default_loan, min_value=0, max_value=loan_cap,
        step=100000, unit="₪", color=COLOR_RED
    )
    st.caption(f"מ-0 (זהה למסלול 1, ללא מינוף) ועד תקרת מימון של 75% מהתיק ({format_shekel(loan_cap)}). כל שקל הלוואה נשאר מושקע בתיק.")

    loan_annual_rate = compact_number_input(
        "ריבית שנתית על ההלוואה (%)",
        value=DEFAULTS["loan_annual_rate"] * 100, min_value=1.0, max_value=12.0,
        step=0.05, unit="%", color=COLOR_RED
    )
    st.caption("בערך פריים פחות 0.75. הריבית מצטברת לחוב, בלי תשלום חודשי, ונפרעת מהעיזבון.")

    # Live view of the resulting portfolio and leverage ratio
    portfolio = net_for_190 + loan_amount
    ltv = (loan_amount / portfolio * 100) if portfolio > 0 else 0.0
    show_net_summary("תיק מושקע במסלול 5 (מסלול 1 + הלוואה)", portfolio)
    _icon = "🟢" if ltv <= 50 else ("🟡" if ltv <= 65 else "🔴")
    st.caption(f"{_icon} מינוף: {ltv:.0f}% מהתיק. השדה חסום בתקרת מימון של 75%, כמקובל אצל מלווים. ככל שקרוב לתקרה, מסוכן יותר לדרישת ביטחונות.")

    return {
        "loan_amount": loan_amount,
        "loan_annual_rate": loan_annual_rate / 100,
    }
