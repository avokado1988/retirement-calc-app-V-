"""
לוחות תוחלת חיים (ישראל) — מבוסס נתוני הלשכה המרכזית לסטטיסטיקה (הלמ"ס).
תוחלת חיים שארית (remaining life expectancy) לפי גיל ומין, מעוגל לנתוני
לוחות התמותה התקופתיים העדכניים. משמש לחישוב אוטומטי של אופק התכנון
(גיל תוחלת חיים) במקום שהמשתמש יזין אותו ידנית.
"""

# תוחלת חיים שארית (שנים נוספות צפויות) בגיל נתון — נקודות עיגון.
# מקור: לוחות תמותה הלמ"ס. ביניהן מתבצעת אינטרפולציה לינארית.
_REMAINING_LE = {
    "male": {
        50: 31.5, 55: 27.0, 60: 22.8, 65: 18.8, 67: 17.3, 70: 15.2,
        75: 11.9, 80: 8.9, 85: 6.4, 90: 4.4, 95: 3.0, 100: 2.0,
    },
    "female": {
        50: 34.5, 55: 29.8, 60: 25.3, 65: 21.0, 67: 19.4, 70: 17.0,
        75: 13.3, 80: 9.9, 85: 7.0, 90: 4.9, 95: 3.3, 100: 2.2,
    },
}


def _interp(table, age):
    """אינטרפולציה לינארית של תוחלת החיים השארית בגיל נתון."""
    ages = sorted(table.keys())
    if age <= ages[0]:
        return table[ages[0]]
    if age >= ages[-1]:
        return table[ages[-1]]
    for i in range(len(ages) - 1):
        a0, a1 = ages[i], ages[i + 1]
        if a0 <= age <= a1:
            frac = (age - a0) / (a1 - a0)
            return table[a0] + frac * (table[a1] - table[a0])
    return table[ages[-1]]


def life_expectancy_age(sex, current_age):
    """
    מחזיר את הגיל הצפוי לתוחלת חיים = גיל נוכחי + תוחלת חיים שארית.
    sex: 'male' / 'female' (או 'זכר' / 'נקבה').
    """
    key = "female" if str(sex) in ("female", "נקבה", "אישה", "f", "F") else "male"
    table = _REMAINING_LE[key]
    remaining = _interp(table, float(current_age))
    return float(current_age) + remaining
