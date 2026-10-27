from django.urls import path

from accounts.views import (
    register,
    login_view,
    logout_view,
    profile,
    edit_profile,
    change_password,
)

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),

    # User Profile & Settings
    path("profile/", profile, name="profile"),
    path("profile/edit/", edit_profile, name="edit_profile"),
    path(
        "profile/change-password/",
        change_password,
        name="change_password",
    ),
]