from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


def register(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not username or not email or not password:
            messages.error(request, "Please fill in all fields.")
            return render(request, "register.html")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "register.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "register.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, "register.html")

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(
            request,
            "Account created successfully. Please login."
        )
        return redirect("login")

    return render(request, "register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("home")

        messages.error(request, "Invalid username or password.")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    messages.success(request, "You have logged out successfully.")
    return redirect("login")


# -----------------------------------
# USER PROFILE
# -----------------------------------

@login_required
def profile(request):
    return render(
        request,
        "profile.html",
        {"profile_user": request.user}
    )


# -----------------------------------
# EDIT PROFILE
# -----------------------------------

@login_required
def edit_profile(request):
    user = request.user

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()

        if not username or not email:
            messages.error(
                request,
                "Username and email are required."
            )
            return render(
                request,
                "edit_profile.html",
                {"profile_user": user}
            )

        if User.objects.filter(
            username=username
        ).exclude(pk=user.pk).exists():
            messages.error(request, "Username already exists.")
            return render(
                request,
                "edit_profile.html",
                {"profile_user": user}
            )

        if User.objects.filter(
            email=email
        ).exclude(pk=user.pk).exists():
            messages.error(request, "Email already registered.")
            return render(
                request,
                "edit_profile.html",
                {"profile_user": user}
            )

        user.username = username
        user.email = email
        user.save(update_fields=["username", "email"])

        messages.success(request, "Profile updated successfully!")
        return redirect("profile")

    return render(
        request,
        "edit_profile.html",
        {"profile_user": user}
    )


# -----------------------------------
# CHANGE PASSWORD
# -----------------------------------

@login_required
def change_password(request):
    if request.method == "POST":
        current_password = request.POST.get("current_password", "")
        new_password = request.POST.get("new_password", "")
        confirm_password = request.POST.get("confirm_password", "")

        user = request.user

        if not user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")

        elif new_password != confirm_password:
            messages.error(request, "New passwords do not match.")

        elif current_password == new_password:
            messages.error(
                request,
                "New password must be different from the current password."
            )

        else:
            try:
                validate_password(new_password, user=user)
            except ValidationError as errors:
                for error in errors.messages:
                    messages.error(request, error)
            else:
                user.set_password(new_password)
                user.save()

                # Keep the user logged in after password change
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, user)

                messages.success(
                    request,
                    "Password changed successfully!"
                )
                return redirect("profile")

    return render(request, "change_password.html")