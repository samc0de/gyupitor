from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()

# Allow CORS for frontend development
origins = [
    "http://localhost",
    "http://localhost:5173", # Default Vite port
    "http://localhost:3000", # Common React port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data based on the BigQuery `findings` table schema
mock_findings = [
    {
        "analysis_date": "2023-10-26",
        "finding_id": "mock-a3f4d5b6c7",
        "project_id": "tlabs-finops",
        "user_email": "sa-tlabs-finops-vm@tlabs-finops.iam.gserviceaccount.com",
        "job_id": "mock-job-12345",
        "query_hash": "a3f4d5b6c7e8f9a0b1c2d3e4f5a6b7c8",
        "query_text": "SELECT\n    billing_account_id,\n    service.id AS service_id,\n    service.description AS service_description,\n    pricing_as_of_time,\n    sku.id AS sku_id,\n    sku.description AS sku_description,\n    geo_taxonomy.type AS region_type,\n    ARRAY_TO_STRING(geo_taxonomy.regions,\"/\") AS regions,\n    pricing_unit,\n    pricing_unit_description,\n    pricing_unit_quantity,\n    start_usage_amount AS start_usage_amount,\n    usd_amount AS usd_amount,\n    account_currency_amount,\n    account_currency_code,\n    currency_conversion_rate\nFROM \n    `dm-network-host-project.dm_billing_detailed_logs.cloud_pricing_export`,\n    UNNEST(list_price.tiered_rates) AS unnest_rates\nWHERE \n    date(pricing_as_of_time) = (\n        SELECT max(date(pricing_as_of_time))\n        FROM `dm-network-host-project.dm_billing_detailed_logs.cloud_pricing_export`\n        WHERE billing_account_id = '011B1C-1C2837-C203FD'\n    )\n    AND billing_account_id = '011B1C-1C2837-C203FD'",
        "total_bytes_billed": 11800000000, # 11.8 GB
        "start_time": "2023-10-26T10:00:00Z",
        "recommendations": [
            {
                "code": "ADD_PARTITION_AND_CLUSTER",
                "details": "Modify the `dm-network-host-project.dm_billing_detailed_logs.cloud_pricing_export` table to be partitioned by `DATE(pricing_as_of_time)` and clustered by `billing_account_id`."
            },
            {
                "code": "REFACTOR_SQL_QUERY",
                "details": "Refactor the SQL query to use `_PARTITIONTIME` pseudo-column to avoid repeated full table scans for finding the latest date."
            }
        ],
        "estimated_cost": 2.16,
        "estimated_savings": 2.09
    },
    {
        "analysis_date": "2023-10-25",
        "finding_id": "mock-e8b9c1d2e3",
        "project_id": "proj-data-eng",
        "user_email": "data.engineer@company.com",
        "job_id": "mock-job-67890",
        "query_hash": "e8b9c1d2e3f4a5b6c7d8e9f0a1b2c3d4",
        "query_text": "SELECT count(*) FROM `some-project.some_dataset.large_table`, UNNEST(some_array_field)",
        "total_bytes_billed": 9500000000, # 9.5 GB
        "start_time": "2023-10-25T14:30:00Z",
        "recommendations": [
            {
                "code": "AVOID_CROSS_JOIN_UNNEST",
                "details": "The query uses an implicit CROSS JOIN with UNNEST. Consider if this is truly necessary or if a more targeted JOIN or subquery approach is better, especially for large tables."
            },
            {
                "code": "LIMIT_STAR_SELECT",
                "details": "Selecting '*' from large tables with UNNEST can lead to excessive data processing. Only select necessary columns."
            }
        ],
        "estimated_cost": 1.80,
        "estimated_savings": 1.55
    }
]

@app.get("/")
async def root():
    return {"message": "BigQuery Cost Optimizer API is running!"}

@app.get("/findings")
async def get_findings():
    return mock_findings
