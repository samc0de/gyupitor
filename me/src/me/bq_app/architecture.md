# BigQuery Cost Optimization Application: Architecture

**Author:** Cloud Software and DevOps Architect
**Version:** 1.0
**Date:** 2023-10-27

## 1. Overview

This document outlines the architecture for the BigQuery Cost Optimization Application. The system is designed to ingest, store, and serve structured data derived from BigQuery performance analysis files. The primary goal is to provide a relational view of query jobs, their raw SQL, and detailed execution timelines, enabling easier analysis and optimization.

The architecture is designed for local deployment using Docker, ensuring portability and ease of setup.

## 2. System Components & Technology Stack

The application consists of three main components: a data ingestion service, a relational database, and a REST API.

### 2.1. Architecture Diagram

The following diagram illustrates the flow of data from the source files into the database and how the API serves this data to a potential client.

```mermaid
graph TD
    subgraph "File System (.bq_cache)"
        A[query_results/*.jsonl]
        B[raw_queries/*.sql]
        C[raw_timelines/*.json]
    end

    subgraph "Application (Docker Container)"
        D[Python Ingestion Script]
        E[SQLite Database (bq_app.db)]
        F[FastAPI REST API]
    end

    subgraph "User"
        G[API Client / Browser]
    end

    A -- Reads --> D
    B -- Reads --> D
    C -- Reads --> D

    D -- Writes to --> E

    F -- Reads from --> E
    G -- Interacts with --> F

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#f9f,stroke:#333,stroke-width:2px
    style C fill:#f9f,stroke:#333,stroke-width:2px
    style E fill:#ccf,stroke:#333,stroke-width:2px
```

### 2.2. Chosen Technologies

| Component | Technology | Justification |
|-----------|------------|---------------|
| **Backend Language** | **Python 3.10+** | Excellent ecosystem for data parsing (e.g., `json`, `pandas`), web frameworks, and database interaction. Widely used and easy to learn. |
| **API Framework** | **FastAPI** | A modern, high-performance web framework for building APIs with Python. It offers automatic data validation, serialization, and interactive API documentation (Swagger UI), which accelerates development. |
| **Database** | **SQLite** | A serverless, self-contained, file-based SQL database engine. It is perfect for local development and containerized applications as it requires zero configuration and is included in Python's standard library. |
| **Containerization** | **Docker & Docker Compose** | The industry standard for creating, deploying, and running applications in isolated environments. Docker Compose simplifies the management of multi-service applications (e.g., ingestion script, API server) for local deployment. |

## 3. Data Model and Ingestion

The core of the application is its ability to transform flat files into a structured, relational format.

### 3.1. Data Model (SQL Schema)

We will use three tables to represent the relationships between queries, jobs, and timelines.

*   `queries`: Stores the unique raw SQL queries. The `query_hash` is the natural primary key.
*   `jobs`: Stores the metadata for each individual BigQuery job execution from the main results file. It links to a specific query via a foreign key.
*   `timelines`: Stores the raw JSON content of the execution timeline for each job.

```sql
-- Table to store the unique raw SQL queries
CREATE TABLE IF NOT EXISTS queries (
    query_hash TEXT PRIMARY KEY,
    raw_sql TEXT NOT NULL
);

-- Table to store individual query job executions
CREATE TABLE IF NOT EXISTS jobs (
    job_id TEXT PRIMARY KEY,
    query_hash TEXT NOT NULL,
    timeline_details_file TEXT,
    total_slot_ms INTEGER,
    total_bytes_processed INTEGER,
    creation_time TIMESTAMP,
    user_email TEXT,
    -- Add other relevant fields from the main results file as needed
    FOREIGN KEY (query_hash) REFERENCES queries(query_hash)
);

-- Table to store the detailed timeline data for each job
CREATE TABLE IF NOT EXISTS timelines (
    job_id TEXT PRIMARY KEY,
    timeline_json TEXT NOT NULL,
    FOREIGN KEY (job_id) REFERENCES jobs(job_id)
);
```

### 3.2. Data Ingestion Plan

An ingestion script (`ingest.py`) will perform the following steps:

1.  **Initialize Database:** Create the SQLite database file (`bq_app.db`) and execute the `CREATE TABLE` statements if the tables do not already exist.
2.  **Process Raw Queries:**
    *   Iterate through all `.sql` files in `.bq_cache/raw_queries/`.
    *   For each file, extract the `query_hash` from the filename.
    *   Read the content of the SQL file.
    *   Insert the `query_hash` and `raw_sql` into the `queries` table. This populates the parent table first to satisfy foreign key constraints.
3.  **Process Job Results and Timelines:**
    *   Read the main results file from `.bq_cache/query_results/` line by line (assuming it's a JSONL file).
    *   For each JSON object (representing a job):
        *   Extract all relevant fields (`job_id`, `query_hash`, `total_slot_ms`, `timeline_details_file`, etc.).
        *   Insert the extracted data into the `jobs` table.
        *   If `timeline_details_file` is present, construct the full path to the timeline file (e.g., `.bq_cache/raw_timelines/{timeline_details_file}`).
        *   Read the entire content of the timeline JSON file.
        *   Insert the `job_id` and the raw JSON content into the `timelines` table.

## 4. Deployment Strategy (Local Docker)

The application will be packaged for easy local deployment using Docker and Docker Compose.

### 4.1. Project Structure

```
.
├── .bq_cache/              # Source data (pre-existing)
│   ├── query_results/
│   ├── raw_queries/
│   └── raw_timelines/
├── src/
│   ├── main.py             # FastAPI application
│   ├── ingest.py           # Data ingestion script
│   └── db.py               # Database connection and schema setup
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

### 4.2. Step-by-Step Deployment Plan

1.  **Prerequisites:** Install Docker and Docker Compose on the local machine.

2.  **Create `Dockerfile`:** Define the container image for the Python application.
    ```dockerfile
    FROM python:3.10-slim

    WORKDIR /app

    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt

    COPY ./src /app

    # The API will be the default command
    CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
    ```

3.  **Create `requirements.txt`:** List Python dependencies.
    ```
    fastapi
    uvicorn[standard]
    pandas