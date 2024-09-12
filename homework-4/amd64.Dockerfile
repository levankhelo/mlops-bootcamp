# Use the provided base image
FROM agrigorev/zoomcamp-model:mlops-2024-3.10.13-slim

# Copy the Python script and requirements file to the container
COPY starter.py starter.py
COPY requirements.txt requirements.txt

# Install the dependencies inside the container
RUN pip install --no-cache-dir -r requirements.txt

# Set the default command to run the Python script with year and month arguments
ENTRYPOINT ["python", "starter.py", "--year", "2023", "--month", "5"]
