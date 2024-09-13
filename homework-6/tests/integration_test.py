import os
import pandas as pd
from datetime import datetime

# Helper function to create datetime objects
def dt(hour, minute, second=0):
    return datetime(2023, 1, 1, hour, minute, second)

# Sample data as per Q3
data = [
    (None, None, dt(1, 1), dt(1, 10)),        # Duration: 9 minutes
    (1, 1, dt(1, 2), dt(1, 10)),              # Duration: 8 minutes
    (1, None, dt(1, 2, 0), dt(1, 2, 59)),     # Duration: ~0.98 minutes
    (3, 4, dt(1, 2, 0), dt(2, 2, 1)),         # Duration: ~60 minutes
]
columns = ['PULocationID', 'DOLocationID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime']

# Create the DataFrame
df_input = pd.DataFrame(data, columns=columns)

# Define the S3 input file path for January 2023
year = 2023
month = 1
input_file = f's3://nyc-duration/in/{year:04d}-{month:02d}.parquet'

# Get S3 endpoint URL from environment variable
s3_endpoint_url = os.getenv('S3_ENDPOINT_URL', 'http://localhost:4566')

# Configure storage options for S3
options = {
    'client_kwargs': {
        'endpoint_url': s3_endpoint_url
    }
}

# Save the DataFrame to S3 using the provided snippet
df_input.to_parquet(
    input_file,
    engine='pyarrow',
    compression=None,
    index=False,
    storage_options=options
)
