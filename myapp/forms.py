from django import forms
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm

from myapp.models import Task, User


class UserCreationForm(BaseUserCreationForm):
    """טופס הרשמה. התפקיד (role) לא נבחר כאן — מנהלים מוגדרים בממשק הניהול /admin/."""

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "tz",
            "username",
            "email",
            "team",
            "password1",
            "password2",
        )
        labels = {
            "first_name": "שם פרטי",
            "last_name": "שם משפחה",
            "tz": "תעודת זהות",
            "username": "שם משתמש",
            "email": "אימייל",
            "team": "צוות",
        }
        error_messages = {
            "tz": {"unique": "כבר קיים משתמש עם תעודת הזהות הזו."},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["team"].required = True
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["team"].empty_label = "בחרי צוות"
        self.fields["password1"].label = "סיסמה"
        self.fields["password2"].label = "אימות סיסמה"
        # הסברים קצרים במקום הטקסטים הארוכים של Django
        self.fields["username"].help_text = "לכניסה למערכת, למשל noa.peretz"
        self.fields["password1"].help_text = "לפחות 8 תווים, ולא רק ספרות"
        self.fields["password2"].help_text = ""

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "user"
        if commit:
            user.save()
        return user


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        exclude = ["team"]
        labels = {
            "task_name": "שם המשימה",
            "description": "תיאור",
            "status": "סטטוס",
            "end_date": "תאריך סיום",
            "user": "עובד משויך",
        }
        widgets = {
            "end_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, team=None, **kwargs):
        super().__init__(*args, **kwargs)
        # אפשר לשייך משימה רק לעובדים מהצוות של המנהל (ולא למנהלים)
        self.fields["user"].queryset = (
            User.objects.filter(team=team).exclude(role="admin").order_by("username")
        )
        self.fields["user"].required = False
        # ברשימת העובדים מוצג השם המלא ולא שם המשתמש
        self.fields["user"].label_from_instance = lambda u: u.get_full_name() or u.username
        # במשימה חדשה הסטטוס תמיד "חדש" — השדה מופיע רק בעריכה
        if not self.instance.pk:
            del self.fields["status"]


class TaskFilterForm(forms.Form):
    STATUS_CHOICES = [
        ("", "כל הסטטוסים"),
        ("new", "חדש"),
        ("in_progress", "בתהליך"),
        ("done", "הושלם"),
    ]

    ASSIGNEE_CHOICES = [
        ("", "כל העובדים"),
        ("unassigned", "לא משויך"),
        ("me", "המשימות שלי"),
    ]

    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False)
    assignee = forms.ChoiceField(choices=ASSIGNEE_CHOICES, required=False)