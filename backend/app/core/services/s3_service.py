import asyncio
import mimetypes
import re
from pathlib import PurePosixPath
from typing import Any, BinaryIO
from urllib.parse import quote
from uuid import uuid4

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from pydantic import BaseModel

from app.core.settings import settings
from app.core.utils.date_utils import utcnow

_SAFE_EXTENSION = re.compile(r'^\.[a-z0-9]{1,16}$')
_SAFE_PREFIX = re.compile(r'^[A-Za-z0-9._/-]*$')


class S3Error(RuntimeError):
    pass


class S3UploadResult(BaseModel):
    key: str
    url: str


class S3Service:
    """
    Object storage. Objects are private (no ACL): share them with presigned URLs, or serve them through a
    public bucket policy / CDN (`AWS_S3_PUBLIC_URL`). The boto3 client is created on first use; blocking calls
    run in a thread.
    """

    def __init__(self, *, bucket: str | None = None, prefix: str = 'resources', client: Any = None):
        self.bucket = bucket or settings.aws_storage_bucket_name
        self.prefix = prefix
        self._client = client

    @property
    def client(self) -> Any:
        if self._client is None:
            self._client = boto3.client(
                's3',
                aws_access_key_id=settings.aws_access_key_id or None,
                aws_secret_access_key=settings.aws_secret_access_key or None,
                region_name=settings.aws_s3_region_name or None,
                endpoint_url=settings.aws_s3_endpoint_url or None,
                config=Config(signature_version='s3v4'),
            )
        return self._client

    # KEYS AND URLS

    def generate_key(self, filename: str, prefix: str | None = None) -> str:
        """`<prefix>/YYYY/MM/DD/<uuid><.ext>`; the client filename contributes only a sanitized extension."""
        prefix = self.prefix if prefix is None else prefix
        if not _SAFE_PREFIX.match(prefix) or '..' in prefix:
            raise ValueError(f'Unsafe S3 key prefix: {prefix!r}')
        extension = PurePosixPath(filename.replace('\\', '/')).suffix.lower()
        if not _SAFE_EXTENSION.match(extension):
            extension = ''
        date_path = utcnow().strftime('%Y/%m/%d')
        parts = [part for part in (prefix.strip('/'), date_path, f'{uuid4().hex}{extension}') if part]
        return '/'.join(parts)

    def public_url(self, key: str) -> str:
        """URL of the object for a public bucket or CDN; private objects need `presigned_get_url`."""
        quoted = quote(key.lstrip('/'))
        if settings.aws_s3_public_url:
            return f'{settings.aws_s3_public_url.rstrip("/")}/{quoted}'
        if settings.aws_s3_endpoint_url:
            return f'{settings.aws_s3_endpoint_url.rstrip("/")}/{self.bucket}/{quoted}'
        region = settings.aws_s3_region_name or 'us-east-1'
        return f'https://{self.bucket}.s3.{region}.amazonaws.com/{quoted}'

    # OPERATIONS

    async def upload(
        self, file: BinaryIO, filename: str, content_type: str | None = None, prefix: str | None = None
    ) -> S3UploadResult:
        """Stream a file-like object (e.g. `UploadFile.file`) under a generated key."""
        return await self.upload_by_key(file, self.generate_key(filename, prefix), content_type or _guess(filename))

    async def upload_by_key(self, file: BinaryIO, key: str, content_type: str | None = None) -> S3UploadResult:
        extra_args = {'ContentType': content_type or _guess(key)}
        try:
            # upload_fileobj reads in chunks (multipart for large files) instead of loading the file into memory.
            await asyncio.to_thread(self.client.upload_fileobj, file, self.bucket, key, ExtraArgs=extra_args)
        except (BotoCoreError, ClientError) as e:
            raise S3Error(f'Upload of {key} failed') from e
        return S3UploadResult(key=key, url=self.public_url(key))

    async def delete(self, key: str) -> None:
        try:
            await asyncio.to_thread(self.client.delete_object, Bucket=self.bucket, Key=key)
        except (BotoCoreError, ClientError) as e:
            raise S3Error(f'Delete of {key} failed') from e

    async def presigned_get_url(self, key: str, expires_in: int | None = None, download_name: str | None = None) -> str:
        params: dict[str, Any] = {'Bucket': self.bucket, 'Key': key}
        if download_name:
            params['ResponseContentDisposition'] = f"attachment; filename*=UTF-8''{quote(download_name)}"
        return await self._presign('get_object', params, expires_in)

    async def presigned_put_url(self, key: str, content_type: str, expires_in: int | None = None) -> str:
        """Direct browser upload: the client must send the same Content-Type header."""
        return await self._presign(
            'put_object', {'Bucket': self.bucket, 'Key': key, 'ContentType': content_type}, expires_in
        )

    async def _presign(self, operation: str, params: dict[str, Any], expires_in: int | None) -> str:
        expires = expires_in or settings.aws_s3_presign_expire_seconds
        try:
            return await asyncio.to_thread(
                self.client.generate_presigned_url, operation, Params=params, ExpiresIn=expires
            )
        except (BotoCoreError, ClientError) as e:
            raise S3Error(f'Presigning {operation} failed') from e


def _guess(name: str) -> str:
    return mimetypes.guess_type(name)[0] or 'application/octet-stream'


_s3_service_instance: S3Service | None = None


def get_s3_service() -> S3Service:
    """Shared instance; nothing touches AWS until the first operation."""
    global _s3_service_instance
    if _s3_service_instance is None:
        _s3_service_instance = S3Service()
    return _s3_service_instance
