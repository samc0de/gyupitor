# BigQuery Cost Optimization Application: Architecture Document

This document outlines the architecture, technology stack, data model, and deployment strategy for the BigQuery Cost Optimization Application.

## 1. System Architecture

The system is designed as a periodic, serverless job that analyzes BigQuery usage data, stores its findings, and exposes them through a simple API.

### Components:

*   **Cloud Scheduler:** A cron job trigger that initiates the analysis process on a defined schedule (e.g., daily).
*   **Cloud Run Job (Analyzer):** A containerized Python application responsible for the core logic. It queries the BigQuery `INFORMATION_SCHEMA` to find expensive queries, analyzes them against a set of optimization rules, and writes the results and recommendations to a results table in BigQuery.
*   **BigQuery (Data Source & Sink):**
    *   **Source:** The `INFORMATION_SCHEMA.JOBS_BY_*` views provide the raw data for analysis.
    *   **Sink:** A dedicated table (`optimization_findings`) stores the structured output from the analyzer job.
*   **Cloud Run Service (API):** A lightweight, containerized FastAPI application that provides an HTTP endpoint to query the findings stored in the `optimization_findings` table.
*   **CI/CD (Cloud Build):** Automates the process of building container images from the source code and deploying them to Cloud Run.

### Architecture Diagram (Mermaid)

```mermaid
graph TD
    subgraph "Google Cloud Platform"
        A[Cloud Scheduler <br> (Daily Cron)] --> B{Cloud Run Job <br> (Analyzer)};
        B -- 1. Queries Job History --> C[BigQuery <br> INFORMATION_SCHEMA.JOBS];
        B -- 2. Analyzes Queries --> B;
        B -- 3. Writes Findings --> D[BigQuery Table <br> bq_cost_optimizer.findings];
        E{Cloud Run Service <br> (FastAPI)} -- 4. Reads Findings --> D;
        F[Developer/Client] -- 5. GET /findings --> E;
    end

    subgraph "CI/CD Pipeline"
        G[Git Repository] -- on push --> H[Cloud Build];
        H -- Builds & Pushes Image --> I[Artifact Registry];
        H -- Deploys --> B;
        H -- Deploys --> E;
    end

    style A fill:#4285F4,stroke:#333,stroke-width:2px,color:#fff
    style B fill:#34A853,stroke:#333,stroke-width:2px,color:#fff
    style C fill:#FBBC05,stroke:#333,stroke-width:2px,color:#fff
    style D fill:#FBBC05,stroke:#333,stroke-width:2px,color:#fff
    style E fill:#34A853,stroke:#333,stroke-width:2px,color:#fff
    style F fill:#EA4335,stroke:#333,stroke-width:2px,color:#fff
```

## 2. Technology Stack

*   **Programming Language:** Python 3.10+
*   **Data Processing:**
    *   `google-cloud-bigquery`: Python client for interacting with BigQuery.
    *   `pandas`: For data manipulation and analysis (optional, can be done in SQL).
*   **API Framework:** FastAPI
*   **Containerization:** Docker
*   **Cloud Platform:** Google Cloud Platform (GCP)
*   **Core Services:**
    *   **Compute:** Cloud Run (for both Job and Service)
    *   **Scheduling:** Cloud Scheduler
    *   **Database:** BigQuery
    *   **Container Registry:** Artifact Registry
    *   **CI/CD:** Cloud Build

## 3. Data Model

A new BigQuery dataset and table will be created to store the analysis results.

*   **Dataset:** `bq_cost_optimizer`
*   **Table:** `findings`

The table will be partitioned by `analysis_date` for efficient querying over time.

### `findings` Table Schema:

| Column Name            | Data Type     | Mode     | Description                                                                                               |
| ---------------------- | ------------- | -------- | --------------------------------------------------------------------------------------------------------- |
| `analysis_date`        | `DATE`        | REQUIRED | The date the analysis was run. This will be the table's partitioning column.                              |
| `finding_id`           | `STRING`      | REQUIRED | A unique identifier for the finding (e.g., a hash of the query and timestamp).                            |
| `project_id`           | `STRING`      | REQUIRED | The GCP project ID where the query was run.                                                               |
| `user_email`           | `STRING`      | REQUIRED | The user or service account that executed the query.                                                      |
| `job_id`               | `STRING`      | NULLABLE | The specific BigQuery job ID that triggered this finding.                                                 |
| `query_hash`           | `STRING`      | REQUIRED | MD5 hash of the normalized query text to group similar queries.                                           |
| `query_text`           | `STRING`      | REQUIRED | The full text of the inefficient query.                                                                   |
| `total_bytes_billed`   | `INTEGER`     | REQUIRED | The number of bytes billed for the query execution.                                                       |
| `start_time`           | `TIMESTAMP`   | REQUIRED | The start time of the query job.                                                                          |
| `recommendations`      | `RECORD`      | REPEATED | An array of structured recommendations.                                                                   |
| `recommendations.code` | `STRING`      | NULLABLE | A short code for the recommendation type (e.g., `ADD_PARTITION_FILTER`, `AVOID_SUBQUERY_SCAN`).             |
| `recommendations.details` | `STRING`   | NULLABLE | A human-readable description of the recommended optimization.                                             |
| `estimated_cost`       | `FLOAT`       | NULLABLE | The estimated cost of this single query in USD.                                                           |
| `estimated_savings`    | `FLOAT`       | NULLABLE | The potential savings in USD if the recommendations are applied.                                          |

## 4. Deployment Strategy

The application will be deployed using a combination of `gcloud` CLI commands and a `cloudbuild.yaml` file for automation.

### Prerequisites:

1.  Enable APIs: Cloud Build, Cloud Run, Artifact Registry, Cloud Scheduler.
2.  Create a service account for the Cloud Run jobs with `BigQuery User` and `BigQuery Data Editor` (for writing results) roles.

### Step-by-Step Deployment Plan:

1.  **Repository Setup:**
    *   Structure the code in a Git repository.
    *   `analyzer/`: Contains the Dockerfile and Python code for the analysis job.
    *   `api/`: Contains the Dockerfile and Python code for the FastAPI application.
    *   `cloudbuild.yaml`: The CI/CD pipeline definition at the root.
    *   `scripts/`: Deployment scripts.

2.  **Create BigQuery Resources:**
    *   Run a SQL script to create the `bq_cost_optimizer` dataset and the `findings` table.
        ```sql
        CREATE SCHEMA IF NOT EXISTS bq_cost_optimizer;
        CREATE TABLE IF NOT EXISTS bq_cost_optimizer.findings (
            analysis_date DATE,
            finding_id STRING,
            project_id STRING,
            user_email STRING,
            job_id STRING,
            query_hash STRING,
            query_text STRING,
            total_bytes_billed INT64,
            start_time TIMESTAMP,
            recommendations ARRAY<STRUCT<code STRING, details STRING>>,
            estimated_cost FLOAT64,
            estimated_savings FLOAT64
        )
        PARTITION BY analysis_date
        OPTIONS(
            description="Stores findings from the BigQuery cost optimization analyzer"
        );
        ```

3.  **CI/CD Pipeline (`cloudbuild.yaml`):**
    *   Define steps to build the Docker image for the `analyzer` and `api`.
    *   Push the built images to Artifact Registry.
    *   Deploy the `analyzer` image as a Cloud Run Job.
    *   Deploy the `api` image as a Cloud Run Service, making it publicly accessible (or internal, depending on requirements).

4.  **Create the Cloud Scheduler Job:**
    *   Use the `gcloud` CLI to create a scheduler job that triggers the Cloud Run Job.
    *   This command will run daily at 2 AM.
        ```bash
        gcloud scheduler jobs create http bq-cost-analyzer-job \
          --schedule "0 2 * * *" \
          --http-method POST \
          --uri "https://<REGION>-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/<PROJECT_ID>/jobs/bq-analyzer:run" \
          --oauth-service-account-email "cicd-service-account@<PROJECT_ID>.iam.gserviceaccount.com" \
          --oauth-token-audience "https://<REGION>-run.googleapis.com/"
        ```
    *   (Note: The URI and authentication method depend on the specific Cloud Run Job setup. The example above shows how to invoke the job's `:run` endpoint.)

5.  **Expose the API:**
    *   The Cloud Run Service for the API will have a stable URL provided upon deployment.
    *   Configure IAM to control access to the API endpoint as needed. By default, new Cloud Run services are private. It can be made public or accessible only to specific principals.

This setup creates a fully automated, serverless, and scalable system for continuously monitoring and reporting on BigQuery cost optimization opportunities.
