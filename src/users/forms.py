import datetime
import re

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    UserCreationForm,
    PasswordResetForm,
    SetPasswordForm,
)

from app.forms import base_form_class

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        max_length=30,
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": base_form_class,
                "placeholder": "your@email.com",
            }
        ),
    )
    first_name = forms.CharField(
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
    last_name = forms.CharField(
        required=True,
        max_length=25,
        label="Фамилия",
        widget=forms.TextInput(
            attrs={
                "class": base_form_class,
                "placeholder": "Ваша фамилия",
            }
        ),
    )
    password1 = forms.CharField(
        required=True,
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={
                "class": base_form_class,
                "placeholder": "Ваш пароль",
            }
        ),
    )
    password2 = forms.CharField(
        required=True,
        label="Подтверждение пароля",
        widget=forms.PasswordInput(
            attrs={
                "class": base_form_class,
                "placeholder": "Подтвердите пароль",
            }
        ),
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Этот email уже используется.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = None
        if commit:
            user.save()
        return user


class CustomUserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Email",
        widget=forms.TextInput(
            attrs={
                "autofocus": True,
                "class": base_form_class,
                "placeholder": "your@email.com",
            }
        ),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={
                "class": base_form_class,
                "placeholder": "Ваш пароль",
            }
        ),
    )

    def clean(self):
        email = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if email and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError("Неверный email или пароль.")
            elif not self.user_cache.is_active:
                raise forms.ValidationError("Этот аккаунт неактивен.")
        return self.cleaned_data


class CustomUserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
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
    last_name = forms.CharField(
        required=True,
        max_length=25,
        label="Фамилия",
        widget=forms.TextInput(
            attrs={
                "class": base_form_class,
                "placeholder": "Ваша фамилия",
            }
        ),
    )
    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": base_form_class,
                "placeholder": "your@email.com",
            }
        ),
    )
    phone = forms.CharField(
        required=False,
        max_length=20,
        label="Телефон",
        widget=forms.TelInput(
            attrs={
                "class": base_form_class,
                "placeholder": "+99999999999",
            }
        ),
    )

    birthday = forms.DateField(
        required=False,
        label="Дата рождения",
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={
                "type": "date",
                "class": base_form_class,
            },
        ),
    )

    bio = forms.CharField(
        required=False,
        label="О себе",
        widget=forms.Textarea(
            attrs={
                "rows": "3",
                "class": base_form_class + " resize-none",
                "placeholder": "Расскажите немного о себе...",
            }
        ),
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "birthday", "phone", "bio")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if (
            email
            and User.objects.filter(email=email).exclude(id=self.instance.id).exists()
        ):
            raise forms.ValidationError("Этот email уже используется.")
        return email

    def clean_birthdate(self):
        birthdate = self.cleaned_data.get("birthdate")
        if birthdate and birthdate > datetime.date.today():
            raise forms.ValidationError("Дата рождения не может быть в будущем")
        return birthdate

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone and not re.match(r"^\+?1?\d{8,15}$", phone.replace(" ", "")):
            raise forms.ValidationError("Номер формата: +99999999999")
        return phone

    def clean_bio(self):
        bio = self.cleaned_data.get("bio")
        if bio and len(bio) > 250:
            raise forms.ValidationError("Максимум 250 символов")
        return bio


class CustomUserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Текущий пароль",
        widget=forms.PasswordInput(
            attrs={
                "class": base_form_class,
                "placeholder": "Текущий пароль",
            }
        ),
    )
    new_password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(
            attrs={
                "class": base_form_class,
                "placeholder": "Новый пароль",
            }
        ),
    )
    new_password2 = forms.CharField(
        label="Подтверждение нового пароля",
        widget=forms.PasswordInput(
            attrs={
                "class": base_form_class,
                "placeholder": "Подтвердите новый пароль",
            }
        ),
    )

    class Meta:
        model = User
        fields = ("old_password", "new_password1", "new_password2")


class CustomUserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label="Email",
        max_length=30,
        widget=forms.EmailInput(
            attrs={
                "autocomplete": "email",
                "class": base_form_class,
                "placeholder": "your@email.com",
            }
        ),
    )


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="Новый пароль",
        required=True,
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                "class": base_form_class,
                "placeholder": "Новый пароль",
            }
        ),
    )
    new_password2 = forms.CharField(
        label="Повторите новый пароль",
        required=True,
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                "class": base_form_class,
                "placeholder": "Повторите новый пароль",
            }
        ),
    )
