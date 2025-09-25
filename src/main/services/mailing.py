from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_email_for_contact(data: dict) -> None:
    subject = "Пользователь хочет связаться"

    context = {
        "name": data.get("name"),
        "email": data.get("email"),
        "phone": data.get("phone"),
        "tg_username": data.get("tg_username"),
    }
    message = render_to_string("main/email_for_contact.html", context)

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [settings.DEFAULT_FROM_EMAIL],
        html_message=message,
    )
