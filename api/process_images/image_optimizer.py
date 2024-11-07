# image_optimizer.py

import logging
import concurrent.futures
from io import BytesIO
from typing import Optional, List

import requests
from PIL import Image
from botocore.exceptions import ClientError

from utils.s3 import upload_file
from utils.cloudfront import invalidate_cdn

# Configure logging
logger = logging.getLogger(__name__)

# Constants
S3_KEY_PREFIX = "your/s3/key/prefix/"
MAX_SIZE = 2880  # 1920 * 1.5


def get_image_bytes_by_url(image_url: str) -> Optional[BytesIO]:
    """
    Fetches image content from a URL and returns it as a BytesIO object.

    Args:
        image_url (str): The URL of the image.

    Returns:
        Optional[BytesIO]: BytesIO object of image content or None if failed.
    """
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        return BytesIO(response.content)
    except requests.RequestException as e:
        logger.exception(f"Failed to fetch image from URL: {image_url}")
        return None


def upload_image(bucket: str, key: str, content_type: str, image_buffer: BytesIO):
    """
    Uploads an image buffer to S3.

    Args:
        bucket (str): S3 bucket name.
        key (str): S3 object key.
        content_type (str): MIME type of the image.
        image_buffer (BytesIO): Image content.
    """
    try:
        upload_file(
            file_buffer=image_buffer,
            bucket=bucket,
            key=S3_KEY_PREFIX + key,
            extra_args={"ContentType": content_type}
        )
        logger.info(f"Uploaded image to S3: s3://{bucket}/{S3_KEY_PREFIX + key}")
    except ClientError as e:
        logger.exception(f"Failed to upload image to S3: {key}")
        raise


def upload_original_images_to_s3(bucket: str, images: List[dict]):
    """
    Uploads original images to S3 using multithreading.

    Args:
        bucket (str): S3 bucket name.
        images (List[dict]): List of image dictionaries with 'id', 'imageType', and 'url'.
    """
    def task(image):
        image_buffer = get_image_bytes_by_url(image["url"])
        if image_buffer:
            upload_image(bucket, image["id"], image["imageType"], image_buffer)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(task, image) for image in images]
        for future in concurrent.futures.as_completed(futures):
            if future.exception():
                logger.error(f"Exception occurred during image upload: {future.exception()}")

def resize_and_convert(image_buffer: BytesIO) -> Optional[BytesIO]:
    """
    Resizes and converts an image to WebP format.

    Args:
        image_buffer (BytesIO): Original image content.

    Returns:
        Optional[BytesIO]: Processed image buffer or None if failed.
    """
    try:
        with Image.open(image_buffer) as img:
            # Resize image if necessary
            if img.width > MAX_SIZE:
                new_width = MAX_SIZE
                new_height = int((MAX_SIZE / img.width) * img.height)
                img = img.resize((new_width, new_height), Image.ANTIALIAS)

            # Check if image is animated
            save_all = getattr(img, "is_animated", False)

            # Convert image to WebP
            output_buffer = BytesIO()
            img.save(output_buffer, format="WEBP", save_all=save_all)
            output_buffer.seek(0)
            return output_buffer
    except Exception as e:
        logger.exception("Failed to resize and convert image.")
        return None


def process_image(bucket: str, image: dict):
    """
    Processes a single image: resizes, converts, and uploads to S3.

    Args:
        bucket (str): S3 bucket name.
        image (dict): Image dictionary with 'id' and 'url'.
    """
    image_buffer = get_image_bytes_by_url(image["url"])
    if not image_buffer:
        logger.error(f"Skipping image due to download failure: {image['url']}")
        return

    processed_buffer = resize_and_convert(image_buffer)
    if not processed_buffer:
        logger.error(f"Skipping image due to processing failure: {image['url']}")
        return

    upload_image(bucket, image["id"], "image/webp", processed_buffer)


def optimize_images(bucket: str, images: List[dict]):
    """
    Optimizes a list of images and uploads them to S3, then invalidates CDN cache.

    Args:
        bucket (str): S3 bucket name.
        images (List[dict]): List of image dictionaries.
    """
    items_to_invalidate = []

    def task(image):
        process_image(bucket, image)
        items_to_invalidate.append(f"/{S3_KEY_PREFIX}{image['id']}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(task, image) for image in images]
        for future in concurrent.futures.as_completed(futures):
            if future.exception():
                logger.error(f"Exception occurred during image optimization: {future.exception()}")

    # Invalidate CDN cache
    if items_to_invalidate:
        try:
            invalidate_cdn(bucket, items_to_invalidate)
            logger.info(f"Invalidated CDN cache for items: {items_to_invalidate}")
        except Exception as e:
            logger.exception("Failed to invalidate CDN cache.")
