from django.db import models
from django.contrib.auth.models import User
from projects.models import Project


class Task(models.Model):

    STATUS_CHOICES = [
        ("todo", "To Do"),
        ("progress", "In Progress"),
        ("completed", "Completed"),
    ]

    PRIORITY_CHOICES = [
        ("high", "High"),
        ("medium", "Medium"),
        ("low", "Low"),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks",
    )

    title = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="todo",
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="medium",
    )

    due_date = models.DateField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        from django.utils import timezone

        return (
            self.due_date is not None
            and self.due_date < timezone.localdate()
            and self.status != "completed"
        )
class TaskActivity(models.Model):

    ACTION_CHOICES = [
        ("created", "Created"),
        ("updated", "Updated"),
        ("status_changed", "Status Changed"),
        ("completed", "Completed"),
    ]

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="activities",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="task_activities",
    )

    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
    )

    description = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.task.title} - {self.get_action_display()}"
class TaskAttachment(models.Model):

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="attachments",
    )

    file = models.FileField(
        upload_to="task_attachments/",
    )

    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="task_attachments",
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"{self.task.title} - {self.file.name}"