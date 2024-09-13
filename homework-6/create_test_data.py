import pandas as pd
from datetime import datetime

def dt(hour, minute, second=0):
    return datetime(2023, 1, 1, hour, minute, second)

data = [
    (None, None, dt(1, 1), dt(1, 10)),         # Duration: 9 minutes
    (1, 1, dt(1, 2), dt(1, 10)),               # Duration: 8 minutes
    (1, None, dt(1, 2, 0), dt(1, 2, 59)),      # Duration: ~0.98 minutes (filtered out)
    (3, 4, dt(1, 2, 0), dt(2, 2, 1)),          # Duration: ~60.02 minutes (filtered out)
]
columns = ['PULocationID', 'DOLocationID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime']

df_input = pd.DataFrame(data, columns=columns)

df_input.to_parquet(
    'test_input.parquet',
    engine='pyarrow',
    compression=None,
    index=False
)
