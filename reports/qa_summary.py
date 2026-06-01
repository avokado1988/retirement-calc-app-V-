import streamlit as st
import pandas as pd
from inputs.ui_components import format_shekel

def render_qa_summary_page(results, user_inputs):
    """
    קובץ בדיקות (QA) עצמאי לחלוטין - ריכוז אינפוטים ושורות סיכום להעתקה מהירה.
    אינו מבצע חישובים — רק שולף נתונים מ-user_inputs ומ-results.
    """
    df_history = results["df"]
    df_full = results.get("df_full", df_history)

    # ─── שליפת מילוני קלט ───────────────────────────────────────────────────
    timeline      = user_inputs.get("timeline", {})
    wealth        = user_inputs.get("wealth", {})
    expenses      = user_inputs.get("expenses", {})
    amendment_190 = user_inputs.get("amendment_190", {})
    real_tax_25   = user_inputs.get("real_tax_25", {})
    rental        = user_inputs.get("rental", {})

    # ─── זמנים ───────────────────────────────────────────────────────────────
    start_age  = float(timeline.get("start_age", 65.5))
    retire_age = float(timeline.get("retirement_age", start_age))
    check_age  = float(timeline.get("check_age", 87.0))

    # ─── הוצאות ──────────────────────────────────────────────────────────────
    inflation          = float(expenses.get("expected_inflation", 0.023))
    age_75_85_inc      = float(expenses.get("age_75_85_increase", 0.005))
    age_85_plus_inc    = float(expenses.get("age_85_plus_increase", 0.015))
    base_exp           = float(expenses.get("current_expenses", 11000))
    caregiver_cost     = float(expenses.get("caregiver_cost", 3500))
    one_time_exp       = float(expenses.get("one_time_expense", 80000))
    one_time_freq      = float(expenses.get("one_time_frequency", 8))
    work_inc           = float(expenses.get("work_income", 0))
    work_end_age       = float(expenses.get("work_end_age", retire_age))

    # ─── הכנסות ──────────────────────────────────────────────────────────────
    ni_base            = float(wealth.get("national_insurance", 2500))

    # ─── הון ונדל"ן ──────────────────────────────────────────────────────────
    net_sale           = float(wealth.get("net_sale", 0) or 0)
    existing_savings   = float(wealth.get("existing_savings", 0) or 0)
    new_apartment_cost = float(wealth.get("new_apartment_cost", 0) or 0)
    kids_help          = float(wealth.get("kids_help", 0) or 0)
    emergency_fund     = float(wealth.get("emergency_fund", 0) or 0)
    prop_appreciation  = float(wealth.get("property_appreciation", 0.023))
    remaining_gimel    = float(wealth.get("remaining_for_gimel", 0) or 0)

    # ─── מסלול 1 — תיקון 190 ─────────────────────────────────────────────────
    desired_pension     = float(amendment_190.get("desired_pension", 0) or 0)
    securing_years      = float(amendment_190.get("securing_years", 20))
    base_coeff          = float(amendment_190.get("base_coefficient", 200))
    adj_coeff           = float(amendment_190.get("adjusted_coefficient", 220))
    capital_for_pension = float(amendment_190.get("capital_for_pension", 0) or 0)
    net_for_190         = float(amendment_190.get("net_for_190", 0) or 0)
    yield_190           = float(amendment_190.get("annual_return_190", 0.05))
    fee_190             = float(amendment_190.get("management_fee_190", 0.006))

    # ─── מסלול 2 — 25% ריאלי ─────────────────────────────────────────────────
    net_for_25          = float(real_tax_25.get("net_for_real_pathway", 0) or 0)
    yield_25            = float(real_tax_25.get("annual_return_25", 0.05))
    fee_25              = float(real_tax_25.get("management_fee_25", 0.006))

    # ─── מסלול 3 — היברידי ───────────────────────────────────────────────────
    net_for_hybrid      = float(real_tax_25.get("net_for_hybrid", 0) or 0)
    yield_hybrid        = float(real_tax_25.get("annual_return_hybrid", 0.05))
    fee_hybrid          = float(real_tax_25.get("management_fee_hybrid", 0.006))

    # ─── מסלול 4 — שכירות ────────────────────────────────────────────────────
    net_for_rental          = float(rental.get("net_for_rental", 0) or 0)
    rental_inc_monthly      = float(rental.get("rental_income_monthly", 0))
    rental_inc_growth       = float(rental.get("rental_income_growth_rate", 0.03))
    rent_paid_monthly       = float(rental.get("rent_paid_monthly", 0))
    rent_paid_growth        = float(rental.get("rent_paid_growth_rate", 0.03))
    rental_tax_rate         = float(rental.get("rental_tax_rate", 0.10))
    rental_prop_value       = float(rental.get("current_property_value", wealth.get("net_sale", 0) or 0))
    rental_appreciation     = float(rental.get("rental_property_appreciation", 0.015))
    rm_enabled_s            = bool(rental.get("rm_enabled", False))
    rm_annual_rate_s        = float(rental.get("rm_annual_rate", 0.055))
    rm_max_ltv_s            = float(rental.get("rm_max_ltv", 0.55))

    # ─── שליפת תוצאות מהמנוע ─────────────────────────────────────────────────
    def _row(df, age):
        sub = df[df["גיל"] >= age]
        return sub.iloc[0] if not sub.empty else df.iloc[-1]

    row_retire = _row(df_full, retire_age)
    row_check  = _row(df_full, check_age)
    row_100    = _row(df_full, 100.0)

    b190_ret   = float(row_retire["צבירה תיקון 190"])
    b25_ret    = float(row_retire["צבירה מסלול ריאלי"])
    bhyb_ret   = float(row_retire.get("צבירה מסלול היברידי", 0))
    brent_ret  = float(row_retire.get("צבירה מסלול שכירות", 0))

    b190_chk   = float(row_check["צבירה תיקון 190"])
    b25_chk    = float(row_check["צבירה מסלול ריאלי"])
    bhyb_chk   = float(row_check.get("צבירה מסלול היברידי", 0))
    brent_chk  = float(row_check.get("צבירה מסלול שכירות", 0))

    b190_100   = float(row_100["צבירה תיקון 190"])
    b25_100    = float(row_100["צבירה מסלול ריאלי"])
    bhyb_100   = float(row_100.get("צבירה מסלול היברידי", 0))
    brent_100  = float(row_100.get("צבירה מסלול שכירות", 0))

    # ─── תזרים מסלול שכירות ──────────────────────────────────────────────────
    df_full["rental_cashflow"] = df_full["תזרים נטו שכירות"]
    cf_retire = float(_row(df_full, retire_age)["rental_cashflow"])
    cf_check  = float(_row(df_full, check_age)["rental_cashflow"])

    df_after_retire = df_full[df_full["גיל"] >= retire_age]
    neg_rows = df_after_retire[df_after_retire["rental_cashflow"] < 0]
    flip_age = float(neg_rows.iloc[0]["גיל"]) if not neg_rows.empty else None

    # ─── משכנתה הפוכה ────────────────────────────────────────────────────────
    rm_activation_age_s = None
    rm_equity_check_s   = None
    rm_interest_total_s = None
    if rm_enabled_s and "משכנתה הפוכה — יתרת חוב" in df_full.columns:
        rm_rows = df_full[df_full["משכנתה הפוכה — יתרת חוב"] > 0]
        if not rm_rows.empty:
            rm_activation_age_s = float(rm_rows.iloc[0]["גיל"])
        rm_equity_check_s   = float(_row(df_full, check_age).get("משכנתה הפוכה — הון עצמי", 0.0))
        rm_interest_total_s = float(df_full["משכנתה הפוכה — ריבית חודשית"].sum())

    # ─── בלוק טקסט משכנתה הפוכה לסיכום ─────────────────────────────────────
    if rm_enabled_s:
        _rm_act = f"גיל {rm_activation_age_s:.1f}" if rm_activation_age_s else "לא הופעלה"
        _rm_eq  = f"{rm_equity_check_s:,.0f} ש\"ח" if rm_equity_check_s is not None else "---"
        _rm_int = f"{rm_interest_total_s:,.0f} ש\"ח" if rm_interest_total_s else "---"
        rm_summary_block = (
            f"  ריבית שנתית RM     : {rm_annual_rate_s*100:.1f}%\n"
            f"  LTV מקסימלי        : {rm_max_ltv_s*100:.0f}%\n"
            f"  גיל הפעלה          : {_rm_act}\n"
            f"  הון עצמי בגיל {check_age:.0f}  : {_rm_eq}\n"
            f"  סהכ ריבית RM       : {_rm_int}"
        )
    else:
        rm_summary_block = ""

    # ─── משיכה חודשית נדרשת (כל מסלול, גיל בדיקה) ───────────────────────────
    inf_chk    = float(row_check.get("inflation_factor", 1.0))
    exp_chk    = float(row_check["הוצאה נומינלית"])
    inc_chk    = float(row_check["הכנסה נומינלית"])
    pen_chk    = float(row_check.get("הכנסה מקצבה מזערית", 0))
    nn_190_chk = max(0.0, exp_chk - (inc_chk + pen_chk))
    nn_25_chk  = max(0.0, exp_chk - inc_chk)
    nn_hyb_chk = max(0.0, exp_chk - (inc_chk + pen_chk))
    nn_rent_chk = max(0.0, -cf_check)  # deficit = what must come from portfolio

    # =========================================================================
    #  UI
    # =========================================================================
    st.subheader("📋 כלי סיכום נתונים להעתקה מהירה (QA)")
    st.caption("הדף שולף נתונים ישירות מהסליידרים ומהמנוע — אינו מחשב דבר בעצמו.")

    # ─── גוש טקסט להעתקה ─────────────────────────────────────────────────────
    copy_text = f"""=== סימולציית פרישה אקטוארית — דוח QA מהיר ===

━━━━━━━━━━  זמנים  ━━━━━━━━━━
  גיל התחלה          : {start_age}
  גיל פרישה          : {retire_age}
  גיל בדיקה          : {check_age}

━━━━━━━━━━  הוצאות  ━━━━━━━━━━
  הוצאה חודשית בסיס  : {base_exp:,.0f} ₪
  אינפלציה שנתית     : {inflation*100:.1f}%
  תוספת אינפלציה 75–85 : {age_75_85_inc*100:.1f}%
  תוספת אינפלציה 85+  : {age_85_plus_inc*100:.1f}%
  מטפלת סיעודית (מ-85): {caregiver_cost:,.0f} ₪/חודש
  הוצאה חד-פעמית     : {one_time_exp:,.0f} ₪ (כל {one_time_freq:.0f} שנים)

━━━━━━━━━━  הכנסות  ━━━━━━━━━━
  הכנסה מעבודה       : {work_inc:,.0f} ₪/חודש (עד גיל {work_end_age:.1f})
  ביטוח לאומי        : {ni_base:,.0f} ₪/חודש (ערך בסיס)

━━━━━━━━━━  הון ונדל"ן  ━━━━━━━━━━
  נטו ממכירה         : {net_sale:,.0f} ₪
  חסכונות קיימים     : {existing_savings:,.0f} ₪
  עלות דירה חדשה     : {new_apartment_cost:,.0f} ₪
  עזרה לילדים        : {kids_help:,.0f} ₪
  קרן חירום          : {emergency_fund:,.0f} ₪
  הון פנוי למסלולים  : {remaining_gimel:,.0f} ₪
  עליית ערך נדל"ן    : {prop_appreciation*100:.1f}%/שנה

━━━━━━━━━━  מסלול 1 — תיקון 190  ━━━━━━━━━━
  קצבה רצויה         : {desired_pension:,.0f} ₪/חודש
  תקופת אבטחה        : {securing_years:.0f} שנים
  מקדם בסיסי         : {base_coeff:.1f}
  מקדם משוקלל        : {adj_coeff:.1f}
  הון לרכישת קצבה    : {capital_for_pension:,.0f} ₪
  הון נטו במסלול 190 : {net_for_190:,.0f} ₪
  תשואה / דמי ניהול  : {yield_190*100:.1f}% / {fee_190*100:.2f}%

━━━━━━━━━━  מסלול 2 — 25% מס ריאלי  ━━━━━━━━━━
  הון במסלול         : {net_for_25:,.0f} ₪
  תשואה / דמי ניהול  : {yield_25*100:.1f}% / {fee_25*100:.2f}%

━━━━━━━━━━  מסלול 3 — היברידי  ━━━━━━━━━━
  הון במסלול         : {net_for_hybrid:,.0f} ₪
  תשואה / דמי ניהול  : {yield_hybrid*100:.1f}% / {fee_hybrid*100:.2f}%
  (קצבה — זהה למסלול 1)

━━━━━━━━━━  מסלול 4 — שכירות  ━━━━━━━━━━
  הון נזיל           : {net_for_rental:,.0f} ₪
  שווי דירה מושכרת   : {rental_prop_value:,.0f} ₪  (עליית ערך: {rental_appreciation*100:.1f}%/שנה)
  שכ"ד גביה          : {rental_inc_monthly:,.0f} ₪/חודש (צמיחה: {rental_inc_growth*100:.1f}%/שנה)
  שכ"ד תשלום         : {rent_paid_monthly:,.0f} ₪/חודש (צמיחה: {rent_paid_growth*100:.1f}%/שנה)
  מס שכירות          : {rental_tax_rate*100:.1f}%
  תזרים בפרישה       : {"+" if cf_retire >= 0 else ""}{cf_retire:,.0f} ₪/חודש
  תזרים בגיל {check_age:.0f}      : {"+" if cf_check >= 0 else ""}{cf_check:,.0f} ₪/חודש
  גיל היפוך תזרים    : {f"גיל {flip_age:.1f}" if flip_age else "נשאר חיובי לאורך כל הדרך"}
{rm_summary_block}

━━━━━━━━━━  תוצאות תיק נזיל — נקודות מפתח  ━━━━━━━━━━
  מסלול 1  | גיל פרישה ({retire_age:.1f}): {b190_ret:>14,.0f} ₪  |  גיל {check_age:.0f}: {b190_chk:>14,.0f} ₪  |  גיל 100: {b190_100:>14,.0f} ₪
  מסלול 2  | גיל פרישה ({retire_age:.1f}): {b25_ret:>14,.0f} ₪  |  גיל {check_age:.0f}: {b25_chk:>14,.0f} ₪  |  גיל 100: {b25_100:>14,.0f} ₪
  מסלול 3  | גיל פרישה ({retire_age:.1f}): {bhyb_ret:>14,.0f} ₪  |  גיל {check_age:.0f}: {bhyb_chk:>14,.0f} ₪  |  גיל 100: {bhyb_100:>14,.0f} ₪
  מסלול 4  | גיל פרישה ({retire_age:.1f}): {brent_ret:>14,.0f} ₪  |  גיל {check_age:.0f}: {brent_chk:>14,.0f} ₪  |  גיל 100: {brent_100:>14,.0f} ₪

━━━━━━━━━━  משיכה חודשית נדרשת — גיל {check_age:.0f}  ━━━━━━━━━━
  מסלול 1 (190 + קצבה)  : {nn_190_chk:>10,.0f} ₪/חודש
  מסלול 2 (25% ריאלי)   : {nn_25_chk:>10,.0f} ₪/חודש
  מסלול 3 (היברידי)      : {nn_hyb_chk:>10,.0f} ₪/חודש
  מסלול 4 (שכירות)       : {nn_rent_chk:>10,.0f} ₪/חודש  {"(גירעון תזרים)" if nn_rent_chk > 0 else "(תזרים עצמאי)"}
============================================================"""

    st.code(copy_text, language="text")

    # ─── טבלת תוצאות ויזואלית ────────────────────────────────────────────────
    st.write("---")
    st.markdown("**🔍 תיק נזיל — נקודות מפתח:**")
    df_summary = pd.DataFrame({
        "נקודת זמן": [
            f"גיל פרישה ({retire_age:.1f})",
            f"גיל נבדק ({check_age:.1f})",
            "גיל 100.0",
        ],
        "מסלול 1 — 190":        [format_shekel(b190_ret),  format_shekel(b190_chk),  format_shekel(b190_100)],
        "מסלול 2 — 25% ריאלי":  [format_shekel(b25_ret),   format_shekel(b25_chk),   format_shekel(b25_100)],
        "מסלול 3 — היברידי":    [format_shekel(bhyb_ret),  format_shekel(bhyb_chk),  format_shekel(bhyb_100)],
        "מסלול 4 — שכירות":     [format_shekel(brent_ret), format_shekel(brent_chk), format_shekel(brent_100)],
    })
    st.table(df_summary.set_index("נקודת זמן"))

    st.markdown(f"**💸 משיכה חודשית נדרשת — גיל {check_age:.0f}:**")
    df_withdrawal = pd.DataFrame({
        "מסלול": [
            "מסלול 1 — 190 + קצבה",
            "מסלול 2 — 25% ריאלי",
            "מסלול 3 — היברידי",
            "מסלול 4 — שכירות",
        ],
        "משיכה חודשית": [
            format_shekel(nn_190_chk),
            format_shekel(nn_25_chk),
            format_shekel(nn_hyb_chk),
            format_shekel(nn_rent_chk) if nn_rent_chk > 0 else "✅ תזרים עצמאי",
        ],
        "הערה": [
            "הוצאה פחות ב\"ל + קצבה",
            "הוצאה פחות ב\"ל בלבד",
            "הוצאה פחות ב\"ל + קצבה",
            "גירעון תזרים שכ\"ד" if nn_rent_chk > 0 else f"תזרים חיובי +{format_shekel(int(-cf_check))}",
        ],
    })
    st.table(df_withdrawal.set_index("מסלול"))
