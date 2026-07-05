# הנחיות קלוד לפרויקט מחשבון פרישה

## הענף העדכני

**`track4-graphs-v3`** — זהו הענף המעודכן ביותר (commit אחרון: 4 ביוני 2026).  
לפני כל עבודה: `git log --oneline origin/track4-graphs-v3 | head -5` לאימות.

## כללי אצבע — מה לא לעשות

- אל תוסיף `st.number_input` ישיר — תמיד `compact_number_input()` מ-`inputs/ui_components.py`
- אל תוסיף `st.slider` ישיר — תמיד `labeled_slider_with_value()`
- אל תוסיף ערכי ברירת מחדל ישירות ל-widget — הוסף ל-`DEFAULTS` ב-`inputs/ui_components.py`
- אל תשתמש ב-`df` לחישובים — רק ל-display. לחישובים: `df_full`
- אל תשנה היסטוריית ה-basis בלי לשמור על הסדר: מדד קודם למשיכה
- אל תוסיף עמודה ל-simulator_engine.py בלי להוסיף אותה ל-history dict (שורה ~235)
- אל תפרסם ללא הרצת `python -m pytest tests/` קודם

## כללי אצבע — מה כן

- הוסף שדות חדשים ל-`DEFAULTS` ב-`inputs/ui_components.py` ואז השתמש ב-`DEFAULTS["my_field"]`
- כל HTML ב-Streamlit → `direction: rtl; text-align: right;`
- בדיקת ריצה אחרי שינויים ב-simulator: `python -c "from simulator_engine import run_simulation; print('ok')"`
- צבעים: `COLOR_RED` להוצאות, `COLOR_GREEN` להכנסות, `COLOR_BLUE` לפרמטרים, `COLOR_ORANGE` לחירום

## TODOs פתוחים (לפי עדיפות)

### 1. visible_tracks — חיבור לגרפים [בינוני]
**קובץ:** `reports/graphs.py` — פונקציה `_track_selector(key_prefix)`

**בעיה:** הפונקציה מתעלמת מ-`visible_tracks` שמגיע מ-`user_inputs`.

**תיקון:**
```python
# שנה חתימה:
def _track_selector(key_prefix, visible_tracks=None):
    if visible_tracks is None: visible_tracks = [1, 2, 3, 4]
    show_190    = st.checkbox(..., value=(1 in visible_tracks))
    show_25     = st.checkbox(..., value=(2 in visible_tracks))
    show_h      = st.checkbox(..., value=(3 in visible_tracks))
    show_rental = st.checkbox(..., value=(4 in visible_tracks))

# ב-render_charts:
def render_charts(df_full, user_inputs):
    visible_tracks = user_inputs.get("visible_tracks", [1, 2, 3, 4])
    ...
    active = _track_selector("a", visible_tracks)
    active = _track_selector("b", visible_tracks)
    ...
```

### 2. kids_help — צמיחה כהשקעה [בינוני]
**בעיה:** כסף לילדים לא גדל עם הזמן בחישוב עושר משפחתי.

**תיקון ב-`reports/qa_report.py`:**
```python
appreciation_rate = float(wealth.get("property_appreciation", 0.023))
years_to_retire = retire_age - start_age
kids_help = float(wealth.get("kids_help", 0))
kids_wealth_retire = kids_help * (1 + appreciation_rate) ** years_to_retire
kids_wealth_check  = kids_help * (1 + appreciation_rate) ** (check_age - start_age)
```

**תיקון ב-`inputs/wealth.py`:** הוסף caption שמסביר שה-% עליית ערך חל גם על כסף לילדים.

### 3. שמירת ברירת מחדל — כתיבה לקוד [נמוך]
**בעיה:** כפתור "שמור נתונים כברירת מחדל" ב-app.py כותב ל-JSON ולא ל-DEFAULTS בקוד.

**תיקון ב-`app.py`:**
```python
import re, pathlib

def _save_defaults_to_code(user_inputs):
    ui_path = pathlib.Path(__file__).parent / "inputs" / "ui_components.py"
    content = ui_path.read_text(encoding="utf-8")
    
    tl = user_inputs.get("timeline", {})
    w  = user_inputs.get("wealth", {})
    e  = user_inputs.get("expenses", {})
    
    new_defaults = f"""DEFAULTS = {{
    "start_age": {tl.get("start_age", 65.5)},
    "retirement_age": {tl.get("retirement_age", 67.0)},
    "check_age": {tl.get("check_age", 97.0)},
    "expected_inflation": {e.get("expected_inflation", 0.023)},
    "current_expenses": {int(e.get("current_expenses", 11000))},
    "caregiver_cost": {int(e.get("caregiver_cost", 0))},
    "one_time_expense": {int(e.get("one_time_expense", 80000))},
    "one_time_frequency": {int(e.get("one_time_frequency", 8))},
    "work_income": {int(e.get("work_income", 0))},
    "desired_pension": {int(user_inputs.get("amendment_190", {}).get("desired_pension", 5306))},
    "national_insurance": {int(w.get("national_insurance", 2500))},
    "annual_return": 0.055,
    "management_fee": 0.006,
    "net_sale": {int(w.get("net_sale", 10000000))},
    "existing_savings": {int(w.get("existing_savings", 440000))},
    "new_apartment_cost": {int(w.get("new_apartment_cost", 5800000))},
    "kids_help": {int(w.get("kids_help", 1000000))},
    "emergency_fund": {int(w.get("emergency_fund", 300000))},
    "property_appreciation": {w.get("property_appreciation", 0.023)},
    "age_75_85_increase": {e.get("age_75_85_increase", 0.005)},
    "age_85_plus_increase": {e.get("age_85_plus_increase", 0.015)}
}}"""
    
    new_content = re.sub(
        r"DEFAULTS\s*=\s*\{[^}]+\}",
        new_defaults,
        content,
        flags=re.DOTALL
    )
    ui_path.write_text(new_content, encoding="utf-8")
```

## ידע על ארכיטקטורת המנוע

### סדר פעולות בכל חודש (simulator_engine.py):
1. חישוב אינפלציה חודשית + עדכון factors
2. חישוב הוצאה נומינלית + הוצאות חד-פעמיות
3. חישוב הכנסות (עבודה, ב"ל, קצבה)
4. חישוב תזרים שכירות (gross → net → maintenance → cashflow)
5. חישוב `net_needed_*` לכל מסלול
6. חסימת משיכות לפני גיל פרישה (`if current_age < retirement_age: net_needed = 0`)
7. חישוב אנואיטה משכנתה הפוכה (אם פעילה)
8. משיכות + מס לכל מסלול (190 / 25 ריאלי / שכירות)
9. החלת תשואה (`balance *= (1 + r_monthly)`)
10. עדכון שווי נדל"ן
11. חישוב שווי ירושה (תיק + ערך קצבה נותר)
12. הוספה ל-history

### מנגנון מס ריאלי (מסלולים 2,3,4):
```python
# בכל חודש — קודם מדד:
basis_25 *= (1 + i_monthly)

# בעת משיכה:
rpr = max(0, (balance - basis) / balance)  # שיעור רווח ריאלי
gross = net_needed / (1 - rpr * 0.25)
pull = min(gross, balance)
tax = pull * rpr * 0.25
basis *= (1 - pull / balance)
balance -= pull
```

### basis_190 (מסלול 1) — ללא צמידות:
```python
# מס 15% נומינלי — basis לא מוצמד
pr = max(0, (balance - basis) / balance)
gross = net_needed / (1 - pr * 0.15)
```

## שאלות שחוזרות — תשובות מהירות

**ש: למה מסלול 4 מתחיל עם פחות כסף?**  
ת: כי ב-rental, `net_for_rental = existing_savings` בלבד (₪440K ב-default). הדירה לא נמכרת, לכן אין נטו ממכירה. זה מכוון.

**ש: למה "עזרה לילדים" לא מנוכה ממסלול 4?**  
ת: במסלול 4 הדירה היא הירושה. הילדים מקבלים את הדירה. לא מנכים גם כסף וגם נכס.

**ש: מה ההבדל בין `df` ל-`df_full`?**  
ת: `df_full` הולך עד גיל 105 תמיד. `df` נחתך ב-`check_age` (ברירת מחדל 97).

**ש: למה הסימולציה לא מתעדכנת כשמשנים ערך?**  
ת: מכוון! לוחצים על ▶️ עדכן סימולציה.

**ש: מה sa_102?**  
ת: ה-"survival age at 100" — מדד דירוג שמבוסס על הצבירה בגיל 100. המסלול עם הצבירה הגבוהה ביותר בגיל 100 מקבל זהב.
