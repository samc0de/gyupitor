import os
import json
import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import SessionLocal, engine

# Ensure the database tables are created
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def ingest_data(db: Session, bq_cache_path: str = ".bq_cache"):
    query_results_path = os.path.join(bq_cache_path, "query_results")
    raw_queries_path = os.path.join(bq_cache_path, "raw_queries")
    raw_timelines_path = os.path.join(bq_cache_path, "raw_timelines")

    if not os.path.exists(query_results_path):
        print(f"Error: {query_results_path} not found. Please ensure .bq_cache is populated.")
        return

    # Ingest query_jobs and raw_queries
    for filename in os.listdir(query_results_path):
        if filename.endswith(".jsonl"):
            file_path = os.path.join(query_results_path, filename)
            with open(file_path, 'r') as f:
                for line in f:
                    job_data = json.loads(line)

            for job_data in data:
                # Ingest RawQuery first
                query_hash = job_data.get("query_hash")
                if query_hash:
                    existing_raw_query = crud.get_raw_query(db, query_hash)
                    if not existing_raw_query:
                        raw_query_file = os.path.join(raw_queries_path, f"{query_hash}.sql")
                        if os.path.exists(raw_query_file):
                            with open(raw_query_file, 'r') as qf:
                                query_text = qf.read()
                            raw_query_schema = schemas.RawQueryCreate(
                                query_hash=query_hash,
                                query_text=query_text
                            )
                            crud.create_raw_query(db, raw_query_schema)
                        else:
                            print(f"Warning: Raw query file not found for hash {query_hash}")

                # Ingest QueryJob
                # Convert timestamps from string to datetime objects
                for ts_field in ["creation_time", "start_time", "end_time"]:
                    if job_data.get(ts_field):
                        # Assuming timestamp is in milliseconds since epoch
                        job_data[ts_field] = datetime.fromtimestamp(int(job_data[ts_field]) / 1000)

                job_schema = schemas.QueryJobCreate(**job_data)
                crud.create_query_job(db, job_schema)

    # Ingest execution_timelines
    for filename in os.listdir(raw_timelines_path):
        if filename.endswith(".json"):
            file_path = os.path.join(raw_timelines_path, filename)
            job_id = os.path.splitext(filename)[0] # Assuming filename is job_id.json

            existing_timeline = crud.get_execution_timeline(db, job_id)
            if not existing_timeline:
                with open(file_path, 'r') as f:
                    timeline_json_content = f.read()
                timeline_schema = schemas.ExecutionTimelineCreate(
                    job_id=job_id,
                    timeline_json=timeline_json_content
                )
                crud.create_execution_timeline(db, timeline_schema)

    print("Data ingestion complete.")


if __name__ == "__main__":
    db_gen = get_db()
    db = next(db_gen)
    try:
        # The cache path is fixed inside the container environment
        ingest_data(db, bq_cache_path="/app/.bq_cache")
    finally:
        db_gen.close()

