import streamlit as st

def render_190_inputs(remaining_for_gimel):
    st.subheader("📑 מסלול תיקון 190 וחישוב קצבה")
    
    # הצגת ההון הזמין שהגיע מקובץ ההון בפורמט קריא עם פסיקים
    st.caption(f"הון התחלתי זמין לקופת גמל: ₪{remaining_for_gimel:,}")
    
    st.markdown("##### 🎯 הגדרת קצבה רצויה לרכישה")
    
    # 1. קצבה רצויה לרכישה (אינפוט חופשי של המשתמש, למשל 5013)
    desired_pension = st.number_input("קצבה רצויה לרכישה (₪ חודשי)", min_value=0, value=5013, step=50)
    
    st.divider()
    st.markdown("##### 🎲 תנאים אקטואריים")
    
    # 2. תקופת אבטחה בשנים (0-35)
    securing_years = st.slider("תקופת אבטחה בשנים", min_value=0, max_value=35, value=20, step=1)
    
    # 3. מקדם המרה בסיסי
    base_coefficient = st.slider("מקדם המרה בסיסי לקצבה", min_value=150, max_value=250, value=200, step=1)
    
    # --- חישוב אקטיבי משולב של שנות האבטחה ---
    # בעולם הפנסיוני, כל שנת אבטחה (הבטחת קצבה ליורשים) מעלה מעט את מקדם ההמרה.
    # הגדרתי כאן שכל שנת אבטחה מוסיפה 0.5 למקדם. אם יש לך נוסחה אחרת באקסל - שנה את השורה הבאה:
    adjusted_coefficient = base_coefficient + (securing_years * 0.5)
    
    # 4. חישוב אוטומטי של ההון הנדרש לרכישת הקצבה
    capital_for_pension = int(desired_pension * adjusted_coefficient)
    
    st.divider()
    st.markdown("##### 📊 חישובים אוטומטיים במסלול:")
    
    st.metric(label="קצבה מזערית/רצויה שתתקבל", value=f"₪{desired_pension:,}")
    st.metric(label="מקדם המרה משוקלל (כולל אבטחה)", value=f"{adjusted_coefficient:.1f}")
    st.metric(label="הון נדרש ומנוכה לטובת הקצבה", value=f"₪{capital_for_pension:,}")
    
    # חישוב ההון שנותר פנוי למסלול הוני פנוי בתיקון 190
    net_for_190 = max(0, remaining_for_gimel - capital_for_pension)
    
    if remaining_for_gimel < capital_for_pension:
        st.error("⚠️ אזהרה: ההון הנדרש לקצבה גבוה מסך ההון הזמין שלך בקופת הגמל!")
    else:
        st.info(f"💰 **יתרת הון נטו פנויה למשיכה הונית בתיקון 190:** ₪{net_for_190:,}")
    
    st.divider()
    st.markdown("##### 📈 תשואה ודמי ניהול ליתרת ההון")
    annual_return_190 = st.slider("תשואה שנתית צפויה במסלול 190 (%)", min_value=0.0, max_value=15.0, value=5.0, step=0.1) / 100
    management_fee_190
