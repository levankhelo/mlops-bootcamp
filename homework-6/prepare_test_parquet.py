import pandas as pd
from datetime import datetime

def dt(hour, minute, second=0):
    return datetime(2023, 1, 1, hour, minute, second)

# Sample data from your unit test
data = [
    (None, None, dt(1, 1), dt(1, 10)),        # Duration: 9 minutes
    (1, 1, dt(1, 2), dt(1, 10)),              # Duration: 8 minutes
    (1, None, dt(1, 2, 0), dt(1, 2, 59)),     # Duration: ~0.98 minutes
    (3, 4, dt(1, 2, 0), dt(2, 2, 1)),         # Duration: ~60.02 minutes
]
columns = ['PULocationID', 'DOLocationID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime']

# Create the DataFrame
df_test = pd.DataFrame(data, columns=columns)

# Save the DataFrame as a Parquet file
df_test.to_parquet('test_input.parquet', engine='pyarrow', index=False)
