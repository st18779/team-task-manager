from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from myapp.models import Task, Team, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """ממשק ניהול למשתמשים — כאן קובעים מי מנהל (role = admin) ולאיזה צוות הוא שייך."""

    list_display = ("username", "tz", "email", "role", "team", "is_staff")
    list_filter = ("role", "team", "is_staff")
    search_fields = ("username", "tz", "email")
    fieldsets = UserAdmin.fieldsets + (("פרטי עבודה", {"fields": ("tz", "role", "team")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("פרטי עבודה", {"fields": ("tz", "role", "team")}),)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("task_name", "team", "user", "status", "end_date")
    list_filter = ("team", "status")


admin.site.register(Team)
