# מחשבון פרישה אקטוארי — בריף טכני מלא לסשן חדש

> **מטרת המסמך:** לאפשר לכל מי שפותח סשן חדש להבין את המצב המלא של הפרויקט ולהמשיך בדיוק מהנקודה.  
> **ענף בסיס:** `claude/final-v4` — זהו ה-default branch הנוכחי. מבוסס על `track4-graphs-v3` + מוזג עם תיקוני `claude/admiring-cerf-SielW` + קבצי תיעוד אלו.

---

## 1. מהי האפליקציה

סימולטור פרישה אקטוארי עם ממשק Streamlit בעברית (RTL). המשתמש מזין נתונים אישיים (גיל, הוצאות, הכנסות, הון, נדל"ן) ומקבל השוואה בין 4 מסלולי השקעה לאורך כל שנות הפרישה, חודש בחודשו עד גיל 105.

**הרצה:** `streamlit run app.py`  
**שפה:** Python 3, Streamlit, Pandas, Plotly  
**כיוון:** RTL (עברית) בכל הממשק  
**קונפיג:** `~/.streamlit/config.toml` — לא קיים, ברירות מחדל של Streamlit

---

## 2. ארבעת המסלולים

| מסלול | שם | בסיס הון | מנגנון מס | קצבה |
|-------|----|----------|-----------|------|
| 1 | תיקון 190 | `net_for_190` | 15% נומינלי (רק על רווח) | כן — קצבה מזערית מובטחת |
| 2 | 25% ריאלי | `net_for_real_pathway` | 25% ריאלי (צמוד מדד) | לא |
| 3 | היברידי | `net_for_hybrid` | 25% ריאלי + קצבה | כן — זהה למסלול 1 |
| 4 | שכירות | `net_for_rental` = `existing_savings` בלבד | 25% ריאלי + 10% שכירות | לא — אבל יש תזרים שכירות |

**שימו לב:** מסלול 4 — הדירה לא נמכרת. ההון הנזיל = חסכונות קיימים בלבד. עזרה לילדים וקרן חירום **לא** מנוכים.

---

## 3. מבנה קבצים

```
retirement-calc-app-V-/
├── app.py                      # נקודת כניסה, URL persistence, כפתור הפעלה
├── simulator_engine.py         # מנוע חישוב חודש-בחודשו (298 שורות)
├── mortality.py                # לוחות תוחלת חיים (הלמ"ס) + אינטרפולציה
├── inputs/
│   ├── __init__.py             # render_all_sidebar_inputs() — מנהל תפריט הצד
│   ├── ui_components.py        # DEFAULTS, compact_number_input, format_*, get_*_style
│   ├── timeline.py             # גיל התחלה, פרישה, בדיקה
│   ├── wealth.py               # נטו ממכירה, חסכונות, דירה חדשה, ילדים, חירום
│   ├── incomes.py              # ב"ל, קצבה, מקדם המרה, עבודה
│   ├── expenses.py             # הוצאות, אינפלציה, מטפלת, חד-פעמיות
│   ├── amendment_190.py        # הגדרות מסלול 1
│   ├── real_tax_25.py          # הגדרות מסלולים 2 ו-3
│   └── rental.py               # מסלול 4: שכירות + משכנתה הפוכה + טבלת סכנה
├── reports/
│   ├── qa_report.py            # לשונית QA — כרטיסי זהב/כסף/ארד, טבלת מדדים (1078 ש')
│   ├── qa_summary.py           # לשונית "העתקה מהירה" — טקסט להעתקה + טבלה
│   └── graphs.py               # גרפים Plotly (347 ש')
└── tests/
    └── test_engine_qa.py       # סוויטת בדיקות (24 invariants)
```

---

## 4. זרימת נתונים

```
app.py
  │
  ├── inputs.render_all_sidebar_inputs()
  │     └── returns: user_inputs = {
  │           "timeline": {...},
  │           "wealth": {...},
  │           "expenses": {...},
  │           "amendment_190": {...},
  │           "real_tax_25": {...},     # כולל מסלול 2 ו-3
  │           "rental": {...},
  │           "visible_tracks": [1,2,3,4]   # רשימת מסלולים מסומנים בצ'קבוקסים
  │         }
  │
  ├── run_simulation(user_inputs)
  │     └── returns: {
  │           "df":       DataFrame (עד check_age),
  │           "df_full":  DataFrame (עד גיל 105),
  │           "ratio_*_97": float per track
  │         }
  │
  └── reports:
        ├── render_qa_section(sim_results, user_inputs)     → tab QA
        ├── render_charts(df_full, user_inputs)             → tab גרפים
        └── render_qa_summary_page(sim_results, user_inputs)→ tab העתקה מהירה
```

---

## 5. מנגנונים מרכזיים

### 5.1 DEFAULTS — מקור אמת לערכי ברירת מחדל
```python
# inputs/ui_components.py שורה 6
DEFAULTS = {
    "start_age": 65.5,
    "retirement_age": 67.0,
    "check_age": 97.0,
    "expected_inflation": 0.023,
    "current_expenses": 11000,
    ...
}
```
כל ה-input widgets מושכים ממנו. **שמירת ברירת מחדל** צריכה לכתוב לdict הזה ישירות בקוד — ראו TODO.

### 5.2 URL Persistence — שמירה אוטומטית בדפדפן
`app.py` חוטף את `st.slider` ו-`st.number_input` ומזריק את הערכים ל-`st.query_params`:
```python
st.slider = patched_slider        # saves to ?saved_slider_<label>=val
st.number_input = patched_number_input  # saves to ?saved_num_<label>=val
```
בטעינה ראשונית, הערכים נשמטים חזרה מה-URL לתוך `st.session_state`. כפתור "נקה נתונים" מוחק את כל מפתחות `saved_*` מ-URL וסשן.

### 5.3 הפעלה על כפתור בלבד — כל תפריט הצד בתוך st.form
כל תפריט הצד עטוף ב-`st.sidebar.form("main_inputs_form")` (app.py). זו הסיבה שהאפליקציה **לא** מתחילה לחשב/לרנדר מחדש (rerun) בכלל בזמן שמזיזים סליידר או מקלידים מספר — Streamlit צובר את כל השינויים בטופס ומריץ מחדש את הסקריפט רק כשלוחצים על אחד מכפתורי ה-submit:
```python
with st.sidebar.form("main_inputs_form"):
    user_inputs = inputs.render_all_sidebar_inputs()
    run_clicked = st.form_submit_button("▶️ עדכן סימולציה", type="primary")
    save_clicked = st.form_submit_button("💾 שמור נתונים אלו כברירת מחדל")

if run_clicked or "sim_results" not in st.session_state:
    st.session_state["sim_results"] = run_simulation(user_inputs)
```
**חשוב:** בגלל זה, כל הקוד בתוך `render_all_sidebar_inputs()` (וב-`inputs/__init__.py`) חייב להשתמש ב-`st.X` הלא-מוסמך (למשל `st.expander`, `st.checkbox`) ולא ב-`st.sidebar.X` — קריאה מוסמכת ל-`st.sidebar.xxx` "בורחת" מהקונטקסט של הטופס ומרנדרת מחוצה לו. כפתור האיפוס ("🗑️ נקה נתונים") נשאר `st.button` רגיל **מחוץ** לטופס, לפני ה-`with`, ולכן ממשיך לפעול מיידית כרגיל.

**Trade-off ידוע:** widgets שחושפים widgets נוספים על בסיס תנאי (למשל checkbox "הפעל משכנתה הפוכה" ב-rental.py שחושף סליידרים נוספים) לא נחשפים באופן מיידי יותר — הם מופיעים רק אחרי לחיצה על submit, כי הטופס מדכא rerun עד אז. זו התנהגות מכוונת (זה בדיוק מה שהמשתמש ביקש).

הודעת "⚠️ יש שינויים שלא חושבו" עדיין מוצגת (מחוץ לטופס) — נשארת רלוונטית במקרה שלוחצים "שמור ברירת מחדל" בלי "עדכן".

### 5.4 compact_number_input
```python
# inputs/ui_components.py שורה 129
def compact_number_input(label, value, min_value=None, max_value=None, step=1, help_text=None, unit="₪", color=COLOR_GREEN):
    col1, col2 = st.columns([2.5, 1.5])
    # col1 = number_input, col2 = formatted preview (עם ID דינמי למניעת קיפאון)
```

### 5.5 visible_tracks
בתפריט הצד, כל מסלול יש checkbox "הצג מסלול זה בהשוואה":
```python
# inputs/__init__.py שורה 71
inputs_dict["visible_tracks"] = [
    t for t, show in [(1, _show_1), (2, _show_2), (3, _show_3), (4, _show_4)] if show
]
```
**⚠️ TODO: הרשימה הזו לא מחוברת לגרפים** — `_track_selector()` ב-`graphs.py` מתעלם ממנה (ראו סעיף TODO).

### 5.6 משכנתה הפוכה (מסלול 4)
מודל אקטוארי ישראלי: הבנק מחשב קצבה חודשית קבועה = `net_loan / n_months` (לא אנואיטה בריבית, אלא חלוקה אחידה של הקרן הנקייה). החוב גדל בריבית דריבית. **Non-recourse**: מוגבל לשווי הנכס. הקצבה פעילה מגיל `rm_start_age` עד `rm_life_expectancy_age`.

**טבלת סכנה** מוצגת תמיד ב-rental.py (ללא RM) — מציגה גיל ריקון חיסכון לפי 3 רמות.

### 5.7 maintenance — הוצאות תחזוקה דו-שלביות
```python
# simulator_engine.py שורה ~74
maintenance_early_pct = float(rental.get("maintenance_early_pct", 0.07))  # 10 שנים ראשונות
maintenance_late_pct  = float(rental.get("maintenance_late_pct", 0.12))   # מ-10 שנים ואילך
rental_start_age = 66.0  # מגיל 66 מחשבים תחזוקה
```

### 5.8 כרטיסי דירוג (QA tab)
כרטיסי זהב/כסף/ארד מבוססי `sa_100` (qa_report.py שורה 373) = עושר נטו כולל בגיל 100, בלחץ (stress-adjusted): `תיק נזיל + שווי נדל"ן + ערך קצבה נותר + קרן חירום`. **דירוג:** המסלול עם `sa_100` הגבוה ביותר מקבל זהב — לא רק צבירת התיק הנזיל. למסלולים עם קצבה (1, 3) יש בונוס טיי-ברייק של `+1`. כשמסלולים 1 ו-4 שניהם מוצגים, מבחן לחץ ייעודי (`track4_wins_stress`) יכול לעקוף את הדירוג המבוסס-ניקוד ולהחליף את מיקומם (qa_report.py שורות 446–455).

---

## 6. מצב הענפים

**סטטוס: הושלם.** `claude/final-v4` (ה-default branch הנוכחי) מבוסס על `track4-graphs-v3` (הגרסה עם RM מלא, כרטיסי זהב/כסף/ארד, maintenance דו-שלבי, Chart B2, טבלת סכנה, tests) ומכיל גם את קבצי התיעוד הללו. כל התיקונים הרלוונטיים מ-`claude/admiring-cerf-SielW` (tooltips, מניעת משיכות מוקדמות, net_for_rental) נבדקו ונכללים.

ענפים ישנים (`Main-ClaudeCode-V1`, `Test_V1-(old)`, `claude/admiring-cerf-SielW`, `claude/merged-v3` וכו') נמחקו מה-remote. הענפים הנותרים: `claude/qa-executive-summary`, `claude/reverse-mortgage-track4`, `track4-graphs-v3`, וה-default `claude/final-v4`.

---

## 7. TODO — דברים שנשארו לפתרון

### 7.1 visible_tracks לא מחובר לגרפים
**בעיה:** `inputs_dict["visible_tracks"]` נשמר, אך `_track_selector()` ב-`graphs.py` תמיד מציג checkboxes עם `value=True` (מתעלם ממה שנבחר בסידבר).

**תיקון נדרש ב-`reports/graphs.py`:**
```python
def _track_selector(key_prefix, visible_tracks=None):
    # visible_tracks = user_inputs.get("visible_tracks", [1,2,3,4])
    # defaults צריכים לבוא מ-visible_tracks, לא מ-True
    show_190    = st.checkbox(..., value=(1 in visible_tracks))
    show_25     = st.checkbox(..., value=(2 in visible_tracks))
    show_h      = st.checkbox(..., value=(3 in visible_tracks))
    show_rental = st.checkbox(..., value=(4 in visible_tracks))
```
ולהעביר `visible_tracks` מ-`render_charts(df_full, user_inputs)` לכל קריאות `_track_selector`.

### 7.2 kids_help — לא מחושב כהשקעה
**בעיה:** `kids_help` מנוכה כהוצאה סטטית. בגרסאות ישנות עבד כהשקעה צומחת לפי שיעור עליית ערך הדירה החדשה.

**תיקון נדרש:**
- ב-`wealth.py`: שנה שם השדה "עליית ערך — דירה חדשה שנתית" + הוסף caption שמסביר שזה גם שיעור הצמיחה של כסף לילדים
- ב-`qa_report.py` ו-`qa_summary.py`: חשב `kids_wealth = kids_help * (1 + appreciation_rate) ** years_to_retire`
- הוסף checkbox "כלול עזרה לילדים בסיכום עושר" (ברירת מחדל: True)

### 7.3 שמירת ברירת מחדל — כותבת לJSON ולא לקוד
**בעיה:** כפתור "שמור נתונים כברירת מחדל" כותב ל-`user_defaults.json`. לא משפיע על DEFAULTS.

**תיקון נדרש ב-`app.py`:** שנה את פונקציית השמירה כך שתקרא את `inputs/ui_components.py`, תמצא את בלוק `DEFAULTS = {...}` בregex, ותחליף אותו בערכים החדשים:
```python
import re, pathlib

def _save_defaults_to_code(user_inputs):
    path = pathlib.Path(__file__).parent / "inputs" / "ui_components.py"
    content = path.read_text(encoding="utf-8")
    # בנה בלוק DEFAULTS חדש מ-user_inputs
    new_block = "DEFAULTS = {\n    ...\n}"
    content = re.sub(r"DEFAULTS\s*=\s*\{[^}]+\}", new_block, content, flags=re.DOTALL)
    path.write_text(content, encoding="utf-8")
```

---

## 8. מדדים מרכזיים בטבלת QA

| מדד | הגדרה |
|-----|--------|
| שיעור משיכה | `(withdrawal_monthly * 12) / balance * 100` — אחוז תיק שנמשך בשנה |
| כלל 400 | `balance / (withdrawal * 400)` — כמה פעמים מכסה התיק את ה-rule-of-4% |
| קרן חירום | `emergency_fund / (withdrawal * 12)` — לכמה שנים מספיקה |
| גיל חוסן | גיל שבו התיק ייגמר (אם ייגמר, אחרת "חסין") |
| שמירת ערך | `balance_at_check / initial_balance * 100` — % שנשמר |
| עושר משפחתי | תיק + שווי נדל"ן (+ ערך קצבה נותר לטרקים 1,3) |

---

## 9. נתוני ברירת מחדל

```python
גיל התחלה: 65.5  |  גיל פרישה: 67.0  |  גיל בדיקה: 97.0
הוצאות: ₪11,000/חודש  |  אינפלציה: 2.3%
נטו ממכירה: ₪10,000,000  |  חסכונות: ₪440,000
דירה חדשה: ₪5,800,000  |  עזרה לילדים: ₪1,000,000  |  קרן חירום: ₪300,000
קצבה ב"ל: ₪2,500  |  קצבה רצויה: ₪5,306
תשואה: 5.5%  |  דמי ניהול: 0.6%
עליית ערך נדל"ן: 2.3%/שנה
```

---

## 10. דגשים לקלוד (CLAUDE notes)

- **אל תריץ סימולציה** בזמן עריכה — היא רצה רק בלחיצה על כפתור.
- **כיוון RTL** — כל `st.markdown` עם HTML חייב `direction: rtl`.
- **`compact_number_input`** תמיד — לא `st.number_input` ישיר. הפונקציה מוסיפה preview צבעוני ומטפלת בURL.
- **`DEFAULTS` ב-ui_components.py** הוא מקור האמת — כשמוסיפים שדה חדש, מוסיפים ל-DEFAULTS.
- **עמודות DataFrame** בעברית — כשמוסיפים עמודה חדשה למנוע, מוסיפים גם ל-history dict ב-simulator_engine.py (שורה 255) ולרשימות columns ב-app.py **tab3** (הטבלה המלאה, שורות 149–194). tab4 הוא לשונית "העתקה מהירה" ואין בו טבלת עמודות.
- **`sim_results_no_rm`** — ב-app.py מחושבת גרסה ללא RM תמיד (לטבלת הסכנה ב-rental.py). אל תמחק את זה.
- **`df_full`** עד גיל 105; **`df`** עד `check_age`. תמיד השתמש ב-`df_full` לחישובים, `df` לטבלת תצוגה.
- **`basis_*` צמוד מדד** — בכל חודש: `basis_25 *= (1 + i_monthly)`. סדר חשוב: קודם צמידות, אחר כך משיכה.
- **tests** ב-`tests/test_engine_qa.py` — הרץ לפני כל push.
