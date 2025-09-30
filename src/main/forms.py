import re

from django import forms

from app.forms import base_form_class


class EmailForContactForm(forms.Form):
    name = forms.CharField(
        required=True,
        max_length=25,
        label="Имя",
        widget=forms.TextInput(
            attrs={
                "class": base_form_class,
                "placeholder": "Ваше имя",
            }
        ),
    )
    email = forms.EmailField(
        required=True,
        max_length=30,
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": base_form_class,
                "placeholder": "example@mail.ru",
            }
        ),
    )
    phone = forms.CharField(
        required=True,
        max_length=20,
        label="Телефон",
        widget=forms.TelInput(
            attrs={
                "class": base_form_class,
                "placeholder": "+99999999999",
            }
        ),
    )
    tg_username = forms.CharField(
        required=True,
        max_length=30,
        label="Ник в Telegram",
        widget=forms.TextInput(
            attrs={
                "class": base_form_class,
                "placeholder": "@telegramnik",
            },
        ),
    )

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if not re.match(r"^\+?1?\d{8,15}$", phone.replace(" ", "")):
            raise forms.ValidationError("Номер формата: +99999999999")
        return phone

    def clean_tg_username(self):
        tg_username = self.cleaned_data.get("tg_username")
        if tg_username.replace(" ", "")[0] != "@":
            raise forms.ValidationError("Нехватает @")
        return tg_username
