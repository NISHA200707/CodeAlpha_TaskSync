from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from projects.views import home, dashboard, create_project
from tasks.views import (
    create_task,
    update_task_status,
    edit_task,
    delete_task,
    upload_task_attachment,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # Home and Dashboard
    path("", home, name="home"),
    path("dashboard/", dashboard, name="dashboard"),

    # Projects
    path(
        "projects/create/",
        create_project,
        name="create_project",
    ),

    # Tasks
    path(
        "tasks/create/",
        create_task,
        name="create_task",
    ),
    path(
        "tasks/<int:task_id>/update-status/",
        update_task_status,
        name="update_task_status",
    ),
    path(
        "tasks/<int:task_id>/edit/",
        edit_task,
        name="edit_task",
    ),
    path(
        "tasks/<int:task_id>/delete/",
        delete_task,
        name="delete_task",
    ),

    # File Attachments
    path(
        "tasks/<int:task_id>/attachments/upload/",
        upload_task_attachment,
        name="upload_task_attachment",
    ),

    # Accounts
    path("accounts/", include("accounts.urls")),

    # Comments
    path("comments/", include("comments.urls")),
]

# Serve uploaded media files during development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )