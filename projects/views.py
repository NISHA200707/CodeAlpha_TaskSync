from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone

from projects.models import Project
from tasks.models import Task, TaskActivity


def home(request):
    return render(request, "home.html")


@login_required
def dashboard(request):
    user_projects = Project.objects.filter(owner=request.user)

    user_tasks = Task.objects.filter(
        assigned_to=request.user
    ).select_related("project", "assigned_to")

    # Search by task title
    search_query = request.GET.get("search", "").strip()

    if search_query:
        user_tasks = user_tasks.filter(
            title__icontains=search_query
        )

    # Filter by status
    selected_status = request.GET.get("status", "")

    valid_statuses = ["todo", "progress", "completed"]

    if selected_status in valid_statuses:
        user_tasks = user_tasks.filter(status=selected_status)
    else:
        selected_status = ""

    # Filter by project
    selected_project = request.GET.get("project", "")

    if selected_project:
        try:
            project_id = int(selected_project)
            user_tasks = user_tasks.filter(
                project_id=project_id,
                project__owner=request.user
            )
        except (ValueError, TypeError):
            selected_project = ""

    # Filter by due date
    selected_due_date = request.GET.get("due_date", "")

    if selected_due_date:
        from django.utils.dateparse import parse_date

        parsed_due_date = parse_date(selected_due_date)

        if parsed_due_date:
            user_tasks = user_tasks.filter(
                due_date=parsed_due_date
            )
        else:
            selected_due_date = ""

    # All tasks assigned to the logged-in user
    all_user_tasks = Task.objects.filter(
        assigned_to=request.user
    )

    # Recent activities for projects the user can access
    activities = TaskActivity.objects.filter(
        Q(task__project__owner=request.user)
        | Q(task__project__members=request.user)
        | Q(task__assigned_to=request.user)
    ).select_related(
        "task",
        "user",
        "task__project",
    ).distinct().order_by("-created_at")[:10]

    # --------------------------------
    # PROGRESS ANALYTICS
    # --------------------------------

    analytics_tasks = all_user_tasks

    analytics_total = analytics_tasks.count()

    analytics_completed = analytics_tasks.filter(
        status="completed"
    ).count()

    analytics_in_progress = analytics_tasks.filter(
        status="progress"
    ).count()

    analytics_todo = analytics_tasks.filter(
        status="todo"
    ).count()

    # Completion percentage
    if analytics_total > 0:
        completion_percentage = round(
            (analytics_completed / analytics_total) * 100
        )
    else:
        completion_percentage = 0

    # Overdue tasks: due date is before today and task is not completed
    today = timezone.localdate()

    overdue_count = analytics_tasks.filter(
        due_date__lt=today
    ).exclude(
        status="completed"
    ).count()

    # Project-wise progress
    project_analytics = []

    for project in user_projects:
        project_tasks = Task.objects.filter(
            project=project,
            assigned_to=request.user
        )

        total = project_tasks.count()

        completed = project_tasks.filter(
            status="completed"
        ).count()

        if total > 0:
            percentage = round((completed / total) * 100)
        else:
            percentage = 0

        project_analytics.append({
            "project": project,
            "total": total,
            "completed": completed,
            "percentage": percentage,
        })

    context = {
        "username": request.user.username,
        "email": request.user.email,

        # Existing dashboard statistics
        "project_count": user_projects.count(),
        "task_count": all_user_tasks.count(),
        "completed_count": analytics_completed,
        "pending_count": all_user_tasks.exclude(
            status="completed"
        ).count(),

        # Existing dashboard data
        "projects": user_projects,
        "tasks": user_tasks,
        "search_query": search_query,
        "selected_status": selected_status,
        "selected_project": selected_project,
        "selected_due_date": selected_due_date,
        "activities": activities,

        # Progress analytics data
        "analytics_total": analytics_total,
        "analytics_completed": analytics_completed,
        "analytics_in_progress": analytics_in_progress,
        "analytics_todo": analytics_todo,
        "completion_percentage": completion_percentage,
        "overdue_count": overdue_count,
        "project_analytics": project_analytics,
    }

    return render(request, "dashboard.html", context)


@login_required
def create_project(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()

        if not name:
            messages.error(request, "Project name is required.")
            return redirect("create_project")

        Project.objects.create(
            name=name,
            description=description,
            owner=request.user
        )

        messages.success(request, "Project created successfully!")
        return redirect("dashboard")

    return render(request, "create_project.html")