from unittest.mock import Mock, patch

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertTemplateUsed

from orders.models import Order

pytestmark = [pytest.mark.django_db]


class TestCheckoutView:
    def test_login_required(self, app, course):
        """Test login redirect, on unauthenticated user"""
        response = app.get(
            reverse("orders:checkout", args=[course.id]),
            expected_status_code=302,
        )
        redirect_url = reverse("users:login") + f"?next=/orders/checkout/{course.id}/"

        assertRedirects(response, redirect_url)

    def test_no_course(self, app, auth_user):
        """Test 404 when no course is found"""
        response = app.get(
            reverse("orders:checkout", args=[1]),
            expected_status_code=404,
        )

    @patch("orders.views.is_purchased")
    def test_redirect_if_purchased(self, mock_is_purchased, app, auth_user, course):
        """Test redirection for already purchased course"""
        mock_is_purchased.return_value = True
        response = app.get(
            reverse("orders:checkout", args=[course.id]),
            expected_status_code=302,
        )

        assert response.url == reverse("main:course-detail", args=[course.id])

    def test_get(self, app, auth_user, course):
        """Test GET request"""
        response = app.get(
            reverse("orders:checkout", args=[course.id]),
        )
        assert response.context["course"] == course
        assert response.context["total_price"] == course.price
        assertTemplateUsed(response, "orders/checkout.html")

    @patch("orders.views.create_yookassa_payment")
    def test_post_fail(self, mock_create_yookassa_payment, app, auth_user, course):
        """Test POST request with invalid data"""
        mock_create_yookassa_payment.side_effect = Exception()
        response = app.post(
            reverse("orders:checkout", args=[course.id]),
        )

        mock_create_yookassa_payment.assert_called_once()
        assert response.context["course"] == course
        assert response.context["total_price"] == course.price
        assert auth_user.orders.first() is None
        assertTemplateUsed(response, "orders/checkout.html")

    @patch("orders.views.create_yookassa_payment")
    def test_post_success(self, mock_create_yookassa_payment, app, auth_user, course):
        """Test POST request with valid data"""
        mock_confirmation = Mock()
        mock_confirmation.confirmation_url = (
            reverse("orders:yookassa_success") + "?order_id=1"
        )
        mock_payment = Mock()
        mock_payment.confirmation = mock_confirmation
        mock_create_yookassa_payment.return_value = mock_payment

        response = app.post(
            reverse("orders:checkout", args=[course.id]), expected_status_code=302
        )

        mock_create_yookassa_payment.assert_called_once()
        assert auth_user.orders.first() is not None
        assert auth_user.orders.first().course == course
        assert response.url == mock_payment.confirmation.confirmation_url


@pytest.mark.parametrize("part", ["success", "cancel"])
class TestYookassaPaymentStatusView:
    def test_login_required(self, app, part):
        """Test login redirect, on unauthenticated user"""
        response = app.get(
            reverse(f"orders:yookassa_{part}") + "?order_id=1",
            expected_status_code=302,
        )
        assertRedirects(
            response,
            reverse("users:login") + f"?next=/orders/yookassa/{part}/?order_id=1",
        )

    @pytest.mark.parametrize("order_id, status_code", [(1, 404), (None, 302)])
    def test_no_order_or_order_id_provided(
        self, part, order_id, status_code, app, auth_user
    ):
        """Test view when no order or order id provided"""
        query = f"?order_id={order_id}" if order_id else ""
        response = app.get(
            reverse(f"orders:yookassa_{part}") + query,
            expected_status_code=status_code,
        )
        if order_id is None:
            assertRedirects(response, reverse("main:home"))

    @pytest.mark.parametrize("status", ["completed", "canceled"])
    def test_order_status(self, part, status, mixer, app, auth_user, course):
        """Test order already handled, using different status"""
        order = mixer.blend(
            "orders.Order", course=course, user=auth_user, status=status
        )
        response = app.get(
            reverse(f"orders:yookassa_{part}") + f"?order_id={order.id}",
        )

        assert response.context["order"] == order
        if status == "completed":
            assertTemplateUsed(response, "orders/yookassa_success.html")
        if status == "canceled":
            assertTemplateUsed(response, "orders/yookassa_cancel.html")

    def test_order_no_payment_id(self, part, mixer, app, auth_user, course):
        """Test no payment id for order provided"""
        order = mixer.blend(
            "orders.Order", course=course, user=auth_user, yookassa_payment_id=None
        )
        response = app.get(reverse(f"orders:yookassa_{part}") + f"?order_id={order.id}")

        assert order.yookassa_payment_id is None
        assert response.context["order"] == order
        assertTemplateUsed(response, "orders/yookassa_pending.html")

    @pytest.mark.parametrize(
        "payment_status",
        ["canceled", "failed", "succeeded"],
    )
    @patch("orders.views.Payment.find_one")
    def test_diff_payment_status(
        self,
        mock_find_one,
        part,
        payment_status,
        mixer,
        app,
        auth_user,
        course,
    ):
        """Test render on Order info on payment_status, using different payment status"""
        mock_payment = Mock()
        mock_payment.status = payment_status
        mock_find_one.return_value = mock_payment

        order = mixer.blend(
            "orders.Order", course=course, user=auth_user, yookassa_payment_id=1
        )
        response = app.get(reverse(f"orders:yookassa_{part}") + f"?order_id={order.id}")
        if payment_status == "succeeded":
            assert response.context["order"] == order
            assert Order.objects.get(id=order.id).status == "completed"
            assertTemplateUsed(response, "orders/yookassa_success.html")
        if payment_status in ["canceled", "failed"]:
            assert response.context["order"] == order
            assert Order.objects.get(id=order.id).status == "canceled"
            assertTemplateUsed(response, "orders/yookassa_cancel.html")
