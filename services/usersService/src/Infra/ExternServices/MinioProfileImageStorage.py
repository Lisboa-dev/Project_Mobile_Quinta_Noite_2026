from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from uuid import uuid4

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from src.infra.config.settings import settings


@dataclass(frozen=True)
class StoredProfileImage:
    object_name: str
    url: str


class MinioProfileImageStorage:
    def __init__(
        self,
        endpoint_url: str = settings.minio_endpoint_url,
        public_url: str = settings.minio_public_url,
        access_key: str = settings.minio_access_key,
        secret_key: str = settings.minio_secret_key,
        bucket_name: str = settings.minio_bucket_name,
        secure: bool = settings.minio_secure,
    ):
        self.bucket_name = bucket_name
        self.public_url = public_url.rstrip("/")
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            use_ssl=secure,
            config=Config(signature_version="s3v4"),
        )

    def ensure_bucket(self) -> None:
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
        except ClientError as exc:
            status_code = exc.response.get("ResponseMetadata", {}).get("HTTPStatusCode")
            if status_code not in {404, 403}:
                raise
            self.client.create_bucket(Bucket=self.bucket_name)

    def save(self, user_id: int, filename: str, content_type: str, content: bytes) -> StoredProfileImage:
        self.ensure_bucket()
        extension = Path(filename or "").suffix.lower()
        object_name = f"profiles/{user_id}/{uuid4().hex}{extension}"
        self.client.upload_fileobj(
            BytesIO(content),
            self.bucket_name,
            object_name,
            ExtraArgs={"ContentType": content_type},
        )
        return StoredProfileImage(
            object_name=object_name,
            url=f"{self.public_url}/{self.bucket_name}/{object_name}",
        )

    def delete(self, object_name: str | None) -> None:
        if not object_name:
            return
        self.client.delete_object(Bucket=self.bucket_name, Key=object_name)
