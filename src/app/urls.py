from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("main.urls", namespace="main")),
    path("users/", include("users.urls", namespace="users")),
    path("admin/", admin.site.urls),
]
