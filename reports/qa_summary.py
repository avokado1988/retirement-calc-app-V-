import streamlit as st
import pandas as pd
from inputs.ui_components import format_shekel, DEFAULTS

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
    leverage      = user_inputs.get("leverage", {})

    # ─── רק המסלולים שנבחרו בסימולציה נכללים בדוח ────────────────────────────
    visible = set(user_inputs.get("visible_tracks", [1, 2, 3, 4, 5]))
    TRACK_TITLES = {
        1: "מסלול 1 — תיקון 190",
        2: "מסלול 2 — 25% מס ריאלי",
        3: "מסלול 3 — היברידי",
        4: "מסלול 4 — שכירות",
        5: "מסלול 5 — מינוף",
    }

    # ─── זמנים ───────────────────────────────────────────────────────────────
    start_age  = float(timeline.get("start_age", 65.5))
    retire_age = float(timeline.get("retirement_age", start_age))
    check_age  = float(timeline.get("check_age", DEFAULTS["check_age"]))

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

    # ─── מסלול 5 — מינוף ─────────────────────────────────────────────────────
    loan_amount_s     = float(leverage.get("loan_amount", 0) or 0)
    loan_rate_s       = float(leverage.get("loan_annual_rate", 0.045))
    gen_return_lev_s  = float(leverage.get("annual_return_lev", 0.06))

    # ─── מסלול 4 — שכירות ────────────────────────────────────────────────────
    net_for_rental          = float(rental.get("net_for_rental", 0) or 0)
    rental_inc_monthly      = float(rental.get("rental_income_monthly", 0))
    rental_inc_growth       = float(rental.get("rental_income_growth_rate", 0.03))
    rent_paid_monthly       = float(rental.get("rent_paid_monthly", 0))
    rent_paid_growth        = float(rental.get("rent_paid_growth_rate", 0.03))
    rental_tax_rate         = float(rental.get("rental_tax_rate", 0.10))
    rental_prop_value       = float(rental.get("current_property_value", wealth.get("net_sale", 0) or 0))
    rental_appreciation     = float(rental.get("rental_property_appreciation", 0.015))
    maintenance_early_pct_s = float(rental.get("maintenance_early_pct", 0.07))
    maintenance_late_pct_s  = float(rental.get("maintenance_late_pct", 0.12))
    # Reverse mortgage is automatic — detect activation from the simulation itself
    rm_enabled_s            = ("משכנתה הפוכה — יתרת חוב" in df_full.columns) and bool((df_full["משכנתה הפוכה — יתרת חוב"] > 0).any())
    rm_annual_rate_s        = float(DEFAULTS.get("rm_annual_rate", 0.06))

    # ─── שליפת תוצאות מהמנוע ─────────────────────────────────────────────────
    def _row(df, age):
        sub = df[df["גיל"] >= age]
        return sub.iloc[0] if not sub.empty else df.iloc[-1]

    row_retire = _row(df_full, retire_age)
    row_check  = _row(df_full, check_age)
    row_102    = _row(df_full, 102.0)

    b190_ret   = float(row_retire["צבירה תיקון 190"])
    b25_ret    = float(row_retire["צבירה מסלול ריאלי"])
    bhyb_ret   = float(row_retire.get("צבירה מסלול היברידי", 0))
    brent_ret  = float(row_retire.get("צבירה מסלול שכירות", 0))

    b190_chk   = float(row_check["צבירה תיקון 190"])
    b25_chk    = float(row_check["צבירה מסלול ריאלי"])
    bhyb_chk   = float(row_check.get("צבירה מסלול היברידי", 0))
    brent_chk  = float(row_check.get("צבירה מסלול שכירות", 0))

    b190_102   = float(row_102["צבירה תיקון 190"])
    b25_102    = float(row_102["צבירה מסלול ריאלי"])
    bhyb_102   = float(row_102.get("צבירה מסלול היברידי", 0))
    brent_102  = float(row_102.get("צבירה מסלול שכירות", 0))

    # ─── מסלול 5 — מינוף (צבירה + יתרת הלוואת בלון) ─────────────────────────
    blev_ret   = float(row_retire.get("צבירה מסלול מינוף", 0))
    blev_chk   = float(row_check.get("צבירה מסלול מינוף", 0))
    blev_102   = float(row_102.get("צבירה מסלול מינוף", 0))
    loan_bal_chk = float(row_check.get("הלוואת בלון — יתרת חוב", 0))
    loan_bal_ret = float(row_retire.get("הלוואת בלון — יתרת חוב", 0))

    # ─── תזרים מסלול שכירות ──────────────────────────────────────────────────
    df_full["rental_cashflow"] = df_full["תזרים נטו שכירות"]
    cf_retire = float(_row(df_full, retire_age)["rental_cashflow"])
    cf_check  = float(_row(df_full, check_age)["rental_cashflow"])

    df_after_retire = df_full[df_full["גיל"] >= retire_age]
    neg_rows = df_after_retire[df_after_retire["rental_cashflow"] < 0]
    flip_age = float(neg_rows.iloc[0]["גיל"]) if not neg_rows.empty else None

    # ─── נומינלים מהמנוע — הוצאות/הכנסות/נדל"ן/קצבה ────────────────────────
    exp_ret      = float(row_retire["הוצאה נומינלית"])
    exp_chk_nom  = float(row_check["הוצאה נומינלית"])
    inc_ret      = float(row_retire["הכנסה נומינלית"])
    inc_chk_nom  = float(row_check["הכנסה נומינלית"])
    pension_ret  = float(row_retire.get("הכנסה מקצבה מזערית", 0))
    pension_chk  = float(row_check.get("הכנסה מקצבה מזערית", 0))
    pension_asset_ret = float(row_retire.get("ערך קצבה נותר", 0))
    pension_asset_chk = float(row_check.get("ערך קצבה נותר", 0))
    prop_ret     = float(row_retire.get("שווי נדלן", 0))
    prop_chk     = float(row_check.get("שווי נדלן", 0))
    rental_prop_ret = float(row_retire.get("שווי נדלן מסלול 4", 0))
    rental_prop_chk = float(row_check.get("שווי נדלן מסלול 4", 0))
    tax_190_ret  = float(row_retire.get("מס ששולם 190", 0))
    tax_25_ret   = float(row_retire.get("מס ששולם 25", 0))
    tax_hyb_ret  = float(row_retire.get("מס ששולם היברידי", 0))
    # Pension monthly computed by engine = capital / adjusted_coeff
    pension_monthly_computed = (capital_for_pension / adj_coeff) if adj_coeff > 0 else 0

    # ─── משכנתה הפוכה ────────────────────────────────────────────────────────
    rm_activation_age_s  = None
    rm_equity_check_s    = None
    rm_interest_total_s  = None
    rm_debt_check_s      = None
    rm_annuity_monthly_s = None
    if rm_enabled_s and "משכנתה הפוכה — יתרת חוב" in df_full.columns:
        rm_rows = df_full[df_full["משכנתה הפוכה — יתרת חוב"] > 0]
        if not rm_rows.empty:
            rm_activation_age_s = float(rm_rows.iloc[0]["גיל"])
        rm_equity_check_s   = float(_row(df_full, check_age).get("משכנתה הפוכה — הון עצמי", 0.0))
        rm_debt_check_s     = float(_row(df_full, check_age).get("משכנתה הפוכה — יתרת חוב", 0.0))
        rm_interest_total_s = float(df_full["משכנתה הפוכה — ריבית חודשית"].sum())
        if "משכנתה הפוכה — משיכה חודשית" in df_full.columns:
            _rm_active = df_full[df_full["משכנתה הפוכה — משיכה חודשית"] > 0]
            if not _rm_active.empty:
                rm_annuity_monthly_s = float(_rm_active.iloc[0]["משכנתה הפוכה — משיכה חודשית"])

    # ─── בלוק טקסט משכנתה הפוכה לסיכום ─────────────────────────────────────
    if rm_enabled_s:
        _rm_act    = f"גיל {rm_activation_age_s:.1f}" if rm_activation_age_s else "לא הופעלה"
        _rm_eq     = f"{rm_equity_check_s:,.0f} ₪" if rm_equity_check_s is not None else "---"
        _rm_debt   = f"{rm_debt_check_s:,.0f} ₪" if rm_debt_check_s is not None else "---"
        _rm_int    = f"{rm_interest_total_s:,.0f} ₪" if rm_interest_total_s else "---"
        _rm_ann    = f"{rm_annuity_monthly_s:,.0f} ₪/חודש" if rm_annuity_monthly_s else "---"
        rm_summary_block = (
            f"  משכנתה הפוכה         : אוטומטית (ריבית {rm_annual_rate_s*100:.1f}%)\n"
            f"  גיל הפעלה (סימול.)   : {_rm_act}\n"
            f"  משיכה ראשונה (מנוע)  : {_rm_ann}\n"
            f"  יתרת חוב בגיל {check_age:.0f}    : {_rm_debt}\n"
            f"  הון עצמי בגיל {check_age:.0f}    : {_rm_eq}\n"
            f"  סהכ ריבית RM         : {_rm_int}"
        )
    else:
        rm_summary_block = "  (לא נדרשה משכנתה הפוכה — התיק כיסה את הגרעון)"

    # ─── משיכה חודשית נדרשת (כל מסלול, גיל בדיקה) ───────────────────────────
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
    st.caption("הדף שולף נתונים ישירות מהסליידרים ומהמנוע — אינו מחשב דבר בעצמו. נכללים רק המסלולים שנבחרו בסימולציה.")

    # ─── בונים את הדוח מרשימת מקטעים, וכוללים רק מסלולים שנבחרו ──────────────
    def _hdr(title):
        return f"━━━━━━━━━━  {title}  ━━━━━━━━━━"

    selected_txt = " · ".join(TRACK_TITLES[t] for t in sorted(visible)) or "(לא נבחר מסלול)"
    parts = []
    parts.append("=== סימולציית פרישה אקטוארית — דוח QA מהיר ===")
    parts.append(f"מסלולים שנבחרו להשוואה: {selected_txt}")

    parts.append(f"""{_hdr("זמנים")}
  גיל התחלה          : {start_age}
  גיל פרישה          : {retire_age}
  גיל בדיקה          : {check_age}""")

    parts.append(f"""{_hdr("הוצאות")}
  הוצאה חודשית בסיס  : {base_exp:,.0f} ₪
  אינפלציה שנתית     : {inflation*100:.1f}%
  תוספת אינפלציה 75–85 : {age_75_85_inc*100:.1f}%
  תוספת אינפלציה 85+  : {age_85_plus_inc*100:.1f}%
  מטפלת סיעודית (מ-85): {caregiver_cost:,.0f} ₪/חודש
  הוצאה חד-פעמית     : {one_time_exp:,.0f} ₪ (כל {one_time_freq:.0f} שנים)""")

    parts.append(f"""{_hdr("הכנסות")}
  הכנסה מעבודה       : {work_inc:,.0f} ₪/חודש (עד גיל {work_end_age:.1f})
  ביטוח לאומי        : {ni_base:,.0f} ₪/חודש (ערך בסיס)""")

    parts.append(f"""{_hdr('הון ונדל"ן')}
  נטו ממכירה         : {net_sale:,.0f} ₪
  חסכונות קיימים     : {existing_savings:,.0f} ₪
  עלות דירה חדשה     : {new_apartment_cost:,.0f} ₪
  עזרה לילדים        : {kids_help:,.0f} ₪
  קרן חירום          : {emergency_fund:,.0f} ₪
  הון פנוי למסלולים  : {remaining_gimel:,.0f} ₪
  עליית ערך נדל"ן    : {prop_appreciation*100:.1f}%/שנה""")

    # ─── בלוקי קלט לכל מסלול — רק אלו שנבחרו ─────────────────────────────────
    if 1 in visible:
        parts.append(f"""{_hdr("מסלול 1 — תיקון 190")}
  קצבה רצויה         : {desired_pension:,.0f} ₪/חודש
  תקופת אבטחה        : {securing_years:.0f} שנים
  מקדם בסיסי         : {base_coeff:.1f}
  מקדם משוקלל        : {adj_coeff:.1f}
  הון לרכישת קצבה    : {capital_for_pension:,.0f} ₪
  קצבה חודשית מחושבת : {pension_monthly_computed:,.0f} ₪  (הון÷מקדם)
  הון נטו במסלול 190 : {net_for_190:,.0f} ₪
  תשואה / דמי ניהול  : {yield_190*100:.1f}% / {fee_190*100:.2f}%""")

    if 2 in visible:
        parts.append(f"""{_hdr("מסלול 2 — 25% מס ריאלי")}
  הון במסלול         : {net_for_25:,.0f} ₪
  תשואה / דמי ניהול  : {yield_25*100:.1f}% / {fee_25*100:.2f}%""")

    if 3 in visible:
        parts.append(f"""{_hdr("מסלול 3 — היברידי")}
  הון במסלול         : {net_for_hybrid:,.0f} ₪
  תשואה / דמי ניהול  : {yield_hybrid*100:.1f}% / {fee_hybrid*100:.2f}%
  קצבה חודשית מחושבת : {pension_monthly_computed:,.0f} ₪  (זהה למסלול 1)""")

    if 4 in visible:
        parts.append(f"""{_hdr("מסלול 4 — שכירות")}
  הון נזיל           : {net_for_rental:,.0f} ₪
  שווי דירה מושכרת   : {rental_prop_value:,.0f} ₪  (עליית ערך: {rental_appreciation*100:.1f}%/שנה)
  שכ"ד גביה          : {rental_inc_monthly:,.0f} ₪/חודש (צמיחה: {rental_inc_growth*100:.1f}%/שנה)
  שכ"ד תשלום         : {rent_paid_monthly:,.0f} ₪/חודש (צמיחה: {rent_paid_growth*100:.1f}%/שנה)
  מס שכירות          : {rental_tax_rate*100:.1f}%
  תחזוקה — 10 שנים ראשונות: {maintenance_early_pct_s*100:.1f}% משכ"ד
  תחזוקה — מ-10 שנים+     : {maintenance_late_pct_s*100:.1f}% משכ"ד
  תזרים בפרישה       : {"+" if cf_retire >= 0 else ""}{cf_retire:,.0f} ₪/חודש
  תזרים בגיל {check_age:.0f}      : {"+" if cf_check >= 0 else ""}{cf_check:,.0f} ₪/חודש
  גיל היפוך תזרים    : {f"גיל {flip_age:.1f}" if flip_age else "נשאר חיובי לאורך כל הדרך"}
  ── משכנתה הפוכה ──
{rm_summary_block}""")

    if 5 in visible:
        parts.append(f"""{_hdr("מסלול 5 — מינוף")}
  סכום הלוואה (בלון) : {loan_amount_s:,.0f} ₪
  ריבית ההלוואה      : {loan_rate_s*100:.2f}%
  תשואת מסלול כללי   : {gen_return_lev_s*100:.1f}%
  מודל               : ללא מכירה כפויה, הריבית מצטברת ונפרעת מהעיזבון
  יתרת חוב בפרישה    : {loan_bal_ret:,.0f} ₪
  יתרת חוב בגיל {check_age:.0f}    : {loan_bal_chk:,.0f} ₪""")

    # ─── תוצאות תיק נזיל — נקודות מפתח (רק מסלולים שנבחרו) ───────────────────
    _keypts = {
        1: (b190_ret, b190_chk, b190_102),
        2: (b25_ret, b25_chk, b25_102),
        3: (bhyb_ret, bhyb_chk, bhyb_102),
        4: (brent_ret, brent_chk, brent_102),
        5: (blev_ret, blev_chk, blev_102),
    }
    _res_lines = [_hdr("תוצאות תיק נזיל — נקודות מפתח")]
    for t in sorted(visible):
        r, c, h = _keypts[t]
        _res_lines.append(
            f"  {TRACK_TITLES[t]:<20} | פרישה ({retire_age:.1f}): {r:>13,.0f} ₪  |  "
            f"גיל {check_age:.0f}: {c:>13,.0f} ₪  |  גיל 102: {h:>13,.0f} ₪")
    if 5 in visible:
        _res_lines.append(
            f"  * מסלול 5: הצבירה היא התיק המושקע. יתרת הלוואת הבלון "
            f"({loan_bal_chk:,.0f} ₪ בגיל {check_age:.0f}) מנוכה מהעיזבון.")
    parts.append("\n".join(_res_lines))

    # ─── תוצאות מנוע — אימות חישובים ─────────────────────────────────────────
    _eng = [_hdr("תוצאות מנוע — אימות חישובים"),
            f"  [גיל פרישה = {retire_age:.1f}]",
            f"  הוצאה נומינלית        : {exp_ret:,.0f} ₪/חודש",
            f'  הכנסה נומינלית (ב"ל)  : {inc_ret:,.0f} ₪/חודש']
    if {1, 3, 5} & visible:
        _eng.append(f"  קצבה חודשית (מנוע)    : {pension_ret:,.0f} ₪/חודש")
        _eng.append(f"  ערך קצבה נותר         : {pension_asset_ret:,.0f} ₪")
    if {1, 2, 3, 5} & visible:
        _eng.append(f'  שווי נדל"ן (מגורים)   : {prop_ret:,.0f} ₪')
    if 4 in visible:
        _eng.append(f'  שווי נדל"ן (מושכרת)   : {rental_prop_ret:,.0f} ₪')
    if 1 in visible:
        _eng.append(f"  מס ששולם — מסלול 190  : {tax_190_ret:,.0f} ₪")
    if 2 in visible:
        _eng.append(f"  מס ששולם — מסלול 25   : {tax_25_ret:,.0f} ₪")
    if 3 in visible:
        _eng.append(f"  מס ששולם — היברידי     : {tax_hyb_ret:,.0f} ₪")
    parts.append("\n".join(_eng))

    # ─── משיכה חודשית נדרשת — גיל בדיקה (רק מסלולים שנבחרו) ──────────────────
    _wd = {
        1: (nn_190_chk, "הוצאה פחות ב\"ל + קצבה"),
        2: (nn_25_chk, "הוצאה פחות ב\"ל בלבד"),
        3: (nn_hyb_chk, "הוצאה פחות ב\"ל + קצבה"),
        4: (nn_rent_chk, "גירעון תזרים שכ\"ד" if nn_rent_chk > 0 else "תזרים עצמאי"),
        5: (nn_190_chk, "גירעון זהה למסלול 1"),
    }
    _wd_lines = [_hdr(f"משיכה חודשית נדרשת — גיל {check_age:.0f}")]
    for t in sorted(visible):
        val, note = _wd[t]
        _wd_lines.append(f"  {TRACK_TITLES[t]:<20}: {val:>10,.0f} ₪/חודש  ({note})")
    parts.append("\n".join(_wd_lines))

    # ─── תוצאות והשוואה — נשלף מכרטיס ההשוואה (qa_report מאחסן ב-session_state) ──
    exec_sum = st.session_state.get("qa_exec_summary")
    if exec_sum and exec_sum.get("tracks"):
        et = exec_sum["tracks"]
        _res = [_hdr(f"תוצאות והשוואה — חציון מונטה קרלו, גיל {check_age:.0f}")]
        _res.append("  (זה מה שמופיע בכרטיס ההשוואה וממנו נגזר הדירוג)")
        for t in sorted(visible):
            d = et.get(t)
            if not d:
                continue
            _rank = d.get("rank")
            _rank_txt = f"מקום {_rank}" if _rank else ""
            _ero = d.get("erosion_age")
            _ero_txt = "צומח תמיד" if _ero is None else f"גיל {_ero:.0f}"
            _lasts = d.get("lasts_age", 120)
            _lasts_txt = "לכל החיים" if _lasts >= 105 else f"גיל {_lasts:.0f}"
            _res.append(
                f"\n  {TRACK_TITLES[t]}  [{_rank_txt} · {d.get('health','')}]\n"
                f"    תיק (חציון)      : {d['fin_med']:>13,.0f} ₪\n"
                f"    נדל\"ן (חציון)    : {d['prop_med']:>13,.0f} ₪\n"
                f"    הלוואות          : {(-d['liab']):>13,.0f} ₪\n"
                f"    מס שבח עתידי     : {(-d['tax']):>13,.0f} ₪\n"
                f"    עזרה לילדים      : {d['kids']:>13,.0f} ₪\n"
                f"    ── סך נכסים נטו  : {d['total']:>13,.0f} ₪\n"
                f"    מחזיק עד         : {_lasts_txt}  |  תחילת שחיקה: {_ero_txt}  |  "
                f"משיכה חודשית: {d['draw_month']:,.0f} ₪")
        lev = exec_sum.get("leverage")
        if lev and 5 in visible:
            _res.append(
                f"\n  כדאיות מינוף (מסלול 5): {lev['verdict']}. מול בלי מינוף — "
                f"תוספת בחציון {'+' if lev['up50']>=0 else ''}{lev['up50']:,.0f} ₪, "
                f"תרחיש גרוע {'+' if lev['up10']>=0 else ''}{lev['up10']:,.0f} ₪ "
                f"(עיזבון חציון {lev['cur_p50']:,.0f}, גרוע {lev['cur_p10']:,.0f}).")
        parts.append("\n".join(_res))
    else:
        parts.append("━━━━━━━━━━  תוצאות והשוואה  ━━━━━━━━━━\n"
                     "  (פתח את לשונית 'השוואת מסלולים והמלצה' פעם אחת בריצה זו כדי "
                     "שהתוצאות המלאות ייכללו כאן.)")

    copy_text = "\n\n".join(parts) + "\n" + "=" * 60

    st.code(copy_text, language="text")

    # ─── טבלת תוצאות ויזואלית (רק מסלולים שנבחרו) ───────────────────────────
    st.write("---")
    st.markdown("**🔍 תיק נזיל — נקודות מפתח:**")
    _summary_cols = {
        1: ("מסלול 1 — 190",       [format_shekel(b190_ret),  format_shekel(b190_chk),  format_shekel(b190_102)]),
        2: ("מסלול 2 — 25% ריאלי", [format_shekel(b25_ret),   format_shekel(b25_chk),   format_shekel(b25_102)]),
        3: ("מסלול 3 — היברידי",   [format_shekel(bhyb_ret),  format_shekel(bhyb_chk),  format_shekel(bhyb_102)]),
        4: ("מסלול 4 — שכירות",    [format_shekel(brent_ret), format_shekel(brent_chk), format_shekel(brent_102)]),
        5: ("מסלול 5 — מינוף",     [format_shekel(blev_ret),  format_shekel(blev_chk),  format_shekel(blev_102)]),
    }
    df_summary = pd.DataFrame({
        "נקודת זמן": [
            f"גיל פרישה ({retire_age:.1f})",
            f"גיל נבדק ({check_age:.1f})",
            "גיל 102",
        ],
        **{_summary_cols[t][0]: _summary_cols[t][1] for t in sorted(visible)},
    })
    st.table(df_summary.set_index("נקודת זמן"))
    if 5 in visible:
        st.caption(f"מסלול 5 מציג את התיק המושקע. יתרת הלוואת הבלון בגיל {check_age:.0f} היא "
                   f"{format_shekel(loan_bal_chk)} ומנוכה מהעיזבון.")

    st.markdown(f"**💸 משיכה חודשית נדרשת — גיל {check_age:.0f}:**")
    _wd_rows = {
        1: ("מסלול 1 — 190 + קצבה", format_shekel(nn_190_chk), "הוצאה פחות ב\"ל + קצבה"),
        2: ("מסלול 2 — 25% ריאלי",  format_shekel(nn_25_chk),  "הוצאה פחות ב\"ל בלבד"),
        3: ("מסלול 3 — היברידי",    format_shekel(nn_hyb_chk), "הוצאה פחות ב\"ל + קצבה"),
        4: ("מסלול 4 — שכירות",
            format_shekel(nn_rent_chk) if nn_rent_chk > 0 else "✅ תזרים עצמאי",
            "גירעון תזרים שכ\"ד" if nn_rent_chk > 0 else f"תזרים חיובי +{format_shekel(int(-cf_check))}"),
        5: ("מסלול 5 — מינוף", format_shekel(nn_190_chk), "גירעון זהה למסלול 1"),
    }
    _sel_wd = [t for t in sorted(visible)]
    df_withdrawal = pd.DataFrame({
        "מסלול":        [_wd_rows[t][0] for t in _sel_wd],
        "משיכה חודשית": [_wd_rows[t][1] for t in _sel_wd],
        "הערה":         [_wd_rows[t][2] for t in _sel_wd],
    })
    st.table(df_withdrawal.set_index("מסלול"))

    # ─── שורה תחתונה — סך נכסים נטו (חציון מונטה קרלו) מכרטיס ההשוואה ─────────
    if exec_sum and exec_sum.get("tracks"):
        et = exec_sum["tracks"]
        st.markdown(f"**🏁 סך נכסים נטו — חציון מונטה קרלו, גיל {check_age:.0f} (מכרטיס ההשוואה):**")
        _rows = []
        for t in sorted(visible):
            d = et.get(t)
            if not d:
                continue
            _rank = d.get("rank")
            _lasts = d.get("lasts_age", 120)
            _rows.append({
                "מסלול": TRACK_TITLES[t],
                "מקום": (f"{_rank}" if _rank else "—"),
                "תיק (חציון)": format_shekel(d["fin_med"]),
                'נדל"ן (חציון)': format_shekel(d["prop_med"]),
                "הלוואות/מס": format_shekel(-(d["liab"] + d["tax"])),
                "עזרה לילדים": format_shekel(d["kids"]),
                "סך נכסים נטו": format_shekel(d["total"]),
                "מחזיק עד": ("לכל החיים" if _lasts >= 105 else f"גיל {_lasts:.0f}"),
            })
        st.table(pd.DataFrame(_rows).set_index("מסלול"))
        lev = exec_sum.get("leverage")
        if lev and 5 in visible:
            st.caption(
                f"כדאיות מינוף (מסלול 5): {lev['verdict']}. תוספת בחציון "
                f"{format_shekel(lev['up50'])} מול פגיעה של {format_shekel(lev['up10'])} "
                f"בתרחיש הגרוע, לעומת בלי מינוף.")
