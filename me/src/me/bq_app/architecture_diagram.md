```mermaid
graph TD
    subgraph User Facing Services
        A[End User] --> B{Web/Mobile App};
        B --> C[API Gateway];
    end

    subgraph Application Backend (Serverless)
        C --> D[Cloud Function: Query Handler];
        D --> E{Cache (Firestore/Memorystore)};
        D --> F[BigQuery Materialized View];
        E -- Cache Miss --> F;
        E -- Cache Hit --> B;
        F -- Query Results --> D;
        D -- Formatted Results --> C;
    end

    subgraph Data Ingestion & Processing
        G[Data Source] --> H[Cloud Storage];
        H -- Object Finalize Trigger --> I[Cloud Function: ETL/ELT];
        I --> J[BigQuery Raw Tables];
    end

    subgraph Data Warehouse Optimization
        J -- Automatic Refresh --> F;
        style F fill:#f9f,stroke:#333,stroke-width:2px
    end

    subgraph Monitoring & Logging
        D --> K[Cloud Logging & Monitoring];
        C --> K;
        F -- Query Metrics --> K;
    end
```
