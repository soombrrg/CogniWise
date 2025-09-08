from django.urls import path

from orders.views import checkout, yookassa_webhook, yookassa_success, yookassa_cancel

app_name = "orders"

urlpatterns = [
    path("checkout/<int:course_id>/", checkout, name="checkout"),
    path("yookassa/webhook/", yookassa_webhook, name="yookassa_webhook"),
    path("yookassa/success/", yookassa_success, name="yookassa_success"),
    path("yookassa/cancel/", yookassa_cancel, name="yookassa_cancel"),
]
