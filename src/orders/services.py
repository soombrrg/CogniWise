import logging
from uuid import uuid4

from django.conf import settings
from django.core.cache import cache
from django.http import Http404
from django.shortcuts import get_object_or_404
from yookassa import Payment

from orders.models import Order

formatter = logging.Formatter(
    fmt="[{asctime}] #{levelname:8} {filename}:" "{lineno} - {name} - {message}",
    style="{",
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(handler)


def is_purchased(user, course_id) -> bool:
    """Check if course is purchased or not, using cache"""
    cache_key = f"purchase_status_{user.id}_{course_id}"
    purchase_status = cache.get(cache_key)

    # if not in cache
    if purchase_status is None:
        purchase_status = Order.objects.filter(
            user=user, course__id=course_id, status="completed"
        ).exists()
        cache.set(cache_key, purchase_status, 1800)
    return purchase_status


def create_order(user, course, price, status) -> Order:
    order = Order.objects.create(
        user=user,
        course=course,
        total_price=price,
        status=status,
    )
    return order


def get_user_order_or_404(order_id, user):
    order = get_object_or_404(Order, id=order_id)
    if order.user != user:
        raise Http404("Заказ не найден")
    return order


def get_user_order_for_update(order_id, user_id):
    order = Order.objects.select_for_update().get(id=order_id, user_id=user_id)
    return order


def create_yookassa_payment(request, order):
    receipt_items = [
        {
            "description": f"Курс: {order.course.title}",
            "quantity": "1",
            "amount": {
                "value": f"{order.total_price:.2f}",
                "currency": "RUB",
            },
            "vat_code": getattr(settings, "YOOKASSA_VAT_CODE", 1),
            "payment_mode": "full_payment",
            "payment_subject": "commodity",
        }
    ]
    customer = {"email": order.user.email}
    discounted_total_rub = order.get_discounted_total_price()

    try:
        idempotence_key = str(uuid4())
        payment = Payment.create(
            {
                "amount": {
                    "value": f"{discounted_total_rub:.2f}",
                    "currency": "RUB",
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": request.build_absolute_uri(
                        "/orders/yookassa/success/"
                    )
                    + f"?order_id={order.id}",
                },
                "capture": True,
                "description": f"Заказ #{order.id}",
                "metadata": {
                    "order_id": order.id,
                    "user_id": order.user.id,
                },
                "receipt": {
                    "customer": customer,
                    "items": receipt_items,
                },
            },
            idempotence_key,
        )

        order.yookassa_payment_id = payment.id
        order.save()
        return payment
    except Exception as e:
        logger.error("Ошибка при создании платежа ЮKassa: %s", str(e))
        raise
