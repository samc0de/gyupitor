FROM python:3.11-slim-bookworm

ENV PATH="/root/.local/bin:${PATH}"
ENV PYTHONPATH="/app"

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install redis celery

# Copy the application code
COPY . /app

# Make start script executable and run it
COPY backend/start.sh /app/start.sh
RUN chmod +x /app/start.sh
CMD ["/app/start.sh"]
