from unittest.mock import patch

import pytest
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from pytest_django.asserts import assertRedirects, assertTemplateUsed

from conftest import mixer
from users.forms import (
    CustomUserCreationForm,
    CustomUserLoginForm,
    CustomUserPasswordChangeForm,
    CustomUserProfileUpdateForm,
    CustomUserUpdateForm,
)
from users.models import CustomUser

pytestmark = [pytest.mark.django_db]


class TestRegisterView:
    def test_user_authenticated(self, app, auth_user):
        """Test redirection when user already authenticated"""
        response = app.get(reverse("users:register"), expected_status_code=302)
        assertRedirects(response, reverse("users:profile"))

    def test_get(self, app):
        """Test rendering form on GET"""
        response = app.get(reverse("users:register"))
        assert isinstance(response.context["form"], CustomUserCreationForm)
        assertTemplateUsed(response, "users/register.html")

    @pytest.mark.parametrize(
        "data, validity",
        [
            (
                {
                    "first_name": "first",
                    "last_name": "last",
                    "email": "user@main.ru",
                    "password1": "PaAswd645411",
                    "password2": "PaAswd645411",
                },
                True,
            ),
            (
                {
                    "first_name": "",
                    "last_name": "l",
                    "email": "user@ma",
                    "password1": "pass",
                    "password2": "pass2",
                },
                False,
            ),
        ],
    )
    @patch("users.views.send_verification_email")
    def test_post(self, mock_send_verification_email, data, validity, app):
        """Test registration on POST, with valid/invalid data"""
        form_validity = CustomUserCreationForm(data).is_valid()
        assert form_validity == validity

        response = app.post(reverse("users:register"), data=data)

        if validity:
            user = CustomUser.objects.get(email=data["email"])

            assert response.context["email"] == user.email
            assert not user.is_active
            assertTemplateUsed(response, "users/registration/verification_sent.html")
        else:
            assert isinstance(response.context["form"], CustomUserCreationForm)
            assertTemplateUsed(response, "users/register.html")


class TestEmailVerificationView:
    def test_verification_failed(self, app):
        """Test failing verification on invalid data"""
        response = app.get(
            reverse("users:email_verification", kwargs={"uidb64": 1, "token": 1}),
        )

        assertTemplateUsed(response, "users/registration/verification_failed.html")

    def test_verification_success(self, mixer, app):
        """Test successful verification"""
        user = mixer.blend("users.CustomUser", is_active=False, email_verified=False)
        assert not user.is_active
        assert not user.email_verified

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        response = app.get(
            reverse(
                "users:email_verification",
                kwargs={"uidb64": uidb64, "token": token},
            ),
            expected_status_code=302,
        )
        user = CustomUser.objects.get(email=user.email)

        assert user.is_active
        assert user.email_verified
        assertRedirects(response, reverse("users:profile"))


class TestLoginView:
    def test_user_authenticated(self, app, auth_user):
        """Test redirection when user already authenticated"""
        response = app.get(reverse("users:login"), expected_status_code=302)
        assertRedirects(response, reverse("users:profile"))

    def test_get(self, app):
        """Test rendering form on GET"""
        response = app.get(reverse("users:login"))

        assert isinstance(response.context["form"], CustomUserLoginForm)
        assertTemplateUsed(response, "users/login.html")

    @pytest.mark.parametrize(
        "data",
        [
            {"username": "user@mail.ru", "password": "PaAswd645411"},
            {"username": "name", "password": 123},
        ],
    )
    def test_post_invalid_form(self, mixer, app, data):
        """Test re-rendering form on POST for invalid data, and inactive user"""
        user = mixer.blend(
            "users.CustomUser",
            is_active=False,
            email="user@mail.ru",
            password=make_password("PaAswd645411"),
        )

        form = CustomUserLoginForm(data=data)
        assert not form.is_valid()

        response = app.post(reverse("users:login"), data=data)

        assert isinstance(response.context["form"], CustomUserLoginForm)
        assertTemplateUsed(response, "users/login.html")

    def test_post_valid_form(self, mixer, app):
        """Test login on POST for valid data, and active user"""
        plain_password = "PaAswd645411"
        user = mixer.blend(
            "users.CustomUser",
            is_active=True,
            password=make_password(plain_password),
        )
        data = {"username": user.email, "password": plain_password}

        form = CustomUserLoginForm(data=data)
        assert form.is_valid()

        response = app.post(reverse("users:login"), data=data, expected_status_code=302)

        assertRedirects(response, reverse("users:profile"))


@pytest.mark.auth_req
class TestLogoutView:
    def test_login_required(self, app):
        """Test login redirect, on unauthenticated user"""
        response = app.get(
            reverse("users:logout"),
            expected_status_code=302,
        )
        assertRedirects(
            response,
            reverse("users:login") + "?next=/users/logout/",
        )

    def test_logout_redirect(self, app, auth_user):
        """Test successful logout redirection"""
        response = app.get(
            reverse("users:logout"),
            expected_status_code=302,
        )
        assertRedirects(response, reverse("main:home"))


@pytest.mark.auth_req
class TestProfileView:
    def test_login_required(self, app):
        """Test login redirect, on unauthenticated user"""
        response = app.get(
            reverse("users:profile"),
            expected_status_code=302,
        )
        assertRedirects(
            response,
            reverse("users:login") + "?next=/users/profile/",
        )

    def test_render(self, app, auth_user, course, order):
        """Test correct profile rendering"""
        response = app.get(
            reverse("users:profile"),
        )

        assert response.context["user"] == auth_user
        assert response.context["user_orders"][0] == order
        assert response.context["courses_covers"][0] == course.course_profile

        assertTemplateUsed(response, "users/profile.html")


@pytest.mark.auth_req
def test_profile_partial_view(app, auth_user):
    """Test partial profile rendering"""
    response = app.get(
        reverse("users:profile-partial"),
    )

    assertTemplateUsed(response, "users/partials/profile_partial.html")


@pytest.mark.auth_req
class TestPasswordChangeView:
    def test_login_required(self, app):
        """Test login redirect, on unauthenticated user"""
        response = app.get(
            reverse("users:password-change"),
            expected_status_code=302,
        )
        assertRedirects(
            response,
            reverse("users:login") + "?next=/users/password-change/",
        )

    def test_get(self, app, auth_user):
        """Test form rendering on GET"""
        response = app.get(reverse("users:password-change"))

        assert isinstance(response.context["form"], CustomUserPasswordChangeForm)
        assert response.context["user"] == auth_user
        assertTemplateUsed(response, "users/partials/password_change.html")

    @pytest.mark.parametrize(
        "data, validity",
        [
            (
                {
                    "old_password": "PaAswd",
                    "new_password1": "PaAswd645411",
                    "new_password2": "PaAswd645411",
                },
                True,
            ),
            (
                {
                    "old_password": "PaA",
                    "new_password1": "PaAswd645411",
                    "new_password2": "PaA",
                },
                False,
            ),
        ],
    )
    def test_post(self, mixer, data, validity, app):
        """Test password changing on POST for valid/invalid data"""
        hashed_old_password = make_password("PaAswd")
        user = mixer.blend("users.CustomUser", password=hashed_old_password)
        form = CustomUserPasswordChangeForm(user=user, data=data)
        form_validity = form.is_valid()
        assert form_validity == validity

        app.client.force_login(user)
        response = app.post(reverse("users:password-change"), data=data)
        user = CustomUser.objects.get(id=user.id)
        if validity:
            assert user.password != hashed_old_password
        else:
            assert user.password == hashed_old_password
        assert response.context["user"] == user
        assert isinstance(response.context["form"], CustomUserPasswordChangeForm)
        assertTemplateUsed(response, "users/partials/password_change.html")


@pytest.mark.auth_req
class TestEditAccountDetailsView:
    def test_login_required(self, app):
        """Test login redirect, on unauthenticated user"""
        response = app.get(
            reverse("users:edit-account-details"),
            expected_status_code=302,
        )
        assertRedirects(
            response,
            reverse("users:login") + "?next=/users/edit-account-details/",
        )

    def test_get(self, app, auth_user):
        """Test form rendering on GET"""
        response = app.get(reverse("users:edit-account-details"))

        assert response.context["user"] == auth_user
        assert isinstance(response.context["user_form"], CustomUserUpdateForm)
        assert isinstance(response.context["profile_form"], CustomUserProfileUpdateForm)
        assertTemplateUsed(response, "users/partials/edit_account_details.html")

    @pytest.mark.parametrize(
        "data, validity, status_code",
        [
            (
                {
                    "email": "user@newmail.ru",
                    "phone": "+999999999",
                },
                True,
                302,
            ),
            (
                {
                    "email": "user@newma",
                    "phone": "4564",
                },
                False,
                200,
            ),
        ],
    )
    def test_post(self, data, validity, status_code, app, auth_user):
        """Test changing account details on POST for valid/invalid data"""
        if validity:
            data["first_name"] = auth_user.first_name
            data["last_name"] = auth_user.last_name
        user_form = CustomUserUpdateForm(instance=auth_user, data=data)
        profile_form = CustomUserProfileUpdateForm(
            instance=auth_user.profile, data=data
        )
        assert user_form.is_valid() == validity
        assert profile_form.is_valid() == validity

        response = app.post(
            reverse("users:edit-account-details"),
            data=data,
            expected_status_code=status_code,
        )

        if validity:
            assertRedirects(response, reverse("users:profile"))
        else:
            assert response.context["user"] == auth_user
            assert isinstance(response.context["user_form"], CustomUserUpdateForm)
            assert isinstance(
                response.context["profile_form"], CustomUserProfileUpdateForm
            )
            assertTemplateUsed(response, "users/partials/edit_account_details.html")
