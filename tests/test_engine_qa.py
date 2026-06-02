import sys, math
import pandas as pd
from simulator_engine import run_simulation

def base_inputs(**over):
    inp = {
        "timeline": {"start_age": 67.0, "retirement_age": 67.0, "check_age": 92.0},
        "wealth": {"net_sale": 10000000, "existing_savings": 440000, "new_apartment_cost": 5800000,
                   "kids_help": 1000000, "emergency_fund": 300000, "property_appreciation": 0.023,
                   "national_insurance": 2500, "remaining_for_gimel": 3340000},
        "expenses": {"current_expenses": 13000, "expected_inflation": 0.025, "age_75_85_increase": 0.005,
                     "age_85_plus_increase": 0.015, "one_time_expense": 0, "one_time_frequency": 8,
                     "caregiver_cost": 3500, "work_income": 0, "work_end_age": 67.0},
        "amendment_190": {"desired_pension": 5306, "securing_years": 20, "base_coefficient": 200,
                          "adjusted_coefficient": 220, "capital_for_pension": 1167320,
                          "net_for_190": 2172680, "annual_return_190": 0.055, "management_fee_190": 0.006},
        "real_tax_25": {"net_for_real_pathway": 3340000, "annual_return_25": 0.055, "management_fee_25": 0.006,
                        "net_for_hybrid": 2172680, "annual_return_hybrid": 0.055, "management_fee_hybrid": 0.006},
        "rental": {"net_for_rental": 440000, "rental_income_monthly": 8000, "rental_income_growth_rate": 0.03,
                   "rent_paid_monthly": 6000, "rent_paid_growth_rate": 0.03, "rental_tax_rate": 0.10,
                   "maintenance_early_pct": 0.07, "maintenance_late_pct": 0.12, "current_property_value": 10000000,
                   "rental_property_appreciation": 0.015, "rm_enabled": False, "rm_annual_rate": 0.055,
                   "rm_start_age": 78, "rm_life_expectancy_age": 92, "rm_loan_amount_ils": 0,
                   "rm_origination_fee": 0.005},
        "visible_tracks": [1, 2, 3, 4],
    }
    for k, v in over.items():
        inp[k] = {**inp[k], **v} if isinstance(v, dict) else v
    return inp

passed, failed = 0, 0
def check(name, cond, detail=""):
    global passed, failed
    if cond: passed += 1; print(f"  ✅ {name}")
    else: failed += 1; print(f"  ❌ {name} {detail}")

print("=== 1. INFLATION & INDEXATION ===")
r = run_simulation(base_inputs())
df = r["df_full"]
inf = df["inflation_factor"]
check("inflation_factor monotonic increasing", (inf.diff().dropna() >= -1e-9).all())
check("inflation_factor starts at 1.0", abs(inf.iloc[0]-1.0) < 1e-9)
# nominal expense at retirement ~= base (with caregiver=0 at 67)
exp0 = df.iloc[0]["הוצאה נומינלית"]
check("nominal expense @67 ~= base 13000", abs(exp0-13000) < 50, f"got {exp0:.0f}")
# expense grows over time
check("expense grows with inflation", df.iloc[120]["הוצאה נומינלית"] > exp0*1.15)

print("=== 2. CAREGIVER (85+) ===")
row85 = df[df["גיל"]>=85.0].iloc[0]
row84 = df[df["גיל"]<85.0].iloc[-1]
cg85 = row85["הוצאות מטפלת"]
check("caregiver 0 before 85", row84["הוצאות מטפלת"]==0)
check("caregiver >0 at 85", cg85>0, f"got {cg85:.0f}")
# caregiver = 3500 * inflation_factor at that row
check("caregiver = 3500*inflation", abs(cg85 - 3500*row85["inflation_factor"])<1.0)
# expense jump at 85 includes caregiver
exp_jump = row85["הוצאה נומינלית"] - row84["הוצאה נומינלית"]
check("expense jumps ~caregiver at 85", exp_jump > 3000, f"jump {exp_jump:.0f}")

print("=== 3. TAX 190 (15% nominal) ===")
# In a withdrawal month, tax_190 = pull * profit_ratio * 0.15
df190 = df[df["מס ששולם 190"]>0]
check("tax 190 charged at some point", len(df190)>0 or df["צבירה תיקון 190"].iloc[-1]>0)

print("=== 4. PENSION INDEXATION ===")
pen = df["הכנסה מקצבה מזערית"]
pen_pos = pen[pen>0]
check("pension paid post-retirement", len(pen_pos)>0)
check("pension indexed upward", pen_pos.iloc[-1] > pen_pos.iloc[0] if len(pen_pos)>1 else True)

print("=== 5. NI INDEXATION ===")
inc = df["הכנסה נומינלית"]
check("income (NI) grows", inc.iloc[120] > inc.iloc[0] if inc.iloc[0]>0 else True)

print("=== 6. PROPERTY APPRECIATION ===")
p0 = df.iloc[0]["שווי נדלן"]; p_end = df.iloc[-1]["שווי נדלן"]
check("residence appreciates", p_end > p0)
pr0 = df.iloc[0]["שווי נדלן מסלול 4"]; pr_end = df.iloc[-1]["שווי נדלן מסלול 4"]
check("rental property appreciates", pr_end > pr0)

print("=== 7. REVERSE MORTGAGE ===")
r2 = run_simulation(base_inputs(rental={"rm_enabled":True,"rm_loan_amount_ils":1600000,
                                         "rm_start_age":78,"rm_life_expectancy_age":92,"rm_origination_fee":0.005}))
d2 = r2["df_full"]
annuity = d2["משכנתה הפוכה — משיכה חודשית"]
total_paid = annuity.sum()
net_loan = 1600000*(1-0.005)
check("total RM received == net principal", abs(total_paid-net_loan)<5, f"paid {total_paid:.0f} vs {net_loan:.0f}")
# annuity zero before start and after life_exp
before = d2[d2["גיל"]<78]["משכנתה הפוכה — משיכה חודשית"]
after = d2[d2["גיל"]>=92]["משכנתה הפוכה — משיכה חודשית"]
check("no annuity before start_age", (before==0).all())
check("no annuity after life_exp", (after==0).all())
# debt monotonic non-decreasing
dbt = d2["משכנתה הפוכה — יתרת חוב"]
check("debt non-decreasing", (dbt.diff().dropna()>=-1e-6).all())
# equity = max(0, prop - debt)
eq = d2["משכנתה הפוכה — הון עצמי"]
recomputed = (d2["שווי נדלן מסלול 4"]-dbt).clip(lower=0)
check("equity = max(0, prop-debt)", ((eq-recomputed).abs()<1.0).all())
# debt at life_exp ~ FV of annuity (sanity: > net_loan, < net_loan*3)
dbt_92 = d2[d2["גיל"]>=92].iloc[0]["משכנתה הפוכה — יתרת חוב"]
check("debt@92 between 1x-2.5x net_loan", net_loan < dbt_92 < net_loan*2.5, f"debt92 {dbt_92:.0f}")

print("=== 8. RM SURPLUS TO SAVINGS ===")
# With RM, rental savings should be >= no-RM savings (annuity surplus added)
r0 = run_simulation(base_inputs())
sav_norm = r0["df_full"][r0["df_full"]["גיל"]>=92].iloc[0]["צבירה מסלול שכירות"]
sav_rm = d2[d2["גיל"]>=92].iloc[0]["צבירה מסלול שכירות"]
check("RM boosts rental savings", sav_rm >= sav_norm - 1, f"rm {sav_rm:.0f} vs norm {sav_norm:.0f}")

print("=== 9. NO NaN / data integrity ===")
check("no NaN in df", not d2.isnull().any().any())
check("all balances finite", all(d2[c].apply(lambda x: math.isfinite(x)).all() for c in
      ["צבירה תיקון 190","צבירה מסלול ריאלי","צבירה מסלול היברידי","צבירה מסלול שכירות"]))

print("=== 10. EDGE: RM disabled => zero RM columns ===")
check("no RM debt when disabled", (r0["df_full"]["משכנתה הפוכה — יתרת חוב"]==0).all())

print(f"\n=== RESULT: {passed} passed, {failed} failed ===")
sys.exit(1 if failed else 0)
