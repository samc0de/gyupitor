#!/bin/bash

# Set the path to the bq_cache directory inside the container
BQ_CACHE_DIR="/app/.bq_cache"

# Set the database URL to use the persistent volume
export DATABASE_URL="sqlite:////app/db_data/bq_analyzer.db"

# Run the data ingestion script
# We need to navigate to the backend directory to ensure correct module resolution
echo "--- Running data ingestion ---"
cd /app/backend
python -c 'from ingest import ingest_data, get_db; db_gen = get_db(); db = next(db_gen); ingest_data(db, bq_cache_path=BQ_CACHE_DIR); db_gen.close()' 
cd /app
echo "--- Data ingestion complete ---"

# Start the FastAPI server
echo "--- Starting FastAPI server ---"
uvicorn backend.main:app --host 0.0.0.0 --port 8000