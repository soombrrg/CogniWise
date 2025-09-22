from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django_resized import ResizedImageField

from users.validators import birthday_validator, phone_validator


class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError("Поле Email должно быть указанно")
        email = self.normalize_email(email)
        user = self.model(
            email=email, first_name=first_name, last_name=last_name, **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(
        self, email, first_name, last_name, password=None, **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("У суперпользователя должно быть: is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("У суперпользователя должно быть: is_superuser=True.")

        return self.create_user(email, first_name, last_name, password, **extra_fields)


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, max_length=30, verbose_name="Email")
    email_verified = models.BooleanField(
        default=False, verbose_name="Email подтвержден"
    )
    first_name = models.CharField(max_length=25, verbose_name="Имя")
    last_name = models.CharField(max_length=25, verbose_name="Фамилия")
    username = models.CharField(max_length=25, unique=True, null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        created = self.pk is None
        super().save(*args, **kwargs)
        if created:
            try:
                profile_exist = self.profile is not None
            except CustomUserProfile.DoesNotExist:
                CustomUserProfile.objects.create(user=self)


class CustomUserProfile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Пользователь",
    )
    avatar = ResizedImageField(
        size=[100, 100],
        crop=["middle", "center"],
        upload_to="avatars/",
        default="avatars/default_user.png",
        blank=True,
        null=True,
        verbose_name="Аватар",
    )
    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        validators=[phone_validator],
        verbose_name="Телефон",
    )
    birthday = models.DateField(
        null=True,
        blank=True,
        validators=[birthday_validator],
        verbose_name="День Рождения",
    )
    bio = models.TextField(
        max_length=250,
        null=True,
        blank=True,
        verbose_name="О себе",
    )

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return f"Профиль для: {self.user.email}"
