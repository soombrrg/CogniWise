import pytest
from mixer.backend.django import mixer as _mixer

from app.tests.test_clients import AppClient


@pytest.fixture
def app():
    return AppClient()


@pytest.fixture
def mixer():
    return _mixer


@pytest.fixture
def user(mixer):
    return mixer.blend("users.CustomUser", email="user@mail.ru")


@pytest.fixture
def auth_user(mixer, user, app):
    app.client.force_login(user)
    return user


@pytest.fixture
def course(mixer):
    return mixer.blend(
        "main.Course",
        title="Test Python Course",
        description="Test Python Course Description",
        price=22.5,
    )


@pytest.fixture
def block(mixer, course):
    return mixer.blend("main.Block", course=course, title="Test Block", order=1)


@pytest.fixture
def subblock(mixer, block):
    return mixer.blend("main.SubBlock", block=block, title="Test SubBlock", order=1)
