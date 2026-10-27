from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.dateparse import parse_date

from projects.models import Project
from tasks.models import Task, TaskActivity, TaskAttachment


def accessible_tasks(user):
    return (
        Task.objects.filter(project__owner=user)
        | Task.objects.filter(project__members=user)
        | Task.objects.filter(assigned_to=user)
    ).distinct()


@login_required
def create_task(request):
    user_projects = Project.objects.filter(owner=request.user)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        project_id = request.POST.get("project")
        assigned_to_id = request.POST.get("assigned_to")
        due_date_text = request.POST.get("due_date", "")
        status = request.POST.get("status", "todo")
        priority = request.POST.get("priority", "medium")

        if not title or not project_id:
            messages.error(
                request,
                "Task title and project are required."
            )
            return redirect("create_task")

        try:
            project = user_projects.get(id=int(project_id))
        except (Project.DoesNotExist, ValueError, TypeError):
            messages.error(request, "Please select a valid project.")
            return redirect("create_task")

        valid_statuses = ["todo", "progress", "completed"]
        valid_priorities = ["high", "medium", "low"]

        if status not in valid_statuses:
            status = "todo"

        if priority not in valid_priorities:
            priority = "medium"

        assigned_to = None

        if assigned_to_id:
            try:
                assigned_to = User.objects.get(id=int(assigned_to_id))
            except (User.DoesNotExist, ValueError, TypeError):
                messages.error(request, "Please select a valid assignee.")
                return redirect("create_task")

        due_date = parse_date(due_date_text) if due_date_text else None

        if due_date_text and due_date is None:
            messages.error(request, "Please enter a valid due date.")
            return redirect("create_task")

        task = Task.objects.create(
            project=project,
            title=title,
            description=description,
            assigned_to=assigned_to,
            status=status,
            priority=priority,
            due_date=due_date,
        )

        TaskActivity.objects.create(
            task=task,
            user=request.user,
            action="created",
            description=(
                f"{request.user.username} created task "
                f"'{task.title}'."
            ),
        )

        messages.success(request, "Task created successfully!")
        return redirect("dashboard")

    context = {
        "projects": user_projects,
        "users": User.objects.all().order_by("username"),
    }

    return render(request, "create_task.html", context)


@login_required
def update_task_status(request, task_id):
    if request.method != "POST":
        return redirect("dashboard")

    task = get_object_or_404(
        accessible_tasks(request.user),
        id=task_id
    )

    new_status = request.POST.get("status", "")
    valid_statuses = ["todo", "progress", "completed"]

    if new_status not in valid_statuses:
        messages.error(request, "Invalid task status.")
        return redirect("dashboard")

    old_status = task.status

    if old_status != new_status:
        task.status = new_status
        task.save(update_fields=["status"])

        if new_status == "completed":
            action = "completed"
            description = (
                f"{request.user.username} completed task "
                f"'{task.title}'."
            )
        else:
            action = "status_changed"
            description = (
                f"{request.user.username} changed task "
                f"'{task.title}' status from "
                f"'{old_status}' to '{new_status}'."
            )

        TaskActivity.objects.create(
            task=task,
            user=request.user,
            action=action,
            description=description,
        )

    messages.success(request, "Task status updated successfully!")
    return redirect("dashboard")


@login_required
def edit_task(request, task_id):
    task = get_object_or_404(
        Task.objects.filter(project__owner=request.user),
        id=task_id
    )

    user_projects = Project.objects.filter(owner=request.user)
    users = User.objects.all().order_by("username")

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        project_id = request.POST.get("project")
        assigned_to_id = request.POST.get("assigned_to", "")
        due_date_text = request.POST.get("due_date", "")
        status = request.POST.get("status", "todo")
        priority = request.POST.get("priority", "medium")

        if not title or not project_id:
            messages.error(
                request,
                "Task title and project are required."
            )
        else:
            try:
                project = user_projects.get(id=int(project_id))
            except (Project.DoesNotExist, ValueError, TypeError):
                messages.error(request, "Please select a valid project.")
            else:
                valid_statuses = ["todo", "progress", "completed"]
                valid_priorities = ["high", "medium", "low"]

                if status not in valid_statuses:
                    messages.error(request, "Please select a valid status.")

                elif priority not in valid_priorities:
                    messages.error(request, "Please select a valid priority.")

                else:
                    assigned_to = None
                    assignment_valid = True

                    if assigned_to_id:
                        try:
                            assigned_to = User.objects.get(
                                id=int(assigned_to_id)
                            )
                        except (
                            User.DoesNotExist,
                            ValueError,
                            TypeError
                        ):
                            messages.error(
                                request,
                                "Please select a valid assignee."
                            )
                            assignment_valid = False

                    due_date = (
                        parse_date(due_date_text)
                        if due_date_text
                        else None
                    )

                    if assignment_valid:
                        if due_date_text and due_date is None:
                            messages.error(
                                request,
                                "Please enter a valid due date."
                            )
                        else:
                            old_status = task.status

                            task.title = title
                            task.description = description
                            task.project = project
                            task.assigned_to = assigned_to
                            task.due_date = due_date
                            task.status = status
                            task.priority = priority
                            task.save()

                            if old_status != status and status == "completed":
                                action = "completed"
                                description = (
                                    f"{request.user.username} completed task "
                                    f"'{task.title}'."
                                )
                            elif old_status != status:
                                action = "status_changed"
                                description = (
                                    f"{request.user.username} changed task "
                                    f"'{task.title}' status from "
                                    f"'{old_status}' to '{status}'."
                                )
                            else:
                                action = "updated"
                                description = (
                                    f"{request.user.username} updated task "
                                    f"'{task.title}'."
                                )

                            TaskActivity.objects.create(
                                task=task,
                                user=request.user,
                                action=action,
                                description=description,
                            )

                            messages.success(
                                request,
                                "Task updated successfully!"
                            )
                            return redirect("dashboard")

    context = {
        "task": task,
        "projects": user_projects,
        "users": users,
    }

    return render(request, "edit_task.html", context)


@login_required
def delete_task(request, task_id):
    task = get_object_or_404(
        Task.objects.filter(project__owner=request.user),
        id=task_id
    )

    if request.method == "POST":
        task.delete()
        messages.success(request, "Task deleted successfully!")
        return redirect("dashboard")

    return render(request, "delete_task.html", {"task": task})


@login_required
def upload_task_attachment(request, task_id):
    if request.method != "POST":
        return redirect("dashboard")

    task = get_object_or_404(
        accessible_tasks(request.user),
        id=task_id,
    )

    uploaded_file = request.FILES.get("file")

    if not uploaded_file:
        messages.error(request, "Please select a file to upload.")
        return redirect("dashboard")

    import os

    allowed_extensions = [
        ".pdf", ".png", ".jpg", ".jpeg",
        ".doc", ".docx", ".xls", ".xlsx",
    ]

    extension = os.path.splitext(uploaded_file.name)[1].lower()

    if extension not in allowed_extensions:
        messages.error(
            request,
            "Invalid file type. Upload PDF, image, Word, or Excel files."
        )
        return redirect("dashboard")

    if uploaded_file.size > 10 * 1024 * 1024:
        messages.error(
            request,
            "File size must not exceed 10 MB."
        )
        return redirect("dashboard")

    attachment = TaskAttachment.objects.create(
        task=task,
        file=uploaded_file,
        uploaded_by=request.user,
    )

    TaskActivity.objects.create(
        task=task,
        user=request.user,
        action="updated",
        description=(
            f"{request.user.username} uploaded a file "
            f"for task '{task.title}'."
        ),
    )

    messages.success(request, "File uploaded successfully!")
    return redirect("dashboard")