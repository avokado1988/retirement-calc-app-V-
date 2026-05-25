import streamlit as st
import pandas as pd
from inputs.ui_components import format_shekel

def render_qa_section(results, user_inputs):
    df_history = results["df"]
    df_full = results.get("df_full", df_history)
    
    timeline = user_inputs["timeline"]
    wealth = user_inputs["wealth"]
    expenses = user_inputs["expenses"]
    
    start_age = timeline["start_age"]
    check_age = timeline["check_age"]
    
    initial_capital_190 = user_inputs["amendment_190"]["net_for_190"]
    initial_capital_25 = user_inputs["real_tax_25"]["net_for_real_pathway"]
    
    property_value_start = wealth["new_apartment_cost"]
    appreciation_rate = wealth["property_appreciation"]
    emergency_fund = wealth["emergency_fund"]
    
    row_start = df_history.iloc[0]
    exp_start = row_start["הוצאה נומינלית"]
    inc_start = row_start["הכנסה נומינלית"]
    pension_190_start = user_inputs["amendment_190"]["desired_pension"]
    
    filtered_df = df_history[df_history["גיל"] >= check_age]
    row_check = filtered_df.iloc[0] if not filtered_df.empty else df_history.iloc[-1]
    
    exp_check = row_check["הוצאה נומינלית"]
    inc_check = row_check["הכנסה נומינלית"]
    inflation_factor_check = row_check["inflation_factor"]
    balance_190_check = row_check["צבירה תיקון 190"]
    balance_25_check = row_check["צבירה מסלול ריאלי"]
    
    years_passed = check_age - start_age
    property_value_check = property_value_start * ((1 + appreciation_rate) ** years_passed)
    
    burn_age_190, burn_age_25 = 99.0, 83.0
    empty_age_190, empty_age_25 = 120.0, 120.0
    
    for idx in range(1, len(df_full)):
        if df_full.iloc[idx]["צבירה תיקון 190"] < df_full.iloc[idx-1]["צבירה תיקון 190"]:
            burn_age_190 = df_full.iloc[idx]["גיל"]
            break
    for idx in range(1, len(df_full)):
        if df_full.iloc[idx]["צבירה מסלול ריאלי"] < df_full.iloc[idx-1]["צבירה מסלול ריאלי"]:
            burn_age_25 = df_full.iloc[idx]["גיל"]
            break
            
    for idx in range(len(df_full)):
        if df_full.iloc[idx]["צבירה תיקון 190"] <= 0:
            empty_age_190 = df_full.iloc[idx]["גיל"]
            break
    for idx in range(len(df_full)):
        if df_full.iloc[idx]["צבירה מסלול ריאלי"] <= 0:
            empty_age_25 = df_full.iloc[idx]["גיל"]
            break

    ratio_190_97 = results.get("ratio_190_97", 0.0)
    ratio_25_97 = results.get("ratio_25_97", 0.0)

    # --- חישובים מוקדמים ---
    net_needed_190_start = max(0, exp_start - inc_start - pension_190_start)
    net_needed_25_start = max(0, exp_start - inc_start)
    
    pct_w_190_start = f"{(net_needed_190_start * 12) / max(1, initial_capital_190) * 100:.2f}%"
    pct_w_25_start = f"{(net_needed_25_start * 12) / max(1, initial_capital_25) * 100:.2f}%"
    
    rule400_190_start = f"{(initial_capital_190 / max(1, net_needed_190_start * 12 * 25)):.1f}" if net_needed_190_start > 0 else "∞"
    rule400_25_start = f"{(initial_capital_25 / max(1, net_needed_25_start * 12 * 25)):.1f}" if net_needed_25_start > 0 else "∞"
    
    emer_190 = f"{(emergency_fund / max(1, net_needed_190_start * 12)):.1f}" if net_needed_190_start > 0 else "∞"
    emer_25 = f"{(emergency_fund / max(1, net_needed_25_start * 12)):.1f}" if net_needed_25_start > 0 else "∞"
    
    total_wealth_190_start = initial_capital_190 + property_value_start + emergency_fund
    total_wealth_25_start = initial_capital_25 + property_value_start + emergency_fund

    net_needed_190_check = max(0, exp_check - inc_check - (pension_190_start * inflation_factor_check))
    net_needed_25_check = max(0, exp_check - inc_check)
    
    pct_w_190_check = (net_needed_190_check * 12) / max(1, balance_190_check) if balance_190_check > 0 else 1.0
    pct_w_25_check = (net_needed_25_check * 12) / max(1, balance_25_check) if balance_25_check > 0 else 1.0
    
    bool_preserve_190 = "TRUE" if balance_190_check > initial_capital_190 else "FALSE"
    bool_preserve_25 = "TRUE" if balance_25_check > initial_capital_25 else "FALSE"
    
    rule400_190_check = (initial_capital_190 / max(1, net_needed_190_check * 12 * 25)) if net_needed_190_check > 0 else 99.0
    rule400_25_check = (initial_capital_25 / max(1, net_needed_25_check * 12 * 25)) if net_needed_25_check > 0 else 99.0
    
    total_wealth_190_check = balance_190_check + property_value_check
    total_wealth_25_check = balance_25_check + property_value_check

    # --- פונקציות עיצוב HTML פנימיות חסינות אש ---
    th_q = 'style="background-color: #F2F2F2; color: #000000; font-weight: bold; padding: 12px; border: 1px solid #C0C0C0; text-align: right; width: 40%; font-size: 16px;"'
    th_190 = 'style="background-color: #FFF2CC; color: #000000; font-weight: bold; padding: 12px; border: 1px solid #C0C0C0; text-align: center; width: 30%; font-size: 16px;"'
    th_25 = 'style="background-color: #FCE4D6; color: #000000; font-weight: bold; padding: 12px; border: 1px solid #C0C0C0; text-align: center; width: 30%; font-size: 16px;"'
    
    td_q = 'style="background-color: #F2F2F2; color: #000000; padding: 10px; border: 1px solid #C0C0C0; text-align: right; font-weight: bold; font-size: 15px;"'
    
    def get_td(val, bg="#FFFFFF", bold=False, size="15px"):
        fw = "font-weight: bold;" if bold else ""
        return f'<td style="background-color: {bg}; color: #000000; padding: 10px; border: 1px solid #C0C0C0; text-align: center; font-size: {size}; {fw}">{val}</td>'

    def c_w(rate): return "#99FF99" if rate <= 0.04 else "#FF9999"
    def c_b(val_str): return "#99FF99" if val_str == "TRUE" else "#FF9999"
    def c_400(val): return "#99FF99" if val >= 1.0 else "#FF9999"
    def c_r(ratio): return "#99FF99" if ratio >= 0.90 else ("#FFCC99" if ratio >= 0.75 else "#FF9999")

    # ==========================================
    # בניית הטבלאות - עטופות במיכל לבן מושלם
    # ==========================================

    st.subheader(f"📊 מצב בגיל פרישה / התחלת סימולציה (גיל {start_age})")
    
    html_1 = f"""
    <div style="background-color: white; padding: 10px; border-radius: 8px; margin-bottom: 20px;">
        <table style="width: 100%; border-collapse: collapse; direction: rtl; font-family: sans-serif;">
            <thead>
                <tr><th {th_q}>שאלה</th><th {th_190}>גיל פרישה - מסלול תיקון 190</th><th {th_25}>גיל פרישה - מסלול 25% מס ריאלי</th></tr>
            </thead>
            <tbody>
                <tr><td {td_q}>עם כמה כסף אני מתחיל פרישה בתיק</td>{get_td(format_shekel(initial_capital_190))}{get_td(format_shekel(initial_capital_25))}</tr>
                <tr><td {td_q}>מה שווי הנדלן שלי?</td>{get_td(format_shekel(property_value_start))}{get_td(format_shekel(property_value_start))}</tr>
                <tr><td {td_q}>גובה קצבאות</td>{get_td(format_shekel(inc_start + pension_190_start))}{get_td(format_shekel(inc_start))}</tr>
                <tr><td {td_q}>כמה כסף נטו אצטרך למשוך מהתיק בכל חודש?</td>{get_td("-"+format_shekel(net_needed_190_start))}{get_td("-"+format_shekel(net_needed_25_start))}</tr>
                <tr><td {td_q}>קצב המשיכה באחוזים בפרישה?</td>{get_td(pct_w_190_start)}{get_td(pct_w_25_start)}</tr>
                <tr><td {td_q}>פי כמה גדול ההון שלי ממה שצריך לפי חוק ה400?</td>{get_td(rule400_190_start)}{get_td(rule400_25_start)}</tr>
                <tr><td {td_q}>כמה שנים ניתן לחיות מקרן החירום בשנים הראשונות?</td>{get_td(emer_190)}{get_td(emer_25)}</tr>
                <tr><td {td_q}>מה שווי כלל הנכסים שלי (הון + נדלן)?</td>{get_td(format_shekel(total_wealth_190_start))}{get_td(format_shekel(total_wealth_25_start))}</tr>
            </tbody>
        </table>
    </div>
    """
    st.markdown(html_1, unsafe_allow_html=True)

    st.subheader(f"🔮 מצב בגיל נבדק בסימולציה (גיל {check_age})")
    
    html_2 = f"""
    <div style="background-color: white; padding: 10px; border-radius: 8px; margin-bottom: 20px;">
        <table style="width: 100%; border-collapse: collapse; direction: rtl; font-family: sans-serif;">
            <thead>
                <tr><th {th_q}>שאלה</th><th {th_190}>גיל נבדק מסלול תיקון 190</th><th {th_25}>גיל נבדק פוליסת חיסכון - 25%</th></tr>
            </thead>
            <tbody>
                <tr><td {td_q}>כמה כסף נטו אצטרך למשוך מהתיק בכל חודש?</td>{get_td("-"+format_shekel(net_needed_190_check))}{get_td("-"+format_shekel(net_needed_25_check))}</tr>
                <tr><td {td_q}>מה שיעור המשיכה בגיל הנבדק והאם הוא שוחק את הקרן?</td>{get_td(f"{pct_w_190_check * 100:.2f}%", c_w(pct_w_190_check), True)}{get_td(f"{pct_w_25_check * 100:.2f}%", c_w(pct_w_25_check), True)}</tr>
                <tr><td {td_q}>כמה כסף נזיל יישאר לי בתיק?</td>{get_td(format_shekel(balance_190_check))}{get_td(format_shekel(balance_25_check))}</tr>
                <tr><td {td_q}>האם ישאר לי יותר כסף ממה שהתחלתי איתו?</td>{get_td(bool_preserve_190, c_b(bool_preserve_190), True)}{get_td(bool_preserve_25, c_b(bool_preserve_25), True)}</tr>
                <tr><td {td_q}>באיזה גיל התיק מתחיל להישחק?</td>{get_td(f"{burn_age_190:.1f}")}{get_td(f"{burn_age_25:.1f}")}</tr>
                <tr><td {td_q}>פי כמה גדול ההון ההתחלתי שלי ממה שצריך לפי חוק ה400?</td>{get_td(f"{rule400_190_check:.1f}", c_400(rule400_190_check), True)}{get_td(f"{rule400_25_check:.1f}", c_400(rule400_25_check), True)}</tr>
                <tr><td {td_q}>מה שווי הנדלן שלי?</td>{get_td(format_shekel(property_value_check))}{get_td(format_shekel(property_value_check))}</tr>
                <tr><td {td_q}>מה שווי כלל הנכסים שלי (הון + נדלן)?
