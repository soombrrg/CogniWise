import logging

import pytest

from app.tests.test_clients import AppS3

pytestmark = [pytest.mark.django_db]

logger = logging.getLogger(__name__)


def test_client_init():
    client = AppS3().client
    assert "botocore.client.S3" in str(client.__class__)
