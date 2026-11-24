from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class Team(models.Model):
    team_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.team_name}"

class User(AbstractUser):
    tz = models.CharField(max_length = 10, primary_key = True)
    role = models.CharField(default = 0)
    team=models.ForeignKey(Team ,on_delete=models.CASCADE, null=True, blank=True)

    # שדות שיתבקשו גם ב-createsuperuser (אחרת תעודת הזהות נשמרת ריקה)
    REQUIRED_FIELDS = ["tz", "email"]

    def __str__(self):
        return self.username

class Task(models.Model):
    task_name = models.CharField(max_length = 50)
    description = models.CharField(max_length = 100)
    status_new="new"
    status_in_progress="in_progress"
    status_done="done"
    status_choices = [
        (status_new,"חדש"),
        (status_in_progress,"בתהליך"),
        (status_done,"הושלם")
    ]
    status = models.CharField(
        max_length=20,
        choices=status_choices,
        default=status_new
    )
    end_date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.task_name}"

