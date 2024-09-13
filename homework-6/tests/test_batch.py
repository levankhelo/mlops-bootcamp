import pandas as pd
from datetime import datetime
from batch import prepare_data

def dt(hour, minute, second=0):
    return datetime(2023, 1, 1, hour, minute, second)

def test_prepare_data():
    # Sample input data
    data = [
        (None, None, dt(1, 1), dt(1, 10)),        # Duration: 9 minutes
        (1, 1, dt(1, 2), dt(1, 10)),              # Duration: 8 minutes
        (1, None, dt(1, 2, 0), dt(1, 2, 59)),     # Duration: ~0.98 minutes
        (3, 4, dt(1, 2, 0), dt(2, 2, 1)),         # Duration: ~60 minutes
    ]
    columns = ['PULocationID', 'DOLocationID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime']
    df_input = pd.DataFrame(data, columns=columns)

    categorical = ['PULocationID', 'DOLocationID']

    # Apply the prepare_data function
    df_actual = prepare_data(df_input, categorical)

    # Define expected output
    expected_data = [
        {
            'PULocationID': '-1',
            'DOLocationID': '-1',
            'tpep_pickup_datetime': dt(1, 1),
            'tpep_dropoff_datetime': dt(1, 10),
            'duration': 9.0
        },
        {
            'PULocationID': '1',
            'DOLocationID': '1',
            'tpep_pickup_datetime': dt(1, 2),
            'tpep_dropoff_datetime': dt(1, 10),
            'duration': 8.0
        }
    ]
    df_expected = pd.DataFrame(expected_data)

    # Reorder columns to match
    df_expected = df_expected[df_actual.columns]

    # Reset index for comparison
    df_actual.reset_index(drop=True, inplace=True)
    df_expected.reset_index(drop=True, inplace=True)

    # Assert that the actual and expected DataFrames are equal
    pd.testing.assert_frame_equal(df_actual, df_expected)

# Run the test
test_prepare_data()
print("Test passed!")
