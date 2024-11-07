import os
import logging
from functools import wraps
from concurrent.futures import ThreadPoolExecutor

from flask import Flask, request, jsonify, abort
from flask_cors import CORS

from api.process_images.image_optimizer import (
    optimize_images,
    upload_original_images_to_s3,
)

# Initialize Flask app
app = Flask(__name__)
PREFIX = "/api"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
API_KEY = os.environ.get("FLASK_API_KEY")
if not API_KEY:
    raise ValueError("API_KEY is not set in environment variables.")

buyer_domains = os.environ.get("BUYER_DOMAINS", "").split(",")

# Enable CORS
CORS(app, resources={r"/api/*": {"origins": buyer_domains}})

def require_apikey(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if request.headers.get("x-api-key") == API_KEY:
            return view_function(*args, **kwargs)
        else:
            logger.warning("Unauthorized access attempt.")
            abort(401, description="Unauthorized")
    return decorated_function

@app.route(f"{PREFIX}/healthcheck")
def healthcheck():
    return jsonify({"status": "Health Check Successful!"}), 200

@app.route(f"{PREFIX}/convert-image", methods=["POST"])
@require_apikey
def convert_image_to_webp_and_upload_s3():
    data = request.get_json()
    try:
        validate_request_data(data)
        cdn = data["cdn"]
        images = data["images"]

        # Upload original images
        upload_original_images_to_s3(cdn, images)

        # Process images in background
        executor = ThreadPoolExecutor(max_workers=5)
        executor.submit(optimize_images, cdn, images)

        return jsonify({"message": "Image optimization is processing in the background."}), 202
    except Exception as err:
        logger.exception("Failed to process images.")
        return jsonify({"error": str(err)}), 500

def validate_request_data(data):
    if not data:
        raise ValueError("No data provided.")
    required_keys = ["images", "cdn"]
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Missing required parameter: {key}")

if __name__ == "__main__":
    from waitress import serve
    logger.info("Starting server at port 5000.")
    serve(app, host="0.0.0.0", port=5000)
