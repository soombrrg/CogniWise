import json
import logging

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
from orders.services import (
    create_order,
    create_yookassa_payment,
    get_user_order_for_update,
    get_user_order_or_404,
    is_purchased,
)

formatter = logging.Formatter(
    fmt="[{asctime}] #{levelname:8} {filename}:" "{lineno} - {name} - {message}",
    style="{",
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(handler)

Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


@login_required
def checkout_view(request, course_id):
    """View for course buying"""
    course = get_object_or_404(Course, id=course_id)

    # Check if user already bought course
    if is_purchased(request.user, course.id):
        return redirect("main:course-detail", course_id=course.id)

    course_price = course.price
    if request.method == "POST":
        try:
            order = create_order(request.user, course, course_price, "pending")

            payment = create_yookassa_payment(order, request)
            return redirect(payment.confirmation.confirmation_url)

        except Exception as e:
            logger.error("Ошибка создания платежа: %s", str(e))
            order.delete()
            messages.error(request, "Ошибка обработки платежа.")
            return render(
                request,
                "orders/checkout.html",
                {"course": course, "total_price": course_price},
            )
    return render(
        request,
        "orders/checkout.html",
        {"course": course, "total_price": course_price},
    )


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
            "Обработка event ЮKassa: %s | Payment ID: %s", event_type, payment_id
        )

        metadata = payment.get("metadata", {})
        order_id = metadata.get("order_id")
        user_id = metadata.get("user_id")

        if not all([order_id, user_id]):
            logger.error(
                "Отсутствуют метаданные: order_id=%s, user_id=%s", order_id, user_id
            )
            return HttpResponseBadRequest("Отсутствуют необходимые метаданные")

        order = get_user_order_for_update(user_id, order_id)

        # Check if order already handled
        if order.status in ["completed", "cancelled"]:
            logger.info(
                "Заказ %s уже имеет финальный статус: %s", order_id, order.status
            )
            return HttpResponse(status=200)

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


@login_required
def yookassa_payment_status_view(request):
    """Success payment page, only for current user"""
    order_id = request.GET.get("order_id")
    if order_id is None:
        return redirect("main:home")

    order = get_user_order_or_404(order_id, request.user)

    if order.status == "completed":
        messages.success(request, "Оплата прошла успешно! Доступ к курсу открыт.")
        return render(request, "orders/yookassa_success.html", {"order": order})
    elif order.status == "canceled":
        messages.error(request, "Платеж был отменен.")
        return render(request, "orders/yookassa_cancel.html", {"order": order})

    if order.yookassa_payment_id is None:
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
            messages.error(request, "Платеж был отменен.")
            return render(request, "orders/yookassa_cancel.html", {"order": order})
    except Exception as e:
        logger.error("Ошибка проверки платежа ЮKassa: %s", str(e))
