import os
import json
import hashlib
from datetime import datetime
from db import create_tables, get_db_connection

# Define paths relative to the container's /app directory
BQ_CACHE_DIR = os.environ.get("BQ_CACHE_DIR", ".bq_cache")
QUERY_RESULTS_DIR = os.path.join(BQ_CACHE_DIR, "query_results")
RAW_QUERIES_DIR = os.path.join(BQ_CACHE_DIR, "raw_queries")
RAW_TIMELINES_DIR = os.path.join(BQ_CACHE_DIR, "raw_timelines")

def calculate_query_hash(sql_content):
    return hashlib.sha256(sql_content.encode('utf-8')).hexdigest()

def ingest_raw_queries():
    conn = get_db_connection()
    cursor = conn.cursor()
    print(f"Ingesting raw queries from {RAW_QUERIES_DIR}...")
    for filename in os.listdir(RAW_QUERIES_DIR):
        if filename.endswith(".sql"):
            filepath = os.path.join(RAW_QUERIES_DIR, filename)
            with open(filepath, 'r') as f:
                raw_sql = f.read()
            query_hash = filename.replace('.sql', '') # Assuming filename is the hash
            
            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO queries (query_hash, raw_sql) VALUES (?, ?)",
                    (query_hash, raw_sql)
                )
                if cursor.rowcount > 0:
                    print(f"  Inserted query: {query_hash}")
                else:
                    print(f"  Skipped existing query: {query_hash}")
            except Exception as e:
                print(f"Error inserting query {query_hash}: {e}")
    conn.commit()
    conn.close()
    print("Raw query ingestion complete.")

def ingest_job_results():
    conn = get_db_connection()
    cursor = conn.cursor()
    print(f"Ingesting job results from {QUERY_RESULTS_DIR}...")
    for filename in os.listdir(QUERY_RESULTS_DIR):
        if filename.endswith(".jsonl"):
            filepath = os.path.join(QUERY_RESULTS_DIR, filename)
            with open(filepath, 'r') as f:
                for line in f:
                    try:
                        job_data = json.loads(line)
                        job_id = job_data.get('job_id')
                        query_hash = job_data.get('query_hash')
                        timeline_details_file = job_data.get('timeline_details_file')
                        total_slot_ms = job_data.get('total_slot_ms')
                        total_bytes_processed = job_data.get('total_bytes_processed')
                        creation_time_str = job_data.get('creation_time')
                        user_email = job_data.get('user_email')

                        # Convert creation_time to a format suitable for TIMESTAMP
                        creation_time = None
                        if creation_time_str:
                            try:
                                # Assuming ISO format 'YYYY-MM-DD HH:MM:SS.ffffffZ'
                                creation_time = datetime.strptime(creation_time_str.split('.')[0], '%Y-%m-%d %H:%M:%S').isoformat()
                            except ValueError:
                                pass # Handle other formats if necessary

                        if not all([job_id, query_hash]):
                            print(f"  Skipping malformed job entry: {job_data.get('job_id')}")
                            continue

                        try:
                            cursor.execute(
                                "INSERT OR IGNORE INTO jobs (job_id, query_hash, timeline_details_file, total_slot_ms, total_bytes_processed, creation_time, user_email) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                (job_id, query_hash, timeline_details_file, total_slot_ms, total_bytes_processed, creation_time, user_email)
                            )
                            if cursor.rowcount > 0:
                                print(f"  Inserted job: {job_id}")
                                # Ingest timeline if available
                                if timeline_details_file:
                                    ingest_timeline(job_id, timeline_details_file, cursor)
                            else:
                                print(f"  Skipped existing job: {job_id}")
                        except Exception as e:
                            print(f"Error inserting job {job_id}: {e}")
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON from line: {line.strip()} - {e}")
    conn.commit()
    conn.close()
    print("Job results ingestion complete.")

def ingest_timeline(job_id, timeline_details_file, cursor):
    timeline_filepath = os.path.join(RAW_TIMELINES_DIR, timeline_details_file)
    if os.path.exists(timeline_filepath):
        with open(timeline_filepath, 'r') as f:
            timeline_json = f.read()
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO timelines (job_id, timeline_json) VALUES (?, ?)",
                (job_id, timeline_json)
            )
            if cursor.rowcount > 0:
                print(f"    Inserted timeline for job: {job_id}")
            # else: print(f"    Skipped existing timeline for job: {job_id}") # Too verbose
        except Exception as e:
            print(f"Error inserting timeline for job {job_id}: {e}")
    else:
        print(f"    Timeline file not found for job {job_id}: {timeline_filepath}")


if __name__ == '__main__':
    print("Starting data ingestion...")
    create_tables()
    ingest_raw_queries()
    ingest_job_results()
    print("Data ingestion finished.")
