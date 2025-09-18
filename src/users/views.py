from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import (
    PasswordResetConfirmView,
    PasswordResetView,
)
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from orders.models import Order
from users.forms import (
    CustomSetPasswordForm,
    CustomUserCreationForm,
    CustomUserLoginForm,
    CustomUserPasswordChangeForm,
    CustomUserPasswordResetForm,
    CustomUserUpdateForm,
)
from users.models import CustomUser


def register_view(request):
    if request.user.is_authenticated:
        return redirect("users:profile")
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            send_verification_email(request, user)
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


def send_verification_email(request, user):
    subject = "Подтверждение регистрации"
    current_site = get_current_site(request)
    user_email = user.email

    context = {
        "user": user,
        "email": user_email,
        "domain": current_site.domain,
        "site_name": current_site.name,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": default_token_generator.make_token(user),
        "protocol": "https" if request.is_secure() else "http",
    }

    message = render_to_string("users/registration/verification_email.html", context)

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        html_message=message,
    )


def email_verification_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.email_verified = True
        user.save()
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        messages.success(request, "Регистрация прошла успешно!")
        return redirect("users:profile")
    else:
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
    purchased_courses = [
        order.course
        for order in Order.objects.filter(user=request.user, status="completed")
    ]
    return render(
        request,
        "users/profile.html",
        {"user": request.user, "purchased_courses": purchased_courses},
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
        else:
            messages.error(
                request, "Пожалуйста, исправьте ошибки.", extra_tags="danger"
            )
    else:
        form = CustomUserPasswordChangeForm(user=request.user)
    return render(
        request,
        "users/partials/password_change.html",
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
