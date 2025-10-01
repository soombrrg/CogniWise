from django.urls import path

from orders.views import (
    checkout_view,
    yookassa_payment_status_view,
    yookassa_webhook,
)

app_name = "orders"

urlpatterns = [
    path("checkout/<int:course_id>/", checkout_view, name="checkout"),
    path("yookassa/webhook/", yookassa_webhook, name="yookassa_webhook"),
    path("yookassa/success/", yookassa_payment_status_view, name="yookassa_success"),
    path("yookassa/cancel/", yookassa_payment_status_view, name="yookassa_cancel"),
]
