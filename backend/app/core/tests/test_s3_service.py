import io
import re
from unittest.mock import MagicMock
from urllib.parse import parse_qs, urlsplit

import boto3
import pytest
from botocore.exceptions import ClientError

from app.core.services import s3_service as s3_module
from app.core.services.s3_service import S3Error, S3Service
from app.core.settings import settings

KEY_PATTERN = r'resources/\d{4}/\d{2}/\d{2}/[0-9a-f]{32}'


@pytest.fixture
def real_client():
    """Offline botocore client: presigning is local, nothing is sent."""
    return boto3.client(
        's3', region_name='eu-central-1', aws_access_key_id='test-key', aws_secret_access_key='test-secret'
    )


@pytest.mark.parametrize(
    'filename, suffix',
    [
        ('photo.JPG', '.jpg'),
        ('../../etc/passwd', ''),
        ('archive.tar.gz', '.gz'),
        ('evil.php%00.png', '.png'),
        ('no-extension', ''),
        ('weird.<script>', ''),
    ],
)
def test_keys_are_uuid_based_with_sanitized_extension(filename, suffix):
    key = S3Service(client=MagicMock()).generate_key(filename)
    assert re.fullmatch(KEY_PATTERN + re.escape(suffix), key)


def test_key_prefix_is_optional_and_validated():
    service = S3Service(client=MagicMock())
    assert re.fullmatch(r'\d{4}/\d{2}/\d{2}/[0-9a-f]{32}\.txt', service.generate_key('a.txt', prefix=''))
    assert service.generate_key('a.txt', prefix='avatars/').startswith('avatars/')
    with pytest.raises(ValueError):
        service.generate_key('a.txt', prefix='../secrets')


def test_client_is_created_lazily(monkeypatch):
    factory = MagicMock()
    monkeypatch.setattr(s3_module.boto3, 'client', factory)
    service = S3Service()
    factory.assert_not_called()
    assert service.client is factory.return_value
    factory.assert_called_once()


@pytest.mark.asyncio
async def test_upload_streams_file_without_acl(monkeypatch):
    monkeypatch.setattr(settings, 'aws_s3_endpoint_url', None)
    monkeypatch.setattr(settings, 'aws_s3_public_url', None)
    monkeypatch.setattr(settings, 'aws_s3_region_name', 'eu-central-1')
    client = MagicMock()
    service = S3Service(bucket='media', client=client)
    file = io.BytesIO(b'content')
    result = await service.upload(file, 'report.pdf')
    client.upload_fileobj.assert_called_once()
    args, kwargs = client.upload_fileobj.call_args
    assert args == (file, 'media', result.key)
    assert kwargs['ExtraArgs'] == {'ContentType': 'application/pdf'}
    assert result.url == f'https://media.s3.eu-central-1.amazonaws.com/{result.key}'


@pytest.mark.parametrize(
    'endpoint, public, expected',
    [
        ('https://storage.yandexcloud.net', None, 'https://storage.yandexcloud.net/media/a/b%20c.txt'),
        ('https://storage.yandexcloud.net/', 'https://cdn.example.com/', 'https://cdn.example.com/a/b%20c.txt'),
    ],
)
def test_public_url_for_custom_endpoint_and_cdn(monkeypatch, endpoint, public, expected):
    monkeypatch.setattr(settings, 'aws_s3_endpoint_url', endpoint)
    monkeypatch.setattr(settings, 'aws_s3_public_url', public)
    assert S3Service(bucket='media', client=MagicMock()).public_url('a/b c.txt') == expected


@pytest.mark.asyncio
async def test_client_errors_are_wrapped_with_cause():
    client = MagicMock()
    error = ClientError({'Error': {'Code': 'AccessDenied', 'Message': 'denied'}}, 'DeleteObject')
    client.delete_object.side_effect = error
    with pytest.raises(S3Error) as raised:
        await S3Service(bucket='media', client=client).delete('a/b.txt')
    assert raised.value.__cause__ is error
    client.delete_object.assert_called_once_with(Bucket='media', Key='a/b.txt')


@pytest.mark.asyncio
async def test_presigned_urls(real_client):
    service = S3Service(bucket='media', client=real_client)
    get_url = await service.presigned_get_url('a/report.pdf', expires_in=120, download_name='Отчёт.pdf')
    query = parse_qs(urlsplit(get_url).query)
    assert urlsplit(get_url).path.endswith('/a/report.pdf')
    assert query['X-Amz-Expires'] == ['120']
    assert 'attachment' in query['response-content-disposition'][0]

    put_url = await service.presigned_put_url('a/upload.png', content_type='image/png')
    put_query = parse_qs(urlsplit(put_url).query)
    assert put_query['X-Amz-Expires'] == [str(settings.aws_s3_presign_expire_seconds)]
    assert 'content-type' in put_query['X-Amz-SignedHeaders'][0]
