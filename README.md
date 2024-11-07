CloudImageOptimizer
CloudImageOptimizer is a Python-based tool designed to optimize images and upload them to AWS S3, with optional CDN invalidation for CloudFront. This tool is particularly useful for reducing image sizes and improving the loading performance of web applications.

Features
Download images from URLs and resize them.
Convert images to WebP format.
Upload optimized images to AWS S3.
Invalidate CloudFront cache to ensure optimized images are served.
Requirements
Python 3.6+
AWS Account with S3 and CloudFront access
Installation
Clone the repository:

bash
Copy code
git clone https://github.com/your-username/cloud-image-optimizer.git
cd cloud-image-optimizer
Set up a virtual environment (recommended):

bash
Copy code
python -m venv .venv
source .venv/bin/activate   # On Windows, use .venv\Scripts\activate
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Create a .env file:

In the root directory, create a .env file with the following environment variables:

env
Copy code
FLASK_API_KEY=your_flask_api_key
CDN_CLOUDFRONT_ID=your_cdn_cf_id
ACCESS_KEY_ID_AWS=your_aws_access_key_id
SECRET_ACCESS_KEY_AWS=your_aws_secret_access_key
Replace the placeholders (your_flask_api_key, your_cdn_cf_id, your_aws_access_key_id, and your_aws_secret_access_key) with your actual values.

Usage
Run the Flask application:

bash
Copy code
python app.py
The server will start on http://localhost:5000.

API Endpoints:

Health Check:

bash
Copy code
GET /api/healthcheck
Returns a JSON response indicating the service is running.
Convert and Upload Images:

arduino
Copy code
POST /api/convert-image
Headers:

x-api-key: Your API key (set in .env as FLASK_API_KEY)
Body:

cdn: The AWS S3 bucket name.
images: A list of image objects, each with id, imageType, and url properties.
Example Request Body:

json
Copy code
{
  "cdn": "your_s3_bucket_name",
  "images": [
    {
      "id": "image1",
      "imageType": "image/jpeg",
      "url": "https://example.com/image1.jpg"
    },
    {
      "id": "image2",
      "imageType": "image/png",
      "url": "https://example.com/image2.png"
    }
  ]
}
Response: Returns a message confirming that image optimization is in progress in the background.

Viewing Logs:

Logs are output to the console to help you monitor the progress of image optimization and detect any issues.
Continuous Integration and Continuous Deployment (CI/CD)
This project includes a CI/CD pipeline using Bitbucket Pipelines, Docker, and AWS ECS Fargate.

CI/CD Workflow Overview
Bitbucket Pipelines: The CI/CD process is defined in .bitbucket-pipelines.yml. The pipeline will:

Build the Docker image from the Dockerfile.
Push the Docker image to AWS ECR (Elastic Container Registry).
Deploy the updated image to AWS ECS Fargate.
Docker:

The Dockerfile specifies the environment setup for the application, packaging it as a Docker container.
Ensure that the Docker image is updated and stored in ECR for deployment.
AWS ECS Fargate:

The task-definition.json file defines the ECS task configuration. It specifies details such as:
Logging configuration with AWS CloudWatch.
Port mappings to expose the application on port 5000.
Secrets management to securely pass sensitive information (like FLASK_API_KEY and AWS credentials) via AWS SSM Parameter Store.
Deployment is done using the latest Docker image stored in ECR.
Setting Up CI/CD for Your Project

Step 1: Configure AWS Resources
ECR (Elastic Container Registry): Create an ECR repository to store your Docker images.
ECS Task Definition: Register the task definition based on task-definition.json.
ECS Service: Set up an ECS service to run the task on Fargate.
SSM Parameters: Store sensitive values (e.g., FLASK_API_KEY, AWS Access Keys) in AWS Systems Manager Parameter Store.

Step 2: Set Up Bitbucket Pipelines
In Bitbucket, ensure your repository has access to AWS credentials by setting the following variables in Bitbucket repository settings under Pipelines > Repository variables:

AWS_ACCESS_KEY_ID: Your AWS access key.
AWS_SECRET_ACCESS_KEY: Your AWS secret access key.
Any other necessary environment variables (e.g., ECR_REPOSITORY_URI).
