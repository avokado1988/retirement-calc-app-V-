import math, numpy as np, pandas as pd
from tests.test_engine_qa import base_inputs
from simulator_engine import run_simulation

def scan(name, inp):
    try:
        r = run_simulation(inp)
    except Exception as e:
        print(f"[{name}] CRASH: {type(e).__name__}: {e}")
        return None
    df = r["df_full"]
    issues=[]
    # non-finite anywhere numeric
    for c in df.columns:
        col=df[c]
        if col.dtype.kind in "fi":
            if not np.isfinite(col.values).all(): issues.append(f"non-finite in {c}")
    bals=["צבירה תיקון 190","צבירה מסלול ריאלי","צבירה מסלול היברידי","צבירה מסלול שכירות"]
    for b in bals:
        mn=df[b].min()
        if mn < -1e-3: issues.append(f"NEG balance {b}={mn:.1f}")
    for k in ["ratio_190_97","ratio_25_97","ratio_hybrid_97","ratio_rental_97"]:
        v=r[k]
        if not math.isfinite(v): issues.append(f"ratio {k}={v}")
        elif abs(v)>1e6: issues.append(f"absurd ratio {k}={v:.2e}")
    print(f"[{name}] {'OK' if not issues else '; '.join(issues)}")
    return r

# 1 huge expenses
scan("huge_expense", base_inputs(expenses={"current_expenses":500000,"expected_inflation":0.025}))
# 2 zero savings all tracks
scan("zero_savings", base_inputs(amendment_190={"net_for_190":0,"capital_for_pension":0,"desired_pension":0,"securing_years":20,"annual_return_190":0.055,"management_fee_190":0.006},
                                 real_tax_25={"net_for_real_pathway":0,"net_for_hybrid":0,"annual_return_25":0.055,"management_fee_25":0.006,"annual_return_hybrid":0.055,"management_fee_hybrid":0.006},
                                 rental={"net_for_rental":0,"rental_income_monthly":0,"rent_paid_monthly":0,"current_property_value":10000000,"rental_property_appreciation":0.015}))
# 3 retire_age > start_age extreme
scan("retire_gt_start", base_inputs(timeline={"start_age":40.0,"retirement_age":90.0,"check_age":92.0}))
# 4 retire < start (already retired)
scan("start_gt_retire", base_inputs(timeline={"start_age":80.0,"retirement_age":67.0,"check_age":97.0}))
# 5 tiny property track4
scan("tiny_property", base_inputs(rental={"net_for_rental":50000,"current_property_value":1.0,"rental_income_monthly":0,"rent_paid_monthly":20000,"rental_property_appreciation":0.0}))
# 6 zero property
scan("zero_property", base_inputs(rental={"net_for_rental":50000,"current_property_value":0.0,"rental_income_monthly":0,"rent_paid_monthly":20000},
                                  wealth={"net_sale":10000000,"existing_savings":440000,"new_apartment_cost":0,"property_appreciation":0.023,"national_insurance":2500}))
# 7 zero baseline (balance_25=0) -> baseline_capital fallback
scan("zero_baseline25", base_inputs(real_tax_25={"net_for_real_pathway":0,"net_for_hybrid":2172680,"annual_return_25":0.055,"management_fee_25":0.006,"annual_return_hybrid":0.055,"management_fee_hybrid":0.006}))
# 8 zero income everything, high expense track4 deficit -> RM
scan("rm_stress", base_inputs(rental={"net_for_rental":120000,"rental_income_monthly":0,"rent_paid_monthly":30000,"current_property_value":3000000,"rental_property_appreciation":0.0},
                              wealth={"net_sale":0,"existing_savings":0,"new_apartment_cost":0,"property_appreciation":0.0,"national_insurance":0}))
# 9 negative return
scan("neg_return", base_inputs(amendment_190={"net_for_190":2172680,"annual_return_190":-0.5,"management_fee_190":0.006,"capital_for_pension":1167320,"desired_pension":5306,"securing_years":20}))
# 10 start_age huge (>=105)
scan("start_105", base_inputs(timeline={"start_age":105.0,"retirement_age":67.0,"check_age":92.0}))
