import pandas as pd

df = pd.read_parquet('output.parquet')
total_predicted_duration = df['predicted_duration'].sum()
print(total_predicted_duration)
