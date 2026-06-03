import streamlit as st
from inputs.ui_components import compact_number_input, show_net_summary, format_shekel, COLOR_GREEN, COLOR_RED, COLOR_BLUE

def render_rental_inputs(wealth_data, check_age=90.0, start_age=67.0):
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

    st.markdown("**הוצאות תחזוקה — % מדמי השכירות (מגיל ההשכרה, גיל 66)**")
    maintenance_early_pct = compact_number_input(
        "תחזוקה — 10 שנים ראשונות (% מהשכירות)",
        value=7.0, min_value=0.0, max_value=30.0, step=0.5, unit="%", color=COLOR_RED
    )
    st.caption("דירה חדשה מקבלן — תיקונים שוטפים, ועד בית, ביטוח. נהוג 5–8% בשנים הראשונות.")
    maintenance_late_pct = compact_number_input(
        "תחזוקה — מ-10 שנים ואילך (% מהשכירות)",
        value=12.0, min_value=0.0, max_value=30.0, step=0.5, unit="%", color=COLOR_RED
    )
    st.caption("לאחר עשור — תיקונים גדולים, שיפוצים, בלאי. נהוג 10–15% מהשכירות.")

    st.divider()
    st.markdown("##### 🏦 משכנתה הפוכה — קצבה חודשית קבועה מהנכס")
    st.caption("הבנק מחשב קצבה חודשית קבועה לכל החיים. החיסכון נשאר נזיל כקרן חירום.")

    # --- Danger table: always visible, uses no-RM simulation ---
    _sim_no_rm = st.session_state.get("sim_results_no_rm")
    if _sim_no_rm and "df_full" in _sim_no_rm:
        _df_hint = _sim_no_rm["df_full"]
        _last_inputs = st.session_state.get("last_inputs", {})
        _retire_age = float(_last_inputs.get("timeline", {}).get("retirement_age", 67))
        _df_post = _df_hint[_df_hint["גיל"] >= _retire_age]

        def _find_threshold_age(df, threshold):
            rows = df[df["צבירה מסלול שכירות"] <= threshold]
            return float(rows.iloc[0]["גיל"]) if not rows.empty else None

        def _cum_deficit_from(df, from_age):
            df_neg = df[(df["תזרים נטו שכירות"] < 0) & (df["גיל"] >= from_age) & (df["גיל"] <= check_age)]
            return float(df_neg["תזרים נטו שכירות"].abs().sum()) if not df_neg.empty else 0.0

        _thresholds = [("₪80,000", 80_000), ("₪40,000", 40_000), ("₪20,000", 20_000)]
        _rows_data = []
        for _label, _thresh in _thresholds:
            _age = _find_threshold_age(_df_post, _thresh)
            if _age is not None:
                _deficit = _cum_deficit_from(_df_hint, _age)
                _rows_data.append((_label, f"גיל {_age:.0f}", f"₪{_deficit:,.0f}"))
            else:
                _rows_data.append((_label, f"לא מגיע עד גיל {check_age:.0f}", "—"))

        _table_rows = "".join(
            f"<tr><td style='padding:4px 10px;text-align:right;'>{r[0]}</td>"
            f"<td style='padding:4px 10px;text-align:center;'>{r[1]}</td>"
            f"<td style='padding:4px 10px;text-align:left;font-weight:700;'>{r[2]}</td></tr>"
            for r in _rows_data
        )
        import json as _json
        _stale = True
        try:
            _last = st.session_state.get("last_inputs", {})
            _last_exp = _last.get("expenses", {})
            _last_rental = _last.get("rental", {})
            _last_timeline = _last.get("timeline", {})
            # Build a fingerprint of the fields that affect the danger table
            _last_fp = _json.dumps({
                "base_expense":   _last_exp.get("base_monthly_expense"),
                "caregiver":      _last_exp.get("caregiver_cost"),
                "one_time":       _last_exp.get("one_time_expense"),
                "one_time_freq":  _last_exp.get("one_time_frequency"),
                "inflation":      _last_exp.get("expected_inflation"),
                "rent_in":        _last_rental.get("rental_income_monthly"),
                "rent_out":       _last_rental.get("rent_paid_monthly"),
                "retire_age":     _last_timeline.get("retirement_age"),
            }, sort_keys=True, default=str)
            # Current widget values (saved by patched_number_input in app.py)
            def _w(label):
                return st.session_state.get(f"saved_num_{label}")
            _curr_fp = _json.dumps({
                "base_expense":   _w("הוצאות חודשיות נוכחיות (₪)"),
                "caregiver":      _w("תוספת עלות מטפלת סיעודית מגיל 85 (₪)"),
                "one_time":       _w("גובה הוצאה חד-פעמית ממוצעת (₪)"),
                "one_time_freq":  _w("תדירות ההוצאה החד-פעמית (כל כמה שנים)"),
                "inflation":      _w("אינפלציה שנתית צפויה (%)"),
                "rent_in":        _w("שכר דירה חודשי — גביה (₪)"),
                "rent_out":       _w("שכר דירה חודשי — תשלום (₪)"),
                "retire_age":     _w("גיל פרישה (הפסקת עבודה)"),
            }, sort_keys=True, default=str)
            _stale = (_last_fp != _curr_fp)
        except Exception:
            _stale = True

        _spinner_css = (
            "<style>"
            "@keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}"
            "@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.35}}"
            ".danger-spinner{display:inline-block;animation:spin 1.2s linear infinite;margin-left:4px;}"
            ".danger-stale{display:inline-flex;align-items:center;gap:4px;color:#b07800;font-size:0.82em;"
            "background:#fff0b3;border-radius:4px;padding:2px 7px;margin-bottom:5px;}"
            "</style>"
        )
        _stale_badge = (
            f"<div class='danger-stale'>"
            f"<span class='danger-spinner'>⟳</span>"
            f" ממתין לעדכון — לחץ <b style='margin:0 3px;'>▶️ עדכן סימולציה</b> לרענון"
            f"</div>"
        ) if _stale else (
            "<div style='color:#1a7a3a;font-size:0.82em;margin-bottom:5px;'>✅ נתונים מעודכנים</div>"
        )

        st.markdown(
            f"{_spinner_css}"
            f"<div style='background:#fff8e1;border:1px solid #f0c040;border-radius:8px;"
            f"padding:10px 14px;margin-bottom:8px;direction:rtl;font-family:sans-serif;font-size:0.85em;'>"
            f"<b>🔍 ניתוח ריקון חיסכון (ללא משכנתה הפוכה)</b>"
            f"{_stale_badge}"
            f"<table style='width:100%;border-collapse:collapse;margin-top:6px;'>"
            f"<thead><tr style='border-bottom:1px solid #e0c000;'>"
            f"<th style='text-align:right;padding:3px 10px;'>סף חיסכון</th>"
            f"<th style='text-align:center;padding:3px 10px;'>גיל הגעה</th>"
            f"<th style='text-align:left;padding:3px 10px;'>גרעון לכיסוי (עד {check_age:.0f})</th>"
            f"</tr></thead><tbody>{_table_rows}</tbody></table>"
            f"<div style='margin-top:6px;color:#888;font-size:0.9em;'>"
            f"= סך הגרעון החודשי המצטבר מגיל ההגעה ועד גיל {check_age:.0f}</div>"
            f"</div>",
            unsafe_allow_html=True
        )
    else:
        st.caption("⏳ הרץ סימולציה לקבלת ניתוח ריקון חיסכון.")

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

        # Manual horizon: the age up to which the annuity is spread.
        rm_life_expectancy_age = compact_number_input(
            "עד איזה גיל לחלק את הקצבה",
            value=90, min_value=70, max_value=105, step=1, unit="גיל", color=COLOR_BLUE
        )
        st.caption("ככל שגבוה יותר — קצבה חודשית נמוכה יותר (פריסה על יותר שנים), אך תקבולים לאורך זמן רב יותר.")

        rm_loan_amount_ils = compact_number_input(
            "סך תקבולים רצויים מהמשכנתה (₪)",
            value=0, min_value=0, step=50000, unit="₪", color=COLOR_BLUE
        )
        st.caption("הסכום שתרצה לקבל בסה״כ לאורך כל התקופה (לפני עמלת פתיחה). החוב לעיזבון יהיה גבוה יותר בשל הריבית המצטברת.")
        if rm_loan_amount_ils > 0 and current_property_value > 0:
            ltv_pct = rm_loan_amount_ils / current_property_value * 100
            ltv_icon = "🟢" if ltv_pct <= 55 else ("🟡" if ltv_pct <= 65 else "🔴")
            st.caption(f"{ltv_icon} LTV: {ltv_pct:.1f}% מהנכס | בישראל: ~45–55% לגיל 65–70, ~65% לגיל 75+")

        rm_origination_fee_pct = compact_number_input(
            "עמלת פתיחת תיק — חד פעמית (%)",
            value=2.0, min_value=0.0, max_value=5.0, step=0.5, unit="%", color=COLOR_RED
        )

        # Live annuity preview and loan summary
        if rm_loan_amount_ils > 0 and rm_life_expectancy_age > rm_start_age:
            r_m = (1 + rm_annual_rate_pct / 100) ** (1 / 12) - 1
            n_m = (rm_life_expectancy_age - rm_start_age) * 12
            orig_fee_ils = rm_loan_amount_ils * rm_origination_fee_pct / 100
            net_loan = rm_loan_amount_ils - orig_fee_ils
            annuity_preview = net_loan / max(1, n_m)
            total_received = net_loan  # by design: total cash-in-hand == net principal
            # FV of drawn balance: debt = M*(1+r)*[(1+r)^n - 1]/r  (annuity-due accumulation)
            if r_m > 0 and n_m > 0:
                debt_at_end = annuity_preview * (1 + r_m) * ((1 + r_m) ** n_m - 1) / r_m
            else:
                debt_at_end = net_loan
            interest_cost = debt_at_end - net_loan
            years_span = rm_life_expectancy_age - rm_start_age

            st.markdown(
                f"<div style='background:#f0f4ff;border-radius:8px;padding:12px 14px;"
                f"direction:rtl;font-family:sans-serif;font-size:0.88em;margin-top:8px;'>"
                f"<b style='font-size:1.05em;'>📊 קצבה חודשית צפויה: ₪{annuity_preview:,.0f}</b>"
                f"<div style='color:#555;font-size:0.92em;margin-top:3px;'>"
                f"תקופת תשלום: גיל {rm_start_age:.0f} ← גיל {rm_life_expectancy_age:.0f} &nbsp;({years_span:.0f} שנים)</div>"
                f"<hr style='margin:8px 0;border:none;border-top:1px solid #ccd;'/>"
                f"<table style='width:100%;border-collapse:collapse;'>"
                f"<tr><td>סך תקבולים — כסף שנכנס לך ({years_span:.0f} שנים)</td>"
                f"<td style='text-align:left;color:#1a7a3a;font-weight:700;'>₪{total_received:,.0f}</td></tr>"
                f"<tr><td>עמלת פתיחת תיק ({rm_origination_fee_pct:.1f}%)</td>"
                f"<td style='text-align:left;color:#c0392b;'>₪{orig_fee_ils:,.0f}</td></tr>"
                f"<tr><td>ריבית מצטברת על החוב</td>"
                f"<td style='text-align:left;color:#c0392b;'>₪{interest_cost:,.0f}</td></tr>"
                f"<tr style='border-top:1px solid #ccd;'><td><b>חוב לעיזבון בגיל {rm_life_expectancy_age:.0f}</b></td>"
                f"<td style='text-align:left;color:#c0392b;font-weight:700;'>₪{debt_at_end:,.0f}</td></tr>"
                f"</table></div>",
                unsafe_allow_html=True
            )
    else:
        rm_annual_rate_pct = 5.5
        rm_start_age = 72
        rm_life_expectancy_age = float(check_age)
        rm_loan_amount_ils = 0
        rm_origination_fee_pct = 2.0

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
        "rm_enabled": enable_rm,
        "rm_annual_rate": rm_annual_rate_pct / 100,
        "rm_start_age": rm_start_age,
        "rm_life_expectancy_age": rm_life_expectancy_age,
        "rm_loan_amount_ils": rm_loan_amount_ils,
        "rm_origination_fee": rm_origination_fee_pct / 100,
    }
