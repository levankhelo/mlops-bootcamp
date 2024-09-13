import os
import subprocess
import pandas as pd
from datetime import datetime

# Helper function to create datetime objects
def dt(hour, minute, second=0):
    return datetime(2023, 1, 1, hour, minute, second)

# Step 1: Create and upload test data
data = [
    (None, None, dt(1, 1), dt(1, 10)),
    (1, 1, dt(1, 2), dt(1, 10)),
    (1, None, dt(1, 2, 0), dt(1, 2, 59)),
    (3, 4, dt(1, 2, 0), dt(2, 2, 1)),
]
columns = ['PULocationID', 'DOLocationID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime']
df_input = pd.DataFrame(data, columns=columns)

# Define S3 paths
year = 2023
month = 1
input_file = f's3://nyc-duration/in/{year:04d}-{month:02d}.parquet'

# Configure storage options
s3_endpoint_url = os.getenv('S3_ENDPOINT_URL', 'http://localhost:4566')
options = {
    'client_kwargs': {
        'endpoint_url': s3_endpoint_url
    }
}

# Upload test data to S3
df_input.to_parquet(
    input_file,
    engine='pyarrow',
    compression=None,
    index=False,
    storage_options=options
)

# Step 2: Run batch.py
os.environ['INPUT_FILE_PATTERN'] = 's3://nyc-duration/in/{year:04d}-{month:02d}.parquet'
os.environ['OUTPUT_FILE_PATTERN'] = 's3://nyc-duration/out/{year:04d}-{month:02d}.parquet'
os.environ['S3_ENDPOINT_URL'] = s3_endpoint_url

result = subprocess.run(['python', 'batch.py', str(year), str(month)], capture_output=True, text=True)

if result.returncode != 0:
    print("batch.py did not run successfully")
    print("Error output:", result.stderr)
else:
    print("batch.py ran successfully")
    print("Standard output:", result.stdout)

# Step 3: Read the output data
output_file = f's3://nyc-duration/out/{year:04d}-{month:02d}.parquet'

df_result = pd.read_parquet(
    output_file,
    storage_options=options
)

print("Output DataFrame:")
print(df_result)

# Step 4: Verify the results
# Define expected results based on your model
expected_ride_ids = [
    '2023/01_0',
    '2023/01_1'
]

# For demonstration, we'll assume the model predicts 10.0 for all valid trips
expected_predicted_durations = [
    10.0,
    10.0
]

df_expected = pd.DataFrame({
    'ride_id': expected_ride_ids,
    'predicted_duration': expected_predicted_durations
})

# Reset indices for comparison
df_result.reset_index(drop=True, inplace=True)
df_expected.reset_index(drop=True, inplace=True)

# Compare the DataFrames
try:
    pd.testing.assert_frame_equal(df_result, df_expected)
    print("Test passed: The output data matches the expected results.")
except AssertionError as e:
    print("Test failed: The output data does not match the expected results.")
    print(str(e))
