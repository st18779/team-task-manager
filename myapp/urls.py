from django.contrib.auth import views as auth_views
from django.urls import path

from myapp import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("tasks/", views.my_tasks, name="my_tasks"),
    path("add/", views.task_create, name="task_create"),
    path("edit/<int:id>/", views.task_update, name="task_update"),
    path("delete/<int:id>/", views.task_delete, name="task_delete"),
    path("assign/<int:id>/", views.task_assignment, name="task_assign"),
    path("complete/<int:id>/", views.task_complete, name="task_complete"),
    path("tasks/filter/<str:status>/", views.searchByStatus, name="searchByStatus"),
]
