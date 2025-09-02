import re

import pytest
from django.http import HttpResponse

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def user(mixer):
    return mixer.blend("auth.User", title="Test User")


@pytest.fixture
def course(mixer):
    return mixer.blend("main.Course", title="Test Course")


@pytest.fixture
def block(mixer, course):
    return mixer.blend("main.Block", course=course, title="Test Block")


@pytest.fixture
def subblock(mixer, block):
    return mixer.blend("main.SubBlock", block=block, title="Test SubBlock")


def test_block_subblock_partial(api, subblock, block, course):
    response = api.get(f"/courses/{course.id}/load/{block.id}/{subblock.id}/")

    assert re.search(r"Test Block", response.content.decode("utf-8"))
    assert re.search(r"Test SubBlock", response.content.decode("utf-8"))


# def test_courses(api, course, user):
#     api.api_client.force_authenticate(user=user)
#     response = api.get(f"/courses/{course.id}/")
#
#     assert re.search(r"Test Course", response.content.decode("utf-8"))
