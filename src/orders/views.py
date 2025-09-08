import json
import logging
from uuid import uuid4

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from yookassa import Configuration, Payment

from main.models import Course
from orders.models import Order

logger = logging.getLogger(__name__)
Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


@login_required
def checkout(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Check if user already bought course
    if Order.objects.filter(
        user=request.user,
        course=course,
        status="completed",
    ).exists():
        messages.info(request, "Вы уже приобрели этот курс!")
        return redirect("main:course_detail", course_id=course.id)

    course_price = course.price
    if request.method != "POST":
        return render(
            request,
            "orders/checkout.html",
            {"course": course, "total_price": course_price},
        )
    try:
        order = Order.objects.create(
            user=request.user,
            course=course,
            total_price=course_price,
            status="pending",
        )

        payment = create_yookassa_payment(order, request)
        return redirect(payment.confirmation.confirmation_url)

    except Exception as e:
        logger.error("Ошибка создания платежа: %s", str(e))
        order.delete()
        messages.error(request, f"Ошибка обработки платежа: {str(e)}")
        return render(
            request,
            "orders/checkout.html",
            {"course": course, "total_price": course_price},
        )


def create_yookassa_payment(order, request):
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
        # Generating key for idempotence
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
        logger.error("Ошибка создания платежа ЮKassa: %s", str(e))
        raise


@csrf_exempt
@require_POST
def yookassa_webhook(request):
    if request.method != "POST":
        logger.warning(f"Недопустимый метод запроса: {request.method}")
        return HttpResponseNotAllowed(["POST"])

    logger.info(
        f"ЮKassa webhook получен | IP: {request.META['REMOTE_ADDR']} | User-Agent: {request.META['HTTP_USER_AGENT']}"
    )

    try:
        raw_body = request.body.decode("utf-8")
        event_json = json.loads(raw_body)
        event_type = event_json.get("type")
        payment = event_json.get("object", {})
        payment_id = payment.get("id")

        logger.info(
            "Обработка события ЮKassa: %s | Payment ID: %s", event_type, payment_id
        )

        metadata = payment.get("metadata", {})
        order_id = metadata.get("order_id")
        user_id = metadata.get("user_id")

        if not all([order_id, user_id]):
            logger.error(
                "Отсутствуют метаданные: order_id=%s, user_id=%s", order_id, user_id
            )
            return HttpResponseBadRequest("Отсутствуют необходимые метаданные")

        order = Order.objects.select_for_update().get(id=order_id, user_id=user_id)

        if event_type == "payment.succeeded":
            if payment.get("status") == "succeeded":
                if order.status != "completed":
                    order.status = "completed"
                    order.yookassa_payment_id = payment_id
                    order.save()
                    logger.info("Заказ %s успешно обработан", order_id)
                logger.info("Заказ %s уже обработан, пропускаем", order_id)

        elif event_type == "payment.canceled":
            if payment.get("status") == "canceled":
                if order.status != "canceled":
                    order.status = "canceled"
                    order.save()
                    logger.info("Заказ %s помечен как отменен", order_id)
                logger.info("Заказ %s уже отменен, пропускаем", order_id)

        return HttpResponse(status=200)
    except json.JSONDecodeError as e:
        logger.error("Ошибка декодирования JSON: %s", str(e))
        return HttpResponseBadRequest("Неверный JSON")
    except Order.DoesNotExist:
        logger.error("Заказ не найден: order_id=%s, user_id=%s", order_id, user_id)
        return HttpResponseBadRequest("Заказ не найден")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {str(e)}")
        return HttpResponse(status=500)


def yookassa_success(request):
    order_id = request.GET.get("order_id")
    if not order_id:
        return redirect("main:home")

    order = get_object_or_404(Order, id=order_id)

    if order.status == "completed":
        messages.success(request, "Оплата прошла успешно! Доступ к курсу открыт.")
        return render(request, "orders/yookassa_success.html", {"order": order})
    elif order.status == "canceled":
        return redirect("orders:yookassa_cancel")

    if not order.yookassa_payment_id:
        return render(request, "orders/yookassa_pending.html", {"order": order})

    try:
        payment = Payment.find_one(order.yookassa_payment_id)
        if payment.status == "succeeded":
            order.status = "completed"
            order.save()
            messages.success(request, "Оплата прошла успешно! Доступ к курсу открыт.")
            return render(request, "orders/yookassa_success.html", {"order": order})
        elif payment.status in ["canceled", "failed"]:
            order.status = "canceled"
            order.save()
            return redirect("orders:yookassa_cancel")
    except Exception as e:
        logger.error("Ошибка проверки платежа ЮKassa: %s", str(e))


def yookassa_cancel(request):
    order_id = request.GET.get("order_id")
    if not order_id:
        return redirect("orders: checkout")

    order = get_object_or_404(Order, id=order_id)
    order.status = "canceled"
    order.save()
    messages.error(request, "Платеж был отменен.")
    return render(request, "orders/yookassa_cancel.html", {"order": order})
