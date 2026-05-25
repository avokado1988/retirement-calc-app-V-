import streamlit as st

def render_190_inputs(remaining_for_gimel):
    st.subheader("📑 מסלול תיקון 190 וחישוב קצבה")
    
    # הצגת ההון שנותר מהמסך הקודם
    st.caption(f"הון התחלתי זמין לקופת גמל: ₪{remaining_for_gimel:,}")
    
    st.markdown("##### 🎯 הגדרת קצבה רצויה לרכישה")
    # המשתמש בוחר כמה קצבה חודשית הוא רוצה לקנות
    desired_pension = st.number_input("קצבה רצויה לרכישה (₪ חודשי)", min_value=0, value=5000, step=50)
    
    st.divider()
    st.markdown("##### 🎲 תנאים אקטואריים (מודל שוק ריאלי)")
    
    # סליידרים לתנאים האקטיביים של הקופה
    securing_years = st.slider("תקופת אבטחה בשנים (חודשי הבטחה ליורשים)", min_value=0, max_value=35, value=20, step=1)
    base_coefficient = st.slider("מקדם המרה בסיסי לקצבה (ללא אבטחה)", min_value=150.0, max_value=300.0, value=200.0, step=1.0)
    
    # --- הנוסחה האקטוארית הריאלית ביותר ---
    # בשוק הפנסיוני, כל שנת הבטחה מייקרת את המקדם בכ-1.0 נקודה בממוצע לגילאי פרישה אלו
    adjusted_coefficient = base_coefficient + (securing_years * 1.0)
    
    # חישוב ישר של ההון הנדרש לחיתוך מהקופה
    capital_for_pension = int(desired_pension * adjusted_coefficient)
    
    st.divider()
    st.markdown("##### 📊 חישובים אקטואריים אוטומטיים:")
    
    # הצגה בשני טורים נקיים ומקצועיים
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="מקדם המרה משוקלל (כולל אבטחה)", value=f"{adjusted_coefficient:.1f}")
    with col2:
        st.metric(label="הון נדרש שינוכה לטובת הקצבה", value=f"₪{capital_for_pension:,}")
    
    # חישוב היתרה שנותרת פנויה למסלול הוני פטור
    net_for_190 = max(0, remaining_for_gimel - capital_for_pension)
    
    if remaining_for_gimel < capital_for_pension:
        st.error(f"⚠️ אזהרה: ההון הנדרש לקצבה (₪{capital_for_pension:,}) גבוה מסך ההון הזמין שלך בקופה (₪{remaining_for_gimel:,})!")
    else:
        st.success(f"💰 **יתרת הון נטו פנויה למשיכה הונית בתיקון 190:** ₪{net_for_190:,}")
    
    st.divider()
    st.markdown("##### 📈 תשואה ודמי ניהול ליתרת ההון")
    annual_return_190 = st.slider("תשואה שנתית צפויה במסלול 190 (%)", min_value=0.0, max_value=15.0, value=5.0, step=0.1) / 100
    management_fee_190 = st.slider("דמי ניהול שנתיים מהצבירה במסלול 190 (%)", min_value=0.0, max_value=2.0, value=0.3, step=0.05) / 100
    
    # שמירת כל הדאטה הריאלי למילון שיעבור למנוע החישוב
    strategy_data = {
        "desired_pension": desired_pension,
        "securing_years": securing_years,
        "base_coefficient": base_coefficient,
        "adjusted_coefficient": adjusted_coefficient,
        "capital_for_pension": capital_for_pension,
        "net_for_190": net_for_190,
        "annual_return_190": annual_return_190,
        "management_fee_190": management_fee_190
    }
    
    return strategy_data
