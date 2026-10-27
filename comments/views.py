
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from tasks.models import Task
from comments.models import Comment
from projects.models import Project


@login_required
def task_comments(request, task_id):
    task = get_object_or_404(
        Task.objects.filter(project__members=request.user)
        | Task.objects.filter(project__owner=request.user)
        | Task.objects.filter(assigned_to=request.user),
        id=task_id
    )

    if request.method == "POST":
        content = request.POST.get("content", "").strip()

        if not content:
            messages.error(request, "Comment cannot be empty.")
        else:
            Comment.objects.create(
                task=task,
                author=request.user,
                content=content
            )
            messages.success(request, "Comment added successfully!")

        return redirect("task_comments", task_id=task.id)

    context = {
        "task": task,
        "comments": task.comments.select_related("author").order_by("-created_at"),
    }

    return render(request, "task_comments.html", context)