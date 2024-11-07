import logging
from io import BytesIO
from typing import Dict, Optional

import boto3
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger(__name__)

# Initialize S3 client
s3_client = boto3.client("s3")


def upload_file(file_buffer: BytesIO, bucket: str, key: str, extra_args: Optional[Dict] = None):
    """
    Uploads a file buffer to an S3 bucket.

    Args:
        file_buffer (BytesIO): The file content to upload.
        bucket (str): The S3 bucket name.
        key (str): The S3 object key.
        extra_args (Optional[Dict]): Additional arguments for S3 upload.

    Raises:
        ClientError: If upload fails.
    """
    try:
        s3_client.upload_fileobj(
            Fileobj=file_buffer,
            Bucket=bucket,
            Key=key,
            ExtraArgs=extra_args or {}
        )
        logger.info(f"Uploaded file to S3: s3://{bucket}/{key}")
    except ClientError as e:
        logger.exception(f"Failed to upload file to S3: s3://{bucket}/{key}")
        raise


def get_cdn_url_by_bucket(bucket: str) -> str:
    """
    Constructs the CDN URL for a given S3 bucket.

    Args:
        bucket (str): The S3 bucket name.

    Returns:
        str: The CDN URL.
    """
    # Replace with actual logic to construct CDN URL
    return f"https://{bucket}.s3.amazonaws.com/"
