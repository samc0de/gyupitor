from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from db import get_db_connection
import json

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>BQ Cost Optimizer API</title>
    </head>
    <body>
        <h1>Welcome to the BQ Cost Optimizer API!</h1>
        <p>Access the API documentation at <a href="/docs">/docs</a>.</p>
        <p>Endpoints:</p>
        <ul>
            <li><code>/queries</code>: Get all unique queries.</li>
            <li><code>/queries/{query_hash}</code>: Get a specific query by hash.</li>
            <li><code>/jobs</code>: Get all job executions.</li>
            <li><code>/jobs/{job_id}</code>: Get a specific job by ID.</li>
            <li><code>/jobs/{job_id}/timeline</code>: Get timeline for a specific job.</li>
        </ul>
    </body>
    </html>
    """

@app.get("/queries")
async def get_queries():
    conn = get_db_connection()
    queries = conn.execute("SELECT query_hash, raw_sql FROM queries").fetchall()
    conn.close()
    return [dict(q) for q in queries]

@app.get("/queries/{query_hash}")
async def get_query(query_hash: str):
    conn = get_db_connection()
    query = conn.execute("SELECT query_hash, raw_sql FROM queries WHERE query_hash = ?", (query_hash,)).fetchone()
    conn.close()
    if query is None:
        raise HTTPException(status_code=404, detail="Query not found")
    return dict(query)

@app.get("/jobs")
async def get_jobs():
    conn = get_db_connection()
    jobs = conn.execute("SELECT * FROM jobs").fetchall()
    conn.close()
    return [dict(job) for job in jobs]

@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    conn = get_db_connection()
    job = conn.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
    conn.close()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return dict(job)

@app.get("/jobs/{job_id}/timeline")
async def get_job_timeline(job_id: str):
    conn = get_db_connection()
    timeline = conn.execute("SELECT timeline_json FROM timelines WHERE job_id = ?", (job_id,)).fetchone()
    conn.close()
    if timeline is None:
        raise HTTPException(status_code=404, detail="Timeline not found for this job")
    return json.loads(timeline['timeline_json'])
