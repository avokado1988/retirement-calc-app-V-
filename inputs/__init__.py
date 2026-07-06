import streamlit as st
from .ui_components import DEFAULTS
from .timeline import render_timeline_inputs
from .wealth import render_wealth_inputs
from .expenses import render_expenses_inputs
from .incomes import render_incomes_inputs
from .amendment_190 import render_190_inputs
from .real_tax_25 import render_track2_inputs, render_track3_inputs
from .rental import render_rental_inputs
from .leverage import render_leverage_inputs

def render_all_sidebar_inputs():
    """מנהל את תפריט הצד ומחזיר אובייקט קלטים מאוחד"""
    st.sidebar.title("⚙️ פרמטרים ומחשבון פרישה")

    inputs_dict = {}

    st.sidebar.markdown("#### 🎯 הגדרות בסיס")

    with st.sidebar.expander("1. נתוני זמנים ופרישה", expanded=True):
        inputs_dict["timeline"] = render_timeline_inputs()

    with st.sidebar.expander("2. נתוני הון ונדל\"ן", expanded=False):
        inputs_dict["wealth"] = render_wealth_inputs()

    remaining_wealth = inputs_dict["wealth"]["remaining_for_gimel"]

    with st.sidebar.expander("3. מקורות הכנסה וקצבה", expanded=False):
        incomes_ui = render_incomes_inputs(remaining_wealth)

    with st.sidebar.expander("4. תקציב והוצאות", expanded=False):
        expenses_ui = render_expenses_inputs()

    # Wire incomes back into the unified inputs dict
    inputs_dict["wealth"]["national_insurance"] = incomes_ui["national_insurance"]
    expenses_ui["work_income"] = incomes_ui["work_income"]
    expenses_ui["work_end_age"] = incomes_ui["work_end_age"]
    inputs_dict["expenses"] = expenses_ui

    st.sidebar.divider()
    st.sidebar.markdown("#### 🔧 הגדרות מתקדמות — מסלולים")

    capital_for_pension = incomes_ui.get("capital_for_pension", 0)

    with st.sidebar.expander("5. מסלול 1 — תיקון 190", expanded=False):
        _show_1 = st.checkbox("הצג מסלול זה בהשוואה", value=(1 in DEFAULTS["visible_tracks"]), key="show_track_1")
        a190 = render_190_inputs(remaining_wealth, capital_for_pension)
        # Inject pension data from incomes
        a190["desired_pension"]      = incomes_ui["desired_pension"]
        a190["securing_years"]       = incomes_ui["securing_years"]
        a190["base_coefficient"]     = incomes_ui["base_coefficient"]
        a190["adjusted_coefficient"] = incomes_ui["adjusted_coefficient"]
        a190["capital_for_pension"]  = capital_for_pension
        inputs_dict["amendment_190"] = a190

    with st.sidebar.expander("6. מסלול 2 — 25% מס ריאלי (ללא קצבה)", expanded=False):
        _show_2 = st.checkbox("הצג מסלול זה בהשוואה", value=(2 in DEFAULTS["visible_tracks"]), key="show_track_2")
        t2 = render_track2_inputs(remaining_wealth)

    net_for_hybrid = inputs_dict["amendment_190"].get("net_for_190", 0)
    with st.sidebar.expander("7. מסלול 3 — 25% ריאלי + קצבה מזערית (היברידי)", expanded=False):
        _show_3 = st.checkbox("הצג מסלול זה בהשוואה", value=(3 in DEFAULTS["visible_tracks"]), key="show_track_3")
        t3 = render_track3_inputs(net_for_hybrid)

    inputs_dict["real_tax_25"] = {**t2, **t3, "net_for_hybrid": net_for_hybrid}

    with st.sidebar.expander("8. מסלול 4 — השכרת הנכס", expanded=False):
        _show_4 = st.checkbox("הצג מסלול זה בהשוואה", value=(4 in DEFAULTS["visible_tracks"]), key="show_track_4")
        _check_age = float(inputs_dict["timeline"].get("check_age", DEFAULTS["check_age"]))
        _start_age = float(inputs_dict["timeline"].get("start_age", 67.0))
        inputs_dict["rental"] = render_rental_inputs(inputs_dict["wealth"], _check_age, _start_age)

    _net_for_190 = inputs_dict["amendment_190"].get("net_for_190", 0)
    _new_apt = float(inputs_dict["wealth"].get("new_apartment_cost", 5500000))
    with st.sidebar.expander("9. מסלול 5 — מינוף (הלוואת בלון)", expanded=False):
        _show_5 = st.checkbox("הצג מסלול זה בהשוואה", value=(5 in DEFAULTS["visible_tracks"]), key="show_track_5")
        inputs_dict["leverage"] = render_leverage_inputs(_net_for_190, _new_apt)

    inputs_dict["visible_tracks"] = [
        t for t, show in [(1, _show_1), (2, _show_2), (3, _show_3), (4, _show_4), (5, _show_5)] if show
    ]

    return inputs_dict
