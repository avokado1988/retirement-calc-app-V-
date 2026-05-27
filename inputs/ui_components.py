import streamlit as st

# 🟢 מילון ערכי ברירת המחדל המדויקים והמיושרים של האפליקציה שלך
DEFAULTS = {
    "start_age": 65.5,
    "retirement_age": 67.0,
    "check_age": 87.0,
    "desired_pension": 5000,
    "current_expenses": 11000,
    "expected_inflation": 0.023,
    "age_75_85_increase": 0.005,
    "age_85_plus_increase": 0.015,
    "one_time_expense": 80000,
    "one_time_frequency": 8,
    "caregiver_cost": 0,
    "national_insurance": 2500,
    "work_income": 0,
    "net_sale": 0,
    "existing_savings": 0,
    "new_apartment_cost": 5800000,
    "property_appreciation": 0.023,
    "kids_help": 0,
    "emergency_fund": 0,
    "annual_return": 0.05,
    "management_fee": 0.006
}

def format_shekel(amount):
    """פונקציית עזר גלובלית לעיצוב מטבע שקלי"""
    return f"{int(amount):,} ₪" if amount is not None else "0 ₪"

def show_net_summary(title, amount):
    """מציג תיבת סיכום מעוצבת להון נטו"""
    st.markdown(
        f"<div style='padding:10px; background-color:#f1f5f9; border-radius:5px; margin:10px 0; border-right:4px solid #1e3a8a;'>"
        f"<span style='font-weight:600; color:#1e3a8a;'>{title}:</span> "
        f"<span style='font-weight:700; color:#0f172a;'>{format_shekel(amount)}</span>"
        f"</div>", 
        unsafe_allow_html=True
    )

def compact_number_input(label, value, min_value=0, max_value=None, step=1, unit="₪"):
    """
    מציג שורת קלט מעוצבת: טקסט מימין, ותיבת הקלדה קטנה משמאל.
    """
    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown(f"<div style='line-height: 2.5; font-weight: 500;'>{label}</div>", unsafe_allow_html=True)
    with col2:
        val_to_use = float(value) if isinstance(value, float) or isinstance(step, float) else int(value)
        min_to_use = float(min_value) if min_value is not None else None
        max_to_use = float(max_value) if max_value is not None else None
        
        # בניית סיומת יחידה לצד התיבה (למשל חיווי של ש"ח)
        suffix = f" {unit}" if unit else ""
        res = st.number_input(
            label,
            min_value=min_to_use, 
            max_value=max_to_use, 
            value=val_to_use, 
            step=step,
            label_visibility="collapsed"
        )
        if unit:
            st.caption(f"יחידות: {unit}")
    return res

def labeled_slider_with_value(label, min_value, max_value, value, step=1.0, format=None, unit=None):
    """
    🔄 הוסב באופן מלא להזנת מספרים תוך שמירה על הערכים והחיוויים האסתטיים בצד שמאל של השורה!
    """
    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown(f"<div style='line-height: 2.5; font-weight: 500;'>{label}</div>", unsafe_allow_html=True)
    with col2:
        # בדיקה האם מדובר באחוזים קטנים מ-1 (כמו 0.05 שמייצג 5%)
        is_percentage_fraction = format is not None and "%" in format and float(value) <= 1.0
        
        # התאמת הערכים להקלדה נוחה
        if is_percentage_fraction:
            # הופך את ה-0.05 ל-5.0 לצורך הקלדה נוחה של המשתמש
            val_to_use = float(value) * 100.0
            min_to_use = float(min_value) * 100.0
            max_to_use = float(max_value) * 100.0
            step_to_use = float(step) * 100.0 if float(step) <= 1.0 else float(step)
        else:
            val_to_use = float(value) if isinstance(step, float) or '.' in str(value) else int(value)
            min_to_use = float(min_value) if isinstance(min_value, float) else int(min_value)
            max_to_use = float(max_value) if isinstance(max_value, float) else int(max_value)
            step_to_use = step

        # יצירת שתי עמודות פנימיות קטנות: אחת לשדה המספר ואחת לסימון (%, שנים, ₪) באותו הגובה
        sub_col1, sub_col2 = st.columns([3, 1])
        with sub_col1:
            raw_input = st.number_input(
                label,
                min_value=min_to_use,
                max_value=max_to_use,
                value=val_to_use,
                step=step_to_use,
                label_visibility="collapsed"
            )
        with sub_col2:
            # קביעת הסימון שיופיע בצד שמאל בדיוק באותו קו
            display_unit = "%" if (format and "%" in format) or unit == "%" else (unit if unit else "")
            st.markdown(f"<div style='line-height: 2.5; font-weight: 600; color: #4b5563;'>{display_unit}</div>", unsafe_allow_html=True)
            
        # החזרת הערך לקוד בצורה הנכונה (אם זה היה שבר אחוזים, נחלק חזרה ב-100)
        res = float(raw_input) / 100.0 if is_percentage_fraction else raw_input
        
    return res
