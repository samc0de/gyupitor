import sqlite3
import os

DATABASE_FILE = os.environ.get("DB_PATH", "./bq_app.db")

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS queries (
            query_hash TEXT PRIMARY KEY,
            raw_sql TEXT NOT NULL
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            query_hash TEXT NOT NULL,
            timeline_details_file TEXT,
            total_slot_ms INTEGER,
            total_bytes_processed INTEGER,
            creation_time TIMESTAMP,
            user_email TEXT,
            FOREIGN KEY (query_hash) REFERENCES queries(query_hash)
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS timelines (
            job_id TEXT PRIMARY KEY,
            timeline_json TEXT NOT NULL,
            FOREIGN KEY (job_id) REFERENCES jobs(job_id)
        );
    """)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_tables()
    print(f"Database initialized at {DATABASE_FILE}")
