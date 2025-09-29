from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("main.urls", namespace="main")),
    path("users/", include("users.urls", namespace="users")),
    path("orders/", include("orders.urls", namespace="orders")),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
