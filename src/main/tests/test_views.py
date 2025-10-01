from unittest.mock import patch

import pytest
from django.urls import reverse
from pytest_django.asserts import (
    assertRedirects,
    assertTemplateUsed,
)

from main.forms import EmailForContactForm

pytestmark = [pytest.mark.django_db]


def test_home_view(app):
    response = app.get(reverse("main:home"))
    assertTemplateUsed(response, "main/home.html")


def test_about_view(app):
    response = app.get(reverse("main:about"))
    assertTemplateUsed(response, "main/about.html")


class TestModalWindowsViews:
    def test_open_demo(self, app):
        response = app.get(reverse("main:modal-open-demo"))
        assertTemplateUsed(response, "main/partials/modal_demo.html")

    def test_open_contact_get(self, app):
        """Test contact modal shows form on GET"""
        response = app.get(reverse("main:modal-open-contact"))

        assert isinstance(response.context["form"], EmailForContactForm)
        assertTemplateUsed(response, "main/partials/modal_contact.html")

    @pytest.mark.parametrize(
        "data, validity",
        [
            (
                {
                    "name": "name",
                    "email": "test@mail.ru",
                    "phone": "+999999999",
                    "tg_username": "@tg_username",
                },
                True,
            ),
            (
                {
                    "name": "na",
                    "email": "test@ma",
                    "phone": "999",
                    "tg_username": "username",
                },
                False,
            ),
        ],
    )
    @patch("main.views.send_email_for_contact")
    def test_open_contact_post(self, mock_send_email_for_contact, data, validity, app):
        """Test contact POST with valid/invalid values"""
        response = app.post(reverse("main:modal-open-contact"), data=data)

        if validity:
            mock_send_email_for_contact.assert_called_once_with(data)
            assertTemplateUsed(response, "main/partials/modal_successful_sending.html")
        else:
            assert isinstance(response.context["form"], EmailForContactForm)
            assertTemplateUsed(response, "main/partials/modal_contact.html")

    def test_close(self, app):
        response = app.get(reverse("main:modal-close"))
        assert response.content.decode() == '<div id="modal"></div>'


class TestCoursesListView:
    def test_courses_list_view(self, app, course):
        response = app.get(reverse("main:courses-list"))
        assert course in response.context["courses"]
        assert (
            f"/covers/default_cover.jpeg"
            in response.context["courses"][0].course_profile.cover.url
        )

    def test_courses_list_no_courses_view(self, app):
        response = app.get(reverse("main:courses-list"))
        msg = "Курсы пока не добавлены"
        assert msg in response.content.decode()


class TestCoursesSearchView:
    @pytest.mark.parametrize(
        "query_dict",
        [
            {"query": "Python"},
            None,
            pytest.param({"query": "NotExist"}, marks=pytest.mark.xfail),
        ],
    )
    def test_courses_search_query_view(self, app, course, query_dict):
        response = app.get(reverse("main:courses-search"), query_dict)
        assert course in response.context["courses"]

    def test_courses_search_query_no_courses_view(self, app):
        response = app.get(reverse("main:courses-search"))
        msg = "Курсы пока не добавлены"
        assert msg in response.content.decode()


@pytest.mark.auth_req
@pytest.mark.purchase_req
class TestCoursesDetailView:
    def test_no_course(self, app, auth_user):
        response = app.get(
            reverse("main:course-detail", args=[1]),
            expected_status_code=404,
        )

    def test_login_required(self, app, course):
        """Test auth requirements"""
        response = app.get(
            reverse("main:course-detail", args=[course.id]),
            expected_status_code=302,
        )
        redirect_url = reverse("users:login") + f"?next=/courses/{course.id}/"

        assertRedirects(response, redirect_url)

    def test_access_denied(self, app, auth_user, course):
        """Test when course isn`t bought"""
        response = app.get(
            reverse("main:course-detail", args=[course.id]),
            expected_status_code=402,
        )
        assertTemplateUsed(response, "main/access_denied.html")

    @patch("main.decorators.is_purchased")
    def test_purchased(
        self, mock_is_purchased, app, auth_user, course, block, subblock
    ):
        """Test when course is bought"""
        mock_is_purchased.return_value = True

        response = app.get(reverse("main:course-detail", args=[course.id]))

        mock_is_purchased.assert_called_once_with(auth_user, course.id)
        assertTemplateUsed(response, "main/course_detail.html")
        assert course == response.context["course"]
        assert block == response.context["first_block"]
        assert subblock == response.context["first_subblock"]

    @patch("main.decorators.is_purchased")
    def test_purchased_no_content(self, mock_is_purchased, app, auth_user, course):
        """Test when course is bought, but it has no content (block, subblock)"""
        mock_is_purchased.return_value = True

        response = app.get(reverse("main:course-detail", args=[course.id]))

        mock_is_purchased.assert_called_once_with(auth_user, course.id)
        assertTemplateUsed(response, "main/course_detail.html")
        assert course == response.context["course"]
        assert response.context["first_block"] is None
        assert response.context["first_subblock"] is None


def _test_load_content(content, content_type, response):
    assert content == response.context["content"]
    assert content_type == response.context["content_type"]
    assertTemplateUsed(response, "main/partials/partial_content.html")


@pytest.mark.auth_req
@pytest.mark.purchase_req
@patch("main.decorators.is_purchased")
class TestLoadNextContentView:
    def test_next_block(self, mock_is_purchased, mixer, app, auth_user, course, block):
        """Test load, next content - block"""
        mock_is_purchased.return_value = True

        block2 = mixer.blend("main.Block", course=course, title="Test Block 2", order=2)

        response = app.get(
            reverse("main:load-next-content", args=[course.id, block.id])
        )
        _test_load_content(block2, "block", response)

    def test_next_subblock(
        self, mock_is_purchased, mixer, app, auth_user, course, block, subblock
    ):
        """Test load, next content - subblock"""
        mock_is_purchased.return_value = True

        response = app.get(
            reverse("main:load-next-content", args=[course.id, block.id])
        )

        _test_load_content(subblock, "subblock", response)

    def test_next_empty(self, mock_is_purchased, mixer, app, auth_user, course, block):
        """Test load, course have no next content"""
        mock_is_purchased.return_value = True

        response = app.get(
            reverse("main:load-next-content", args=[course.id, block.id])
        )
        assert response.content.decode() == ""


@pytest.mark.auth_req
@pytest.mark.purchase_req
@patch("main.decorators.is_purchased")
class TestLoadNextContentFromSubblockView:
    def test_next_from_subblock_next_block(
        self, mock_is_purchased, mixer, app, auth_user, course, block, subblock
    ):
        """Test load from subblock, next content - block"""
        mock_is_purchased.return_value = True

        block2 = mixer.blend("main.Block", course=course, title="Test Block 2", order=2)

        response = app.get(
            reverse(
                "main:load-next-content-from-subblock",
                args=[course.id, block.id, subblock.id],
            )
        )
        _test_load_content(block2, "block", response)

    def test_next_from_subblock_next_subblock(
        self, mock_is_purchased, mixer, app, auth_user, course, block, subblock
    ):
        """Test load from subblock, next content - subblock"""
        mock_is_purchased.return_value = True

        subblock2 = mixer.blend(
            "main.SubBlock", block=block, title="Test SubBlock 2", order=2
        )

        response = app.get(
            reverse(
                "main:load-next-content-from-subblock",
                args=[course.id, block.id, subblock.id],
            )
        )

        _test_load_content(subblock2, "subblock", response)
