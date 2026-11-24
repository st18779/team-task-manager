from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Case, IntegerField, When
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from myapp.models import Task
from .forms import TaskFilterForm, TaskForm, UserCreationForm

NO_PERMISSION = "אין לך הרשאה לבצע פעולה זו"


def is_admin(user):
    return user.role == "admin"


def team_tasks(user):
    """משימות הצוות, ממוינות: בתהליך → חדש → הושלם, ובתוך כל קבוצה לפי תאריך סיום."""
    status_order = Case(
        When(status=Task.status_in_progress, then=0),
        When(status=Task.status_new, then=1),
        default=2,
        output_field=IntegerField(),
    )
    return (
        Task.objects.filter(team=user.team)
        .select_related("user")
        .annotate(status_order=status_order)
        .order_by("status_order", "end_date")
    )


def home(request):
    return render(request, "home.html")


def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "accounts/register.html", {"form": form})


@login_required
def my_tasks(request):
    tasks = team_tasks(request.user)

    form = TaskFilterForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        status = form.cleaned_data.get("status")
        assignee = form.cleaned_data.get("assignee")

        if status:
            tasks = tasks.filter(status=status)

        if assignee == "unassigned":
            tasks = tasks.filter(user__isnull=True)
        elif assignee == "me":
            tasks = tasks.filter(user=request.user)

    return render(
        request,
        "admin/showAllTasks.html",
        {"tasks": tasks, "form": form, "today": timezone.localdate()},
    )


@login_required
def searchByStatus(request, status):
    tasks = team_tasks(request.user).filter(status=status)
    form = TaskFilterForm(initial={"status": status})
    return render(
        request,
        "admin/showAllTasks.html",
        {"tasks": tasks, "form": form, "today": timezone.localdate()},
    )


@login_required
def task_create(request):
    if not is_admin(request.user):
        return HttpResponseForbidden(NO_PERMISSION)

    if request.method == "POST":
        formTask = TaskForm(request.POST, team=request.user.team)
        if formTask.is_valid():
            task = formTask.save(commit=False)
            task.team = request.user.team
            task.save()
            return redirect("my_tasks")
    else:
        formTask = TaskForm(team=request.user.team)

    return render(request, "admin/taskform.html", {"formTask": formTask})


@login_required
def task_update(request, id):
    if not is_admin(request.user):
        return HttpResponseForbidden(NO_PERMISSION)

    task = get_object_or_404(Task, pk=id, team=request.user.team)

    if request.method == "POST":
        formTask = TaskForm(request.POST, instance=task, team=request.user.team)
        if formTask.is_valid():
            formTask.save()
            return redirect("my_tasks")
    else:
        formTask = TaskForm(instance=task, team=request.user.team)

    return render(request, "admin/taskform.html", {"formTask": formTask})


@login_required
def task_delete(request, id):
    if not is_admin(request.user):
        return HttpResponseForbidden(NO_PERMISSION)

    task = get_object_or_404(Task, pk=id, team=request.user.team)

    if request.method == "POST":
        task.delete()
        return redirect("my_tasks")

    return render(request, "admin/task_confirm_delete.html", {"task": task})


@login_required
@require_POST
def task_assignment(request, id):
    task = get_object_or_404(Task, pk=id)

    if task.team_id != request.user.team_id:
        return HttpResponseForbidden("אין לך הרשאה למשימה מצוות אחר")

    if is_admin(request.user):
        return HttpResponseForbidden("מנהל לא משייך לעצמו משימות")

    if task.user_id is None:
        task.user = request.user
        task.status = Task.status_in_progress
        task.save(update_fields=["user", "status"])

    return redirect("my_tasks")


@login_required
@require_POST
def task_complete(request, id):
    task = get_object_or_404(Task, pk=id)

    if task.team_id != request.user.team_id:
        return HttpResponseForbidden("אין לך הרשאה למשימה מצוות אחר")

    if not (is_admin(request.user) or task.user_id == request.user.pk):
        return HttpResponseForbidden(NO_PERMISSION)

    task.status = Task.status_done
    task.save(update_fields=["status"])

    return redirect("my_tasks")
