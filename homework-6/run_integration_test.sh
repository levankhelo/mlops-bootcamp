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

sleep 15

# Create the S3 bucket in Localstack if it doesn't exist
echo "Creating bucket..."
aws --endpoint-url="$S3_ENDPOINT_URL" s3 mb s3://nyc-duration || true

# Create test data using the separate Python script
echo "Creating test data..."
python create_test_data.py

# Upload the test data to S3
echo "Uploading test data to S3..."
aws --endpoint-url="$S3_ENDPOINT_URL" s3 cp test_input.parquet s3://nyc-duration/in/2023-01.parquet

# Run the batch.py script for January 2023
echo "Running batch.py script..."
python batch.py 2023 1

# Download the output from S3
echo "Downloading output from S3..."
aws --endpoint-url="$S3_ENDPOINT_URL" s3 cp s3://nyc-duration/out/2023-01.parquet output.parquet

# Calculate the sum of predicted durations using the separate Python script
echo "Calculating sum of predicted durations..."
total_predicted_duration=$(python calculate_sum.py)

echo "Total predicted duration: $total_predicted_duration"
