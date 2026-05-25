import streamlit as st

def render_190_inputs(remaining_for_gimel):
    st.subheader("📑 מסלול תיקון 190 וחישוב קצבה")
    
    # הצגת ההון הזמין שהגיע מקובץ ההון
    st.caption(f"הון התחלתי זמין לקופת גמל: ₪{remaining_for_gimel:,}")
    
    st.markdown("##### 🔍 בדיקת קצבה מזערית (כ-5,012 ₪ ב-2024)")
    existing_pension = st.number_input("סך קצבאות פנסיה קיימות ברוטו כיום (₪)", min_value=0, value=7613, step=100)
    
    # חישוב: האם חסר כסף לקצבה המזערית?
    MIN_REQUIRED_PENSION = 5012
    strategy_data = {
        "existing_pension": existing_pension,
        "capital_for_pension": 0  # ברירת מחדל: לא צריך לנעול הון
    }
    
    if existing_pension >= MIN_REQUIRED_PENSION:
        st.success("✅ תנאי קצבה מזערית מתקיים! אין צורך להקצות הון נוסף לקצבה.")
        strategy_data["meets_min_pension"] = True
    else:
        st.warning("⚠️ הקצבה הקיימת נמוכה מהקצבה המזערית. יש להקצות הון להשלמת הקצבה.")
        strategy_data["meets_min_pension"] = False
        
        # כאן הוספנו את האינפוט שביקשת!
        strategy_data["capital_for_pension"] = st.slider(
            "הון לטובת השלמה לקצבה מזערית (₪)", 
            min_value=0, 
            max_value=int(remaining_for_gimel), 
            value=0, 
            step=10_000,
            help="סכום זה יינעל לצורך קבלת קצבה ולא יהיה זמין למשיכה הונית לפי תיקון 190."
        )
    
    st.divider()
    
    # חישוב ההון הנותר לתיקון 190 אחרי שהורדנו את מה שננעל לקצבה
    strategy_data["net_for_190"] = remaining_for_gimel - strategy_data["capital_for_pension"]
    st.info(f"הון נטו פנוי למשיכה הונית בתיקון 190: ₪{strategy_data['net_for_190']:,}")
    
    st.markdown("##### ⚙️ פרמטרים כלכליים למסלול")
    strategy_data["conversion_coefficient"] = st.slider("מקדם המרה לקצבה (לחישוב אקטוארי)", min_value=150, max_value=250, value=200, step=1)
    strategy_data["annual_return_190"] = st.slider("תשואה שנתית צפויה במסלול 190 (%)", min_value=0.0, max_value=15.0, value=5.0, step=0.1) / 100
    strategy_data["management_fee_190"] = st.slider("דמי ניהול שנתיים מהצבירה במסלול 190 (%)", min_value=0.0, max_value=2.0, value=0.3, step=0.05) / 100
        
    return strategy_data
