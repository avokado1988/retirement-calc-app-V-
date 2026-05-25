import streamlit as st
from inputs.ui_components import format_shekel

def render_qa_section(results, user_inputs):
    st.subheader("❓ שאלות ותשובות אסטרטגיות")
    
    df = results["df"]
    check_age = user_inputs["timeline"]["check_age"]
    
    # שאלה 1: כמה נשאר לי ביד (נטו) בגיל הבדיקה?
    st.markdown(f"### 🎯 כמה הון נטו יישאר ליורשים בגיל {check_age}?")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="נטו במסלול תיקון 190", 
                  value=format_shekel(results["end_balance_190_net"]),
                  delta=f"סך מס ששולם: {format_shekel(results['total_tax_paid_190'])}", delta_color="inverse")
    with col2:
        st.metric(label="נטו במסלול 25% ריאלי", 
                  value=format_shekel(results["end_balance_25_net"]),
                  delta=f"סך מס ששולם: {format_shekel(results['total_tax_paid_25'])}", delta_color="inverse")
                  
    st.divider()
    
    # שאלה 2: מתי נגמר הכסף (אם בכלל)?
    st.markdown("### 📉 האם הכסף צפוי להסתיים ומתי?")
    
    # בדיקה עבור 190
    empty_190 = df[df["צבירה תיקון 190"] <= 0]
    if not empty_190.empty:
        age_empty_190 = empty_190.iloc[0]["גיל"]
        st.error(f"🔴 במסלול **תיקון 190**: הכסף צפוי להסתיים בגיל **{age_empty_190}**")
    else:
        st.success(f"🟢 במסלול **תיקון 190**: הכסף יציב ומספיק מעבר לגיל {check_age}!")
        
    # בדיקה עבור 25%
    empty_25 = df[df["צבירה מסלול ריאלי"] <= 0]
    if not empty_25.empty:
        age_empty_25 = empty_25.iloc[0]["גיל"]
        st.error(f"🔴 במסלול **25% ריאלי**: הכסף צפוי להסתיים בגיל **{age_empty_25}**")
    else:
        st.success(f"🟢 במסלול **25% ריאלי**: הכסף יציב ומספיק מעבר לגיל {check_age}!")

    st.divider()
    
    # שאלה 3: השוואת תזרים ממוצע
    st.markdown("### 💰 מה היה גובה ההוצאה החודשית הממוצעת בסימולציה?")
    avg_expense = df["הוצאה נומינלית"].mean()
    st.info(f"לאורך תקופת הסימולציה, ההוצאה החודשית הממוצעת שלך (מותאמת אינפלציה וגיל) עמדה על **{format_shekel(avg_expense)}** לחודש.")
