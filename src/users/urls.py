from django.urls import path

from users.views import (
    account_details_view,
    change_password,
    edit_account_details_view,
    login_view,
    logout_view,
    profile_view,
    register_view,
    update_account_details_view,
)

app_name = "users"

urlpatterns = [
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("profile/", profile_view, name="profile"),
    path("change-password/", change_password, name="change-password"),
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
