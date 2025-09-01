# BigQuery Cost Optimization Application: Architecture Design

**Author:** Cloud Software and DevOps Architect
**Version:** 1.0
**Status:** Proposed

## 1. Overview

This document outlines the core architecture for a BigQuery Cost Optimization application. The system is designed to periodically analyze BigQuery usage data from `INFORMATION_SCHEMA`, identify high-cost and compute-intensive queries, store these findings, and expose them through a simple API. The architecture prioritizes serverless technologies on Google Cloud Platform (GCP) to ensure scalability, low operational overhead, and cost-effectiveness.

## 2. System Architecture Diagram

The following diagram illustrates the major components of the system and their interactions.

```mermaid
graph TD
    subgraph "Periodic Analysis Pipeline (Scheduled)"
        A[Cloud Scheduler] --triggers (every 24h)--> B[Cloud Function: Job Analyzer];
        B --1. queries usage data--> C[BigQuery INFORMATION_SCHEMA];
        B --2. writes analysis results--> D[Cloud SQL for PostgreSQL];
    end

    subgraph "API & User Access"
        E[User / BI Tool] --HTTPS request--> F[Cloud Run: FastAPI App];
        F --reads analysis data--> D;
    end

    subgraph "CI/CD Pipeline (Automated Deployment)"
        G[Git Repository] --on push--> H[Cloud Build];
        H --builds & pushes image--> I[Artifact Registry];
        H --deploys--> F;
        H --deploys--> B;
    end

    style A fill:#4CAF50,color:#fff
    style B fill:#4CAF50,color:#fff
    style F fill:#2196F3,color:#fff
    style D fill:#FF9800,color:#fff
    style C fill:#00BCD4,color:#fff
    style H fill:#9C27B0,color:#fff
    style I fill:#9C27B0,color:#fff
    style G fill:#9C27B0,color:#fff
```

### Component Responsibilities:

- **Cloud Scheduler**: Triggers the analysis pipeline on a defined schedule (e.g., daily).
- **Cloud Function (Job Analyzer)**: The core data processing engine. It queries BigQuery, processes the job data using Python and Pandas, and writes the summarized results and recommendations to the Cloud SQL database.
- **BigQuery `INFORMATION_SCHEMA`**: The source of truth for job metadata.
- **Cloud SQL for PostgreSQL**: A managed relational database used to store the results of the analysis, including project summaries, lists of expensive jobs, and optimization recommendations.
- **Cloud Run (FastAPI App)**: A containerized, serverless service that hosts the Python-based FastAPI application. It provides RESTful API endpoints for accessing the stored analysis data.
- **CI/CD (Cloud Build)**: An automated pipeline that tests, builds, and deploys changes to both the Cloud Function and the Cloud Run API service upon commits to the source code repository.

## 3. Technology Stack

| Category              | Technology / Service                                 |
| --------------------- | ---------------------------------------------------- |
| **Programming Language**  | Python 3.10+                                         |
| **API Framework**         | FastAPI                                              |
| **Data Processing**       | Pandas                                               |
| **Containerization**      | Docker                                               |
| **Cloud Platform**        | Google Cloud Platform (GCP)                          |
| **Scheduled Compute**     | Cloud Functions (Gen 2)                              |
| **API Hosting**           | Cloud Run                                            |
| **Database**              | Cloud SQL for PostgreSQL                             |
| **Data Source**           | BigQuery `INFORMATION_SCHEMA`                        |
| **CI/CD**                 | Cloud Build                                          |
| **Container Registry**    | Artifact Registry                                    |
| **Scheduling**            | Cloud Scheduler                                      |
| **Infrastructure as Code**| Terraform (Recommended)                              |

## 4. Data Model

The following SQL DDL defines the initial schema for the PostgreSQL database. Timestamps are used to track when data was captured and updated.

```sql
-- To track each time the analysis job is run
CREATE TABLE analysis_runs (
    run_id SERIAL PRIMARY KEY,
    run_timestamp TIMESTAMPTZ DEFAULT NOW(),
    status VARCHAR(50) NOT NULL, -- e.g., 'SUCCESS', 'FAILURE'
    records_processed INT
);

-- Stores aggregated usage data for each project
CREATE TABLE project_summary (
    summary_id SERIAL PRIMARY KEY,
    run_id INT REFERENCES analysis_runs(run_id),
    project_id VARCHAR(255) NOT NULL,
    estimated_on_demand_cost_usd NUMERIC(12, 2),
    total_billed_tb NUMERIC(12, 2),
    total_slot_hours NUMERIC(12, 2),
    num_queries INT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (run_id, project_id) -- Ensures one summary per project per run
);

-- Stores the most expensive jobs identified in a run
CREATE TABLE expensive_jobs (
    id SERIAL PRIMARY KEY,
    run_id INT REFERENCES analysis_runs(run_id),
    project_id VARCHAR(255) NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    job_id VARCHAR(255) NOT NULL UNIQUE,
    total_bytes_billed_tb NUMERIC(12, 2),
    estimated_cost_usd NUMERIC(12, 2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Stores the most compute-intensive jobs identified in a run
CREATE TABLE compute_intensive_jobs (
    id SERIAL PRIMARY KEY,
    run_id INT REFERENCES analysis_runs(run_id),
    project_id VARCHAR(255) NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    job_id VARCHAR(255) NOT NULL UNIQUE,
    total_slot_hours NUMERIC(12, 2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 5. Deployment Plan

This plan outlines the steps to deploy the application on GCP. It assumes the use of Infrastructure as Code (IaC) via Terraform for provisioning resources and Cloud Build for CI/CD.

### Step 1: GCP Project & IAM Setup

1.  **Create GCP Resources**: Use Terraform to provision the following:
    *   A **Cloud SQL for PostgreSQL** instance.
    *   An **Artifact Registry** repository for Docker images.
    *   A dedicated **Service Account (SA)** for the application with the following roles:
        *   `roles/bigquery.user` (to run queries against `INFORMATION_SCHEMA`).
        *   `roles/cloudsql.client` (to connect to the Cloud SQL instance).
        *   `roles/run.invoker` (to allow public access to Cloud Run if needed).
        *   `roles/cloudfunctions.invoker` (to allow Scheduler to invoke the function).
2.  **Secret Manager**: Store the Cloud SQL database password and connection string in Google Secret Manager.

### Step 2: Application Code & Configuration

1.  **Repository Structure**: Organize the source code in a Git repository:
    ```
    /app/           # FastAPI application code
    /functions/     # Cloud Function code
    /terraform/     # Terraform scripts for infrastructure
    cloudbuild.yaml # CI/CD pipeline definition
    Dockerfile      # Dockerfile for the FastAPI app
    requirements.txt
    ```
2.  **Configuration**: Both the Cloud Function and Cloud Run service will be configured via environment variables to fetch database credentials from Secret Manager at runtime.

### Step 3: CI/CD Pipeline (cloudbuild.yaml)

Create a `cloudbuild.yaml` file to define the build, test, and deploy process. The pipeline will have the following stages:

1.  **Install Dependencies**: `pip install -r requirements.txt`.
2.  **Run Tests**: `pytest` (or other testing framework).
3.  **Build Docker Image**: Build the Docker image for the FastAPI application.
    ```yaml
    - name: 'gcr.io/cloud-builders/docker'
      args: ['build', '-t', '$_REGION-docker.pkg.dev/$PROJECT_ID/$_REPO_NAME/bq-optimizer-api:$COMMIT_SHA', '.']
    ```
4.  **Push Docker Image**: Push the newly built image to Artifact Registry.
    ```yaml
    - name: 'gcr.io/cloud-builders/docker'
      args: ['push', '$_REGION-docker.pkg.dev/$PROJECT_ID/$_REPO_NAME/bq-optimizer-api:$COMMIT_SHA']
    ```
5.  **Deploy to Cloud Run**: Deploy the new image to the Cloud Run service, pointing to the latest image digest and injecting secrets.
    ```yaml
    - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
      entrypoint: gcloud
      args:
        - 'run'
        - 'deploy'
        - 'bq-optimizer-api'
        - '--image=$_REGION-docker.pkg.dev/$PROJECT_ID/$_REPO_NAME/bq-optimizer-api:$COMMIT_SHA'
        - '--region=$_REGION'
        - '--update-secrets=DB_CONNECTION_STRING=db-conn-string:latest'
    ```
6.  **Deploy Cloud Function**: Deploy the code from the `/functions` directory.
    ```yaml
    - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
      entrypoint: gcloud
      args:
        - 'functions'
        - 'deploy'
        - 'bq-job-analyzer'
        - '--source=./functions'
        - '--trigger-http'
        - '--runtime=python310'
    ```

### Step 4: Schedule the Analysis Job

1.  **Create Cloud Scheduler Job**: Manually or via Terraform, create a Cloud Scheduler job.
    *   **Target**: HTTP.
    *   **URL**: The trigger URL of the `bq-job-analyzer` Cloud Function.
    *   **Frequency**: A cron expression (e.g., `0 2 * * *` for 2 AM daily).
    *   **Authentication**: Use OIDC to authenticate as the application's dedicated Service Account.

This completes the initial deployment. The system will now run automatically, and any code changes pushed to the repository will trigger a new deployment via Cloud Build.