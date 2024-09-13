#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Load environment variables from the .env file
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
else
  echo ".env file not found!"
  exit 1
fi

# Start Localstack using Docker Compose
echo "Starting Localstack..."
docker-compose up -d

# Wait until Localstack is ready
echo "Waiting for Localstack to be ready..."
until curl -s "$S3_ENDPOINT_URL/health" | grep "\"s3\": \"running\"" > /dev/null; do
  sleep 5
  echo "Waiting for Localstack S3 service to be ready..."
done
echo "Localstack is ready."

# Create the S3 bucket in Localstack if it doesn't exist
aws --endpoint-url="$S3_ENDPOINT_URL" s3 mb s3://nyc-duration || true

# Create test data using the separate Python script
python create_test_data.py

# Upload the test data to S3
aws --endpoint-url="$S3_ENDPOINT_URL" s3 cp test_input.parquet s3://nyc-duration/in/2023-01.parquet

# Run the batch.py script for January 2023
python batch.py 2023 1

# Download the output from S3
aws --endpoint-url="$S3_ENDPOINT_URL" s3 cp s3://nyc-duration/out/2023-01.parquet output.parquet

# Calculate the sum of predicted durations using the separate Python script
total_predicted_duration=$(python calculate_sum.py)

echo "Total predicted duration: $total_predicted_duration"
