import sys
import os
import pickle
import pandas as pd

def get_input_path(year, month):
    default_input_pattern = 'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year:04d}-{month:02d}.parquet'
    input_pattern = os.getenv('INPUT_FILE_PATTERN', default_input_pattern)
    return input_pattern.format(year=year, month=month)

def get_output_path(year, month):
    default_output_pattern = 's3://nyc-duration-prediction-alexey/taxi_type=fhv/year={year:04d}/month={month:02d}/predictions.parquet'
    output_pattern = os.getenv('OUTPUT_FILE_PATTERN', default_output_pattern)
    return output_pattern.format(year=year, month=month)

def get_s3_options():
    if os.getenv('S3_ENDPOINT_URL'):
        s3_endpoint_url = os.getenv('S3_ENDPOINT_URL')
        return {
            'client_kwargs': {
                'endpoint_url': s3_endpoint_url
            }
        }
    return None

def read_data(filename):
    """
    Read data from a parquet file, either from local filesystem or S3.

    Args:
        filename (str): The path to the parquet file.

    Returns:
        pd.DataFrame: Raw data.
    """
    if filename.startswith('s3://'):
        # Check if S3_ENDPOINT_URL is set
        s3_endpoint_url = os.getenv('S3_ENDPOINT_URL')
        if s3_endpoint_url:
            # Configure storage options to point to Localstack
            options = {
                'client_kwargs': {
                    'endpoint_url': s3_endpoint_url
                }
            }
            df = pd.read_parquet(filename, storage_options=options)
        else:
            # Read from actual S3 service
            df = pd.read_parquet(filename)
    else:
        # Read from local filesystem or HTTP URL
        df = pd.read_parquet(filename)
    return df

def save_data(df, output_file):
    """
    Save DataFrame to a Parquet file, either to local filesystem or S3.

    Args:
        df (pd.DataFrame): The DataFrame to save.
        output_file (str): The destination file path.
    """
    if output_file.startswith('s3://'):
        s3_endpoint_url = os.getenv('S3_ENDPOINT_URL')
        if s3_endpoint_url:
            # Configure storage options to point to Localstack
            options = {
                'client_kwargs': {
                    'endpoint_url': s3_endpoint_url
                }
            }
            df.to_parquet(
                output_file,
                engine='pyarrow',
                compression=None,
                index=False,
                storage_options=options
            )
        else:
            # Save to actual S3
            df.to_parquet(
                output_file,
                engine='pyarrow',
                compression=None,
                index=False
            )
    else:
        # Save to local filesystem
        df.to_parquet(
            output_file,
            engine='pyarrow',
            compression=None,
            index=False
        )


def prepare_data(df, categorical):
    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60

    # Filter records with duration between 1 and 60 minutes
    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    # Fill missing values and convert categorical columns to strings
    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')

    return df

def main(year, month):
    input_file = get_input_path(year, month)
    output_file = get_output_path(year, month)

    with open('model.bin', 'rb') as f_in:
        dv, lr = pickle.load(f_in)

    categorical = ['PULocationID', 'DOLocationID']

    # Read and prepare data
    df = read_data(input_file)
    df = prepare_data(df, categorical)
    df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')

    # Feature engineering
    dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(dicts)

    # Make predictions
    y_pred = lr.predict(X_val)
    print('Predicted mean duration:', y_pred.mean())

    # Save results
    df_result = pd.DataFrame()
    df_result['ride_id'] = df['ride_id']
    df_result['predicted_duration'] = y_pred

    # Save the data using save_data
    save_data(df_result, output_file)

if __name__ == "__main__":
    year = int(sys.argv[1])
    month = int(sys.argv[2])
    main(year, month)
