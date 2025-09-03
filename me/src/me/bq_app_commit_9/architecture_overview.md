# BQ Application - Architecture Overview

## 1. Guiding Principles

This architecture is designed based on the insights from the BigQuery analysis, which highlighted the need for a system capable of handling high-volume streaming data, supporting both real-time and batch analytics, and maintaining cost-effectiveness and scalability. The core principles are:

- **Serverless First:** Prioritize managed and serverless services (Cloud Run, Cloud Functions, Dataflow, BigQuery) to minimize operational overhead, reduce costs, and enable automatic scaling.
- **Event-Driven:** Build a loosely coupled system where components react to events. This enhances scalability and resilience.
- **Scalability & Elasticity:** The architecture must scale horizontally to handle fluctuating loads, from a few events per second to millions, without manual intervention.
- **Cost-Effectiveness:** Pay-per-use pricing models are favored. Data lifecycle management will be used to move data to cheaper storage tiers over time.
- **DevOps & Automation:** The entire infrastructure should be manageable as code (IaC), with robust CI/CD pipelines for automated testing and deployment.

## 2. High-Level Architecture Components

The architecture is divided into four main layers: Data Ingestion, Data Processing, Data Storage & Analytics, and Application & Serving.

![Architecture Diagram](architecture_diagram.md)

### 2.1. Data Ingestion

- **Cloud Pub/Sub:** This is the central entry point for all incoming data streams (e.g., user clicks from web/mobile apps, IoT sensor readings). 
    - **Why Pub/Sub?** It acts as a scalable, durable buffer, decoupling the data producers from the consumers. This prevents data loss during processing spikes and allows different parts of the system to consume the data at their own pace. It provides at-least-once delivery guarantees and can scale globally.

### 2.2. Data Processing

We employ a two-pronged approach to processing: a hot path for real-time needs and a cold path for batch processing.

- **Cloud Functions (Hot Path / Streaming):**
    - **Role:** Subscribed to the Pub/Sub topic to perform lightweight, near real-time processing. Common tasks include data validation, enrichment (e.g., adding a timestamp), and simple transformations before streaming the data directly into a "raw" table in BigQuery.
    - **Why Cloud Functions?** They are perfect for short-lived, event-triggered tasks. They scale to zero, meaning you only pay when they are running, which is extremely cost-effective for sporadic workloads.

- **Cloud Dataflow (Cold Path / Batch & Advanced Streaming):**
    - **Role:** Used for complex, large-scale data transformations, aggregations, and batch processing. Dataflow jobs can be scheduled (e.g., daily) to read raw data from BigQuery or Cloud Storage, perform heavy computations (like sessionization or calculating daily aggregates), and write the cleaned, structured results into curated tables in BigQuery.
    - **Why Dataflow?** It provides a powerful, managed Apache Beam environment that can handle massive datasets. It auto-scales worker resources, optimizing for performance and cost. It's ideal for ETL/ELT jobs that are too complex or long-running for Cloud Functions.

### 2.3. Data Storage & Analytics

- **Google Cloud Storage (GCS):**
    - **Role:** Serves as the primary data lake. Raw, unaltered event data from Cloud Functions is archived here for long-term storage, disaster recovery, and re-processing if needed. 
    - **Why GCS?** It's a highly durable, low-cost object store. We will use lifecycle policies to automatically transition older data to colder, cheaper storage classes (e.g., Nearline, Coldline) to manage costs.

- **BigQuery:**
    - **Role:** The core of our analytics platform, serving as the data warehouse.
        - **Raw Tables:** Data is streamed directly from Cloud Functions into these tables for real-time availability.
        - **Processed/Curated Tables:** Dataflow jobs populate these tables with cleaned, aggregated, and analysis-ready data. These are the primary tables used by the backend API and BI tools.
    - **Why BigQuery?** Its serverless, columnar storage architecture is built for petabyte-scale analytics. The separation of storage and compute allows for incredible query performance and cost control. Its native integration with the GCP ecosystem makes it a natural choice.

### 2.4. Application & Serving Layer

- **Cloud Run:**
    - **Role:** Hosts the backend API for the application. This service will query the curated tables in BigQuery to serve data to the front-end applications (web/mobile).
    - **Why Cloud Run?** It's a fully managed, serverless platform for running stateless containers. It scales automatically based on request traffic, including scaling to zero. This provides the scalability of Kubernetes with the simplicity of a serverless platform, significantly reducing operational complexity.

- **Cloud Load Balancing + Cloud Armor:**
    - **Role:** The public-facing entry point for all API traffic. The Global External HTTPS Load Balancer distributes traffic to the appropriate Cloud Run service. Cloud Armor provides essential security features like DDoS protection and a Web Application Firewall (WAF).
    - **Why?** This combination ensures high availability, low latency (through its global CDN), and robust security for our application endpoints.

- **Looker Studio (formerly Google Data Studio):**
    - **Role:** The primary tool for Business Intelligence (BI) and data visualization. Business users and analysts can connect directly to BigQuery to build interactive dashboards and reports on the processed data.
    - **Why?** It's a free, powerful BI tool that integrates seamlessly with BigQuery, enabling self-service analytics without requiring engineering resources.

## 3. DevOps and Operations

- **Infrastructure as Code (IaC):** All cloud resources will be defined using Terraform. This ensures reproducibility, version control, and automated environment provisioning.
- **CI/CD:** A CI/CD pipeline (e.g., using GitHub Actions or Cloud Build) will be implemented to automatically build, test, and deploy both the application code (Cloud Run, Cloud Functions) and infrastructure changes (Terraform).
- **Monitoring & Logging:** Cloud Monitoring and Cloud Logging will be used to collect metrics, logs, and traces from all services. Dashboards and alerts will be configured to monitor system health, performance, and costs, enabling proactive issue resolution.