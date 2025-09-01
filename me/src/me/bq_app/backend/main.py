from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from datetime import datetime, timedelta
import uuid

from .models import Recommendation

app = FastAPI(
    title="BigQuery Cost Optimization API",
    description="API for managing BigQuery cost optimization recommendations.",
    version="0.1.0",
)

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:3000",  # Frontend runs on port 3000
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock database for recommendations
mock_recommendations: List[Recommendation] = [
    Recommendation(
        id=uuid.uuid4(),
        project_id="tlabs-finops",
        user_email="sa-tlabs-finops-vm@tlabs-finops.iam.gserviceaccount.com",
        job_id="job-12345-abcde",
        query_hash="a" * 64,
        query_text="SELECT ... FROM `dm-network-host-project.dm_billing_detailed_logs.cloud_pricing_export` WHERE date(pricing_as_of_time) = (SELECT max(date(pricing_as_of_time)) FROM ...)",
        total_billed_gb=290.34,
        estimated_cost_usd=1.42,
        inefficiency_type="FULL_TABLE_SCAN",
        recommendation_title="Optimize `cloud_pricing_export` Table and Queries",
        recommendation_details="Recreate the `cloud_pricing_export` table with partitioning on `pricing_as_of_time` and clustering on `billing_account_id`. Rewrite query to avoid full table scan.",
        status="NEW",
        created_at=datetime.now() - timedelta(days=2),
        updated_at=datetime.now() - timedelta(days=2),
    ),
    Recommendation(
        id=uuid.uuid4(),
        project_id="tlabs-finops",
        user_email="sa-tlabs-finops-vm@tlabs-finops.iam.gserviceaccount.com",
        job_id="job-67890-fghij",
        query_hash="b" * 64,
        query_text="SELECT ... FROM `dm-network-host-project.dm_billing_detailed_logs.gcp_billing_export_resource_v1_011B1C_1C2837_C203FD` WHERE datetime(export_time) > parse_datetime(...) GROUP BY ...",
        total_billed_gb=276.51,
        estimated_cost_usd=1.35,
        inefficiency_type="PARTITION_MISMATCH",
        recommendation_title="Optimize `gcp_billing_export_resource` Table and Queries",
        recommendation_details="Recreate the table with partitioning on `export_time` and clustering on `project.id` and `service.id`.",
        status="NEW",
        created_at=datetime.now() - timedelta(days=1),
        updated_at=datetime.now() - timedelta(days=1),
    ),
]

@app.get("/recommendations", response_model=List[Recommendation])
async def get_recommendations():
    """Retrieve a list of all optimization recommendations."""
    return mock_recommendations

@app.get("/recommendations/{recommendation_id}", response_model=Recommendation)
async def get_recommendation(recommendation_id: uuid.UUID):
    """Retrieve a single optimization recommendation by ID."""
    for rec in mock_recommendations:
        if rec.id == recommendation_id:
            return rec
    raise HTTPException(status_code=404, detail="Recommendation not found")
