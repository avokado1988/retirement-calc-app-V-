import streamlit as st

def render_190_inputs(remaining_for_gimel):
    st.subheader("📑 מסלול תיקון 190 וחישוב קצבה")
    
    st.caption(f"הון התחלתי זמין לקופת גמל: ₪{remaining_for_gimel:,}")
    
    st.markdown("##### 🎯 הגדרת קצבה רצויה לרכישה")
    
    # המשתמש מכניס בדיוק כמה קצבה הוא רוצה לקנות (למשל 5000)
    desired_pension = st.number_input("קצבה רצויה לרכישה (₪ חודשי)", min_value=0, value=5000, step=50)
    
    st.divider()
    st.markdown("##### 🎲 תנאים אקטואריים")
    
    securing_years = st.slider("תקופת אבטחה בשנים", min_value=0, max_value=35, value=20, step=1)
    base_coefficient = st.slider("מקדם המרה בסיסי לקצבה", min_value=150.0, max_value=300.0, value=200.0, step=1.0)
    
    # חישוב המקדם: נניח שכל שנת אבטחה מוסיפה 0.5 למקדם (אם באקסל זה שונה - אפשר לשנות את ה-0.5)
    adjusted_coefficient = base_coefficient + (securing_years * 0.5)
    
    # --- הנה החישוב הישיר שמונע את ה"באג" ---
    # ההון הנדרש הוא פשוט: קצבה כפול המקדם המותאם!
    capital_for_pension = int(desired_pension * adjusted_coefficient)
    
    st.divider()
    st.markdown("##### 📊 חישובים אוטומטיים במסלול:")
    
    st.metric(label="קצבה רצויה נבחרת", value=f"₪{desired_pension:,}")
    st.metric(label="מקדם המרה משוקלל (כולל שנות אבטחה)", value=f"{adjusted_coefficient:.1f}")
    
    # כאן תראה את המיליון ש"ח שחיפשת!
    st.metric(label="הון נדרש שינוכה לטובת הקצבה", value=f"₪{capital_for_pension:,}")
    
    # חישוב היתרה למשיכה הונית
    net_for_190 = max(0, remaining_for_gimel - capital_for_pension)
    
    if remaining_for_gimel < capital_for_pension:
        st.error("⚠️ אזהרה: ההון הנדרש לקצבה גבוה מסך ההון הזמין שלך!")
    else:
        st.info(f"💰 **יתרת הון נטו פנויה למשיכה הונית בתיקון 190:** ₪{net_for_190:,}")
    
    st.divider()
    st.markdown("##### 📈 תשואה ודמי ניהול ליתרת ההון")
    annual_return_190 = st.slider("תשואה שנתית צפויה במסלול 190 (%)", min_value=0.0, max_value=15.0, value=5.0, step=0.1) / 100
    management_fee_190 = st.slider("דמי ניהול שנתיים מהצבירה במסלול 190 (%)", min_value=0.0, max_value=2.0, value=0.3, step=0.05) / 100
    
    strategy_data = {
        "desired_pension": desired_pension,
        "securing_years": securing_years,
        "adjusted_coefficient": adjusted_coefficient,
        "capital_for_pension": capital_for_pension,
        "net_for_190": net_for_190,
        "annual_return_190": annual_return_190,
        "management_fee_190": management_fee_190
    }
    
    return strategy_data
