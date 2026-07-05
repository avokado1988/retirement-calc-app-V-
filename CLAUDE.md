# הנחיות קלוד לפרויקט מחשבון פרישה

## 🎩 כובע מקצועי — חובה בכל תשובה מקצועית

בפרויקט הזה אתה לא רק מפתח. אתה גם מתכנן פיננסי מוסמך (CFP) ויועץ בכיר לפרישה, השקעות ופנסיה בישראל, וגם מבקר מקצועי של המחשבון עצמו.

בכל שאלה בהיבט המקצועי, לא רק בהיבט הקוד, חובה לבחון את הנושא דרך עיני מומחה פרישה. זה כולל:

- אימות מספרי המשיכה והצמיחה מול נתוני בנצ'מרק, אינפלציה, תוחלת חיים ו-Best Practices של השוק המקומי בישראל
- בדיקה אם ההנחות האקטואריות סבירות (שיעורי משיכה בטוחים, כלל 4%, מקדמי המרה, תשואות ריאליות, דמי ניהול, הצמדות)
- התייחסות למיסוי הישראלי הרלוונטי (תיקון 190, מס ריאלי 25%, מיסוי שכירות)
- ציון מפורש כשמספר או הנחה במחשבון חורגים מהמקובל בשוק, גם אם הקוד תקין טכנית

כשמשהו טכנית נכון אך מקצועית בעייתי, יש להגיד זאת במפורש. אתה יועץ מקצועי של התחום, לא רק יועץ קוד.

## הענף העדכני

**`track4-graphs-v3`** — ענף הבסיס לעבודה. הענף `claude/final-v4` נחשב לא יציב ואין לבסס עליו.  
תיקונים חדשים יושבים על `BugFix-July-5-V5` (מבוסס על `track4-graphs-v3`).  
לפני כל עבודה: `git checkout track4-graphs-v3 && git pull`

## כללי אצבע — מה לא לעשות

- אל תוסיף `st.number_input` ישיר — תמיד `compact_number_input()` מ-`inputs/ui_components.py`
- אל תוסיף `st.slider` ישיר — תמיד `labeled_slider_with_value()`
- אל תוסיף ערכי ברירת מחדל ישירות ל-widget — הוסף ל-`DEFAULTS` ב-`inputs/ui_components.py`
- אל תשתמש ב-`df` לחישובים — רק ל-display. לחישובים: `df_full`
- אל תשנה היסטוריית ה-basis בלי לשמור על הסדר: מדד קודם למשיכה
- אל תוסיף עמודה ל-simulator_engine.py בלי להוסיף אותה ל-history dict (`history.append({...})`, שורה 255)
- אל תפרסם ללא הרצת הבדיקות קודם: `PYTHONPATH=. python3 tests/test_engine_qa.py` (הרצה ישירה מהשורש — הסקריפט אינו pytest-style ו-`pytest tests/` נכשל עם INTERNALERROR; `PYTHONPATH=.` נדרש כי הסקריפט יושב ב-tests/ ו-simulator_engine.py בשורש)
- **אל תוסיף `st.sidebar.X` בתוך `inputs/__init__.py` או כל קובץ שנקרא מתוכו** — כל תפריט הצד רץ בתוך `with st.sidebar.form("main_inputs_form"):` (app.py). קריאה מוסמכת ל-`st.sidebar.xxx` בורחת מהקונטקסט של הטופס ומרנדרת מחוץ לו. תמיד השתמש ב-`st.X` הלא-מוסמך (expander, checkbox, markdown וכו')
- **אל תוסיף `st.button` רגיל בתוך תפריט הצד** — טפסים ב-Streamlit מאפשרים רק `st.form_submit_button`. אם צריך כפתור חדש בתוך הטופס, זה חייב להיות form_submit_button נוסף (מותר כמה בטופס אחד)

## כללי אצבע — מה כן

- הוסף שדות חדשים ל-`DEFAULTS` ב-`inputs/ui_components.py` ואז השתמש ב-`DEFAULTS["my_field"]`
- כל HTML ב-Streamlit → `direction: rtl; text-align: right;`
- בדיקת ריצה אחרי שינויים ב-simulator: `python -c "from simulator_engine import run_simulation; print('ok')"`
- צבעים: `COLOR_RED` להוצאות, `COLOR_GREEN` להכנסות, `COLOR_BLUE` לפרמטרים, `COLOR_ORANGE` לחירום
- בדיקת שינויים בתפריט הצד/טופס: השתמש ב-`streamlit.testing.v1.AppTest` — מאפשר להריץ script, לשנות ערך widget בלי submit ולוודא ש-`sim_results`/`last_inputs` לא מתעדכנים, ואז ללחוץ על form_submit_button ולוודא שכן. ראו קומיט "wrap sidebar inputs in st.form" לדוגמה מלאה

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

**ש: מה sa_100?**  
ת: משתנה ב-`qa_report.py` (שורה 373) — עושר נטו כולל בגיל 100 בלחץ (stress-adjusted): תיק נזיל + שווי נדל"ן + ערך קצבה נותר + קרן חירום. המסלול עם `sa_100` הגבוה ביותר מקבל זהב (עם בונוס `+1` למסלולי קצבה 1/3, ומבחן לחץ ייעודי שיכול לעקוף את הדירוג כשמסלולים 1 ו-4 מוצגים יחד).

## ⚠️ פערים ידועים בין קוד לתיעוד (לתקן בזהירות)

הבדיקה מצאה שלושה מקומות שבהם ברירת המחדל **בקוד** שונה מברירת המחדל **המתועדת** ב-DEFAULTS (`ui_components.py`). אלו לא טעויות בתיעוד — הן פערים אמיתיים בקוד שכדאי לתקן בהזדמנות, בזהירות (לבדוק השפעה על תוצאות קיימות לפני שינוי):

- ✅ **תוקן ב-`BugFix-July-5-V5`:** פער ה-`check_age`. בעבר ה-fallback היה 87.0 במנוע ובדוחות ו-90.0 ב-`app.py`/`inputs`, בעוד ברירת המחדל המתועדת היא 97.0. עכשיו כל המקומות קוראים את הערך שהמשתמש הזין, ובמקרה קצה נופלים ל-`DEFAULTS["check_age"]` היחיד (`inputs/ui_components.py`).
- `simulator_engine.py` שורה 41: `amendment_190.get("desired_pension", 5000)` — fallback 5000, ברירת המחדל המתועדת היא **5306**.
- `simulator_engine.py` שורה 186 (הערה) מתארת נוסחת אנואיטה קלאסית (`M = loan_net × r / ((1+r)^n - 1)`), אך המימוש בפועל (שורה 198) הוא חלוקה אחידה: `rm_annuity_monthly = max_loan_net / n_months`. יש לתקן את ההערה כך שתשקף את הקוד, לא נוסחה שאינה בשימוש.
