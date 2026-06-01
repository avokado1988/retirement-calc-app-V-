import streamlit as st
from inputs.ui_components import compact_number_input, show_net_summary, format_shekel, COLOR_GREEN, COLOR_RED, COLOR_BLUE

def render_rental_inputs(wealth_data, check_age=90.0):
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
    enable_rm = st.checkbox("הפעל משכנתה הפוכה", value=False, key="enable_rm")

    if enable_rm:
        # Deficit hint: find when savings near depletion (≤100K), then sum deficit from there to check_age
        sim_res = st.session_state.get("sim_results")
        if sim_res and "df_full" in sim_res:
            df_hint = sim_res["df_full"]
            last_inputs = st.session_state.get("last_inputs", {})
            retire_age_hint = float(last_inputs.get("timeline", {}).get("retirement_age", 67))

            # Find age when savings drop to ≤100K (after retirement)
            DEPLETION_THRESHOLD = 100_000
            df_after_retire = df_hint[df_hint["גיל"] >= retire_age_hint]
            depleting_rows = df_after_retire[df_after_retire["צבירה מסלול שכירות"] <= DEPLETION_THRESHOLD]

            if not depleting_rows.empty:
                rm_trigger_age = float(depleting_rows.iloc[0]["גיל"])
                # Cumulative deficit from that age to check_age — deflated to today's money
                df_neg = df_hint[
                    (df_hint["תזרים נטו שכירות"] < 0) &
                    (df_hint["גיל"] >= rm_trigger_age) &
                    (df_hint["גיל"] <= check_age)
                ]
                if not df_neg.empty:
                    # Deflate by inflation_factor → real values in today's ₪
                    inf_factors = df_neg["inflation_factor"].replace(0, 1)
                    real_def = (df_neg["תזרים נטו שכירות"] / inf_factors).abs()
                    cum_def = float(real_def.sum())
                    min_def = float(real_def.min())
                    max_def = float(real_def.max())
                    st.info(
                        f"💡 **החסכונות מגיעים ל-₪100K בגיל {rm_trigger_age:.0f}** — "
                        f"זה הגיל הרלוונטי להפעיל משכנתה הפוכה.\n\n"
                        f"גרעון מצטבר מגיל {rm_trigger_age:.0f} עד גיל {check_age:.0f} "
                        f"**במחירי היום**: **₪{cum_def:,.0f}** | "
                        f"גרעון חודשי טיפוסי: **₪{min_def:,.0f} – ₪{max_def:,.0f}**"
                    )
                else:
                    st.info(
                        f"💡 **החסכונות מגיעים ל-₪100K בגיל {rm_trigger_age:.0f}** — "
                        f"אין גרעון תזרים שלילי מגיל זה עד גיל {check_age:.0f}."
                    )
            else:
                st.success(f"✅ החסכונות לא מתקרבים לאפס עד גיל {check_age:.0f} — משכנתה הפוכה אינה הכרחית.")

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
            value=int(check_age), min_value=70, max_value=105, step=1, unit="גיל", color=COLOR_BLUE
        )
        st.caption(f"ברירת מחדל = גיל הבדיקה ({check_age:.0f}). ככל שגבוה יותר — קצבה נמוכה יותר, הבנק לוקח יותר סיכון.")

        rm_loan_amount_ils = compact_number_input(
            "סכום ההלוואה הרצוי (₪)",
            value=0, min_value=0, step=50000, unit="₪", color=COLOR_BLUE
        )
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
            net_loan = rm_loan_amount_ils * (1 - rm_origination_fee_pct / 100)
            if r_m > 0 and n_m > 0:
                annuity_preview = net_loan * r_m / ((1 + r_m) ** n_m - 1)
            else:
                annuity_preview = net_loan / max(1, n_m)
            total_received = annuity_preview * n_m
            interest_cost = rm_loan_amount_ils - total_received
            orig_fee_ils = rm_loan_amount_ils * rm_origination_fee_pct / 100
            years_span = rm_life_expectancy_age - rm_start_age

            st.markdown(
                f"<div style='background:#f0f4ff;border-radius:8px;padding:12px 14px;"
                f"direction:rtl;font-family:sans-serif;font-size:0.88em;margin-top:8px;'>"
                f"<b style='font-size:1.05em;'>📊 קצבה חודשית צפויה: ₪{annuity_preview:,.0f}</b>"
                f"<hr style='margin:8px 0;border:none;border-top:1px solid #ccd;'/>"
                f"<table style='width:100%;border-collapse:collapse;'>"
                f"<tr><td>קרן — תביעת הבנק מהעיזבון</td>"
                f"<td style='text-align:left;font-weight:700;'>₪{rm_loan_amount_ils:,.0f}</td></tr>"
                f"<tr><td>עמלת פתיחת תיק ({rm_origination_fee_pct:.1f}%)</td>"
                f"<td style='text-align:left;color:#c0392b;'>₪{orig_fee_ils:,.0f}</td></tr>"
                f"<tr><td>סך תקבולים ({years_span:.0f} שנים)</td>"
                f"<td style='text-align:left;color:#1a7a3a;font-weight:700;'>₪{total_received:,.0f}</td></tr>"
                f"<tr style='border-top:1px solid #ccd;'><td><b>ריבית מצטברת</b></td>"
                f"<td style='text-align:left;color:#c0392b;font-weight:700;'>₪{interest_cost:,.0f}</td></tr>"
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
