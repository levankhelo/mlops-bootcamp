#!/usr/bin/env python
# coding: utf-8

# In[35]:


get_ipython().system('pip freeze | grep scikit-learn')


# In[36]:


get_ipython().system('python -V')


# In[37]:


import pickle
import pandas as pd


# In[38]:


with open('model.bin', 'rb') as f_in:
    dv, model = pickle.load(f_in)


# In[39]:


categorical = ['PULocationID', 'DOLocationID']


def read_data(filename):
    df = pd.read_parquet(filename)

    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')

    return df


# In[40]:


df = read_data('https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-03.parquet')


# In[41]:


dicts = df[categorical].to_dict(orient='records')
X_val = dv.transform(dicts)
y_pred = model.predict(X_val)


# In[42]:


deviation = abs(df['duration'] - y_pred)
mean_deviation = deviation.mean()
print(f"Q1. Notebook. standard deviation: {mean_deviation}")


# In[56]:


#Create new dataframe with ride_id column and write in new file
year = 2024  # Assuming the dataset is for 2024
month = 3    # March as indicated in the filename

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


# In[58]:


# Step 4: Check the size of the output file
import os

file_size = os.path.getsize(output_file) / (1024 * 1024)  # Convert bytes to MB
print(f"Q2: preparing the output. file size: {file_size:.2f} MB")


# In[67]:


pip list --format=freeze > requirements.txt

