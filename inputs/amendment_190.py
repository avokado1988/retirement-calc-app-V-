import streamlit as st

def render_190_inputs(remaining_for_gimel):
    st.subheader("📑 מסלול תיקון 190 וחישוב קצבה")
    
    # הצגת ההון הזמין שהגיע מקובץ ההון בפורמט קריא עם פסיקים
    st.caption(f"הון התחלתי זמין לקופת גמל: ₪{remaining_for_gimel:,}")
    
    st.markdown("##### 🔍 הגדרות קצבה ותקופת אבטחה")
    
    # 1. קצבה קיימת מהפנסיה
    existing_pension = st.number_input("סך קצבאות פנסיה קיימות ברוטו כיום (₪)", min_value=0, value=7613, step=100)
    
    # 2. האינפוט החדש שביקשת - תקופת אבטחה בשנים (0-35)
    securing_years = st.slider("תקופת אבטחה בשנים (תקופת הבטחה)", min_value=0, max_value=35, value=20, step=1)
    
    # הגדרת רף קצבה מזערית לפי החוק (לשנת 2024 כ-5,012 ₪)
    MIN_REQUIRED_PENSION = 5012
    
    # חישוב הפער חודש בחודש לקצבה המזערית
    pension_gap = max(0, MIN_REQUIRED_PENSION - existing_pension)
    
    st.markdown("##### ⚙️ פרמטרים אקטואריים")
    conversion_coefficient = st.slider("מקדם המרה לקצבה (לחישוב אקטוארי)", min_value=150, max_value=250, value=200, step=1)
    
    # 3. החישוב האוטומטי הדינמי שביקשת!
    # ככל ששנות האבטחה עולות, ההון הנדרש להשלמה משתנה בהתאם
    if existing_pension >= MIN_REQUIRED_PENSION:
        capital_for_pension = 0
        calculated_pension = existing_pension
    else:
        # נוסחת חישוב הון נדרש המושפע ישירות משנות האבטחה ומקדם ההמרה
        # (אם יש לך נוסחה שונה באקסל, נעדכן אותה בקלות כאן בשורת החישוב)
        capital_for_pension = int(pension_gap * 12 * securing_years * (conversion_coefficient / 200))
        calculated_pension = existing_pension + (capital_for_pension / conversion_coefficient)

    # הצגת החישובים האוטומטיים בצורה נקייה וברורה עם פסיקים
    st.divider()
    st.markdown("##### 📊 חישובים אוטומטיים במסלול (משתנים לפי תקופת האבטחה):")
    
    if existing_pension >= MIN_REQUIRED_PENSION:
        st.success("✅ תנאי קצבה מזערית מתקיים מהפנסיה הקיימת! אין צורך להקצות הון נוסף לקצבה.")
        st.metric(label="קצבה מזערית כוללת צפויה", value=f"₪{calculated_pension:,.0f}")
        st.metric(label="הון נדרש לקצבה מזערית", value="₪0")
        net_for_190 = remaining_for_gimel
    else:
        st.warning("⚠️ הקצבה הקיימת נמוכה מהרף. נדרשת השלמה מתוך ההון ההתחלתי.")
        st.metric(label="השלמה חודשית נדרשת לקצבה המזערית", value=f"₪{pension_gap:,}")
        st.metric(label="הון נדרש לקצבה מזערית (משתנה לפי אבטחה)", value=f"₪{capital_for_pension:,}")
        st.metric(label="קצבה מזערית כוללת (אחרי השלמה)", value=f"₪{calculated_pension:,.0f}")
        
        # חישוב ההון שנותר פנוי למסלול הוני אחרי שגרענו את ההון לקצבה
        net_for_190 = max(0, remaining_for_gimel - capital_for_pension)
        
    st.info(f"💰 **הון נטו פנוי למשיכה הונית בתיקון 190:** ₪{net_for_190:,}")
    
    st.divider()
    st.markdown("##### 📈 תשואה ודמי ניהול")
    annual_return_190 = st.slider("תשואה שנתית צפויה במסלול 190 (%)", min_value=0.0, max_value=15.0, value=5.0, step=0.1) / 100
    management_fee_190 = st.slider("דמי ניהול שנתיים מהצבירה במסלול 190 (%)", min_value=0.0, max_value=2.0, value=0.3, step=0.05) / 100
    
    # אריזת הנתונים למילון שיעבור למנוע החישוב
    strategy_data = {
        "existing_pension": existing_pension,
        "securing_years": securing_years,
        "capital_for_pension": capital_for_pension,
        "calculated_pension": calculated_pension,
        "net_for_190": net_for_190,
        "conversion_coefficient": conversion_coefficient,
        "annual_return_190": annual_return_190,
        "management_fee_190": management_fee_190
    }
    
    return strategy_data
