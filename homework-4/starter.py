#!/usr/bin/env python
# coding: utf-8

import argparse
import pickle
import pandas as pd
import os

categorical = ['PULocationID', 'DOLocationID']

# Step 1: Set up argument parsing
def parse_args():
    parser = argparse.ArgumentParser(description="Process taxi data for a given year and month")
    parser.add_argument('--year', type=int, default=2023, help="The year of the dataset")
    parser.add_argument('--month', type=int, default=4, help="The month of the dataset")
    return parser.parse_args()



def read_data(filename):


    df = pd.read_parquet(filename)

    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')

    return df

def main():
    args = parse_args()
    # Extract the year and month from the arguments
    year = args.year
    month = args.month

    with open('model.bin', 'rb') as f_in:
        dv, model = pickle.load(f_in)

    df = read_data('https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-03.parquet')

    dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(dicts)
    y_pred = model.predict(X_val)


    deviation = abs(df['duration'] - y_pred)
    mean_deviation = deviation.mean()
    print(f"Q1. Notebook. standard deviation: {mean_deviation}")

    #Create new dataframe with ride_id column and write in new file
    df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')

    # Prepare the dataframe
    df_result = pd.DataFrame({
        'ride_id': df['ride_id'],
        'predicted_duration': y_pred
    })

    # Create new file
    output_file = 'yellow_tripdata_2024-03_with_ride_id.parquet'

    df_result.to_parquet(
        output_file,
        engine='pyarrow',
        compression=None,
        index=False
    )

    # Print mean predicted duration
    mean_predicted_duration = y_pred.mean()
    print(f"Q5. Parametrize the script. Mean predicted duration: {mean_predicted_duration:.2f} minutes")

    file_size = os.path.getsize(output_file) / (1024 * 1024)  # Convert bytes to MB
    print(f"Q2: preparing the output. file size: {file_size:.2f} MB")



# Execute the script
if __name__ == '__main__':
    main()