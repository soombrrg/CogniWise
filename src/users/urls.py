from django.contrib.auth.views import (
    PasswordResetCompleteView,
    PasswordResetDoneView,
)
from django.urls import path

from users.views import (
    CustomPasswordResetConfirmView,
    CustomPasswordResetView,
    account_details_view,
    edit_account_details_view,
    email_verification_view,
    login_view,
    logout_view,
    password_change_view,
    profile_view,
    register_view,
    update_account_details_view,
)

app_name = "users"

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
]

# Profile
urlpatterns += [
    path("profile/", profile_view, name="profile"),
    path("password-change/", password_change_view, name="password_change"),
    path("account-details/", account_details_view, name="account-details"),
    path(
        "edit-account-details/",
        edit_account_details_view,
        name="edit-account-details",
    ),
    path(
        "update-account-details/",
        update_account_details_view,
        name="update-account-details",
    ),
]

# Registration
urlpatterns += [
    path("register/", register_view, name="register"),
    path(
        "register/<uidb64>/<token>/", email_verification_view, name="email_verification"
    ),
]

# Password Resetting
urlpatterns += [
    path(
        "password-reset/",
        CustomPasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        PasswordResetDoneView.as_view(
            template_name="users/password/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset/<uidb64>/<token>/",
        CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        PasswordResetCompleteView.as_view(
            template_name="users/password/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
]
