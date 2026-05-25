# --- חישוב יתרת הון נטו פנויה למסלול הריאלי ---
    # במסלול ריאלי 25% אין ניכוי הון לקצבה, ולכן כל ההון ההתחלתי נשאר פנוי לחלוטין
    net_for_real_pathway = remaining_for_real
    
    st.divider()
    st.markdown("##### 📊 סיכום הון במסלול:")
    
    # הצגת הודעת הצלחה ירוקה בדיוק כמו בתיקון 190
    st.success(f"💰 **יתרת הון נטו פנויה למשיכה למסלול הריאלי:** ₪{net_for_real_pathway:,}")
    
    # אריזת הנתונים למילון (וודא שאתה שומר על השמות המקוריים של המשתנים שלך)
    strategy_data = {
        "net_for_real_pathway": net_for_real_pathway,
        "annual_return_real": annual_return_real,
        "management_fee_real": management_fee_real
    }
    
    return strategy_data
