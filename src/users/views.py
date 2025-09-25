from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    PasswordResetConfirmView,
    PasswordResetView,
)
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from users.forms import (
    CustomSetPasswordForm,
    CustomUserCreationForm,
    CustomUserLoginForm,
    CustomUserPasswordChangeForm,
    CustomUserPasswordResetForm,
    CustomUserProfileUpdateForm,
    CustomUserUpdateForm,
)
from users.services.check import is_verified_by_token
from users.services.fetching import (
    get_profile_by_user,
    get_user_by_uidb64,
    get_user_profile_data,
)
from users.services.mailing import secret_email_context_gen, send_verification_email


def register_view(request):
    if request.user.is_authenticated:
        return redirect("users:profile")
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            context = secret_email_context_gen(request, user)
            send_verification_email(context)
            return render(
                request,
                "users/registration/verification_sent.html",
                {"email": user.email},
            )
        else:
            messages.error(request, "Пожалуйста исправьте ошибки в форме.")
    else:
        form = CustomUserCreationForm()
    return render(request, "users/register.html", {"form": form})


def email_verification_view(request, uidb64, token):
    user = get_user_by_uidb64(uidb64)
    if is_verified_by_token(user, token):
        user.is_active = True
        user.email_verified = True
        user.save()
        messages.success(request, "Регистрация прошла успешно!")
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        return redirect("users:profile")
    return render(request, "users/registration/verification_failed.html")


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
    user_profile_data = get_user_profile_data(request.user)
    return render(
        request,
        "users/profile.html",
        {"user": request.user, **user_profile_data},
    )


@login_required
def profile_partial_view(request):
    user_profile_data = get_user_profile_data(request.user)
    return render(
        request,
        "users/partials/profile_partial.html",
        {"user": request.user, **user_profile_data},
    )


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomUserPasswordResetForm
    template_name = "users/password/password_reset_form.html"
    email_template_name = "users/password/password_reset_email.html"
    subject_template_name = "users/password/password_reset_subject.txt"
    success_url = reverse_lazy("users:password_reset_done")


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy("users:password_reset_complete")
    template_name = "users/password/password_reset_confirm.html"


@login_required
def password_change_view(request):
    if request.method == "POST":
        form = CustomUserPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Пароль успешно обновлен!", extra_tags="success")
            return render(
                request,
                "users/partials/password_change.html",
                {"user": user, "form": form},
            )
        messages.error(request, "Пожалуйста, исправьте ошибки.", extra_tags="danger")
    else:
        form = CustomUserPasswordChangeForm(user=request.user)
    return render(
        request,
        "users/partials/password_change.html",
        {"user": request.user, "form": form},
    )


@login_required
def edit_account_details_view(request):
    profile = get_profile_by_user(request.user)

    if request.method == "POST":
        user_form = CustomUserUpdateForm(request.POST, instance=request.user)
        profile_form = CustomUserProfileUpdateForm(
            request.POST, request.FILES, instance=profile
        )
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, "Данные профиля обновлены!", extra_tags="success")
            return redirect("users:profile")
        else:
            messages.error(
                request, "Пожалуйста, исправьте ошибки в форме.", extra_tags="danger"
            )
    else:
        user_form = CustomUserUpdateForm(instance=request.user)
        profile_form = CustomUserProfileUpdateForm(instance=profile)
    return render(
        request,
        "users/partials/edit_account_details.html",
        {"user": request.user, "user_form": user_form, "profile_form": profile_form},
    )
