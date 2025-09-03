#!/bin/bash

# Change to the correct directory
cd /app/me/bq_app/backend

# Start the Celery worker in the background
celery -A main.celery_app worker --loglevel=info &

# Start the FastAPI application
uvicorn main:app --host 0.0.0.0 --port 8000
