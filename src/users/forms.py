from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordChangeForm,
)
from django.contrib.auth import get_user_model, authenticate

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        max_length=66,
        label="Электронная почта",
        widget=forms.EmailInput(
            attrs={
                "class": "w-full px-4 py-3 bg-slate-800/50 border border-slate-600 rounded-lg text-slate-200 "
                "placeholder-slate-400 focus:outline-none focus:border-emerald-400 focus:ring-1 "
                "focus:ring-emerald-400 transition duration-300 soft-neon-border",
                "placeholder": "Ваш email",
            }
        ),
    )
    first_name = forms.CharField(
        required=True,
        max_length=66,
        label="Имя",
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-3 bg-slate-800/50 border border-slate-600 rounded-lg text-slate-200 "
                "placeholder-slate-400 focus:outline-none focus:border-emerald-400 focus:ring-1 "
                "focus:ring-emerald-400 transition duration-300 soft-neon-border",
                "placeholder": "Ваше имя",
            }
        ),
    )
    last_name = forms.CharField(
        required=True,
        max_length=66,
        label="Фамилия",
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-3 bg-slate-800/50 border border-slate-600 rounded-lg text-slate-200 "
                "placeholder-slate-400 focus:outline-none focus:border-emerald-400 focus:ring-1 "
                "focus:ring-emerald-400 transition duration-300 soft-neon-border",
                "placeholder": "Ваша фамилия",
            }
        ),
    )
    password1 = forms.CharField(
        required=True,
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-4 py-3 bg-slate-800/50 border border-slate-600 rounded-lg text-slate-200 "
                "placeholder-slate-400 focus:outline-none focus:border-emerald-400 focus:ring-1 "
                "focus:ring-emerald-400 transition duration-300 soft-neon-border",
                "placeholder": "Ваш пароль",
            }
        ),
    )
    password2 = forms.CharField(
        required=True,
        label="Подтверждение пароля",
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-4 py-3 bg-slate-800/50 border border-slate-600 rounded-lg text-slate-200 "
                "placeholder-slate-400 focus:outline-none focus:border-emerald-400 focus:ring-1 "
                "focus:ring-emerald-400 transition duration-300 soft-neon-border",
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
                "class": "w-full px-4 py-3 bg-slate-800/50 border border-slate-600 rounded-lg text-slate-200 "
                "placeholder-slate-400 focus:outline-none focus:border-emerald-400 focus:ring-1 "
                "focus:ring-emerald-400 transition duration-300 soft-neon-border",
                "placeholder": "Ваш email",
            }
        ),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-4 py-3 bg-slate-800/50 border border-slate-600 rounded-lg text-slate-200 "
                "placeholder-slate-400 focus:outline-none focus:border-emerald-400 focus:ring-1 "
                "focus:ring-emerald-400 transition duration-300 soft-neon-border",
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
        max_length=66,
        label="Имя",
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-3 bg-slate-800/50 border border-slate-600 rounded-lg text-slate-200 "
                "placeholder-slate-400 focus:outline-none focus:border-emerald-400 focus:ring-1 "
                "focus:ring-emerald-400 transition duration-300 soft-neon-border",
                "placeholder": "Ваше имя",
            }
        ),
    )
    last_name = forms.CharField(
        required=True,
        max_length=66,
        label="Фамилия",
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-3 bg-slate-800/50 border border-slate-600 rounded-lg text-slate-200 "
                "placeholder-slate-400 focus:outline-none focus:border-emerald-400 focus:ring-1 "
                "focus:ring-emerald-400 transition duration-300 soft-neon-border",
                "placeholder": "Ваша фамилия",
            }
        ),
    )
    email = forms.EmailField(
        required=True,
        label="Электронная почта",
        widget=forms.EmailInput(
            attrs={
                "class": "w-full px-4 py-3 bg-slate-800/50 border border-slate-600 rounded-lg text-slate-200 "
                "placeholder-slate-400 focus:outline-none focus:border-emerald-400 focus:ring-1 "
                "focus:ring-emerald-400 transition duration-300 soft-neon-border",
                "placeholder": "Ваш email",
            }
        ),
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if (
            email
            and User.objects.filter(email=email).exclude(id=self.instance.id).exists()
        ):
            raise forms.ValidationError("Этот email уже используется.")
        return email


class CustomUserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Current password",
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-4 py-3 bg-slate-800/50 border border-slate-600 rounded-lg text-slate-200 placeholder-slate-400 focus:outline-none focus:border-emerald-400 focus:ring-1 focus:ring-emerald-400 transition duration-300 soft-neon-border",
                "placeholder": "Текущий пароль",
            }
        ),
    )
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-4 py-3 bg-slate-800/50 border border-slate-600 rounded-lg text-slate-200 placeholder-slate-400 focus:outline-none focus:border-emerald-400 focus:ring-1 focus:ring-emerald-400 transition duration-300 soft-neon-border",
                "placeholder": "Новый пароль",
            }
        ),
    )
    new_password2 = forms.CharField(
        label="New password (repeat)",
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-4 py-3 bg-slate-800/50 border border-slate-600 rounded-lg text-slate-200 placeholder-slate-400 focus:outline-none focus:border-emerald-400 focus:ring-1 focus:ring-emerald-400 transition duration-300 soft-neon-border",
                "placeholder": "Повторите новый пароль",
            }
        ),
    )
