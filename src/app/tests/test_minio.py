import logging

import pytest
from django.conf import settings
from minio import Minio

pytestmark = [pytest.mark.django_db]

logger = logging.getLogger(__name__)


def test_minio_static():
    client = Minio(
        settings.MINIO_STORAGE_ENDPOINT,
        access_key=settings.MINIO_STORAGE_ACCESS_KEY,
        secret_key=settings.MINIO_STORAGE_SECRET_KEY,
        secure=settings.MINIO_STORAGE_USE_HTTPS,
    )

    assert client.bucket_exists(settings.MINIO_STORAGE_STATIC_BUCKET_NAME)
