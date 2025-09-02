import os
import json
import shutil
import logging
from sqlalchemy.orm import Session
from db import SessionLocal
import models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CACHE_DIR = '.bq_cache'
RAW_QUERIES_DIR = f'{CACHE_DIR}/raw_queries'
RAW_TIMELINES_DIR = f'{CACHE_DIR}/raw_timelines'
PROCESSED_QUERIES_DIR = f'{CACHE_DIR}/processed_queries'
PROCESSED_TIMELINES_DIR = f'{CACHE_DIR}/processed_timelines'


def ensure_cache_dirs_exist():
    """Creates the cache directories if they don't already exist."""
    os.makedirs(RAW_QUERIES_DIR, exist_ok=True)
    os.makedirs(RAW_TIMELINES_DIR, exist_ok=True)
    os.makedirs(PROCESSED_QUERIES_DIR, exist_ok=True)
    os.makedirs(PROCESSED_TIMELINES_DIR, exist_ok=True)

def ingest_new_files():
    ensure_cache_dirs_exist()
    db: Session = SessionLocal()
    try:
        # Process timelines first to get metadata
        for timeline_filename in os.listdir(RAW_TIMELINES_DIR):
            if not timeline_filename.endswith('.json'):
                continue

            timeline_path = os.path.join(RAW_TIMELINES_DIR, timeline_filename)
            with open(timeline_path, 'r') as f:
                timeline_data = json.load(f)

            query_hash = timeline_data.get('query_hash')
            if not query_hash:
                logger.warning(f"Skipping timeline {timeline_filename} due to missing query_hash.")
                continue

            # Check if this query hash already exists
            existing_query = db.query(models.Query).filter(models.Query.query_hash == query_hash).first()
            if existing_query:
                logger.info(f"Query with hash {query_hash} already exists. Skipping.")
                # Move the processed file
                shutil.move(timeline_path, os.path.join(PROCESSED_TIMELINES_DIR, timeline_filename))
                continue

            # Find the corresponding SQL file
            sql_filename = f"{query_hash}.sql"
            sql_path = os.path.join(RAW_QUERIES_DIR, sql_filename)

            if not os.path.exists(sql_path):
                logger.warning(f"SQL file for query_hash {query_hash} not found. Skipping timeline {timeline_filename}.")
                continue

            with open(sql_path, 'r') as f:
                query_text = f.read()

            # Create new Query record
            new_query = models.Query(
                query_hash=query_hash,
                query_text=query_text,
                timestamp=timeline_data.get('timestamp'),
                total_slot_ms=timeline_data.get('total_slot_ms'),
                total_bytes_processed=timeline_data.get('total_bytes_processed'),
                total_rows=timeline_data.get('total_rows')
            )
            db.add(new_query)
            db.commit()
            logger.info(f"Ingested query with hash: {query_hash}")

            # Move processed files
            shutil.move(timeline_path, os.path.join(PROCESSED_TIMELINES_DIR, timeline_filename))
            shutil.move(sql_path, os.path.join(PROCESSED_QUERIES_DIR, sql_filename))

    finally:
        db.close()
