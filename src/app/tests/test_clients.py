import boto3
from botocore.config import Config
from django.conf import settings
from django.test import Client
from django.utils.functional import cached_property


class AppClient:
    """Simulating User client API"""

    @cached_property
    def client(self) -> Client:
        return Client()

    def get(self, *args, expected_status_code=200, **kwargs):
        result = self.client.get(*args, **kwargs)
        assert result.status_code == expected_status_code

        return result

    def post(self, *args, expected_status_code=200, **kwargs):
        result = self.client.post(*args, **kwargs)
        assert result.status_code == expected_status_code

        return result


class AppS3:
    """Methods for directly calling s3 API"""

    @cached_property
    def client(self):
        session = boto3.session.Session()
        return session.client(
            "s3",
            region_name=settings.AWS_S3_REGION_NAME,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            config=Config(signature_version="s3"),
        )

    def get_presigned_url(self, object_id: str, expires: int) -> str:
        return self.client.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                "Key": object_id,
                "ResponseContentDisposition": "attachment",
            },
            ExpiresIn=expires,
        )
