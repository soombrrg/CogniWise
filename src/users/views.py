from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render

from orders.models import Order
from users.forms import (
    CustomUserCreationForm,
    CustomUserLoginForm,
    CustomUserPasswordChangeForm,
    CustomUserUpdateForm,
)
from users.models import CustomUser


def register_view(request):
    if request.user.is_authenticated:
        return redirect("users:profile")
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            messages.success(request, "Регистрация прошла успешно!")
            return redirect("users:profile")
        else:
            messages.error(request, "Пожалуйста исправьте ошибки в форме.")
    else:
        form = CustomUserCreationForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("users:profile")
    if request.method == "POST":
        form = CustomUserLoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            messages.success(request, "Вход успешно выполнен!")
            return redirect("users:profile")
        else:
            messages.error(request, "Неверный email или пароль")
    else:
        form = CustomUserLoginForm()
    return render(request, "users/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Вы вышли из аккаунта.")
    return redirect("main:home")


@login_required
def profile_view(request):
    purchased_courses = [
        order.course
        for order in Order.objects.filter(user=request.user, status="completed")
    ]
    return render(
        request,
        "users/profile.html",
        {"user": request.user, "purchased_courses": purchased_courses},
    )


@login_required
def change_password(request):
    if request.method == "POST":
        form = CustomUserPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Пароль успешно обновлен!", extra_tags="success")
            return render(
                request,
                "users/partials/change_password.html",
                {"user": user, "form": form},
            )
        else:
            messages.error(
                request, "Пожалуйста, исправьте ошибки.", extra_tags="danger"
            )
    else:
        form = CustomUserPasswordChangeForm(user=request.user)
    return render(
        request,
        "users/partials/change_password.html",
        {"user": request.user, "form": form},
    )


@login_required
def account_details_view(request):
    user = CustomUser.objects.get(id=request.user.id)
    return render(request, "users/partials/account_details.html", {"user": user})


@login_required
def edit_account_details_view(request):
    form = CustomUserUpdateForm(instance=request.user)
    return render(
        request,
        "users/partials/edit_account_details.html",
        {"user": request.user, "form": form},
    )


@login_required
def update_account_details_view(request):
    if request.method == "POST":
        form = CustomUserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Данные профиля обновлены!", extra_tags="success")
            return render(
                request,
                "users/partials/update_success.html",
                {"user": user, "form": form},
            )
        else:
            messages.error(
                request, "Пожалуйста, исправьте ошибки в форме.", extra_tags="danger"
            )
    else:
        form = CustomUserUpdateForm(instance=request.user)
    return render(
        request,
        "users/partials/edit_account_details.html",
        {"user": request.user, "form": form},
    )
