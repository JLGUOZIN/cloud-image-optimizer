import logging
import time
import uuid
from typing import List

import boto3
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger(__name__)

# Constants
CDN_CLOUDFRONT_ID = "your-cloudfront-distribution-id"

# Initialize the CloudFront client
cloudfront_client = boto3.client("cloudfront")


def invalidate_cdn(cdn: str, items: List[str]):
    """
    Creates an invalidation in CloudFront for the specified items.

    Args:
        cdn (str): CDN identifier (unused but kept for interface consistency).
        items (List[str]): List of paths to invalidate.

    Raises:
        Exception: If the invalidation request fails.
    """
    caller_reference = f"{int(time.time())}-{uuid.uuid4()}"

    if not CDN_CLOUDFRONT_ID:
        logger.error("CloudFront distribution ID is not set.")
        raise ValueError("CloudFront distribution ID is not set.")

    try:
        response = cloudfront_client.create_invalidation(
            DistributionId=CDN_CLOUDFRONT_ID,
            InvalidationBatch={
                "Paths": {
                    "Quantity": len(items),
                    "Items": items,
                },
                "CallerReference": caller_reference,
            },
        )
        logger.info(f"Invalidation created: {response['Invalidation']['Id']}")
    except ClientError as e:
        logger.exception("Failed to create CloudFront invalidation.")
        raise
