import pandas as pd
import numpy as np

def run_simulation(user_inputs):
    timeline = user_inputs.get("timeline", {})
    wealth = user_inputs.get("wealth", {})
    expenses = user_inputs.get("expenses", {})
    amendment_190 = user_inputs.get("amendment_190", {})
    real_tax_25 = user_inputs.get("real_tax_25", {})
    rental = user_inputs.get("rental", {})

    start_age = float(timeline.get("start_age", 65.5))
    retirement_age = float(timeline.get("retirement_age", 67.0))
    check_age = float(timeline.get("check_age", 87.0))

    annual_inflation_base = float(expenses.get("expected_inflation", 0.023))

    # Monthly net returns — all 4 tracks
    r_monthly_190 = (1 + (float(amendment_190.get("annual_return_190", 0.05)) - float(amendment_190.get("management_fee_190", 0.006)))) ** (1/12) - 1
    r_monthly_25 = (1 + (float(real_tax_25.get("annual_return_25", 0.05)) - float(real_tax_25.get("management_fee_25", 0.006)))) ** (1/12) - 1
    r_monthly_hybrid = (1 + (float(real_tax_25.get("annual_return_hybrid", 0.05)) - float(real_tax_25.get("management_fee_hybrid", 0.006)))) ** (1/12) - 1
    r_monthly_rental = r_monthly_25  # track 4 uses same return as track 2

    # Initial balances
    balance_190 = float(amendment_190.get("net_for_190", 0))
    basis_190 = balance_190
    balance_25 = float(real_tax_25.get("net_for_real_pathway", 0))
    basis_25 = balance_25
    balance_hybrid = float(real_tax_25.get("net_for_hybrid", 0))
    basis_hybrid = balance_hybrid
    balance_rental = float(rental.get("net_for_rental", 0))
    basis_rental = balance_rental

    baseline_capital = balance_25 if balance_25 > 0 else 1.0

    # Base parameters
    base_monthly_expense = float(expenses.get("current_expenses", 11000))
    work_income_static = float(expenses.get("work_income", 0))
    work_end_age = float(expenses.get("work_end_age", retirement_age))
    ni_base = float(wealth.get("national_insurance", 2500))
    pension_base = float(amendment_190.get("desired_pension", 5000))
    caregiver_cost_base = float(expenses.get("caregiver_cost", 0))
    capital_for_pension = float(amendment_190.get("capital_for_pension", 0))
    securing_years = float(amendment_190.get("securing_years", 20))
    securing_months_total = securing_years * 12

    # Property
    property_value = float(wealth.get("new_apartment_cost", 5800000))
    property_rental_value = float(wealth.get("new_apartment_cost", 5800000))
    prop_appreciation_monthly = (1 + float(wealth.get("property_appreciation", 0.023))) ** (1/12) - 1

    # Track 4 rental parameters
    rental_income_base = float(rental.get("rental_income_monthly", 0))
    rent_paid_base = float(rental.get("rent_paid_monthly", 0))
    rental_income_growth_monthly = (1 + float(rental.get("rental_income_growth_rate", 0.03))) ** (1/12) - 1
    rent_paid_growth_monthly = (1 + float(rental.get("rent_paid_growth_rate", 0.03))) ** (1/12) - 1
    rental_tax_rate = float(rental.get("rental_tax_rate", 0.10))

    history = []
    inflation_factor = 1.0
    retirement_inflation_factor = 1.0
    rental_income_factor = 1.0
    rent_paid_factor = 1.0
    total_months = int((105 - start_age) * 12) + 1

    for m in range(total_months):
        current_age = start_age + (m / 12.0)

        # --- Inflation ---
        current_ann_inf = annual_inflation_base
        if current_age >= 85.0: current_ann_inf += float(expenses.get("age_85_plus_increase", 0.015))
        elif current_age >= 75.0: current_ann_inf += float(expenses.get("age_75_85_increase", 0.005))
        i_monthly = (1 + current_ann_inf) ** (1/12) - 1

        if m > 0:
            inflation_factor *= (1 + i_monthly)
            rental_income_factor *= (1 + rental_income_growth_monthly)
            rent_paid_factor *= (1 + rent_paid_growth_monthly)

        # Pension inflation starts only after retirement month
        if current_age > retirement_age:
            retirement_inflation_factor *= (1 + i_monthly)

        # --- Expenses ---
        curr_base_exp = base_monthly_expense
        if current_age >= 85.0: curr_base_exp += caregiver_cost_base
        freq = int(expenses.get("one_time_frequency", 8) * 12)
        if freq > 0 and m > 0 and m % freq == 0:
            curr_base_exp += float(expenses.get("one_time_expense", 80000))
        nominal_expense = curr_base_exp * inflation_factor

        # --- Income ---
        curr_work_inc = work_income_static if current_age < work_end_age else 0.0
        # NI is indexed via inflation_factor from start_age, but paid only from retirement_age
        ni_indexed = ni_base * inflation_factor if current_age >= retirement_age else 0.0
        p_indexed = pension_base * retirement_inflation_factor if current_age >= retirement_age else 0.0
        base_income = curr_work_inc + ni_indexed

        # --- Track 4 rental cash flows ---
        rental_income_gross = rental_income_base * rental_income_factor
        net_rental_income = rental_income_gross * (1 - rental_tax_rate)
        rent_paid_indexed = rent_paid_base * rent_paid_factor

        # --- Shortfalls ---
        net_needed_190 = max(0.0, nominal_expense - (base_income + p_indexed))
        net_needed_25 = max(0.0, nominal_expense - base_income)
        net_needed_hybrid = max(0.0, nominal_expense - (base_income + p_indexed))

        # Block withdrawals before retirement for tracks 1-3
        if current_age < retirement_age:
            net_needed_190 = 0.0
            net_needed_25 = 0.0
            net_needed_hybrid = 0.0

        # Track 4: no pre-retirement block — rental covers from day 1
        total_out_rental = nominal_expense + rent_paid_indexed
        total_in_rental = base_income + net_rental_income
        net_needed_rental = max(0.0, total_out_rental - total_in_rental)

        # --- Pension asset value (tracks 1 and 3 only) ---
        if current_age < retirement_age:
            pension_asset_value = capital_for_pension
        else:
            months_since_retire = (current_age - retirement_age) * 12
            guarantee_remaining = max(0.0, securing_months_total - months_since_retire)
            pension_asset_value = guarantee_remaining * p_indexed

        # --- Track 1: Withdrawal (190 method, 15% nominal) ---
        tax_190 = 0.0
        if net_needed_190 > 0 and balance_190 > 0:
            pr = max(0.0, (balance_190 - basis_190) / balance_190)
            gross = net_needed_190 / (1 - (pr * 0.15))
            pull = min(gross, balance_190)
            tax_190 = pull * pr * 0.15
            basis_190 *= (1 - (pull / balance_190))
            balance_190 -= pull

        # --- Track 2: Withdrawal (25% real) ---
        tax_25 = 0.0
        if net_needed_25 > 0 and balance_25 > 0:
            rpr = max(0.0, (balance_25 - basis_25) / balance_25)
            gross25 = net_needed_25 / (1 - (rpr * 0.25))
            pull25 = min(gross25, balance_25)
            tax_25 = pull25 * rpr * 0.25
            basis_25 *= (1 - (pull25 / balance_25))
            balance_25 -= pull25
        if m > 0: basis_25 *= (1 + i_monthly)

        # --- Track 3: Withdrawal (25% real, hybrid) ---
        tax_hybrid = 0.0
        if net_needed_hybrid > 0 and balance_hybrid > 0:
            rpr_h = max(0.0, (balance_hybrid - basis_hybrid) / balance_hybrid)
            gross_h = net_needed_hybrid / (1 - (rpr_h * 0.25))
            pull_h = min(gross_h, balance_hybrid)
            tax_hybrid = pull_h * rpr_h * 0.25
            basis_hybrid *= (1 - (pull_h / balance_hybrid))
            balance_hybrid -= pull_h
        if m > 0: basis_hybrid *= (1 + i_monthly)

        # --- Track 4: Withdrawal (25% real, rental) ---
        tax_rental = 0.0
        if net_needed_rental > 0 and balance_rental > 0:
            rpr_r = max(0.0, (balance_rental - basis_rental) / balance_rental)
            gross_r = net_needed_rental / (1 - (rpr_r * 0.25))
            pull_r = min(gross_r, balance_rental)
            tax_rental = pull_r * rpr_r * 0.25
            basis_rental *= (1 - (pull_r / balance_rental))
            balance_rental -= pull_r
        if m > 0: basis_rental *= (1 + i_monthly)

        # --- Apply returns (after withdrawals, before next month) ---
        if balance_190 > 0: balance_190 *= (1 + r_monthly_190)
        if balance_25 > 0: balance_25 *= (1 + r_monthly_25)
        if balance_hybrid > 0: balance_hybrid *= (1 + r_monthly_hybrid)
        if balance_rental > 0: balance_rental *= (1 + r_monthly_rental)
        property_value *= (1 + prop_appreciation_monthly)
        property_rental_value *= (1 + prop_appreciation_monthly)

        # --- Inheritance values (liquid + pension guarantee asset) ---
        inheritance_190 = balance_190 + pension_asset_value
        inheritance_hybrid = balance_hybrid + pension_asset_value

        history.append({
            "גיל": current_age,
            "חודש": m,
            "הוצאה נומינלית": nominal_expense,
            "הכנסה נומינלית": base_income,
            "הכנסה מקצבה מזערית": p_indexed,
            "צבירה תיקון 190": balance_190,
            "צבירה מסלול ריאלי": balance_25,
            "צבירה מסלול היברידי": balance_hybrid,
            "צבירה מסלול שכירות": balance_rental,
            "מס ששולם 190": tax_190,
            "מס ששולם 25": tax_25,
            "מס ששולם היברידי": tax_hybrid,
            "מס ששולם שכירות": tax_rental,
            "שווי נדלן": property_value,
            "שווי נדלן מסלול 4": property_rental_value,
            "ערך קצבה נותר": pension_asset_value,
            "שווי ירושה 190": inheritance_190,
            "שווי ירושה היברידי": inheritance_hybrid,
            "הכנסת שכירות נטו": net_rental_income,
            "הוצאת שכירות": rent_paid_indexed,
            "inflation_factor": inflation_factor
        })

    df_full = pd.DataFrame(history)
    row_97 = df_full[df_full["גיל"] >= 97.0].iloc[0] if not df_full[df_full["גיל"] >= 97.0].empty else df_full.iloc[-1]

    return {
        "df": df_full[df_full["גיל"] <= check_age],
        "df_full": df_full,
        "ratio_190_97": float(row_97["צבירה תיקון 190"] / baseline_capital),
        "ratio_25_97": float(row_97["צבירה מסלול ריאלי"] / baseline_capital),
        "ratio_hybrid_97": float(row_97["צבירה מסלול היברידי"] / baseline_capital),
        "ratio_rental_97": float(row_97["צבירה מסלול שכירות"] / baseline_capital),
    }
