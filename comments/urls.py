
from django.urls import path
from . import views

urlpatterns = [
    path(
        "task/<int:task_id>/",
        views.task_comments,
        name="task_comments"
    ),
]