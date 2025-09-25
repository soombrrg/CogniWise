from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def send_verification_email(context: dict) -> None:
    subject = "Подтверждение регистрации"

    message = render_to_string("users/registration/verification_email.html", context)

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [context.get("email")],
        html_message=message,
    )


def secret_email_context_gen(request, user) -> dict:
    current_site = get_current_site(request)
    url_context = {
        "email": user.email,
        "domain": current_site.domain,
        "site_name": current_site.name,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": default_token_generator.make_token(user),
        "protocol": "https" if request.is_secure() else "http",
    }
    return url_context
