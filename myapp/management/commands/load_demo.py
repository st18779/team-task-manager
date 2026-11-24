"""
טעינת נתוני דוגמה: שלושה צוותים, מנהלים, עובדים ומשימות.

הרצה:
    python manage.py load_demo

הפקודה לא מוחקת נתונים קיימים. אם משתמש או משימה כבר קיימים — הם מדולגים.
הסיסמה של כל משתמשי הדוגמה: Demo1234!
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from myapp.models import Task, Team, User

PASSWORD = "Demo1234!"

# (שם משתמש, שם פרטי, שם משפחה, ת"ז, תפקיד)
TEAMS = {
    "פיתוח": [
        ("michal", "מיכל", "לוי", "900000011", "admin"),
        ("yossi", "יוסי", "כהן", "900000012", "user"),
        ("noa", "נועה", "פרץ", "900000013", "user"),
        ("avi", "אבי", "מזרחי", "900000014", "user"),
    ],
    "עיצוב": [
        ("dana", "דנה", "אברהם", "900000021", "admin"),
        ("shira", "שירה", "ביטון", "900000022", "user"),
        ("eitan", "איתן", "גולן", "900000023", "user"),
    ],
    "שיווק": [
        ("rachel", "רחל", "פרידמן", "900000031", "admin"),
        ("tamar", "תמר", "שפירא", "900000032", "user"),
        ("david", "דוד", "אוחיון", "900000033", "user"),
    ],
}

# (צוות, שם משימה, תיאור, סטטוס, עובד משויך, ימים עד תאריך הסיום)
TASKS = [
    # פיתוח
    ("פיתוח", "תיקון באג בדף ההתחברות", "כשמזינים סיסמה שגויה לא מופיעה הודעת שגיאה. להוסיף הודעה ברורה מתחת לטופס.", "in_progress", "yossi", 2),
    ("פיתוח", "ייצוא משימות לאקסל", "להוסיף כפתור שמוריד את רשימת המשימות של הצוות כקובץ Excel.", "new", None, 10),
    ("פיתוח", "שיפור מהירות טעינת הדשבורד", "הדף נטען לאט כשיש הרבה משימות. לבדוק את השאילתות ולהוסיף אינדקסים.", "in_progress", "noa", -1),
    ("פיתוח", "התראות במייל על משימה חדשה", "לשלוח מייל לעובד כשמשייכים אליו משימה.", "new", None, 14),
    ("פיתוח", "עדכון גרסת Django", "לעדכן לגרסה האחרונה ולוודא שכל הבדיקות עוברות.", "done", "avi", -5),
    ("פיתוח", "גיבוי אוטומטי של מסד הנתונים", "להגדיר גיבוי יומי בשעה 02:00 ושמירה של 7 הגיבויים האחרונים.", "done", "yossi", -8),
    # עיצוב
    ("עיצוב", "עיצוב דף נחיתה חדש", "דף נחיתה לקמפיין הקרוב — מובייל ודסקטופ, לפי שפת המותג.", "in_progress", "shira", 5),
    ("עיצוב", "הכנת אייקונים לאפליקציה", "סט של 12 אייקונים בסגנון קו אחיד, בפורמט SVG.", "new", None, 12),
    ("עיצוב", "עדכון לוגו לגרסה כהה", "גרסה של הלוגו שמתאימה לרקע כהה, כולל קובץ PNG שקוף.", "done", "eitan", -3),
    ("עיצוב", "מוקאפ למסך פרופיל משתמש", "מסך פרופיל עם תמונה, פרטים אישיים והגדרות התראות.", "new", None, 7),
    # שיווק
    ("שיווק", "הכנת קמפיין לחנוכה", "רעיון מרכזי, 3 באנרים וטקסטים לרשתות החברתיות.", "in_progress", "tamar", 4),
    ("שיווק", "כתיבת פוסט לבלוג החברה", "פוסט על 5 טיפים לניהול משימות בצוות, כ-600 מילים.", "new", None, 6),
    ("שיווק", "דוח ביצועים חודשי", "סיכום כניסות לאתר, המרות ותוצאות הקמפיינים של החודש.", "done", "david", -2),
    ("שיווק", "תיאום צילומים לאתר", "לקבוע צלם ומיקום לצילומי צוות לעמוד 'אודות'.", "new", None, 15),
]


class Command(BaseCommand):
    help = "טוען נתוני דוגמה (צוותים, משתמשים ומשימות) לצורך הדגמה וצילומי מסך"

    @transaction.atomic
    def handle(self, *args, **options):
        today = timezone.localdate()
        users = {}
        created_users = created_tasks = 0

        for team_name, members in TEAMS.items():
            team, _ = Team.objects.get_or_create(team_name=team_name)
            for username, first, last, tz, role in members:
                user = User.objects.filter(username=username).first()
                if user is None:
                    user = User(
                        tz=tz, username=username, first_name=first, last_name=last,
                        email=f"{username}@example.com", role=role, team=team,
                    )
                    user.set_password(PASSWORD)
                    user.save()
                    created_users += 1
                users[username] = user

        for team_name, name, description, status, assignee, days in TASKS:
            team = Team.objects.get(team_name=team_name)
            _, created = Task.objects.get_or_create(
                team=team,
                task_name=name,
                defaults={
                    "description": description,
                    "status": status,
                    "user": users.get(assignee) if assignee else None,
                    "end_date": today + timedelta(days=days),
                },
            )
            created_tasks += created

        self.stdout.write(self.style.SUCCESS(
            f"נוצרו {created_users} משתמשים ו-{created_tasks} משימות. הסיסמה לכל משתמשי הדוגמה: {PASSWORD}"
        ))
