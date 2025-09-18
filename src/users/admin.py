from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import CustomUser, CustomUserProfile


class CustomUserProfileInline(admin.StackedInline):
    extra = 1
    max_num = 1
    model = CustomUserProfile
    fields = ("avatar", "phone", "birthday", "bio")


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    inlines = [CustomUserProfileInline]
    list_display = ("email", "email_verified", "first_name", "last_name", "is_staff")
    list_filter = (
        "is_staff",
        "is_superuser",
        "email_verified",
    )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "email_verified", "password")}),
        (
            "Personal info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_superuser",
                    "is_active",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )


admin.site.register(CustomUserProfile)
admin.site.register(CustomUser, CustomUserAdmin)
