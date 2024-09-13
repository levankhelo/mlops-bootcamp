import sys
import pickle
import pandas as pd

def read_data(filename):
    """
    Read data from a parquet file.

    Args:
        filename (str): The path to the parquet file.

    Returns:
        pd.DataFrame: Raw data.
    """
    df = pd.read_parquet(filename)
    return df

def prepare_data(df, categorical):
    """
    Preprocess the data by computing duration and handling categorical variables.

    Args:
        df (pd.DataFrame): The raw data.
        categorical (list): List of categorical column names.

    Returns:
        pd.DataFrame: Preprocessed data.
    """
    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60

    # Filter records with duration between 1 and 60 minutes
    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    # Fill missing values and convert categorical columns to strings
    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')

    return df

def main(year, month):
    """
    Main function to process the data and make predictions.

    Args:
        year (int): The year of the data.
        month (int): The month of the data.
    """
    input_file = f'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year:04d}-{month:02d}.parquet'
    output_file = f'output/yellow_tripdata_{year:04d}-{month:02d}.parquet'

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
    df_result.to_parquet(output_file, engine='pyarrow', index=False)

if __name__ == "__main__":
    year = int(sys.argv[1])
    month = int(sys.argv[2])
    main(year, month)
