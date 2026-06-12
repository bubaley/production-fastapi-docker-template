import asyncio
import mimetypes
from datetime import datetime
from typing import Any, BinaryIO, Optional

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from loguru import logger
from pydantic import BaseModel

from app.core.settings import settings


class S3UploadResult(BaseModel):
    url: str
    key: str


class S3Service:
    """Service for handling AWS S3 operations"""

    def __init__(self):
        """Initialize S3 client with credentials from environment variables"""
        self.s3_client = None

        self.access_key_id = settings.aws_access_key_id
        self.secret_access_key = settings.aws_secret_access_key
        self.region_name = settings.aws_s3_region_name
        self.endpoint_url = settings.aws_s3_endpoint_url
        self.bucket_name = settings.aws_storage_bucket_name
        self.root_folder = 'resources'

        self._initialize_client()

    def _initialize_client(self):
        """Initialize S3 client"""
        try:
            client_config: dict[str, Any] = {
                'service_name': 's3',
                'aws_access_key_id': self.access_key_id,
                'aws_secret_access_key': self.secret_access_key,
                'region_name': self.region_name,
                'endpoint_url': self.endpoint_url,
            }

            # client_config['endpoint_url'] = settings.aws_s3_endpoint_url
            # client_config['config'] = Config(
            #     signature_version='s3v4',
            #     s3={'addressing_style': 'path', 'payload_signing_enabled': False},
            #     region_name=settings.aws_s3_region_name,
            #     response_checksum_validation='when_required',
            #     request_checksum_calculation='when_required',
            # )
            # os.environ['AWS_S3_DISABLE_BODY_SIGNING'] = 'true'
            # logger.info(f'Using custom S3 endpoint: {self.endpoint_url}')

            self.s3_client = boto3.client(**client_config)

        except NoCredentialsError:
            logger.warning('AWS credentials not found. S3 functionality will be disabled.')
        except Exception as e:
            logger.error(f'Failed to initialize S3 client: {str(e)}')

    def _generate_file_key(self, filename: str) -> str:
        """Generate file key for S3 storage using year/month/day/file structure"""
        now = datetime.now()
        year = now.strftime('%Y')
        month = now.strftime('%m')
        day = now.strftime('%d')
        root_folder = f'{self.root_folder}/' if self.root_folder else ''
        return f'{root_folder}{year}/{month}/{day}/{filename}'

    def generate_file_key(self, filename: str) -> str:
        """Generate file key for S3 storage (public method)"""
        return self._generate_file_key(filename)

    def generate_public_url(self, file_key: str) -> str:
        file_key = file_key.lstrip('/')
        return f'{self.endpoint_url}/{self.bucket_name}/{file_key}'

    async def upload_file(
        self, file_content: BinaryIO, filename: str, content_type: Optional[str] = None
    ) -> S3UploadResult:
        if not self.s3_client:
            raise Exception('S3 client is not initialized. Check AWS credentials and configuration.')

        try:
            file_key = self._generate_file_key(filename)
            if not content_type:
                content_type, _ = mimetypes.guess_type(filename)
                if not content_type:
                    content_type = 'application/octet-stream'

            file_content.seek(0)
            file_data = file_content.read()
            put_object_args = {
                'Bucket': self.bucket_name,
                'Key': file_key,
                'Body': file_data,
                'ContentType': content_type,
            }

            if not self.endpoint_url:
                put_object_args['ACL'] = 'public-read'

            def _upload():
                if self.s3_client:
                    return self.s3_client.put_object(**put_object_args)

            await asyncio.get_event_loop().run_in_executor(None, _upload)
            file_url = self.generate_public_url(file_key)
            return S3UploadResult(url=file_url, key=file_key)

        except ClientError as e:
            logger.error(f'Failed to upload file to S3: {str(e)}')
            raise Exception(f'File upload failed: {str(e)}')
        except Exception as e:
            logger.error(f'Unexpected error during file upload: {str(e)}')
            raise Exception(f'File upload failed: {str(e)}')

    async def upload_file_by_key(
        self, file_content: bytes, file_key: str, content_type: Optional[str] = None
    ) -> S3UploadResult:
        """Upload file to S3 by pre-generated key"""
        if not self.s3_client:
            raise Exception('S3 client is not initialized. Check AWS credentials and configuration.')

        try:
            if not content_type:
                content_type = 'application/octet-stream'

            put_object_args = {
                'Bucket': self.bucket_name,
                'Key': file_key,
                'Body': file_content,
                'ContentType': content_type,
            }

            if not self.endpoint_url:
                put_object_args['ACL'] = 'public-read'

            def _upload():
                if self.s3_client:
                    return self.s3_client.put_object(**put_object_args)

            await asyncio.get_event_loop().run_in_executor(None, _upload)
            file_url = self.generate_public_url(file_key)
            return S3UploadResult(url=file_url, key=file_key)

        except ClientError as e:
            logger.error(f'Failed to upload file to S3: {str(e)}')
            raise Exception(f'File upload failed: {str(e)}')
        except Exception as e:
            logger.error(f'Unexpected error during file upload: {str(e)}')
            raise Exception(f'File upload failed: {str(e)}')


_s3_service_instance = None


def get_s3_service() -> S3Service:
    """Get S3 service instance (lazy initialization)"""
    global _s3_service_instance
    if _s3_service_instance is None:
        try:
            _s3_service_instance = S3Service()
        except Exception as e:
            logger.error(f'Failed to initialize S3 service: {e}')
            raise Exception(f'S3 service initialization failed: {e}')
    return _s3_service_instance
