FROM python:3.9-slim

WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main application file
COPY main.py .

# Copy the recommendations data from analysis directory relative to the build context
# The implementation directory is the build context, so ../analysis is correct path
COPY ../analysis /analysis

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
# Use "main:app" because main.py is copied to /app and the app instance is named "app"
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
