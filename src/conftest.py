import pytest
from mixer.backend.django import mixer as _mixer

from app.tests.test_clients import AppClient


@pytest.fixture
def api():
    return AppClient()


@pytest.fixture
def mixer():
    return _mixer
