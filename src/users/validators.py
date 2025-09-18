import datetime

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

phone_validator = RegexValidator(
    regex=r"^\+?1?\d{8,15}$",
    message="Номер должен быть формата: '+999999999'",
)


def birthday_validator(value):
    if value and value > datetime.date.today():
        raise ValidationError("Invalid date of birth")
